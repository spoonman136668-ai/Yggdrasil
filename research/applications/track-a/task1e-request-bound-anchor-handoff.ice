TITLE: TASK-1E — Request-Bound Anchor Handoff
DATE: 2026-09-22
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / TASK-1
PARENT: TASK-1D T1DF1 PRIMARY CLOSURE
PARENT CLOSURE: 08179f03b4e20ab1c8f66f32f69b68b68706f83d
HANDOFF DIAGNOSIS: d3c42b834e684a7716c3c87f4c9b36d02c9c82c6

QUESTION

Does Task-1 spatial relocation recover
when each request retains the ingress / egress anchor generation
that existed when the request was created,
rather than retroactively rebinding all unfinished work
to the new anchors?

MOTIVATION

The exact frozen Task-1D replay showed that
the Phase-4 failure is dominated by flow-handoff debt.

At epoch 128:

33 legacy requests remain unfinished.

Only 3 of those 33 ultimately finish.

30 expire.

Legacy requests consume:

369 of 518 Phase-4 ROUTE operations.

Legacy share of Phase-4 route service:

71.24%.

Legacy RAW work at the old ingress has zero eligible SENSE cells
after the anchor change.

Legacy S work already in flight is rebound to the new S egress
while route direction remains counterclockwise.

Observed legacy S remaining route distances after the shift:

mean:
45.59 hops.

median:
45.

p90:
52.

max:
56.

The global request expiry remains 32 epochs.

Thus the existing relocation test conflates:

reorganization around new demand

with

retroactive migration of old in-flight work.

Task-1E isolates only that interface seam.

FROZEN PARENTS

Developmental Substrate V0:
92654adf407310a01e368e2c53934beae749482c

Task-1 T1F1:
22b6ab5a036732cc9efbda077069e971c34a337e

Task-1B T1BF1:
83af31c2a95adeba47700f7c34d159d7739549c9

Task-1D T1DF1:
4f57b9adfdaa8041757ca02e15dcf70a1429f9ad

PRIMARY BASELINE

Task-1E returns to the frozen
T1BF1 NEUTRAL_SENSE + oldest-request-first scheduler.

Reason:

Task-1C unconditional ingress priority failed.

Task-1D admission backpressure failed.

Neither scheduling treatment earned retention.

Task-1E therefore isolates handoff semantics
on the simplest surviving neutral-sense parent.

NO V0 CHANGE

Preserve exactly:

D2;

G5_FULL OFF;

B update;

rho = 3/4;

V0 evidence radii;

cooperative radius;

ECHO_PHASE;

Hill law;

refractory semantics;

recruitment law;

fixed 64-cell ring topology;

R_TASK = 2;

one operation per cell per epoch;

one operation per request per epoch;

request expiry = 32 epochs;

neutral-sense eligibility;

stream-matched PROCESS / ROUTE / VERIFY / REPAIR;

one-edge routing;

fixed route direction;

verification;

repair;

corruption rate and stateless identity;

distributed lesion semantics;

anchor shift = +16;

phase lengths;

arrival load;

truth-table interpreter;

request-side deferred acceptance;

oldest-request-first local scheduling.

No dynamic topology.

No central scheduler.

No global queue input.

No phase oracle.

No learned controller.

ANCHOR GENERATION CONTRACT

For every request r:

REQUEST_ANCHORS(r)
=
anchors_for(seed, r.created).

This is deterministic from:

the frozen task seed;

the request creation epoch;

the frozen anchor schedule.

No additional learned state exists.

No request changes its anchor generation after creation.

REQUEST-BOUND SENSE

A RAW request may be sensed only at
its REQUEST_ANCHORS ingress.

Thus:

requests created before epoch 128
remain senseable at the old ingress
until sensed or expired;

requests created at or after epoch 128
are created and sensed at the new ingress.

No request teleports.

REQUEST-BOUND ROUTE COMPLETION

ROUTE direction remains:

C:
clockwise.

S:
counterclockwise.

Each ROUTE operation still moves exactly one ring edge.

A request reaches AT_EGRESS
when its packet position reaches
its REQUEST_ANCHORS egress.

Thus:

pre-rotation in-flight work
continues toward the old egress;

new Phase-4 work
uses the new egress.

No route is reversed.

No path planner exists.

VERIFY / REPAIR

VERIFY and REPAIR remain local to the packet position.

No change.

PRIMARY ARMS

Exactly three.

DYNAMIC_REBIND

Exact T1BF1 NEUTRAL_SENSE
with inherited oldest-request-first matching
and inherited CURRENT-anchor semantics.

This is the causal parent.

REQUEST_BOUND

Exact same dynamics and scheduler,
except SENSE and ROUTE completion
use REQUEST_ANCHORS(r).

FIXED_BOUND

Exact inherited FIXED_ROLE controller
under the same REQUEST_ANCHORS task semantics.

Its permanent role map remains frozen
at the initial spatial placement.

The fixed role map does not rotate.

PURPOSE OF FIXED_BOUND

This is a conventional assigned-role comparator
under the repaired task handoff semantics.

It does not enter the causal treatment delta
between DYNAMIC_REBIND and REQUEST_BOUND.

MECHANISM TELEMETRY

For REQUEST_BOUND report:

unfinished legacy requests at epoch 128;

legacy RAW requests sensed after epoch 128;

legacy requests routed after epoch 128;

legacy requests reaching their request-bound egress;

