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


FINAL ACCEPTED PRIMARY CLOSURE — GLOBAL INFORMATION-DESIGN / MEASUREMENT-CONDITIONED MICRO-PATCH

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-POSITIVE.

FROZEN HARNESS SHA-256

40e39df728c731d8f03c16084cd57a0d4c5d54287e3c5ae99e04446eaa325847.

ACCEPTED PRIMARY FAMILY

20260920500000..20260920502399.

PRIMARY MATRIX

2,400 underlying worlds.

7 policies.

16,800 policy-world evaluations.

Validation:

- exactly 2,400 unique held-out seeds;
- exact accepted seed interval;
- exactly seven policy rows / seed;
- no accepted-seed gaps;
- no accepted-seed duplicates;
- zero functionally-trivial worlds;
- contaminated 202609204... family excluded;
- no post-primary parameter tuning.

PRIMARY CANDIDATE

AOPT-L03.

MIXED CONTEXT — FINAL RECOVERY

Pooled across:
COMPACT
and:
FOUR-PATCH.

AOPT-L03 median final functional recovery:

1%:
0.9830.

2%:
0.9644.

5%:
0.9854.

10%:
0.9896.

Frozen 1%..5% target:

>=0.94.

PASS:
all three.

MIXED T90 RELIABILITY

AOPT-L03
T90-world fraction:

1%:
88.0%.

2%:
88.0%.

5%:
95.5%.

Frozen target:

>=80%
for all three

and:
>=85%
for:
at least two of three.

PASS:
all three exceed 85%.

This is:
the strongest reliable
small-lesion functional-recovery result
in:
the H151..H156 sequence.

COMBINED BIAS + INFORMATION-DESIGN EFFECT

FIXED-L10
T90-world fraction:

1%:
58.5%.

2%:
51.0%.

5%:
70.5%.

AOPT-L03 improvement:

1%:
+29.5 percentage points.

2%:
+37.0.

5%:
+25.0.

Required:

>=15 points
in:
at least two of three.

PASS:
3 / 3.

Thus:

the H152/H153 reliability ceiling
was not:
an unavoidable consequence
of:
the 24-observation cap.

Measurement / inference configuration
was:
a major part
of:
the limit.

QUERY-DESIGN VALUE
AT FIXED REGULARIZATION

FIXED-L03
T90-world fraction:

1%:
81.5%.

2%:
76.0%.

5%:
93.5%.

AOPT-L03:

88.0%,
88.0%,
95.5%.

Improvement:

1%:
+6.5 points.

2%:
+12.0.

5%:
+2.0.

Required:

>=5 points
in:
at least two of three

OR:
the frozen downtime alternative.

PASS:
1%
and:
2%.

Median functional downtime:

1%:
AOPT 1.764
versus:
FIXED 1.967.

Reduction:
approximately 10.3%.

2%:
2.398
versus:
2.658.

Reduction:
approximately 9.8%.

5%:
2.554
versus:
2.805.

Reduction:
approximately 8.9%.

Therefore:

query design adds:
measurable value
beyond:
the lambda change.

AOPT VERSUS GREEDY D-OPT / LEVERAGE

LEV-L03
T90-world fraction:

1%:
88.0%.

2%:
86.5%.

5%:
95.0%.

AOPT-L03:

88.0%,
88.0%,
95.5%.

AOPT matches / exceeds:
LEV
in:
3 / 3.

Median final recovery difference
AOPT minus LEV:

1%:
approximately -0.0006.

2%:
approximately +0.0015.

5%:
approximately +0.0013.

No:
>0.02
AOPT deficit.

PASS.

Interpretation:

both:
global D-optimal / leverage
and:
A-optimal conditioning

are:
effective.

A-optimal trace reduction
has:
a small edge
at:
2% / 5%
without:
meaningful quality sacrifice.

DIRECT CONDITIONING MECHANISM

FOUR-PATCH,
MIXED 2%:

median posterior covariance trace:

FIXED-L03:
96.19.

AOPT-L03:
86.92.

Reduction:
approximately 9.6%.

FOUR-PATCH,
MIXED 5%:

FIXED-L03:
272.32.

AOPT-L03:
260.56.

Reduction:
approximately 4.3%.

PASS:
both required cells.

This directly links:
the designed measurement set

to:
lower posterior uncertainty
for:
the joint missing-state solve.

MULTI-WOUND RELIABILITY

AOPT-L03
T90-world fraction:

MIXED 1%:

COMPACT:
87%.

FOUR:
89%.

