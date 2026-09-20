TITLE: DG-1A-CLR1-H177 — Local Function-Coverage Information-Design Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / COGNITIVE LESION-REGENERATION
BRANCH: dg1a-ar
PARENT: dg1a-clr1-h176-cognitive-lesion-repair-boundary-audit.ice

PURPOSE

H175 established:
fine-scale selective cognitive micro-patching is possible.

H176 established:
global held-out task R^2 can look repaired
while the lesion-local learned function remains under-reconstructed.

The failure is not:
collateral interference,
large repair footprint,
or insufficient global task accuracy.

It is:
LOCAL FUNCTION GENERALIZATION.

H177 asks:

CAN THE SAME TWO TARGET-TASK FUNCTIONAL OBSERVATIONS
BE CHOSEN MORE INTELLIGENTLY

so that:

- lesion-local held-out fidelity improves;
- global target R^2 stays repaired;
- unrelated learned behavior stays preserved;
- moving responsibility remains repairable;
- observation cost stays exactly two?

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model repair.
No global retraining candidate.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT COGNITIVE MODEL

Reuse H176 exactly:

g=0.25.

N approximately 3209.

Two learned nonlinear functions:
A and B.

Same:
teacher class,
training distributions,
training / validation / held-out sample counts,
RBF body,
scale-aware ridge,
responsibility map,
k_star rule,
developmental regeneration,
lambda=0.01 local repair prior,
five repair cycles.

LESION MAGNITUDES

Primary:

BASE:
1.0 * k_star.

DOUBLE:
2.0 * k_star,
bounded by 10% of body.

H176 HALF is omitted:
already repairable.

H176 TRIPLE is omitted:
too far beyond the two-observation boundary
for this discriminative query-design test.

TRAJECTORIES

SAME:
repeat the original selective patch.

FOLLOW:
recompute current responsibility and selective patch every cycle,
using the exact H176 rule.

FUNCTIONAL OBSERVATION POOL

64 target-task lesion-local candidate queries.

Same H176 generator:

- lesion-member-centered / patch-centroid mixture;
- Gaussian macro jitter sd=0.12;
- inside unit disk;
- target values hidden until selected.

UNLABELED LOCAL COVERAGE PROBES

For every cycle:

generate:
128 lesion-local unlabeled probe points

using:
the same lesion centroid

and:
Gaussian jitter sd=0.15,

with a domain distinct from:

- repair candidate queries;
- H176/H177 local validation points;
- global held-out test points.

These probes reveal:

READOUT GEOMETRY ONLY.

No teacher target is observed at:
coverage probes.

G-OPTIMAL / COVERAGE QUERY DESIGN

Let:

X_cand:
64 x K
lesion-cell basis matrix
for candidate repair queries.

Let:

P:
128 x K
lesion-cell basis matrix
for unlabeled coverage probes.

Start:

A0 = lambda * I.

At each query-selection step:

for every unselected candidate row x,

consider:

A_new = A + x^T x.

Compute:

v_new(q)
=
p_q^T
A_new^{-1}
p_q

for every unlabeled probe row p_q.

Choose:

the candidate minimizing:

max_q v_new(q).

Tie:

lower candidate index.

Then:
A <- A_new.

This is:
target-blind
G-optimal-style
worst-case local predictive-variance reduction.

No:
teacher target,
repair target,
held-out output,
unrelated-task target

enters:
query selection.

POLICIES

A — CONTEXT0

Developmental repair only.

0 target observations.

B — LEV2

Exact H176 TARGET2
maximum-leverage
two-query parent.

C — GOPT2

PRIMARY CANDIDATE.

Exactly:
two target-task queries

selected by:
the frozen local-coverage rule.

D — LEV4

Exact H176 TARGET4
four-query reference.

E — ORACLE

Exact local pre-lesion two-head state restore.

Evaluation ceiling only.

LOCAL REPAIR

For LEV2 / GOPT2 / LEV4:

- target head only;
- current developmental target state as prior;
- lambda=0.01;
- surviving target coefficients fixed;
- unrelated head:
  developmental context only.

No unrelated-task functional observations.

GENERALIZATION TELEMETRY

Per cycle:

1.
repair-query MSE;

2.
128-point evaluation-only local-validation MSE
from the H176 validation domain;

3.
global held-out target R^2;

4.
unrelated-task global held-out R^2.

Coverage probes:
never receive targets
and:
cannot be used for evaluation labels.

PRIMARY FACTORIAL

Base learned worlds:
12.

Targets:
A, B.

Target-lesion worlds:
24.

Magnitudes:
BASE, DOUBLE.

Trajectories:
SAME, FOLLOW.

Policies:
5.

Policy lifetimes:

24 * 2 * 2 * 5
=
480.

Repair cycles:
5.

Total policy repair cycles:
2,400.

