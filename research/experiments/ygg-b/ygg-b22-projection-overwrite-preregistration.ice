TITLE: YGG-B22 Parameter-Free Projection Overwrite Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: e4698d5cee348c4fe4810487f65c96d772f8b5ea
PARENT_EXPERIMENT: YGG-B21

QUESTION
Can a parameter-free address-local replacement rule provide latest-write temporal semantics on the exact B21 overwrite task without adding state, gates, timestamps, or learned parameters?

NORTH-STAR TARGET
Establish the minimum mechanism needed for genuine sequence order sensitivity before stronger sequence or language tasks.

FROZEN FROM YGG-B21
- one entity per sequence;
- four ROLE×SLOT addresses;
- five writes followed by one query;
- the same address is written first and fifth with different values;
- three intervening writes;
- sequence length=23;
- KEYS=8, ROLES=2, SLOTS=2, VALUES=8;
- address dimension=8;
- value dimension=2;
- memory shape=2x8;
- pending address register=8;
- persistent state=24 scalars;
- learned parameters=104;
- exact learned key embedding;
- exact ROLE/SLOT masks;
- exact train/eval corpus and holdout;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=.005;
- seeds=111,222,333,444,555;
- exact RESET, ORDER_SWAP, VALUE_SHUFFLE, ROLE_FLIP, SLOT_FLIP controls;
- exact B21 success thresholds;
- deterministic CPU execution.

SCIENTIFIC CHANGE
Replace only the write update.

B21 additive write:
M <- M + v q^T

B22 projection overwrite for unit address q:
old <- M q
M <- M - old q^T + v q^T

No learned gate.
No timestamp.
No erase token.
No extra state.
No extra parameters.
No optimizer or corpus change.

MECHANISTIC PROPERTY
Immediately after a write to unit address q:
M q = v
up to deterministic floating-point tolerance, before subsequent writes to other non-orthogonal addresses.

SUCCESS
Unchanged B21 thresholds:
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
- all 64 heldout quadruples scored
- no heldout latest target in training
- duplicate complete execution byte-identical.

MECHANICAL GATE
- exact B21 corpus structure and masks;
- exact 24-scalar state and 104 parameters;
- projection overwrite formula exact;
- address q normalized before overwrite;
- direct unit test verifies isolated same-address second write replaces first write exactly within tolerance.

INTERPRETATION
Positive:
Temporal latest-write semantics requires replacement rather than additional learned capacity; the minimal parameter-free overwrite operation is sufficient.

Negative:
Even explicit local replacement is insufficient under structural interference; stronger recency/gating architecture is required.

FAILURE
Do not add state, gates, timestamps, parameters, change thresholds, corpus, seeds, or training schedule after observing results.

BOUNDARY
No language task yet.
No online adaptation.
No recursive self-modification.
