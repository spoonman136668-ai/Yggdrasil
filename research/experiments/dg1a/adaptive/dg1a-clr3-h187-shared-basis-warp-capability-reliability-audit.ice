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


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — SHARED BASIS-WARP HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H187 HELD-OUT PRIMARY EXECUTION.

FINAL H187 SANDBOX HARNESS

File:

h187_basis_warp_v1.py

SHA-256:

bdc1ac91733e4e8f3cb2b362f7daa23978d9b27013206bdad3f0ccdbd0ba070a.

PARENT SUBSTRATE

Exact H186 / H183
accepted substrate.

No:
cell count,
gate,
coverage morphology,
C hybrid,
teacher,
context geometry,
or:
acceptance rule
changes.

B BASIS WARP

Physical B daughter centers:

remain:
exactly:
the H181
coverage-balanced
48-cell geometry.

The B basis
evaluates:
one:
shared,
bounded
5-parameter
input warp

only when:
the accepted B gate
is active.

Parameters:

log_sx,
log_sy,
theta,
tx,
ty.

Bounds:

log scales:
[-0.40,+0.40].

theta:
[-20,+20] degrees.

translation:
each:
[-0.08,+0.08].

Warp fitting:

B training coordinates
+
B training targets only.

No:
validation,
held-out,
A functional target,
C data

enters:
warp optimization.

Coordinate search:

identity start.

5 deterministic sweeps.

Initial steps:

0.20,
0.20,
10 degrees,
0.04,
0.04.

Step sizes:
halve
after:
each sweep.

At:
each candidate warp,

B daughter coefficients
are:
ridge-refit

with:
alpha=.01.

The chosen warp
and:
B coefficients

are:
frozen
before:
C appears.

SANITY

Disjoint family:

20260923690000
and:
20260923690001.

2 worlds.

6 policies.

12 evaluations.

Accepted sanity-output SHA-256:

6db6fbfd7c0b3857fa15311300215d65fc999fe8a21036ae5566ef649697daa8.

Mechanical checks:

- exact 6 policies / world;
- B physical centers:
  unchanged
  by:
  warp;
- B active-cell count:
  unchanged;
- B gate:
  exact parent;
- no:
  held-out / validation
  leakage;
- C hybrid:
  exact H186;
- hibernation / reactivation:
  exact.

NON-EVIDENCE SIGNAL

World:
20260923690000.

BASE48
post-B R^2:

approximately:
0.8587.

WARP48:

approximately:
0.9189.

WARP32:

approximately:
0.9194.

World:
20260923690001.

BASE48:

approximately:
0.8925.

WARP48:

approximately:
0.9328.

WARP32:

approximately:
0.9433.

Thus:

the shared basis warp
can:
materially improve
B competence

without:
adding:
physical cells

inside:
sanity.

Generalization:

validation R^2
remains:
close to:
held-out R^2

in:
both sanity worlds.

BOUNDARY DIAGNOSTIC

One:
log-scale parameter

lands:
near:
the frozen:
0.40
absolute bound

in:
each sanity world.

Representative:

-0.3875
or:
+/-0.3875

on:
one axis.

This is:
NON-EVIDENCE.

No:
warp bound,
warp regularizer,
coordinate-search schedule,
cell count,
router,
or:
acceptance gate

is changed.

The held-out primary
will determine:

whether:
the gain
is:
robust

or:
depends:
too strongly
on:
the search boundary.

PRIMARY FAMILY

20260923600000..20260923600019.

20 held-out worlds.

6 policies.

120 evaluations.

H187 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H187 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — SHARED BASIS-WARP CAPABILITY RELIABILITY

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-POSITIVE BY PREREGISTERED GATES / MAJOR POSITIVE ACTIVE-STRUCTURE RESULT.

FINAL H187 HARNESS SHA-256

bdc1ac91733e4e8f3cb2b362f7daa23978d9b27013206bdad3f0ccdbd0ba070a.

ACCEPTED PRIMARY MATRIX SHA-256

165051ddce2d9823826262aa6950a7fd31b3ae726ce86a2a5b7b054d40867fac.

ACCEPTED PRIMARY FAMILY

20260923600000..20260923600019.

PRIMARY MATRIX

20 held-out worlds.

6 policies.

120 evaluations.

Validation:

- exact 20 primary seeds;
- exact 6 policies / seed;
- no duplicate seed x policy rows;
- no missing evaluations;
- no post-primary warp tuning.

