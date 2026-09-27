YGG-A48 PREREGISTRATION — EVENT118 TIMING × PHASE3 BACKGROUND FACTORIAL
Parent A47 run 36285542450 valid SINGLE_EVENT_TIMING_SENSITIVE.
Question: is the timing effect of the third phase3 corruption event sufficient across backgrounds, or does it require either of the other two phase3 corruption events?
Freeze exact A47 substrate: replicate6 runtime/programs/arrival stream, donor3 non-phase3 corruptions [16,38,146], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Factorial:
- event105 present vs absent;
- event113 present vs absent;
- third event placed at offset22 (request118; inherited collapsing timing) vs offset23 (request119; inherited noncollapsing timing from A47).
Eight arms per mode. No other corruption ID changes.
Anchors:
- 105 present,113 present,third offset22 must collapse;
- 105 present,113 present,third offset23 must not collapse.
Classification:
THIRD_EVENT_TIMING_SUFFICIENT if for all four 105/113 backgrounds offset22 collapses and offset23 does not.
BACKGROUND_DEPENDENT_THIRD_EVENT if the offset22-vs23 effect exists in some but not all backgrounds, with identical matrices across modes.
THIRD_EVENT_TIMING_LOST if no background distinguishes offset22 from offset23.
CROSS_MODE_FACTORIAL_DIFFERENCE if matrices differ across modes.
ANCHOR_NOT_REPRODUCED if inherited full-background anchors fail.
OTHER_VALID_PATTERN otherwise.
Report exact corruption count per arm; count variation is an explicit factorial consequence and is not normalized.
Validity: exact eight factorial arms; only 105/113 presence and third-event timing vary; non-phase3 IDs exact; no duplicate corruption IDs; fixed runtime/program/arrivals exact; []/[2] exact; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
