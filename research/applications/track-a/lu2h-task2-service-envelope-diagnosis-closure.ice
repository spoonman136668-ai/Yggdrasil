TITLE: LU-2H TASK-2 EXACT-PARENT SERVICE-ENVELOPE DIAGNOSIS CLOSURE
DATE: 2026-09-24
STATUS: CLOSED / PRE-SENSE CONGESTION + EXPIRY + RECOVERY-TARGET + HORIZON MISMATCH IDENTIFIED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
d9f0da965a3a94453a95e9a17de9961d45c9033f

FROZEN AUDIT:
bac323e1a00b31f80e555339846d55141609ce10

INSTRUMENTATION FIX:
31a52389c16a8f22161144efd603ac5f590a6de3

CORRECTED EXECUTION HEAD:
759eb08ac365b30c166e3e30ab4aec8c2118d098

GITHUB ACTIONS RUN:
36048974466

SOURCE SHA256:
67a68718d3a74c300e769f4e7ab1c1a35923ade5d943e209dbb0ac6567b078be

OBSERVATION BOUNDARY

Exact ten bound LU-2G manifests only.
U_A0 exact parent only.
Observation-only.
No new world.
No dynamics change.
No scheduler change.
No expiry change.
No load change.
No corruption change.
No recovery-threshold change.
No learned-model change.

DUPLICATE AUDIT EVIDENCE

complete executions:
2

bytes each:
1918637

SHA256 both:
f415d596cc0683510972c3bba3faced4cb35618ce3588ba728ec058f62a4501c

byte-identical:
TRUE

DIAGNOSTIC CLASSIFICATION

PRE_SENSE_CONGESTION:
SUPPORTED

TWO_PROCESS_STAGE_SERVICE_COST:
NOT IDENTIFIED AS DOMINANT POST-ADMISSION BOTTLENECK

ROUTE_OR_VERIFY_CONGESTION:
NOT IDENTIFIED AS DOMINANT

EXPIRY_ENVELOPE_MISMATCH:
SUPPORTED

RECOVERY_TARGET_MISMATCH:
SUPPORTED

FINITE_HORIZON_CENSORING:
SUPPORTED

UNRESOLVED:
FALSE

STRUCTURAL TASK-2 PATH

clean operations:
10

corrupted operations through mandatory reverify:
12

inherited expiry:
32 epochs

VERIFIED -> DONE uses a separate epoch:
TRUE

AGGREGATE PIPELINE WAITS

PRE-SENSE

count:
4302

mean:
21.1452812645 epochs

median:
26

p90:
30

maximum:
31

SENSE -> PROCESS_A extra wait

count:
4212

mean:
0.5581671415

median:
0

p90:
0

maximum:
20

PROCESS_A -> PROCESS_B extra wait

count:
3697

mean:
0.0294833649

median:
0

p90:
0

maximum:
4

PROCESS_B -> first ROUTE extra wait

count:
2798

mean:
0.0214438885

median:
0

p90:
0

maximum:
4

between ROUTE hops extra wait

count:
10892

mean:
0.0065185457

median:
0

p90:
0

maximum:
4

last ROUTE -> first VERIFY extra wait

count:
1557

mean:
0.0128452152

median:
0

p90:
0

maximum:
3

Therefore the dominant queueing delay is before SENSE.

Once a request is admitted into the service pipeline,
the two PROCESS stages, routing, and verification are usually serviced
without additional queueing delay.

DEADLINE / HORIZON ACCOUNTING ACROSS TEN WORLDS

corrupt requests reaching egress with no epoch available for initial VERIFY:
6

detected corruptions with no epoch available for REPAIR:
2

repaired requests expiring before mandatory re-VERIFY:
14

repair/verified paths censored by finite experiment horizon:
16

These counts establish that the inherited 32-epoch lifetime and the
160-epoch observation horizon are materially interacting with the longer
Task-2 service path after substantial upstream admission delay.

RECOVERY DIAGNOSIS

event windows evaluated:
30

frozen recovery target reached:
0 / 30

unreached:
30 / 30

This includes the demand reversal, lesion onset, and anchor rotation windows.

The exact parent therefore does not demonstrate that the frozen Task-2
recovery target is attainable inside the preregistered +8-epoch windows.

CAUSAL INTERPRETATION

The Task-2 failure is not primarily caused by queueing between the two
PROCESS stages, routing hops, or the VERIFY operation.

The dominant service-budget loss occurs before SENSE.

The median request has already spent 26 of its 32 allowed epochs waiting
before it is sensed.

That leaves only six epochs at the median for a clean ten-operation
Task-2 path, making expiry pressure structural under the offered workload.

Corruption adds two mandatory service operations and therefore exposes this
boundary more strongly.

Separately, the frozen recovery target is not reached in any measured event
window by the exact parent, so it is not a valid discriminator for the
current Task-2 environment.

Finite-horizon censoring is also real and must be accounted for separately
from mechanism failure.

DECISION

Do not modify LU-2G.

Do not reinterpret LU-2G as qualified.

Do not tune the learned U model.

Do not change repair or verification logic.

The next discriminating experiment must test the exact parent only and ask
whether reducing offered Task-2 load while retaining the inherited 32-epoch
expiry removes the pre-SENSE congestion enough to restore baseline
feasibility.

This tests the smallest causal hypothesis exposed by LU-2H:

the nominal PROCESS-load normalization of three two-stage requests per epoch
does not normalize the actual whole-pipeline service demand.

Recovery-target calibration remains observation-only in that experiment;
do not select a target using learned-U performance.

PLAIN-SPEAK INTERPRETATION

We found where the time is going.

It is not getting stuck between the two calculations.
It is not getting stuck routing.
It is not getting stuck at verification.

It is waiting to start.

The typical Task-2 request waits 26 epochs before SENSE,
but the entire request only gets 32 epochs to live.

Once work actually enters the pipeline, almost every later stage moves on
the next available epoch.

That explains why repair sometimes looks incomplete:
the request often arrives at the repair boundary after most of its lifetime
has already been spent in the admission queue.

The recovery score has a second problem.
The hand-written parent hit the frozen target in none of the 30 measured
event windows, so that score cannot currently tell us whether learned
recruitment is good or bad.

The next experiment should therefore leave the organism and neural model
alone and reduce only the offered Task-2 workload for the exact parent.

If that clears the admission queue and restores baseline feasibility,
we have identified an environment-capacity mismatch rather than a
developmental limitation.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
