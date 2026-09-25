TITLE: YGG-A18 L12 Stream-Failure Attribution Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: f5906290375b5dfac8415e5cb2b612deb74ac17a
PARENT_EXPERIMENT: YGG-A17

QUESTION
Is the unresolved L12 replicate-6/phase-4/S stream collapse caused by the L12 topology under full learned control itself, or does the 58-event branch-repair workload contribute materially?

FROZEN
All A17 manifests, L12 construction, alpha=1.0, task, weights, scheduler, horizon, service capacity, repair semantics, thresholds, and deterministic execution remain exact.

CONDITIONS
Using the exact A15 alpha=1.0 L8 anchor, compute the C3 stream-noncollapse rule separately for:
1. L12 U_A25 damage OFF
2. L12 U_A25 damage ON

For each condition report every failing replicate/phase/stream cell and ratio relative to the matched L8 condition.

ATTRIBUTION CATEGORIES
TOPOLOGY_ONLY_IDENTICAL:
damage OFF and ON fail on the exact same cells with exact same completed counts.

TOPOLOGY_DOMINANT_DIFFERENT:
both fail, but failure sets/counts differ.

REPAIR_INDUCED:
damage OFF passes globally while damage ON fails.

REPAIR_RESCUES:
damage OFF fails while damage ON passes globally.

BOTH_PASS:
both pass globally.

VALIDITY
- exact A17 L12 nested topology;
- exact A15 L8 alpha=1.0 anchor;
- damage OFF contains zero scheduled branch damage;
- damage ON contains exact 58 repairs, 29 B + 29 C;
- all matching, maturity, terminal integrity, duplicate execution, and restoration gates exact.

SUCCESS
YGG_A18_L12_STREAM_FAILURE_ATTRIBUTION=true iff evidence is valid and exactly one preregistered attribution category is produced. No category is required to be positive.

FAILURE
Do not alter topology, repair workload, stream threshold, alpha, task, or weights after observing results.

BOUNDARY
Diagnostic attribution only. No accepted baseline mutation, online adaptation, or recursive self-modification.
