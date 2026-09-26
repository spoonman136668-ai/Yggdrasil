TITLE: YGG-C18 Near-Onset Retention Predicate Attribution Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_RESULT: YGG-C17 BELOW_WEAKER

QUESTION
At alpha 0.134765625, why are all pressure levels marked unretained even where stream_noncollapse and completion-area metrics match the above-onset arm?

FROZEN DIAGNOSTIC
Reuse exact C17 evidence and parent retention predicate. Do not change alpha, pressure levels, thresholds, learned weights, manifests, or scheduler. Decompose every retained=false decision into its constituent predicate failures and identify the first differing predicate versus alpha 0.1357421875.

SUCCESS
Classify MATURITY_COUNT_GATED, STREAM_COLLAPSE_GATED, COMPLETION_GATED, MULTI_PREDICATE, or UNEXPLAINED_PREDICATE_DIVERGENCE with exact per-level evidence.

BOUNDARY
Attribution only. No threshold relaxation or post-result tuning.
