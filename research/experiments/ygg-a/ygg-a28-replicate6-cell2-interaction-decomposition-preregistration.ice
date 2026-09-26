TITLE: YGG-A28 Replicate-6 Cell-2 Interaction Decomposition Preregistration
DATE: 2026-09-26
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_RESULT: YGG-A27 REPLICATE6_CONTEXT_SPECIFIC
PARENT_RUN: 36229807712

QUESTION
Which member or members of replicate 6's frozen L11 lesion are necessary for the cell-2-induced stream-collapse phenotype observed in YGG-A27?

FROZEN
- exact YGG-A27 replicate-6 manifest, task, scheduler, horizon, service capacity, maturity, matching, terminal-integrity and stream-noncollapse rules;
- alpha=.25; repair OFF; exact learned weights; U_A0 and U_A25;
- target cell 2; deterministic execution; no retraining or online adaptation.

DESIGN
Use actual manifest replicate 6 only. Anchor is its exact frozen L11 lesion. Positive control is L11 plus cell 2. For each cell x in the original L11 lesion, test (L11 minus x) plus cell 2, preserving cardinality 11. No other manifest field may change.

REPORT
For both modes report exact stream-phase counts, stream-collapse predicate, correct_done, maturity, matching, terminal integrity and zero branch damage for anchor, positive control, and every leave-one-out arm.

CLASSIFICATION
SINGLE_NECESSARY_PARTNER: exactly one removed L11 cell abolishes the cell-2 collapse in both modes.
MULTIPLE_NECESSARY_PARTNERS: more than one removed L11 cell abolishes collapse in both modes.
CROSS_MODE_INTERACTION: abolishing sets differ between modes.
DISTRIBUTED_CONTEXT: no single leave-one-out removal abolishes collapse in either mode.
OTHER_VALID_PATTERN: valid evidence matches none above.

SUCCESS
YGG_A28_REPLICATE6_CELL2_INTERACTION_DECOMPOSITION=true iff evidence is valid, duplicate complete execution is byte-identical, actual replicate ID is verified as 6, and exactly one preregistered classification is emitted.

FAILURE
Do not change target cell, lesion membership, thresholds, task, alpha, repair state, scheduler, horizon, service capacity, or classification rules after results.

BOUNDARY
Diagnostic only. No accepted baseline mutation. No online adaptation. No recursive self-modification.
END
