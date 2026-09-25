TITLE: YGG-A2 Terminal Integrity Service Priority Primary Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-A
PREREGISTRATION: fe98512607bbd5a267a2735ae5fd881e47b5d86e
EXECUTION_HEAD: ac4f53c9811cb34699be96c0fa25d7afa995ba41
WORKFLOW_RUN_ID: 36118134802
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: 0656859682fcfd6bd7d438fddcdada9cc78bdd5ebd8e85dba5e1f59b2d0890c1

QUALIFICATION
YGG_A2_TERMINAL_INTEGRITY_PRIORITY=false
baseline_feasible_count=9
evidence_coverage_pass=true
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
verify_priority_changed_winner=41
repair_priority_changed_winner=2

FAILING WORLD
replicate=10
correct_done=141
incorrect_done=0
backlog=19
maturity_pass=false
repair_integrity=false
verify_priority_changed_winner=4
repair_priority_changed_winner=1
failing_corrupt_request=141
terminal_state=AT_EGRESS
detection_epoch=null
repair_epoch=null
verified_epoch=null

INTERPRETATION
The terminal-integrity priority treatment was materially exercised across the frozen primary sweep but was insufficient to close the remaining replicate-10 integrity failure.
This falsifies the narrow A2 hypothesis that ordinary competition with already-eligible nonterminal work was the full cause of the A1 single-world failure.
The fork/join dependency mechanism remained exact, duplicate execution remained deterministic, matching integrity remained intact, and no incorrect DONE occurred.

NEXT QUESTION
Before selecting an A3 intervention, diagnose whether request 141 lacked a locally eligible VERIFY opportunity near the frozen horizon, rather than merely losing such an opportunity to inherited scheduling.

BOUNDARY
Do not retune A2.
Do not extend the horizon, weaken maturity, remove corruption, change frozen manifests, or add service capacity under A2.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