STRICT RELIABILITY

Reuse H176 strict condition.

A condition is RELIABLE iff:

1.
>=90%
cycle-1 joint repair success;

2.
>=90%
cycle-5 joint repair success;

3.
median unrelated-function post-repair loss
<=0.03
at cycle 1 and cycle 5;

4.
median target held-out R^2
does not decline by >0.03
from cycle 1 to cycle 5;

5.
median lesion-local validation MSE
is <=1.25x
the matched ORACLE local-validation MSE

at cycle 1 and cycle 5;

6.
median local-validation MSE
does not increase by >50%
from cycle 1 to cycle 5.

PRIMARY ACCEPTANCE SHAPE

H177 supports:
TWO-OBSERVATION
LOCAL FUNCTION-COVERAGE REPAIR

if:

1.
Baseline learning:
median held-out R^2 >=0.90
for both tasks.

2.
Localization success:
>=85%
of target-lesion worlds.

3.
GOPT2 is RELIABLE
for BASE / SAME.

4.
GOPT2 is RELIABLE
for BASE / FOLLOW.

These are:
the decisive cognitive gates.

5.
GOPT2
median cycle-5 local-validation MSE

is:
at least 15% lower
than LEV2

for:
BASE / FOLLOW

and:
no worse by >5%
for:
BASE / SAME.

6.
GOPT2
does not reduce:
cycle-1 or cycle-5
joint repair success
by:
>5 percentage points
relative to LEV2

in:
any BASE condition.

7.
GOPT2
median unrelated-function loss

is:
<=0.03
for:
every magnitude / trajectory cell.

8.
GOPT2
uses:
exactly two
target-task functional observations
per cycle
and:
zero unrelated-task observations.

9.
FOLLOW movement is real:

for BASE / FOLLOW,
median patch Jaccard <=0.75

OR:

median centroid displacement >=0.05.

10.
Generalization:

for every GOPT2 condition declared RELIABLE,

global held-out target R^2
remains within:
0.05
of original baseline

and:

repair-query MSE
does not:
hide:
cycle-5 local-validation growth >50%.

11.
LEV4 remains:
a higher-observation reference.

If LEV4 is RELIABLE
where GOPT2 is not,

report:
that:
query design alone
did not eliminate
the supervision deficit.

12.
ORACLE remains:
the local-state ceiling.

STRONG SUPPORT

H177 receives STRONG support if:

all primary gates pass

AND:

GOPT2 is RELIABLE
for:
DOUBLE / SAME

or:
DOUBLE / FOLLOW

without:
extra observations.

MIXED / NEGATIVE CONDITIONS

Treat H177 as mixed / negative if:

- GOPT2 still fails BASE / FOLLOW local validation;
- coverage-designed queries reduce local MSE
  but damage global R^2;
- query geometry overfits:
  the unlabeled coverage-probe distribution;
- LEV4 remains necessary at BASE;
- FOLLOW responsibility motion remains:
  fundamentally underconstrained
  by two target values.

NEXT INFLECTION

If:
GOPT2 passes:
BASE / SAME
and:
BASE / FOLLOW

with:
strict local generalization,

do NOT:
spend another long repair-optimization block.

Proceed directly to:

CLR2-H178 —
DEVELOPMENTAL CAPABILITY ADDITION.

learn A
->
preserve A
->
grow bounded patch for B
->
integrate B
->
preserve A+B.

SANITY WORLD SEEDS

20260922690000...

PRIMARY WORLD SEEDS

20260922600000
through:
20260922600011.

Sanity:
NON-EVIDENCE.

No:
teacher,
training distribution,
ridge scaling,
localization threshold,
magnitude,
trajectory rule,
coverage-probe distribution,
query-selection rule,
observation budget,
lambda,
cycle count,
or:
acceptance gate

may change
after:
the first held-out H177 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_COGNITIVE_LOCAL_FUNCTION_COVERAGE_QUERY_DESIGN

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — LOCAL FUNCTION-COVERAGE QUERY-DESIGN HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H177 HELD-OUT PRIMARY EXECUTION.

FINAL H177 SANDBOX HARNESS

File:

h177_clr1_gopt_v1.py

SHA-256:

670830bbe048ae170e196902af23f2ee8f37e05e4e4ad8e105de0531a3462834.

PARENT COGNITIVE MODEL

Exact H176
fine-scale cognitive model:

g=.25.

N=3209.

Same:
teacher,
training distribution,
scale-aware ridge,
responsibility map,
k_star,
BASE / DOUBLE lesions,
SAME / FOLLOW trajectories,
developmental repair,
lambda=.01,
five-cycle lifetime.

PRE-PRIMARY COMPARISON ISOLATION

To isolate:
QUERY SELECTION

rather than:
candidate-pool randomness,

H177 uses:

one COMMON
64-point
candidate query pool

per:

seed
x
target
x
magnitude
x
trajectory
x
cycle.

LEV2,
GOPT2,
and:
LEV4

select from:
the same candidate coordinates.

This is:
a methodological
pre-primary control.

It does NOT:
use:
any target value.

The LEV2 result
is therefore:

the H176
maximum-leverage
algorithm

re-evaluated
on:
the H177 common pool,

not:
a byte-identical
H176 random-pool replay.

No:
repair budget,
lambda,
teacher,
or:
acceptance gate
changes.

GOPT2

Unlabeled coverage probes:

128
lesion-local points.

Domain:

separate from:

- repair candidates;
- lesion-local validation;
- global held-out test.

No:
target value
is observed
at:
coverage probes.

For:
candidate design row x,

choose:
the point that minimizes:

the maximum
posterior predictive variance

over:
the 128
unlabeled coverage probes

after:
adding x.

Repeat:
for:
two total selected queries.

lambda=.01
sets:
the design prior.

Tie:

lower candidate index.

POLICIES

CONTEXT0.

LEV2.

GOPT2.

LEV4.

ORACLE.

All:
functional repair policies

observe:
target-task values only.

Zero:
unrelated-task
functional observations.

SANITY

Disjoint family:

20260922690000
and:
20260922690001.

2 base worlds.

4 target-lesion worlds.

2 magnitudes.

2 trajectories.

5 policies.

80 policy lifetimes.

Accepted sanity-output SHA-256:

80d466a38825027e06789aa7879c342cd6181433062524b822ff6391e8d814fd.

Mechanical checks:

- exact 80 rows;
- exact 5 policies
  per:
  target x magnitude x trajectory;
- 4 / 4
  target conditions
  localize;
- LEV2 / GOPT2:
  exactly 2 observations / cycle;
- LEV4:
  exactly 4;
- zero unrelated-task observations;
- coverage probes:
  target-blind;
- local validation:
  disjoint from:
  repair queries
  and:
  coverage probes.

NON-EVIDENCE SIGNAL

GOPT2
does NOT:
uniformly dominate
LEV2
in:
the sanity matrix.

Representative:

BASE / FOLLOW,
cycle 1:

GOPT2
local-validation MSE:
approximately 0.0083.

LEV2:
approximately 0.0103.

But:
cycle 5:

GOPT2:
approximately 0.0115.

LEV2:
approximately 0.0083.

DOUBLE cells
are also:
mixed.

Thus:

the hypothesis is:
live
and:
nontrivial.

No:
coverage distribution,
selection criterion,
query count,
lambda,
magnitude,
trajectory,
sample size,
or:
acceptance gate

was changed
from:
sanity outcomes.

PRIMARY FAMILY

20260922600000..20260922600011.

12 held-out
base learned worlds.

24 target-lesion worlds.

480 policy lifetimes.

2,400
policy repair cycles.

H177 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H177 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — LOCAL FUNCTION-COVERAGE INFORMATION DESIGN

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / NEGATIVE FOR TWO-QUERY COVERAGE REPAIR / REPAIR-OPTIMIZATION LINE CLOSED.

FINAL H177 HARNESS SHA-256

670830bbe048ae170e196902af23f2ee8f37e05e4e4ad8e105de0531a3462834.

ACCEPTED PRIMARY MATRIX SHA-256

3275b03f336509b6a8a184f237cc4e38aa6a2758a8485f2652418f6b3a92adbd.

ACCEPTED PRIMARY FAMILY

20260922600000..20260922600011.

PRIMARY MATRIX

12 held-out learned worlds.

24 target-lesion worlds.

2 magnitudes.

2 trajectories.

5 policies.

480 policy lifetimes.

2,400 repair cycles.

BASELINE

Median held-out R^2:

A:
approximately 0.9694.

B:
approximately 0.9543.

100%
of:
accepted target worlds

retain:
both learned functions
above:
R^2 0.85.

PASS.

LOCALIZATION

22 / 24
target-lesion worlds

localize successfully

under:
the frozen H176/H177
causal selective-patch rule.

Rate:

91.7%.

Frozen target:
>=85%.

PASS.

GOPT2 — BASE / SAME

Cycle-1 joint success:
100%.

Cycle-5:
100%.

But:

local-validation / ORACLE ratio

cycle 1:
approximately 1.769.

cycle 5:
approximately 1.356.

Frozen limit:
<=1.25.

FAIL.

GOPT2 — BASE / FOLLOW

Cycle-1 joint success:
100%.

Cycle-5:
approximately 77.3%.

Local-validation / ORACLE ratio:

cycle 1:
approximately 1.649.

cycle 5:
approximately 2.174.

FAIL.

Thus:

GOPT2
is NOT:
strictly reliable
for:
either decisive
BASE condition.

