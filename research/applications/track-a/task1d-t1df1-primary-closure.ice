TITLE: TASK-1D T1DF1 PRIMARY CLOSURE
DATE: 2026-09-22
STATUS: CLOSED NEGATIVE / LOCAL ADMISSION BACKPRESSURE ACTIVE BUT INSUFFICIENT
TRACK: DG-1 / TASK-1D

T1DF1:
4f57b9adfdaa8041757ca02e15dcf70a1429f9ad

MANIFEST BINDING:
b8b582e62fbd3574755257743e424806403d4461

PRIMARY MANIFEST SHA256:
80da942fecf911f3e4e11a16347e7241a61e11bc8834a2eb7c4fefde84121566

DUPLICATE PRIMARY

runs:
2

raw output bytes:
43761 each

raw output SHA256:
a96ea8246da32a0e8191fd98a5204cc23bc8280d65f6f2199d3eedbeb73959df

byte identical:
true

all integrity probes:
PASS

SCIENTIFIC STATUS

TASK1D_BACKPRESSURE_INFORMATION_GAIN:
FALSE

TASK1D_QUALIFIED:
FALSE

MECHANISM ACTIVE:
TRUE

positive-pressure opportunities:
242

pressure-prioritized SENSE matches:
214

pressure SENSE preemptions of older downstream work:
206

Mean positive P_ADMIT:

C:
1.48696

S:
1.37008

Thus the local queue-differential treatment
was genuinely active.

OLDEST_NEUTRAL

correct DONE:
237 / 320

overall correct completion:
74.0625%

expired:
38

final backlog:
45

Phase-0 completion:
100%

Phase-4 final-16 correct completion:
53.125%

anchor-rotation recovery:
NOT ATTAINED

demand-reversal recovery:
5 epochs

lesion recovery:
0 epochs

final-16 RAW backlog area:
614

final-16 non-RAW backlog area:
252

final-16 total backlog area:
866

operations per correct completion:
11.0844

INGRESS_PRIORITY

correct DONE:
241 / 320

overall correct completion:
75.3125%

expired:
26

final backlog:
53

Phase-4 final-16 correct completion:
18.75%

anchor-rotation recovery:
NOT ATTAINED

demand-reversal recovery:
5 epochs

lesion recovery:
5 epochs

final-16 RAW backlog area:
32

final-16 non-RAW backlog area:
848

final-16 total backlog area:
880

operations per correct completion:
11.7012

PRESSURE_ADMISSION

correct DONE:
238 / 320

overall correct completion:
74.375%

expired:
30

final backlog:
52

Phase-4 final-16 correct completion:
28.125%

anchor-rotation recovery:
NOT ATTAINED

demand-reversal recovery:
3 epochs

lesion recovery:
0 epochs

final-16 RAW backlog area:
343

final-16 non-RAW backlog area:
553

final-16 total backlog area:
896

operations per correct completion:
12.3277

REPAIR / SAFETY — PRESSURE_ADMISSION

scheduled corruptions:
14

corruptions reaching egress:
11

verification detected:
11 / 11

repair success:
11 / 11

incorrect DONE:
0

repair detection:
100%

repair success:
100%

QUALIFICATION INTERPRETATION

PRESSURE_ADMISSION passes:

mechanism activity;

Phase-0 non-regression;

RAW-backlog reduction threshold;

demand-reversal recovery;

lesion recovery;

incorrect-DONE safety;

operation-cost boundary;

repair detection;

repair success;

integrity.

It fails:

total-backlog improvement versus OLDEST_NEUTRAL;

total-backlog improvement versus INGRESS_PRIORITY;

Phase-4 throughput improvement versus OLDEST_NEUTRAL;

Phase-4 throughput improvement versus INGRESS_PRIORITY;

Phase-4 >=85%;

anchor-rotation recovery;

non-RAW backlog non-regression.

CAUSAL INTERPRETATION

The local differential does what it was designed to do:

it avoids the extreme admission flood
created by unconditional INGRESS_PRIORITY.

Its queue split lies between:

OLDEST_NEUTRAL
and
INGRESS_PRIORITY.

But it does not improve total congestion.

Compared with OLDEST_NEUTRAL:

RAW backlog falls by 271 area-units;

non-RAW backlog rises by 301;

total backlog rises slightly;

and final-window throughput falls
from 53.125%
to 28.125%.

Therefore:

the remaining Task-1 relocation problem
is not solvable by an admission-only signal,
even when that signal is local and congestion-aware.

The bottleneck has moved beyond
the boundary between RAW and admitted work.

The next diagnostic must localize
the downstream spatial service deficit itself.

Do not tune:

the pressure threshold;

queue weights;

smoothing;

gain;

or admission probability.

NEXT JUSTIFIED STEP

Run an observation-only frozen replay
that measures for Phase 4:

stage occupancy by spatial position;

eligible stream-matched cell count
around each packet;

service matches by stage and ring sector;

packet movement / route-hop throughput;

time spent waiting by stage;

distance from relocated ingress / egress;

and whether backlog clusters
at particular ring regions.

The next causal mechanism,
if any,
must target the first downstream spatial bottleneck
demonstrated by that diagnosis.

PLAIN-SPEAK INTERPRETATION

We gave the front door
a local congestion gauge.

It worked as a gauge.

It stopped the system
from opening the door as aggressively
as Task-1C did.

But it still did not make the pipeline faster.

It only chose a middle-sized traffic jam.

That means the real remaining problem
is not deciding how many jobs
to let through the door.

Something deeper inside
the spatial pipeline
cannot redeploy fast enough
after the work locations move.

Now we measure exactly where.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
