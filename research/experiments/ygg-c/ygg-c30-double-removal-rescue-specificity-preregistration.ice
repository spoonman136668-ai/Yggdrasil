YGG-C30 PREREGISTRATION — ADDITION SPECIFICITY IN THE BASE_MINUS42_MINUS46 FAILURE STATE
Parent C29 valid COOPERATIVE_42_46_SUPPRESSION.
Question: at levels10..12, is cell41 specifically able to rescue the failing BASE_38_TO_42 minus{42,46} state, or can many absent cells substitute?
Freeze exact C29 substrate: replicate8 identity, 38->42 repaired base, alpha0.134765625, levels10,11,12, exact manifests/weights/task/scheduler/retention/maturity, deterministic.
At each level:
- reproduce BASE_38_TO_42 rescue;
- reproduce BASE_REMOVE42_REMOVE46 failure;
- reproduce BASE_REMOVE42_REMOVE46_ADD41 rescue.
Let F be the exact failing BASE_REMOVE42_REMOVE46 lesion at that level.
For every cell c in0..63 not currently present in F, evaluate ADD_c = F union {c}, changing exactly one membership.
This includes cells42 and46 themselves as restoration controls and41 as the inherited rescue anchor.
Report rescuing_additions and failing_additions at every level.
Classification:
CELL41_UNIQUE_NOVEL_RESCUER if among additions other than restoration controls42/46, only41 rescues all levels10..12.
SMALL_RESCUER_SET if 41 rescues all and 1..5 additional non-control cells also rescue all.
BROAD_ADDITION_RESCUE if >5 additional non-control cells rescue all.
CELL41_NOT_PORTABLE if41 fails any level.
ANCHOR_NOT_REPRODUCED if inherited base/double-removal/+41 anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact levels10..12; alpha/replicate/base exact; exhaustive absent-cell additions per level; exactly one added membership per arm; 41/42/46 controls present; non-lesion fields preserved; duplicate byte-identical; globals restored.
Scientific negatives are valid. No post-result tuning.
