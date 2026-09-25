TITLE: YGG-B24 Two-Entity Temporal Overwrite Integration Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: d1f6c83915928771d948cb1f018307f73784b6f2
TEMPORAL_PARENT: YGG-B23
ENTITY_PARENT: YGG-B17

QUESTION
Can projection-overwrite temporal memory compose with the proven two-entity value3D structural-binding regime while preserving the latest value for either entity?

NORTH-STAR TARGET
Integrate multi-entity structural composition with genuine temporal update semantics before moving toward richer sequence/language tasks.

FROZEN MECHANISMS
From B17:
- two distinct entities per sequence;
- exactly two distinct ROLE×SLOT addresses per entity;
- learned 8x8 entity/key embedding;
- exact ROLE/SLOT masks;
- value dimension=3;
- memory=3x8;
- pending address register=8;
- persistent state=32;
- learned parameters=120;
- exact Cartesian holdout rule;
- exact optimizer/training schedule and seeds.

From B23:
- parameter-free projection overwrite:
  old <- M q
  M <- M - old q^T + v q^T
- latest-write query semantics;
- RESET, QUERY_ORDER_SWAP, VALUE_SHUFFLE, ROLE_FLIP, SLOT_FLIP controls;
- deterministic CPU execution.

TEMPORAL TASK
Six writes followed by one query:
1. generate the exact B15/B17 four-address two-entity structural set: two addresses for entity 0 and two for entity 1;
2. write all four once;
3. deterministically choose one of the two addresses for entity 0 and overwrite it;
4. deterministically choose one of the two addresses for entity 1 and overwrite it;
5. choose one of the two overwrite events as the query target;
6. latest overwrite value at the queried entity/address is the target.

Sequence length=27.

TRAIN/EVAL
TRAIN_N=8192
EVAL_N=4096
batch=256
epochs=75
Adam lr=.005
seeds=111,222,333,444,555

Training queried latest values come only from allowed quadruples.
Evaluation queried latest values come only from held-out Cartesian quadruples.
Original and overwrite values for each updated address must differ.

SUCCESS
- min persistent OOD latest-value accuracy >=.90
- median persistent >=.95
- max reset <=.35
- min persistent-reset gap >=.50
- min QUERY_ORDER_SWAP degradation >=.40
- min value-shuffle degradation >=.40
- min role-flip degradation >=.40
- min slot-flip degradation >=.40
- all five seeds causal direction true
- state exactly 32
- parameters exactly 120
- all 64 queried heldout quadruples scored per seed
- no queried heldout latest target in training
- both entities queried across every evaluation seed
- duplicate complete execution byte-identical.

MECHANICAL GATE
- exactly two entities;
- exactly two distinct structural addresses per entity before overwrite;
- exactly one overwritten address per entity;
- six writes total;
- sequence length=27;
- projection overwrite formula exact;
- value dimension=3;
- state=32;
- parameters=120.

INTERPRETATION
Positive:
Multi-entity structural binding and temporal overwrite compose under the first regime where both are individually proven.

Negative:
Temporal replacement does not survive entity multiplicity despite value3D static competence; the interaction becomes the next sequence-intelligence boundary.

FAILURE
Do not add state, parameters, gates, timestamps, change thresholds, corpus, seeds, optimizer, or training schedule after results.

BOUNDARY
No language task yet.
No online adaptation.
No recursive self-modification.
