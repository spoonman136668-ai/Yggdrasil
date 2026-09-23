TITLE: TASK-1D — Local Admission Backpressure Differential
DATE: 2026-09-22
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / TASK-1
PARENT: TASK-1C T1CF1 PRIMARY CLOSURE
PARENT CLOSURE: 3e71c2c982790b85db0234205e2c0dae10b5788b
TASK-1B BACKPRESSURE DIAGNOSIS: c1535a7abb4568d1b7fcb64ba18172036fa2dd61

QUESTION

Can a cell use only local queue pressure
to decide when ingress admission deserves priority,
avoiding both:

oldest-first ingress starvation;

and

unconditional ingress-priority downstream flooding?

MOTIVATION

Task-1C established:

unconditional ingress priority
reduced final-16 RAW backlog area
from 452 to 172;

but increased non-RAW backlog area
from 374 to 723;

and reduced Phase-4 final-16 throughput
from 40.625% to 21.875%.

Thus admission starvation is causal,
but fixed priority moves congestion downstream.

Backpressure / max-pressure scheduling
provides the relevant architectural principle:

use local queue differential
to condition service
rather than assigning unconditional priority.

TASK-1D tests only this principle
at the Task-1 admission boundary.

FROZEN PARENTS

Developmental Substrate V0:
92654adf407310a01e368e2c53934beae749482c

Task-1B T1BF1:
83af31c2a95adeba47700f7c34d159d7739549c9

Task-1C T1CF1:
42e149bd9505221da598d9550f9d6ff272a248ea

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

neutral-sense eligibility;

one task operation per cell per epoch;

one task operation per request per epoch;

request expiry;

route direction;

one-edge ROUTE;

verification;

repair;

corruption;

lesion;

anchor rotation +16;

phase lengths;

arrival load;

truth-table interpreter;

request-side deferred acceptance.

PRIMARY ARMS

Exactly four:

OLDEST_NEUTRAL

Exact T1BF1 NEUTRAL_SENSE
with inherited oldest-request-first proposal order.

INGRESS_PRIORITY

Exact T1CF1 treatment:
eligible ingress RAW/SENSE work
is always proposed before non-SENSE work
for ingress-local cells.

PRESSURE_ADMISSION

New Task-1D treatment.

FIXED_ROLE

Exact inherited fixed comparator.

LOCAL PRESSURE DEFINITION

For each nonlesioned cell i
and each stream X in {C,S}
at epoch t:

Q_RAW(i,X)

=
number of unfinished RAW requests
of stream X
located at X's current ingress anchor

when cell i is within R_TASK
of that ingress.

Otherwise Q_RAW(i,X)=0.

Q_DOWN(i,X)

=
number of unfinished,
non-RAW,
non-EXPIRED,
non-DONE requests
of stream X

whose current packet position
is within R_TASK
of cell i.

Define local admission pressure:

P_ADMIT(i,X)
=
Q_RAW(i,X) - Q_DOWN(i,X).

PRESSURE_ADMISSION RULE

For a cell i:

construct the exact inherited
neutral-sense eligible request set.

For a stream X,
RAW/SENSE requests for X
receive proposal priority
over non-SENSE requests

iff:

P_ADMIT(i,X) > 0.

If P_ADMIT(i,X) <= 0:

no RAW priority is granted
for that stream.

If both C and S RAW classes
have positive pressure
for the same cell:

order the two RAW classes
by larger P_ADMIT first.

Exact pressure ties
fall back to:

oldest request;
request id;
existing stateless tie key.

Within each positive-pressure RAW class:

oldest request first;
then request id;
then existing stateless tie key.

All non-prioritized requests
retain inherited oldest-request-first order.

After prioritized RAW candidates
are exhausted,
remaining proposals use inherited order.

ZERO-THRESHOLD / NO TUNING

The threshold is exactly:

P_ADMIT > 0.

There is no:

gain;

ratio;

queue ceiling;

queue floor;

smoothing;

decay;

lookahead;

probability;

stage weight;

global queue;

global throughput;

future phase;

learned scheduler;

or post-result pressure threshold.

The rule compares
current local upstream RAW work

against

current local already-admitted work.

MECHANISM TELEMETRY

For PRESSURE_ADMISSION record:

positive_pressure_opportunities;

pressure_prioritized_sense_matches;

pressure_sense_preemption_count;

mean positive P_ADMIT by stream;

epochs with positive admission pressure by stream;

epochs with nonpositive admission pressure by stream.

Retain all Task-1B ingress diagnostics,
Task-1C priority diagnostics,
and inherited task metrics.

POST-FREEZE DISCIPLINE

Implement and mechanically validate.

Freeze exact implementation as T1DF1.

Only after T1DF1:

