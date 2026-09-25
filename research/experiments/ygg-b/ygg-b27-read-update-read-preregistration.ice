TITLE: YGG-B27 Read-Update-Read Sequence Episode Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: f1b9726614af1c57841310c25f5d1daa57c5e2fa
PARENT_EXPERIMENT: YGG-B26

QUESTION
Can the same compact three-entity substrate emit a correct read, accept a later overwrite, and emit a second correct read in one uninterrupted sequence episode?

NORTH-STAR TARGET
Cross from terminal associative retrieval into ordered multi-output sequence intelligence without adding persistent state or learned parameters.

FROZEN FROM B26
- three distinct entities;
- learned 8x8 key embedding;
- exact ROLE/SLOT masks;
- value dimension=3;
- memory=3x8 plus pending register=8;
- persistent state=32;
- learned parameters=120;
- seven active structural bindings;
- exact Cartesian held-out rule for the post-update target;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=.005;
- seeds=111,222,333,444,555;
- deterministic CPU execution;
- no online adaptation.

SCIENTIFIC CHANGE
Replace a single terminal query with an ordered episode:
1. write seven active bindings;
2. READ-1 queries one active address and emits target-1;
3. UPDATE overwrites a different active address with a distinct value;
4. READ-2 queries that overwritten address and emits its latest value.

READ-1 and READ-2 addresses must be distinct.
Training READ-2 targets use allowed quadruples only.
Evaluation READ-2 targets use held-out Cartesian quadruples only.

ARCHITECTURE
The memory, pending register, embeddings, role/slot transforms, projection-overwrite rule, and readout are unchanged.
The same model parameters are used for both outputs.
No extra recurrent state, timestamp, gate, or learned parameter is allowed.

CONTROLS
- tokenwise RESET control;
- swap READ-1 and READ-2 query identities while leaving targets fixed;
- shuffle write values;
- flip query roles;
- flip query slots.

SUCCESS
- min persistent joint two-read accuracy >=.90;
- median persistent joint accuracy >=.95;
- max reset joint accuracy <=.20;
- min persistent-reset gap >=.60;
- min query-identity-swap degradation >=.40;
- min write-value-shuffle degradation >=.40;
- min query-role-flip degradation >=.40;
- min query-slot-flip degradation >=.40;
- all five seeds causal direction true;
- persistent state exactly 32;
- parameters exactly 120;
- all 64 held-out READ-2 quadruples scored per seed;
- no held-out READ-2 target in training;
- duplicate execution byte-identical.

INTERPRETATION
Positive:
The compact substrate supports an ordered read-update-read episode rather than only terminal lookup.

Negative:
The current substrate can store and overwrite bindings but does not yet support reliable multi-output sequence episodes under the frozen architecture.

FAILURE
Do not add state, parameters, gates, timestamps, alter thresholds, corpus construction, seeds, or training after results.

BOUNDARY
Synthetic sequence task only.
No language corpus yet.
No online adaptation.
No recursive self-modification.
