YGG-C27 PREREGISTRATION — FULL ONE-TOGGLE NEIGHBORHOOD OF 38->42 RESCUE
Parent C26 run 36312692184 valid BASINS_COMPATIBLE; C22 established exact 38->42 universal rescue.
Question: how robust is the universally rescuing 38->42 lesion state to any single cell-membership toggle under the same fixed pressure conditions?
Freeze exact corrected C26/C22 substrate: replicate8 identity, below alpha0.134765625, levels8..16, exact manifests/weights/task/scheduler/retention/maturity, deterministic.
At each level:
- reproduce ORIGINAL_R8 failing anchor;
- construct BASE_38_TO_42 = original replicate8 lesion with cell38 removed and cell42 added; this must rescue.
- for each cell c in 0..63, create exactly one TOGGLE_c arm:
  if c is in BASE_38_TO_42 remove it; otherwise add it.
No other lesion cell changes.
Report per cell the exact fail_levels and rescue_levels across8..16.
Classification:
ONE_TOGGLE_BASIN_ROBUST if every one of the64 toggles rescues at every level.
ONE_TOGGLE_UNIVERSAL_CRITICAL if at least one cell toggle fails at every level8..16.
MIXED_ONE_TOGGLE_BASIN if at least one toggle fails somewhere and no toggle fails at all nine levels.
ANCHOR_NOT_REPRODUCED if original/base anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact levels8..16; alpha exact; replicate8 exact; exact38->42 base; exactly64 unique toggle arms each level; each arm differs from base by exactly one cell membership; non-lesion fields preserved; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
