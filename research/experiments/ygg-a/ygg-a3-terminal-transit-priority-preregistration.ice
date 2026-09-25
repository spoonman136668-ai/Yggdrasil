TITLE: YGG-A3 Terminal Transit Service Priority Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: be9b002391a1addaa192b64b120d1ef54ee63825
PARENT_EXPERIMENT: YGG-A2
DIAGNOSTIC_RUN: 36119055521
DIAGNOSTIC_ARTIFACT: 10855957294

QUESTION
Was the remaining replicate-10 integrity failure caused by terminal transit arriving at egress too late to create any VERIFY opportunity, and can prioritizing an already-eligible final ROUTE into egress restore the frozen capability envelope without extra time or service capacity?

DIAGNOSTIC BASIS
For frozen primary replicate 10, corrupt request 141:
- first_egress_epoch=159
- frozen horizon ends after epoch 159
- ticks already at AT_EGRESS before matching=0
- eligible VERIFY ticks=0
- selected VERIFY ticks=0
- terminal state=AT_EGRESS
- detected=false

A2 materially exercised VERIFY and REPAIR priority elsewhere but could not affect a request that had no post-arrival verification tick.

SCIENTIFIC CHANGE
When multiple already-eligible local operations compete for the same service opportunity, use:
1. VERIFY
2. REPAIR
3. TERMINAL_ROUTE: a ROUTE whose single inherited next hop lands at that request's current egress
4. all other operation types in exact inherited order

The terminal-route classification may use only the request's current local position, stream direction, and current request anchors needed by the inherited routing rule.
It MUST NOT inspect expected output, corruption correctness, future state, or evaluator information.

FROZEN FROM A2
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
- A2 VERIFY > REPAIR priority
- no model RNG
- no learned authority
- no online adaptation

MECHANICAL GATE
Demonstrate before primary execution:
- VERIFY still outranks competing lower-priority work;
- REPAIR still outranks competing lower-priority work;
- a final already-eligible ROUTE to egress outranks an otherwise competing inherited nonterminal operation;
- an ordinary nonterminal ROUTE does not receive terminal priority;
- no priority class creates eligibility;
- within equal priority, inherited ordering is unchanged;
- B/C sibling order remains exercised in both directions;
- D remains blocked until both B and C complete;
- repair/reverify fixture remains exact;
- zero incorrect DONE;
- duplicate execution byte-identical.

PRIMARY
Execute all ten frozen A1 primary worlds twice.
The two complete ordered sweeps must be byte-identical.

SUCCESS
Use A1/A2 capability gates unchanged:
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

REPORT
- VERIFY priority changed winners
- REPAIR priority changed winners
- TERMINAL_ROUTE priority changed winners
- per-world priority interventions
- replicate-10 first egress and terminal integrity outcome

FALSIFICATION
A3 is a scientific negative if any frozen capability gate fails.
Do not extend T, weaken maturity, alter manifests, add service capacity, fuse ROUTE with VERIFY, or tune priority after observing results.

INTERPRETATION
Positive: the A1/A2 residual failure was a terminal-transit liveness margin problem; earlier service of already-eligible final egress routes is sufficient.
Negative: terminal-transit priority alone is insufficient; advance to a new preregistered mechanism.

BOUNDARY
No LU-2V mutation.
No shared-baseline promotion from this lane alone.
No online adaptation.
No recursive self-modification.
