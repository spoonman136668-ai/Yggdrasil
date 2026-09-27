YGG-A66 PREREGISTRATION — ALTERNATE CAUSAL ROUTES FOR A65 COMPOUND-CONTEXT FAILURES
Parent A65 run36346244037 valid COMPOUND_CONTEXT_BREAKS_SELECTOR.
Question: when the A64-selected pair fails under two simultaneous context flips, does another frozen A57 causal pair remain effective under the same compound context?
Freeze exact A65/A64 substrate: replicate6 runtime/programs/native arrivals, donor3 corruption[16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Frozen A57 causal pair set P:
(103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123).
Frozen failed A65 contexts and selected pairs:
(97,103)->(105,111)
(97,105)->(103,111)
(98,117)->(105,111)
(99,105)->(103,111)
(106,121)->(105,117)
For each context pair(k,l):
- reproduce the selected-pair compound failure exactly;
- for every causal pair(i,j) in P with i,j not in{k,l}, evaluate flip(i,j,k,l);
- no pair overlapping a context position is eligible.
Report exact effective_pairs per context = eligible pairs whose compound arm abolishes collapse.
Classification:
ALTERNATE_ROUTE_EXISTS_ALL if every one of five contexts has at least one effective pair.
PARTIAL_ALTERNATE_ROUTE if at least one but not all contexts have an effective pair.
NO_ALTERNATE_ROUTE if none of the five contexts has any effective pair.
CROSS_MODE_FALLBACK_DIFFERENCE if effective-pair sets differ between modes.
ANCHOR_NOT_REPRODUCED if any A65 selected-pair compound failure fails to reproduce.
OTHER_VALID_PATTERN otherwise.
Validity: exact five contexts; exact frozen pair set; eligibility mechanical and frozen; every compound arm changes exactly four distinct registered stream labels; selected A65 failures exact; corruption fixed; []/[2] exact; deterministic duplicate; globals restored.
Scientific negatives are valid. No post-result tuning.
