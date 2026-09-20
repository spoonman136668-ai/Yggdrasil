TITLE: DG-1A-CLR3-H186 — Hybrid Role-Reuse + Minimal New-Cell Capability Addition Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / CAPABILITY REUSE / ACTIVE-STRUCTURE EFFICIENCY
BRANCH: dg1a-ar
PARENT: dg1a-clr3-h185-context-gated-role-multiplexed-capability-reuse-audit.ice

PURPOSE

H185 established:

- zero-new-cell C role reuse on selected parent cells
  matches the median competence of adding 48 new C daughters;
- parent role reuse cuts physical active growth in half
  relative to a new 48-cell C population;
- both role reuse and new-cell growth remain limited by a ~70–75%
  world-level joint-reliability tail;
- direct reuse of B-daughter locations fails,
  so capability geometry still matters.

H186 asks:

CAN:
MOST
NEW CAPABILITY STATE

BE STORED:
ON ALREADY-ACTIVE CELLS

WHILE:
A VERY SMALL
NEW-CELL SCAFFOLD

SUPPLIES:
THE MISSING GEOMETRIC DEGREES OF FREEDOM?

Primary candidate:

32 reused parent-role coefficients
+
16 new C daughter cells.

This keeps:
48 C functional coefficients total

but:
adds only:
16 physical C cells.

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT MODEL

Reuse H185 exactly through:

- A learning;
- 48-cell B capability addition;
- context-only B-router accommodation;
- frozen A coefficients;
- frozen B daughter coefficients;
- frozen accommodated B router;
- learned C context router.

No:
A/B functional replay.

C ROLE + NEW-CELL HYBRID

Stage 1:
ROLE SUBSTRATE

Select:
K_role
already-active parent cells

using:
the H185
coverage-balanced
C geometry.

Fit:
C-specific role coefficients

on:
those parent basis functions

under:
the frozen C router.

Stage 2:
RESIDUAL NEW-CELL SCAFFOLD

Compute:
the remaining C training residual

after:
the role-only fit.

Using:
the SAME C training input geometry,

select:
K_new
new daughter growth sites

with:

- deterministic 8-center
  coverage seeds;
- residual-driven
  local frontier expansion;
- role-selected parent sites
  excluded
  from:
  new-cell parent-site selection
  where possible.

Instantiate:
standard:
capability-specific
C daughter centers

at:
those parent sites.

FINAL JOINT C FIT

After:
role sites
and:
new daughter sites

are fixed,

fit:
ALL:

K_role
parent-role columns

plus:

K_new
new-daughter columns

JOINTLY

to:
the original:
current A+B residual

under:
the C context gate.

Thus:

the role-only intermediate fit

is used only:
to identify:
where:
the new-cell scaffold
is most needed.

Final coefficients:

are:
jointly optimized.

No:
A/B coefficient
or:
router
is changed.

POLICIES

A — ROLE32_NEW16

PRIMARY CANDIDATE.

32:
reused parent roles.

16:
new C daughters.

Total C functional coefficients:
48.

New C physical cells:
16.

B — ROLE32_NEW32

32 parent roles.

32 new C daughters.

Total C coefficients:
64.

New C physical cells:
32.

C — ROLE48_NEW16

48 parent roles.

16 new C daughters.

Total C coefficients:
64.

New C physical cells:
16.

D — ROLE48

Exact H185
PARENT_ROLE48.

Zero new C cells.

E — NEW48

Exact H185
NEW_C48.

48 new C cells.

F — GLOBAL_PARENT_ROLE

H185
global parent-role
capacity ceiling.

SITE SELECTION DETAILS

ROLE SITES

Use:
the exact H185/H181
coverage-balanced rule:

- 8 deterministic k-means centroids
  from:
  C training coordinates;
- map:
  to:
  right-half parent cells;
- round-robin:
  connected growth;
- residual score:
  from:
  current A+B C residual.

NEW-CELL SITES

After:
role-only intermediate fit:

