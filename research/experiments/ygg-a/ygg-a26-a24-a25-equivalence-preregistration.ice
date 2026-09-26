TITLE: YGG-A26 A24/A25 Equivalence Reconciliation Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_RESULTS: YGG-A24, YGG-A25

QUESTION
Why does A24 report replicate-6 phase-4 S collapse for L11 plus marginal cell 59 while A25 reports no collapse for replicate 6 under intended L11 plus cell 59?

FROZEN
Use exact A24 and A25 committed implementations, manifests, alpha=.25, U_A0/U_A25, repair-off state, scheduler, horizon, stream-noncollapse rule, learned weights, and deterministic execution. No threshold or architecture changes.

METHOD
For replicate 6 only, materialize the exact A24 rank-12 manifest and exact A25 target-cell manifest before execution. Compare canonical manifest bytes, lesion lists, lesion-set runtime behavior, validator path, non-lesion fields, and scored world outputs. If inputs are byte-identical, execute both call paths and compare result/stream-phase/state hashes. If inputs differ, identify the first differing field and provenance without correcting it in-run.

CLASSIFICATION
INPUT_DIVERGENCE; RUNTIME_BINDING_DIVERGENCE; EXECUTION_PATH_DIVERGENCE; EXACT_EQUIVALENCE_REPRODUCED; OTHER_VALID_DISCREPANCY.

SUCCESS
YGG_A26_A24_A25_EQUIVALENCE_RECONCILIATION=true iff duplicate execution is byte-identical, evidence integrity passes, and exactly one classification is produced.

BOUNDARY
Reconciliation only. Do not infer from A25 beyond the discrepancy until resolved. No repair/tuning/baseline mutation.
