TITLE: YGG-A24 L12 Marginal-Cell Attribution Closure
DATE: 2026-09-25
STATUS: CLOSED / VALID ATTRIBUTION
LANE: YGG-A
PREREGISTRATION: 8b712901de835b21e9fa4e549d9eb2ed12654122
PARENT_CLOSURE: bdd206305eeacd120e8d151184a9a1ad7c371859
EXECUTION_HEAD: e57ca03011ad06e086562e83a1af67ebe8ac73e1
WORKFLOW_RUN_ID: 36202937163
DUPLICATE_SHA256: 4d10faa50a252516a51af817c1e1130b4e3ec27588ef0648322adef28b6d9f88

RESULT
YGG_A24_L12_MARGINAL_CELL_ATTRIBUTION=true
classification=SINGLE_CELL_SPECIFIC

Both U_A0 and U_A25:
rank12=false
rank13=true
rank14=true
rank15=true
rank16=true

Observed collapse:
replicate=6
phase=4
stream=S
anchor count=5
candidate count=2
ratio=.4

Replicate-6 marginal cells:
rank12=59
rank13=63
rank14=60
rank15=12
rank16=22

INTERPRETATION
The L12 boundary is not lesion-cardinality driven. At constant cardinality 12, only the natural rank-12 marginal arm collapses, identically under fixed and learned controllers. In replicate 6 the distinguishing marginal cell is cell 59.

NEXT QUESTION
Test cell 59 as the twelfth lesion across every other seed context where cell 59 is not already present in the frozen L11 anchor. Determine whether cell 59 is globally sensitive or only harmful in the replicate-6 context.

BOUNDARY
Diagnostic only.
No baseline mutation, online adaptation, weight update, or recursive self-modification.