residual_2
=
y_C
-
[
f_A
+
f_B
+
f_C_role_intermediate
].

Compute:
residual score
for:
all parent cells.

Use:
the same:
8 deterministic
C input-coverage centroids.

Map:
to:
nearest:
right-half parent sites

that:
are NOT:
already:
role sites

when:
an unused alternative exists.

Grow:
connected
new-cell micro-patches

round-robin

using:
residual_2 score.

If:
a frontier can only:
continue through:
a role-selected site,

it may:
traverse:
that site

but:
must choose:
an unused parent site
for:
the actual daughter
when:
available.

No:
C validation / test
target
enters:
selection.

C ROUTER

Exact H185:

C-positive.

A+B-negative.

Six-feature logistic gate.

Context coordinates only.

PRIMARY METRICS

After C:

- A R^2;
- B R^2;
- C train / validation / test R^2;
- A loss;
- B loss;
- joint A+B+C competence;
- A/B retention;
- C router metrics.

RESOURCE METRICS

- parent physical cells;
- B daughter cells;
- new C daughter cells;
- total physical active cells;
- active-cell growth fraction;
- reused role coefficient count;
- new C daughter coefficient count;
- total C functional coefficient count;
- total added permanent parameters;
- parameter-growth fraction;
- role-site / new-site overlap;
- role-site / B-site overlap;
- new-site / B-site overlap;
- C compute proxy;
- total sequential compute.

PRIMARY FACTORIAL

Held-out worlds:
20.

Policies:
6.

Evaluations:
120.

PRIMARY ACCEPTANCE SHAPE

H186 supports:
HYBRID
ROLE-REUSE
+
MINIMAL NEW-CELL
CAPABILITY ADDITION

if:

1.
Stage-B baseline:
median B held-out R^2 >=0.90.

2.
Stage-B reliability:
>=90%
worlds
B>=0.85.

3.
ROLE32_NEW16:
median C held-out R^2 >=0.90.

4.
ROLE32_NEW16:
>=90%
worlds
C>=0.85.

5.
Median A loss <=0.03.

6.
Median B loss <=0.03.

7.
WORLD JOINT COMPETENCE:

>=90%
of:
ROLE32_NEW16 worlds

finish:
A,
B,
C
all:
R^2 >=0.85.

8.
WORLD A+B RETENTION:

>=90%
retain:
A within 0.05
of:
stage-A baseline

AND:
B within 0.05
of:
post-B baseline.

9.
GENERALIZATION:

C validation-test gap <=0.05.

C train-test gap <=0.10.

10.
ACTIVE-CELL GROWTH:

new C physical cells:
16.

Total physical cells
after:
A+B+C:

N
+
48 B daughters
+
16 C daughters.

Growth fraction
relative to:
original parent:

<=2.0%.

11.
PERMANENT PARAMETER GROWTH:

48 B coefficients
+
32 C parent-role coefficients
+
16 C daughter coefficients
+
12 gate parameters

<=3.5%
of:
parent coefficient count.

12.
HYBRID VALUE:

ROLE32_NEW16

joint competence

must exceed:
ROLE48

by:
>=10 percentage points

OR:
reach:
>=90%
when:
ROLE48 remains below.

13.
ACTIVE-STRUCTURE VALUE:

ROLE32_NEW16

must:
match or exceed:
NEW48
joint competence

while:
using:
at most:
one-third
as many:
new C physical cells.

16 versus 48.

14.
ROLE32_NEW32
and:
ROLE48_NEW16

are:
diagnostic margins.

If:
only:
the higher-memory
or:
higher-new-cell
hybrid passes,

report:
the minimum:
reliable hybrid point.

15.
COMPUTE:

ROLE32_NEW16
median total compute

<25%
of:
GLOBAL_PARENT_ROLE.

16.
HIBERNATION / REACTIVATION:

C contribution
can:
be disabled
and:
restored

with:
prediction-return
errors
<=1e-10.

17.
GLOBAL_PARENT_ROLE
remains:
C role-capacity ceiling.

