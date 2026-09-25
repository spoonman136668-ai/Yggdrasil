TITLE: YGG-B21 Temporal Overwrite Sequence Intelligence Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 80c1bcfff5da9092d0442ebb437bb7b8bbf9dd53
STATIC_CAPACITY_PARENT: YGG-B20
LOW_LOAD_PARENT: YGG-B14

QUESTION
Can the current compact persistent binding mechanism represent temporal update semantics: an address is written, other bindings intervene, that same address is overwritten with a different value, and a later query retrieves the most recent value rather than an order-insensitive mixture?

NORTH-STAR TARGET
Begin genuine sequence-intelligence testing after the static binding-load boundary is resolved.

FROZEN SUBSTRATE
- one entity per sequence;
- four ROLE×SLOT addresses;
- address dimension=8;
- exact learned key embedding path;
- exact fixed ROLE/SLOT masks;
- VALUES=8;
- value dimension=2;
- memory=2x8 plus 8-scalar pending address;
- persistent state=24 scalars;
- learned parameters=104;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=.005;
- seeds=111,222,333,444,555;
- deterministic CPU execution.

TEMPORAL TASK
Five write events followed by one query:
1. write each of the four structural addresses once;
2. choose one update address deterministically;
3. after at least two intervening writes relative to its initial write, write that same address again with a new value different from the original;
4. query the updated address;
5. target is the second/latest value.

Sequence length=23 tokens (5 * 4 write tokens + 3 query tokens).

CORPUS
Training latest values use the established non-heldout quadruple rule.
Evaluation latest queried value is from the established heldout set.
The original value at the updated address must differ from the latest value.
No heldout queried quadruple may appear as the latest training target.

CAUSAL CONTROLS
RESET: reset persistent state every token.
ORDER_SWAP: swap the first and second writes to the updated address while holding all address/value identities fixed; target remains the originally latest value, so a truly recency-sensitive representation should degrade.
VALUE_SHUFFLE: shuffle write values across write events.
ROLE_FLIP and SLOT_FLIP remain exact.

SUCCESS
- min persistent OOD latest-value accuracy >=.90
- median persistent >=.95
- max reset <=.35
- min persistent-reset gap >=.50
- min ORDER_SWAP degradation >=.40
- min value-shuffle degradation >=.40
- min role-flip degradation >=.40
- min slot-flip degradation >=.40
- all five seeds causal direction true
- state exactly 24
- parameters exactly 104
- all 64 queried heldout quadruples scored
- no queried heldout latest-value quadruple in training
- duplicate complete execution byte-identical.

INTERPRETATION
Positive:
The compact memory supports explicit latest-write temporal semantics without new state or gates.

Negative:
Static binding competence does not imply temporal update competence. The architecture requires a recency/gating/erasure mechanism before stronger sequence or language tasks.

FAILURE
Do not add gates, timestamps, erase operations, state, parameters, or threshold changes after seeing results.

BOUNDARY
No language task yet.
No online adaptation.
No recursive self-modification.
