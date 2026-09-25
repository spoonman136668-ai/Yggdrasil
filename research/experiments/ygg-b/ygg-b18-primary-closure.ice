TITLE: YGG-B18 Full-Load Three-Dimensional Value Binding Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-B
PREREGISTRATION: 28dc1862e5347e661cf435d6482e122bb731adbc
PARENT_CLOSURE: eb2d0192d36d22e423f8c5552e69e52d5363e079
EXECUTION_HEAD: 77e78fe1b01cf683a388112e7a9ae0f2e67200c1
WORKFLOW_RUN_ID: 36148610055
DUPLICATE_SHA256: 735a25f914a9a69ef1bd9e916d8a98a209892a8d9c46f5206dc2f186ebcbbb07

RESULT
YGG_B18_FULL_LOAD_VALUE3D_BINDING=false
median_persistent_ge_095=true
min_persistent_ge_090=false
all causal/control gates=true
OOD:
111=0.99560546875
222=0.98828125
333=0.852294921875
444=0.997802734375
555=0.989013671875

INTERPRETATION
Value3D nearly solves the full eight-binding task, but one frozen seed remains below threshold. The remaining boundary is therefore narrower than B13: between the successful four-binding B17 condition and the eight-binding condition.

NEXT QUESTION
Test six bindings at value3D, preserving two entities and three distinct ROLE×SLOT addresses per entity, to localize the load boundary.

BOUNDARY
Scientific negative sealed unchanged. No threshold tuning, no online adaptation, no recursive self-modification.
