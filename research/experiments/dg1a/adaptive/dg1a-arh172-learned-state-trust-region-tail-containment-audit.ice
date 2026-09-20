TITLE: DG-1A-AR-H172 — Learned-State Trust-Region / Logit-Tail Containment Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh171-fine-scale-learned-micro-function-matched-turnover-stress.ice

PURPOSE

H171 received STRONG support under its preregistered group-level gates:

fine-scale learned classification survived:
approximately one body-equivalent turnover
with low supervision cost.

But:
post-primary tail analysis found:
rare catastrophic learned-logit drift

that:
top-line classification accuracy
could completely hide.

H172 asks:

CAN
A TARGET-BLIND
LOCAL STATE TRUST REGION

contain:
learned-logit runaway

without:
increasing:
functional observation cost

or:
sacrificing:
task accuracy?

BOUNDARY

Synthetic computational research only.

No:
production model repair,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or runtime activation.

PARENT MODEL

Reuse:
H171 exactly.

Cell scale:
g=0.25 only.

Tasks:
SMOOTH,
MIXED.

Turnover:
ROAMING,
HOTSPOT.

Feedback eta:
0,
0.10.

Matched lifetime:
292 cycles.

Teacher,
training,
student ridge,
damage,
query pool,
H169 purchase rule,
lambda,
and observation budget:
unchanged.

DEVELOPMENTAL CYCLE PRIOR

After:
100%
membership regeneration
and:
context reconstruction,

before:
the first functional micro-anchor solve,

capture:

p_cycle

=
the complete vector
of:
context-repaired coefficients

for:
the current lesion.

This p_cycle is:
TARGET-BLIND.

It uses:
only:
current mutable neighboring state
and:
developmental reconstruction.

LOCAL SCALE

Let:
B

be:
the set of currently live
non-lesion Moore-neighbor cells
touching:
the lesion.

Compute:

rms_local =
sqrt(
mean(
w_B^2
)
).

Compute:

rms_global =
sqrt(
mean(
w_surviving^2
)
).

Define:

s_cycle =
max(
rms_local,
0.25 * rms_global,
1e-6
).

No:
functional target,
lost learned coefficient,
held-out test output,
or:
teacher label

enters:
s_cycle.

TRUST REGION

For:
a lesion of:
K cells,

radius:

R_tau =
tau
*
s_cycle
*
sqrt(K).

After:
each unconstrained
local ridge solve

produces:
candidate vector
u,

define:

d =
u - p_cycle.

If:

||d||_2
<= R_tau,

accept:
u.

Otherwise:

project:

u_TR =
p_cycle
+
R_tau
*
d / ||d||_2.

The same:
p_cycle
and:
R_tau

remain:
fixed
for:
the entire:
repair cycle

including:
all 12
post-membership
maturation solves.

Thus:

functional repair
cannot:
walk indefinitely
away from:
the cycle's
developmental reconstruction.

TRUST LEVELS

Primary:

TAU2.

tau=2.0.

Robustness comparator:

TAU4.

tau=4.0.

No:
tau value
may change
after:
sanity.

FUNCTIONAL OBSERVATIONS

Exact H171 / H169
HIST-GEOM one-plus-one controller.

Always:
one maximum-leverage
binary task label.

Second label iff:

rho_geom >=0.98

OR:

cycle>1
AND:
rho_geom<=0.50
AND:
novelty5>=0.75.

No extra observations
are introduced.

POLICIES

A — H171-UNCONSTRAINED

Exact H171
HIST-GEOM-1PLUS1.

B — TRUST2-HIST-GEOM

PRIMARY CANDIDATE.

H171 controller
plus:
tau=2
cycle trust region.

C — TRUST4-HIST-GEOM

Robustness comparator.

tau=4.

D — MICRO2-LEVERAGE

H171
two-query reference.

E — LOCAL-CHECKPOINT-ORACLE

Exact learned-state ceiling.

PRIMARY FACTORIAL

Task:
2.

Turnover:
2.

eta:
2.

Worlds / cell:
10.

