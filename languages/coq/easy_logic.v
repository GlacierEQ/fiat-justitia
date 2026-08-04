Theorem implication_identity : forall P : Prop, P -> P.
Proof.
  intros P evidence.
  exact evidence.
Qed.
