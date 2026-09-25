TITLE: YGG-B17 Three-Dimensional Value-Channel Entity Binding Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 61110520572d9e43b976ff900fd0fd187274a5cf
STRUCTURAL_PARENT: YGG-B15

QUESTION
Does increasing only the value/superposition channel from 2D to 3D recover the two-entity/four-binding structural generalization lost in B15?

NORTH-STAR TARGET
Resolve the entity-binding capacity boundary before increasing sequence load or beginning language capability experiments.

FROZEN FROM YGG-B15
- exact learned 8x8 entity/key embedding;
- exact ROLE and SLOT masks;
- exact two distinct entities per sequence;
- exactly two distinct ROLE×SLOT addresses per entity;
- four bindings total;
- sequence length=19;
- KEYS=8, ROLES=2, SLOTS=2, VALUES=8;
- address dimension=8;
- exact Cartesian holdout rule;
- exact training/evaluation corpus generation;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=0.005;
- seeds=111,222,333,444,555;
- RESET, VALUE_SHUFFLE, ROLE_FLIP, SLOT_FLIP controls;
- all accuracy and causal thresholds unchanged;
- deterministic CPU execution.

SCIENTIFIC CHANGE
value_dimension: 2 -> 3

Consequences:
memory: 2x8 -> 3x8
pending address register: unchanged 8
persistent_state_scalars: 24 -> 32
learned_parameters: 104 -> 120

No address geometry, task structure, entity count, binding count, holdout, optimizer, threshold, or training-schedule change.

MODEL
key_embedding: 8 x 8
fixed ROLE masks
fixed SLOT masks
value_embedding: 8 x 3
terminal_readout: linear 3 -> 8 classes
persistent_state_scalars=32
learned_parameters=120

SUCCESS
- minimum OOD persistent accuracy >=0.90
- median OOD persistent accuracy >=0.95
- maximum reset accuracy <=0.35
- minimum persistent-reset gap >=0.50
- minimum value-shuffle degradation >=0.40
- minimum role-flip degradation >=0.40
- minimum slot-flip degradation >=0.40
- all five seeds persistent > reset, value-shuffle, role-flip, slot-flip
- state exactly 32 scalars
- parameters exactly 120
- no held-out quadruple in training
- all 64 held-out quadruples scored per seed
- duplicate complete execution byte-identical.

MECHANICAL GATE
- exact B15 learned entity geometry path;
- exact ROLE/SLOT masks;
- two entities and four bindings;
- value dimension=3;
- memory shape=3x8;
- state=32;
- parameters=120;
- sequence length=19.

INTERPRETATION
Positive:
The B15 multi-entity boundary is primarily a value/superposition capacity limit, extending the B11/B12 value-width mechanism to multi-entity structural binding.

Negative:
A 3D value channel is insufficient; entity multiplicity imposes an additional structural constraint beyond the B11/B12 capacity mechanism.

FAILURE
Do not alter value width, state budget, thresholds, task, entities, bindings, masks, seeds, holdout, optimizer, or training schedule after observing results.

BOUNDARY
Diagnostic state expansion only; no compact-model promotion.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
