TITLE: YGG-A21 L16 Alpha-by-Repair Stream Attribution Closure
DATE: 2026-09-25
STATUS: CLOSED / VALID ATTRIBUTION
LANE: YGG-A
PREREGISTRATION: f64a3cfc1fe24c930113a6a1fa96a8e643e71573
PARENT_CLOSURE: 8856415561fcae6bf43db7bc58152021fe5ff872
EXECUTION_HEAD: 101d58915feb060e2b2913fa9cb4e4cdc36708f7
WORKFLOW_RUN_ID: 36196106056
DUPLICATE_SHA256: eb44d50ca69accbf8fb563eeeb8be9900795d9311158f3b9d3691cb30c7395e4

RESULT
YGG_A21_L16_ALPHA_BY_REPAIR_ATTRIBUTION=true
attribution_classification=PERSISTENT_STREAM_FAILURE

STREAM-NONCOLLAPSE MATRIX
alpha=.25 repair OFF=false repair ON=false
alpha=.50 repair OFF=false repair ON=false
alpha=1.00 repair OFF=false repair ON=false

FAILURE DETAILS
alpha=.25:
replicate 6 phase 4 stream S: L8=5 L16=2 ratio=.4
same with repair OFF and ON.

alpha=.50 and 1.00:
replicate 6 phase 4 stream S: 5->3 ratio=.6
replicate 10 phase 4 stream S: 7->5 ratio=.7142857143
same with repair OFF and ON.

INTERPRETATION
The hidden L16 service collapse is not explained by learned-control blend magnitude in .25..1.0 and is not caused by the 58-event branch-repair mechanism. The highest-value remaining distinction is controller family / execution context: fixed U_A0 versus learned U_A25 under the same A task and exact L16 lesion.

NEXT QUESTION
Compare U_A0 and U_A25 at alpha=.25, repair OFF, each against its own same-mode L8 anchor.

BOUNDARY
No baseline mutation, weight update, online adaptation, or recursive self-modification.
