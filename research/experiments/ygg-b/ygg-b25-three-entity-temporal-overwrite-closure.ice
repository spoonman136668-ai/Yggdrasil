TITLE: YGG-B25 Three-Entity Temporal Overwrite Integration Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC POSITIVE
LANE: YGG-B
PREREGISTRATION: 073f03e27e3ef7fc3f4ab218efc4e25236efa875
PARENT_CLOSURE: b3c18c0521e9bb8e57220ed1e2927e72e56c61cc
EXECUTION_HEAD: d9cdf3ad375a907c31bf8ebe7b27432103ce4394
WORKFLOW_RUN_ID: 36198879019
DUPLICATE_SHA256: 0d18e4e961e0656551dd3c92e438728d89de2374ff0334da68e1ee758481087e

RESULT
YGG_B25_THREE_ENTITY_TEMPORAL_OVERWRITE=true
mechanical gate=true
three entities exact
six active bindings exact
one overwrite per entity exact
state=32
parameters=120
all five seeds persistent OOD latest-value accuracy=1.0
all five query-order-swap accuracy=0.0
all causal/reset/value/role/slot/holdout gates=true

INTERPRETATION
Projection overwrite scales cleanly to three entities at the proven six-active-binding capacity with no extra learned state or parameters.

NEXT QUESTION
Raise active structural load only from six to seven while keeping three entities, value3D, one overwrite per entity, projection overwrite, state, parameters, optimizer, controls, and thresholds frozen.

BOUNDARY
No language task yet.
No online adaptation.
No recursive self-modification.
