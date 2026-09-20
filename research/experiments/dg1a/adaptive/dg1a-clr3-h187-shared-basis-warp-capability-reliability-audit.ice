TITLE: DG-1A-CLR3-H187 — Context-Conditioned Shared Basis-Warp Capability Reliability Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / CAPABILITY REUSE / BASIS EFFICIENCY
BRANCH: dg1a-ar
PARENT: dg1a-clr3-h186-hybrid-role-reuse-minimal-new-cell-audit.ice

PURPOSE

H186 established:

- capability C can reach 95% world-level competence
  with:
  32 reused parent-role coefficients
  +
  only 16 new physical C cells;

- total A+B+C physical active-cell growth can remain near 2%;

- joint A+B+C reliability nevertheless remains 75%
  because the inherited stage-B addition falls below B R^2 0.85
  in 4 / 20 worlds;

- increasing C role state or C physical cells
  does not repair that tail.

Therefore:

the next bottleneck is:
B FUNCTIONAL BASIS EFFICIENCY,

not:
C structure.

H187 asks:

CAN THE SAME
48 PHYSICAL B DAUGHTER CELLS

be made more reliable
by giving the entire B daughter population

ONE SMALL
SHARED
CONTEXT-CONDITIONED
BASIS TRANSFORMATION

learned from:
B training data,

without:

- adding physical B cells;
- replaying A functional targets;
- materially expanding routing state?

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT MODEL

Reuse H186 exactly except:
the B daughter basis may be transformed
for the declared warp policies.

A:

same H186/H185 learned parent phenotype.

A coefficients:
frozen after stage A.

B:

same 48-cell
H181 coverage-balanced
distributed morphology.

Same:
six-parameter learned B context router.

C:

same H186
ROLE32_NEW16
hybrid mechanism
for sequential tests.

No:
A/B functional replay
during:
C addition.

SHARED B BASIS WARP

The 48 physical B daughter centers:

remain:
the exact H181
coverage-balanced daughter centers.

No:
cell is moved physically.

Instead:

only when:
the B router is active,

the B daughter basis
evaluates input coordinates through
one shared 2D affine-like warp.

Let:

u =
[x, y]^T.

Let:
c_B

be:
the mean
of:
B training input coordinates.

Warp parameters:

q =
(
log_sx,
log_sy,
theta,
tx,
ty
).

Define:

S =
diag(
exp(log_sx),
exp(log_sy)
).

R(theta) =
2D rotation.

Warped coordinate:

u'
=
c_B
+
R(theta)
S
(
u - c_B
)
+
[tx, ty]^T.

The physical daughter centers
remain unchanged.

The B daughter RBF design
uses:

phi(
u',
daughter_center
).

Thus:

one:
five-parameter
shared transform

changes:
the effective receptive geometry
of:
all 48 B daughter cells

without:
adding:
new active cells.

ROUTING

B contribution:

B_gate(u)
*
Phi_B_warp(u)
*
w_B.

Outside:
B context,

the accepted B gate
suppresses:
the entire:
warped B substrate.

Therefore:

the warp is:
context-conditioned
through:
the existing learned router.

WARP PARAMETER BOUNDS

log_sx,
log_sy:

[-0.40, +0.40].

Equivalent scales:

approximately:
0.67..1.49.

theta:

[-20 degrees, +20 degrees].

tx,
ty:

[-0.08, +0.08].

These bounds:

prevent:
the warp
from:
becoming:
an arbitrary global remapping.

They are:
frozen before sanity.

WARP FIT

Use:

B TRAINING INPUTS
and:
B TRAINING TARGETS only.

No:
B validation,
B held-out,
A functional target,
C data

enters:
warp fitting.

For:
a proposed q:

1.
construct:
the gated warped
48-column
B daughter design;

2.
fit:
B daughter coefficients
by:
ridge alpha=0.01

to:
the frozen A residual:

y_B
-
f_A(X_B);

3.
score:
training residual MSE
+
warp regularization.

Warp regularization:

0.001
*
[
log_sx^2
+
log_sy^2
+
(theta / 20deg)^2
+
(tx / 0.08)^2
+
(ty / 0.08)^2
].

DETERMINISTIC COORDINATE SEARCH

Start:
identity warp.

Initial steps:

log scale:
0.20.

theta:
10 degrees.

translation:
0.04.

For:
each coordinate,
evaluate:
current,
plus step,
minus step

within:
the frozen bounds.

Choose:
the lowest objective.

Tie:
smaller absolute parameter magnitude,
then:
negative-before-positive
deterministic order.

Sweep:
all five coordinates.

After:
each full sweep:

halve:
all step sizes.

Run:
5 sweeps total.

Final:
q
and:
ridge coefficients

are:
the B learned state.

No:
validation-based stopping.

NO PHYSICAL CELL CHANGE

Warp fitting:

does NOT:
change:
B daughter center positions.

does NOT:
add:
new cells.

does NOT:
alter:
A coefficients.

does NOT:
alter:
gate feature count.

POLICIES

A — BASE48_HYBRID_C

Exact H186:
standard 48-cell B
+
ROLE32_NEW16 C.

B — WARP48_HYBRID_C

PRIMARY CANDIDATE.

Same:
48 B physical cells
+
5 shared B warp parameters
+
same:
ROLE32_NEW16 C hybrid.

C — WARP48_ROLE48_C

Same:
warped B substrate.

C:
ROLE48
zero-new-C-cell reference.

