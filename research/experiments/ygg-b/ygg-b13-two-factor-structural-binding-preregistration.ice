TITLE: YGG-B13 Two-Factor Structural Binding Cartesian Holdout Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 2e3ab27ad17ff3d55665c24d491b8d941f601ac4
PARENT_EXPERIMENT: YGG-B12

QUESTION
Can the B12 compact persistent-memory mechanism compose over two independent structural factors, ROLE and SLOT, while preserving the successful two-dimensional value channel and exact 24-scalar persistent-state budget?

NORTH-STAR TARGET
Advance from single-factor role binding to deeper compositional structure without adding memory capacity, attention, external memory, or evaluation-time adaptation.

FROZEN FROM YGG-B12
- KEYS=8
- VALUES=8
- key/address dimension=8
- value dimension=2
- memory shape=2x8
- pending address register=8
- persistent_state_scalars=24
- learned_parameters=104
- train_examples=8192
- eval_examples=4096
- batch_size=256
- epochs=75
- optimizer=Adam
- learning_rate=0.005
- seeds=111,222,333,444,555
- deterministic CPU execution
- RESET and VALUE_SHUFFLE control semantics
- B12 capability thresholds unless explicitly extended below.

STRUCTURE
ROLES=2
SLOTS=2
Each sequence chooses two distinct entities.
For each entity instantiate all four ROLE x SLOT addresses:
R0/S0, R0/S1, R1/S0, R1/S1.
Thus every sequence contains exactly eight bindings and a query selecting one of those eight addresses.

Binding token form:
KEY, ROLE, SLOT, VALUE

Query token form:
QUERY_KEY, QUERY_ROLE, QUERY_SLOT

sequence_length=35

FIXED STRUCTURAL OPERATORS
ROLE masks:
R0 = [1,1,1,1,1,1,1,1]
R1 = [1,-1,1,-1,1,-1,1,-1]

SLOT masks:
S0 = [1,1,1,1,1,1,1,1]
S1 = [1,1,-1,-1,1,1,-1,-1]

address(k,r,s) =
L2_normalize(key_embedding[k] * ROLE_MASK[r] * SLOT_MASK[s])

All masks are fixed and non-learned.
The same address operator is used for memory write and query read.

MODEL
key_embedding: 8 x 8
value_embedding: 8 x 2
terminal_readout: linear 2 -> 8 classes
learned_parameters=104 exactly

PERSISTENT STATE
memory M: 2 x 8 = 16 scalars
pending address register: 8 scalars
total persistent_state_scalars=24 exactly

CARTESIAN HOLDOUT
A quadruple (key,role,slot,value) is held out iff:
(key + 2*role + 3*slot + value) mod 4 == 0

This withholds exactly 64 of 256 possible quadruples:
exactly two values for every key/role/slot address.
Every key, role, slot, value, and key/role/slot address remains represented in training through allowed quadruples.

TRAINING DATA
For each sequence:
- choose two distinct keys;
- instantiate all eight key/role/slot addresses;
- choose each binding value only from allowed quadruples;
- query one of the eight addresses uniformly;
- target is the value bound to the queried address.

OOD EVALUATION
Use the same two-key/eight-address structure.
The queried address receives a held-out value for that exact key/role/slot address.
All other bindings receive allowed values.
Target is the held-out value.

CONTROLS
RESET:
Reset M and pending state before every token.

VALUE_SHUFFLE:
Randomly permute the eight binding values within each evaluation sequence while leaving all structural and query tokens unchanged.

ROLE_FLIP:
Flip R0<->R1 on every binding role token while leaving the query role unchanged.

SLOT_FLIP:
Flip S0<->S1 on every binding slot token while leaving the query slot unchanged.

SUCCESS
- minimum OOD persistent accuracy >= 0.90
- median OOD persistent accuracy >= 0.95
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum value-shuffle degradation >= 0.40
- minimum role-flip degradation >= 0.40
- minimum slot-flip degradation >= 0.40
- all five seeds persistent > reset, value-shuffle, role-flip, and slot-flip
- persistent state exactly 24 scalars
- learned parameter count exactly 104
- no held-out quadruple appears in training
- all 64 held-out quadruples appear in scored evaluation for every seed
- duplicate complete execution byte-identical

MECHANICAL GATE
Confirm:
- exact preregistered role masks;
- exact preregistered slot masks;
- all four role/slot mask products are distinct;
- value dimension exactly 2;
- memory shape exactly 2x8;
- state exactly 24;
- parameters exactly 104;
- structural masks are non-learned;
- each generated sequence contains all eight structural addresses.

FAILURE
Any unmet frozen capability gate is a scientific negative.
Do not change masks, state budget, thresholds, schedule, seeds, task, holdout, or controls after observing results.

INTERPRETATION
Positive:
The compact B12 mechanism supports a second compositional structural factor under the same persistent-state budget.

Negative:
The B12 mechanism has reached a structural-composition boundary despite solving single-factor role binding; the next experiment should localize whether the boundary is address interference, eight-binding superposition load, or structural depth.

BOUNDARY
No shared-baseline promotion from B13 alone.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
