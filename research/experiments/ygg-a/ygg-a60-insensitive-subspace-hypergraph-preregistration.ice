YGG-A60 PREREGISTRATION — EXHAUSTIVE VALIDATION OF THE A57-A59 CAUSAL HYPERGRAPH
Parents: A57 PAIRWISE_REDUNDANT_CAUSALITY, A58 GENUINE_THIRD_ORDER_CAUSALITY, A59 GENUINE_FOURTH_ORDER_CAUSALITY.
Question: within the eight A56 single-flip-insensitive positions, does the frozen set of discovered minimal causal hyperedges predict collapse/noncollapse for every possible flip combination?
Freeze exact A59 native substrate: replicate6 runtime/programs/arrival stream, donor3 corruption [16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Frozen vertex set I={103,105,106,111,117,121,123,125}.
Frozen minimal causal hyperedges:
Pairs E2={(103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123)}.
Triples E3={(105,106,121),(105,121,125),(106,123,125),(111,117,121),(111,117,125),(111,121,125)}.
Quadruple E4={(103,105,123,125)}.
Evaluate every one of the 2^8=256 subsets S of I exactly once per mode, flipping precisely the stream labels in S.
Frozen model prediction:
- predict NONCOLLAPSE iff S contains at least one frozen hyperedge from E2 union E3 union E4.
- otherwise predict COLLAPSE.
The empty set is the native collapse anchor; all A57/A58/A59 tested subsets must reproduce.
Classification:
HYPERGRAPH_MODEL_EXACT if observed collapse/noncollapse matches prediction for all256 subsets in both modes.
MISSING_HIGHER_ORDER_EDGE if at least one predicted-collapse subset actually abolishes collapse.
NONMONOTONE_EDGE_FAILURE if at least one subset containing a frozen hyperedge nevertheless still collapses.
CROSS_MODE_SUBSPACE_DIFFERENCE if observed subset outcomes differ between modes.
ANCHOR_NOT_REPRODUCED if native/lower-order frozen anchors fail.
OTHER_VALID_PATTERN otherwise.
Report false_positive_subsets, false_negative_subsets, and exact mismatch sets.
Validity: exact256 unique subsets per mode; only registered stream labels vary; rid/t/bits/programs fixed; all other arrivals exact; corruption fixed; []/[2] exact; frozen E2/E3/E4 exact; known lower-order anchors reproduced; deterministic duplicate; globals restored.
Scientific negatives are valid. No post-result tuning.
