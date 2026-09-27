YGG-C25 PREREGISTRATION — SYMMETRIC CELL2/CELL6 REPAIR DIRECTION
Parent C24 run 36304396514 valid BOTH_FACTORS_INDEPENDENTLY_SUFFICIENT.
Question: starting from the original failing replicate8 lesion, is adding partner6 cell2 or removing replicate8 cell6 independently sufficient to restore maturity?
Freeze exact corrected C24 substrate: replicate8 identity, below alpha0.134765625, levels8..16, exact manifests/weights/task/scheduler/retention/maturity, deterministic.
At every level reproduce:
- ORIGINAL_R8 failing anchor;
- FULL_PARTNER6 rescuing anchor.
From ORIGINAL_R8 evaluate:
A add cell2 only (cardinality +1).
B add neutral-control cell10 only (+1).
C remove cell6 only (-1).
D remove neutral-control cell14 only (-1).
E add2 + remove6 (cardinality preserved).
F add10 + remove14 neutral paired control (cardinality preserved).
Cell2/cell10 are partner6-unique and cell6/cell14 replicate8-unique at all levels by C24 eligibility.
Classification:
BOTH_FACTORS_INDEPENDENTLY_REPAIR if add2-only rescues all levels while add10-only fails, and remove6-only rescues all while remove14-only fails.
CELL2_ADDITION_REPAIRS if only the addition contrast is universally specific.
CELL6_REMOVAL_REPAIRS if only the removal contrast is universally specific.
PAIR_REQUIRED_FOR_REPAIR if one-sided suspect arms fail but add2+remove6 rescues all.
MIXED_REPAIR_DIRECTION for any other stable valid pattern.
ANCHOR_NOT_REPRODUCED if original/full-partner anchors fail.
Validity: exact alpha/levels/replicate8; required cell eligibility exact; one-sided cardinalities exact; paired cardinality exact; non-lesion fields preserved; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
