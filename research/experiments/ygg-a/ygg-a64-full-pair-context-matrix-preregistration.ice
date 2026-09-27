YGG-A64 PREREGISTRATION — COMPLETE CAUSAL-PAIR x PHASE3-CONTEXT SUPPRESSOR MATRIX
Parents A61-A63.
Question: across all seven frozen A57 causal pairs, which phase3 context positions suppress each pair, and is there any shared suppressor core?
Freeze exact A63 substrate: replicate6 runtime/programs/native arrivals, donor3 corruption [16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Pairs:
(103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123).
For each pair(i,j):
- NATIVE collapses.
- each singleton i/j collapses.
- pair(i,j) abolishes collapse.
- for every phase3 k in96..127 excluding i,j, evaluate exactly triple(i,j,k): 30 contexts per pair.
Total scientific context arms:210 per mode.
Report per pair exact suppressor set S_ij, suppressor frequency for every phase3 rid, intersection across all seven pairs, union, and pairwise Jaccard overlap.
Inherited anchors: A61 suppressor set for(106,117), A62 set for(105,111), and A63 request99 outcomes must reproduce exactly.
Classification:
GLOBAL_SUPPRESSOR_CORE if intersection across all seven S_ij is nonempty.
PAIR_SPECIFIC_SUPPRESSOR_MATRIX if intersection is empty and every pair has at least one suppressor.
MIXED_SUPPRESSOR_MATRIX if some pair has no suppressors or another valid pattern.
CROSS_MODE_MATRIX_DIFFERENCE if any S_ij differs between modes.
ANCHOR_NOT_REPRODUCED if any native/single/pair or inherited A61-A63 anchor fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact seven pairs; exact30 contexts per pair; exact210 contexts/mode; only registered stream labels vary; rid/t/bits/programs fixed; all other arrivals exact; corruption fixed; []/[2] exact; inherited sets exact; deterministic duplicate; globals restored.
Scientific negatives are valid. No post-result tuning.
