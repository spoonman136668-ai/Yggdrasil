YGG-B66 PREREGISTRATION — MATCHED INTERVENTION-COHORT DECOMPOSITION
Parent B65 valid D5_PARETO_DOMINATES_SIGNAL.
Question: is FIXED_D5's B65 advantage caused by the timing of its intervention, or by the fact that GATED and FIXED_D5 intervene on different subsets of trajectories?

Freeze threshold T=2.6009554862976074 bit-exact. No refitting.
Fresh seeds exactly [3444,3555,3666,3777,3888], disjoint from B60-B65.
Freeze exact B65 substrate:120 parameters,32 persistent-state scalars,q=[0..4],deterministic Torch,same12 cyclic forward/reverse six-competitor orders.
Matched branches remain unchanged:
CONTROL: no intervention.
GATED: exact frozen signal policy, at most one target refresh.
FIXED_D5: exact B65 blind depth5 policy, at most one target refresh if target remains capable; no signal.

Do not change either policy.
For every matched trajectory record whether GATED intervened and whether FIXED_D5 intervened, then partition into exactly:
BOTH_INTERVENE
GATED_ONLY
D5_ONLY
NEITHER_INTERVENE

Within each cohort report:
- trajectory count;
- target failures-by6 for CONTROL/GATED/FIXED_D5;
- final target accuracy;
- intervention counts;
- six non-q collateral NEW_ERROR and REPAIR counts relative to matched CONTROL.
Also report the full-population B65 metrics for anchor replication.

Classification:
TIMING_ADVANTAGE_PERSISTS_MATCHED if in BOTH_INTERVENE FIXED_D5 has fewer target failures than GATED and no greater collateral NEW_ERROR count.
SELECTION_EFFECT_DOMINATES if the full-population D5 advantage reproduces but the BOTH_INTERVENE target-failure difference disappears or reverses.
SIGNAL_TIMING_ADVANTAGE_MATCHED if in BOTH_INTERVENE GATED has fewer target failures than FIXED_D5.
DISCORDANT_COHORT_DOMINATES if most full-population failure difference is localized to GATED_ONLY or D5_ONLY.
MIXED_TIMING_SELECTION_EFFECT otherwise.
ANCHOR_NOT_REPRODUCED if B65 construction, threshold, orders, or full-population direction fails.

Validity: exact fresh seeds/disjointness; exact12 orders; threshold bit-exact; policies byte-equivalent in decision logic to B65; one intervention max/branch; D5 signal-free; matched starting states; cohort assignment computed only from intervention occurrence; all seven original blocks scored after depth6; fixed parameters/capacity; deterministic duplicate.
Scientific negatives are valid. No post-result tuning.
