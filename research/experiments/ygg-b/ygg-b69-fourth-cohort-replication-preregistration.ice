YGG-B69 PREREGISTRATION — FOURTH COHORT REPLICATION

Parent B68 valid THIRD_COHORT_NONPARETO. The original B65 cohort reproduced D5_PARETO_DOMINATES_SIGNAL, while both the B66 cohort and the third disjoint cohort failed to reproduce the full-population D5 Pareto direction.

Question: does a fourth disjoint frozen cohort again classify non-Pareto, strengthening the interpretation that the original B65 direction was cohort-specific?

Freeze exact B68/B66 substrate:
- q positions exactly [0,1,2,3,4];
- threshold T=2.6009554862976074 bit-exact;
- exact 12 cyclic forward/reverse six-competitor orders;
- exact CONTROL, GATED, and FIXED_D5 decision logic;
- 120 parameters and 32 persistent-state scalars;
- deterministic Torch;
- no policy changes, threshold refitting, or additional intervention budget.

New fourth cohort seeds exactly:
[4555,4666,4777,4888,4999]
These are disjoint from the B65, B66, and B68 cohorts.

Run the exact B66 cohort decomposition with only the seed list rebound to this fourth cohort.

Report the same frozen full-population and cohort metrics as B68.

Classification:
FOURTH_COHORT_D5_PARETO if full_population_d5_pareto=true.
FOURTH_COHORT_NONPARETO if full_population_d5_pareto=false.
ANCHOR_NOT_REPRODUCED if B68 no longer reproduces THIRD_COHORT_NONPARETO.
OTHER_VALID_PATTERN otherwise.

Validity: exact new seed cohort; exact threshold; exact q positions; exact policy code paths; frozen parent anchor reproduced; deterministic duplicate; state and parameter counts exact.
Scientific negatives are valid. No post-result tuning.
