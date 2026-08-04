module Main where

import Data.Char (ord)
import Data.List (intercalate, isPrefixOf)
import Numeric (showHex)

-- Haskell — Advanced Example: Pure Capability-Policy AST Validator
--
-- What: Validates a typed action plan against explicit read, write, tool,
--       network, and destructive-action policy.
-- Where: Compilers, workflow planners, agent admission gates, and financial or
--        safety-sensitive transformation systems.
-- When: Use when the decision boundary benefits from immutable data,
--       exhaustive pattern matching, and deterministic pure evaluation.
-- Why: Algebraic data types make every action and rejection reason explicit.
-- How: Lexically safe relative paths, exact allowlists, pure validation, and a
--      dependency-free deterministic demonstration receipt.

data Action
  = ReadArtifact FilePath
  | WriteInternal FilePath
  | InvokeTool String
  | ExternalCall String
  | DeleteArtifact FilePath
  deriving (Eq, Show)

data Policy = Policy
  { allowedTools :: [String]
  , allowedDomains :: [String]
  , readableRoots :: [FilePath]
  , writableRoots :: [FilePath]
  , destructiveAllowed :: Bool
  }
  deriving (Eq, Show)

data ValidationError
  = EmptyPlan
  | EmptyIdentifier String
  | UnsafeRelativePath FilePath
  | ReadOutsideRoot FilePath
  | WriteOutsideRoot FilePath
  | ToolNotAllowed String
  | DomainNotAllowed String
  | DestructiveActionDenied FilePath
  deriving (Eq, Show)

data Decision = Decision
  { accepted :: Bool
  , actionCount :: Int
  , errors :: [ValidationError]
  , receiptHash :: String
  }
  deriving (Eq, Show)

splitOnSlash :: String -> [String]
splitOnSlash value = go value [] []
  where
    go [] current parts = reverse (reverse current : parts)
    go ('/' : rest) current parts = go rest [] (reverse current : parts)
    go (char : rest) current parts = go rest (char : current) parts

safeRelativePath :: FilePath -> Either ValidationError FilePath
safeRelativePath [] = Left (EmptyIdentifier "path")
safeRelativePath path@('/' : _) = Left (UnsafeRelativePath path)
safeRelativePath path
  | '\\' `elem` path = Left (UnsafeRelativePath path)
  | any invalidSegment segments = Left (UnsafeRelativePath path)
  | otherwise = Right (intercalate "/" segments)
  where
    segments = splitOnSlash path
    invalidSegment segment = null segment || segment == "." || segment == ".."

withinRoots :: [FilePath] -> FilePath -> Bool
withinRoots roots path = any matches roots
  where
    matches root = root `isPrefixOf` path

validateRead :: Policy -> FilePath -> [ValidationError]
validateRead policy path =
  case safeRelativePath path of
    Left err -> [err]
    Right safePath
      | withinRoots (readableRoots policy) safePath -> []
      | otherwise -> [ReadOutsideRoot safePath]

validateWrite :: Policy -> FilePath -> [ValidationError]
validateWrite policy path =
  case safeRelativePath path of
    Left err -> [err]
    Right safePath
      | withinRoots (writableRoots policy) safePath -> []
      | otherwise -> [WriteOutsideRoot safePath]

validateAction :: Policy -> Action -> [ValidationError]
validateAction policy (ReadArtifact path) = validateRead policy path
validateAction policy (WriteInternal path) = validateWrite policy path
validateAction policy (InvokeTool tool)
  | null tool = [EmptyIdentifier "tool"]
  | tool `elem` allowedTools policy = []
  | otherwise = [ToolNotAllowed tool]
validateAction policy (ExternalCall domain)
  | null domain = [EmptyIdentifier "domain"]
  | domain `elem` allowedDomains policy = []
  | otherwise = [DomainNotAllowed domain]
validateAction policy (DeleteArtifact path) =
  case safeRelativePath path of
    Left err -> [err]
    Right safePath
      | destructiveAllowed policy -> []
      | otherwise -> [DestructiveActionDenied safePath]

-- Deterministic demonstration hash. Production Tower receipts use SHA-256;
-- this exhibit keeps the algorithm dependency-free while preserving the
-- canonicalize -> hash -> receipt architecture.
stableHash :: String -> String
stableHash input =
  let modulus = 4294967291 :: Integer
      step acc char = (acc * 16777619 + toInteger (ord char)) `mod` modulus
      digest = foldl step 2166136261 input
   in pad 8 (showHex digest "")
  where
    pad width value = replicate (max 0 (width - length value)) '0' ++ value

canonicalAction :: Action -> String
canonicalAction (ReadArtifact path) = "read:" ++ path
canonicalAction (WriteInternal path) = "write_internal:" ++ path
canonicalAction (InvokeTool tool) = "tool:" ++ tool
canonicalAction (ExternalCall domain) = "external:" ++ domain
canonicalAction (DeleteArtifact path) = "delete:" ++ path

validatePlan :: Policy -> [Action] -> Decision
validatePlan policy actions =
  let planErrors = if null actions then [EmptyPlan] else []
      discoveredErrors = planErrors ++ concatMap (validateAction policy) actions
      canonical = intercalate "|" (map canonicalAction actions)
   in Decision
        { accepted = null discoveredErrors
        , actionCount = length actions
        , errors = discoveredErrors
        , receiptHash = stableHash canonical
        }

assert :: String -> Bool -> IO ()
assert label condition =
  if condition
    then putStrLn ("PASS " ++ label)
    else error ("FAILED " ++ label)

main :: IO ()
main = do
  let policy =
        Policy
          { allowedTools = ["tower.validate", "tower.receipt"]
          , allowedDomains = ["api.github.com"]
          , readableRoots = ["registry/", "generated/", "docs/"]
          , writableRoots = ["build/", "artifacts/"]
          , destructiveAllowed = False
          }
      permitted =
        [ ReadArtifact "registry/tower.yml"
        , InvokeTool "tower.validate"
        , WriteInternal "artifacts/proof.json"
        , ExternalCall "api.github.com"
        ]
      forbidden =
        [ InvokeTool "shell.unbounded"
        , WriteInternal "build/../secrets.txt"
        , WriteInternal "build-evil/output.txt"
        , ReadArtifact "/etc/passwd"
        , DeleteArtifact "registry/tower.yml"
        ]
      permittedDecision = validatePlan policy permitted
      forbiddenDecision = validatePlan policy forbidden
      emptyDecision = validatePlan policy []

  assert "permitted plan accepted" (accepted permittedDecision)
  assert "permitted action count" (actionCount permittedDecision == 4)
  assert "receipt is deterministic" (receiptHash permittedDecision == receiptHash (validatePlan policy permitted))
  assert "forbidden plan rejected" (not (accepted forbiddenDecision))
  assert "all forbidden actions explained" (length (errors forbiddenDecision) == 5)
  assert "lexical traversal rejected" (UnsafeRelativePath "build/../secrets.txt" `elem` errors forbiddenDecision)
  assert "sibling prefix rejected" (WriteOutsideRoot "build-evil/output.txt" `elem` errors forbiddenDecision)
  assert "absolute read rejected" (UnsafeRelativePath "/etc/passwd" `elem` errors forbiddenDecision)
  assert "empty plan rejected with reason" (errors emptyDecision == [EmptyPlan])
  print permittedDecision
  print forbiddenDecision
  print emptyDecision
