TITLE: YGG-B9 Orthogonal Role-Subspace Cartesian Holdout Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 7e9640e2328eebeb154ca4baf7cdb26553b9a0a7
PARENT_EXPERIMENT: YGG-B8

QUESTION
Can explicit non-overlapping role subspaces eliminate cross-role address interference and recover role-sensitive compositional generalization under the same compact persistent-state and parameter budgets?

FROZEN FROM B6-B8
- exact entity/role/value task and 14-token sequence;
- exact training/evaluation generation and Cartesian triple holdout;
- 8192 training examples, 4096 OOD examples;
- batch_size=256, epochs=75, Adam, learning_rate=0.005;
- seeds=111,222,333,444,555;
- exact RESET, VALUE_SHUFFLE, ROLE_FLIP controls;
- persistent_state_scalars=16;
- learned_parameters=88;
- exact B7/B8 success thresholds.

SCIENTIFIC CHANGE
Keep one learned 8-dimensional key vector per key.
Construct addresses by fixed role masks:
R0 mask = [1,1,1,1,0,0,0,0]
R1 mask = [0,0,0,0,1,1,1,1]

address(k,r) = L2_normalize(key_embedding[k] * role_mask[r])

The same operator is used for write and query.
Cross-role address dot products are exactly zero by construction.
No learned role parameters are added.

RATIONALE
B7 and B8 both preserved strong role causality but retained high address cosine interference on multiple seeds. B9 tests the stronger representation hypothesis that role identity needs dedicated orthogonal subspaces rather than a transform within one fully shared address space.

SUCCESS
Unchanged:
- minimum OOD persistent accuracy >= 0.90
- median OOD persistent accuracy >= 0.95
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum value-shuffle degradation >= 0.40
- minimum role-flip degradation >= 0.40
- all five seeds causal direction
- persistent state exactly 16
- learned parameters exactly 88
- no held-out triple in training
- all 32 held-out triples scored per seed
- duplicate complete execution byte-identical

DIAGNOSTIC
Report maximum cross-role absolute address cosine separately from maximum same-role off-diagonal cosine.

FAILURE
Any unmet frozen capability gate is a scientific negative.
Do not change masks, dimensions, thresholds, schedule, seeds, task, or holdout after observing results.

BOUNDARY
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
