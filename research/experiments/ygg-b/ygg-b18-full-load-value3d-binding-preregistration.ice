TITLE: YGG-B18 Full-Load Three-Dimensional Value Binding Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: eb2d0192d36d22e423f8c5552e69e52d5363e079
MECHANISM_PARENT: YGG-B17
STRUCTURAL_PARENT: YGG-B13

QUESTION
Does the 3D value/superposition channel that solved B17 also solve the full two-entity/eight-binding ROLE×SLOT task that failed in B13?

NORTH-STAR TARGET
Determine whether multi-entity structural composition is ready for higher sequence intelligence, or whether an eight-binding capacity boundary remains.

FROZEN FROM YGG-B13
- exact two distinct entities per sequence;
- all four ROLE×SLOT addresses for each entity;
- exactly eight bindings total;
- sequence length=35;
- KEYS=8, ROLES=2, SLOTS=2, VALUES=8;
- address dimension=8;
- exact learned entity/key embedding path;
- exact fixed ROLE/SLOT masks;
- exact Cartesian holdout rule;
- exact training/evaluation corpus construction;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=0.005;
- seeds=111,222,333,444,555;
- RESET, VALUE_SHUFFLE, ROLE_FLIP, SLOT_FLIP controls;
- exact B13 capability thresholds;
- deterministic CPU execution.

SCIENTIFIC CHANGE
Use B17's proven value mechanism:
value_dimension: 2 -> 3
memory: 2x8 -> 3x8
persistent_state_scalars: 24 -> 32
learned_parameters: 104 -> 120

No entity count, binding count, address dimension, masks, task structure, holdout, threshold, seed, optimizer, or training-schedule change.

SUCCESS
- minimum OOD persistent accuracy >=0.90
- median OOD persistent accuracy >=0.95
- maximum reset accuracy <=0.35
- minimum persistent-reset gap >=0.50
- minimum value-shuffle degradation >=0.40
- minimum role-flip degradation >=0.40
- minimum slot-flip degradation >=0.40
- all five seeds persistent > all controls
- state exactly 32 scalars
- parameters exactly 120
- no held-out quadruple in training
- all 64 held-out quadruples scored per seed
- duplicate complete execution byte-identical.

MECHANICAL GATE
- exact B13 eight-binding structural corpus;
- one sequence contains all eight entity×ROLE×SLOT addresses;
- exact B13 ROLE/SLOT masks;
- value dimension=3;
- memory shape=3x8;
- state=32;
- parameters=120;
- sequence length=35.

INTERPRETATION
Positive:
The B13 failure was predominantly a value/superposition capacity boundary. A 3D value channel supports two-entity, two-factor composition at the full eight-binding load.

Negative:
Even with B17's successful value capacity, eight-binding load remains beyond the current mechanism; locate the load boundary before language.

FAILURE
Do not alter value width, state budget, thresholds, task, entities, bindings, masks, seeds, holdout, optimizer, or training schedule after results.

BOUNDARY
Diagnostic state expansion only.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
