YGG-A46 PREREGISTRATION — PHASE3 WITHIN-PHASE CORRUPTION ROTATION
Parent A45 run 36283969522 valid MIXED_PHASE_PAIR_SENSITIVITY.
Frozen donor3 base corruption schedule under replicate6 runtime is [16,38,105,113,118,146], with phase3 events [105,113,118], corresponding to within-phase offsets [9,17,22].
Question: once the critical phase3 membership/count is preserved, does singleton-cell2 sensitivity depend on the exact within-phase timing of those three corruption events?
Freeze exact A45 substrate: replicate6 runtime/programs/arrival stream, donor3 schedule outside phase3 unchanged, alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic, no retraining/adaptation/threshold/topology/baseline changes.
Arms:
- for shift s in 0..31, replace each phase3 event 96+o with 96+((o+s) mod 32);
- all non-phase3 donor3 corruption events remain exact [16,38,146].
This preserves total corruption count, phase3 corruption count=3, and the circular-spacing multiset among the three phase3 events. Thirty-two arms total, including s=0 anchor.
Classification:
PHASE3_MEMBERSHIP_SUFFICIENT if all 32 shifts collapse in both modes.
WITHIN_PHASE_TIMING_SENSITIVE if at least one shift collapses and at least one shift does not, with identical shift pattern across modes.
PHASE3_BASE_ONLY if only s=0 collapses in both modes.
CROSS_MODE_WITHIN_PHASE_DIFFERENCE if shift patterns differ across modes.
ANCHOR_NOT_REPRODUCED if s=0 does not collapse.
OTHER_VALID_PATTERN otherwise.
Validity: exact donor3 schedule and phase3 offsets; shifts exactly 0..31; non-phase3 IDs unchanged; total and phase3 counts preserved; phase3 circular-spacing multiset preserved; fixed runtime/program/arrivals exact; []/[2] exact; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
