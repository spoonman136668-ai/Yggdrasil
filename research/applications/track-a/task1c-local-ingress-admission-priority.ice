TITLE: TASK-1C — Local Ingress Admission Priority
DATE: 2026-09-22
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / TASK-1
PARENT: TASK-1B T1BF1 PRIMARY CLOSURE
PARENT CLOSURE: b6cc257acbbd839ef6d831e4ed6afd1abd34d482
DIAGNOSIS: c1535a7abb4568d1b7fcb64ba18172036fa2dd61

QUESTION

After commitment-neutral sensing,
does spatial relocation still fail because
the local oldest-request-first matcher
lets older downstream work monopolize cells
that could admit new work at the relocated ingress?

CAUSAL HYPOTHESIS

The Phase-4 diagnosis found:

eligible RAW work exists at the relocated S ingress;

but in the final 16 epochs
S SENSE executes zero times on average;

while older PROCESS / ROUTE / VERIFY work
continues consuming local stream-matched cells.

Therefore the remaining candidate bottleneck is not
visibility or basic eligibility.

It is local admission starvation.

TASK-1C changes only
the ordering of a cell's local task proposals.

FROZEN PARENTS

Developmental Substrate V0:
92654adf407310a01e368e2c53934beae749482c

Task-1 T1F1:
22b6ab5a036732cc9efbda077069e971c34a337e

Task-1B T1BF1:
83af31c2a95adeba47700f7c34d159d7739549c9

Task-1B source SHA256:
e8d409c5eb8e750123aae4979fd1091611a915c22f7cf977e420345186aef6b9

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

fixed ring topology;

R_TASK = 2;

one task operation per cell per epoch;

one task operation per request per epoch;

request expiry;

route direction;

one-edge ROUTE;

verification;

repair;

corruption semantics;

lesion semantics;

anchor rotation +16;

phase lengths;

arrival load;

truth-table interpreter.

Preserve Task-1B commitment-neutral SENSE eligibility exactly.

PRIMARY ARMS

Exactly three:

OLDEST_NEUTRAL

Exact Task-1B NEUTRAL_SENSE dynamics
with the inherited oldest-request-first matcher.

INGRESS_PRIORITY

Exact OLDEST_NEUTRAL dynamics
except for one local proposal-order rule.

FIXED_ROLE

Exact inherited fixed-role comparator.
No role-map movement.
No scheduling change.

INGRESS_PRIORITY RULE

For each nonlesioned cell
at each epoch:

construct the exact same set
of locally eligible unfinished requests
as OLDEST_NEUTRAL.

If the cell is within R_TASK
of a stream ingress
and has one or more eligible RAW requests
for that ingress:

place those eligible RAW/SENSE requests
ahead of all eligible non-SENSE requests
in that cell's proposal list.

Within the RAW/SENSE class:

preserve oldest-request-first ordering,
then request id,
then the existing stateless tie key.

After all eligible RAW/SENSE options
for that cell are exhausted:

preserve the inherited
oldest-request-first ordering
for every remaining eligible request.

For cells with no eligible ingress RAW work:

proposal ordering is exactly inherited.

REQUEST-SIDE DEFERRED ACCEPTANCE

Unchanged.

A request receiving proposals
still chooses among proposing cells
using the inherited stateless:

TASK1-REQUEST-CELL-PREF

hash ordering.

A rejected cell continues
to its next local preference.

Therefore TASK-1C changes
only the order in which an ingress-local cell
offers its one epoch of task capacity.

NO NEW PARAMETER

There is:

no scheduling probability;

no fairness fraction;

no new timer;

no queue threshold;

no backlog threshold;

no global congestion signal;

no learned scheduler;

no stage weight;

no per-stream quota;

no permanent role reservation.

The treatment is binary:

ingress-local RAW first
versus inherited oldest-first.

MECHANISM ACTIVITY TELEMETRY

For INGRESS_PRIORITY record:

ingress_priority_opportunities;

ingress_priority_sense_matches;

sense_preemption_count.

A SENSE match counts as a preemption iff
the matched cell had at least one
eligible non-SENSE request
strictly older than the selected RAW request
at the moment preferences were constructed.

