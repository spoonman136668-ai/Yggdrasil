YGG-C31 PREREGISTRATION — FULL-PRESSURE PORTABILITY OF C30 RESCUER CLASS
Parent C30 valid SMALL_RESCUER_SET.
Question: do the five novel rescuers of the BASE_38_TO_42 minus{42,46} state remain effective outside levels10..12, or is their equivalence class pressure-specific?
Freeze exact C30/C29 substrate: replicate8 identity, alpha0.134765625, levels8..16, exact manifests/weights/task/scheduler/retention/maturity, deterministic.
At each level construct:
BASE = exact38->42 repaired state.
F = BASE minus{42,46}.
Evaluate F and F+cell for exactly:
novel rescuers N={38,40,41,45,47}
restoration controls R={42,46}.
Record BASE outcome, F outcome, and each addition outcome.
Inherited anchors: at levels10..12 BASE rescues, F fails, and every addition in N union R rescues.
Primary:
- failure levels of F;
- rescue levels for each c in N union R;
- among F-failing levels, whether each novel rescuer restores rescue.
Classification:
NOVEL_RESCUERS_FULLY_PORTABLE if every c in N rescues at every level where F fails.
NOVEL_RESCUERS_PRESSURE_SPECIFIC if each inherited mid-pressure anchor reproduces but at least one c in N fails to rescue some other F-failing level.
NO_EXTRA_FAILURE_LEVELS if F fails only at inherited levels10..12 and all inherited rescue anchors reproduce.
ANCHOR_NOT_REPRODUCED if inherited C30 anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact levels8..16; alpha/replicate/base exact; exact F=-42/-46; exact N/R sets; exactly one registered addition per arm; inherited levels10..12 exact; duplicate byte-identical; globals restored.
Scientific negatives are valid. No post-result tuning.
