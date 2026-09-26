TITLE: YGG-B30 READ-1 Write-Position Attribution Preregistration
DATE: 2026-09-26
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_RESULT: YGG-B29 INTRINSIC_READ1_LIMIT
PARENT_CLOSURE: 3d15770c538b9009131f12de0d21b7e637f15294

QUESTION
Is B29's intrinsic READ-1 deficit explained by the original write-event position, and therefore binding age/interference within the seven-write prefix, or is the limit distributed across all seven prefix bindings?

NORTH-STAR TARGET
Localize the compact distributed-memory failure mechanism before changing state size, parameter count, write rule, or readout.

FROZEN
- exact B27/B28/B29 sequence data family;
- exact seven active prefix bindings;
- exact B29 READ-1-only training arm;
- exact three-entity construction and evaluation split;
- exact 32 persistent-state scalars;
- exact 120 learned parameters;
- exact embeddings, ROLE/SLOT masks, projection write, and readout;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=.005;
- seeds=111,222,333,444,555;
- deterministic CPU execution;
- inherited capability threshold=.90;
- no architecture expansion or online adaptation.

METHOD
For each frozen seed, train the exact B29 READ-1-only arm and evaluate the exact B29 evaluation set at the original READ-1 point.
Partition predictions by q1_event, the original write-event position 0..6.
For every position report sample count and READ-1 accuracy.
For attribution, a position is capable only if its minimum accuracy across all five seeds is >=.90.

CLASSIFICATION
AGE_THRESHOLD_PATTERN:
there is exactly one k in 1..6 such that every position below k is limited and every position k..6 is capable.

POSITION_SPECIFIC_NONMONOTONIC:
at least one position is capable and at least one is limited, but no single ordered threshold k explains the map.

BROAD_PREFIX_LIMIT:
all seven positions are limited.

NO_REPRODUCED_POSITION_LIMIT:
all seven positions are capable.

SUCCESS
YGG_B30_READ1_WRITE_POSITION_ATTRIBUTION=true iff mechanical/integrity gates pass, duplicate execution is byte-identical, every position 0..6 is populated for every seed, and exactly one classification is produced.

FAILURE
Do not change threshold, task, seeds, optimizer, epochs, state, parameters, or write/read mechanics after observing results.

BOUNDARY
Diagnostic only.
Synthetic sequence task only.
No language corpus yet.
No online adaptation.
No recursive self-modification.
