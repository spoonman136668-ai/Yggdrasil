TITLE: YGG-B19 Six-Binding Value3D Load Boundary Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: f7238e3f9adfbb067c2a371fea9fb57161a17ea8
POSITIVE_PARENT: YGG-B17
NEGATIVE_PARENT: YGG-B18

QUESTION
At value dimension 3, does the two-entity structural-binding system remain above the frozen capability threshold at six concurrent bindings?

NORTH-STAR TARGET
Localize the structural sequence-load boundary before language experiments.

FROZEN
- KEYS=8, ROLES=2, SLOTS=2, VALUES=8;
- address dimension=8;
- value dimension=3;
- memory shape=3x8;
- pending address register=8;
- persistent state=32 scalars;
- learned parameters=120;
- exact learned key embedding;
- exact fixed ROLE/SLOT masks;
- exact Cartesian holdout;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=.005;
- seeds=111,222,333,444,555;
- exact RESET, VALUE_SHUFFLE, ROLE_FLIP, SLOT_FLIP controls;
- exact capability thresholds;
- deterministic CPU execution.

SCIENTIFIC CHANGE
Binding load only:
B17=4 bindings total, two per entity.
B19=6 bindings total, three per entity.
B18=8 bindings total, four per entity.

For each sequence:
- choose two distinct entity keys using the B13/B18 deterministic ranking;
- independently for each entity choose exactly one of the four ROLE×SLOT addresses to omit using deterministic seeded random ranking;
- include the other three addresses for that entity;
- total six bindings;
- across the mechanical corpus all four structural address types must be represented;
- sequence length=27.

SUCCESS
Unchanged:
- min OOD persistent >=.90
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
Positive: the value3D load boundary lies above six and below/equal eight under current evidence.
Negative: the boundary lies between four and six.

FAILURE
Do not change load, value width, thresholds, seeds, masks, holdout, optimizer, or training schedule after results.

BOUNDARY
No language task yet.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
