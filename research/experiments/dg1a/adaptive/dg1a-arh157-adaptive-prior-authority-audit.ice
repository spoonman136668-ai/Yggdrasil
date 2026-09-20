TITLE: DG-1A-AR-H157 — Adaptive Developmental-Prior Authority / Noisy Local Feedback Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh156-joint-measurement-conditioning-audit.ice

PURPOSE

H156 established:

the dominant H152-H155 reliability limit
was:
OVER-REGULARIZATION.

A fixed:
lambda=0.03

plus:
24 local feedback observations

raised:
MIXED 1%..5%
median functional recovery
to:
approximately 0.97..0.99

and:
T90 reliability
to:
approximately 84%..96%.

But:

hard-coding:
one prior strength

is not:
a developmental control solution.

H157 asks:

CAN
A MICRO-PATCH
INFER:
HOW STRONGLY
TO TRUST
ITS DEVELOPMENTAL PRIOR

FROM:
ONLY
THE LOCAL FUNCTIONAL EVIDENCE
IT ACTUALLY ACQUIRES?

And:

CAN
PRIOR AUTHORITY
INCREASE AGAIN
WHEN:
LOCAL FEEDBACK
IS NOISY?

BOUNDARY

Synthetic research only.

No:
production model repair,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or runtime activation.

PARENT MODEL

Reuse:
H156.

R=8.
N=197.
sigma=0.22.
membership repair p=0.50.
12 post-membership maturation steps.

Contexts:

SMOOTH,
MIXED,
SCRAMBLED.

Damage:

1%,
2%,
5%.

Geometry:

COMPACT,
FOUR-PATCH.

Local feedback pool:

64 H152-style
lesion-local queries.

Primary query design:

GLOBAL LEVERAGE /
GREEDY D-OPTIMAL.

Maximum:
24 acquired feedback observations.

FEEDBACK NOISE

Functional feedback target
may be noisy.

For world w:

let:

s_w =
sqrt(
MSE(
Y_LESION,
Y_BASE
)
).

For feedback query j:

observed target =

true pre-lesion target
+
epsilon_j.

epsilon_j ~
Normal(
0,
eta * s_w
).

Primary eta:

0.00,
0.10,
0.25.

Noise potentials:

- deterministic from:
  world seed,
  query index,
  eta domain;
- common across:
  policies
  at:
  the same eta;
- evaluation queries remain:
  noise-free;
- no policy receives:
  true feedback target
  when eta >0.

Thus:

noise is scaled
to:
the actual lesion-induced
functional error
of:
that world.

ADAPTIVE PRIOR GRID

Declared lambda grid:

0.01,
0.03,
0.10,
0.30.

No other lambda
may be introduced
after:
primary begins.

ADAPTIVE SELECTION

Primary adaptive rule:

LEAVE-ONE-OUT
LOCAL PREDICTIVE ERROR.

Before:
four feedback observations
have been acquired:

lambda =
0.03.

Once:
at least four observations exist,

for each candidate lambda:

1.
for each acquired feedback observation k:
   fit:
   all lesion coefficients
   using:
   all other acquired feedback observations;

2.
use:
   the current developmental context prior
   and:
   candidate lambda;

3.
predict:
   the held-out acquired feedback target k;

4.
compute:
   mean squared leave-one-out error.

Choose:

the lambda
with:
lowest LOOCV error.

Tie-break:

choose:
the larger lambda.

This is:
a conservative
data-dependent prior-authority rule.

IMPORTANT

LOOCV uses only:
already-acquired local feedback.

It may NOT read:

- lost coefficients;
- held-out 256-query evaluation targets;
- unacquired feedback targets;
- latent context class.

QUERY SELECTION UNDER ADAPTIVE LAMBDA

After:
lambda is selected
for:
the current maturation step,

new feedback queries
are selected
using:
global leverage

with:
that lambda.

Thus:

prior authority
and:
measurement design

remain:
internally consistent.

FUNCTIONAL POLICIES

A — LEV-L03

Frozen H156 best fixed-prior parent.

lambda=0.03.

