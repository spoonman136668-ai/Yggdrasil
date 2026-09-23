TITLE: TASK-1C T1CF1 PRIMARY CLOSURE
DATE: 2026-09-22
STATUS: CLOSED NEGATIVE / ADMISSION STARVATION CONFIRMED / CONGESTION SHIFTED DOWNSTREAM
TRACK: DG-1 / TASK-1C

T1CF1:
42e149bd9505221da598d9550f9d6ff272a248ea

MANIFEST BINDING:
c1ab14d1705919dd3de78d4f842cab6c713ca55c

PRIMARY MANIFEST SHA256:
f9951bb57215d07fcdc2c6426c3effa0167bab0427c16c9b80b0222641a342cd

DUPLICATE PRIMARY

runs:
2

raw output bytes:
37586 each

raw output SHA256:
cc699e845ace5eaa97cf8e92ccba803c8059ad13d0f4d6688f153f5438918371

byte identical:
true

all integrity probes:
PASS

SCIENTIFIC STATUS

TASK1C_LOCAL_ADMISSION_GAIN:
FALSE

MECHANISM ACTIVE:
TRUE

INGRESS_PRIORITY opportunities:
1231

INGRESS_PRIORITY SENSE matches:
320

SENSE preemptions of strictly older downstream work:
304

Therefore the scheduling treatment was strongly exercised.

OLDEST_NEUTRAL

correct DONE:
190 / 320

overall correct completion:
59.375%

expired:
85

final backlog:
45

operations per correct completion:
12.4684

Phase-0 completion:
100%

Phase-4 final-16 correct completion:
40.625%

anchor-rotation recovery:
NOT ATTAINED

final-16 RAW backlog area:
452

final-16 non-RAW backlog area:
374

lesion recovery:
2 epochs

INGRESS_PRIORITY

correct DONE:
205 / 320

overall correct completion:
64.0625%

expired:
59

final backlog:
56

operations per correct completion:
13.8585

Phase-0 completion:
100%

Phase-4 final-16 correct completion:
21.875%

anchor-rotation recovery:
NOT ATTAINED

final-16 RAW backlog area:
172

final-16 non-RAW backlog area:
723

lesion recovery:
0 epochs

CHANGE VERSUS OLDEST_NEUTRAL

overall completion:
+4.6875 percentage points

RAW backlog area:
-280
(-61.95%)

non-RAW backlog area:
+349
(+93.32%)

Phase-4 final-16 throughput:
-18.75 percentage points

QUALIFICATION

PASS:
mechanism active.

PASS:
Phase-0 non-regression.

PASS:
RAW backlog reduced >=40%.

PASS:
lesion criterion.

PASS:
incorrect DONE = 0.

PASS:
operation cost <=125% parent.

PASS:
repair success >=90%.

PASS:
integrity.

FAIL:
Phase-4 final-16 >=85%.

FAIL:
Phase-4 improvement >=20 percentage points.

FAIL:
anchor-rotation recovery <=8 epochs.

FAIL:
non-RAW backlog <=125% parent.

FAIL:
demand-reversal recovery <=8 epochs.

FAIL:
repair detection >=95%.

REPAIR NOTE

INGRESS_PRIORITY scheduled corruptions:
19

corruptions reaching egress:
14

verification detected:
12

repair success among detected:
100%

incorrect DONE:
0

The repair-detection failure is consistent with downstream congestion:
two corrupted packets recorded as reaching the egress path
did not complete the expected detection surface before the horizon / queue progression.

CAUSAL INTERPRETATION

Task-1C confirms both halves of the scheduling diagnosis.

First:

old downstream work really was starving ingress admission.

When RAW is given local priority,
RAW backlog falls by approximately 62%.

Second:

unconditional ingress priority is not a solution.

The admitted work accumulates downstream.

Non-RAW backlog nearly doubles.

Phase-4 end throughput becomes substantially worse.

Therefore the organism does not need:

more SENSE privilege;

a larger task radius;

more permanent ingress capacity;

or a tuned priority percentage.

It needs a local rule that couples admission
to downstream service capacity.

This is the classical shape of a backpressure problem:

admit / forward work
when the downstream pipeline can absorb it;

slow admission
when downstream queues are already saturated.

The required signal must remain local.

NEXT JUSTIFIED STEP

Research and preregister a local backpressure scheduler
using only locally observable queue / stage information.

The next mechanism should not introduce:

global queue length;

global throughput;

future phase identity;

central scheduling;

dynamic topology;

a tuned probability;

or permanent roles.

The comparison should isolate:

oldest-first;

unconditional ingress priority;

and one preregistered local backpressure rule.

PLAIN-SPEAK INTERPRETATION

We proved the old jobs were cutting in line.

Then we forced new jobs to the front.

That fixed the front-door pileup.

But it created a much bigger pileup inside the building.

So the problem is not simply:

"new jobs need priority."

The organism needs to know,
using only nearby information,

whether the next part of the pipeline
has room before admitting more work.

That is a local backpressure problem.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
