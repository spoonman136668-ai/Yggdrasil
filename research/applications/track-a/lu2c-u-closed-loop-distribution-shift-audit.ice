TITLE: LU-2C — CLOSED-LOOP U-RECRUITMENT DISTRIBUTION-SHIFT AUDIT
DATE: 2026-09-23
STATUS: PREREGISTERED / NO DIAGNOSTIC WORLD EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Determine whether the LU-1E U-recruitment head
experiences a measurable closed-loop distribution shift:

does teacher-vs-learned U probability error
increase on U-cell observations generated
by the HYBRID_HU organism's own trajectory
relative to U-cell observations generated
by the TEACHER_V02 trajectory?

This is observation-only.

No training.

No weight change.

No authority change.

PARENTS

LU2AF1-R1:
ba771ec410b5a35498e0b146e71781ac4df4285c

LU-2A qualified closure:
dc235c5a6712c199803cc51d066b16378f10d438

LU-2B non-confirmation closure:
b2382bf65dbd239b1b53721f63c01d8c01dca9b6

LU-2B replicate-3 diagnosis:
c6cee6c747e17e3a45a906ed76d767afe3ec1074

CANONICAL LEARNED WEIGHTS

SHA256:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

No retraining.

No optimizer.

No online adaptation.

No alternate checkpoint.

SCIENTIFIC QUESTION

For the same frozen LU-1E U head,
compare teacher-vs-learned U TV distance
on two naturally generated closed-loop observation distributions:

A.
TEACHER_TRAJECTORY_U

B.
HYBRID_TRAJECTORY_U

The learned model is evaluated observationally
on every focal U decision opportunity in both arms.

Only HYBRID_HU uses learned U probabilities to choose transitions.

TEACHER_V02 continues to use exact V0.2 U recruitment probabilities.

MODEL AUTHORITY

Exactly inherited LU-2A/LU-2B.

TEACHER_V02:
exact V0.2.

HYBRID_HU:
learned H release;
learned U recruitment;
exact V0.2 C/S stay-defect;
exact hard lifecycle.

No authority change.

OBSERVATION INSTRUMENTATION

At every focal U evaluation in both arms record:

world replicate;

epoch;

phase;

cell index;

teacher [C,S,H,U] probability;

learned [C,S,H,U] probability;

TV distance;

local state observation hash.

The additional learned forward pass
in TEACHER_V02 is observation-only.

It must not:

consume RNG;

change a transition probability;

change an outcome;

change model state;

change cell state;

change request state;

or alter telemetry used by the scientific parent.

FRESH DIAGNOSTIC WORLDS

Exactly 10 paired worlds.

Derive only after the LU-2C preregistration commit exists.

Namespace:

LU2C-U-SHIFT|LU2AF1-R1|replicate

for replicate 1..10.

No LU-2A or LU-2B world reuse.

No result-dependent selection.

No rejection sampling.

No world replacement.

Bind all 10 complete manifest identities
before any diagnostic arm executes.

COMMON RANDOMNESS

Retain exact parent common-random discipline.

The two arms use identical world manifests
and identical pre-bound random variates.

The TEACHER arm's additional learned inference
may not introduce RNG.

MECHANICAL GATE BEFORE DIAGNOSTIC EXECUTION

Prove:

1.
parent source identity exact;

2.
canonical learned weight SHA exact;

3.
teacher arm transition trace is byte-identical
with instrumentation OFF vs ON
on a mechanical fixture;

4.
hybrid arm transition trace is byte-identical
with instrumentation OFF vs ON;

5.
instrumentation adds no RNG draw;

6.
instrumentation changes no parent transition probability;

7.
instrumentation changes no parent transition outcome;

8.
every logged TV is finite and in [0,1];

9.
phase classification is deterministic from epoch only;

10.
duplicate instrumented mechanical evidence byte-identical.

DIAGNOSTIC METRICS

For every world and each arm report:

U evaluation count;

mean U TV;

median U TV;

p90 U TV;

p95 U TV;

p99 U TV;

maximum U TV.

Also report separately by phase:

0;

1;

2;

3;

4.

For each world compute:

overall mean-TV ratio =
HYBRID_TRAJECTORY_U mean TV
/
TEACHER_TRAJECTORY_U mean TV.

Phase-4 mean-TV ratio =
HYBRID phase-4 mean TV
/
TEACHER phase-4 mean TV.

If denominator is zero,
report ratio as undefined
and do not count that world for ratio criteria.

DISTRIBUTION-SHIFT CRITERION

LU2C_U_CLOSED_LOOP_SHIFT_SUPPORTED = TRUE iff:

all integrity/mechanical probes pass;

at least 8 of 10 worlds have defined overall ratios;

at least 8 of 10 worlds have defined phase-4 ratios;

and either:

OVERALL SHIFT:

HYBRID mean U TV > TEACHER mean U TV
in at least 7 of 10 worlds

AND

median defined overall mean-TV ratio >=1.10;

OR

PHASE-4 SHIFT:

HYBRID phase-4 mean U TV > TEACHER phase-4 mean U TV
in at least 7 of 10 worlds

AND

median defined phase-4 mean-TV ratio >=1.15.

PATH-DEPENDENCE INTERPRETATION

LU2C_PATH_DEPENDENCE_WITHOUT_TV_SHIFT_SUPPORTED = TRUE iff:

LU2C_U_CLOSED_LOOP_SHIFT_SUPPORTED = FALSE;

all integrity probes pass;

learned U decisions still produce
at least one realized transition difference
across the 10-world HYBRID suite;

and the HYBRID and TEACHER state trajectories
diverge in at least 7 of 10 worlds.

This outcome means
small approximation differences are being amplified
by developmental path dependence
without a strong increase in per-decision U approximation error.

INTERPRETATION

IF U CLOSED-LOOP SHIFT SUPPORTED

The next justified learning experiment may target
U-recruitment distribution coverage.

Do not train on LU-2B replicate 3 alone.

Use a separately preregistered fresh teacher/hybrid state collection
with disjoint training/validation/test worlds.

Do not change H or C/S authority during that experiment.

IF PATH DEPENDENCE WITHOUT TV SHIFT SUPPORTED

Do not assume more U imitation training will fix the problem.

The evidence would favor a narrower authority boundary,
confidence-gated learned U authority,
or another mechanism for limiting trajectory amplification.

Any such authority mechanism requires a new preregistration.

IF NEITHER

The present evidence is insufficient
to distinguish distribution shift
from developmental amplification.

Do not tune.

Design a stronger diagnostic before changing the model.

NO POST-RESULT TUNING

Do not alter:

world count;

namespace;

weights;

parent dynamics;

learned authority;

TV metric;

phase boundaries;

shift thresholds;

or interpretation rules
after diagnostic execution begins.

PLAIN-SPEAK QUESTION

The neural recruitment head looks reasonably close
to the hand-written rule one decision at a time.

But its decisions change the organism.

That means later cells may see
a different kind of world
than the model saw on the hand-written trajectory.

LU-2C asks:

does the neural recruitment model
actually become less accurate
on the worlds its own earlier decisions create?

If yes,
we have a normal closed-loop distribution-shift problem.

If no,
then even small errors are being magnified
by the developmental system's path dependence,
and simply training the same predictor harder
may not solve the real issue.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