24 observations.

B — LEV-L10

Frozen stronger-prior comparator.

lambda=0.10.

24 observations.

C — ADAPT-CV

PRIMARY CANDIDATE.

lambda chosen:
from:
0.01,
0.03,
0.10,
0.30

by:
local-feedback LOOCV.

24 observations.

D — AOPT-ADAPT-CV

Same:
adaptive lambda.

A-optimal query selection.

Tests:
design-rule robustness.

E — FIXED-L03

Generated-order query comparator.

lambda=0.03.

24 observations.

F — ORACLE-LAMBDA

NON-DEPLOYABLE diagnostic.

Uses:
the same acquired local query sequence
as:
LEV-L03.

At:
final analysis only,

reports:
which lambda
from:
the declared grid

would have minimized:
the held-out evaluation MSE
for:
that world.

It does NOT:
alter:
the executed repair trajectory.

This measures:
lambda-selection headroom
without:
granting repair authority.

G — CHECKPOINT-ORACLE

Exact lost coefficient restore.

Evaluation ceiling only.

PRIMARY FACTORIAL

Contexts:
3.

Damage:
3.

Geometry:
2.

Feedback eta:
3.

Worlds / cell:
100.

Total underlying worlds:

3 x 3 x 2 x 3 x 100
=
5,400.

Primary executed repair policies:

A,
B,
C,
D,
E,
G

=
6 executed policy-worlds
per underlying world.

ORACLE-LAMBDA
is:
an analysis record,
not:
an additional repair execution.

Executed primary evaluations:

32,400.

PRIMARY METRICS

1. final functional recovery;
2. T50/T90/T99;
3. T90 world fraction;
4. functional downtime;
5. selected lambda trajectory;
6. final selected lambda;
7. fraction of steps at each lambda;
8. lambda changes / world;
9. feedback observations;
10. LOOCV error;
11. LEV-L03 versus ADAPT-CV;
12. LEV-L10 versus ADAPT-CV;
13. AOPT-ADAPT versus LEV-ADAPT;
14. noise x lambda interaction;
15. compact/four interaction;
16. oracle-lambda identity;
17. adaptive-lambda agreement with oracle-lambda;
18. oracle checkpoint gap.

PRIMARY ACCEPTANCE SHAPE

H157 supports:
ADAPTIVE DEVELOPMENTAL-PRIOR AUTHORITY

if:

1.
CLEAN FEEDBACK
eta=0,
MIXED 1%..5%:

ADAPT-CV
median final recovery
>=0.95.

2.
CLEAN FEEDBACK
eta=0,
MIXED 1%..5%:

ADAPT-CV
T90 world fraction
is:
within 5 percentage points
of:
LEV-L03

for:
all three damage fractions.

Thus:
adaptation must not sacrifice:
the H156 gain.

3.
NOISY FEEDBACK
eta=0.10 or 0.25,
MIXED 1%..5%:

ADAPT-CV
must improve:
T90 world fraction
over:
LEV-L03

by:
>=8 percentage points

in:
at least three of:
the six
eta x damage groups.

4.
At:
eta=0.25,

median final selected lambda
under:
ADAPT-CV

must be:
greater than:
the median selected lambda
at:
eta=0

in:
at least two of:
MIXED 1%,2%,5%.

This tests:
automatic restoration
of:
prior authority
under noisy evidence.

5.
At:
eta=0,

median final selected lambda
must be:
<=0.03

for:
at least two of:
MIXED 1%,2%,5%.

This tests:
automatic release
of:
prior authority
when:
fresh evidence is clean.

6.
AOPT-ADAPT-CV
must remain:
within:
0.03
median final recovery
of:
ADAPT-CV

in:
at least:
four of:
the six
MIXED
eta=0 and eta=0.25
small-lesion groups.

7.
For:
SMOOTH 1%..5%,
eta<=0.10:

ADAPT-CV
median final recovery
>=0.95.

8.
CHECKPOINT-ORACLE
remains:
the ceiling.

DIAGNOSTIC GATES

