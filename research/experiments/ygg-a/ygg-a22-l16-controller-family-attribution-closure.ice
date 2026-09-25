TITLE: YGG-A22 L16 Controller-Family Stream Attribution Closure
DATE: 2026-09-25
STATUS: CLOSED / VALID ATTRIBUTION
LANE: YGG-A
PREREGISTRATION: 4682ff0798c64a27609ecc30b054909a77299c32
PARENT_CLOSURE: cb882666823b2384c7a83e032f74b4b4c9b31b21
EXECUTION_HEAD: b4c6266f771b8183c44ee6f59c4819cc44c8f5c3
WORKFLOW_RUN_ID: 36198945146
DUPLICATE_SHA256: d976ac4937af8184593810d79c1f254fcbb28feb2533cf7fdee51f7ca00f4da4

RESULT
YGG_A22_L16_CONTROLLER_FAMILY_ATTRIBUTION=true
attribution_classification=BOTH_FAIL

U_A0:
L8 correct_done=1438
L16 correct_done=1440
ratio=1.0013908205841446
stream_noncollapse=false
failure replicate=6 phase=4 stream=S L8=5 L16=2 ratio=.4

U_A25:
L8 correct_done=1443
L16 correct_done=1445
ratio=1.0013860013860014
stream_noncollapse=false
failure replicate=6 phase=4 stream=S L8=5 L16=2 ratio=.4

INTERPRETATION
The hidden L16 service-quality failure is not specific to learned control. It is present identically under fixed and learned controller families in the A-task execution context, while aggregate completion remains intact.

NEXT QUESTION
Map exact nested L8-L16 stream retention under both U_A0 and U_A25 at alpha=.25, repair OFF, to locate the A-context transition and compare its shape with the C5/C16 pressure pattern.

BOUNDARY
Diagnostic only.
No baseline mutation, online adaptation, weight update, or recursive self-modification.
