TITLE: YGG-A21 L16 Alpha-by-Repair Stream Attribution Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: 8856415561fcae6bf43db7bc58152021fe5ff872
PARENT_EXPERIMENT: YGG-A20

QUESTION
At exact nested L16, is the hidden stream-collapse boundary primarily driven by learned-control blend strength, branch-repair interaction, or both?

NORTH-STAR TARGET
Identify the integration variable responsible for the service-quality failure revealed by A20 before designing a repair.

FROZEN
- exact A20/A19 task, ten manifests, L16 nested lesion geometry, scheduler, horizon, service capacity, maturity, matching, terminal-integrity, and learned weights;
- exact branch-repair mechanism and 58-event schedule when repair is ON;
- deterministic execution;
- no retraining or online adaptation.

FACTORIAL
Learned-control alpha:
0.25
0.50
1.00

Repair state:
OFF
ON

For each alpha, build a same-alpha L8 anchor and a same-alpha L16 condition.
For repair OFF compare L16 OFF against L8 OFF.
For repair ON compare L16 ON against L8 ON.

STREAM-NONCOLLAPSE
Use the exact C3 rule:
for each replicate, phase, and stream, if same-alpha L8 completed count >=4 then L16 completed count must be >=75% of that L8 count.

INTEGRITY / CAPABILITY
At every alpha:
- exact L16 nested lesion;
- non-lesion fields frozen;
- repair OFF has zero scheduled/applied/repaired branch damage;
- repair ON has exactly 58 scheduled/applied/repaired with 29 B + 29 C;
- all ON repairs precede D;
- no unrepaired terminal branch;
- d_while_branch_incorrect=0;
- incorrect_done=0;
- matching integrity exact;
- maturity.pass=true;
- horizon-aware terminal integrity=true;
- ON aggregate correct_done / same-alpha OFF >=.95;
- every-world ON/OFF correct_done ratio >=.90;
- learned arm materially exercised.

CLASSIFICATION
Report the exact 3x2 stream-noncollapse matrix.

ALPHA_DOMINANT:
repair OFF and ON share the same pass/fail pattern across alpha and at least one alpha transition exists.

REPAIR_DOMINANT:
at least one alpha has repair OFF pass and repair ON fail, while alpha alone does not explain the matrix.

MIXED_ALPHA_REPAIR:
both alpha transitions and repair-state differences occur.

NO_STREAM_FAILURE_AT_L16:
all six conditions pass.

PERSISTENT_STREAM_FAILURE:
all six conditions fail.

OTHER_VALID_PATTERN:
any other valid deterministic matrix.

No classification is required to be favorable.

DUPLICATION / RESTORATION
Complete six-cell factorial must be byte-identical across duplicate runs.
Runtime alpha, validator, lesion_set, damage schedule, and any patched harness functions must be restored exactly.

SUCCESS
YGG_A21_L16_ALPHA_BY_REPAIR_ATTRIBUTION=true iff all evidence is valid and one preregistered classification is produced.

FAILURE
Do not alter alpha levels, lesion geometry, repair schedule, thresholds, task, weights, scheduler, horizon, or service capacity after observing results.

BOUNDARY
Diagnostic only.
No accepted baseline mutation.
No online adaptation.
No recursive self-modification.
