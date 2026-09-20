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
