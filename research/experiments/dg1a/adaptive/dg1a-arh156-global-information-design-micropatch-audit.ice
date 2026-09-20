TITLE: DG-1A-AR-H156 — Global Information-Design / Measurement-Conditioned Functional Micro-Patch Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh155-residual-routed-global-joint-repair-audit.ice
RELATED_PARENT: dg1a-arh155-shared-joint-component-routed-micropatch-audit.ice

PURPOSE

H154 established:

functional error can be locally observed
without:
the missing parameter state
being separable by wound component.

H155 shared-joint repair established:

a joint solve is necessary,
but:
partitioning feedback into component TRAIN / VALIDATION streams
can discard useful measurement information.

The separately completed H155 residual-routed joint audit established:

routing the next query
toward:
the currently largest wound residual

does NOT:
solve the reliability limit.

Its best 24-query policies were:
fixed global allocation
and:
posterior-uncertainty allocation.

Therefore:

the next unresolved variable is:

MEASUREMENT CONDITIONING.

H156 asks:

CAN
THE SAME
24-OBSERVATION
LOCAL FUNCTIONAL-FEEDBACK CAP

BE CHOSEN
AS:
ONE GLOBAL
INFORMATION-DESIGN PROBLEM

SO THAT:

THE JOINT
LOST-STATE INVERSE PROBLEM

IS:
BETTER CONDITIONED

WITHOUT:
GLOBAL RETRAINING,
CHECKPOINT RESTORE,
OR:
MORE FEEDBACK?

BOUNDARY

Synthetic research only.

H156 does NOT:
- claim general cognition;
- repair a production model;
- execute STAB-18-R1;
- spend canonical scientific execution;
- alter surviving original coefficients;
- expose lost original coefficients to non-oracle policies;
- authorize runtime activation.

PARENT COLONY

Reuse:
H151 / H152.

R=8 lattice disk.
N=197.
Gaussian RBF readout.
sigma=0.22.

Contexts:

SMOOTH,
MIXED,
SCRAMBLED.

Damage:

1%,
2%,
5%,
10%.

Geometry:

COMPACT,
FOUR-PATCH.

Membership regeneration:

p=0.50
H150/H151 frontier schedule.

Post-membership maturation:

12 steps.

Surviving original coefficients:
immutable.

SHARED FEEDBACK CANDIDATE POOL

Reuse:
the H152 64-query local pool.

Each query is generated near:
one damaged cell,
with:
Gaussian jitter sd=0.12
body-radius units.

The candidate pool is:
local to the lesion

but:
NOT partitioned
by:
wound component.

All selected feedback observations:
train:
one global joint ridge solve
over:
all regenerated lesion coefficients.

No:
validation-only observations.

No:
component-local parameter solve.

No:
unselected target value
may influence:
query selection.

GLOBAL JOINT SOLVE

For lesion coefficient vector w_R:

minimize

||Phi_R w_R - r||^2
+
lambda ||w_R - w_prior||^2.

w_prior:

current context-harmonic reconstruction
at:
the beginning of the maturation step.

All acquired observations:
enter the solve.

Surviving original coefficients:
remain fixed.

PRIMARY OBSERVATION CAP

24 observations.

Two:
new observations
per:
post-membership maturation step.

Thus:

H156 changes:
measurement selection / conditioning,

not:
the feedback budget.

QUERY-DESIGN POLICIES

A — FIXED-L10

H152-style comparator.

Generated-order query selection.

lambda=0.10.

B — FIXED-L03

Generated-order query selection.

lambda=0.03.

Separates:
regularization effect
from:
information-design effect.

C — LEV-L10

Greedy global posterior leverage.

lambda=0.10.

For candidate row p:

score =
p^T Sigma p.

This is also:
the greedy
D-optimal
log-determinant gain ordering

because:
Delta logdet =
log(1 + p^T Sigma p).

D — LEV-L03

Same:
global leverage / greedy D-optimal selection.

lambda=0.03.

E — AOPT-L03

PRIMARY CANDIDATE.

