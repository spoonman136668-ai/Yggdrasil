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


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — LEARNED-STATE TRUST-REGION HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H172 HELD-OUT PRIMARY EXECUTION.

FINAL H172 SANDBOX HARNESS

File:

h172_trust_region_v1.py

SHA-256:

7e0ddc689ff094af85b2629b8adb5044fb920758a42eac493aff55d7ca89e888.

PARENT H171 MODEL

Reuse:
the accepted H171
fine-scale learned
matched-turnover substrate.

Cell scale:

g=0.25.

Repair lifetime:

292 cycles.

Tasks:

SMOOTH,
MIXED.

Turnover:

ROAMING,
HOTSPOT.

Label noise eta:

0,
0.10.

Observation controller:

exact H171/H169
HIST-GEOM one-plus-one rule.

No:
functional observation count
or:
purchase rule

is changed.

TRUST-REGION PRIOR

At:
100%
membership restoration
for:
each repair cycle,

freeze:

p_cycle =
the current context-repaired
lesion coefficient vector.

Estimate:

rms_local =
RMS
of:
currently surviving live-neighbor
coefficients
touching:
the lesion.

rms_global =
RMS
of:
all surviving
coefficients.

s_cycle =
max(
rms_local,
0.25 * rms_global,
1e-6
).

For lesion size K:

R_tau =
tau
*
s_cycle
*
sqrt(K).

No:
target label,
lost coefficient,
held-out test output,
or:
teacher output

enters:
the trust radius.

PROJECTION

After:
every local ridge solve

inside:
the repair cycle,

candidate:
u.

d =
u - p_cycle.

If:

||d||_2
<=
R_tau,

accept u.

Else:

project:

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
all post-membership
maturation solves
within:
that cycle.

TRUST LEVELS

TRUST2:

tau=2.0.

TRUST4:

tau=4.0.

No:
tau adjustment
after:
sanity.

POLICIES

H171_UNCONSTRAINED.

TRUST2_HIST_GEOM.

TRUST4_HIST_GEOM.

MICRO2_LEVERAGE.

LOCAL_CHECKPOINT_ORACLE.

SANITY

Disjoint family:

20260922190000...

6 representative
condition-world lifetimes.

5 policies.

30 policy lifetimes.

Sanity-output SHA-256:

38bc8caf98baae54c82b7d709d493c3f7dd635a8c9857303ddfd29b9daff1ff8.

Mechanical checks:

- exactly five policies / seed;
- exact six sanity seeds;
- oracle final learned-output fidelity:
  exactly 1.0;
- observation counts:
  unchanged
  between:
  H171_UNCONSTRAINED,
  TRUST2,
  TRUST4;
- trust projection
  affects:
  only:
  repaired lesion coefficients;
- no:
  lost learned coefficient,
  held-out test output,
  teacher output,
  or:
  target label

enters:
the trust-region bound.

NON-EVIDENCE SIGNAL

TRUST2:

minimum sanity
FINAL learned-output fidelity:

approximately 0.9625.

No:
negative-fidelity sanity world.

Median projection duty:

approximately 3.1%.

Maximum sanity projection duty:

approximately 8.2%.

TRUST4:

is:
mostly inactive
in:
the sanity matrix,

with:
maximum projection duty:

approximately 1.0%.

No:
sanity policy
shows:
material observation-count
increase.

These values are:

NON-EVIDENCE.

No:

- tau;
- prior definition;
- local-scale definition;
- projection center;
- teacher;
- training rule;
- damage law;
- query rule;
- history window;
- lambda;
- feedback-noise rate;
- lifetime;
- acceptance gate

was changed.

PRIMARY FAMILY

20260922100000..20260922100079.

80 held-out worlds.

5 policies.

400 policy lifetimes.

Approximately:

116,800
policy repair cycles.

H172 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H172 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — LEARNED-STATE TRUST-REGION HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H172 HELD-OUT PRIMARY EXECUTION.

FINAL H172 SANDBOX HARNESS

File:

h172_trust_region_v1.py

SHA-256:

