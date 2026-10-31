# MR32-F — diagonal Bayesian comparator qualification receipt

Date: 2026-10-31
PR: #716 (OPEN / DRAFT / UNMERGED)
Exact source head: `5659a65c256558cef40dd90281eb212ec83f8d96`
Base: MR31 development head `0503b25fe74dca30035a65c1d81edabddd31926e`
Classification: SOURCE-ONLY CONVENTIONAL CONTROL / ENGINEERING QUALIFICATION / NOT EFFICACY.

## Added comparator

`research/native/itd02/mr32/diagonal_bayes_control.py` is a diagonal Bayesian linear consequence predictor. It maintains independent Normal-Gaussian coefficient posteriors for eight output dimensions, uses 16 public input features plus selected-action one-hot and bias, updates sufficient statistics only after selected-action feedback, emits predictive uncertainty and supports integrity-checked checkpoint restore.

It is an intentionally transparent diagonal-covariance linear baseline. It is NOT a Bayesian network, causal structure learner, nonlinear model, planner or strongest possible Bayesian control. Its additive linear representation cannot capture arbitrary interactions without feature expansion. The 0..2 action IDs remain development interface values, not permission to map to original owner action semantics.

The restore path was corrected to permit unbounded sufficient-statistic values while still rejecting nonfinite/invalid precision. Precision and weighted sums are mathematical accumulated statistics and must not be forced into the normalized observation range.

## Exact-head qualification

Dedicated Actions run: `41220697147`
Head: `5659a65c256558cef40dd90281eb212ec83f8d96`

- Windows job `124594494440`: PASS; 30 tests; syntax compile; resource inventory; clean checkout.
- Ubuntu job `124594494651`: PASS; 30 tests; syntax compile; resource inventory; clean checkout.

The test suite includes posterior update ordering, action-conditioned behavior, uncertainty reduction under repeated evidence, cold restore equivalence, pending-feedback rejection, tamper rejection and dimensions/action validation.

## Same deterministic 256-step inventory

| Model | Serialized state bytes (Windows/Linux) | Deep Python object bytes | tracemalloc peak bytes | Wall seconds Windows / Linux |
|---|---:|---:|---:|---:|
| Memoryless mean | 63 | 852 | 166,312 / 166,320 | 0.00712 / 0.00725 |
| Diagonal Bayesian linear | 1,865 | 11,961 | 24,216 / 24,232 | 0.08575 / 0.08163 |
| Conventional prototype/EMA | 3,483 | 4,419 | 134,728 / 134,736 | 0.01801 / 0.01801 |
| Recurrent state-space | 3,170 | 5,808 | 114,584 / 114,592 | 0.10156 / 0.10120 |
| MR32 residual prototype | 3,853 | 7,335 | 178,408 / 178,512 | 0.08124 / 0.07119 |

Interpretation:
- Bayesian posterior checkpoint is 1,865 bytes, about 52% smaller than MR32's 3,853-byte checkpoint.
- Bayesian Python object estimate is 11,961 bytes, about 63% larger than MR32's 7,335 bytes.
- Bayesian traced transient allocation is substantially lower in this inventory than MR32, but this is not OS process RSS.
- Bayesian wall time was approximately 0.082–0.086 s, versus MR32 0.071–0.081 s in these individual hosted-runner observations.
- These measurements are one deterministic synthetic stream, single pass per hosted OS, and the checkpoint envelopes/model structures are not semantically uniform. They are descriptive engineering diagnostics, NOT total-resource parity or evidence of model performance.

## Current broader qualification

- MR32-F focused source workflow Windows/Linux: PASS.
- NCI-04G5, G6, G7, G7A at this PR head: PASS.
- G29 atlas workflow run `41220697081`: Windows failed closed at `scripts/build_code_atlas.py --check-if-present` because the indexed source file set is stale; Linux had reached the same failure and was still in regeneration when inspected. G29/full integration qualification is NOT PASS.
- Full final regression after atlas refresh: NOT EXECUTED / NOT QUALIFIED.
- Bayesian predictive accuracy, causal benefit, task reward, restart-under-interference benefit, unfamiliar transfer: NOT TESTED.
- Recurrent comparator is a small fixed-reservoir/online-readout control, not a capable tuned recurrent learner.
- No original-world first-use or protected cohort was accessed. FSA-04 #83 remains OPEN.

## Next gate

1. Refresh the G29 advisory source atlas using the repository's canonical generator against the exact current PR tree; do not hand-edit generated content.
2. Complete G29 and mandatory final integration/full regression.
3. Build a common canonical checkpoint envelope and account for resident state bytes, Python/runtime RSS and inference/training compute on calibrated repeated runs.
4. Add a stronger Bayesian/model-based comparator with interactions or learned transition structure, and a genuinely trained recurrent/state-space baseline. Keep this diagonal baseline as a minimum transparent control.
5. Evaluate efficacy only under independently admitted, preregistered FIT/CHECK/TRANSFER cohorts after FSA first-use authority is qualified.

No PR merge, accepted-ref change, model integration, runtime activation, cohort dispatch or promotion is authorized by this receipt.
