YGG-B65 PREREGISTRATION — SIGNAL-TIMED PREVENTION WITH MATCHED COLLATERAL LEDGER
Parent B64 valid SIGNAL_TIMING_STRICTLY_BETTER.
Question: does the signal-timed one-shot policy retain its target-failure advantage over the strongest blind schedule while causing no greater intervention-specific collateral to the other six bindings?
Frozen threshold T=2.6009554862976074. No refitting.
Strongest B64 blind comparator is FIXED_D5.
New seeds exactly [2888,2999,3111,3222,3333], disjoint from B60-B64.
Freeze exact B64 substrate:120 parameters,32 persistent-state scalars,q=[0..4],deterministic Torch,same12 cyclic forward/reverse six-competitor orders.
Matched branches:
CONTROL: no intervention.
GATED: exact frozen signal policy, at most one target refresh.
FIXED_D5: at most one target refresh immediately before scheduled competitor depth5 if target remains capable; no signal.
After depth6, query all seven original bindings in every branch.
For each non-q binding j:
GATED_NEW_ERROR = CONTROL final j correct and GATED final j incorrect.
GATED_REPAIR = CONTROL final j incorrect and GATED final j correct.
D5_NEW_ERROR and D5_REPAIR defined analogously.
Also report target-q final accuracy and first-loss/failures-by6 per branch.
No arbitrary collateral threshold is introduced.
Classification:
SIGNAL_PARETO_DOMINATES_D5 if GATED failures-by6 < D5 failures-by6 and GATED collateral NEW_ERROR count <= D5 collateral NEW_ERROR count.
SIGNAL_TARGET_BETTER_COLLATERAL_WORSE if GATED failures-by6 < D5 but GATED collateral NEW_ERROR count > D5.
D5_PARETO_DOMINATES_SIGNAL if D5 failures-by6 <= GATED and D5 collateral NEW_ERROR count <= GATED with at least one strict inequality.
MIXED_COLLATERAL_TRADEOFF otherwise.
ANCHOR_NOT_REPRODUCED if B64 construction or depth0 anchors fail.
Validity: exact fresh seeds/disjointness; exact12 orders; threshold bit-exact; GATED/FIXED_D5 one intervention maximum; D5 signal-free; matched starting states; all seven original blocks scored after depth6; collateral defined only relative to matched CONTROL; fixed parameters/capacity; deterministic duplicate.
Scientific negatives are valid. No post-result tuning.