Also retain all Task-1B ingress diagnostics
and all inherited Task-1 metrics.

POST-FREEZE MANIFEST DISCIPLINE

Implement and mechanically validate first.

Freeze exact implementation as T1CF1.

Only after T1CF1:

derive a fresh primary seed from T1CF1;

derive four fresh balanced,
nonconstant,
non-affine truth tables;

derive exact 320-request arrival manifest;

derive corruption schedule;

derive lesion offset;

derive initial anchors.

Bind the complete manifest identity
before any primary execution.

Run two complete raw primaries byte-identically.

Only the external duplicate gate
may open scientific metrics.

MECHANICAL GATE

Before T1CF1 prove:

1. OLDEST_NEUTRAL is behaviorally identical
   to frozen T1BF1 NEUTRAL_SENSE
   under a shared mechanical manifest.

2. FIXED_ROLE is behaviorally identical
   to the frozen inherited fixed comparator.

3. If no eligible ingress RAW request exists,
   INGRESS_PRIORITY local preferences
   equal inherited preferences exactly.

4. INGRESS_PRIORITY may reorder only
   eligible RAW/SENSE requests
   ahead of non-SENSE requests
   for ingress-local cells.

5. It cannot change request stream.

6. It cannot change task stage semantics.

7. It cannot alter request-side
   deferred-acceptance preference.

8. It cannot exceed one operation
   per cell or request per epoch.

9. R_TASK remains 2.

10. neutral-sense eligibility remains exact.

11. PROCESS / ROUTE / VERIFY / REPAIR
    remain stream-commitment matched.

12. all inherited integrity probes pass.

13. two complete mechanical sweeps
    are byte-identical.

PRIMARY QUALIFICATION

TASK1C_LOCAL_ADMISSION_GAIN = TRUE iff all are true:

1. mechanism active:
   sense_preemption_count > 0;

2. Phase-0 INGRESS_PRIORITY
   correct-completion fraction
   is at least 95%
   of OLDEST_NEUTRAL;

3. Phase-4 final-16
   correct-completion rate
   is at least 85%;

4. Phase-4 final-16 rate
   improves by at least
   20 percentage points
   versus OLDEST_NEUTRAL;

5. anchor-rotation recovery latency
   is <= 8 epochs;

6. final-16 RAW backlog area
   is at least 40% lower
   than OLDEST_NEUTRAL;

7. final-16 non-RAW unfinished backlog area
   is no more than 125%
   of OLDEST_NEUTRAL;

8. demand-reversal recovery
   remains <= 8 epochs;

9. lesion recovery remains <= 8 epochs
   OR lesion backlog area
   is no worse than OLDEST_NEUTRAL;

10. incorrect DONE = 0;

11. operations per correct completion
    <=125% of OLDEST_NEUTRAL;

12. repair detection >=95%;

13. repair success >=90%;

14. all integrity probes pass.

FAILURE ATTRIBUTION

If RAW backlog falls strongly
but non-RAW backlog rises enough
to prevent throughput recovery:

local ingress starvation is real,
but unconditional ingress priority
merely moves congestion downstream.

Then do not tune a priority percentage.

The next question becomes
whether a genuinely local backpressure signal
can balance admission against downstream capacity.

If ingress priority is active
but RAW backlog does not fall materially:

the scheduling diagnosis is incomplete.

If Phase 4 qualifies
without nominal / lesion / repair regression:

the principal relocation failure
was local admission starvation,
not inability to reorganize functional commitment.

NO POST-RESULT TUNING

Do not change after results:

priority scope;

RAW definition;

R_TASK;

eligibility;

phase lengths;

anchor rotation;

arrival load;

expiry;

repair;

D family;

G5 status;

V0 dynamics;

qualification thresholds.

PLAIN-SPEAK QUESTION

The cells can see the new jobs now.

The problem is that
the old jobs keep cutting in line.

Task-1C does one simple thing:

right at the front door,
a cell offers its next unit of work
to a waiting new arrival first.

Everywhere else,
the old rule stays the same.

If that restores relocation,
the bottleneck was admission starvation.

If it only pushes the traffic jam
one stage deeper,
we will see that too.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