BASE48 FAMILY DIFFICULTY

BASE48_HYBRID_C:

median post-B B R^2:

approximately:
0.94536.

Worlds:
B>=0.85:

18 / 20
=
90%.

Thus:

the unwarped 48-cell
B substrate

already:
lands:
exactly
on:
the frozen:
90%
reliability threshold

inside:
this H187 family.

PRIMARY CANDIDATE

WARP48_HYBRID_C.

POST-B B CAPABILITY

Median B held-out R^2:

approximately:
0.97485.

Frozen target:
>=0.90.

PASS.

Worlds:
B>=0.85:

19 / 20
=
95%.

Frozen target:
>=90%.

PASS.

The shared:
five-parameter
basis warp

therefore:

raises:
B world reliability

from:
90%

to:
95%

with:

ZERO
additional physical B cells.

A PRESERVATION AT B STAGE

Median:
post-B A R^2

BASE48:

approximately:
0.99691.

WARP48:

approximately:
0.99610.

Difference:

approximately:
-0.00081.

Frozen allowance:

no more than:
0.01
median degradation.

PASS.

B GENERALIZATION

Median:
validation-test gap:

approximately:
0.00268.

Median:
train-test gap:

approximately:
0.00413.

PASS.

WARP MAGNITUDE

Median:

|log_sx|:
approximately:
0.1875.

|log_sy|:
approximately:
0.11875.

|theta|:
approximately:
4.06 degrees.

translation norm:
approximately:
0.0225.

Frozen limits:

0.30,
0.30,
15 degrees,
0.08.

PASS.

Maximum:
absolute log-scale
inside:
the accepted primary

does approach:
0.3875

in:
some worlds,

but:

the MEDIAN
learned warp

is:
well inside:
the frozen bounds.

Thus:

the primary gain
is NOT:
a population-wide
boundary-saturation artifact.

AFTER C — H186 HYBRID

WARP48_HYBRID_C:

median C held-out R^2:

approximately:
0.95225.

Worlds:
C>=0.85:

19 / 20
=
95%.

PASS.

Median A total loss:

approximately:
0.00464.

Median B loss
after C:

approximately:
0.00105.

A+B retention:

19 / 20
=
95%.

PASS.

JOINT A+B+C

WARP48_HYBRID_C:

18 / 20
=
90%.

Frozen target:
>=90%.

PASS
at:
the boundary.

Failure decomposition:

one world:
B remains:
below:
0.85
after:
the warp.

one different world:
C remains:
below:
0.85.

All:
other:
18 worlds

finish:
A,
B,
C
jointly competent.

ACTIVE STRUCTURE

WARP48_HYBRID_C:

48 B physical daughters
+
16 C physical daughters.

Total:
64
new physical cells.

Growth fraction:

approximately:
1.994%.

Frozen ceiling:
<=2%.

PASS.

PERMANENT PARAMETERS

48 B coefficients
+
5 B warp parameters
+
32 C reused roles
+
16 C daughter coefficients
+
12 router parameters

=
113
added parameters.

Growth fraction:

approximately:
3.521%.

Frozen ceiling:
<=3.7%.

PASS.

COMPUTE

Median:
WARP48_HYBRID_C
total compute:

approximately:
101.5 million
proxy units.

GLOBAL_B_GLOBAL_C:

approximately:
4.09 billion.

Ratio:

approximately:
2.48%.

Frozen ceiling:
<25%.

PASS.

HIBERNATION / REACTIVATION

Exact:

maximum return errors:

0.

PASS.

PREREGISTERED WARP-VALUE COMPARATOR GATE

BASE48
world B>=0.85:

90%.

WARP48:

95%.

Absolute improvement:

+5 percentage points.

Frozen comparator gate required:

>=10-point improvement

OR:

reach:
>=90%

when:
BASE remains below:
90%.

Because:
BASE lands:
exactly at:
90%,

neither:
formal branch
is satisfied.

FAIL.

This is:
a comparator-effect-size miss,

not:
an absolute:
B reliability failure.

All:
absolute:
B quality / reliability
gates pass.

ZERO-NEW-C-CELL RESULT

WARP48_ROLE48_C:

uses:

48:
B physical daughter cells

and:

ZERO:
new C physical cells.

Capability C
is stored as:
48 context-gated
role coefficients

