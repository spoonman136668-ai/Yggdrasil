YGG-A63 PREREGISTRATION — REQUEST99 PORTABILITY ACROSS ALL A57 CAUSAL PAIRS
Parent A62 valid PARTIAL_SUPPRESSOR_PORTABILITY; request99 suppressed both tested causal pairs.
Question: does request99 act as a portable suppressor across the complete frozen A57 pairwise causal set?
Freeze exact A62/A61 substrate: replicate6 runtime/programs/native arrivals, donor3 corruption [16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Frozen A57 causal pairs:
(103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123).
For every pair (i,j) and each mode evaluate:
- NATIVE anchor: collapse.
- SINGLE_i and SINGLE_j: collapse.
- PAIR_i_j: noncollapse.
- TRIPLE_i_j_99: flip exactly i,j,99.
Request99 is not a member of any tested pair.
Primary: rescued_pairs = pairs for which adding99 restores collapse.
Classification:
REQUEST99_GLOBAL_SUPPRESSOR if all7 pair+99 triples collapse.
REQUEST99_PARTIAL_SUPPRESSOR if 1..6 pair+99 triples collapse.
REQUEST99_NO_PORTABLE_EFFECT if none collapse.
CROSS_MODE_99_DIFFERENCE if rescued-pair sets differ across modes.
ANCHOR_NOT_REPRODUCED if any native/single/pair anchor fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact seven frozen pairs; exact native/two-single/pair/triple arms per pair; only registered stream labels vary; rid/t/bits/programs fixed; all other arrivals exact; corruption fixed; []/[2] exact; deterministic duplicate; globals restored.
Scientific negatives are valid. No post-result tuning.
