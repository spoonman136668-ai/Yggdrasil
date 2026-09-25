TITLE: YGG-A3 Terminal Transit Service Priority Primary Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-A
PREREGISTRATION: dcdbbc6fb65e78a7c0299a8d84d57ae3168380fe
PARENT_CLOSURE: be9b002391a1addaa192b64b120d1ef54ee63825
EXECUTION_HEAD: 0122c8719dd85054461a2f060e36674a70469f3f
WORKFLOW_RUN_ID: 36120401312
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: a2eb5b9b6a6be16fe5a940bbe3511fe30ff6ebd870cbd90e2c2109f41a927a63

QUALIFICATION
YGG_A3_TERMINAL_TRANSIT_PRIORITY=false
baseline_feasible_count=9
all_zero_incorrect_done=true
all_matching_integrity=true
both_sibling_orders_exercised=true
d_never_before_join=true
fork_dependencies_exact=true
repair_reverify_fixture=true
duplicate_byte_identical=true
all_maturity_pass=false
all_repair_integrity=false

CAUSAL EXERCISE
verify_priority_changed_winner=42
repair_priority_changed_winner=2
terminal_route_priority_changed_winner=62

FAILING WORLD
replicate=10
correct_done=141
incorrect_done=0
backlog=19
maturity_pass=false
repair_integrity=false
terminal_route_priority_changed_winner=4
verify_priority_changed_winner=3
repair_priority_changed_winner=1
failing_corrupt_request=141
terminal_state=AT_EGRESS
detection_epoch=null

INTERPRETATION
Terminal-route priority was materially exercised but did not create enough temporal margin for request 141 to obtain a post-arrival VERIFY opportunity.
This falsifies the A3 hypothesis that prioritizing already-eligible final transit alone is sufficient.
The result is consistent with the A3 observability diagnostic: the residual gap is at the egress handoff/terminal observation boundary, not ordinary local competition.

BOUNDARY
Do not retune A3.
No horizon extension.
No added service capacity.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
