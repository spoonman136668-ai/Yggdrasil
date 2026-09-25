TITLE: YGG-B11 Two-Dimensional Value-Channel Capacity Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 4d5ad6590f2f4fa9e8454cd81c61a2c78f932f6a
STRUCTURAL_PARENT: YGG-B9
B9_PARENT_CLOSURE: 540d004b8a99b3b909f074e143fd699f3c9a367d

QUESTION
Is the remaining role-conditioned Cartesian-holdout boundary primarily caused by the inherited one-dimensional value channel, and does expanding only value representation/readout to two dimensions recover the frozen capability while preserving B9's exact role-subspace address mechanism?

FROZEN FROM B9
- exact entity/role/value task and 14-token sequence;
- exact two-entity, two-role, four-binding structure;
- exact Cartesian held-out triple rule: (key + 2*role + value) mod 4 == 0;
- exact training/evaluation corpus generation;
- train_examples=8192;
- eval_examples=4096;
- batch_size=256;
- epochs=75;
- optimizer=Adam;
- learning_rate=0.005;
- seeds=111,222,333,444,555;
- exact RESET, VALUE_SHUFFLE, ROLE_FLIP controls;
- exact B9 learned 8-dimensional key embedding;
- exact B9 disjoint role masks:
  R0=[1,1,1,1,0,0,0,0]
  R1=[0,0,0,0,1,1,1,1]
- exact normalized address construction;
- no learned role parameters;
- deterministic CPU execution.

SCIENTIFIC CHANGE
Change only value representation and memory value width:
- value_embedding: 8 x 2 instead of 8 x 1;
- memory M: 2 x 8 instead of 1 x 8;
- terminal_readout: linear 2 -> 8 instead of linear 1 -> 8.

ADDRESS / ROLE GEOMETRY
Unchanged from B9.
Cross-role address dot product remains exactly zero by construction.
Same-role entity geometry remains learned exactly as in B9.

PERSISTENT STATE
Memory M: 2 x 8 = 16 scalars.
Pending address register: 8 scalars.
Total persistent_state_scalars=24.

LEARNED PARAMETERS
key embedding: 8 x 8 = 64
value embedding: 8 x 2 = 16
readout weight: 8 x 2 = 16
readout bias: 8
total learned_parameters=104

RATIONALE
B9 eliminated cross-role interference but retained severe same-role address collapse and achieved OOD accuracy 0.71-0.90.
B10 showed that replacing learned geometry with a fixed low-coherence address codebook made performance substantially worse.
This suggests learned address geometry carries useful structure and shifts the next bottleneck candidate to the scalar value/superposition channel.
B11 tests that candidate directly.

MECHANICAL GATE
Confirm before primary interpretation:
- value dimension exactly 2;
- memory shape 2 x 8;
- persistent state exactly 24 scalars;
- learned parameter count exactly 104;
- role masks exactly B9;
- cross-role address cosine <= 1e-7;
- duplicate execution deterministic.

SUCCESS
Use B9 capability thresholds unchanged:
- minimum OOD persistent accuracy >= 0.90
- median OOD persistent accuracy >= 0.95
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum value-shuffle degradation >= 0.40
- minimum role-flip degradation >= 0.40
- all five seeds persistent > reset, value-shuffle, and role-flip
- persistent state exactly 24 scalars
- learned parameter count exactly 104
- no held-out triple appears in training
- all 32 held-out triples scored per seed
- duplicate complete execution byte-identical

FAILURE
Any unmet frozen capability gate is a scientific negative.
Do not change value width, state budget, B9 masks, thresholds, seeds, training schedule, task, or holdout after observing results.

INTERPRETATION
Positive:
The scalar value channel was the dominant remaining bottleneck under B9's learned address geometry.

Negative:
A two-dimensional value channel is insufficient; the next hypothesis must involve richer binding/readout structure or learned geometry regularization rather than simple value-width expansion.

BOUNDARY
This is a diagnostic state-budget expansion, not a compact-model promotion.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