Underlying worlds:
80.

Policies:
5.

Policy lifetimes:
400.

Matched repair cycles:
approximately:
116,800.

PRIMARY METRICS

1.
baseline accuracy;

2.
FINAL accuracy;

3.
accuracy retention;

4.
Brier degradation;

5.
HALF / FINAL learned-output fidelity;

6.
world fraction:
FINAL learned-output fidelity >=0.95;

7.
world count:
FINAL learned-output fidelity <0;

8.
world count:
FINAL learned-output fidelity <-10;

9.
minimum FINAL learned-output fidelity;

10.
cumulative absolute
test-logit error exposure;

11.
paired exposure ratio
versus:
MICRO2-LEVERAGE;

12.
paired exposure ratio
versus:
H171-UNCONSTRAINED;

13.
trust projection count;

14.
trust projection duty;

15.
median / maximum
projection ratio;

16.
observation count;

17.
HOTSPOT repeat load;

18.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H172 supports:
TARGET-BLIND
LEARNED-STATE
TAIL CONTAINMENT

if:

1.
Baseline competence:
median test accuracy
>=0.85
for:
both task classes.

2.
TRUST2
median FINAL accuracy

is:
no more than:
0.03 below:
its own baseline

for:
every:
task x regime x eta group.

3.
>=90%
of TRUST2 worlds

finish:
within:
0.05 accuracy
of:
their own baseline

for:
every group.

4.
TRUST2
median Brier degradation

<=0.03
for:
every group.

5.
TRUST2
median FINAL learned-output fidelity

>=0.95
for:
every group.

6.
WORLD-LEVEL TAIL GATE:

>=95%
of:
all TRUST2 worlds

finish:
FINAL learned-output fidelity
>=0.95.

7.
ZERO:

TRUST2 worlds
with:
FINAL learned-output fidelity
<0.

8.
ZERO:

TRUST2 worlds
with:
FINAL learned-output fidelity
<-10.

9.
TRUST2
paired cumulative exposure

relative to:
MICRO2-LEVERAGE

has:
group median
<=1.35

for:
every group.

10.
TRUST2
median cumulative exposure

is:
lower than:
H171-UNCONSTRAINED

in:
at least:
6 of:
8 groups.

11.
TRUST2
uses:
the same median
functional observation count

as:
H171-UNCONSTRAINED

inside:
each group.

12.
TRUST4
must NOT:
produce:
a new:
accuracy,
Brier,
or:
tail-fidelity
failure

that:
TRUST2 avoids.

This tests:
that:
the result
is not:
a knife-edge
tau=2 artifact.

13.
LOCAL-CHECKPOINT-ORACLE
remains:
the exact learned-state ceiling.

STRONG SUPPORT

H172 receives:
STRONG support

if:

all primary gates pass

AND:

100%
of:
TRUST2 worlds

finish:
FINAL learned-output fidelity
>=0.95

AND:

pooled TRUST2
cumulative exposure

is:
no greater than:
H171-UNCONSTRAINED.

MIXED / NEGATIVE CONDITIONS

Treat H172 as:
mixed / negative
if:

- trust containment
  preserves:
  logits
  only by:
  degrading:
  classification accuracy;

- projection duty
  approaches:
  100%
  and:
  the system becomes:
  effectively frozen;

- TAU2
  and:
  TAU4
  disagree:
  catastrophically;

- target-blind local scale
  fails:
  to contain:
  rare runaway worlds;

- observation cost
  must increase;

- trust region
  hides:
  calibration drift
  rather than:
  preventing it.

SANITY WORLD SEEDS

20260922190000...

PRIMARY WORLD SEEDS

20260922100000
through:
20260922100079.

Sanity:
NON-EVIDENCE.

No:
tau,
local-scale definition,
projection center,
teacher,
training rule,
damage law,
query rule,
history window,
lambda,
feedback-noise rate,
lifetime,
or acceptance gate

may change
after:
the first held-out H172 world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_LEARNED_STATE_TRUST_REGION_TAIL_CONTAINMENT

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