A.
If:
ORACLE-LAMBDA
usually differs
from:
ADAPT-CV,

then:
LOOCV is:
a poor authority estimator
even if:
adaptive repair works.

B.
If:
the same lambda
wins:
across:
all noise classes,

then:
adaptive authority
is:
not justified
by:
this model.

C.
If:
higher noise
requires:
higher lambda
but:
T90 still collapses,

then:
the feedback channel
needs:
noise-aware measurement budgeting,
not:
prior adaptation alone.

MIXED / NEGATIVE CONDITIONS

Treat H157 as:
mixed / negative
if:

- adaptive lambda
  degrades:
  clean H156 performance;
- LOOCV repeatedly selects:
  strong prior
  under:
  clean contradictory evidence;
- higher feedback noise
  does not:
  increase:
  inferred prior authority;
- adaptive policy
  does not:
  outperform:
  fixed lambda=0.03
  under:
  noisy feedback;
- lambda selection
  oscillates:
  excessively;
- A-opt / leverage
  disagree:
  catastrophically;
- surviving original coefficients
  must change.

SANITY

Disjoint family:

20260920590000...

Declared cells:

MIXED 2% FOUR eta=0;
MIXED 2% FOUR eta=0.25;
MIXED 5% COMPACT eta=0;
MIXED 5% COMPACT eta=0.25;
SMOOTH 2% FOUR eta=0.10;
SCRAMBLED 5% FOUR eta=0.25.

20 worlds / cell.

Sanity:
NON-EVIDENCE.

No:
lambda grid,
selection rule,
noise level,
budget,
or:
acceptance criterion
may change
from:
sanity outcomes.

PRIMARY SEEDS

20260920500000
through:
20260920505399.

The seed maps:
one-to-one
to:
the 5,400 primary factorial worlds.

No execution-semantic change
after:
the first held-out H157 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_ADAPTIVE_PRIOR_AUTHORITY_MICROPATCH

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false


PRE-PRIMARY PROVENANCE CORRECTION 01 — HELD-OUT SEED ROLLOVER

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H157 HELD-OUT PRIMARY EXECUTION.

DISCOVERY

The originally preregistered H157 primary interval:

20260920500000..20260920505399

overlaps:

the accepted H156 primary family:

20260920500000..20260920502399.

Therefore:

the original H157 interval
is NOT:
held out.

No H157 primary output
has been executed or accepted
from:
that interval.

DISPOSITION

The entire originally declared H157 primary family:

20260920500000..20260920505399

is:
INELIGIBLE /
NON-EVIDENCE

for:
H157 acceptance.

This rollover is:
provenance-only.

No:

- lambda grid;
- LOOCV rule;
- feedback-noise level;
- query-design policy;
- observation budget;
- context;
- damage fraction;
- geometry;
- sample size;
- acceptance gate

is changed.

REPLACEMENT H157 PRIMARY FAMILY

20260920600000
through:
20260920605399.

The 5,400 seeds map:
one-to-one
to:
the frozen H157 factorial worlds.

Repository and sandbox checks
found:
no prior H157 use
of:
the 202609206... family

before:
this freeze.

SANITY FAMILY

Remains:

20260920590000...

Sanity outputs remain:
NON-EVIDENCE.

H157 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first accepted
202609206...
primary world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — ADAPTIVE PRIOR AUTHORITY HARNESS

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H157 HELD-OUT PRIMARY EXECUTION.

UNIQUE SANDBOX HARNESS SHA-256

6f827ef787cf936f6f7135e7d8423a14dec4b977a25b91092aabdfddee844cbe.

The harness is pinned
under:
an H157-specific filename.

ADAPTIVE PRIOR GRID

0.01,
0.03,
0.10,
0.30.

Before:
four acquired observations:

lambda=0.03.

After:
four or more:

choose lambda
by:
exact ridge
leave-one-out predictive error
on:
already-acquired local feedback.

LOOCV is evaluated
using:
the standard linear-smoother
leave-one-out residual identity.

Tie-break:

larger lambda.

QUERY DESIGN

ADAPT-CV:

global leverage /
greedy D-optimal.

AOPT-ADAPT-CV:

global A-optimal.

Query selection reads:
basis geometry

and:
the lambda
selected from:
already-acquired feedback.

It does not read:
unacquired targets.

FEEDBACK NOISE

Observed local target:

true target
+
Gaussian noise.

Noise sd:

eta
*
sqrt(
lesion held-out MSE
).

Primary eta:

0,
0.10,
0.25.

Noise draws:

- deterministic per world / eta;
- common across policies;
- absent from:
  held-out functional evaluation.

SANITY MATRIX

Disjoint:
20260920590000...
family.

120 underlying worlds.

720 executed policy-world evaluations.

Validation:

- exactly 120 unique sanity seeds;
- six executed policies / seed;
- zero duplicate seed x policy rows;
- zero functionally-trivial worlds.

NON-EVIDENCE SANITY SIGNAL

Representative MIXED 2% FOUR:

eta=0:

LEV-L03:
median final recovery
approximately 0.950,
T90 reach 95%.

ADAPT-CV:
approximately 0.988,
T90 reach 100%,
median final lambda 0.01.

eta=0.25:

LEV-L03:
approximately 0.937,
T90 reach 65%.

ADAPT-CV:
approximately 0.983,
T90 reach 100%,
median final lambda 0.01.

Representative MIXED 5% COMPACT:

eta=0:

ADAPT-CV:
approximately 0.997,
T90 reach 100%,
median final lambda 0.01.

eta=0.25:

approximately 0.997,
T90 reach 100%,
median final lambda 0.01.

The non-deployable
oracle-lambda analysis
also selected:
0.01
through:
these representative sanity cells.

Thus:

sanity does NOT support:
the pre-experiment intuition
that:
eta=0.25
must restore:
stronger prior authority.

No:
noise level,
lambda grid,
selection rule,
query rule,
budget,
or:
acceptance gate
is changed.

This creates:
a genuine falsifiable primary question:

does:
the selected prior
increase with noise
across:
the full held-out factorial,

or:
is the correct authority
still:
weaker than:
lambda=0.03?

PRIMARY FAMILY REMAINS

20260920500000..20260920505399.

No execution-semantic change
is permitted
after:
the first held-out H157 primary world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — ADAPTIVE PRIOR / NOISY FEEDBACK HARNESS

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H157 HELD-OUT PRIMARY EXECUTION.

CORRECTED H157 SANDBOX HARNESS SHA-256

c4a67f7d875bcb92e1f38803d9bcb389764713b9409ebe9dd6a9a71f32f8170e.

PARENT HASHES

H151:
3f6042716b4e5a26f41569376a4dca833f5bae5f3c053aa2280615bfadb32e37.

H152:
e8be77384de4fef8a6b8eda875575f581edfc97794d5060e57e4e3bfa7b3b4e3.

H156 final measurement-conditioning harness:
40e39df728c731d8f03c16084cd57a0d4c5d54287e3c5ae99e04446eaa325847.

IMPLEMENTATION

Lambda grid:

0.01,
0.03,
0.10,
0.30.

Before:
four acquired feedback observations,

adaptive lambda:
0.03.

After:
four observations,

choose lambda by:
leave-one-out predictive error
on:
already-acquired local feedback only.

Tie:
larger lambda.

Adaptive query selection:

- ADAPT-CV:
  global leverage / D-optimal proxy;
- AOPT-ADAPT-CV:
  A-optimal trace-reduction proxy.

The currently selected lambda
is used:
both for:
query design
and:
the joint ridge solve
for that maturation step.

Fixed comparators:

LEV-L03:
lambda 0.03.

LEV-L10:
lambda 0.10.

FIXED-L03:
generated-order queries,
lambda 0.03.

CHECKPOINT-ORACLE:
exact lost-state restore,
evaluation ceiling only.

ORACLE-LAMBDA:

analysis-only.

It uses:
the final LEV-L03
selected query set
and:
developmental prior

to identify:
which declared lambda
would minimize:
noise-free held-out evaluation MSE.

