TITLE: YGG-A2 Terminal Integrity Service Priority Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: ygg-a1-primary-closure.ice
PARENT_PREREGISTRATION: 44e5db473c0a0aa4c6065b77aa2d83cedecfc1eb
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Was YGG-A1's single-world failure primarily a terminal integrity service-margin failure rather than a failure of the fork/join dependency mechanism?

A1 OBSERVATION THAT MOTIVATES A2
A1 passed its mechanical fork/join gate and nine of ten frozen primary worlds were baseline-feasible.
Replicate 10 preserved zero incorrect DONE and exact fork/join dependency behavior, but one corrupted request that had reached egress remained undetected in AT_EGRESS at the frozen horizon.
A2 tests one narrow scheduling hypothesis rather than extending the horizon or weakening any integrity gate.

SCIENTIFIC CHANGE
When more than one already-eligible local operation competes for the same service opportunity, rank terminal integrity work before inherited nonterminal work:
1. VERIFY
2. REPAIR
3. all other operation types in the exact inherited order.

This priority may choose among operations that are already locally eligible.
It MUST NOT create eligibility, move a request, add service capacity, add cells, add epochs, add operations, change corruption, change expiry, or expose nonlocal information.

FROZEN FROM A1
- exact ten A1 primary manifests
- exact 160-epoch horizon
- requests_per_epoch=1
- exact fork/join task graph A -> {B,C} -> D
- both sibling orders
- exact programs, seeds, arrivals, lesions, anchor rotations, corruption schedule, expiry, routing, repair semantics, verification semantics, and DONE semantics
- exact local operation capacity
- exact U_A0 arm
- exact maturity rules
- exact baseline-feasibility rule
- exact duplicate/integrity gates
- no model RNG
- no learned authority
- no online adaptation

MECHANICAL GATE
Before primary execution demonstrate:
- VERIFY outranks an otherwise competing inherited nonterminal operation when both are already locally eligible;
- REPAIR outranks an otherwise competing inherited nonterminal operation when both are already locally eligible;
- priority never creates an operation that was not already eligible;
- within equal priority, inherited ordering is unchanged;
- B/C sibling order remains exercised in both directions;
- D remains blocked until both B and C complete;
- fork dependencies remain exact;
- corruption is detected, repaired exactly, and reverified;
- zero incorrect DONE;
- duplicate execution byte-identical.

PRIMARY
Execute all ten frozen A1 primary worlds twice.
The two complete ordered sweeps must be byte-identical.

SUCCESS
Use A1 capability gates unchanged:
- baseline_feasible_count >= 8
- zero incorrect DONE in all ten worlds
- matching duplicate cell/request integrity in all ten worlds
- both sibling orders exercised
- D never executes before B/C join
- fork dependencies exact
- repair integrity true in all ten worlds
- maturity pass true in all ten worlds
- repair/reverify fixture true
- duplicate complete execution byte-identical

Additionally report:
- number of service decisions where VERIFY priority changed the inherited winner;
- number of service decisions where REPAIR priority changed the inherited winner;
- per-world terminal integrity priority interventions.

FALSIFICATION
A2 is a scientific negative if any frozen capability gate fails after the priority treatment.
Do not extend T, weaken maturity, remove corruption, alter manifests, add capacity, or retune priority after observing results.

INTERPRETATION
Positive: A1's remaining failure is consistent with terminal integrity service margin under the inherited scheduler; fork/join remains feasible when already-eligible integrity work is locally prioritized.
Negative: terminal priority alone is insufficient; advance to a new preregistered hypothesis rather than tuning A2.

BOUNDARY
No LU-2V mutation.
No shared-baseline promotion from this lane alone.
No learned developmental C/S authority.
No online adaptation.
No recursive self-modification.
