module advanced_capability_lattice where

open import Data.Nat using (ℕ; zero; suc; _≤_; z≤n; s≤s)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

data Action : Set where
  read plan writeInternal external destructive : Action

rank : Action → ℕ
rank read = 0
rank plan = 1
rank writeInternal = 2
rank external = 3
rank destructive = 4

Allowed : Action → Action → Set
Allowed maximum requested = rank requested ≤ rank maximum

lower-transitive :
  {maximum requested lower : Action} →
  rank lower ≤ rank requested →
  Allowed maximum requested →
  Allowed maximum lower
lower-transitive z≤n allowed = z≤n
lower-transitive (s≤s lower) (s≤s allowed) =
  s≤s (lower-transitive lower allowed)

destructive-not-external :
  Allowed external destructive → zero ≡ suc zero
destructive-not-external ()
