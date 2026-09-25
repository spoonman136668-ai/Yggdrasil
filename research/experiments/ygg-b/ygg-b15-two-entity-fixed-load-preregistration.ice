TITLE: YGG-B15 Two-Entity Fixed-Load Structural Binding Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: dd5254209f72785ac27389171589b0f0bb74b6db
PARENT_EXPERIMENT: YGG-B14

QUESTION
At the exact successful B14 load of four concurrent bindings, does increasing from one entity to two entities impair ROLE×SLOT compositional generalization?

NORTH-STAR TARGET
Localize the B13 structural-composition boundary before increasing sequence load or moving toward language capability.

FROZEN FROM YGG-B14
- KEYS=8
- ROLES=2
- SLOTS=2
- VALUES=8
- address dimension=8
- value dimension=2
- memory shape=2x8
- pending address register=8
- persistent_state_scalars=24
- learned_parameters=104
- exact fixed ROLE masks
- exact fixed SLOT masks
- exact Cartesian quadruple holdout rule
- bindings_per_sequence=4
- sequence_length=19
- train_examples=8192
- eval_examples=4096
- batch_size=256
- epochs=75
- Adam learning_rate=0.005
- seeds=111,222,333,444,555
- exact RESET, VALUE_SHUFFLE, ROLE_FLIP, SLOT_FLIP controls
- exact B14/B13 capability thresholds
- deterministic CPU execution.

SCIENTIFIC CHANGE
Entity count only.

B14:
- one entity
- all four ROLE×SLOT addresses
- four bindings.

B15:
- two distinct entities
- exactly two distinct ROLE×SLOT addresses for each entity
- four bindings total.

For each entity independently, choose two of the four structural addresses by deterministic seeded random ranking. Across the frozen corpus all four ROLE×SLOT address types must be represented.

No model, memory, state, value width, mask, threshold, optimizer, seed, holdout, control, total binding count, or sequence length change.

CARTESIAN HOLDOUT
Unchanged:
(key + 2*role + 3*slot + value) mod 4 == 0

Exactly 64 of 256 possible quadruples remain held out globally.
OOD evaluation places a held-out value on the queried address and allowed values on the other three bindings.

SUCCESS
Unchanged:
- minimum OOD persistent accuracy >=0.90
- median OOD persistent accuracy >=0.95
- maximum reset accuracy <=0.35
- minimum persistent-reset gap >=0.50
- minimum value-shuffle degradation >=0.40
- minimum role-flip degradation >=0.40
- minimum slot-flip degradation >=0.40
- all five seeds persistent > reset, value-shuffle, role-flip, slot-flip
- persistent state exactly 24 scalars
- learned parameters exactly 104
- no held-out quadruple in training
- all 64 held-out quadruples scored for every seed
- duplicate complete execution byte-identical.

MECHANICAL GATE
Confirm:
- exact B14 ROLE/SLOT masks;
- two distinct entities per sequence;
- exactly two distinct structural addresses per entity;
- four bindings total;
- sequence length exactly 19;
- all four structural address types appear in a deterministic mechanical corpus;
- value dimension=2;
- memory shape=2x8;
- state=24;
- parameters=104.

INTERPRETATION
Positive:
Two-entity interference is not sufficient to explain B13. Combined with B14, the remaining boundary is primarily concurrent superposition load between four and eight bindings.

Negative:
Entity multiplicity itself contributes materially to the B13 boundary even at B14's successful total load.

FAILURE
Any unmet frozen capability gate is a scientific negative.
Do not change entity count, binding count, thresholds, masks, dimensions, seeds, schedule, holdout, or controls after results.

BOUNDARY
No shared-baseline promotion from B15 alone.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
