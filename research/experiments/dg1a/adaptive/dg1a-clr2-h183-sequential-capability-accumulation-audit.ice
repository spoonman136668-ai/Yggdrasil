TITLE: DG-1A-CLR2-H183 — Sequential Capability Accumulation Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / DEVELOPMENTAL CAPABILITY ACCUMULATION
BRANCH: dg1a-ar
PARENT: dg1a-clr2-h181-coverage-balanced-context-gated-capability-addition-audit.ice

PURPOSE

H181 established:
a previously absent capability B
can be added to:
a frozen learned capability A

using:

- 48 new daughter cells;
- eight coverage-balanced micro-patches;
- one six-parameter learned context router;
- B-only functional training;
- no A task-output replay;
- approximately 1.50% new active cells;
- approximately 1.68% permanent parameter growth;

while:
preserving A
and:
achieving:
95%
world-level
B competence.

H183 asks:

CAN THE SAME DEVELOPMENTAL MECHANISM
ACCUMULATE ANOTHER NEW CAPABILITY

WITHOUT:
RETRAINING
OR:
REWRITING
A OR B?

Sequence:

learn A
->
add B
->
freeze A+B
->
add C
->
preserve A+B+C.

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

CELLULAR BODY

Fine cognitive scale:

g=.25.

Parent body:

N=3209 cells.

Parent A coefficients:

learned first
and:
then frozen.

Capability-addition substrate:

same H181
48-cell
coverage-balanced
distributed daughter morphology.

Each added capability receives:

48 new daughter cells
+
one:
six-parameter
context router.

No:
existing functional coefficient
may:
change
after:
its capability stage
is frozen.

CAPABILITY CONTEXTS

Three:
separable input contexts

inside:
the unit disk.

A context:

center:
(-0.48, 0.00).

B context:

center:
(+0.34, +0.34).

C context:

center:
(+0.34, -0.34).

Each:

Gaussian sd:
0.20.

Reject:
outside:
the unit disk.

Also enforce:

A:
x <= -0.05.

B:
x >= +0.05
AND:
y >= +0.05.

C:
x >= +0.05
AND:
y <= -0.05.

The contexts:

are:
disjoint
but:
share:
one underlying
cellular input space.

TEACHERS

A,
B,
C:

independent:
smooth nonlinear
learned teachers.

Use:
the accepted H178-H181
smooth teacher family:

random tanh field
+
low-frequency sinusoid.

Teacher parameters:

world-seed deterministic
and:
capability-domain separated.

Students:

receive:
only:
training examples.

No:
teacher parameter
is:
exposed.

STAGE 1 — LEARN A

A functional examples:

768 train.

256 validation.

512 held-out test.

Context-silence examples:

128 coordinates
drawn from:
the union
of:
right-half
B/C context support.

Target:
0.

These examples:

do NOT:
contain:
B or C
teacher outputs.

They teach:
A context silence

without:
teaching:
future capabilities.

Parent A ridge:

alpha=.000625.

After:
stage 1:

freeze:
all:
parent A coefficients.

STAGE 2 — ADD B

B samples:

768 train.

256 validation.

512 held-out test.

Fit:
B router

from:
context identity only.

Positive:
64 B-context coordinates.

Negative:
64 A-context coordinates.

Gate feature map:

[1,x,y,x^2,x*y,y^2].

L2=.01.

Deterministic IRLS.

No:
functional target
enters:
router fitting.

B DAUGHTER MORPHOLOGY

Exact H181
coverage-balanced mechanism.

Coverage geometry:

B training input coordinates only.

Deterministic:
8-center k-means.

Map:
centroids
to:
nearest:
right-half parent sites.

Grow:
eight:
Moore-connected
micro-patches

round-robin

to:
48 total daughter cells.

Within:
each frontier:

choose:
highest:
B residual-score
parent site.

Instantiate:
48 daughter centers

with:
capability-specific
micro-offset domain:

world seed
|
"B"
|
daughter index.

B daughter design:

B router
*
daughter basis.

Fit:
B daughter coefficients

to:
current phenotype
B residual:

y_B
-
f_A(X_B).

Ridge:
0.01.

Freeze:
B daughter coefficients
and:
B router
after:
stage 2.

Evaluate:

A
and:
B

before:
starting C.

STAGE 3 — ADD C

C samples:

768 train.

256 validation.

512 held-out test.

C ROUTER

Positive:

64 C-context coordinates.

Negative:

32 A-context
+
32 B-context
coordinates.

No:
A,
B,
or:
C
functional targets

enter:
router fitting.

Same:
six-feature
logistic model.

L2=.01.

C DAUGHTER MORPHOLOGY

Exact H181
coverage-balanced
48-cell mechanism,

now:
using:
C training input geometry.

Candidate parent sites:

all:
original parent-cell sites
compatible with:
C context:

