YGG-C28 PREREGISTRATION — SINGLE-REMOVAL COMPENSATION FOR C27 UNIVERSALLY CRITICAL ADDITIONS
Parent C27 run 36316836609 valid ONE_TOGGLE_UNIVERSAL_CRITICAL with universal critical additions cells4,5,41.
Question: after adding one universally forbidden cell to the 38->42 repaired state, can removing exactly one currently present lesion cell restore rescue under the same fixed pressure?
Freeze exact corrected C27 substrate: replicate8 identity, below alpha0.134765625, levels8..16, exact manifests/weights/task/scheduler/retention/maturity, deterministic.
At each level:
- reproduce ORIGINAL_R8 failing and BASE_38_TO_42 rescuing anchors.
- reproduce ADD_c failure for each c in {4,5,41}.
- for each critical c and every cell r currently present in BASE_38_TO_42, evaluate COMP_c_REMOVE_r = BASE + c - r. These arms preserve base cardinality exactly.
Do not exclude cells38/42 or any other present cell; exhaustive current-base membership is required at each level.
Report per critical c and level exact rescuing_removals and failing_removals.
Classification:
ALL_CRITICAL_ADDITIONS_COMPENSABLE if each c has at least one rescuing removal at every level8..16.
PARTIAL_CRITICAL_COMPENSABILITY if at least one c/level has a rescuing removal but the above universal condition fails.
NO_SINGLE_REMOVAL_COMPENSATION if no compensation arm rescues anywhere.
ANCHOR_NOT_REPRODUCED if base or critical-addition anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact critical set{4,5,41}; exact levels; alpha/replicate exact; exact38->42 base; exhaustive base-present removals for each c/level; every compensation differs from base by exactly +c and -r and preserves cardinality; non-lesion fields preserved; duplicate byte-identical; globals restored.
Scientific negatives are valid. No post-result tuning.
