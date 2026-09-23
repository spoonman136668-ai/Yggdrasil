TITLE: TASK-1 T1F1 PRIMARY CLOSURE
DATE: 2026-09-22
STATUS: CLOSED / PARTIAL POSITIVE / ANCHOR-RELOCATION FAILURE
TRACK: DG-1 / TASK-1

T1F1:
22b6ab5a036732cc9efbda077069e971c34a337e

MANIFEST-BINDING COMMIT:
2db282ba78ac51f882e87f29daec491bb8d510ff

PRIMARY MANIFEST SHA256:
ef76ca548a1c9754eb2779812d7c14cbe66788821198b5d7c6ebc291360f2d86

DUPLICATE PRIMARY GATE

runs:
2

raw output bytes:
36963 each

raw output SHA256:
d9d2767a8ff9368fd3d5f6e2529a4c0fef07344c9dfcf941c1c4abff6cd2cdeb

byte identical:
true

external duplicate-primary gate:
PASS

all integrity probes:
PASS

SCIENTIFIC STATUS

TASK1_EMERGENT_ORGANIZATION_GAIN:
FALSE

TASK1_REPAIR_GAIN:
TRUE

TASK1_QUALIFIED:
FALSE

EMERGENT ORGANIZATION CHECKS

PASS:
Phase-0 EMERGENT_V0 >=95% of FIXED_ROLE.

PASS:
Phases 1-4 completion area >=10% above FIXED_ROLE.

PASS:
Demand-reversal recovery within 8 epochs.

PASS:
Lesion recovery / backlog criterion.

FAIL:
Phase-4 final-16 correct-completion rate >=85%.

Observed:
43.75%.

PASS:
Phase-0 to Phase-4 dominant-operation change >=25%.

Observed:
100%.

PASS:
at least three operation classes represented by >=4 cells
in both required organization windows.

PASS:
incorrect DONE = 0.

PASS:
operation cost <=125% of FIXED_ROLE.

PASS:
integrity.

REPAIR RESULT

TASK1_REPAIR_GAIN:
TRUE.

Scheduled corruptions:
19.

EMERGENT_V0 corruption applied:
17.

Corruptions reaching egress:
14.

Verification detected:
14.

Detection fraction:
100%.

Successfully repaired / correctly completed after repair:
14 / 14.

Repair success fraction:
100%.

Correct completion among scheduled-corrupt requests:
73.6842%.

EMERGENT_NO_REPAIR:
0%.

Incorrect DONE:
0.

Median noncorrupt latency:
EMERGENT_V0 = 15 epochs.
EMERGENT_NO_REPAIR = 14 epochs.

The repair path therefore meets every frozen causal-repair criterion.

EMERGENT_V0 OVERALL

Correct DONE:
188 / 320.

Full correct-completion fraction:
58.75%.

Expired:
89.

Final unfinished backlog:
43.

Incorrect DONE:
0.

Operations per correct completion:
11.8883.

FIXED_ROLE OVERALL

Correct DONE:
46 / 320.

Full correct-completion fraction:
14.375%.

Expired:
210.

Final unfinished backlog:
64.

Incorrect DONE:
0.

Operations per correct completion:
40.4783.

PERTURBATION RESULT

Demand reversal recovery latency:
0 epochs.

Lesion recovery latency:
3 epochs.

Anchor-rotation recovery latency:
NOT ATTAINED.

Phase-0 final-16 throughput:
78.125%.

Phase-4 final-16 correct-completion rate:
43.75%.

Correct-completion area over Phases 1-4:
EMERGENT_V0 = 153.
FIXED_ROLE = 23.

FUNCTIONAL REORGANIZATION

Dominant-operation change after demand reversal:
50.0%.

After lesion:
30.77%.

After anchor rotation:
100%.

Phase-0 to Phase-4:
100%.

Thus the Phase-4 failure is not caused by cells refusing to change
functional operation.

The population reorganizes strongly,
but the relocated service pipeline does not recover enough throughput.

CAUSAL CLASSIFICATION

Per the preregistered failure-attribution rule:

Phase 0 is strong.

Demand reversal succeeds.

Lesion recovery succeeds.

Anchor rotation fails.

Therefore the current evidence supports:

FUNCTIONAL ALLOCATION IS ADAPTABLE,
BUT SPATIAL ORGANIZATION IS TOO POSITION-BOUND.

Do not tune V0.

Do not add dynamic topology inside Task-1.

Do not alter anchor rotation, phase length, task radius,
arrival load, expiry, D family, G5 status, or qualification thresholds
after observing this result.

NEXT JUSTIFIED STEP

Run an observation-only replay on the exact frozen T1F1 primary
to localize the Phase-4 throughput bottleneck among:

SENSE availability near relocated ingress;

PROCESS availability after sensing;

ROUTE handoff continuity;

VERIFY availability at relocated egress;

REPAIR availability;

commitment-state availability near the moved anchors;

or backlog inherited into the relocated pipeline.

No Task-1 dynamics may change in that diagnostic.

PLAIN-SPEAK INTERPRETATION

The cells learned to change jobs.

They handled the demand reversal.

They recovered from the distributed lesion.

Their verify-and-repair loop worked perfectly on every corrupted job
that reached verification.

They also beat the permanently assigned controller by a very large margin.

But when the physical places where work entered and exited moved,
the organism changed what its cells were doing without moving enough
useful service capacity into the right places quickly enough.

So this is not a failure of flexible roles.

It is a failure of spatial redeployment.

That is a much narrower and more useful result.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
