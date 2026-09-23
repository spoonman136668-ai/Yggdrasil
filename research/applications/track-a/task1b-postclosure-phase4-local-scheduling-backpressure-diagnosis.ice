TITLE: TASK-1B POST-CLOSURE PHASE-4 LOCAL SCHEDULING / BACKPRESSURE DIAGNOSIS
DATE: 2026-09-22
STATUS: OBSERVATION-ONLY / FROZEN-T1BF1 REPLAY
TRACK: DG-1 / TASK-1B
PARENT CLOSURE: b6cc257acbbd839ef6d831e4ed6afd1abd34d482

PURPOSE

Localize the remaining Phase-4 relocation failure after
commitment-neutral ingress sensing proved active but insufficient.

SOURCE / MANIFEST

T1BF1:
83af31c2a95adeba47700f7c34d159d7739549c9

source SHA256:
e8d409c5eb8e750123aae4979fd1091611a915c22f7cf977e420345186aef6b9

primary manifest SHA256:
0a88b7f42c283c09c74925744157e9cd5279afd4a6c02e1b9a866da5016b9d71

The replay uses the exact frozen NEUTRAL_SENSE primary dynamics.
Instrumentation observes stage composition, local eligibility, matching,
and request age immediately before local matching.

No dynamics, matching rule, task randomness, corruption, lesion,
anchors, phase lengths, or qualification are changed.

CENTRAL FINDING

After neutral sensing, the dominant relocation bottleneck is no longer
simple ingress eligibility.

It is local scheduling / pipeline backpressure.

The frozen matcher chooses the oldest eligible local request
without stage balancing.

During Phase 4, older downstream packets monopolize the same local
stream-matched cells that could admit new RAW work.

PHASE-4 FINAL 16 EPOCHS — C STREAM

SENSE:
mean RAW demand = 17.5625
mean RAW demand with eligible cell = 12.3125
mean matches = 0.5625

PROCESS:
mean demand = 0.8125
mean eligible = 0.8125
mean matches = 0.625

ROUTE:
mean demand = 6.125
mean eligible = 6.125
mean matches = 5.5

VERIFY:
mean demand approximately 0.4375
eligible approximately all
matches approximately all

Mean stage occupancy:
RAW = 17.5625
SENSED = 0.8125
ROUTING = 5.4375

PHASE-4 FINAL 16 EPOCHS — S STREAM

SENSE:
mean RAW demand = 19.0
mean RAW demand with eligible cell = 11.5
mean matches = 0.0

PROCESS:
mean demand = 5.3125
mean eligible = 5.3125
mean matches = 0.5

ROUTE:
mean demand = 4.8125
mean eligible = 4.8125
mean matches = 3.0

VERIFY:
mean demand approximately 0.4375
eligible approximately all
matches approximately all

Mean stage occupancy:
RAW = 19.0
SENSED = 5.3125
PROCESSED = 0.6875
ROUTING = 4.125

Correct-stream committed cells near SENSED S packets:
mean approximately 1.529.

Correct-stream committed cells near ROUTING S packets:
mean approximately 1.621.

Therefore the final-window S ingress often has eligible sensing capacity,
yet receives zero SENSE matches.

REQUEST AGE — FINAL 16 EPOCHS

C stream:

RAW mean age:
11.65

SENSED:
12.46

PROCESSED:
13.55

ROUTING:
20.70

AT_EGRESS:
19.86

Matched SENSE requests:
n = 9
mean age = 12.33

Matched PROCESS:
n = 10
mean age = 13.20

Matched ROUTE:
n = 88
mean age = 20.68

Matched VERIFY:
n = 7
mean age = 19.86

S stream:

RAW mean age:
14.13

SENSED:
12.41

PROCESSED:
15.91

ROUTING:
19.23

AT_EGRESS:
21.71

REPAIR_PENDING:
20.0

Matched SENSE:
n = 0

Matched PROCESS:
n = 8
mean age = 16.25

Matched ROUTE:
n = 48
mean age = 19.06

Matched VERIFY:
n = 7
mean age = 21.71

Matched REPAIR:
n = 1
age = 20

CAUSAL INTERPRETATION

The frozen oldest-request-first rule is locally rational
for latency and expiry avoidance.

But after spatial relocation it creates a pipeline capture effect.

Long-lived ROUTING / AT_EGRESS packets are older than the new RAW jobs.

They repeatedly win local contention.

The system therefore spends scarce stream-matched capacity
finishing old spatial commitments while under-serving
the newly relocated ingress.

This explains why Task-1B can:

increase sensing eligibility;
perform real opposite-stream SENSE;
reduce RAW backlog directionally;

yet still fail to restore relocation throughput.

The remaining issue is not:

lack of task visibility;

lack of local eligible cells in general;

broken routing;

missing verification;

or permanent role assignment.

It is:

LOCAL PIPELINE SERVICE FAIRNESS
UNDER A MOVED DEMAND FRONT.

NEXT JUSTIFIED CAUSAL QUESTION

Does a purely local stage-fair matching rule
remove relocation starvation without:

a global queue;
a central scheduler;
permanent roles;
dynamic topology;
V0 changes;
or weakened downstream correctness?

The next experiment must change only local task-operation selection.

It must preserve:

T1BF1 neutral-sense eligibility;
V0;
D2;
G5 OFF;
R_TASK;
request lifecycle;
route semantics;
repair;
expiry;
arrival load;
anchor rotation;
and hard one-operation-per-cell/per-request budgets.

No post-result scheduling parameter sweep is justified.

PLAIN-SPEAK INTERPRETATION

The front door is no longer locked.

There are cells that could pick up the new S jobs.

But they keep choosing older jobs that are already deeper inside
the pipeline.

That makes sense locally:
the older jobs are closer to expiring.

But after the entrance moves,
the organism gets trapped paying off old work
while new work piles up outside.

So the next question is not:

"can more cells sense?"

It is:

"can a cell share its attention fairly
between finishing old work
and admitting new work?"

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