STRONG SUPPORT

H186 receives:
STRONG support

if:

ROLE32_NEW16
passes:
all primary gates

AND:
joint A+B+C competence
>=95%.

MIXED / NEGATIVE CONDITIONS

Treat H186 as:
mixed / negative
if:

- 16 new cells
  do not:
  close:
  the role-reuse reliability tail;

- hybrid fitting
  increases:
  A/B interference;

- reliable performance
  still requires:
  48 new C cells;

- role-state memory
  plus:
  new-cell growth
  provides:
  no advantage
  over:
  one mechanism alone.

NEXT

If H186 succeeds:

proceed to:
CLR3-H187 —
HIBERNATION / ACTIVE-COMPUTE SCALING.

If H186 fails:

the next architectural test
should:
share:
basis state
between:
capabilities

or:
develop:
context-dependent
internal basis transformations,

rather than:
simply:
adding:
more role coefficients
or:
new cells.

SANITY WORLD SEEDS

20260923590000...

PRIMARY WORLD SEEDS

20260923500000
through:
20260923500019.

Sanity:
NON-EVIDENCE.

No:
context geometry,
teacher,
B substrate,
router rule,
role count,
new-cell count,
site-selection rule,
ridge,
or:
acceptance gate

may change
after:
the first held-out H186 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_HYBRID_ROLE_REUSE_MINIMAL_NEW_CELL_CAPABILITY_ADDITION

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-SANITY PROVENANCE RECOVERY 01 — EXACT PARENT SUBSTRATE RESTORED

DATE:
2026-09-20.

STATUS:
RECORDED BEFORE H186 SANITY OR PRIMARY EXECUTION.

BACKGROUND

The transient sandbox Python files used by:
H183,
H184,
and:
H185

were no longer present
when:
H186 implementation began.

The committed .ice specifications
remained intact,
but:
the exact transient code path
was temporarily unavailable.

RECOVERY

The prior execution history
was inspected

and:
the original source commands
for:

- H178 capability substrate;
- H181 deterministic k-means routine;
- H183 sequential capability substrate;
- H185 role-reuse wrapper

were recovered.

A semantic parent chain
was rebuilt from:
those exact prior source commands.

H186 parent substrate:

h183_seq_caps_v3.py

plus:
the recovered:
H178 / H181 helper semantics.

PARENT REPRODUCTION CHECK

Before:
any H186 sanity seed
was executed,

the rebuilt parent chain
was run on:
accepted H185 sanity seed:

20260923490000.

H186 control:

ROLE48

was compared against:
accepted H185:

PARENT_ROLE48.

H186 control:

NEW48

was compared against:
accepted H185:

NEW_C48.

The following fields
match exactly
at:
floating-point output precision:

- postB_B_r2;
- postC_A_r2;
- postC_B_r2;
- postC_C_r2;
- A_total_loss;
- B_loss_after_C;
- joint_ABC.

Example:

PARENT_ROLE48 / ROLE48:

postB_B_r2 =
0.8975810028292733.

postC_C_r2 =
0.9177317158342284.

A_total_loss =
3.030536145387508e-05.

NEW_C48 / NEW48:

postC_C_r2 =
0.9155105882475112.

Thus:

H186 now continues:
the accepted H185
scientific substrate

rather than:
an approximate reconstruction.

NON-EVIDENCE

All:
earlier approximate
parent-reconstruction trials

are:
NON-EVIDENCE

and:
cannot enter:
H186 acceptance.

H186 SCIENTIFIC STATUS

Sanity:
NOT STARTED
at:
this provenance note.

Primary:
NOT STARTED.

No:
H186 scientific variable
or:
acceptance gate
was changed.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — HYBRID ROLE-REUSE + MINIMAL NEW-CELL HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H186 HELD-OUT PRIMARY EXECUTION.

FINAL H186 SANDBOX HARNESS

File:

h186_hybrid_role_v1.py

SHA-256:

5d400ebd2f6f9686a201adfa1e323fc3593ce9ac6711bd349e52799efa3635b8.

PARENT SUBSTRATE

Recovered:
the exact prior
H178 / H183 / H185
scientific semantics

from:
the original
execution-source history.

Parent validation:

H186
ROLE48
and:
NEW48

reproduce:
accepted H185
PARENT_ROLE48
and:
NEW_C48

exactly
on:
accepted H185
sanity seed:
20260923490000.

Thus:

H186 scientific differences
are limited to:
the preregistered
hybrid C substrate.

HYBRID MECHANICS

ROLE32_NEW16:

1.
select:
32 reused parent-role sites

with:
the exact H185
coverage-balanced
C geometry;

2.
fit:
an intermediate
32-role
C function

only to:
identify:
remaining residual structure;

3.
compute:
residual_2;

4.
select:
16 fresh
C daughter sites

from:
the same:
8-center
C coverage geometry

using:
residual_2
for:
local frontier scoring;

5.
exclude:
role-selected
parent sites
from:
actual new-daughter
site occupation

when:
an unused alternative exists;

6.
allow:
role sites
to:
act only as:
connected-growth
traversal locations
if needed;

7.
instantiate:
standard:
C-specific
micro-offset daughter centers;

8.
fit:
all:
32 reused role coefficients
+
16 new daughter coefficients

JOINTLY

to:
the original:
A+B
C residual.

The intermediate:
role-only fit

does NOT:
define:
final coefficients.

Parent A,
B daughter coefficients,
and:
the accommodated B router

remain:
frozen.

C router:

exact H185.

No:
A/B functional replay.

POLICIES

ROLE32_NEW16.

ROLE32_NEW32.

ROLE48_NEW16.

ROLE48.

NEW48.

GLOBAL_PARENT_ROLE.

SANITY

Disjoint family:

20260923590000
and:
20260923590001.

2 worlds.

6 policies.

12 evaluations.

Accepted sanity-output SHA-256:

597c8a0a411c2296063d8fe52291d66efe75f779ae46ae3deefcfc79aa21a151.

Mechanical checks:

- exact 6 policies / sanity world;
- ROLE32_NEW16:
  32 reused role coefficients;
- ROLE32_NEW16:
  16 new C physical cells;
- ROLE32_NEW32:
  32 new C cells;
- ROLE48_NEW16:
  16 new C cells;
- ROLE48:
  zero new C cells;
- NEW48:
  48 new C cells;
- parent A/B state:
  frozen;
- hibernation / reactivation:
  exact zero error;
- accepted primary family:
  no prior sandbox use detected.

NON-EVIDENCE SIGNAL

World:
20260923590000.

Parent stage-B:

B R^2:
approximately 0.7787.

Thus:
joint competence
is already impossible
before:
C addition.

C results:

ROLE48:
approximately 0.9705.

NEW48:
approximately 0.9697.

ROLE32_NEW16:
approximately 0.9842.

ROLE32_NEW32:
approximately 0.9906.

ROLE48_NEW16:
approximately 0.9850.

World:
20260923590001.

Stage-B B R^2:
approximately 0.9687.

C results:

ROLE48:
approximately 0.9417.

NEW48:
approximately 0.9452.

ROLE32_NEW16:
approximately 0.9740.

ROLE32_NEW32:
approximately 0.9776.

ROLE48_NEW16:
approximately 0.9742.

Thus:

inside:
the disjoint sanity pair,

a small:
fresh geometric scaffold

improves:
C competence

relative to:
role-only
and:
new-only
48-state references

without:
materially increasing:
A/B interference.

These values are:

NON-EVIDENCE.

No:

- role count;
- new-cell count;
- residual-stage rule;
- site-selection rule;
- gate;
- teacher;
- ridge;
- acceptance gate

was changed
from:
sanity outcomes.

PRIMARY FAMILY

20260923500000..20260923500019.

20 held-out worlds.

6 policies.

120 evaluations.

H186 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H186 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