It does NOT:
alter:
any repair trajectory.

FEEDBACK NOISE

For each world:

noise scale =
eta
*
sqrt(
MSE(
lesioned output,
pre-lesion output
)
).

eta:

0,
0.10,
0.25.

Noise potentials:

deterministic from:
world seed,
eta,
and:
feedback query index;

common across:
policies
within:
the same world / eta cell.

Evaluation remains:
noise-free.

SANITY

Disjoint family:

20260920590000...

120 underlying sanity worlds.

720 policy-world evaluations.

Mechanical checks:

- exact six executed policies / world;
- all policies complete;
- surviving original coefficients remain fixed;
- adaptive lambda uses only acquired feedback;
- unacquired targets remain hidden;
- oracle checkpoint remains evaluation-only;
- no functionally-trivial sanity world observed.

NON-EVIDENCE scientific signal:

ADAPT-CV selected:
lambda=0.01
for:
nearly all declared sanity worlds,

including:
most eta=0.25 worlds.

This does NOT:
change:
the lambda grid,
LOOCV rule,
noise levels,
acceptance criteria,
or:
primary design.

It is:
a live hypothesis test
for:
the held-out primary.

REPLACEMENT H157 PRIMARY FAMILY

20260920600000..20260920605399.

No H157 primary world
from:
this family
has been executed
at:
this freeze.

No execution-semantic change
is permitted
after:
the first accepted replacement-primary world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY PROVENANCE CORRECTION 02 — AUTHORITATIVE H156 PARENT / EXECUTABLE SEED BINDING

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H157 ACCEPTED PRIMARY EXECUTION.

AUTHORITATIVE PARENT

The header parent pointer:

dg1a-arh156-joint-measurement-conditioning-audit.ice

does not identify:
the accepted H156 artifact
that closed:
the measurement-conditioning experiment.

The authoritative accepted parent is:

dg1a-arh156-global-information-design-micropatch-audit.ice

with:
final accepted status
MIXED-POSITIVE.

This correction changes:
provenance only.

No H157 policy,
factor,
threshold,
or:
acceptance criterion
changes.

EXECUTABLE SEED-BINDING CORRECTION

Provenance Correction 01
already declared:

20260920500000..20260920505399

INELIGIBLE /
NON-EVIDENCE

because:
it overlaps:
the accepted H156 primary family.

It declared:
the replacement H157 family:

20260920600000..20260920605399.

The later implementation-freeze text
incorrectly repeated:

20260920500000..20260920505399

in:
one trailing
"PRIMARY FAMILY REMAINS"
statement.

That trailing statement is:
SUPERSEDED.

No H157 accepted primary world
has been executed
from:
the replacement 202609206... family.

FINAL H157 PRIMARY FAMILY

20260920600000
through:
20260920605399.

FINAL PINNED EXECUTABLE

h157_adaptive_prior_frozen_v2.py

SHA-256:

c4a67f7d875bcb92e1f38803d9bcb389764713b9409ebe9dd6a9a71f32f8170e.

The executable differs from:
the previous pinned H157 source

only in:
binding primary execution
to:
the already-declared
202609206...
replacement family.

SANITY REPLAY

The full disjoint H157 sanity matrix
was rerun under:
the final pinned executable.

Output SHA-256:

aeef98609945a1f14a5db205eb31c76144e0b37ffca48d9bfe55cf2e3eaf22f5.

This is:
byte-identical

to:
the previous H157 sanity output.

Therefore:

- adaptive lambda mechanics unchanged;
- feedback-noise mechanics unchanged;
- leverage / A-optimal mechanics unchanged;
- LOOCV rule unchanged;
- sanity-selected interpretation unchanged.

H157 ACCEPTED PRIMARY STATUS

NOT STARTED
at:
this freeze.

No execution-semantic change
is permitted
after:
the first accepted
202609206...
primary world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — ADAPTIVE DEVELOPMENTAL-PRIOR AUTHORITY

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-NEGATIVE FOR ADAPTIVE AUTHORITY / POSITIVE WEAKER-PRIOR DISCOVERY.