legacy requests completed;

legacy requests expired;

new Phase-4 requests completed;

Phase-4 ROUTE operations spent on legacy versus new work;

legacy remaining route distance at epoch 128
under request-bound semantics;

legacy remaining route distance under dynamic-rebind semantics
for descriptive comparison.

Also retain all inherited Task-1 / Task-1B metrics.

PRE-ROTATION PARITY

Because REQUEST_ANCHORS equals CURRENT anchors
for every request before epoch 128:

DYNAMIC_REBIND and REQUEST_BOUND
must be behaviorally identical through epoch 127.

Mechanical gate must prove exact pre-rotation trace parity.

Any pre-128 divergence fails the experiment.

POST-FREEZE DISCIPLINE

Implement and mechanically validate.

Freeze exact implementation as T1EF1.

Only after T1EF1:

derive fresh primary seed;

derive four fresh balanced,
nonconstant,
non-affine programs;

derive arrivals;

corruption schedule;

lesion offset;

anchors.

Bind complete manifest
before any primary arm execution.

Two complete raw primaries
must be byte-identical
before scientific opening.

MECHANICAL GATE

Before T1EF1 prove:

1. DYNAMIC_REBIND exact parity
   with frozen T1BF1 NEUTRAL_SENSE
   on the mechanical manifest.

2. FIXED_BOUND equals inherited FIXED_ROLE
   before epoch 128.

3. REQUEST_BOUND equals DYNAMIC_REBIND
   through epoch 127.

4. request-bound ingress
   equals anchors_for(seed, created).

5. request-bound egress
   equals anchors_for(seed, created).

6. pre-rotation requests retain old anchors
   after t = 128.

7. Phase-4 requests use new anchors.

8. no request teleportation.

9. one-edge route invariant.

10. route direction invariant.

11. neutral-sense rule unchanged.

12. downstream stream matching unchanged.

13. one-op cell and request invariants pass.

14. all inherited integrity probes pass.

15. two complete mechanical sweeps
    are byte-identical.

PRIMARY INFORMATION GAIN

TASK1E_HANDOFF_INFORMATION_GAIN = TRUE iff all are true:

1. mechanism active:
   at least one legacy RAW request
   is sensed after epoch 128
   OR at least one legacy in-flight request
   reaches its old request-bound egress
   after epoch 128;

2. Phase-0 REQUEST_BOUND completion
   is at least 95% of DYNAMIC_REBIND;

3. pre-rotation behavior through epoch 127
   remains exact-parity;

4. Phase-4 final-16 correct completion
   is at least 20 percentage points higher
   than DYNAMIC_REBIND;

5. final-16 total backlog area
   is at least 30% lower
   than DYNAMIC_REBIND;

6. at least 50% of the unfinished legacy cohort
   present at epoch 128
   completes correctly before expiry;

7. incorrect DONE = 0;

8. operations per correct completion
   <=125% of DYNAMIC_REBIND;

9. all integrity probes pass.

PRIMARY QUALIFICATION

TASK1E_QUALIFIED = TRUE iff
TASK1E_HANDOFF_INFORMATION_GAIN = TRUE
and all are true:

1. Phase-4 final-16 correct completion >=85%;

2. anchor-rotation recovery latency <=8 epochs;

3. demand-reversal recovery latency <=8 epochs;

4. lesion recovery latency <=8 epochs
   OR lesion backlog area
   no worse than DYNAMIC_REBIND;

5. repair detection >=95%;

6. repair success >=90%.

FAILURE ATTRIBUTION

If legacy cohort completion improves strongly
but new Phase-4 throughput remains poor:

the handoff defect is real
but a genuine spatial service-redeployment deficit remains.

If both legacy completion
and new Phase-4 throughput improve
but qualification is missed narrowly:

request-bound handoff is useful,
but additional task-interface or service redistribution
may still be required.

If REQUEST_BOUND fails to improve
legacy expiration or route debt:

the diagnosis is wrong
or implementation does not isolate the intended anchor semantics.

If REQUEST_BOUND qualifies:

the prior Task-1 relocation failures
were materially confounded
by retroactive in-flight destination rebinding.

The frozen V0 organism then has positive evidence
for useful spatial functional reorganization
under a clean handoff contract.

NO POST-RESULT TUNING

Do not change after primary results:

anchor-binding rule;

creation-time generation rule;

arrival load;

expiry;

route length;

route direction;

R_TASK;

scheduler;

neutral sensing;

phase lengths;

anchor displacement;

D family;

G5;

V0;

repair;

or qualification.

EXTERNAL DESIGN ALIGNMENT

The narrow engineering analogy is
flow/session continuity during endpoint migration:

old in-flight work is allowed to drain
under its established flow context
while new work enters through the new context.

Task-1E does not import
a network protocol or theorem.

It tests only the causal principle
that relocation should not silently rewrite
the destination semantics of already-admitted work.

PLAIN-SPEAK QUESTION

When the workplace moves,
should jobs already inside the old workplace
be told that their finish line suddenly moved too?

Task-1D says that rule creates a giant traffic jam.

Task-1E does something simpler:

old jobs finish through the old door;

new jobs start at the new door.

Nothing teleports.

Nothing gets deleted.

The cells still have to reorganize locally.

We are just removing the artificial rule
that changes an old job's destination halfway through the job.

Then we ask again:

CAN THE ORGANISM REORGANIZE AROUND THE NEW WORK LOCATION?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
