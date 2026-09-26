TITLE: YGG-C18 Retention Predicate Decomposition Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_RESULT: YGG-C17 BELOW_WEAKER

QUESTION
At alpha=.134765625, why is retention false at every lesion level despite matching integrity, near-baseline completion, and stream noncollapse at most levels?

FROZEN
Exact C17 alphas, lesion levels 8..16, learned weights, manifests, scheduler, horizon, pressure construction, and all existing thresholds. No threshold changes.

METHOD
Recompute C17 summaries without changing execution and expose every boolean term contributing to retained for each level. Attribute false retention to maturity, stream noncollapse, completion-ratio, matching/integrity, or any other existing predicate. Compare alpha=.134765625 against .1357421875 term-by-term. Do not redefine retained.

CLASSIFICATION
MATURITY_GATED; STREAM_GATED; COMPLETION_GATED; INTEGRITY_GATED; MULTI_PREDICATE_GATED; OTHER_VALID_PREDICATE.

SUCCESS
YGG_C18_RETENTION_PREDICATE_DECOMPOSITION=true iff original C17 outputs are reproduced exactly, duplicate analysis is byte-identical, and every false retained result is fully accounted for by existing frozen predicates.

BOUNDARY
Diagnostic decomposition only. No scientific threshold edits, learned-weight changes, or baseline mutation.
