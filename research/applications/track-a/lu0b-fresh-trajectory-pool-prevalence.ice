TITLE: LU-0B — Fresh-Trajectory Global-Pool Prevalence Audit
DATE: 2026-09-23
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT

LU-0 closure:
074513c64a64318053fcbfcabdc9207202849063.

LU0F1:
67b4c725193c6af707f5d3937d6854006704bfaa.

Developmental Substrate V0.1:
4d3887fba0478bc1ef3bc4bea44f8e08582f5803.

Task-1H strong confirmation:
1b848079ae0d54dd9e7b01c8d004a93b16aeb62d.

QUESTION

LU-0 proved exact strict-local identifiability is false
for valid constructed V0.1 states.

But its frozen materiality gate did not fully pass
because only 2 / 4 constructed local templates
flipped the preferred C/S recruitment side.

How often does the organism-wide pool
actually matter during naturally reached
V0.1 task trajectories?

PURPOSE

Measure the prevalence and magnitude
of the pc/ps dependency
without changing V0.1 dynamics.

LU-0B is observation-only.

It does not:

remove the pool from the running organism;

change LOCAL_HEDGE;

change task scheduling;

train a neural network;

alter V0.1;

or change any Task-1 threshold.

FRESH WORLDS

Freeze the audit implementation as LU0BF1.

Only after LU0BF1 exists,
derive exactly five fresh worlds.

For k = 1..5:

replicate key =
SHA1(
"LU0B-PREVALENCE|"
+
LU0BF1
+
"|"
+
k
).

task seed =
first 32 hex chars of:

SHA256(
"LU0B-PRIMARY-SEED|"
+
LU0BF1
+
"|"
+
k
).

Use the exact inherited Task-1 generators for:

four balanced nonconstant nonaffine programs;

320 arrivals;

5% stateless corruption;

distributed eight-cell lesion;

initial anchors;

+16 Phase-4 anchor rotation.

These worlds must not equal
Task-1F or Task-1H primary manifests.

PRIMARY DYNAMICS

Run exactly:

V0.1 / LOCAL_HEDGE.

Use exact frozen Task-1F R1 LOCAL_HEDGE dynamics:

T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063.

No GLOBAL_HEDGE arm is required.

OBSERVATION METHOD

Instrument the exact V0.1 step
without changing return values.

At each epoch,
before the exact LOCAL_HEDGE step:

compute from the inherited demand_adapter:

d_C;
d_S;
L_C12;
L_S12;
L_C3;
L_S3.

Compute the exact inherited updated global pools:

C_pool';
S_pool';

pc;
ps.

Then call the exact frozen V0.1 step.

Intercept the exact inherited
support_margin_field calls
inside U recruitment.

Return the inherited value unchanged.

Use those calls only to observe
the exact U recruitment contexts
that the running V0.1 trajectory actually reaches.

No intervention may alter:

states;

timers;

B;

Q;

pool state;

requests;

randomness;

or operation order.

OBSERVED U-CELL HAZARDS

For each actual U recruitment evaluation,
record the exact V0.1 C/S hazards:

sup_C
=
W_POOL * pc
+
W_LOCAL * L_C3;

sup_S
=
W_POOL * ps
+
W_LOCAL * L_S3;

opp_C
=
W_POOL * ps
+
W_LOCAL * L_S3;

opp_S
=
W_POOL * pc
+
W_LOCAL * L_C3;

g_C;
g_S;

lambda_C;
lambda_S.

Use the exact support-margin values
returned by the running parent function.

COUNTERFACTUAL NO-POOL SHADOW

For the same exact local state,
compute a shadow only:

pc = 0;
ps = 0.

Preserve:

L_C3;
L_S3;
support-margin C;
support-margin S;
all current cell/local states.

Compute:

lambda_C_local;

lambda_S_local.

Do not feed the shadow result
back into the organism.

DIRECTIONAL METRIC

When:

lambda_C + lambda_S > 0,

define actual C share:

s_C
=
lambda_C
/
(lambda_C + lambda_S).

For the no-pool shadow:

s_C_local
=
lambda_C_local
/
(lambda_C_local + lambda_S_local)

when its denominator is positive.

Directional TV for the binary C/S recruitment choice:

TV_side
=
|s_C - s_C_local|.

A side flip occurs when:

actual higher-probability side is C
and shadow higher-probability side is S;

or the directional mirror.

Ties are not flips.

RATE METRIC

Define:

lambda_CS
=
lambda_C + lambda_S.

lambda_CS_local
=
lambda_C_local + lambda_S_local.

Relative C/S recruitment-rate delta:

R_rate
=
|lambda_CS - lambda_CS_local|
/
max(lambda_CS, 1e-12).

REPORT PER WORLD

U recruitment evaluations;

mean / median / p90 TV_side;

fraction TV_side >= 0.01;

fraction TV_side >= 0.05;

fraction TV_side >= 0.10;

C/S side flips;

side-flip fraction;

mean / median / p90 R_rate;

fraction R_rate >= 0.10;

fraction R_rate >= 0.25;

fraction R_rate >= 0.50;

mean |pc - ps|;

mean pc;

mean ps.

Also report the same metrics
by Task-1 phase 0..4.

DIRECTIONAL PREVALENCE

LU0B_DIRECTIONAL_POOL_PREVALENT = TRUE iff:

1. observation mechanism active
   in all five worlds;

2. all parent runtime integrity probes pass;

3. median across worlds of
   fraction(TV_side >= 0.05)
   is at least 0.10;

4. at least 4 of 5 worlds
   contain at least one C/S side flip;

5. pooled side-flip fraction
   is at least 0.02.

RATE PREVALENCE

LU0B_RATE_POOL_PREVALENT = TRUE iff:

1. observation mechanism active
   in all five worlds;

2. all parent runtime integrity probes pass;

3. median across worlds of
   fraction(R_rate >= 0.10)
   is at least 0.25;

4. at least 4 of 5 worlds
   have fraction(R_rate >= 0.10)
   greater than zero.

NEGLIGIBLE PREVALENCE

LU0B_POOL_PRACTICALLY_NEGLIGIBLE = TRUE iff:

1. DIRECTIONAL_POOL_PREVALENT = FALSE;

2. RATE_POOL_PREVALENT = FALSE;

3. median across worlds
   fraction(TV_side >= 0.05)
   < 0.01;

4. median across worlds
   fraction(R_rate >= 0.10)
   < 0.05;

5. pooled side-flip fraction
   < 0.001.

INTERPRETATION

If either:

LU0B_DIRECTIONAL_POOL_PREVALENT

or

LU0B_RATE_POOL_PREVALENT

is TRUE:

the global pool materially contributes
during naturally reached V0.1 states.

Before strict-local learned-updater training,
preregister a local-pool replacement experiment.

Do not simply hide pc/ps
inside the neural student.

If:

LU0B_POOL_PRACTICALLY_NEGLIGIBLE = TRUE:

the nonidentifiability shown by LU-0
is rare in natural trajectories.

A strict-local learned-updater feasibility experiment
may proceed,
but must retain an explicit out-of-distribution
counterfactual test for the LU-0 seam.

Otherwise:

the result is intermediate.

Preregister a direct student A/B:

STRICT_LOCAL

versus

LOCAL_PLUS_POOL

before an architecture decision.

MECHANICAL GATE

Before LU0BF1 prove:

exact parent LOCAL_HEDGE parity;

observer returns inherited values unchanged;

five-manifest generator frozen
but primary manifests not yet derived;

observer captures U evaluations;

no observation on non-U support calls
is misclassified as U recruitment;

counterfactual never enters dynamics;

phase labels diagnostic only;

two mechanical runs byte-identical.

PRIMARY DISCIPLINE

After LU0BF1:

derive and bind all five manifests
before any trajectory executes.

Then run two complete five-world audits
byte-identically.

Interpret only after duplicate identity.

NO POST-RESULT TUNING

Do not change:

five-world count;

fresh-world derivation;

no-pool counterfactual;

TV thresholds;

rate thresholds;

prevalence thresholds;

side-flip definition;

phase definitions;

parent V0.1 dynamics;

or interpretation rules

after execution.

PLAIN-SPEAK QUESTION

LU-0 showed that distant activity
CAN change what a cell is told to do
even when its neighborhood looks identical.

Now we ask:

DOES THAT ACTUALLY HAPPEN OFTEN
WHILE THE ORGANISM IS WORKING?

We will watch real V0.1 trajectories.

For every uncommitted cell
that is deciding what to become,
we calculate its real instruction.

Then, without changing the organism,
we ask what that instruction
would have been
if the two global pool signals
were removed.

If the answer changes often,
we need to redesign that global dependency
before building the neural cell brain.

If it almost never changes,
we may be able to train locally
and treat LU-0 as an edge-case test.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
