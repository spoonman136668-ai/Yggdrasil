TITLE: TASK-1G T1GF1 PRIMARY CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / EDF ACTIVE BUT NO REPAIR-SERVICE INFORMATION GAIN / BENCHMARK LIFETIME BOUNDARY IDENTIFIED
TRACK: DG-1 / TASK-1G

T1GF1:
ec41d76f5e80005e6b65db651753b04ec3f9d8cf

FIVE-MANIFEST BINDING:
b7519d905f07d6b91551c1b44636d284ebd8f376

PREREGISTRATION:
2b1988f0d891d1e24de28ad32b8a32a3d6c0e29a

FROZEN SOURCE SHA256:
dc46ac0cc462f5f3ff93c56c28db4ed7da92ce67654d1633b4d3014e9ae01197

DUPLICATE PRIMARY SWEEPS

runs:
2

replicates per sweep:
5

raw bytes per sweep:
186837

raw SHA256:
1b27f8f1fa747ed612eac14b8f87efa58268e2c080d8e12e94a47e777658ccc9

byte identical:
true

external open output bytes:
189333

external open output SHA256:
617f21ef92479ae5f223302a955ab31f98ef6e9ed166d2270577805d962195d5

all integrity probes:
PASS

SCIENTIFIC STATUS

TASK1G_REPAIR_SERVICE_INFORMATION_GAIN:
FALSE

TASK1G_QUALIFIED:
FALSE

INFORMATION-GAIN CHECKS

mechanism active in at least 3/5:
PASS.
Observed:
5/5.

repair-detection nonregression:
PASS.

repair-success nonregression:
PASS.

expiry-after-correct-repair strictly lower:
FAIL.

Parent total:
1.

EDF treatment total:
1.

Phase-0 nonregression:
PASS.

Phase-4 no worse than -5 percentage points:
PASS.

incorrect DONE zero / integrity:
PASS.

operation cost within 125%:
PASS.

MECHANISM ACTIVITY

The EDF rule was not inert.

Repair-critical local proposal preemptions:

R1:
7.

R2:
2.

R3:
7.

R4:
14.

R5:
10.

Repair-critical matches:

R1:
17.

R2:
28.

R3:
26.

R4:
44.

R5:
33.

Thus the treatment actively changed
local proposal ordering
in all five fresh manifests.

PAIRED REPAIR RESULTS

R1

Parent repair detection:
100%.

EDF:
100%.

Parent repair success:
88.889%.

EDF:
88.889%.

Correctly repaired requests expiring before reverify:

Parent:
1.

EDF:
1.

R2

Parent repair success:
100%.

EDF:
100%.

Expiry-after-correct-repair:
0 / 0.

R3

Parent repair detection:
100%.

EDF:
100%.

Parent repair success:
86.667%.

EDF:
86.667%.

Expiry-after-correct-repair:
0 / 0.

R4

Parent repair detection:
95.652%.

EDF:
95.652%.

Parent repair success:
100%.

EDF:
100%.

Expiry-after-correct-repair:
0 / 0.

R5

Parent repair detection:
100%.

EDF:
100%.

Parent repair success:
94.118%.

EDF:
94.118%.

Expiry-after-correct-repair:
0 / 0.

PHASE-4 RESULT

The frozen final-window completion metric
is paired-identical in every replicate:

R1:
112.5% / 112.5%.

R2:
121.875% / 121.875%.

R3:
128.125% / 128.125%.

R4:
134.375% / 134.375%.

R5:
115.625% / 115.625%.

Median EDF final-window completion:
121.875%.

Thus repair-critical EDF
does not improve or materially regress
the already-strong LOCAL_HEDGE spatial organization.

POST-CLOSURE OBSERVATION-ONLY FAILURE LOCALIZATION

No dynamics were changed for this audit.

R1 request 239

stream:
S.

created:
119.

SENSE:
139.

PROCESS:
140.

route begins:
141.

reaches egress:
148.

corruption detected:
149.

repair:
150.

expiry:
151.

The repaired output is correct.

Five locally eligible S-stream
VERIFY / REPAIR cells are available
at epochs 149 and 150.

Therefore local repair eligibility
is not the blocker.

The post-detection sequence is already
as fast as the one-operation-per-request rule permits:

