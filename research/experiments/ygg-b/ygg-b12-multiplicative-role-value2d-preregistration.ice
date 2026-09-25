TITLE: YGG-B12 Multiplicative-Role Two-Dimensional Value Cross-Confirmation Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: fcdca2a0ea0604fb9758a795c3bd71d56791cf06
MECHANISM_PARENT: YGG-B11
GEOMETRY_PARENT: YGG-B7

QUESTION
Does the two-dimensional value channel that rescued YGG-B11 also recover the frozen role-conditioned Cartesian-holdout capability under YGG-B7's full-width multiplicative role geometry?

PURPOSE
YGG-B11 converted the B9 role-subspace task from negative to positive by changing only the value channel from one dimension to two.
B12 cross-confirms whether that benefit generalizes across a different previously-tested role geometry rather than depending specifically on B9's disjoint role subspaces.

FROZEN TASK / TRAINING / CONTROLS
Preserve exactly from YGG-B6 through B11:
- entity/role/value task and 14-token sequence;
- two entities, both roles per entity, four bindings per sequence;
- Cartesian triple holdout: (key + 2*role + value) mod 4 == 0;
- train_examples=8192;
- eval_examples=4096;
- batch_size=256;
- epochs=75;
- Adam learning_rate=0.005;
- seeds=111,222,333,444,555;
- RESET, VALUE_SHUFFLE, ROLE_FLIP controls;
- deterministic CPU execution;
- all B11 capability thresholds unchanged.

FROZEN B7 ADDRESS GEOMETRY
key_embedding: 8 x 8 learned
R0 mask = [1,1,1,1,1,1,1,1]
R1 mask = [1,-1,1,-1,1,-1,1,-1]
address(k,r)=L2_normalize(key_embedding[k] * role_mask[r])
Masks are fixed and non-learned.
The same address operator is used for memory write and query read.

FROZEN B11 VALUE CHANNEL
value_embedding: 8 x 2
memory M: 2 x 8
terminal_readout: linear 2 -> 8

PERSISTENT STATE
memory=16 scalars
pending address=8 scalars
persistent_state_scalars=24 exactly

LEARNED PARAMETERS
key embedding=64
value embedding=16
readout weight=16
readout bias=8
learned_parameters=104 exactly

MECHANICAL GATE
Confirm before primary interpretation:
- role masks exactly equal frozen B7 masks;
- value dimension exactly 2;
- memory shape exactly 2 x 8;
- persistent state exactly 24;
- learned parameters exactly 104;
- both role-address operators are deterministic and use no learned role parameters;
- duplicate complete execution byte-identical.

SUCCESS
Use B11 thresholds unchanged:
- minimum OOD persistent accuracy >= 0.90
- median OOD persistent accuracy >= 0.95
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum value-shuffle degradation >= 0.40
- minimum role-flip degradation >= 0.40
- all five seeds persistent > reset, value-shuffle, and role-flip
- persistent state exactly 24
- learned parameters exactly 104
- no held-out triple in training
- all 32 held-out triples scored per seed
- duplicate complete execution byte-identical

INTERPRETATION
Positive:
The B11 value-width effect generalizes across B7's full-width multiplicative role geometry, strengthening the conclusion that scalar value/superposition capacity was a general bottleneck.

Negative:
The B11 rescue depends materially on interaction with B9's disjoint role-subspace geometry; the next model must jointly account for address geometry and value-channel capacity.

FAILURE
Any unmet frozen capability gate is a scientific negative.
Do not alter masks, value width, state budget, thresholds, seeds, schedule, task, holdout, or controls after observing results.

BOUNDARY
No shared-baseline promotion from B12 alone.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
