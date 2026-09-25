TITLE: YGG-B23 Dual Temporal Overwrite Composition Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 0252d436ed7ad07b0d69433c729fa7192f96dd95
PARENT_EXPERIMENT: YGG-B22

QUESTION
Can the parameter-free projection-overwrite memory preserve the latest values of two independently updated structural addresses in the same sequence and retrieve either one compositionally?

NORTH-STAR TARGET
Advance sequence intelligence from one latest-write dependency to multiple concurrent temporal updates before language tasks.

FROZEN FROM B22
- one entity per sequence;
- four ROLE×SLOT addresses;
- KEYS=8, ROLES=2, SLOTS=2, VALUES=8;
- address dimension=8;
- value dimension=2;
- projection-overwrite update rule exact;
- memory=2x8 plus 8-scalar pending address;
- persistent state=24;
- learned parameters=104;
- exact learned key embedding and ROLE/SLOT masks;
- exact Cartesian holdout logic;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=.005;
- seeds=111,222,333,444,555;
- deterministic CPU execution.

TEMPORAL TASK
Six writes followed by one query:
1. write all four structural addresses once;
2. choose two distinct update addresses deterministically;
3. overwrite each selected address once with a new value different from its original;
4. query one of the two updated addresses, chosen deterministically;
5. target is that address's latest value.

Sequence length=27 tokens.

The two overwrite events occur after all four initial writes, so each updated address has intervening structural activity.

CONTROLS
RESET: unchanged.
QUERY_ORDER_SWAP: swap the original and overwrite events for the queried address only; target remains the originally latest value.
VALUE_SHUFFLE: shuffle values across all six writes.
ROLE_FLIP and SLOT_FLIP: unchanged structural controls.

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
- state exactly 24
- parameters exactly 104
- all 64 queried heldout quadruples scored
- no queried heldout latest target in training
- both updated addresses are queried across the mechanical/evaluation corpus
- duplicate execution byte-identical.

INTERPRETATION
Positive:
Projection overwrite supports multiple concurrent temporal updates without new state or parameters.
Negative:
Single-overwrite competence does not compose; structural interference between overwritten addresses remains a sequence-intelligence boundary.

FAILURE
Do not add state, gates, timestamps, parameters, or alter thresholds/corpus after results.

BOUNDARY
No language task yet.
No online adaptation.
No recursive self-modification.
