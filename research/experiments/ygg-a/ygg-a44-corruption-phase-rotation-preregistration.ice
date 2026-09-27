YGG-A44 PREREGISTRATION — COUNT-PRESERVING CORRUPTION PHASE ROTATION
Parent A43 run 36282823011 valid CORRUPTION_SCHEDULE_DOMINANT.
Question: does singleton-cell2 sensitivity depend on the temporal/developmental phase placement of a corruption schedule, rather than merely its event count and internal spacing?
Freeze exact A43 substrate: replicate6 runtime seed/context/anchors, exact replicate6 programs and replicate6 arrival/content stream, alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic, no retraining/adaptation/threshold/topology/baseline changes.
Donor corruption schedules: exact primary request seeds for donors [1,2,3,4,5,6,7,8,9,10], generating corruption IDs against the fixed replicate6 arrival stream exactly as A43.
For each donor schedule S and phase rotation k in [0,1,2,3,4], construct S_k = sorted(((rid + 32*k) mod 160) for rid in S).
This preserves corruption-event count and all pairwise circular spacings while moving the schedule across the five 32-request developmental phases.
Evaluate exact [] versus [2] under each S_k with the inherited A28 collapse predicate.
Anchors: k=0 must reproduce A43 donor collapse set exactly [3,6,8,10] (native donor6 plus partner donors3,8,10) in both modes.
Classification:
PHASE_PLACEMENT_INVARIANT if every donor has the same collapse outcome for all five rotations.
PHASE_SENSITIVE if at least one donor changes collapse outcome across rotations and both modes agree on the full donor/rotation pattern.
CROSS_MODE_PHASE_DIFFERENCE if the donor/rotation collapse matrices differ by mode.
ANCHOR_NOT_REPRODUCED if k=0 donor outcomes differ from [3,6,8,10].
OTHER_VALID_PATTERN otherwise.
Validity: donor IDs exact; rotation set exact; corruption count preserved for every arm; circular-spacing multiset preserved; exact fixed runtime/program/arrival stream; []/[2] exact; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