For candidate p:

score =
p^T Sigma^2 p
/
(1 + p^T Sigma p).

This is:
the one-step reduction
in:
posterior covariance trace

under:
a rank-one measurement update.

It explicitly asks:

which next local query
reduces:
joint coefficient uncertainty
the most?

F — CONTEXT0

No:
functional feedback.

G — CHECKPOINT-ORACLE

Exact lost coefficient restore.

Evaluation ceiling only.

SANITY-ONLY REGULARIZATION COMPARATORS

FIXED-L30.
LEV-L30.

lambda=0.30.

These are:
not:
primary policies.

DESIGN DIAGNOSTICS

After:
24 observations

record:

- design matrix rank;
- smallest singular value;
- largest singular value;
- condition number when finite;
- effective rank;
- posterior covariance trace;
- precision log determinant.

These metrics:
are diagnostics.

They do not:
alter:
the repair policy
or:
stopping.

REGULARIZATION FREEZE

Candidate lambda values examined only on:
disjoint NON-EVIDENCE sanity worlds:

0.03,
0.10,
0.30.

Sanity showed:

- lambda=0.30
  materially underfits:
  MIXED repair;

- lambda=0.10
  remains:
  more biased than:
  0.03;

- lambda=0.03
  substantially raises:
  MIXED final recovery / T90 reach
  without:
  destabilizing:
  SMOOTH sanity worlds.

Therefore:

lambda=0.03
is frozen
for:
the primary low-bias information-design candidate.

FIXED-L10
and:
LEV-L10
remain:
primary comparators

so:
regularization benefit
cannot be mislabeled
as:
query-design benefit.

SANITY

Disjoint family:

20260920490000...

Declared cells:

MIXED 1% COMPACT;
MIXED 1% FOUR;
MIXED 2% FOUR;
MIXED 5% COMPACT;
MIXED 5% FOUR;
SMOOTH 2% FOUR;
SCRAMBLED 5% FOUR.

20 worlds / cell.

9 sanity policies.

140 worlds.
1,260 policy-world evaluations.

The final rolled harness reproduces:
the prior sanity output
byte-for-byte.

Sanity is:
NON-EVIDENCE.

No:
primary acceptance threshold
is selected from:
held-out primary outcomes.

PRIMARY FACTORIAL

3 contexts
x
4 damage fractions
x
2 geometries
x
100 worlds

=
2,400 underlying worlds.

7 policies.

16,800 policy-world evaluations.

COMMON-WORLD DISCIPLINE

Within one world,
all policies share:

- colony;
- learned coefficient field;
- lesion;
- membership regeneration schedule;
- 64 candidate feedback queries;
- feedback targets;
- held-out evaluation queries.

Only:
query selection
and:
ridge lambda
differ,
except:
CONTEXT0 / ORACLE.

PRIMARY METRICS

1. final functional recovery;
2. functional T50/T90/T99;
3. T90-world fraction;
4. functional downtime;
5. feedback observations;
6. held-out MSE ratio;
7. lesion-weight RMSE, analysis only;
8. design rank;
9. smallest singular value;
10. design condition number;
11. design effective rank;
12. posterior covariance trace;
13. precision log determinant;
14. COMPACT / FOUR-PATCH interaction;
15. AOPT-L03 versus FIXED-L03;
16. AOPT-L03 versus LEV-L03;
17. low-lambda versus lambda=0.10 effect;
18. oracle gap.

PRIMARY QUESTIONS

Q1.

Is:
24-query reliability

limited by:
poor conditioning
of:
the selected measurement set?

Q2.

Does:
lower ridge bias
lambda=0.03

recover:
substantial lost-state information
that:
lambda=0.10
suppresses?

Q3.

After:
holding lambda fixed,

does:
global information design

outperform:
generated-order measurement?

Q4.

Does:
global design
remove:
the multi-wound penalty

without:
allocating query budgets
by:
wound identity?

Q5.

Does:
A-optimal trace reduction
offer:
a functional advantage
over:
greedy D-optimal / leverage selection?

