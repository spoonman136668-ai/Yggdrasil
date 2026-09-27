YGG-A47 PREREGISTRATION — SINGLE-EVENT PHASE3 TIMING DECOMPOSITION
Parent A46 run 36284325097 valid WITHIN_PHASE_TIMING_SENSITIVE.
Frozen donor3 base phase3 corruption IDs are [105,113,118], offsets [9,17,22].
Question: which individual phase3 corruption event timings are sufficient to change singleton-cell2 collapse when the other two phase3 events remain fixed?
Freeze exact A46 substrate: replicate6 runtime/programs/arrival stream, donor3 non-phase3 corruption IDs [16,38,146], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
For each base phase3 event e in [105,113,118], construct 32 arms by replacing only e with 96+s for s in 0..31 while the other two phase3 events remain exactly fixed.
If replacement duplicates another fixed event, that arm is mechanically invalid and omitted; report the omission explicitly.
The base arm for each family is the original event offset and must reproduce collapse.
No other corruption ID changes.
Classification:
NO_SINGLE_EVENT_TIMING_EFFECT if every valid single-event move in all three families retains collapse.
SINGLE_EVENT_TIMING_SENSITIVE if exactly one event family contains both collapsing and noncollapsing valid arms.
SUBSET_EVENT_TIMING_SENSITIVE if exactly two event families contain both outcomes.
ALL_THREE_EVENT_TIMING_SENSITIVE if all three event families contain both outcomes.
CROSS_MODE_SINGLE_EVENT_DIFFERENCE if outcome matrices differ by mode.
ANCHOR_NOT_REPRODUCED if any family base arm does not collapse.
OTHER_VALID_PATTERN otherwise.
Validity: exact donor3 base schedule; exact three event families; only one event replaced per arm; non-phase3 IDs unchanged; phase3 count remains3; duplicate-free schedules only; fixed runtime/program/arrivals exact; []/[2] exact; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
