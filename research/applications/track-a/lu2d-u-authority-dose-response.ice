TITLE: LU-2D — U-RECRUITMENT LEARNED-AUTHORITY DOSE RESPONSE
DATE: 2026-09-23
STATUS: PREREGISTERED / NO DOSE WORLD EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Test whether developmental trajectory amplification
scales with the magnitude of learned U-recruitment authority.

LU-2C showed:

closed-loop U distribution shift:
NOT SUPPORTED;

developmental path dependence without U-TV shift:
SUPPORTED.

Therefore LU-2D does not retrain the U head.

It varies only how much
the frozen learned U probability distribution
is allowed to replace the exact V0.2 teacher distribution.

PARENTS

LU2AF1-R1:
ba771ec410b5a35498e0b146e71781ac4df4285c

LU-2A qualified closure:
dc235c5a6712c199803cc51d066b16378f10d438

LU-2B non-confirmation closure:
b2382bf65dbd239b1b53721f63c01d8c01dca9b6

LU-2B replicate-3 diagnosis:
c6cee6c747e17e3a45a906ed76d767afe3ec1074

LU-2C diagnostic closure:
75c1bb71dd8008eaaddd11de039d8a369ee9f882

CANONICAL LEARNED WEIGHTS

SHA256:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

No retraining.

No alternate checkpoint.

No optimizer.

No online adaptation.

SCIENTIFIC QUESTION

For focal U cells,
define a convex probability blend:

P_alpha =
(1 - alpha) * P_teacher
+
alpha * P_learned

for categories:

C, S, H, U.

Test exactly:

alpha = 0.00
alpha = 0.25
alpha = 0.50
alpha = 1.00

No other alpha is permitted.

ARM DEFINITIONS

U_A0

alpha = 0.

Exact V0.2 U recruitment.

U_A25

alpha = 0.25.

U_A50

alpha = 0.50.

U_A100

alpha = 1.00.

Full learned U recruitment.

ISOLATION OF U AUTHORITY

For all four arms:

H release:
exact V0.2 teacher.

C/S stay-defect:
exact V0.2 teacher.

FC/FS hard lifecycle:
exact V0.2.

Thus the only scientific difference among arms
is U-recruitment probability blend alpha.

This removes learned H as a possible causal contributor.

OBSERVATION / MODEL BOUNDARY

The learned U model receives exactly OBS-V1.

No new input.

No global information.

No phase id.

No request id.

No task id.

No absolute position.

No future information.

No teacher-derived feature is supplied to the learned model.

The teacher distribution is used only externally
to define the authority blend.

NO NEW RNG

Blending introduces no RNG.

All four arms use the exact same
pre-bound U transition random variates.

The same event/category random draws
must be used across all alphas.

COMMON RANDOMNESS

For each world:

same manifest;

same arrivals;

same programs;

same corruption schedule;

same lesion;

same anchors;

same initial state;

same base RNG identity;

same transition random variates.

FRESH WORLDS

Exactly 10 fresh worlds.

Derive only after LU2DF1 exists.

Namespace:

LU2D-U-DOSE|LU2DF1|replicate

for replicate 1..10.

No LU-2A, LU-2B, or LU-2C world reuse.

No rejection sampling.

No world replacement.

No result-dependent selection.

Bind all ten complete manifest identities
before any scientific arm executes.

MECHANICAL GATE BEFORE LU2DF1

Prove:

1.
exact LU2AF1-R1 parent source identity;

2.
canonical learned weight SHA exact;

3.
U_A0 is exact V0.2 / parent U behavior;

4.
all arms use exact teacher H release;

5.
all arms use exact teacher C/S stay-defect;

6.
all arms use exact hard lifecycle;

7.
only U recruitment probability differs by alpha;

8.
P_alpha is exactly convex interpolation
for all four U categories;

9.
alpha values exactly
0, .25, .50, 1;

10.
blended probabilities finite;

11.
each probability in [0,1];

12.
probability sum within 1e-6 of 1;

13.
no new RNG;

14.
same pre-bound U random variates
across arms;

15.
OBS-V1 unchanged;

16.
D2 preserved;

17.
LOCAL_HEDGE preserved;

18.
ECHO_PHASE preserved;

19.
NO_POOL preserved;

20.
G5_FULL OFF;

21.
request-bound handoff preserved;

22.
duplicate mechanical evidence byte-identical.

PRIMARY EXECUTION

For each bound world run:

