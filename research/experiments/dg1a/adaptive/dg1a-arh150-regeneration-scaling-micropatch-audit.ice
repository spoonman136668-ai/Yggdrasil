TITLE: DG-1A-AR-H150 — Regeneration Scaling / Cognitive Micro-Patch Granularity Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh149-dual-history-regional-revalidation-cohort-proof-audit.ice
PREREGISTERED_FROM_HEAD: 05d6a2389bf13a86b57120c35c258a289177b421

PURPOSE

H149 closed a repair-authority question.

A separate architectural question is now high leverage:

IF YGGDRASIL IS BUILT FROM
MORE,
SMALLER,
INDEPENDENTLY REGENERABLE
COMPUTATIONAL CELLS,

DOES THAT MAKE
COGNITIVE MICRO-PATCHING
FASTER OR CHEAPER?

The key distinction is:

SMALLER CELLS
ARE NOT AUTOMATICALLY
FASTER TO REGENERATE.

Finer granularity increases:
the number of cells
representing the same macroscopic structure.

It is useful only if:
the finer representation
also shrinks the functional blast radius
of a local failure
enough to compensate.

H150 measures:

1.
body-size scaling;

2.
patch-size scaling;

3.
parallel micro-patch scaling;

4.
cell-granularity versus functional-localization break-even;

5.
repair throughput,
latency,
and cost
under fixed local regenerative dynamics.

BOUNDARY

Synthetic research only.

H150 is:
a geometric / computational upper-bound audit.

It does NOT:
- execute STAB-18-R1;
- train a real Yggdrasil NCA;
- claim biological regeneration;
- claim learned cognitive regeneration;
- use a saved full phenotype as repair input;
- establish production cell size;
- establish production lesion thresholds.

The repair kernel intentionally assumes:
perfectly localized missing-body membership.

This ORACLE LOCAL FRONTIER isolates:
regeneration geometry and resource scaling
from:
injury detection.

A later cognitive experiment must replace:
oracle lesion membership
with:
locally observable developmental evidence.

RELATION TO EXISTING RESEARCH

The adopted Functional Regeneration Protocol requires:
T50,
T90,
repair-resource accounting,
and matched controls.

The prior wound-memory synthetic POC found:
approximately 96%..100% restoration
across unseen sizes
with:
3..7 local recruitment steps,

including:
120 / 121 restored cells
in a 709-cell body
after:
a 121-cell lesion
in six steps.

H150 does not reuse those numbers as:
primary evidence.

They motivate:
the scaling question.

PRIMARY REPAIR KERNEL

BODY

2D integer lattice disk.

A body cell is:
a lattice point
inside:
radius R.

LESION

A declared subset
of body cells
is removed.

No exterior cell
is eligible for restoration.

LOCAL FRONTIER

At each synchronous repair step:

a missing body cell
is repair-eligible
when:
at least one Moore-neighbor
is currently live.

STOCHASTIC LOCAL UPDATE

Each eligible missing cell
receives:
one Bernoulli repair opportunity
per step.

Primary activation probability:
0.50.

Successful opportunity:
restores the cell.

This mirrors:
stochastic local-update scheduling
without claiming:
the full Yggdrasil dynamics.

No restored cell
receives:
a copied pre-damage mutable state.

The experiment tracks:
membership / functional-mass recovery.

FUNCTIONAL PROXY

Each body cell carries:
equal local functional mass
unless:
Axis C explicitly changes
functional blast-radius assumptions.

For Axes A/B:

RecoveryFraction(t) =
restored lesion cells by t
/
initial lesion cells.

This is:
a micro-function availability proxy,

not:
a claim that real intelligence
decomposes linearly by cell.

PRIMARY AXIS A — BODY SIZE x PATCH FRACTION

Disk radii:

6,
8,
11,
15,
21,
30.

Approximate body scale:
from:
~100 cells

to:
~2,800 cells.

Patch fractions:

0.01,
0.02,
0.05,
0.10,
0.20,
0.40,
0.60.

Lesion families:

A1 —
CENTER COMPACT.

A2 —
OFF-CENTER COMPACT.

A3 —
IRREGULAR CONNECTED.

For compact lesions:
select cells nearest:
the lesion center
until:
the declared damage count
is reached.