FINAL PINNED HARNESS SHA-256

c4a67f7d875bcb92e1f38803d9bcb389764713b9409ebe9dd6a9a71f32f8170e.

ACCEPTED PRIMARY FAMILY

20260920600000..20260920605399.

PRIMARY MATRIX

5,400 underlying worlds.

6 executed policies.

32,400 executed policy-world evaluations.

Validation:

- exactly 5,400 unique held-out seeds;
- exact accepted seed interval;
- exactly six executed policy rows / seed;
- zero duplicate seed x policy rows;
- zero functionally-trivial worlds;
- ineligible 202609205... H157 family excluded;
- no post-primary parameter tuning.

PRIMARY CANDIDATE

ADAPT-CV.

CLEAN MIXED FUNCTIONAL QUALITY

eta=0.

ADAPT-CV median final recovery:

1%:
0.9965.

2%:
0.9902.

5%:
0.9943.

Frozen target:
>=0.95.

PASS:
3 / 3.

CLEAN MIXED T90 RELIABILITY

ADAPT-CV:

1%:
95.0%.

2%:
98.5%.

5%:
99.0%.

LEV-L03:

1%:
87.5%.

2%:
87.5%.

5%:
91.5%.

Thus:

ADAPT-CV
does NOT sacrifice:
the H156 gain.

It materially improves it.

The preregistered wording:
"within 5 percentage points"

is:
literally exceeded
in the favorable direction
by:

+7.5,
+11.0,
+7.5 points.

Therefore:

the literal symmetric gate
does not pass,

but:
the stated no-sacrifice intent
is strongly satisfied.

This wording issue
does NOT:
alter:
the final H157 adaptive-authority conclusion.

NOISY MIXED PERFORMANCE

eta=0.10.

ADAPT-CV T90-world fraction:

1%:
96.0%.

2%:
98.0%.

5%:
99.5%.

LEV-L03:

1%:
91.0%.

2%:
86.5%.

5%:
96.5%.

Improvement:

+5.0,
+11.5,
+3.0 points.

eta=0.25.

ADAPT-CV:

1%:
94.5%.

2%:
97.0%.

5%:
98.5%.

LEV-L03:

1%:
90.0%.

2%:
86.0%.

5%:
95.0%.

Improvement:

+4.5,
+11.0,
+3.5 points.

Frozen noisy-feedback gate:

>=8-point improvement
in:
at least 3 of:
6 eta x damage groups.

Observed:

2 / 6.

FAIL.

Thus:

adaptive lambda improves:
noisy repair,

but:
not broadly enough
to satisfy:
the preregistered effect-size gate.

PRIOR-AUTHORITY RESPONSE TO NOISE

ADAPT-CV
median final selected lambda:

eta=0:

1%:
0.01.

2%:
0.01.

5%:
0.01.

eta=0.10:

1%:
0.01.

2%:
0.01.

5%:
0.01.

eta=0.25:

1%:
0.01.

2%:
0.01.

5%:
0.01.

Frozen hypothesis:

eta=0.25
should increase:
median prior authority
above:
eta=0

in:
at least 2 / 3
MIXED damage fractions.

Observed:

0 / 3.

FAIL.

This is:
the decisive H157 result.

Under:
the tested feedback-noise range,

the correct inferred prior
does NOT:
become stronger.

CLEAN PRIOR RELEASE

At:
eta=0,

median selected lambda:
0.01
for:
3 / 3.

Required:
<=0.03
for:
at least 2 / 3.

PASS.

LOOCV VERSUS NON-DEPLOYABLE ORACLE-LAMBDA

MIXED agreement rate:

eta=0:

1%:
100%.

2%:
100%.

5%:
100%.

eta=0.10:

1%:
98.5%.

2%:
100%.

5%:
99.0%.

eta=0.25:

1%:
97.0%.

2%:
95.0%.

5%:
93.5%.

Median oracle lambda:

0.01

for:
every:
eta x MIXED small-lesion group.

Thus:

LOOCV is:
not failing
to discover:
a hidden stronger-prior optimum.

