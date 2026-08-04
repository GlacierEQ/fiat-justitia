import Std

/-!
Advanced Lean 4 exhibit: prove monotonicity of the Tower authority gate.
Evidence class: formally_verified when accepted by the Lean kernel.
-/

inductive ActionClass where
  | read | plan | writeInternal | external | destructive
  deriving Repr, DecidableEq

def rank : ActionClass → Nat
  | .read => 0
  | .plan => 1
  | .writeInternal => 2
  | .external => 3
  | .destructive => 4

def allowed (maximum requested : ActionClass) : Prop :=
  rank requested ≤ rank maximum

theorem lowerActionRemainsAllowed
    (maximum requested lower : ActionClass)
    (hAllowed : allowed maximum requested)
    (hLower : rank lower ≤ rank requested) :
    allowed maximum lower := by
  exact Nat.le_trans hLower hAllowed

theorem destructiveBlockedByExternal :
    ¬ allowed ActionClass.external ActionClass.destructive := by
  simp [allowed, rank]

structure Receipt where
  sequence : Nat
  previousSequence : Nat
  monotonic : previousSequence ≤ sequence

theorem receiptNeverMovesBackward (r : Receipt) :
    r.previousSequence ≤ r.sequence := by
  exact r.monotonic
