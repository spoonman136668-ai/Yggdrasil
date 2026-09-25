TITLE: YGG-A20 Integrated Fine Recovery Map Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: a8d562506ce989acbb79c416b0163399016c1df0
PARENT_EXPERIMENT: YGG-A19

QUESTION
At what exact nested lesion level does stream service recover under the fully integrated alpha=1.0 + 58-repair regime after the observed L13 failure?

FROZEN
All A19 task, manifests, alpha, learned weights, repair schedule, terminal-integrity contract, scheduler, horizon, service capacity, thresholds, deterministic execution, and L8 stream anchor remain exact.

LEVELS
Test exact C5 nested hash-ranked lesions:
L13, L14, L15, L16.

Each level is inherited L8 plus the first (level-8) cells ranked by:
h64("YGG-C3-RESOURCE-PRESSURE", seed, cell), then cell.

STREAM RETENTION
Use exact C3 rule versus the A15 alpha=1.0 L8 damage-ON anchor:
for every replicate, phase, and stream with L8 count >=4,
current count must be >=75% of L8.

ANCHOR
L13 must reproduce YGG-A19 exactly:
stream_noncollapse=false
single failure replicate=6, phase=4, stream=S, L8=5, current=3, ratio=.6.

REPORT
For every level:
- exact lesion lineage/cardinality;
- all stream failures;
- aggregate correct_done and damage ratio;
- repair/terminal/maturity/matching integrity;
- learned-arm exercise.

CLASSIFICATION
Let R be the first tested level in {13,14,15,16} with stream_noncollapse=true.

If no level recovers: NO_RECOVERY_THROUGH_L16.
If R exists and all tested levels >=R also pass: THRESHOLD_LIKE_RECOVERY_AT_R.
Otherwise: IRREGULAR_RECOVERY.

No classification is required to be positive.

VALIDITY
- strict one-cell nesting across 13..16;
- L13 accepted failure exact;
- non-lesion fields frozen;
- all 58 repairs exact;
- all capability/integrity gates exact;
- duplicate complete execution byte-identical;
- all runtime/harness globals restored.

SUCCESS
YGG_A20_INTEGRATED_FINE_RECOVERY_MAP=true iff evidence is valid and exactly one preregistered classification is produced.

FAILURE
Do not change lesions, thresholds, alpha, repair count, task, weights, scheduler, horizon, or service capacity after results.

BOUNDARY
Diagnostic mapping only; no baseline mutation, online adaptation, or recursive self-modification.
