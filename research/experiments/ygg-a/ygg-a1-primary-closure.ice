TITLE: YGG-A1 Fork Join Exact Parent Primary Closure
DATE: 2026-09-24
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-A
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc
PREREGISTRATION: 44e5db473c0a0aa4c6065b77aa2d83cedecfc1eb

MECHANICAL GATE
RUN: 36073766615
HEAD: e04c9ed77ac50c7df9e0afb8e44b81068abd415f
STATUS: PASS
DUPLICATE_SHA256: 5eef6f51e3ece3b5cb93c335d88751097724b8db11c2034ac6652ca67072cedd
Both B->C and C->B sibling orders were exercised.
D remained blocked until both siblings existed.
Fork dependencies were exact.
Corruption detection, repair, independent reverify, maturity, and zero-incorrect-DONE all passed.

PRIMARY
RUN: 36074076030
HEAD: 5a6f83d4fd84e0496d569634112fecd52efeadd5
ARTIFACT_ID: 10838954665
ARTIFACT_SHA256: e90e6e03408a4c7f6adc46ef627d47e1545c88413ba5c2c5d08477a92be2dcc3
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: 19ac8cbfa0b87c80ea63a167edc6c749798758161a2511944616cfe1a96b9772

QUALIFICATION
YGG_A1_FORK_JOIN_EXACT_PARENT_FEASIBLE=false
baseline_feasible_count=9
evidence_coverage_pass=true
feasible_replicates=1,2,3,4,5,6,7,8,9
all_zero_incorrect_done=true
all_matching_integrity=true
both_sibling_orders_exercised=true
d_never_before_join=true
fork_dependencies_exact=true
duplicate_byte_identical=true
all_maturity_pass=false
all_repair_integrity=false

FAILURE LOCALIZATION
Replicate 10 was the only infeasible primary world.
correct_done=141
incorrect_done=0
expired=0
backlog=19
operations_per_correct_completion=13.27659574468085
demand_recovery=3
lesion_recovery=0
anchor_recovery=0

Replicate 10 scheduled ten corruptions.
Nine corrupted requests reached egress.
Eight of those nine were detected, repaired, and independently reverified.
Request 141 reached egress corrupted but remained AT_EGRESS through the terminal horizon:
detection_epoch=null
repair_epoch=null
done_epoch=null
terminal_state=AT_EGRESS
maturity_pass=false

INTERPRETATION
The fork/join dependency logic itself is mechanically sound and remained output-safe in all ten primary worlds: no incorrect DONE occurred.
The preregistered robustness claim nevertheless fails because one deterministic primary world exhausted terminal service slack before a corrupted egress request received VERIFY.
This exposes a scheduling/service-margin boundary under fork/join load rather than an arithmetic or dependency-correctness failure.

SCIENTIFIC CONSEQUENCE
Do not rescue A1 by extending T, relaxing maturity, changing the replicate set, or weakening the repair requirement.
A follow-up must be a new preregistered experiment testing whether terminal VERIFY/REPAIR service policy can restore robustness under the same fork/join topology.

BOUNDARY
No shared-baseline promotion.
No learned C/S authority.
No online adaptation.
No recursive self-modification.
