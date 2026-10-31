# YGG-DB01 — Development-only sensory feedback feasibility

Parent source: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`
Branch: `research/ygg-db01-development-only`
Status: EXPLORATORY; NO SCIENTIFIC RESULT; NO NATIVE LEARNING CLAIM.

## Frozen question
Can a fixed-capacity shared local developmental update receive temporally patterned sensory signals, and can future controlled training establish a causal behavioral benefit from predictable success feedback versus irregular failure feedback?

## Boundaries
The repository currently contains an accepted DG-1 NCA *design* but no verified executable native DG-1 update in its source atlas. PublicCausalCells is a conventional comparator and must not be reported as DG-1 cognition. No accepted research refs, schedulers, production paths, or autonomous loops are modified.

## Proposed first stages
1. Implement a standalone deterministic, fixed-capacity 2D Moore-neighborhood developmental update and structural tests, without claiming trained capability.
2. Add a pure feedback encoder: success => regular beat train; failure => irregular noise. Feed temporal samples only through explicit local input; do not expose outcome bits or hidden labels.
3. Validate deterministic replay, input locality, no hidden capacity growth, reverse/no-feedback/sham controls and equal compute/data budgets.
4. Freeze a separate complete preregistration (seeds, split, task, data hashes, thresholds, budgets and evaluator) **before** primary learning runs. No primary run is authorized by this note.

## Scientific interpretation
Adapter unit-test PASS is not learning improvement. Even if trained behavior improves, distinguish predictable structure, noise amplitude, valence, information leakage, and reward equivalence through controls. Report negative results unchanged.

## Authority
Research-only source branch. No production, promotion, scheduler, queue, owner, or protected first-use authority.
