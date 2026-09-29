YGG-B68 PREREGISTRATION — THIRD COHORT REPLICATION

Parent B67 valid SEED_COHORT_SENSITIVITY: the B65 anchor cohort [2888,2999,3111,3222,3333] reproduces D5_PARETO_DOMINATES_SIGNAL under B66 instrumentation, while the disjoint B66 cohort [3444,3555,3666,3777,3888] does not.

Question: is the observed seed-cohort sensitivity reproducible on a third disjoint frozen cohort, or was the B66 cohort an isolated exception?

Freeze exact B66/B67 substrate:
- q positions exactly [0,1,2,3,4];
- threshold T=2.6009554862976074 bit-exact;
- exact 12 cyclic forward/reverse six-competitor orders;
- exact CONTROL, GATED, and FIXED_D5 decision logic;
- 120 parameters and 32 persistent-state scalars;
- deterministic Torch;
- no policy changes, threshold refitting, or additional intervention budget.

New third cohort seeds exactly:
[4001,4111,4222,4333,4444]
These are disjoint from both prior cohorts.

Run the exact B66 cohort decomposition with only the seed list rebound to this third cohort. Retain the frozen B65 and B66 cohort classifications as parent anchors; do not rerun or refit them to choose the new seeds.

Report:
- full-population D5 Pareto boolean;
- cohort classification;
- control/gated/D5 failures-by6;
- gated/D5 intervention counts;
- gated/D5 final target accuracy;
- gated/D5 collateral NEW_ERROR and REPAIR counts.

Classification:
THIRD_COHORT_D5_PARETO if full_population_d5_pareto=true.
THIRD_COHORT_NONPARETO if full_population_d5_pareto=false.
ANCHOR_NOT_REPRODUCED if B67 no longer reproduces SEED_COHORT_SENSITIVITY.
OTHER_VALID_PATTERN otherwise.

Validity: exact new seed cohort; exact threshold; exact q positions; exact policy code paths; frozen parent anchor reproduced; deterministic duplicate; state and parameter counts exact.
Scientific negatives are valid. No post-result tuning.
