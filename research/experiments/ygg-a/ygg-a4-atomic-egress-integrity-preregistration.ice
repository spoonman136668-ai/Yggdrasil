TITLE: YGG-A4 Atomic Egress Integrity Handoff Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_DIAGNOSTIC_CLOSURE: f0fdda0e9997e1aed9d467fd875f4e826900b79e
SOURCE_NEGATIVE: YGG-A2
FROZEN_PARENT: YGG-A1
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Is the remaining fork/join integrity failure caused by asynchronous terminal verification semantics, such that locally verifying a request atomically when ROUTE first reaches its egress is sufficient to preserve terminal integrity under the frozen 160-epoch horizon?

MOTIVATION
YGG-A3 established that failing corrupt request 141 first reached egress at epoch 159.
It had zero later VERIFY-eligible ticks and therefore could not be repaired by A2's terminal-priority scheduler.
A4 tests the semantic-boundary hypothesis directly rather than extending time or adding general service capacity.

SCIENTIFIC CHANGE
When a matched ROUTE operation moves a request onto its exact egress cell, perform the existing frozen VERIFY check immediately as part of that same local handoff:
- if output is correct: transition directly to VERIFIED and set verified_epoch to the current epoch;
- if output is corrupt: set detected=true and transition directly to REPAIR_PENDING.

This handoff check:
- uses the exact frozen expected-value function;
- uses only the request already present at its local egress;
- consumes no additional matched cell/request pair;
- increments no additional request operation count;
- adds no epoch;
- creates no new routing or processing eligibility;
- does not perform repair atomically.

A corrupt request detected at epoch 159 therefore remains REPAIR_PENDING at the frozen horizon and must satisfy the already-frozen TERMINAL_159 maturity rule exactly.

FROZEN FROM YGG-A1
- exact ten primary manifests;
- exact 160-epoch horizon;
- requests_per_epoch=1;
- exact A -> {B,C} -> D fork/join graph;
- exact programs, seeds, arrivals, lesions, anchor rotations, corruption schedule, expiry, routing, repair semantics, DONE semantics, and local matching;
- exact inherited scheduler with no A2 priority treatment;
- exact local matched-operation capacity;
- exact U_A0 arm;
- exact maturity rules;
- exact baseline-feasibility rule;
- exact duplicate/matching integrity gates;
- no model RNG;
- no learned authority;
- no online adaptation.

MECHANICAL GATE
Before primary execution demonstrate:
- a route entering egress with correct output ends the same matched operation in VERIFIED;
- a route entering egress with corrupt output ends the same matched operation in REPAIR_PENDING with detected=true;
- operation count increases by exactly one for the matched ROUTE and not two;
- no extra matched cell/request pair is created;
- non-egress ROUTE behavior remains unchanged;
- repair remains a later separately matched operation;
- re-verification after repair uses the same atomic egress rule only when a later ROUTE reaches egress; otherwise existing AT_EGRESS repair/reverify semantics remain exact;
- both B/C sibling orders remain exercised;
- D remains blocked until both siblings complete;
- fork dependencies remain exact;
- duplicate execution byte-identical;
- zero incorrect DONE.

PRIMARY
Execute all ten frozen A1 primary worlds twice.
The two complete ordered sweeps must be byte-identical.

SUCCESS
Use the exact A1 capability gates:
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
- atomic correct verifications;
- atomic corruption detections;
- atomic detections at epoch 159;
- total matched operations per world;
- whether replicate 10 request 141 is detected at epoch 159 and satisfies TERMINAL_159.

FALSIFICATION
Any unmet frozen capability gate is a scientific negative.
Do not extend T, weaken maturity, alter manifests, remove corruption, change route distance, add a second matched service operation, or add capacity after observing results.

INTERPRETATION
Positive: the remaining failure is consistent with a terminal handoff semantic gap; local integrity observation must occur at boundary arrival rather than requiring a later scheduling epoch.
Negative: atomic egress observation alone is insufficient; advance to a new preregistered mechanism.

BOUNDARY
No LU-2V mutation.
No shared-baseline promotion from this lane alone.
No learned developmental authority.
No online adaptation.
No recursive self-modification.
