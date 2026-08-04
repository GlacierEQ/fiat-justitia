module Main where

data Tree a = Leaf a | Node (Tree a) (Tree a)
  deriving (Eq, Show)

size :: Tree a -> Int
size (Leaf _) = 1
size (Node left right) = size left + size right

main :: IO ()
main = print (size (Node (Leaf "left") (Leaf "right")))