derive fresh primary seed;

derive four fresh balanced,
nonconstant,
non-affine programs;

derive exact arrivals;

corruption schedule;

lesion offset;

anchors.

Bind complete manifest
before any primary execution.

Two complete raw primaries
must be byte-identical
before scientific opening.

MECHANICAL GATE

Before T1DF1 prove:

1. OLDEST_NEUTRAL parity
   with frozen T1BF1 NEUTRAL_SENSE.

2. INGRESS_PRIORITY parity
   with frozen T1CF1 treatment.

3. FIXED_ROLE parity
   with inherited fixed control.

4. if P_ADMIT <= 0 for all eligible RAW streams,
   PRESSURE_ADMISSION proposal order
   equals inherited oldest-first exactly.

5. if P_ADMIT > 0,
   only eligible RAW/SENSE proposal ordering
   may move ahead of inherited non-SENSE work.

6. pressure uses only current local request state.

7. request-side deferred acceptance unchanged.

8. eligibility unchanged.

9. request stream immutable.

10. downstream PROCESS / ROUTE / VERIFY / REPAIR
    remain stream-commitment matched.

11. one-op cell and request invariants pass.

12. all inherited integrity probes pass.

13. two complete mechanical sweeps
    are byte-identical.

PRIMARY INFORMATION GAIN

TASK1D_BACKPRESSURE_INFORMATION_GAIN = TRUE iff all are true:

1. mechanism active:
   pressure_sense_preemption_count > 0;

2. Phase-0 PRESSURE_ADMISSION completion
   is at least 95% of OLDEST_NEUTRAL;

3. final-16 total backlog area
   is at least 20% lower
   than OLDEST_NEUTRAL;

4. final-16 total backlog area
   is at least 20% lower
   than INGRESS_PRIORITY;

5. Phase-4 final-16 correct completion
   is at least 10 percentage points higher
   than OLDEST_NEUTRAL;

6. Phase-4 final-16 correct completion
   is at least 10 percentage points higher
   than INGRESS_PRIORITY;

7. incorrect DONE = 0;

8. operations per correct completion
   <=125% of OLDEST_NEUTRAL;

9. all integrity probes pass.

PRIMARY QUALIFICATION

TASK1D_QUALIFIED = TRUE iff
TASK1D_BACKPRESSURE_INFORMATION_GAIN = TRUE
and all are true:

1. Phase-4 final-16 correct completion >=85%;

2. anchor-rotation recovery latency <=8 epochs;

3. final-16 RAW backlog area
   <=60% of OLDEST_NEUTRAL;

4. final-16 non-RAW backlog area
   <=125% of OLDEST_NEUTRAL;

5. demand-reversal recovery <=8 epochs;

6. lesion recovery <=8 epochs
   OR lesion backlog area
   no worse than OLDEST_NEUTRAL;

7. repair detection >=95%;

8. repair success >=90%.

FAILURE ATTRIBUTION

If pressure reduces downstream flooding
but does not improve Phase-4 throughput:

admission control is not
the remaining dominant seam.

If pressure improves both RAW and non-RAW backlog
but not enough for qualification:

local congestion awareness is useful,
but Task-1 still lacks adequate
spatial execution redistribution.

If pressure oscillates between
admit / do-not-admit
and worsens latency:

instantaneous queue differential
is too reactive for this substrate.

Do not add smoothing inside Task-1D.

If PRESSURE_ADMISSION qualifies:

a local queue differential
is sufficient to coordinate
front-door admission with nearby pipeline load
without a central scheduler.

NO POST-RESULT TUNING

Do not change:

pressure definition;

zero threshold;

queue scope;

R_TASK;

eligibility;

phase lengths;

arrival load;

expiry;

repair;

D family;

G5;

V0;

or qualification
after primary results.

EXTERNAL RESEARCH ALIGNMENT

Backpressure / max-pressure scheduling
is an established decentralized queue-control family
in which local queue differences
drive service or routing decisions.

Recent work continues to use
local-information max-pressure / backpressure
for decentralized network control,
while also documenting practical delay
and queue-structure tradeoffs.

Task-1D does not claim
theoretical throughput optimality.

It imports only the narrow design principle:

LOCAL UPSTREAM LOAD
MINUS
LOCAL DOWNSTREAM LOAD

can be a useful decentralized
service-pressure signal.

PLAIN-SPEAK QUESTION

Task-1C opened the front door too wide.

Task-1D gives the cell
one local question before it does that:

"Are more jobs waiting outside
than I already have piled up nearby inside?"

If yes,
admit the new work first.

If no,
keep finishing the older work.

No central scheduler sees the whole organism.

No one tunes a percentage.

The cell only compares
two nearby piles.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
