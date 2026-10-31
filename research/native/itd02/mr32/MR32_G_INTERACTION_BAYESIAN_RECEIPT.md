# MR32-G — interaction Bayesian control exact-head qualification

Date: 2026-10-31
PR #716 remains OPEN / DRAFT / UNMERGED.
Exact qualified head: `98beb759934139eae531e4d4b7b5fb773cb77d32`.
Base: `0503b25fe74dca30035a65c1d81edabddd31926e`.

## New conventional model

`interaction_bayes_control.py` adds a diagonal Bayesian linear model with 68 coefficients per output: bias + 16 public features + 3 selected-action indicators + 48 feature×action interactions. It uses a Normal-Gaussian conjugate update on observed selected-action consequences and supports predictive uncertainty and integrity-checked checkpoints.

`test_interaction_bayes_control.py` includes a balanced synthetic sign-reversal relation. It compares the interaction model with the additive diagonal Bayesian model on the four held-out action×feature combinations. This is a test of feature-basis expressivity, not an original environment or native architecture efficacy test.

## Exact-head CI

Actions run `41223916743`:
- Windows job `124603983637`: PASS, 37 tests, syntax compile, resource inventory and clean checkout.
- Ubuntu job `124603983783`: PASS, 37 tests, syntax compile, resource inventory and clean checkout.

Both test modules and implementation were part of the exact tested checkout.

## Same 256-step diagnostic inventory

| Model | Serialized bytes | Deep Python object bytes | tracemalloc peak bytes Windows/Linux | Wall seconds Windows/Linux |
|---|---:|---:|---:|---:|
| Memoryless mean | 63 | 852 | 166,312 / 166,320 | 0.00893 / 0.00818 |
| Additive diagonal Bayesian | 1,865 | 11,961 | 24,216 / 24,232 | 0.10090 / 0.10186 |
| Interaction Bayesian | 5,326 | 36,529 | 48,288 / 48,312 | 0.28082 / 0.27613 |
| Conventional prototype/EMA | 3,483 | 4,419 | 134,728 / 134,736 | 0.02119 / 0.02054 |
| Recurrent state-space | 3,170 | 5,808 | 114,584 / 114,592 | 0.11873 / 0.12090 |
| MR32 residual prototype | 3,853 | 7,335 | 178,408 / 178,512 | 0.09675 / 0.09044 |

Interpretation: interaction Bayesian model has substantially more representational capacity and incurs larger state and compute costs. Its serialized checkpoint is 5,326 bytes, deep object estimate 36,529 bytes, and elapsed time about 0.276–0.281 s in one hosted-runner pass. This is neither fair resource parity nor evidence of predictive superiority outside the small synthetic expressivity test. Hosted runners are uncalibrated; timings are single-run/noisy; tracemalloc is not process RSS; serialization formats differ.

## Separate G29 status

At the same commit, G29 Atlas Acceptance run `41223916745`:
- Windows failed closed at `scripts/build_code_atlas.py --check-if-present` with `YGG_ATLAS_FAIL_CLOSED: indexed file set changed`.
- Linux reached the same freshness failure and was still in regeneration when last checked.
- This is an advisory source-index integration blocker, distinct from MR32's exact-head focused CI, which passed on both platforms.
- No G29 or full final integration regression PASS is claimed.

## Scientific and governance disposition

`INTERACTION_BAYESIAN_EXACT_HEAD_CI=WINDOWS_LINUX_PASS`
`SYNTHETIC_ACTION_FEATURE_EXPRESSIVITY_TEST=PASS`
`RESOURCE_PARITY=NOT_ESTABLISHED`
`SCIENTIFIC_EFFICACY=NOT_TESTED`
`UNFAMILIAR_TRANSFER=NOT_TESTED`
`G29_ATLAS=BLOCKED_STALE_INDEX`
`FSA04_ORIGINAL_FIRST_USE=BLOCKED`

The interaction model remains a conventional diagonal-covariance Bayesian linear learner over an explicitly expanded fixed feature basis; it is not a Bayesian network, causal graph learner or planner.

No original-world environment, protected cohort, accepted source, production model, controller, or runtime was modified.
