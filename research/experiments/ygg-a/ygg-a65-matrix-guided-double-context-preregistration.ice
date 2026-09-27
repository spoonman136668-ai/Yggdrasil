YGG-A65 PREREGISTRATION — MATRIX-GUIDED REPAIR UNDER TWO SIMULTANEOUS CONTEXT FLIPS
Parent A64 valid PAIR_SPECIFIC_SUPPRESSOR_MATRIX.
Question: does the frozen A64 single-context suppressor matrix compose well enough to select a causal pair that remains effective under two simultaneous context perturbations?
Freeze exact A64 substrate: replicate6 runtime/programs/native arrivals, donor3 corruption [16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Freeze the exact A64 seven-pair suppressor matrix.
Candidate double-context cases are exactly the37 unordered phase3 context pairs (k,l) for which exactly one frozen causal pair P:
- contains neither k nor l;
- is not suppressed by k individually;
- is not suppressed by l individually.
The selected pair for each case is that unique P; no post-result selection.
For each case evaluate:
- PAIR_P anchor: P alone abolishes collapse.
- P_PLUS_k anchor: P+k abolishes collapse per A64.
- P_PLUS_l anchor: P+l abolishes collapse per A64.
- P_PLUS_k_l: flip exactly the two pair positions plus k and l.
Classification:
SINGLE_CONTEXT_MATRIX_COMPOSES if all37 P_PLUS_k_l arms abolish collapse in both modes.
COMPOUND_CONTEXT_BREAKS_SELECTOR if at least one quadruple restores collapse and modes agree.
CROSS_MODE_COMPOSITION_DIFFERENCE if quadruple outcomes differ between modes.
ANCHOR_NOT_REPRODUCED if any frozen pair or single-context anchor fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact37 frozen unique-selector cases derived from A64 only; exact selected pair per case; only registered four stream labels vary in compound arm; exact pair/triple anchors; corruption fixed; []/[2] exact; deterministic duplicate; globals restored.
Scientific negatives are valid. No post-result tuning.