QUERY-DESIGN COMPARISON

BASE / SAME:

GOPT2
cycle-5 local-validation MSE

is:
approximately 16.9%
lower
than:
LEV2.

But:

cycle-1 local-validation MSE

is:
approximately 26.2%
higher.

BASE / FOLLOW:

GOPT2
cycle-5 local-validation MSE

is:
approximately 36.7%
HIGHER
than:
LEV2.

Cycle-1:

approximately 17.7%
higher.

Therefore:

target-blind
worst-case local-variance
coverage

does NOT:
consistently improve:
the learned-function
repair manifold.

It can:
trade:
one part
of:
local geometry

against:
another.

FOLLOW RELIABILITY

GOPT2
BASE / FOLLOW

also loses:
world-level repeated-repair reliability:

cycle 5:

approximately 77.3%

versus:

LEV2:
approximately 95.5%.

Thus:

the failure is:
not:
only:
a strict oracle-relative
local-validation threshold.

It also:
appears:
in:
world-level repeated repair.

LEV4 REFERENCE

LEV4
also fails:
the strict local-generalization
envelope.

BASE / SAME:

local-validation / ORACLE ratio

approximately:
1.254
at cycle 1

and:
1.270
at cycle 5.

BASE / FOLLOW:

approximately:
1.341
and:
1.106.

Even:
four:
pointwise leverage observations

do not:
cleanly establish:
the frozen
local-function reconstruction
criterion.

This indicates:

the remaining issue
is NOT:
simply:
two versus four
query count.

It is:
the underdetermined mapping
between:

a tiny:
local observation set

and:

the full:
lesion-local
learned function.

FOLLOW MOVEMENT

BASE / FOLLOW
patch motion remains:
strong.

Median:
patch Jaccard

approximately:
0.006
for:
GOPT2.

Median centroid displacement:

approximately:
0.744
normalized macro units.

Thus:

the moving-repair challenge
is:
genuine.

PRIMARY GATE REVIEW

PASS:

1.
Baseline learning.

2.
Localization success.

7.
Collateral preservation.

8.
Exactly two:
target-only
observations
for:
GOPT2.

9.
FOLLOW motion.

12.
Oracle ceiling.

FAIL:

3.
GOPT2 reliable
BASE / SAME.

4.
GOPT2 reliable
BASE / FOLLOW.

5.
Required:
BASE / FOLLOW
>=15%
local-validation
improvement
versus LEV2.

Observed:
worse.

6.
GOPT2
does not:
preserve:
cycle-5
BASE / FOLLOW
joint success
within:
5 points
of:
LEV2.

Observed:
approximately -18.2 points.

10.
Strict local generalization.

11.
LEV4 diagnostic:
more observations
do not:
cleanly solve:
the local-function gap.

STRONG SUPPORT:

FAIL.

FINAL INTERPRETATION

H177 is:

NEGATIVE

for:

TWO-OBSERVATION
LOCAL FUNCTION-COVERAGE
QUERY DESIGN.

H175 remains:
direct evidence
that:

selective
fine-scale
cognitive micro-patching

can:
restore:
global learned behavior

with:
very low collateral interference.

H176 / H177 add:

a stricter warning.

A local repair
can:

restore:
top-line task behavior

without:
uniquely reconstructing:
the lesion-local
function manifold.

Neither:

more pointwise leverage

nor:

target-blind
G-optimal coverage

fully resolves:
that underdetermination.

ARCHITECTURAL CONSEQUENCE

Stop:
the long
repair-query
optimization line.

The program directive is:

proof-of-cognition,
not:
perfect local-state reconstruction.

The unresolved:
local-function fidelity
risk

must:
remain:
an explicit open constraint,

but:

it should NOT:
block:
the next:
cognitive inflection experiment.

H175 has already demonstrated:

- learned multi-function specialization;
- causal selective lesions;
- bounded local regeneration;
- low collateral interference;
- repeated behavioral repair.

Therefore:

proceed to:
DEVELOPMENTAL CAPABILITY ADDITION

while:

measuring:
local-function drift
and:
interference

as:
mandatory safety metrics.

NEXT:

CLR2-H178 —
BOUNDED DEVELOPMENTAL
CAPABILITY ADDITION.

learn A

->

freeze / preserve A

->

grow:
a bounded
new cellular patch

for:
previously unseen capability B

->

learn B
using:
local patch plasticity

->

integrate:
A+B

->

measure:

A retention,
B generalization,
new active cells,
new compute,
interference,
reuse,
and:
whether:
B can be added
without:
global retraining.

H177 DOES NOT AUTHORIZE

- production use;
- live model repair;
- biological claims;
- whole-model retraining
  as:
  the candidate architecture;
- canonical scientific claims;
- STAB-18-R1 execution.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