U_A0;
U_A25;
U_A50;
U_A100.

Run the complete ten-world four-arm sweep twice.

Require raw canonical sweep bytes
to be byte-identical
before scientific evaluation opens.

TELEMETRY

For every nonzero-alpha arm report:

U evaluation count;

mean teacher-vs-learned U TV;

realized U transition differences vs U_A0
under common randomness;

first state-vector divergence epoch vs U_A0;

epochs with state-vector divergence vs U_A0;

whether the state trajectory later reconverges.

FUNCTIONAL TELEMETRY

For every arm/world report inherited Task-1 metrics including:

Phase-0 completion;

phases-1-4 correct-completion area;

Phase-4 final-window completion;

final-16 total backlog;

anchor-rotation recovery latency;

demand-reversal recovery latency;

lesion criterion;

incorrect DONE;

operations per correct completion.

DOSE-RESPONSE METRICS

For each alpha > 0
and each world compute:

state-divergence fraction =
epochs whose cell-state vector differs from U_A0
/
160;

absolute completion-area deviation =
abs(area_alpha - area_A0)
/
max(area_A0,1);

absolute Phase-4 final-window gap =
abs(phase4_alpha - phase4_A0).

Across 10 worlds report the median of each metric
for alpha .25, .50, 1.00.

PATH-AMPLIFICATION DOSE RESPONSE

LU2D_PATH_AMPLIFICATION_DOSE_RESPONSE_SUPPORTED = TRUE iff:

all integrity gates pass;

all three nonzero alpha arms
produce at least one realized U transition difference
across the ten-world suite;

and

median state-divergence fraction satisfies:

median_A25
<=
median_A50
<=
median_A100

with

median_A100
>=
1.25 * median_A25

unless median_A25 = 0,
in which case median_A100 must be >0.

FUNCTIONAL-SENSITIVITY DOSE RESPONSE

LU2D_FUNCTIONAL_SENSITIVITY_DOSE_RESPONSE_SUPPORTED = TRUE iff:

all integrity gates pass;

and both:

median absolute completion-area deviation A100
>
median absolute completion-area deviation A25;

median absolute Phase-4 final-window gap A100
>
median absolute Phase-4 final-window gap A25.

This criterion does not require strict monotonicity at alpha .50.

LOW-DOSE PRESERVATION OBSERVATION

Report whether U_A25 independently satisfies
the exact LU-2A/LU-2B functional-preservation bars
on all ten worlds.

This is observational only.

Even if all ten pass,
LU-2D does not authorize promotion.

A fresh independent confirmation
would still be required.

INTERPRETATION

IF PATH-AMPLIFICATION DOSE RESPONSE SUPPORTED

Then the developmental substrate
amplifies learned U perturbations
in a dose-sensitive manner.

This would justify testing
a bounded learned-U authority mechanism
rather than retraining the same predictor.

IF FUNCTIONAL-SENSITIVITY ALSO SUPPORTED

Then larger learned U authority
also produces larger organism-level functional deviation.

A lower authority dose becomes
a scientifically justified candidate
for independent confirmation.

IF PATH RESPONSE SUPPORTED
BUT FUNCTIONAL RESPONSE NOT SUPPORTED

Then trajectories are dose-sensitive
while Task-1 function is comparatively robust.

Do not infer promotion safety
without independent confirmation.

IF NEITHER

The authority-amplitude hypothesis
is not supported.

Do not tune alpha.

Design a different path-dependence control experiment.

NO POST-RESULT TUNING

After LU2DF1 freeze do not change:

alpha values;

world count;

namespace;

weights;

OBS-V1;

H authority;

C/S authority;

teacher blend law;

task workload;

scheduler;

expiry;

topology;

lesion;

anchor relocation;

common randomness;

dose-response metrics;

or interpretation thresholds.

PLAIN-SPEAK QUESTION

We now know the neural recruiter
is not becoming less accurate
on the world it creates.

The problem is that
small early differences can echo forward
through development.

LU-2D asks a very simple causal question:

if we turn the neural recruiter's authority down,
does the organism's trajectory move less?

At 0 percent,
the hand-written recruiter is fully in charge.

At 25 percent,
the neural probabilities have a small influence.

At 50 percent,
they have equal influence.

At 100 percent,
the neural recruiter is fully in charge.

Everything else is held fixed,
including the random numbers.

If divergence grows as learned authority grows,
we will have direct evidence
that the important control variable
is perturbation magnitude,
not ordinary model accuracy.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