detect;
repair;
then mandatory reverify.

There is no remaining epoch
for reverify before expiry.

R3 requests 120 and 121

both created:
60.

first SENSE:
81 / 82.

both reach egress:
90.

both corruption detections:
91.

expiry:
92.

Five locally eligible C-stream
VERIFY cells exist at detection.

Both requests therefore reach detection
with only one epoch of lifetime remaining.

They expire before repair can complete.

R5 request 281

created:
140.

SENSE:
145.

PROCESS:
151.

reaches egress:
157.

corruption detected:
158.

repair:
159.

Five eligible S-stream cells
exist at both critical stages.

The repaired output is correct.

The 160-epoch experiment ends
before epoch 160 re-verification can occur.

This is finite-horizon censoring,
not an expiry failure.

CAUSAL INTERPRETATION

Task-1G falsifies the hypothesis
that the remaining formal repair miss
is caused by ordinary local request ordering
after corruption has been detected.

Deadline priority is active,
but it cannot recover time
that was already consumed
before the request entered
the detected repair critical path.

The failing requests spend most
of their lifetime upstream.

Once they reach VERIFY / REPAIR,
local executor availability is adequate
and the critical operations happen immediately
or at the earliest permitted epoch.

Therefore the remaining qualification failures
are not evidence for:

another LOCAL_HEDGE defect;

a repair-computation defect;

a verification-computation defect;

insufficient local repair eligibility;

or lack of deadline urgency
inside the detected repair path.

They expose a benchmark service-envelope boundary:

the frozen 32-epoch request lifetime
must cover:

queue admission;

SENSE;

PROCESS;

six ROUTE hops;

initial VERIFY;

and, for corrupted work,
REPAIR plus mandatory re-VERIFY.

Under loaded local queues,
some requests arrive at first verification
too near expiry
for the two extra corruption-recovery steps.

The final experimental horizon
also censors a correctly repaired late request.

IMPORTANT BOUNDARY

Do not change the Task-1G expiry
or qualification thresholds post-result.

Do not reinterpret Task-1G as qualified.

Do not add another repair-priority knob.

Do not weaken mandatory re-verification.

Do not reroll the five manifests.

TASK-1F INTERPRETATION REMAINS

The robust Task-1F result remains intact:

LOCAL_HEDGE produced positive Phase-4 information gain
in 5/5 fresh manifests;

median Phase-4 gain:
+31.25 percentage points;

backlog reduction:
5/5;

new relocated S completion gain:
5/5;

Phase-0 preserved;

safety preserved;

operation cost bounded.

Task-1G does not weaken that causal result.

It shows that the remaining formal qualification miss
is orthogonal to LOCAL_HEDGE
and lies in the Task-1 benchmark lifecycle envelope.

NEXT JUSTIFIED STEP

Do not launch another substrate mechanism
to chase this benchmark artifact.

First perform a frozen,
observation-only Task-1 service-envelope analysis
using the existing five Task-1G manifests.

Quantify:

minimum operation-path length
for clean versus corrupted requests;

queue-wait distributions
before each pipeline stage;

age at first VERIFY;

remaining lifetime at first VERIFY;

fraction of requests for which
successful corruption recovery
is mathematically impossible
once first detection occurs;

finite-horizon censoring
of late arrivals;

and whether the 32-epoch expiry
provides a feasible recovery SLA
at the frozen offered load.

This analysis may inform
a future Task-2 / benchmark contract.

It may not retroactively change
Task-1F or Task-1G qualification.

PLAIN-SPEAK INTERPRETATION

Giving urgent repaired jobs priority
did not solve the failures.

The reason is simple:

by the time those jobs were known to be broken,
they were already too old.

The cells fixed them as fast as the rules allowed.

There were enough local cells available.

But the job had spent so much time
waiting earlier in the pipeline
that there was no time left
for:

detect the error;
fix it;
check the fix.

One late job had a different problem:

it was fixed on the final epoch,
so the experiment stopped
before the last check.

That means we have reached
a benchmark boundary,
not another organism defect.

The local uncertainty change from Task-1F
is still a strong five-world positive result.

We should now measure whether
the Task-1 deadline itself
is compatible with the work
we ask each request to perform,
rather than inventing another cellular knob.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
