TITLE: YGG-B20 Seven-Binding Value3D Boundary Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: b08a0189a04e5391161d8296373e28205fb8ea45
POSITIVE_PARENT: YGG-B19
NEGATIVE_PARENT: YGG-B18

QUESTION
At value dimension 3, does the two-entity structural-binding system remain above the frozen capability threshold at seven concurrent bindings?

NORTH-STAR TARGET
Resolve the final one-binding uncertainty between the six-binding PASS and eight-binding negative before moving toward higher sequence intelligence.

FROZEN
- KEYS=8, ROLES=2, SLOTS=2, VALUES=8;
- address dimension=8;
- value dimension=3;
- memory shape=3x8;
- persistent state=32;
- learned parameters=120;
- exact learned key embeddings and fixed ROLE/SLOT masks;
- exact Cartesian holdout;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=.005;
- seeds=111,222,333,444,555;
- exact reset/value-shuffle/role-flip/slot-flip controls;
- exact capability thresholds;
- deterministic CPU execution.

SCIENTIFIC CHANGE
Binding load only:
B19=6
B20=7
B18=8

Per sequence:
- choose two distinct entity keys using the inherited deterministic ranking;
- choose one entity deterministically to carry all four ROLE×SLOT addresses;
- the other entity carries exactly three distinct ROLE×SLOT addresses;
- choose the omitted address deterministically from the same seeded generator;
- total seven bindings;
- sequence length=31;
- across the mechanical corpus both choices of full entity and all four omission types must occur.

SUCCESS
Unchanged:
- minimum OOD persistent >=.90
- median OOD persistent >=.95
- max reset <=.35
- min persistent-reset gap >=.50
- min value-shuffle degradation >=.40
- min role-flip degradation >=.40
- min slot-flip degradation >=.40
- all five seeds causal direction true
- state exactly 32
- parameters exactly 120
- no holdout leakage
- all 64 held-out quadruples scored per seed
- duplicate complete execution byte-identical.

INTERPRETATION
Positive: seven bindings are supported and the observed threshold lies between seven and eight.
Negative: the observed threshold lies between six and seven.

FAILURE
Do not change load, value width, thresholds, seeds, masks, holdout, optimizer, or training schedule after results.

BOUNDARY
No language task yet.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
