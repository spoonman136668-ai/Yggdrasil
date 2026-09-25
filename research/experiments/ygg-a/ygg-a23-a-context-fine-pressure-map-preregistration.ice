TITLE: YGG-A23 A-Context Fine Pressure Map Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: 3613dd94d6e9242245d63374d5d0be6ed4340180
PARENT_EXPERIMENT: YGG-A22

QUESTION
What is the exact L8-L16 stream-retention pattern in the A-task execution context under fixed and learned controller families?

NORTH-STAR TARGET
Localize the hidden service-quality boundary to task/execution context before attempting a repair mechanism.

FROZEN
- exact A22/A21 task, ten manifests, scheduler, horizon, service capacity, maturity, matching, terminal-integrity, and thresholds;
- alpha=.25;
- repair OFF;
- exact learned weights;
- deterministic execution;
- no retraining or online adaptation.

MODES
U_A0
U_A25

PRESSURE LEVELS
L8,L9,L10,L11,L12,L13,L14,L15,L16.

LESION CONSTRUCTION
Exact C5 nested one-cell construction:
inherited L8 plus first (level-8) cells ranked by
h64("YGG-C3-RESOURCE-PRESSURE", seed, cell), then cell.

STREAM-NONCOLLAPSE
For each mode separately, use its own L8 anchor.
If L8 completed count >=4 for a replicate/phase/stream, a pressure level passes only if current count >=75% of that L8 count.

INTEGRITY
For every mode/level:
- exact nested lesion cardinality;
- non-lesion fields frozen;
- zero branch damage;
- incorrect_done=0;
- matching integrity exact;
- maturity.pass=true;
- horizon-aware terminal integrity=true;
- aggregate correct_done / same-mode L8 >=.90.

REPORT
For each mode:
- stream_noncollapse_by_level;
- exact failure cells per level;
- first failure;
- first recovery after failure, if any;
- max passing level;
- aggregate correct_done ratios.

CROSS-MODE CLASSIFICATION
IDENTICAL_MAPS:
U_A0 and U_A25 stream-noncollapse maps are identical.

A25_WEAKER:
every U_A25 passing level also passes U_A0, with at least one extra U_A0 pass.

A25_STRONGER:
every U_A0 passing level also passes U_A25, with at least one extra U_A25 pass.

CROSSING_MAPS:
neither passing set contains the other.

SUCCESS
YGG_A23_A_CONTEXT_FINE_PRESSURE_MAP=true iff all evidence is valid and exactly one preregistered classification is produced.

FAILURE
Do not alter modes, alpha, lesion construction, thresholds, task, scheduler, horizon, or service capacity after results.

BOUNDARY
Diagnostic only.
No accepted baseline mutation.
No online adaptation.
No recursive self-modification.