x>=0,
y<=0.

Coverage:

8 deterministic
k-means centroids

from:
C training coordinates.

Map:
to:
nearest:
eligible
unused-within-C
parent sites.

B and C:

MAY:
select:
the same parent
growth site.

They still create:
distinct:
daughter cells

with:
capability-specific
micro-offset domains.

This directly tests:
shared developmental
spatial reuse

without:
sharing:
functional coefficients.

C fit target:

current frozen
A+B phenotype residual:

y_C
-
[
f_A(X_C)
+
f_B(X_C)
].

Only:
new:
C daughter coefficients
are:
plastic.

A:
frozen.

B:
frozen.

B router:
frozen.

C ridge:
0.01.

After:
stage 3:

freeze:
C daughter coefficients
and:
C router.

PRIMARY CANDIDATE

SEQ48_48

B:
48 daughters.

C:
48 daughters.

Total:
96 new daughter cells.

Two routers:
12 parameters.

No:
functional replay
of:
A or B

during:
C learning.

COMPARATORS

A — SEQ48_48

Primary candidate.

B — SEQ64_64

Same:
coverage-balanced
mechanism

but:
64 daughter cells
for:
B

and:
64 for:
C.

Higher-margin
structure comparator.

C — SEQ48_48_NO_C_GATE

B stage:
same accepted
48-cell
routed addition.

C:
48 coverage-balanced
daughter cells

but:
ungated.

Tests:
whether:
routing remains:
necessary
during:
sequential accumulation.

D — SEQ48_48_RANDOM_C

B:
accepted:
coverage-balanced 48.

C:
random:
8-patch
48-cell morphology

with:
the learned C gate.

Tests:
whether:
coverage balancing
remains:
important
for:
the second addition.

E — GLOBAL_C

After:
accepted B stage,

grow:
one C daughter
at:
every parent site.

Use:
learned C gate.

High-capacity C ceiling.

Not:
a candidate efficient architecture.

No:
A/B retraining.

STAGE METRICS

After A:

- A train / validation / test R^2.

After B:

- A R^2;
- B train / validation / test R^2;
- A loss from:
  pre-B baseline;
- B router metrics;
- B active cells;
- B compute.

After C:

- A R^2;
- B R^2;
- C train / validation / test R^2;
- A loss from:
  pre-C value;
- B loss from:
  pre-C value;
- total A loss
  from:
  stage-1 baseline;
- total B loss
  from:
  stage-2 baseline;
- C router metrics;
- C active cells;
- total added cells;
- total permanent parameters;
- total compute.

JOINT COMPETENCE

After:
stage 3,

a world has:
joint A+B+C competence

iff:

A held-out R^2 >=0.85

AND:

B held-out R^2 >=0.85

AND:

C held-out R^2 >=0.85.

CAPABILITY RETENTION

A retained:

post-C A R^2
within:
0.05
of:
its original:
stage-1 baseline.

B retained:

post-C B R^2
within:
0.05
of:
its:
post-B baseline.

HIBERNATION / REACTIVATION

After:
stage 3:

1.
Hibernate B only:
set:
B daughter contribution
to zero.

Verify:
A and C predictions
return:
to:
their:
B-off
integrated state
exactly.

2.
Reactivate B:
restore:
stored B daughter coefficients.

Verify:
all A/B/C predictions
return:
to:
the integrated state
without:
retraining.

3.
Hibernate C only.

4.
Reactivate C.

Report:
normalized prediction-return
errors
for:
all unaffected
and:
reactivated contexts.

STRUCTURAL REUSE METRICS

Report:

- B growth-site set;
- C growth-site set;
- B/C parent-site Jaccard;
- B/C centroid-set distance;
- fraction of:
  C daughter sites
  whose parent site
  was also:
  a B growth site;
- total distinct parent growth sites
  supporting:
  B or C;
- new daughter cells
  per:
  capability.

This measures:
whether:
different learned capabilities

reuse:
developmental locations

even though:
their mutable coefficients
remain:
separate.

RESOURCE METRICS

Report:

- parent active cells N;
- B daughters;
- C daughters;
- total daughters;
- total active-cell growth fraction;
- routing parameters;
- total permanent added parameters;
- permanent parameter-growth fraction;
- stage-B compute proxy;
- stage-C compute proxy;
- total addition compute proxy;
- capability gain / added cell;
- capability gain / permanent parameter;
- capability gain / compute.

NORTH-STAR TELEMETRY

Capability count:

after A:
1.

after B:
2.

after C:
3.

Permanent active structure:

N
->
N + K_B
->
N + K_B + K_C.

Report:

relative capability multiplier:

3x
from:
the stage-1
single-capability baseline.

Relative active-cell multiplier:

(
N + K_B + K_C
)
/
N.

For:
SEQ48_48:

approximately:
1.0299x.

