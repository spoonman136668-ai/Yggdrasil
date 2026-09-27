YGG-C24 PREREGISTRATION — CELL2 REMOVAL VS CELL6 ADDITION ONE-SIDED DECOMPOSITION
Parent C23 run 36282449458 valid SINGLE_REVERSION_FRAGILE.
Question: are the two dominant reverse-lesion factors independently sufficient to destroy the full partner6 rescue, or were the C23 failures consequences of cardinality-preserving replacement itself?
Freeze exact corrected C23/C22 substrate: replicate8 identity, partner6 full rescuing lesion donor, below alpha 0.134765625, levels8..16, exact manifests/weights/task/scheduler/retention/maturity, deterministic. No retraining/adaptation/threshold/topology/baseline mutation.
At each level reproduce:
- ORIGINAL_R8 failing anchor;
- FULL_PARTNER6 rescuing anchor.
Evaluate from FULL_PARTNER6 the following exact arms when referenced cells are present in the level-specific unique sets:
A remove partner6-unique cell2 only (cardinality -1);
B remove neutral-control partner6-unique cell10 only (cardinality -1);
C add replicate8-unique cell6 only (cardinality +1);
D add neutral-control replicate8-unique cell14 only (cardinality +1);
E replace 2->6 (cardinality preserved; inherited universal-failure anchor);
F replace 10->14 (cardinality preserved; inherited universal-rescue control).
Cell10 and cell14 are frozen neutral controls because C23 pair10->14 was mature at every level8..16, while 10->6 and 2->14 were universal failures.
Classification:
BOTH_FACTORS_INDEPENDENTLY_SUFFICIENT if remove2-only fails all eligible levels while remove10-only rescues, and add6-only fails all eligible levels while add14-only rescues.
CELL2_REMOVAL_SUFFICIENT if only the removal contrast shows that pattern.
CELL6_ADDITION_SUFFICIENT if only the addition contrast shows that pattern.
REPLACEMENT_INTERACTION_REQUIRED if one-sided suspect arms rescue but inherited 2->6 fails.
MIXED_ONE_SIDED_CAUSALITY for any other stable valid pattern.
ANCHOR_NOT_REPRODUCED if original/full-partner or inherited 2->6 / 10->14 anchors fail.
Validity: exact alpha/levels/replicate8/partner6; dynamic eligibility of cells attested; one-sided cardinalities exact; matched control cardinalities exact; inherited replacement anchors exact where eligible; non-lesion fields preserved; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
