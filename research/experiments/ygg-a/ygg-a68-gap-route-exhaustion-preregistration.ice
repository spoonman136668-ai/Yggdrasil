YGG-A68 PREREGISTRATION — EXHAUST ALL KNOWN CAUSAL ROUTES IN THE A67 GAP
Parent A67 valid TWO_ROUTE_REDUNDANCY_HAS_GAPS.
Question: under the sole uncovered double-context state(99,107), is every frozen A57 causal pair disabled, or can a pair that is individually suppressed by99 or107 re-emerge under the compound state?
Freeze exact A67/A64 substrate: replicate6 runtime/programs/native arrivals, donor3 corruption[16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Frozen causal pairs:
(103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123).
Context is exactly k=99,l=107. Neither is a member of any causal pair.
For every causal pair(i,j), evaluate:
PAIR_i_j
PAIR_i_j_PLUS_99
PAIR_i_j_PLUS_107
PAIR_i_j_PLUS_99_107
Inherited A67 anchor:
compound arms for(103,111) and(106,111) must collapse.
Frozen A64 individual-context suppressor expectations must reproduce for all seven pairs.
Report:
- compound_effective_pairs = pairs whose four-flip arm abolishes collapse;
- reactivated_pairs = compound-effective pairs for which99 or107 individually suppresses the pair.
Classification:
HIGHER_ORDER_ROUTE_REACTIVATION if at least one reactivated_pair exists.
ALTERNATE_ROUTE_WITHOUT_REACTIVATION if compound_effective_pairs nonempty but none are reactivated.
KNOWN_ROUTE_CAPACITY_EXHAUSTED if compound_effective_pairs empty.
CROSS_MODE_GAP_DIFFERENCE if compound effective sets differ across modes.
ANCHOR_NOT_REPRODUCED if A64 single-context or A67 compound anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact seven frozen pairs; exact context99/107; pair, two triples, quadruple per pair; all changed labels exact; corruption fixed; []/[2] exact; deterministic duplicate; globals restored.
Scientific negatives are valid. No post-result tuning.
