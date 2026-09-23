TITLE: TASK-1E T1EF1 PRIMARY CLOSURE
DATE: 2026-09-22
STATUS: CLOSED FORMAL NEGATIVE / STRONG CAUSAL HANDOFF GAIN / NEAR-QUALIFICATION
TRACK: DG-1 / TASK-1E

T1EF1:
04872029aeb773b3e98ccb71537c18ff965487e1

MANIFEST BINDING:
1c762a4a3d4b5685c225e339940f53d4b9cf224b

PRIMARY MANIFEST SHA256:
b759aca22f379bffa887ea820cb476a9f8a9da15bf58c78cb3f7b52455edccda

AUTHORITATIVE DUPLICATE PRIMARY

runs:
2

raw output bytes:
40057 each

raw output SHA256:
b983ef1e086318851dac61b7bbd55fd5a150e4e7b9d45ddd842512684067dba3

byte identical:
true

external duplicate-primary gate:
PASS

all integrity probes:
PASS

SCIENTIFIC STATUS

TASK1E_HANDOFF_INFORMATION_GAIN:
FALSE

TASK1E_QUALIFIED:
FALSE

FORMAL INFORMATION-GAIN CHECKS

PASS:
mechanism active.

PASS:
Phase-0 REQUEST_BOUND >=95% DYNAMIC_REBIND.

PASS:
exact pre-rotation trace parity.

PASS:
Phase-4 final-16 gain >=20 percentage points.

Observed gain:
+43.75 percentage points.

PASS:
legacy cohort completion >=50%.

Observed:
97.6744%.

PASS:
incorrect DONE = 0.

PASS:
operations per correct completion <=125% DYNAMIC_REBIND.

PASS:
integrity.

FAIL:
final-16 total backlog area reduced >=30%.

DYNAMIC_REBIND:
889.

REQUEST_BOUND:
638.

Reduction:
28.2340%.

Miss against frozen 30% threshold:
1.7660 percentage points.

FORMAL QUALIFICATION CHECKS

PASS:
anchor-rotation recovery <=8 epochs.

REQUEST_BOUND:
0 epochs.

PASS:
demand-reversal recovery <=8 epochs.

REQUEST_BOUND:
2 epochs.

PASS:
lesion recovery criterion.

REQUEST_BOUND:
0 epochs.

PASS:
repair detection >=95%.

REQUEST_BOUND:
100%.

PASS:
repair success >=90%.

REQUEST_BOUND:
93.75%.

FAIL:
TASK1E_HANDOFF_INFORMATION_GAIN is FALSE
because the frozen backlog-reduction threshold is not met.

FAIL:
Phase-4 final-16 correct completion >=85%.

REQUEST_BOUND:
78.125%.

Miss against frozen threshold:
6.875 percentage points.

DYNAMIC_REBIND RESULT

correct DONE:
229 / 320.

overall correct completion:
71.5625%.

expired:
40.

Phase-4 final-16 correct completion:
34.375%.

anchor-rotation recovery:
NOT ATTAINED.

demand-reversal recovery:
2 epochs.

lesion recovery:
0 epochs.

final-16 total backlog area:
889.

operations per correct completion:
10.8689956332.

LEGACY HANDOFF — DYNAMIC_REBIND

unfinished legacy requests at epoch 128:
43.

legacy correct DONE:
3.

legacy expired:
40.

legacy completion fraction:
6.9767%.

legacy RAW at epoch 128:
28.

legacy RAW sensed after rotation:
0.

legacy requests reaching request egress after rotation:
3.

legacy route operations after rotation:
179.

Legacy in-flight remaining route distance at epoch 128
under dynamic rebinding:

n:
13.

mean:
36.6154.

median:
49.

p90:
54.

max:
55.

The same cohort under creation-time request-bound geometry would have:

mean:
3.3846.

median:
3.

p90:
6.

max:
7.

REQUEST_BOUND RESULT

correct DONE:
275 / 320.

overall correct completion:
85.9375%.

expired:
1.

Phase-4 final-16 correct completion:
78.125%.

anchor-rotation recovery:
0 epochs.

demand-reversal recovery:
2 epochs.

lesion recovery:
0 epochs.

final-16 total backlog area:
638.