gap:
2 points.

MIXED 2%:

COMPACT:
91%.

FOUR:
85%.

gap:
6 points.

MIXED 5%:

COMPACT:
94%.

FOUR:
97%.

gap:
3 points.

Thus:

FOUR-PATCH reliability
is:
within 10 points
of:
COMPACT

in:
3 / 3.

This is:
a major improvement
over:
H152..H155.

MULTI-WOUND LATENCY

Median functional T90
among worlds reaching T90:

MIXED 1%:

COMPACT:
3.

FOUR:
6.

MIXED 2%:

COMPACT:
4.

FOUR:
9.

MIXED 5%:

COMPACT:
7.

FOUR:
8.

Frozen <=20% latency-penalty gate:

PASS:
5%.

FAIL:
1%,
2%.

Therefore:

H156 removes:
the distributed-wound
RELIABILITY gap

but:

does NOT remove:
the distributed-wound
LATENCY gap
for:
the smallest lesions.

This is:
the principal remaining limit.

SMOOTH CONTEXT

AOPT-L03
median final recovery:

1%:
0.9994.

2%:
0.9985.

5%:
0.9990.

PASS:
all >=0.95.

Lower regularization
and:
information design

do NOT:
destabilize:
smooth developmental repair.

SCRAMBLED CONTEXT

At:
5% damage:

AOPT-L03
median final recovery:
0.8642.

SMOOTH:
0.9990.

SCRAMBLED remains:
materially below:
SMOOTH.

The gap:
approximately 0.135.

Mechanism specificity:
retained,
although:
functional feedback can still
recover substantial arbitrary-state signal.

CHECKPOINT-ORACLE

Final recovery:
1.0.

Remains:
the ceiling.

PASS.

PREREGISTERED GATE REVIEW

PASS:

1.
MIXED 1%..5%
median final recovery >=0.94.

2.
MIXED T90 reliability
>=0.80 all
and:
>=0.85 in at least two.

3.
>=15-point gain
over:
FIXED-L10
in:
3 / 3.

4.
Information-design value
over:
FIXED-L03
at:
1%
and:
2%.

5.
AOPT
matches / exceeds:
LEV
without:
material final-recovery loss.

6A.
FOUR-PATCH
T90-world reliability parity
within:
10 points
in:
3 / 3.

7.
Posterior-trace reduction
in:
FOUR-PATCH
2%
and:
5%.

8.
SMOOTH quality.

9.
SCRAMBLED remains:
below:
SMOOTH.

10.
ORACLE ceiling.

FAIL:

6B.
FOUR-PATCH
median T90 latency penalty
<=20%
in:
at least two of three.

Observed pass:
1 / 3.

FINAL INTERPRETATION

H156 is:

MIXED-POSITIVE.

The core H156 hypothesis is:
SUPPORTED.

The 24-query limit
was NOT:
intrinsically too small.

A major portion
of:
the prior reliability failure

came from:

- overly strong regularization;
- poorly conditioned measurement selection;
- component-first allocation
  that did not optimize:
  the joint inverse problem.

With:

lambda=0.03

and:

global information-designed queries,

MIXED
1%..5%
functional T90 reliability rises to:

88%,
88%,
95.5%.

This is:
a substantial step
toward:
reliable intelligence micro-patching.

The remaining failure
has changed character.

It is no longer primarily:

CAN
THE PATCH
RECOVER?

It is:

HOW FAST
CAN
MULTIPLE
SMALL PATCHES
RECOVER?

The multi-wound reliability gap
is essentially removed,

but:
1% / 2%
FOUR-PATCH worlds

often require:
more maturation steps
than:
compact worlds.

ARCHITECTURAL CONSEQUENCE

The next experiment should NOT:

increase:
the 24-observation cap.

It should:

change:
the temporal schedule
of:
the same 24
information-designed observations.

Candidate:

FRONT-LOADED /
SUFFICIENCY-TRIGGERED
FEEDBACK BURSTS.

Examples:

- 4 observations / step
  for:
  6 steps;

- 6 observations / step
  for:
  4 steps;

- adaptive batch size
  driven by:
  posterior trace / rank sufficiency.

The target is:

preserve:
H156 reliability

while:

reducing:
FOUR-PATCH functional T90

without:
more total observations.

NEXT SCOPED EXPERIMENT

H157 —
TEMPORAL INFORMATION-SCHEDULING /
FRONT-LOADED MICRO-PATCH FEEDBACK.

H156 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- global retraining;
- biological claims;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
