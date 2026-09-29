YGG-A74 PREREGISTRATION — OUTER SINGLETON BOUNDARY

Parent A73 valid LEFT_WINDOW_EXTENDS_INTO_GAP. Across both U_A0 and U_A25, the observed singleton rescue set in positions 101..107 is {101,102,104,107}; positions 103,105,106 collapse. A72 also established rescue at 97,98,99,100,108,109.

Question: do the singleton-rescue regions extend beyond the previously tested outer positions 97 and 109?

Freeze exact A73 substrate:
- replicate6 runtime/programs/native arrivals;
- donor3 corruption [16,38,146,118];
- alpha=.25;
- modes U_A0 and U_A25;
- target cell2;
- exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules;
- repair off;
- deterministic execution.

Evaluate EMPTY plus exactly these singleton positions:
94,95,96,97,109,110,111,112.
No pair or compound arm is permitted.

Inherited anchors:
- EMPTY collapses in both modes.
- singleton 97 rescues in both modes.
- singleton 109 rescues in both modes.

Report the singleton rescue set in each mode.

Classification:
OUTER_WINDOWS_CLOSED if 94,95,96,110,111,112 all collapse in both modes while 97 and 109 rescue.
LEFT_OUTER_EXTENSION if one or more of 94,95,96 rescue and none of 110,111,112 rescue, with identical sets across modes.
RIGHT_OUTER_EXTENSION if one or more of 110,111,112 rescue and none of 94,95,96 rescue, with identical sets across modes.
BILATERAL_OUTER_EXTENSION if at least one position on each side rescues with identical sets across modes.
CROSS_MODE_OUTER_BOUNDARY if the rescue sets differ across modes.
ANCHOR_NOT_REPRODUCED if EMPTY/97/109 fails to reproduce.
OTHER_VALID_PATTERN otherwise.

Validity: exact nine arms per mode; exact candidate positions; singleton-only changes; only registered stream changes; corruption fixed; []/[2] lesions exact; deterministic duplicate; runtime/program/global state restored.
Scientific negatives are valid. No post-result tuning.