PRIMARY ACCEPTANCE SHAPE

H156 supports:
MEASUREMENT-CONDITIONED
COGNITIVE MICRO-PATCHING

if:

1.
MIXED 1%..5%,
AOPT-L03
median final functional recovery
>=0.94
for:
all three damage fractions.

2.
MIXED 1%..5%,
AOPT-L03
T90-world fraction
>=0.80
for:
all three

and:
>=0.85
for:
at least two of three.

3.
Relative to:
FIXED-L10,

AOPT-L03
improves:
T90-world fraction
by:
>=15 percentage points

in:
at least two of:
MIXED 1%,2%,5%.

This tests:
the combined
bias + information-design correction.

4.
Relative to:
FIXED-L03,

AOPT-L03
improves:
T90-world fraction
by:
>=5 percentage points

in:
at least two of:
MIXED 1%,2%,5%

OR:

reduces:
median functional downtime
by:
>=10%

without:
lowering T90-world fraction
by:
>2 points

in:
at least two of three.

This isolates:
information-design value
at:
fixed regularization.

5.
For:
MIXED 1%..5%,
AOPT-L03
matches or exceeds:
LEV-L03
T90-world fraction

in:
at least two of three

and:
is not:
>0.02 lower
in:
median final recovery
for:
any of three.

6.
FOUR-PATCH,
MIXED 1%..5%:

AOPT-L03
T90-world fraction
is:
within:
10 percentage points
of:
COMPACT

in:
at least two of three

and:

median T90 penalty
is:
<=20%
in:
at least two of three.

7.
AOPT-L03
reduces:
median posterior covariance trace

relative to:
FIXED-L03

for:
FOUR-PATCH
MIXED
2%
and:
5%.

This is:
the direct conditioning-mechanism gate.

8.
SMOOTH 1%..5%
AOPT-L03
median final recovery
>=0.95.

9.
SCRAMBLED
AOPT-L03
remains:
materially below:
SMOOTH

at:
5% damage.

10.
CHECKPOINT-ORACLE
remains:
the functional ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H156 as:
mixed / negative
if:

- lambda change explains:
  essentially all improvement
  and:
  information design adds:
  no measurable value;

- designed query sets
  improve matrix diagnostics
  without:
  improving functional reliability;

- FOUR-PATCH reliability
  remains:
  strongly below:
  COMPACT;

- lower lambda
  destabilizes:
  SMOOTH repair;

- A-optimal selection
  underperforms:
  fixed or leverage selection;

- 24 observations
  remain:
  insufficient
  despite:
  improved conditioning;

- surviving original coefficients
  must change.

PROVENANCE INCIDENT / PRIMARY-SEED ROLLOVER

Before:
this H156 preregistration
was committed,

a stale sandbox process
touched:
parts of:
the provisional

20260920400000..20260920402399
primary family.

No:
H156 acceptance rule
was derived from:
those provisional primary outputs.

They are:
CONTAMINATED /
NON-EVIDENCE.

Do not inspect or use:
their scientific metrics
for:
H156 acceptance.

FINAL HELD-OUT H156 PRIMARY FAMILY

20260920500000
through:
20260920502399.

This family:
has not been used
for:
sanity,
debugging,
threshold selection,
or:
exploratory analysis.

FROZEN SANDBOX HARNESS

File:
h156_measurement_conditioning_frozen_v2.py

SHA-256:
40e39df728c731d8f03c16084cd57a0d4c5d54287e3c5ae99e04446eaa325847.

The final rolled harness
differs from:
the prior sanity harness
only in:
the primary seed family.

A complete sanity rerun
under:
this exact file

produced:
byte-identical output
to:
the previous disjoint sanity run.

No execution-semantic change
is permitted
after:
the first accepted
202609205...
primary world.

H156 accepted primary status:

NOT STARTED
at:
this freeze.

H156 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- global retraining;
- biological claims;
- STAB-18-R1 execution;
- canonical scientific claims.

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_GLOBAL_INFORMATION_DESIGN_MICROPATCH

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false
