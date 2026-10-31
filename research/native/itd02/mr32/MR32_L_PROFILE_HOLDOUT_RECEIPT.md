# MR32-L — leave-one-profile-out retention diagnostic receipt

Date: 2026-10-31
PR #716: OPEN / DRAFT / UNMERGED.
Exact source/test head: `324eb6f44c9e0c61c2f3208a522c76eb59c8910a`.
Actions run: `41226991895`.
- Ubuntu job `124613151462`: PASS, 50 tests, syntax, resource inventory, FIT/TRANSFER script, eight-fold script, clean checkout.
- Windows job `124613151517`: PASS, 50 tests, syntax, resource inventory, FIT/TRANSFER script, eight-fold script, clean checkout.

## Protocol

Eight folds; each fold withholds one of the eight combinations of evidence-count category, prediction-error category and contradiction category from FIT. The utility scorer trains on the other seven profiles for 30 epochs. Only the learned weights are copied into a fresh TRANSFER store; new-key records for all eight profiles are inserted and no transfer feedback is supplied. The active budget remains seven. Per-fold active-set precision is compared with fixed recency and evidence-only controls.

## Aggregate results (identical on Windows and Ubuntu)

| Control | Mean precision@7 |
|---|---:|
| Learned utility scorer | **0.929** |
| Evidence-only | 0.714 |
| Fixed recency | 0.571 |

Total transfer-feedback events across all eight folds: **0**.

## Critical per-profile limitation

The withheld profile itself was selected into the active seven in only **2 of 8 folds**. The two selected held-out profiles were positive-label combinations; two other positive-label combinations were not selected when withheld. Thus mean active-set quality across all profile folds is strong on this small constructed cohort, but complete generalization to every unseen metadata combination is NOT demonstrated.

## Interpretation

This is better than the earlier disjoint-key FIT/TRANSFER check because one metadata combination is absent from training in each fold. However:
- All folds share the same known synthetic majority-rule generator.
- The novel item is one combination of already defined metadata categories, not a new task family or causal mechanism.
- Scorer metadata, linear function class and target rule are hand-designed.
- One deterministic order per fold; no repeated randomization or uncertainty interval.
- No future query distribution, real task reward, causal decision, restart interference or authentic environment is modeled.

The result demonstrates limited interpolation across a small metadata profile grid, not general intelligence, native causal learning or unfamiliar-world transfer. The failure to retain 6/8 withheld profiles (including two positive profiles) is retained as a limitation, not hidden by the mean score.

## Disposition

`MR32_L_8_FOLD_PROFILE_DIAGNOSTIC=WINDOWS_LINUX_PASS`
`LEARNED_MEAN_PRECISION_AT_7=0.929`
`EVIDENCE_ONLY_MEAN_PRECISION_AT_7=0.714`
`RECENCY_MEAN_PRECISION_AT_7=0.571`
`WITHHELD_PROFILE_SELECTED=2_OF_8`
`TRANSFER_FEEDBACK_EVENTS=0`
`AUTHENTIC_TASK_EFFICACY=NOT_TESTED`
`UNFAMILIAR_TASK_FAMILY_TRANSFER=NOT_TESTED`
`G29_ATLAS=BLOCKED_STALE_INDEX`
`FSA04_ORIGINAL_FIRST_USE=BLOCKED`

Evidence is repository-resident. No original-world environment, protected cohort, accepted source, merge, production integration or promotion was used.