operations per correct completion:
9.9236363636.

CHANGE VERSUS DYNAMIC_REBIND

overall correct completion:
+14.375 percentage points.

Phase-4 final-16:
+43.75 percentage points.

final-16 total backlog area:
-251 area-units.

relative backlog reduction:
28.2340%.

operations per correct completion:
improved from 10.8690 to 9.9236.

LEGACY HANDOFF — REQUEST_BOUND

unfinished legacy requests at epoch 128:
43.

legacy correct DONE:
42.

legacy expired:
1.

legacy completion fraction:
97.6744%.

legacy RAW at epoch 128:
28.

legacy RAW sensed after rotation:
28.

legacy requests reaching request-bound egress after rotation:
43.

legacy route operations after rotation:
240.

Thus creation-time anchor binding
removes the previously diagnosed orphaning
and destination-rebinding failure.

REPAIR / SAFETY — REQUEST_BOUND

scheduled corruptions:
19.

corruptions applied:
16.

corruptions reaching egress:
16.

verification detected:
16 / 16.

detection fraction:
100%.

repaired:
16.

correct DONE after repair:
15.

repair success fraction of detected:
93.75%.

incorrect DONE:
0.

median noncorrupt latency:
15 epochs.

FIXED_BOUND

correct DONE:
46 / 320.

overall correct completion:
14.375%.

Phase-4 final-16:
0%.

final-16 total backlog area:
1024.

anchor-rotation recovery:
NOT ATTAINED.

The permanently assigned controller
does not spatially redeploy its functional roles.

CAUSAL INTERPRETATION

Task-1E strongly confirms the Task-1D handoff diagnosis.

Retroactive rebinding of unfinished work
was a major artificial source
of the prior spatial-relocation failure.

Under request-bound semantics:

legacy cohort completion rises
from 6.98%
to 97.67%;

anchor recovery changes
from not attained
to immediate;

Phase-4 final-window throughput rises
by 43.75 percentage points;

overall completion rises
by 14.375 percentage points;

operation cost per correct completion falls;

verification / repair safety remains intact.

Therefore:

REQUEST-BOUND HANDOFF
IS A REAL AND LARGE CAUSAL IMPROVEMENT.

However the preregistered scientific verdict remains negative.

The backlog reduction reaches 28.23%,
not the frozen 30%.

Final-window throughput reaches 78.125%,
not the frozen 85%.

Do not round either threshold into a pass.

Do not alter the frozen criteria after seeing the result.

RESIDUAL QUESTION

With legacy handoff debt almost eliminated,
the remaining Phase-4 deficit now belongs primarily
to service of the new relocated workload
or to the measurement window itself.

REQUEST_BOUND Phase-4 new arrivals:
64.

New Phase-4 correct DONE by horizon:
20.

But late Phase-4 arrivals are horizon-censored by
the mandatory multi-stage pipeline.

The minimum success path still requires:

SENSE;
PROCESS;
six ROUTE hops;
VERIFY.

That is at least nine task operations
even without contention or repair.

Therefore the next step must be
observation-only diagnosis before another mechanism.

Measure:

new Phase-4 completion
by request creation epoch;

matured-cohort completion
for requests with sufficient horizon;

stage occupancy at t=159;

request ages at t=159;

per-stage service matches
during the final 16 epochs;

local stream-commitment availability
around the new anchors and packet positions;

whether the remaining 78.125% threshold miss
is caused by actual spatial service deficit
or by finite-horizon censoring.

Do not reinterpret TASK1E as qualified
if the metric itself is found to be poorly aligned.

Any measurement correction
must be preregistered prospectively
and tested on a fresh frozen experiment.

PLAIN-SPEAK INTERPRETATION

The handoff fix worked.

Almost every old job
finished through the door it started with.

That removed the giant traffic jam
created by moving old jobs' destinations
while they were already in flight.

The organism then recovered immediately
when the workplace moved
and handled far more work.

But we set two bars in advance,
and it missed both by a little.

So this is not a qualification pass.

It is a strong causal result
with a smaller remaining problem.

Now that the old-job artifact is gone,
we can finally measure whether
the remaining gap belongs to the organism
or to how the end of the experiment
counts jobs that did not have enough time to finish.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
