TITLE: TASK-1B T1BF1 PRIMARY CLOSURE
DATE: 2026-09-22
STATUS: CLOSED NEGATIVE / MECHANISM ACTIVE / PARTIAL INGRESS IMPROVEMENT
TRACK: DG-1 / TASK-1B

T1BF1:
83af31c2a95adeba47700f7c34d159d7739549c9

MANIFEST BINDING:
e75e1c088db8016aa39c34e15ab6b470966cb736

MECHANICAL EVIDENCE CORRECTION:
1284dffd95b840a9f637f31d970b3721552703da

PRIMARY MANIFEST SHA256:
0a88b7f42c283c09c74925744157e9cd5279afd4a6c02e1b9a866da5016b9d71

AUTHORITATIVE DUPLICATE PRIMARY

runs:
2

bytes:
36851 each

SHA256:
f2310efeb7e8a09c931b1666f90c25347aa1a5597115354a7b1bd413746ded8b

byte identical:
true

all integrity probes:
PASS

SCIENTIFIC STATUS

TASK1B_INGRESS_BOOTSTRAP_GAIN:
FALSE

MECHANISM ACTIVE:
TRUE

Opposite-stream committed cells performing SENSE:
23.

Therefore the causal treatment was genuinely exercised.

MATCHED_SENSE

overall correct completion:
68.4375%

correct DONE:
219 / 320

expired:
52

final backlog:
49

operations per correct completion:
11.0183

Phase-4 final-16 correct completion:
34.375%

anchor-rotation recovery:
NOT ATTAINED

final-16 RAW backlog area:
773

NEUTRAL_SENSE

overall correct completion:
72.1875%

correct DONE:
231 / 320

expired:
42

final backlog:
47

operations per correct completion:
10.9610

Phase-4 final-16 correct completion:
40.625%

anchor-rotation recovery:
NOT ATTAINED

final-16 RAW backlog area:
585

Change versus MATCHED_SENSE:

overall completion:
+3.75 percentage points

Phase-4 final-16:
+6.25 percentage points

RAW backlog area:
-188
(-24.32%)

This is a real directional improvement,
but it does not reach the preregistered effect size.

QUALIFICATION FAILURES

Phase-4 final-16 >=85%:
FAIL

Phase-4 improvement >=20 percentage points:
FAIL

anchor-rotation recovery <=8 epochs:
FAIL

final-16 RAW backlog area reduction >=40%:
FAIL

All other primary checks pass,
including:

mechanism activity;

Phase-0 non-regression;

zero-eligible ingress criterion;

demand-reversal recovery;

lesion recovery;

incorrect DONE = 0;

operation-cost boundary;

repair detection;

repair success;

integrity.

REPAIR / SAFETY

NEUTRAL_SENSE:

scheduled corruptions:
20

corruptions reaching egress:
17

detected:
17 / 17

repaired and correctly completed:
17 / 17

repair success:
100%

incorrect DONE:
0

median noncorrupt latency:
14.5 epochs

Thus the treatment does not gain throughput by weakening verification.

CAUSAL INTERPRETATION

The Task-1 post-closure diagnosis was partly correct.

Requiring matching stream commitment before SENSE
does contribute to relocation brittleness.

Removing that requirement:

admits more relocated work;
reduces expiry;
reduces RAW backlog;
improves repair exposure;
improves overall completion.

But the gain is too small.

Therefore the dominant remaining failure lies downstream
of environmental transduction.

The organism can now see more relocated work,
but stream-specific execution after SENSE remains position-bound.

Do not broaden SENSE again.

Do not change V0.

Do not add dynamic topology.

NEXT JUSTIFIED STEP

Run an observation-only Task-1B replay
to measure stage composition and eligibility through Phase 4.

Specifically distinguish:

SENSED waiting for PROCESS;

PROCESSED / ROUTING waiting for stream-matched transport;

AT_EGRESS waiting for VERIFY;

REPAIR_PENDING;

and the local C/S commitment distribution around each packet stage.

The next causal experiment must target the first downstream stage
that accumulates after neutral sensing.

PLAIN-SPEAK INTERPRETATION

Letting the wrong-side cell pick a job up at the new door helped.

It helped enough to prove that the front-door rule was part of the problem.

But it did not solve relocation.

The jobs are getting farther into the organism,
then getting stuck somewhere after pickup.

So we should not make sensing even looser.

We should find the next exact choke point.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
