TITLE: YGG-B21 Temporal Overwrite Sequence Intelligence Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-B
PREREGISTRATION: e05a915f6eec160c1a6bfc671b4349a4240afe13
PARENT_CLOSURE: 80c1bcfff5da9092d0442ebb437bb7b8bbf9dd53
EXECUTION_HEAD: f96f3e5295e07c4f3ecba8ad4380f6d1ece59eb3
WORKFLOW_RUN_ID: 36183500726
DUPLICATE_SHA256: 76aa90cd868b8e653ad33cc65a28ea9ec4e9f01c1464551f6045982aa06484e4

RESULT
YGG_B21_TEMPORAL_OVERWRITE_SEQUENCE_INTELLIGENCE=false
mechanical gate=true
all 64 heldout quadruples scored=true
no heldout latest target leakage=true
state=24
parameters=104

Persistent latest-value accuracy:
111=0.340576171875
222=0.349853515625
333=0.396728515625
444=0.34375
555=0.412841796875

ORDER_SWAP accuracy is exactly equal to persistent accuracy for every seed.
ORDER_SWAP degradation=0.0 for every seed.

INTERPRETATION
The additive superposition memory is effectively order-insensitive for repeated writes to the same address. Static binding competence through seven bindings does not provide latest-write semantics. A recency/overwrite mechanism is required before stronger sequence or language tasks.

NEXT QUESTION
Keep the entire B21 task, state size, parameters, masks, corpus, and controls fixed, but replace additive writes with a parameter-free address-local projection overwrite:
M <- M - (M q) q^T + v q^T
for unit address q.
This is the smallest architectural change that enforces replacement along the written address without adding gates, timestamps, learned state, or parameters.

BOUNDARY
No threshold tuning.
No language task yet.
No online adaptation.
No recursive self-modification.
