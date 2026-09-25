TITLE: YGG-A22 L16 Controller-Family Stream Attribution Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: cb882666823b2384c7a83e032f74b4b4c9b31b21
PARENT_EXPERIMENT: YGG-A21

QUESTION
Under the exact A-task L16 pressure context at alpha=.25 with branch repair OFF, is the hidden stream-collapse boundary specific to learned-controller family U_A25 or also present under fixed-controller family U_A0?

NORTH-STAR TARGET
Separate controller-family effects from task/lesion-context effects before changing the developmental architecture.

FROZEN
- exact A21/A20 task, ten manifests, nested L8 and L16 lesion construction, scheduler, horizon, service capacity, maturity, matching, terminal-integrity, and thresholds;
- alpha=.25;
- repair OFF only;
- exact learned weights;
- deterministic execution;
- no retraining or online adaptation.

CONDITIONS
Controller family:
U_A0
U_A25

For each mode:
- run exact L8 repair-OFF anchor;
- run exact L16 repair-OFF condition;
- compare L16 stream service to the same-mode L8 anchor.

STREAM-NONCOLLAPSE
Exact C3 rule:
for every replicate, phase, and stream, if same-mode L8 completed count >=4 then L16 count must be >=75% of L8.

INTEGRITY
For both modes:
- exact L8/L16 nested lesions;
- non-lesion manifest fields frozen;
- zero scheduled/applied/repaired branch damage;
- incorrect_done=0;
- matching integrity exact;
- maturity.pass=true;
- horizon-aware terminal integrity=true;
- L16 aggregate correct_done / L8 aggregate correct_done >=.90.

CLASSIFICATION
BOTH_FAIL:
U_A0 and U_A25 both fail stream noncollapse.

LEARNED_CONTROLLER_ONLY:
U_A0 passes, U_A25 fails.

FIXED_CONTROLLER_ONLY:
U_A0 fails, U_A25 passes.

BOTH_PASS:
both pass.

No classification is required to be favorable.

DUPLICATION / RESTORATION
Complete two-mode experiment must be byte-identical across duplicate runs.
Runtime alpha, validator, lesion_set, damage schedule, and temporary adapters restored exactly.

SUCCESS
YGG_A22_L16_CONTROLLER_FAMILY_ATTRIBUTION=true iff all validity/integrity gates pass and exactly one preregistered classification is produced.

FAILURE
Do not alter controller definitions, alpha, lesions, thresholds, task, scheduler, horizon, or service capacity after results.

BOUNDARY
Diagnostic only.
No baseline mutation.
No online adaptation.
No recursive self-modification.
