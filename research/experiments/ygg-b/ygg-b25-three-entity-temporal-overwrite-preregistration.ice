TITLE: YGG-B25 Three-Entity Temporal Overwrite Integration Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: b3c18c0521e9bb8e57220ed1e2927e72e56c61cc
TEMPORAL_PARENT: YGG-B24
STATIC_CAPACITY_PARENT: YGG-B19

QUESTION
Can projection-overwrite temporal memory scale to three entities at the already-proven six-active-binding value3D capacity?

NORTH-STAR TARGET
Extend multi-entity temporal sequence intelligence to the known static capacity frontier before introducing a qualitatively new language-like task.

FROZEN
- KEYS=8, ROLES=2, SLOTS=2, VALUES=8;
- learned 8x8 key/entity embedding;
- exact ROLE/SLOT masks;
- value dimension=3;
- memory=3x8;
- pending register=8;
- persistent state=32;
- learned parameters=120;
- parameter-free projection-overwrite rule exact;
- exact Cartesian holdout;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=.005;
- seeds=111,222,333,444,555;
- deterministic CPU execution;
- unchanged RESET, QUERY_ORDER_SWAP, VALUE_SHUFFLE, ROLE_FLIP, SLOT_FLIP controls.

STRUCTURAL / TEMPORAL TASK
Nine writes followed by one query:
1. choose three distinct entities deterministically;
2. choose exactly two distinct ROLE×SLOT addresses per entity deterministically;
3. write all six active bindings once;
4. choose exactly one of the two addresses per entity and overwrite it once;
5. choose one of the three overwritten entities as the query target;
6. target is that address's latest value.

Active bindings remain six.
Overwrite events replace rather than add active addresses.
Sequence length=39 tokens.

TRAIN/EVAL
Training queried latest values use only allowed quadruples.
Evaluation queried latest values use only held-out Cartesian quadruples.
Each overwrite value must differ from its original value.

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
- all three entities queried in every evaluation seed
- duplicate execution byte-identical.

MECHANICAL GATE
- exactly three distinct entities;
- exactly two distinct structural addresses per entity;
- exactly one overwrite per entity;
- six active bindings and nine writes;
- sequence length=39;
- projection overwrite formula exact;
- value dimension=3;
- state=32;
- parameters=120.

INTERPRETATION
Positive:
Temporal overwrite scales to three entities at the known six-binding capacity without extra state or parameters.

Negative:
Multi-entity temporal composition fails before the known static capacity frontier; the interaction becomes the next boundary.

FAILURE
Do not add state, parameters, gates, timestamps, or alter thresholds/corpus/seeds/training after results.

BOUNDARY
No language task yet.
No online adaptation.
No recursive self-modification.
