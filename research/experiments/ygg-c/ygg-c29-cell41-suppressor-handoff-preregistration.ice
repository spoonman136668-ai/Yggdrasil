YGG-C29 PREREGISTRATION — CELL41 SUPPRESSOR HANDOFF AT MID-PRESSURE GAP
Parent C28 valid PARTIAL_CRITICAL_COMPENSABILITY.
Question: at levels10..12, where ADD41 is not repaired by any single removal, do the early suppressor42 and late suppressor46 cooperate when removed together, or is rescue explained by a generic two-removal/cardinality effect?
Freeze exact C28 substrate: replicate8 identity, 38->42 repaired base, alpha0.134765625, levels10,11,12 only, exact manifests/weights/task/scheduler/retention/maturity, deterministic.
At each level reproduce:
- BASE_38_TO_42 rescue.
- ADD41 failure.
- ADD41_REMOVE42 failure.
- ADD41_REMOVE46 failure.
Evaluate:
A ADD41_REMOVE42_REMOVE46.
Matched control:
B ADD41_REMOVE6_REMOVE14, using two removals that individually failed to compensate cell41 throughout C28 mid-pressure levels.
Also record BASE_REMOVE42_REMOVE46 and BASE_REMOVE6_REMOVE14 without ADD41 as structural controls.
Classification:
COOPERATIVE_42_46_SUPPRESSION if A rescues all levels10..12 and B fails all.
GENERIC_TWO_REMOVAL_RESCUE if both A and B rescue all levels10..12.
PARTIAL_PAIR_SUPPRESSION if A rescues at least one but not all middle levels.
NO_PAIR_SUPPRESSION if A fails all levels10..12.
ANCHOR_NOT_REPRODUCED if inherited base/add41/single-removal anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact levels10..12; alpha/replicate/base exact; registered cell changes only; A/B each +41 and exactly two removals; structural controls exact; non-lesion fields preserved; duplicate byte-identical; globals restored.
Scientific negatives are valid. No post-result tuning.
