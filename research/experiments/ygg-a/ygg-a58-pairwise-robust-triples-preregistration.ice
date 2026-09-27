YGG-A58 PREREGISTRATION — THIRD-ORDER INTERACTIONS AMONG A57 PAIRWISE-ROBUST SETS
Parent A57 run 36317382651 valid PAIRWISE_REDUNDANT_CAUSALITY.
Question: do genuinely third-order stream-history interactions exist among A56-insensitive positions after excluding every triple that already contains an A57 sensitive pair?
Freeze exact A57 native substrate: replicate6 runtime/programs/arrival stream, donor3 corruption [16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Frozen insensitive set I={103,105,106,111,117,121,123,125}.
Frozen A57 sensitive-pair set E={(103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123)}.
Candidate triples are exactly all unordered triples from I containing no pair in E. There are 23 such triples.
Arms per mode:
- NATIVE anchor.
- inherited eight SINGLE_k anchors and 28 PAIR_i_j anchors sufficient to re-establish A57 map.
- exactly 23 TRIPLE_i_j_k candidate arms, each flipping only those three stream labels.
Primary sensitive_triples = candidate triples that abolish collapse.
Classification:
GENUINE_THIRD_ORDER_CAUSALITY if at least one candidate triple abolishes collapse.
PAIRWISE_MODEL_SUFFICIENT_WITHIN_I if all23 candidate triples retain collapse.
CROSS_MODE_TRIPLE_DIFFERENCE if sensitive-triple sets differ across modes.
PAIR_ANCHOR_NOT_REPRODUCED if A57 single/pair map differs.
NATIVE_ANCHOR_NOT_REPRODUCED if native no longer collapses.
OTHER_VALID_PATTERN otherwise.
Validity: exact candidate set derived solely from frozen I/E; exactly23 candidate triples; registered stream labels only; rid/t/bits/programs fixed; all other arrivals exact; corruption fixed; []/[2] exact; A57 map reproduced; deterministic duplicate; globals restored.
Scientific negatives are valid. No post-result tuning.
