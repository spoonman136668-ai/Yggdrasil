TITLE: YGG-A26 A24/A25 Equivalence Reconciliation Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_RESULTS: YGG-A24, YGG-A25

QUESTION
Why did A24 report replicate-6 collapse for the L11+cell59 arm while A25 reported no collapse for replicate 6 under its intended L11+cell59 arm?

FROZEN DIAGNOSTIC
No scientific threshold or scheduler changes. Reconstruct replicate 6 in both parent code paths and compare, byte-for-byte where applicable: base manifest, L11 lesion, added cell, final lesion, validator normalization, runtime lesion_set, stream-phase outputs, state/trace hashes, controller mode, alpha, and all non-lesion fields.

SUCCESS
Produce exactly one evidence-backed classification: INPUT_DIVERGENCE, VALIDATION_DIVERGENCE, RUNTIME_DIVERGENCE, SCORING_DIVERGENCE, or EXACT_EQUIVALENCE_REQUIRES_DEFECT_REVIEW.

BOUNDARY
Reconciliation only. No repair or tuning until discrepancy is explained.