For irregular connected lesions:
grow:
a seeded random connected cluster
inside the body
using:
held-out world RNG.

PRIMARY WORLDS

100 worlds
per:
body-size x patch-fraction x lesion-family cell.

6 x 7 x 3 x 100
=
12,600 worlds.

PRIMARY AXIS B — SAME DAMAGE, MANY MICRO-PATCHES

Body radius:
21.

Total damaged fraction:
0.20.

Split the same total damaged-cell count into:

1,
2,
4,
8,
16

spatially separated compact patches.

Primary:
200 worlds / split count.

1,000 worlds.

All patches:
repair concurrently.

This isolates:
whether:
parallel local frontiers
reduce:
functional recovery latency

without:
changing total lost functional mass.

PRIMARY AXIS C — CELL GRANULARITY / LOCALIZATION BREAK-EVEN

This is:
the central intelligence-patching question.

Hold:
macroscopic cognitive body area
constant.

Represent the same macro-organ
with relative cell linear scale:

g =
1.00,
0.75,
0.50,
0.35,
0.25.

Smaller g means:
more computational cells
per fixed macro area.

Idealized cell count scales as:

N(g)
proportional to
1 / g^2.

A macro-level defect has:
fixed physical / functional radius.

But:
the localizable blast radius
may shrink
with cell granularity.

Define:

localization exponent beta.

Damaged macro-area fraction:

f_damage(g)
=
min(
f0,
f0 * g^beta
).

Interpretation:

beta = 0:
smaller cells do NOT improve localization.

beta = 1:
linear localization improvement.

beta = 2:
area-proportional localization improvement.

beta >2:
super-localization.

Primary beta values:

0,
0.5,
1,
1.5,
2,
2.5.

Primary base macro defect:

f0 =
0.10.

For each:
g x beta,

instantiate:
a disk body
with:
N approximately proportional to 1/g^2

and:
remove the corresponding compact lesion fraction.

Measure:

- damaged cell count;
- T50;
- T90;
- T99;
- repair opportunities;
- repaired cells / step;
- normalized recovery / step;
- peak simultaneous frontier;
- cumulative cell-updates spent;
- macro functional downtime proxy.

Primary:
250 worlds / g x beta.

5 x 6 x 250
=
7,500 worlds.

BREAK-EVEN DEFINITION

Finer granularity is:
MICRO-PATCH ADVANTAGEOUS

only when it reduces at least one of:

- T90;
- total repair opportunities;
- macro functional downtime;

without increasing another
by more than:
20%.

The key derived quantity is:

cost_per_macro_damage =
total repair opportunities
/
f0.

The architectural break-even beta*
is:
the smallest localization exponent
where:
g <1
provides a median cost or latency advantage
over:
g =1.

PRIMARY AXIS D — PARALLEL REPAIR INTERFERENCE

A larger organism of smaller cells
may need:
many simultaneous micro-patches.

Use:
radius 30 body.

Each patch:
2% body-equivalent local lesion.

Concurrent patch count:

1,
2,
4,
8,
16,
32.

Two communication-capacity models:

D1 —
UNLIMITED LOCAL.

Every frontier cell:
receives its Bernoulli opportunity.

D2 —
BOUNDED REPAIR BANDWIDTH.

Per step:
at most 10% of body cells
may receive:
repair opportunities.

When demand exceeds capacity:

allocate:
round-robin across connected wound components.

Primary:
200 worlds / concurrency x bandwidth model.

6 x 2 x 200
=
2,400 worlds.

This tests:
whether micro-patching scales
only because:
the toy implicitly grants
unbounded parallel compute.

CONTROLS

C0 —
DETERMINISTIC FRONTIER.

Repair probability:
1.0.

Provides:
geometric lower bound
on repair steps.

C1 —
PRIMARY STOCHASTIC.

Repair probability:
0.50.

C2 —
SLOW STOCHASTIC.

Repair probability:
0.25.

Controls are applied on:
a stratified subset
of Axis A
and:
Axis C.

They are not:
used to tune primary thresholds.

PRIMARY METRICS

1.
initial body cells N;

2.
damaged cells;

3.
damage fraction;

4.
restored fraction trajectory;

5.
T50;

6.
T90;

