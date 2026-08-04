import Std

structure StageReceipt where
  sequence : Nat
  previous : Nat
  monotonic : previous ≤ sequence

def Linked (left right : StageReceipt) : Prop :=
  left.sequence = right.previous

theorem linkedChainMonotonic
    (left right : StageReceipt)
    (hLinked : Linked left right) :
    left.sequence ≤ right.sequence := by
  rw [hLinked]
  exact right.monotonic
