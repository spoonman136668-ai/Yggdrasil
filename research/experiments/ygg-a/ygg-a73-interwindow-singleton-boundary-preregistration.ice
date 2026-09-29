YGG-A73 PREREGISTRATION — INTERWINDOW SINGLETON BOUNDARY

Parent A72 valid LOCAL_WINDOW_BROADENING with identical singleton rescue set {97,98,99,100,101,107,108,109} in both U_A0 and U_A25. Positions 105 and 106 collapse in both modes.

Question: where is the exact singleton-rescue boundary between the broadened left window ending at 101 and the right rescue window beginning at 107?

Freeze exact A72 substrate:
- replicate6 runtime/programs/native arrivals;
- donor3 corruption [16,38,146,118];
- alpha=.25;
- modes U_A0 and U_A25;
- target cell2;
- exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules;
- repair off;
- deterministic execution.

Evaluate EMPTY plus exactly these singleton positions:
101,102,103,104,105,106,107.
No pair or compound arm is permitted.

Inherited anchors:
- EMPTY collapses in both modes.
- singleton 101 rescues in both modes.
- singleton 105 collapses in both modes.
- singleton 106 collapses in both modes.
- singleton 107 rescues in both modes.

Report the singleton rescue set in each mode.

Classification:
BOUNDARY_AT_101 if positions 102,103,104,105,106 all collapse in both modes while 101 and 107 rescue.
LEFT_WINDOW_EXTENDS_INTO_GAP if one or more of 102,103,104 rescue with identical rescue sets across modes.
CROSS_MODE_BOUNDARY if the rescue sets differ across modes.
ANCHOR_NOT_REPRODUCED if EMPTY/101/105/106/107 fails to reproduce.
OTHER_VALID_PATTERN otherwise.

Validity: exact eight arms per mode; exact candidate positions; singleton-only changes; only registered stream changes; corruption fixed; []/[2] lesions exact; deterministic duplicate; runtime/program/global state restored.
Scientific negatives are valid. No post-result tuning.
