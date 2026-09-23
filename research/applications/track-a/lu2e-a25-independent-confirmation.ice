TITLE: LU-2E — INDEPENDENT CONFIRMATION OF 25-PERCENT LEARNED U AUTHORITY
DATE: 2026-09-23
STATUS: PREREGISTERED / NO CONFIRMATION WORLD EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Independently confirm the low-dose result observed in LU-2D:

25-percent learned U-recruitment authority
causally changes developmental decisions
while preserving the validated Task-1 functional envelope.

This is confirmation only.

No new alpha.

No tuning.

No retraining.

PARENTS

LU2AF1-R1:
ba771ec410b5a35498e0b146e71781ac4df4285c

LU2DF1:
f6f82f9d6e13818d9bad7ffc19c59fda1a077aa5

LU-2D closure:
db8e40a58b5bdfb553b469ca14a1262b9a262f9a

LU-2C path-dependence closure:
75c1bb71dd8008eaaddd11de039d8a369ee9f882

CANONICAL LEARNED WEIGHTS

SHA256:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

No alternate checkpoint.

No optimizer.

No online adaptation.

AUTHORITY

Exactly two arms.

U_A0

H:
exact V0.2 teacher.

U:
exact V0.2 teacher.

C/S:
exact V0.2 teacher.

FC/FS:
exact V0.2 hard lifecycle.

U_A25

H:
exact V0.2 teacher.

U:
P =
0.75 * P_teacher
+
0.25 * P_learned.

C/S:
exact V0.2 teacher.

FC/FS:
exact V0.2 hard lifecycle.

No other mechanism differs.

COMMON RANDOMNESS

Paired arms use:

the same manifest;

the same arrivals;

the same programs;

the same corruption schedule;

the same lesion;

the same anchors;

the same initial state;

the same base RNG identity;

the same transition random variates.

The probability blend introduces no RNG draw.

FRESH CONFIRMATION WORLDS

Exactly 10.

Derive only after LU2EF1 exists.

Namespace:

LU2E-A25-CONFIRM|LU2EF1|replicate

for replicate 1..10.

Do not reuse LU-2A, LU-2B, LU-2C, or LU-2D worlds.

No rejection sampling.

No replacement world.

No result-dependent selection.

Bind all ten complete manifest identities
before any confirmation arm executes.

IMPLEMENTATION

LU2EF1 is a thin confirmation harness only.

It must delegate transition execution
to exact LU2DF1.

It may change only:

fresh-world namespace;

manifest validation;

arm selection limited to U_A0 and U_A25;

confirmation summarization.

It may not change the dose implementation.

MECHANICAL GATE

Before primary confirmation execution prove:

1.
LU2DF1 source identity exact;

2.
canonical learned weight SHA exact;

3.
U_A0 exact parent parity;

4.
U_A25 alpha exactly 0.25;

5.
H authority exact teacher in both arms;

6.
C/S authority exact teacher in both arms;

7.
hard lifecycle exact teacher;

8.
no new RNG;

9.
common-random U variates retained;

10.
D2 preserved;

11.
LOCAL_HEDGE preserved;

12.
ECHO_PHASE preserved;

13.
NO_POOL preserved;

14.
G5_FULL OFF;

15.
request-bound handoff preserved;

16.
duplicate mechanical evidence byte-identical.

PRIMARY EXECUTION

Run all 10 paired worlds twice.

Require the complete canonical 10-world paired sweep
to be byte-identical between executions
before confirmation qualification opens.

CAUSAL CONFIRMATION

LU2E_A25_CAUSAL = TRUE iff:

U evaluations > 0;

teacher-vs-active U TV >1e-6
for at least one evaluation;

and at least one realized U transition differs
from U_A0 under common randomness.

FUNCTIONAL CONFIRMATION

Use exactly the LU-2A/LU-2B bars.

For every world:

Phase-0 U_A25 completion
>=95% U_A0.

Phase-4 U_A25 final-window completion
>=85% absolute.

Phase-4 U_A25 final-window completion
no more than 10 percentage points below U_A0.

Phases-1-4 completion-area ratio
>=0.90.

Median completion-area ratio
across 10 worlds
>=0.95.

Final-16 U_A25 backlog
<=125% U_A0.

Anchor-rotation recovery
<=8 epochs.

Demand-reversal recovery
<=8 epochs.

Inherited lesion criterion:
PASS.

Incorrect DONE:
0.

Operations per correct completion
<=125% U_A0.

All integrity probes:
PASS.

OVERALL

LU2E_A25_INDEPENDENT_CONFIRMATION = TRUE iff:

duplicate sweep identity passes;

causal confirmation passes;

functional confirmation passes;

all integrity probes pass.

INTERPRETATION

IF TRUE

25-percent learned U authority
is independently confirmed
as a bounded-authority candidate mechanism.

This still does not authorize automatic substrate promotion.

The next mechanistic question becomes:

can the already-qualified learned H-release head
be combined with independently confirmed bounded U authority
without breaking the functional envelope?

That combination requires a separate preregistered experiment.

IF FALSE

Do not promote U_A25.

Do not tune alpha on the failed worlds.

Diagnose the confirmation miss.

NO POST-RESULT TUNING

Do not change:

alpha;

weights;

world count;

namespace;

H authority;

C/S authority;

topology;

task workload;

scheduler;

expiry;

lesion;

anchor relocation;

common randomness;

or preservation bars
after execution begins.

PLAIN-SPEAK QUESTION

The 25-percent neural recruiter
worked on the dose-response worlds.

Now we repeat only that one setting
on ten completely new worlds.

Nothing else changes.

If it again changes real recruitment decisions
while every world stays inside the same functional limits,
then 25-percent learned recruitment
has earned independent confirmation.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