7.
T99;

8.
completion time;

9.
cells restored / step;

10.
fraction restored / step;

11.
peak frontier size;

12.
mean frontier size;

13.
cumulative repair opportunities;

14.
successful repair updates;

15.
opportunities / restored cell;

16.
macro functional downtime proxy;

17.
parallelism efficiency;

18.
body-size scaling exponent;

19.
patch-size scaling exponent;

20.
granularity break-even beta*.

TIMEOUT

Maximum:
256 repair steps.

If:
T90
is not reached,

record:
censored at 256.

PRIMARY QUESTIONS

Q1.

At fixed patch fraction,
does normalized recovery time
remain approximately invariant
with body size,

or:
does larger body size
slow repair?

Q2.

At fixed body size,
how does:
T90
scale with:
patch fraction?

Q3.

At fixed total damaged mass,
does splitting damage into:
many spatially separated micro-patches

reduce:
T90
through:
greater parallel frontier area?

Q4.

When:
cell count increases
because cells become smaller,

what localization improvement
is required
before:
micro-patching becomes
latency / cost advantageous?

Q5.

Does:
bounded repair bandwidth
erase:
the apparent parallel micro-patch advantage?

PRIMARY ACCEPTANCE SHAPE

H150 supports the
MICRO-PATCH ARCHITECTURE HYPOTHESIS
if:

1.
T90 for:
1%..5% lesions
is materially lower
than:
20%..60% lesions
within the same body size;

2.
at fixed total damaged fraction,
4+ spatially separated patches
show:
lower median T90
than:
one compact patch
under:
unlimited-local repair;

3.
that advantage does not disappear completely
under:
the bounded-bandwidth model;

4.
there exists:
at least one
beta <=2
for which:
finer granularity
g <=0.50
produces:
lower median T90
or:
lower macro downtime
than:
g=1
without:
>20% opportunity-cost penalty;

5.
the inferred break-even
does not require:
implausible super-localization
beta >2;

6.
small-cell advantage
is robust to:
repair probability
0.25..1.0
in the stratified controls.

MIXED / NEGATIVE CONDITIONS

Treat H150 as:
mixed or negative
for intelligence micro-patching
if:

- smaller cells only increase:
repair work
without reducing:
macro recovery latency;

- beta >2
is required
before:
finer granularity helps;

- multi-patch speedup exists only
under:
unbounded parallel opportunities
and vanishes
under:
bounded repair bandwidth;

- small lesions do not materially
recover faster
than:
large lesions;

- body-size scaling is strongly superlinear;

- stochastic local update
creates:
large long-tail recovery delays
for fine-grained bodies.

IMPORTANT INTERPRETATION BOUNDARY

A positive H150 result would establish only:

GEOMETRIC / RESOURCE PLAUSIBILITY
OF
COGNITIVE MICRO-PATCHING.

It would NOT establish:

- learned cognitive specialization;
- correct injury localization;
- semantic capability recovery;
- memory transfer;
- safe live cognitive replacement.

Those become:
the next scoped experiment.

NEXT EXPERIMENT IF H150 IS POSITIVE OR MIXED-POSITIVE

H151 —
FUNCTIONAL COGNITIVE MICRO-PATCH.

Assign:
a local computational colony
a measurable function.

Lesion:
1%..20%
of participating cells.

Regenerate:
without restoring saved mutable state.

Measure:
functional RecoveryFraction,
T50,
T90,
and:
whether neighboring developmental context
reconstructs the lost specialization.

NEXT EXPERIMENT IF H150 IS NEGATIVE

Do NOT:
simply increase cell count.

Investigate:
hierarchical regenerative granularity

where:
small repairable subunits
exist only inside:
high-turnover cognitive regions.

PRIMARY SEEDS

Axis A:
20260919600000
through:
20260919612599.

Axis B:
20260919620000
through:
20260919620999.

Axis C:
20260919630000
through:
20260919637499.

Axis D:
20260919640000
through:
20260919642399.

These seed families are:
held out.

SANITY SEEDS

20260919690000
family.

Sanity outputs:
NON-EVIDENCE.

No primary threshold
may be tuned
after:
the first held-out primary world
is executed.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_REGENERATION_SCALING_MICROPATCH

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false