7e0ddc689ff094af85b2629b8adb5044fb920758a42eac493aff55d7ca89e888.

PARENT H171 HARNESS

SHA-256:

59141dc4bcea2c6befa58869c63ba725f5637d53360bf74bf3c67dbd4f6f5457.

TRUST-REGION IMPLEMENTATION

After:
100%
membership return
and:
context reconstruction,

capture:

p_cycle

as:
the complete current
context-repaired lesion vector.

Compute:

rms_local

from:
currently live
non-lesion Moore neighbors
touching:
the lesion.

Compute:

rms_global

from:
all surviving coefficients.

Define:

s_cycle =
max(
rms_local,
0.25 * rms_global,
1e-6
).

For:
K lesion cells,

radius:

R_tau =
tau
*
s_cycle
*
sqrt(K).

After:
each local functional ridge solve,

candidate:

u.

Displacement:

d =
u - p_cycle.

If:
||d||_2
<=R_tau,

accept:
u.

Otherwise:

project:
onto:
the Euclidean ball
centered at:
p_cycle
with:
radius R_tau.

The same:

p_cycle
and:
R_tau

remain:
fixed
through:
the complete repair cycle.

TRUST LEVELS

TRUST2:

tau=2.0.

TRUST4:

tau=4.0.

No:
target output,
teacher label,
lost learned coefficient,
held-out evaluation output

enters:
trust-center
or:
trust-radius authority.

QUERY / OBSERVATION CONTROL

Identical to:
H171.

HIST-GEOM-1PLUS1:

always:
one maximum-leverage
task label.

Second label iff:

rho_geom>=0.98

OR:

cycle>1
AND:
rho_geom<=0.50
AND:
novelty5>=0.75.

No:
new observation
is introduced
by:
the trust region.

POLICIES

H171-UNCONSTRAINED.

TRUST2-HIST-GEOM.

TRUST4-HIST-GEOM.

MICRO2-LEVERAGE.

LOCAL-CHECKPOINT-ORACLE.

SANITY

Disjoint family:

20260922190000...

6 representative
learned matched-turnover worlds.

5 policies.

30 policy lifetimes.

292 repair cycles / lifetime.

Mechanical checks:

- exactly five policies / seed;
- exact six sanity seeds;
- LOCAL-CHECKPOINT-ORACLE
  final learned-output fidelity:
  exactly 1.0;
- TRUST2 / TRUST4
  use:
  the same functional observation count
  as:
  H171-UNCONSTRAINED
  inside:
  each paired sanity world;
- trust center / radius
  are:
  target-blind;
- no:
  lost learned coefficient,
  held-out test label,
  or:
  teacher output
  enters:
  projection authority;
- mutable repaired state
  persists:
  through:
  all 292 cycles.

Accepted sanity matrix SHA-256:

38bc8caf98baae54c82b7d709d493c3f7dd635a8c9857303ddfd29b9daff1ff8.

NON-EVIDENCE SIGNAL

TRUST2:

selective projection duty
in:
the six representative sanity worlds

is:
approximately:
0.003
to:
0.082.

Maximum observed
candidate displacement / radius ratio:

approximately:
1.06
to:
1.27.

Thus:

TRUST2
is:
not:
freezing:
ordinary local repair.

Representative
TRUST2
FINAL learned-output fidelities:

approximately:
0.962
to:
0.994.

Representative
TRUST2
cumulative logit exposure:

approximately:
36
to:
128.

TRUST4:

is:
mostly inactive
in:
the same sanity worlds

and:
closely tracks:
the unconstrained H171 policy.

No representative sanity world
contains:
the catastrophic
H171 logit-tail event.

Therefore:

the primary remains:
a live:
tail-containment test.

No:

- tau;
- local-scale definition;
- projection center;
- teacher;
- training rule;
- damage law;
- query rule;
- observation count;
- lifetime;
- sample size;
- acceptance gate

is changed.

PRIMARY FAMILY

20260922100000..20260922100079.

80 held-out learned-task worlds.

5 policies.

400 policy lifetimes.

292 repair cycles / lifetime.

H172 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H172 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