Tests:
whether better B reliability
alone
raises:
three-capability joint competence
without:
the 16-cell C scaffold.

D — WARP32_HYBRID_C

32:
coverage-balanced B daughter cells

with:
the same:
5-parameter
shared B warp.

C:
ROLE32_NEW16.

Lower-active-structure diagnostic.

E — WARP48_NEW48_C

Warped B.

C:
exact NEW48 reference.

F — GLOBAL_B_GLOBAL_C

High-capacity reference.

Global B daughter basis
plus:
global C role / daughter ceiling.

Not:
a candidate efficient architecture.

PRIMARY METRICS

B stage:

- A baseline R^2;
- B train / validation / test R^2;
- B world competence;
- B gate quality;
- fitted warp parameters;
- warp objective;
- B daughter coefficient RMS;
- effective B input-coverage metrics
  after warp;
- active B cell count;
- B permanent parameters;
- B compute proxy.

After C:

- A R^2;
- B R^2;
- C train / validation / test R^2;
- A loss;
- B loss;
- C competence;
- joint A+B+C competence;
- A+B retention;
- total physical active cells;
- permanent parameter growth;
- total compute;
- hibernation / reactivation.

PRIMARY FACTORIAL

Held-out worlds:
20.

Policies:
6.

Evaluations:
120.

PRIMARY ACCEPTANCE SHAPE

H187 supports:
SHARED
CONTEXT-CONDITIONED
BASIS WARPING

if:

1.
BASE48_HYBRID_C
reproduces:
the H186-family difficulty:

median B R^2 >=0.90.

2.
WARP48_HYBRID_C:

median post-B
B held-out R^2 >=0.90.

3.
WARP48_HYBRID_C:

>=90%
of worlds
finish:
post-B
B R^2 >=0.85.

This is:
the decisive inherited-tail gate.

4.
WARP48_HYBRID_C
does NOT:
degrade:
median post-B A R^2

by:
>0.01
relative to:
BASE48_HYBRID_C.

5.
B generalization:

median:
B validation-test gap <=0.05.

B train-test gap <=0.10.

6.
WARP VALUE:

world B>=0.85
rate

must improve:
by:
>=10 percentage points

over:
BASE48_HYBRID_C

OR:
reach:
>=90%
when:
BASE remains below.

7.
WARP MAGNITUDE:

median:
abs(log_sx),
abs(log_sy)
<=0.30.

median:
abs(theta)
<=15 degrees.

median:
sqrt(tx^2+ty^2)
<=0.08.

This prevents:
success
from:
living only
at:
the search boundary.

8.
AFTER C:

WARP48_HYBRID_C
median C R^2 >=0.90.

9.
AFTER C:

>=90%
worlds
C R^2 >=0.85.

10.
JOINT A+B+C COMPETENCE:

>=90%
of:
WARP48_HYBRID_C worlds

finish:
A,
B,
C
all:
R^2 >=0.85.

11.
A+B RETENTION:

>=90%
retain:
A within:
0.05
of:
stage-A baseline

AND:
B within:
0.05
of:
post-B warped baseline.

12.
ACTIVE STRUCTURE:

WARP48_HYBRID_C

uses:
48 B daughters
+
16 C daughters.

Total physical growth:
<=2.0%.

No:
extra physical cell
is introduced
by:
the basis warp.

13.
PERMANENT PARAMETER GROWTH:

48 B coefficients
+
5 B warp parameters
+
32 C roles
+
16 C daughter coefficients
+
12 router parameters

<=3.7%
of:
parent coefficient count.

14.
COMPUTE:

median total compute
<25%
of:
GLOBAL_B_GLOBAL_C.

15.
HIBERNATION / REACTIVATION:

prediction-return errors
<=1e-10.

16.
WARP48_ROLE48_C diagnostic:

if:
it also reaches:
>=90%
joint A+B+C competence,

report:
the 16 new C cells
are no longer required
after:
B reliability improves.

17.
GLOBAL_B_GLOBAL_C
remains:
capacity ceiling.

STRONG SUPPORT

H187 receives:
STRONG support

if:

WARP48_HYBRID_C

achieves:
>=95%
post-B B competence

AND:
>=95%
joint A+B+C competence

with:
<=2%
physical active growth.

MIXED / NEGATIVE CONDITIONS

Treat H187 as:
mixed / negative
if:

- warp training overfits:
  B training data;

- B world reliability
  remains:
  below 90%;

- useful warps
  consistently hit:
  parameter bounds;

- the warp improves:
  B
  but:
  destabilizes:
  A or C;

- joint reliability
  remains:
  dominated by:
  a different tail;

- five shared parameters
  provide:
  no reliability value.

NEXT

If H187 succeeds:

proceed to:
CLR3-H188 —
HIBERNATION / ACTIVE-COMPUTE SCALING.

If H187 fails:

test:
shared:
context-conditioned
basis-factor state

or:
low-rank:
feature reuse
across:
capabilities

rather than:
adding:
more physical cells.

SANITY WORLD SEEDS

20260923690000...

PRIMARY WORLD SEEDS

20260923600000
through:
20260923600019.

Sanity:
NON-EVIDENCE.

No:
cell budget,
context geometry,
warp family,
warp bounds,
warp objective,
coordinate-search schedule,
router,
C hybrid,
ridge,
or:
acceptance gate

may change
after:
the first held-out H187 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_CONTEXT_CONDITIONED_SHARED_BASIS_WARP_CAPABILITY_RELIABILITY

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
