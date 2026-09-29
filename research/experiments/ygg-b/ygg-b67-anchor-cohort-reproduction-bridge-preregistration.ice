YGG-B67 PREREGISTRATION — B65 ANCHOR-COHORT REPRODUCTION BRIDGE
Parent B66 valid ANCHOR_NOT_REPRODUCED.
Question: did B66 lose the B65 D5 Pareto direction because the new disjoint seed cohort changed the result, or because the B66 cohort-decomposition instrumentation changed the underlying comparison?

Freeze exact B65 anchor cohort:
- seeds exactly [2888,2999,3111,3222,3333];
- q positions exactly [0,1,2,3,4];
- threshold T=2.6009554862976074 bit-exact;
- exact 12 cyclic forward/reverse six-competitor orders;
- exact CONTROL, GATED, and FIXED_D5 decision logic from B65/B66;
- 120 parameters and 32 persistent-state scalars;
- deterministic Torch;
- no policy changes, no threshold refitting, no additional intervention budget.

Run two matched analyses on the SAME B65 seeds:
1. Native B65 prevention-collateral ledger.
2. B66 cohort-decomposition instrumentation with only the seed list rebound to the B65 anchor cohort.

Also reproduce the original B66 new-cohort classification on seeds [3444,3555,3666,3777,3888].

Shared B65/B66 full-population metrics must match exactly on the B65 seeds:
control/gated/D5 failures-by6;
gated/D5 intervention counts;
gated/D5 final target accuracy;
gated/D5 collateral NEW_ERROR and REPAIR counts.

Classification:
SEED_COHORT_SENSITIVITY if the B65-seed metrics are instrumentation-equivalent, B65 remains D5_PARETO_DOMINATES_SIGNAL, the B66 decomposition on B65 seeds has full_population_d5_pareto=true, and the original B66 new cohort remains ANCHOR_NOT_REPRODUCED.
INSTRUMENTATION_DRIFT if any shared full-population metric differs between B65 and B66 instrumentation on the same B65 seeds.
B65_ANCHOR_NOT_REPRODUCED if the native B65 anchor no longer classifies D5_PARETO_DOMINATES_SIGNAL.
PARENT_B66_NOT_REPRODUCED if the frozen original B66 new-cohort classification no longer reproduces.
OTHER_VALID_PATTERN otherwise.

Validity: exact seed cohorts; exact threshold; exact q positions; exact policy code paths; shared metrics compared without tolerance except floating values which must be bit-identical Python floats; parent B66 classification reproduced; duplicate complete execution byte-identical.
Scientific negatives are valid. No post-result tuning.
