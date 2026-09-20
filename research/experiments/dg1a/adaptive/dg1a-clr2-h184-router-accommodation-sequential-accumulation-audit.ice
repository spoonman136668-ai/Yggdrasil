TITLE: DG-1A-CLR2-H184 — Context-Only Router Accommodation for Sequential Capability Accumulation
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / DEVELOPMENTAL CAPABILITY ACCUMULATION
BRANCH: dg1a-ar
PARENT: dg1a-clr2-h183-sequential-capability-accumulation-audit.ice

PURPOSE

H183 established:
A -> B -> C sequential capability accumulation works in median
with only 96 new daughter cells and 12 routing parameters,
but world-level joint A+B+C competence is 80%, below the 90% gate.

The main mechanism signal:
B's router, trained before C existed,
has median activation ~0.174 on future C-context inputs.

H184 asks:

CAN:
ROUTING-ONLY
developmental accommodation

raise:
joint A+B+C reliability

WITHOUT:
changing:
A coefficients,
B daughter coefficients,
cell budget,
or:
functional targets?

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT MODEL

Reuse H183 exactly:

- g=.25;
- N=3209;
- same A/B/C contexts and teachers;
- same A silence training;
- same 48-cell H181 coverage-balanced daughter mechanism;
- same six-feature logistic gates;
- same daughter ridge;
- same hibernation/reactivation;
- same frozen A/B functional coefficients after their stages.

STAGE A

Exact H183.

STAGE B

Exact H183:

- learn B with 48 daughters;
- fit B gate using B-positive / A-negative context coordinates;
- freeze B daughters.

NEW ROUTER-ACCOMMODATION STEP

When:
C context becomes available,

BEFORE:
learning C functional outputs,

refit:
B router ONLY.

Positive:
64 B-context coordinates.

Negative:
32 A-context coordinates
+
32 C-context coordinates.

No:
A,
B,
or:
C
functional targets

enter:
this update.

B daughter coefficients:

remain:
frozen.

A coefficients:

remain:
frozen.

The old B gate parameters:

are:
replaced
by:
the accommodated six-parameter gate.

No:
additional permanent routing parameters
are added.

ROUTER-ACCOMMODATION SAFETY METRICS

Immediately after:
B-router accommodation,
before C addition,

report:

- A R^2;
- B R^2;
- B loss relative to:
  pre-accommodation post-B baseline;
- A loss relative to:
  pre-accommodation post-B value;
- B gate activation:
  on A,
  B,
  C contexts.

STAGE C

After:
router accommodation,

add C
with:
the same H183/H181 mechanism:

- 48 coverage-balanced daughters;
- C gate:
  C-positive,
  A/B-negative
  context identity only;
- fit only:
  C daughter coefficients
  to:
  current A+B residual.

No:
A/B functional replay.

POLICIES

A — STATIC48_48

Exact H183 SEQ48_48.

No:
B-router accommodation.

B — ADAPT48_48

PRIMARY CANDIDATE.

48 B daughters,
accommodated B router,
48 C daughters.

C — ADAPT48_32

Same:
B router accommodation.

C:
32 coverage-balanced daughters.

Lower-structure diagnostic.

D — ADAPT64_48

B:
64 daughters.

Accommodated B router.

C:
48 daughters.

Tests:
whether:
stage-B margin
helps:
joint tails
without:
increasing C budget.

E — ADAPT48_RANDOM_C

Accommodated B router.

C:
48 random distributed daughters
with:
learned C gate.

Morphology comparator.

F — GLOBAL_C

Accommodated B router.

C:
global daughter capacity ceiling.

PRIMARY FACTORIAL

Held-out worlds:
20.

Policies:
6.

Evaluations:
120.

PRIMARY METRICS

- stage-A baseline A R^2;
- post-B B R^2;
- pre-adapt B gate C-context activation;
- post-adapt B gate C-context activation;
- B R^2 change from route adaptation;
- A R^2 change from route adaptation;
- post-C A/B/C R^2;
- A total loss;
- B loss after C;
- C train/validation/test R^2;
- world-level joint competence;
- A/B retention;
- active cells;
- routing parameters;
- compute;
- hibernation/reactivation;
- B/C growth-site overlap.

PRIMARY ACCEPTANCE SHAPE

H184 supports:
CONTEXT-ONLY ROUTER ACCOMMODATION

if:

1.
STATIC48_48 reproduces:
H183-level stage-B competence:
median B R^2 >=0.90,
>=90% worlds B>=0.85.

2.
ADAPT48_48
post-accommodation:
median B R^2 loss
relative to:
pre-adaptation B baseline
<=0.02.

3.
>=90%
of ADAPT48_48 worlds
retain B within:
0.05
through:
router accommodation.

4.
Post-adaptation:
median B-gate activation
on C context
<=0.05.

5.
Post-adaptation:
median B-gate activation
on B context
>=0.90.

6.
After C:
median C R^2 >=0.90.

7.
After C:
>=90%
of worlds
C R^2 >=0.85.

8.
After C:
median A total loss <=0.03.

9.
After C:
median B loss
relative to:
post-B baseline
<=0.03.

10.
WORLD-LEVEL JOINT COMPETENCE:

>=90%
of ADAPT48_48 worlds
finish:
A,
B,
C
all:
R^2 >=0.85.

This is:
the decisive H183 correction.

11.
WORLD-LEVEL RETENTION:

>=90%
retain:
A within 0.05
of:
stage-A baseline
AND:
B within 0.05
of:
post-B baseline.

12.
GENERALIZATION:

C validation-test gap <=0.05.

C train-test gap <=0.10.

13.
ROUTING-ONLY DISCIPLINE:

zero:
A/B functional-target replay
during:
B-router accommodation
and:
C addition.

14.
ACTIVE STRUCTURE:

ADAPT48_48
remains:
96 daughters
<=3.1%
of:
parent cells.

15.
PERMANENT PARAMETERS:

96 daughter coefficients
+
12 active router parameters
<=3.5%
of:
parent coefficient count.

16.
ADAPTATION VALUE:

ADAPT48_48
joint competence
must improve:
by:
>=10 percentage points
over:
STATIC48_48

OR:
reach:
>=90%
when STATIC48_48 remains below.

17.
COVERAGE:

ADAPT48_48
joint competence
>=:
ADAPT48_RANDOM_C

and:
C median R^2
>=:
random-C
or:
C R^2 variance
lower by >=20%.

18.
HIBERNATION / REACTIVATION:

exact-return errors <=1e-10.

19.
GLOBAL_C
remains:
C-capacity ceiling.

STRONG SUPPORT

H184 receives STRONG support if:

all primary gates pass

AND:

ADAPT48_32
also reaches:
>=90%
joint A+B+C competence.

MIXED / NEGATIVE CONDITIONS

Treat H184 as mixed / negative if:

- router accommodation
  damages B;
- B-on-C activation
  remains high;
- C reliability does not improve;
- joint competence stays <90%;
- old-router adaptation needs:
  B functional replay;
- more cells,
  not routing,
  remain necessary.

NEXT

If H184 passes:

proceed to:
CLR3-H185 —
CAPABILITY HIBERNATION / REACTIVATION
AND:
ACTIVE-COMPUTE SCALING.

If H184 fails:

test:
multi-context
router architecture
rather than:
increasing daughter-cell count.

SANITY WORLD SEEDS

20260923390000...

PRIMARY WORLD SEEDS

20260923300000
through:
20260923300019.

Sanity:
NON-EVIDENCE.

No:
context geometry,
teacher,
cell budget,
gate feature map,
gate sample count,
gate L2,
daughter ridge,
freeze rule,
or:
acceptance gate

may change
after:
the first held-out H184 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_CONTEXT_ONLY_ROUTER_ACCOMMODATION

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — CONTEXT-ONLY ROUTER ACCOMMODATION HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H184 HELD-OUT PRIMARY EXECUTION.

FINAL H184 SANDBOX HARNESS

File:

h184_router_accom_v1.py

SHA-256:

5b70b29f3a4e878f97e04783db3f1c1f1cd700587e883973c8f897b209330542.

PARENT MODEL

Exact H183
three-capability
sequential substrate.

No:
context,
teacher,
cell budget,
coverage morphology,
daughter fit,
or:
acceptance rule
changes.

ROUTER ACCOMMODATION

After:
B addition

and:
before:
C functional learning,

replace:
B's six routing parameters

with:
a newly fit
six-parameter gate.

Positive:

64 B-context coordinates.

Negative:

32 A-context
+
32 C-context coordinates.

No:
functional target
enters:
this fit.

B daughter coefficients:

remain:
frozen.

A coefficients:

remain:
frozen.

Thus:

only:
B's context-routing state

is:
developmentally accommodated

to:
the newly available
C context.

STAGE C

Exact H183
coverage-balanced
C addition

unless:
a comparator
declares:
32 cells,
64-B margin,
random C,
or:
global C.

POLICIES

STATIC48_48.

ADAPT48_48.

ADAPT48_32.

ADAPT64_48.

ADAPT48_RANDOM_C.

GLOBAL_C.

SANITY

Disjoint family:

20260923390000
and:
20260923390001.

2 worlds.

6 policies.

12 evaluations.

Accepted sanity-output SHA-256:

0d620e6429312a814eedff7acd062f7419878b4609aa86ef031029ec8285d069.

Mechanical checks:

- exact 6 policies / world;
- A coefficients:
  frozen;
- B daughter coefficients:
  frozen;
- B router:
  only state modified
  in:
  accommodation policies;
- zero:
  A/B/C
  functional targets
  enter:
  B-router accommodation;
- C addition:
  exact:
  H183 mechanics;
- hibernation / reactivation:
  exact.

NON-EVIDENCE ROUTING SIGNAL

World:
20260923390000.

Pre-adaptation
B-gate activation
on:
C context:

approximately:
0.252.

Post-adaptation:

approximately:
0.0029.

B-gate activation
on:
B context:

approximately:
0.9948.

B R^2 route-adaptation change:

slightly positive
at:
approximately:
+0.0023.

World:
20260923390001.

B-on-C:

approximately:
0.305
->
0.0052.

B-on-B:

approximately:
0.9941.

B R^2 loss:

approximately:
0.0014.

Thus:

context-only
router accommodation

can:
suppress:
future-context leakage

without:
materially damaging:
the old capability

inside:
sanity.

NON-EVIDENCE SEQUENTIAL SIGNAL

ADAPT48_48:

both sanity worlds

finish:
A,
B,
C
all:
above:
R^2 0.85.

ADAPT48_32:

also:
passes:
both sanity worlds.

This is:
NON-EVIDENCE.

No:

- gate samples;
- gate L2;
- cell budget;
- coverage rule;
- context geometry;
- teacher;
- ridge;
- acceptance gate

was changed.

PRIMARY FAMILY

20260923300000..20260923300019.

20 held-out worlds.

6 policies.

120 evaluations.

H184 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H184 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