The oracle diagnostic
agrees:

WEAKER PRIOR AUTHORITY
REMAINS OPTIMAL
THROUGH:
eta=0.25

in:
this synthetic model.

LAMBDA STABILITY

Median lambda changes / world:

1.

The adaptive trajectory
typically transitions:

0.03
->
0.01

and:
stays there.

No:
excessive oscillation.

AOPT VERSUS LEVERAGE UNDER ADAPTATION

For:
MIXED
eta=0
and:
eta=0.25,
1%..5%,

AOPT-ADAPT-CV
median final recovery
differs from:
ADAPT-CV

by:
far less than 0.03
in:
all six groups.

PASS.

Their T90 reliability
is also:
closely aligned.

Therefore:

the weaker-prior result
is not:
an artifact
of:
one information-design rule.

SMOOTH QUALITY

ADAPT-CV
median final recovery
for:
SMOOTH
1%..5%,
eta=0 or 0.10:

approximately:
0.9994..0.9998.

PASS:
all >=0.95.

CHECKPOINT-ORACLE

Remains:
the functional ceiling
at:
1.0.

PASS.

PREREGISTERED GATE REVIEW

PASS:

1.
Clean MIXED final recovery.

5.
Clean feedback releases:
prior authority
to:
<=0.03.

6.
AOPT / leverage
adaptive-design robustness.

7.
SMOOTH quality.

8.
ORACLE ceiling.

FAIL / MIXED:

2.
Literal "within 5 points"
clean T90 gate

only because:
ADAPT-CV
outperforms:
LEV-L03
by:
more than 5 points.

No-sacrifice intent:
PASS.

3.
Noisy-feedback
>=8-point improvement
in:
3 / 6 groups.

Observed:
2 / 6.

FAIL.

4.
Higher eta
increases:
median selected lambda

in:
2 / 3.

Observed:
0 / 3.

FAIL.

FINAL INTERPRETATION

H157 is:

MIXED-NEGATIVE
for:

ADAPTIVE DEVELOPMENTAL-PRIOR AUTHORITY.

The expected controller behavior:

MORE NOISE
->
TRUST DEVELOPMENTAL PRIOR MORE

is:
not supported.

Instead:

both:
local LOOCV

and:
the non-deployable
held-out oracle-lambda diagnostic

converge strongly on:

lambda =
0.01.

This remains true
through:
25%
feedback noise
scaled to:
lesion functional error.

The important positive discovery is:

H156's lambda=0.03
was still:
more conservative
than necessary

for:
this synthetic inverse problem.

WEAKER PRIOR AUTHORITY
PLUS:
INFORMATION-DESIGNED FEEDBACK

raises:
MIXED T90 reliability

to:
approximately:
95%..99%
under:
clean feedback

and:
94.5%..99.5%
under:
the tested noisy feedback.

Therefore:

the next architecture
should NOT:
add:
a complex adaptive-authority controller

unless:
future regimes
actually produce:
a prior/noise tradeoff.

Use:
the simpler measured:
weak-prior regime

as:
the next baseline.

REMAINING OPEN PROBLEM

H156 already isolated:

MULTI-WOUND LATENCY.

H157 does not:
change:
the 24-observation temporal schedule.

Therefore:

the next experiment should return to:

HOW
THE 24
INFORMATION-DESIGNED
OBSERVATIONS

ARE DISTRIBUTED
OVER TIME.

Use:

lambda=0.01

as:
the measured weak-prior baseline,

then compare:

- 2 observations x 12 steps;
- 4 x 6;
- 6 x 4;
- possibly:
  information-sufficiency-triggered
  batch sizes

while:
keeping:
the same total
24-observation cap.

Target:

reduce:
FOUR-PATCH
functional T90

without:
sacrificing:
the now-high
T90-world reliability.

NEXT SCOPED EXPERIMENT

H158 —
TEMPORAL INFORMATION-SCHEDULING /
FRONT-LOADED FUNCTIONAL MICRO-PATCH FEEDBACK.

H157 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- global retraining;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
