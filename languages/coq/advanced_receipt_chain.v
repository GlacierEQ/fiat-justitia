Require Import Coq.Arith.Arith.
Require Import Coq.Lists.List.
Import ListNotations.

Record Receipt := {
  sequence : nat;
  previous_sequence : nat;
  monotonic : previous_sequence <= sequence
}.

Definition chain_step (left right : Receipt) : Prop :=
  sequence left <= sequence right /\
  previous_sequence right = sequence left.

Theorem chain_step_never_moves_backward :
  forall left right, chain_step left right ->
  sequence left <= sequence right.
Proof.
  intros left right H.
  destruct H as [Horder Hlink].
  exact Horder.
Qed.

Fixpoint ordered (receipts : list Receipt) : Prop :=
  match receipts with
  | [] | [_] => True
  | left :: right :: tail =>
      chain_step left right /\ ordered (right :: tail)
  end.

Theorem ordered_head_step :
  forall left right tail,
  ordered (left :: right :: tail) ->
  sequence left <= sequence right.
Proof.
  intros left right tail H.
  simpl in H.
  destruct H as [Hstep Htail].
  apply chain_step_never_moves_backward.
  exact Hstep.
Qed.
