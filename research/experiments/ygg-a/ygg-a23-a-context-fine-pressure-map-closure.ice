TITLE: YGG-A23 A-Context Fine Pressure Map Closure
DATE: 2026-09-25
STATUS: CLOSED / VALID DIAGNOSTIC
LANE: YGG-A
PREREGISTRATION: 46e278339e4d201bc35c8ffca22d8f836eb3c9b1
PARENT_CLOSURE: 3613dd94d6e9242245d63374d5d0be6ed4340180
EXECUTION_HEAD: 44f2ddf19b69b332fb1cd25914005f95e10768d5
WORKFLOW_RUN_ID: 36200102579
DUPLICATE_SHA256: 11a3a7f07d3acf9088797b6e09ae0b4829644a4d1608801337bcf7bc43e6ba8f

RESULT
YGG_A23_A_CONTEXT_FINE_PRESSURE_MAP=true
cross_mode_classification=IDENTICAL_MAPS

U_A0 stream map:
L8=true L9=true L10=true L11=true L12=false L13=false L14=false L15=false L16=false
first_failure=L12
first_recovery=none
failure cell: replicate=6 phase=4 stream=S L8=5 current=2 ratio=.4

U_A25 stream map:
L8=true L9=true L10=true L11=true L12=false L13=false L14=false L15=false L16=false
first_failure=L12
first_recovery=none
failure cell: replicate=6 phase=4 stream=S L8=5 current=2 ratio=.4

C-reference map:
L8=true L9=true L10=true L11=false L12=false L13=true L14=true L15=true L16=true

INTERPRETATION
Fixed and learned controller families have the same A-context boundary. The controller family is therefore not the source of the hidden service-quality transition. Because the lesion sets are strictly nested and every level from L12 upward contains the L12-added cell, the persistent L12-L16 failure may be a single-cell bottleneck rather than a monotonic cardinality effect.

NEXT QUESTION
Hold the passing L11 lesion fixed and add each rank-12 through rank-16 marginal cell one at a time at constant lesion cardinality 12. Determine whether failure follows one specific marginal cell, several cells, or only cumulative interaction.

BOUNDARY
Diagnostic only.
No baseline mutation, online adaptation, weight update, or recursive self-modification.