on:
already-active
parent cells.

Results:

median B R^2:
approximately:
0.97485.

median C R^2:
approximately:
0.94104.

B>=0.85:

95%.

C>=0.85:

95%.

Joint A+B+C:

18 / 20
=
90%.

A+B retention:

95%.

Thus:

after:
the B basis reliability
improvement,

the:
16-new-C-cell
hybrid scaffold

is NO LONGER REQUIRED

to:
reach:
the frozen:
90%
three-capability
joint threshold.

This is:
the strongest
H187 architectural result.

THREE CAPABILITIES

A,
B,
C

can:
reach:
90%
joint world competence

with:

only:
48
new physical cells

beyond:
the original:
3209-cell
A body.

Physical active-cell growth:

approximately:
1.496%.

B:
uses:
the 48 physical daughters.

C:
uses:
context-gated
role state

on:
already-active
parent cells.

WARP32 DIAGNOSTIC

WARP32_HYBRID_C:

32:
B physical daughters.

16:
C physical daughters.

Total:
48
new physical cells.

Physical growth:

approximately:
1.496%.

Median B:

approximately:
0.97392.

B>=0.85:

95%.

Median C:

approximately:
0.95229.

C>=0.85:

95%.

Joint:

90%.

Thus:

a different:
48-physical-cell
allocation

also:
reaches:
the:
90%
three-capability
joint threshold.

This independently supports:

the result is:
not tied
to:
one exact:
48-B / 0-C
physical allocation.

PRIMARY GATE REVIEW

PASS:

1.
Base-family median competence.

2.
Warped B median competence.

3.
Warped B world reliability.

4.
A preservation.

5.
B generalization.

7.
Warp magnitude.

8.
C median competence.

9.
C world reliability.

10.
Joint A+B+C competence.

11.
A+B retention.

12.
Active structure.

13.
Permanent parameter growth.

14.
Compute.

15.
Hibernation / reactivation.

16.
WARP48_ROLE48_C diagnostic:
ZERO new C cells
also reaches:
90%
joint competence.

17.
Global capacity ceiling.

FAIL:

6.
Preregistered:
>=10-point
relative B-reliability improvement.

Observed:
+5 points

because:
BASE48
was already:
90%
on:
this family.

STRONG SUPPORT:

FAIL.

Reason:

joint competence:

90%

not:
the frozen:
95%
strong-support threshold.

FINAL INTERPRETATION

H187 is:

MIXED-POSITIVE
under:
the exact:
preregistered gate set.

Architecturally:

the result is:
a major positive
for:
the Yggdrasil North Star.

A:
five-parameter
shared basis transformation

raises:
the reliability
of:
a fixed:
small:
B cellular population

without:
adding:
physical structure.

That improved B substrate
then allows:
capability C

to live:
as:
context-gated
role state

on:
already-active
parent cells

while:
the complete:
A+B+C phenotype

reaches:
90%
world-level
joint competence.

Physical active structure:

one:
3209-cell
parent body

plus:
only:
48:
physical daughter cells

supports:
three:
learned capabilities.

Relative:
active-cell multiplier:

approximately:
1.01496x

for:
a:
3x
capability-count
phenotype

inside:
this synthetic
three-capability
experiment.

This does NOT:
prove:
asymptotic
sublinear scaling.

But:

it is:
direct:
proof-of-mechanism

for:

CAPABILITY GROWTH
WITHOUT:
PROPORTIONAL
ACTIVE-STRUCTURE GROWTH.

NEXT

Proceed to:

CLR3-H188 —
HIBERNATION /
ACTIVE-COMPUTE
SCALING AUDIT.

Do NOT:

optimize:
the remaining:
5%
B tail
or:
5%
C tail

before:
measuring:
the North-Star
resource behavior.

H188 should:

store:
A+B+C

using:
the accepted:
low-active-structure
H187 phenotype

and measure:

- one-capability active mode;
- two-capability active mode;
- all-capability active mode;
- active cell / active role count;
- actual forward compute proxy;
- stored memory;
- switch / wake cost;
- exact dormancy / reactivation;
- whether:
  dormant capability state
  can remain:
  stored
  without:
  remaining:
  computationally active.

H187 DOES NOT AUTHORIZE

- production use;
- live model modification;
- biological claims;
- whole-model retraining;
- canonical scientific claims;
- STAB-18-R1 execution.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
