TITLE: YGG-B26 Three-Entity Seven-Binding Temporal Capacity Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 622fbba0a936bfc73bf238cc2d4a6bc6b6b89153
PARENT_EXPERIMENT: YGG-B25
STATIC_CAPACITY_REFERENCE: YGG-B20

QUESTION
Can the three-entity projection-overwrite system preserve temporal latest-write semantics when active structural load rises from six to seven bindings?

NORTH-STAR TARGET
Push the integrated multi-entity temporal substrate to the known seven-binding static frontier before introducing a qualitatively new sequence task.

FROZEN FROM B25
- three distinct entities;
- learned 8x8 key/entity embedding;
- exact ROLE/SLOT masks;
- value dimension=3;
- memory=3x8;
- pending register=8;
- persistent state=32;
- learned parameters=120;
- parameter-free projection overwrite;
- exact Cartesian holdout;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=.005;
- seeds=111,222,333,444,555;
- deterministic CPU execution;
- unchanged RESET, QUERY_ORDER_SWAP, VALUE_SHUFFLE, ROLE_FLIP, SLOT_FLIP controls;
- unchanged success thresholds.

SCIENTIFIC CHANGE
Active bindings only:
B25=6
B26=7

STRUCTURAL TASK
- choose three distinct entities deterministically;
- choose one entity deterministically as the heavy entity;
- heavy entity receives exactly three distinct ROLE×SLOT addresses;
- the other two entities receive exactly two distinct ROLE×SLOT addresses each;
- total active bindings=7;
- across the mechanical corpus all three heavy-entity choices and all structural address types are exercised.

TEMPORAL TASK
After the seven initial writes:
- choose one active address per entity deterministically;
- overwrite exactly one address per entity;
- query one of the three overwritten entities;
- target is its latest overwrite value.

Total writes=10.
Sequence length=43 tokens.
Overwrite values differ from originals.

TRAIN/EVAL
Training queried latest values use allowed quadruples only.
Evaluation queried latest values use held-out Cartesian quadruples only.

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

INTERPRETATION
Positive:
Temporal overwrite reaches the known seven-binding static frontier across three entities without added state or parameters.

Negative:
Temporal composition lowers the usable structural-load frontier below the static seven-binding result.

FAILURE
Do not add state, parameters, gates, timestamps, or alter thresholds/corpus/seeds/training after results.

BOUNDARY
No language task yet.
No online adaptation.
No recursive self-modification.
