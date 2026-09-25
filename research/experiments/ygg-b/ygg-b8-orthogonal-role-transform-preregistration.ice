TITLE: YGG-B8 Orthogonal Role-Transform Cartesian Holdout Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 152c32eb62f4310e149d878bc38915be6806068e
PARENT_EXPERIMENT: YGG-B7

QUESTION
Can a fixed globally mixing orthogonal role transform reduce the address-geometry interference that remained after B7's elementwise sign binding, while preserving the compact persistent-state budget and all frozen role-sensitive compositional gates?

FROZEN FROM B6/B7
- exact entity/role/value task and 14-token sequence;
- exact training/evaluation generation;
- exact Cartesian triple holdout;
- 8192 training examples and 4096 OOD examples;
- batch 256, 75 epochs, Adam, learning_rate 0.005;
- seeds 111,222,333,444,555;
- exact RESET, VALUE_SHUFFLE, ROLE_FLIP controls;
- persistent_state_scalars=16;
- learned_parameters=88;
- all B7 success thresholds unchanged.

SCIENTIFIC CHANGE
Role R0 uses the learned key vector unchanged.
Role R1 uses a fixed normalized 8x8 Walsh-Hadamard transform H:
address(k,R0)=L2_normalize(key_embedding[k])
address(k,R1)=L2_normalize(H * key_embedding[k])

H is fixed, orthogonal, non-learned, and preregistered.
The same transform is used for memory write and query read.

No attention.
No external memory.
No learned role parameters.
No additional hidden state.
No evaluation-time adaptation.

RATIONALE
B7 raised persistent OOD accuracy to 0.66-0.85 but four seeds retained maximum address cosine above 0.99. A globally mixing orthogonal transform tests whether the remaining limitation is the local elementwise geometry of sign binding rather than role binding itself.

SUCCESS
Unchanged from B7:
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

FAILURE
Any unmet gate is a scientific negative.
Do not tune H, thresholds, training schedule, seeds, state budget, or task after observing results.

BOUNDARY
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
