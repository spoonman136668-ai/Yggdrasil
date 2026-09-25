TITLE: YGG-B14 Reduced-Load Two-Factor Structural Binding Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 48f00fbecefbe54e86c38dd0663fcd6bd116218e
PARENT_EXPERIMENT: YGG-B13

QUESTION
Was the YGG-B13 failure primarily caused by eight-binding superposition load, rather than ROLE×SLOT structural depth itself?

NORTH-STAR TARGET
Establish the sequence-composition capacity boundary before broadening toward language capability.

FROZEN FROM YGG-B13
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
- train_examples=8192
- eval_examples=4096
- batch_size=256
- epochs=75
- Adam learning_rate=0.005
- seeds=111,222,333,444,555
- exact RESET, VALUE_SHUFFLE, ROLE_FLIP, SLOT_FLIP semantics
- exact B13 success thresholds
- deterministic CPU execution.

SCIENTIFIC CHANGE
Reduce concurrent bindings only.

B13:
- two distinct entities per sequence
- all four ROLE×SLOT addresses for each entity
- eight bindings total.

B14:
- one entity per sequence
- all four ROLE×SLOT addresses for that entity
- four bindings total.

No model, state, mask, value width, threshold, optimizer, seed, holdout, or control change.

SEQUENCE
For one uniformly sampled key k, instantiate:
(k,R0,S0)
(k,R0,S1)
(k,R1,S0)
(k,R1,S1)

Binding token form:
KEY, ROLE, SLOT, VALUE

Query:
QUERY_KEY, QUERY_ROLE, QUERY_SLOT

sequence_length=19
bindings_per_sequence=4

CARTESIAN HOLDOUT
Unchanged:
(key + 2*role + 3*slot + value) mod 4 == 0

Exactly 64 of 256 possible quadruples remain held out globally.
Every key/role/slot address appears in training through allowed values.
OOD evaluation assigns a held-out value to the queried address and allowed values to the other three bindings.

SUCCESS
Unchanged from B13:
- minimum OOD persistent accuracy >= 0.90
- median OOD persistent accuracy >= 0.95
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum value-shuffle degradation >= 0.40
- minimum role-flip degradation >= 0.40
- minimum slot-flip degradation >= 0.40
- all five seeds persistent > reset, value-shuffle, role-flip, slot-flip
- persistent state exactly 24 scalars
- learned parameters exactly 104
- no held-out quadruple in training
- all 64 held-out quadruples scored for every seed
- duplicate complete execution byte-identical.

MECHANICAL GATE
Confirm:
- exact B13 ROLE masks;
- exact B13 SLOT masks;
- four distinct role/slot products;
- exactly one key and four structural addresses per sequence;
- value dimension=2;
- memory shape=2x8;
- persistent state=24;
- parameters=104.

INTERPRETATION
Positive:
B13's boundary is substantially attributable to concurrent superposition load; ROLE×SLOT depth itself remains viable at four bindings.

Negative:
Reducing concurrent binding load is insufficient, strengthening the case for a structural-depth/address-representation boundary.

FAILURE
Any unmet frozen gate is a scientific negative.
Do not tune binding count, thresholds, masks, dimensions, seeds, training schedule, holdout, or controls after results.

BOUNDARY
No shared-baseline promotion from B14 alone.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