This is:
not:
a proof
of:
asymptotic scaling.

It is:
the first:
multi-capability
developmental accumulation
measurement.

PRIMARY FACTORIAL

Held-out worlds:

20.

Policies:

5.

Policy evaluations:

100.

PRIMARY ACCEPTANCE SHAPE

H183 supports:
SEQUENTIAL
DEVELOPMENTAL
CAPABILITY ACCUMULATION

if:

1.
Stage-A baseline:

median A held-out R^2 >=0.90.

2.
SEQ48_48
after B:

median B held-out R^2 >=0.90.

3.
SEQ48_48
after B:

>=90%
of worlds

B R^2 >=0.85.

4.
Stage-B A preservation:

median A loss <=0.03.

5.
After C:

median C held-out R^2 >=0.90.

6.
After C:

>=90%
of worlds

C R^2 >=0.85.

7.
After C:
A retention:

median total A loss
from:
stage-1 baseline

<=0.03.

8.
After C:
B retention:

median B loss
from:
post-B baseline

<=0.03.

9.
WORLD-LEVEL
JOINT COMPETENCE:

>=90%
of:
SEQ48_48 worlds

finish:
A,
B,
and:
C

all:
R^2 >=0.85.

10.
WORLD-LEVEL
RETENTION:

>=90%
of worlds

retain:

A within:
0.05
of:
stage-1 baseline

AND:

B within:
0.05
of:
post-B baseline.

11.
GENERALIZATION:

B and C
validation-test gap:

median <=0.05.

B and C
train-test gap:

median <=0.10.

12.
ROUTER QUALITY:

both:
B and C
median context accuracy
>=0.95.

For each router:

positive-context mean activation
>=0.90.

negative-context mean activation
<=0.10.

13.
ACTIVE STRUCTURE:

SEQ48_48
total new active cells:

96.

Growth fraction:

<=3.1%
of:
the original:
3209-cell parent body.

14.
PERMANENT PARAMETERS:

96 daughter coefficients
+
12 gate parameters

<=3.5%
of:
parent coefficient count.

15.
COMPUTE:

SEQ48_48
median total addition compute

<25%
of:
GLOBAL_C
plus:
the accepted stage-B
addition compute.

16.
HIBERNATION / REACTIVATION:

all:
prediction-return
errors

<=1e-10.

17.
ROUTING NECESSITY:

SEQ48_48_NO_C_GATE

must:
show:

either:

median A or B loss
at least:
0.05
worse

than:
SEQ48_48

OR:

joint competence
at least:
10 percentage points
lower.

If:
ungated C also passes,
report:
routing is:
not required
for:
the third capability
under:
these contexts.

18.
COVERAGE VALUE:

SEQ48_48

joint competence

must be:
>=:
SEQ48_48_RANDOM_C

and:

either:
C median R^2
>=0.03
higher

OR:

C R^2 standard deviation
>=20%
lower

unless:
RANDOM_C
also:
already passes:
all:
capability / retention gates.

19.
GLOBAL_C
remains:
the C-capacity ceiling.

STRONG SUPPORT

H183 receives:
STRONG support

if:

all primary gates pass

AND:

SEQ48_48

achieves:
>=95%
world-level
joint A+B+C competence

while:
total active-cell growth
remains:
<3.1%.

MIXED / NEGATIVE CONDITIONS

Treat H183 as:
mixed / negative
if:

- B addition
  cannot:
  reproduce:
  H181 reliability;

- C addition
  requires:
  modifying:
  A or B
  functional coefficients;

- C routing
  materially suppresses:
  C competence;

- adding C
  erodes:
  B even though:
  B coefficients
  are frozen;

- routing parameters
  become:
  a hidden large
  architecture;

- active-cell growth
  scales:
  near-linearly
  with:
  full parent size
  rather than:
  bounded patches;

- hibernation
  of:
  one capability
  destabilizes:
  the others.

NEXT

If H183 succeeds:

next:
CLR3-H184 —
CAPABILITY HIBERNATION / REACTIVATION
AND:
STRUCTURAL REUSE.

Test:

- selective dormancy;
- low-active-compute
  capability switching;
- whether:
  dormant capability cells
  can:
  be reactivated
  without:
  recomputation;
- whether:
  new capability D
  can:
  reuse:
  dormant or:
  overlapping
  developmental structure.

SANITY WORLD SEEDS

20260923290000...

PRIMARY WORLD SEEDS

20260923200000
through:
20260923200019.

Sanity:
NON-EVIDENCE.

No:
context geometry,
teacher family,
sample count,
parent ridge,
B/C daughter count,
k-means rule,
gate feature map,
gate sample count,
gate L2,
daughter ridge,
freeze rule,
or:
acceptance gate

may change
after:
the first held-out H183 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SEQUENTIAL_DEVELOPMENTAL_CAPABILITY_ACCUMULATION

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
