TITLE: DG-1A-AR-H150 — Regeneration Scaling / Cognitive Micro-Patch Granularity Audit
DATE: 2026-09-19
STATUS: PRIMARY COMPLETE / POSITIVE GEOMETRIC MICRO-PATCH PLAUSIBILITY / AREA-LOCALIZATION BREAK-EVEN
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



PRE-PRIMARY IMPLEMENTATION FREEZE 01 — SANITY-SEED ROLLOVER / EXACT METRIC REALIZATION

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE ACCEPTED H150 PRIMARY EXECUTION.

SANITY-SEED CONTAMINATION

The first harness smoke check accidentally exercised:
a small number of seeds
from:
the initially reserved H150 primary families.

Those smoke rows were inspected.

Therefore:
for conservative evidence hygiene,
the entire originally reserved H150 primary families
beginning:

20260919600000,
20260919620000,
20260919630000,
20260919640000

are:
CONTAMINATED / NON-EVIDENCE.

They must not:
be used for accepted H150 primary conclusions.

No primary threshold,
acceptance criterion,
repair probability,
body size,
patch fraction,
granularity,
or:
bandwidth parameter
was changed from those smoke outputs.

FINAL HELD-OUT PRIMARY SEEDS

Axis A:
20260919700000
through:
20260919712599.

Axis B:
20260919720000
through:
20260919720999.

Axis C:
20260919730000
through:
20260919737499.

Axis D:
20260919740000
through:
20260919742399.

These replacement families:
were selected before:
accepted primary execution.

SANITY FAMILY

20260919690000
family.

A full stratified sanity/control run
on this family produced:
4320 NON-EVIDENCE rows
with:
zero 256-step censoring.

HARNESS SHA-256

be1954b9bee838ff6ba42d442bd447cb4b457206bb1617995d71e165f13ac6d7

No execution-semantic change is permitted
after:
the first accepted replacement-primary world
is executed.

EXACT STOCHASTIC REPAIR REALIZATION

For unlimited-local repair:

each damaged cell i
draws an independent:

W_i ~ Geometric(p)

with support:
1,2,3,...

A boundary-damaged cell
becomes eligible at:
time 0.

An interior damaged cell
becomes eligible
after:
the first neighboring damaged cell
repairs.

Repair time is therefore:

T_i =
W_i
+
min(
repair time of an already-repaired damaged neighbor
or:
0 for a live boundary neighbor
).

The harness computes this exactly
as:
weighted first-passage / Dijkstra propagation.

This is equivalent to:
synchronous Bernoulli local repair opportunities
under:
unlimited local parallelism.

BOUNDED-BANDWIDTH REALIZATION

Axis D bounded mode
is simulated explicitly by step.

Per repair step:

at most:
floor(0.10 * body_cells)

eligible damaged cells
receive:
one Bernoulli opportunity.

Allocation is:
round-robin
across:
the originally declared micro-patch components.

Within a component:
eligible cell IDs
are served:
deterministically.

PRIMARY activation probability:
0.50.

AXIS A EXACT LESION REALIZATION

CENTER COMPACT:
nearest body cells
to:
(0,0).

OFF-CENTER COMPACT:
nearest body cells
to:
(0.42R,0).

IRREGULAR CONNECTED:
seed inside:
0.65R,

then:
connected Moore-neighbor growth
with:
selected-neighbor preference
plus:
held-out seeded jitter.

AXIS B EXACT MULTI-PATCH REALIZATION

Total damage:
ceil(0.20N).

Patch centers:
equally spaced
on:
radius 0.58R

with:
held-out random angular rotation.

Damage cells:
assigned as:
nearest still-unselected body cells
to:
each patch center.

All patches:
repair concurrently.

AXIS C EXACT GRANULARITY REALIZATION

Base macro radius at:
g=1
is:
15.

For granularity g:

R(g) =
round(15/g).

Thus:
cell count grows approximately:
1/g^2.

Localized damage fraction:

f(g,beta) =
0.10 * g^beta.

The lesion is:
center compact.

No macro defect center jitter
is used
in primary Axis C.

This isolates:
granularity / localization scaling
from:
lesion-position variance.

AXIS D EXACT PATCH REALIZATION

Body radius:
30.

Each micro-patch requests:

ceil(0.02N)
cells.

Patch centers:
use the same:
equally spaced 0.58R ring
with:
held-out angular rotation.

Overlap is prevented
by:
nearest still-unselected assignment.

At high concurrency:
declared patch identities
remain:
the bandwidth-allocation components

even when:
their spatial frontiers approach.

METRIC FREEZE

T50,
T90,
T99:

first repair step
where:
50%,
90%,
99%
of initially damaged cells
are restored.

COMPLETION:

first step where:
all damaged cells
are restored.

REPAIR OPPORTUNITIES:

number of Bernoulli local-update opportunities
spent on:
damaged cells.

Under unlimited-local repair:
this equals:
sum_i W_i.

SUCCESSFUL REPAIR UPDATES:

number of restored damaged cells.

OPPORTUNITIES PER RESTORED CELL:

repair_opportunities
/
successful_repair_updates.

PEAK FRONTIER:

maximum number
of simultaneously eligible unrepaired cells
over:
the repair trajectory.

MEAN FRONTIER:

mean eligible unrepaired cells
through:
repair completion
or:
the 256-step censoring horizon.

MACRO FUNCTIONAL DOWNTIME PROXY:

sum over repair steps
of:

unrepaired damaged cells
/
total body cells.

This has units of:
body-fraction x repair-step.

It measures:
integrated unavailable local functional mass
under:
the equal-cell functional proxy.

RESTORED CELLS / STEP:

successful repaired cells
/
completion time,

or:
256
when censored.

NORMALIZED RECOVERY / STEP:

final recovered fraction
/
completion time,

or:
256
when censored.

AXIS C COST PER MACRO DAMAGE:

repair opportunities
/
0.10.

The denominator is:
the fixed base macro defect fraction f0,
not:
the localized cell-level fraction.

This intentionally penalizes:
fine granularity
when:
it increases cell count
without:
sufficient localization benefit.

PRIMARY CONTROL SUBSET

Repair-probability robustness
uses the NON-EVIDENCE sanity family only
until:
the main p=0.50 primary is closed.

Stratified controls:

Axis-A-like:
R in:
8,15,30;

damage:
0.02,0.10,0.40;

p:
0.25,0.50,1.00.

Axis-C-like:
g:
1.00,0.50,0.25;

beta:
0,1,2;

p:
0.25,0.50,1.00.

80 sanity worlds
per:
condition.

These controls:
do not alter primary parameters.

PRIMARY EXECUTION STATUS

Accepted H150 replacement-primary execution:
HAS NOT STARTED
at the moment of this freeze.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — GEOMETRY / COST / SATURATION SEMANTICS

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H150 HELD-OUT PRIMARY EXECUTION.

No H150 held-out primary world
has been executed.

BODY REALIZATION

A radius-R body contains every integer lattice point:

x^2 + y^2 <= R^2.

Neighborhood:

Moore 8-neighborhood
restricted to:
body cells.

DAMAGE COUNT

For declared fraction f:

damaged_cells =
ceil(f * N),

bounded to:
1..N-1.

REPAIR STEP

At each synchronous step:

a missing body cell is:
frontier-eligible

iff:

at least one live Moore neighbor exists.

Every selected eligible cell receives:
one Bernoulli repair opportunity.

Successful repair:
restores membership permanently
for the remainder of the world.

Repair stops when:

all lesion cells are restored

or:

256 steps are reached.

THRESHOLD LATENCIES

T50,
T90,
T99

are:

the first completed repair step
at which:
50%,
90%,
99%

of initial lesion membership
has been restored.

REPAIR OPPORTUNITY COST

One repair opportunity =
one Bernoulli trial
for:
one eligible missing cell.

opportunities_per_restored_cell =
total repair opportunities
/
successful restored cells.

MACRO FUNCTIONAL DOWNTIME PROXY

Equal functional mass per body cell.

For each world:

macro downtime =
the discrete area under:

currently missing body-cell fraction

from:
the initial damaged state
through:
repair completion / censoring.

This is:
a geometry / availability proxy only.

AXIS A LESION REALIZATION

CENTER COMPACT:

select cells nearest:
(0,0).

OFF-CENTER COMPACT:

draw one held-out RNG angle.

Lesion center radius:
0.45R.

Select:
nearest body cells
to:
that off-center point.

IRREGULAR CONNECTED:

choose:
one held-out RNG seed cell
from:
the inner 0.5R disk.

Grow:
a Moore-connected cluster
by:
repeated random frontier recruitment

until:
the declared lesion count.

AXIS B MULTI-PATCH REALIZATION

Body:
R=21.

Total damage:
20%.

Requested patch counts:
1,2,4,8,16.

Choose patch centers:
with deterministic farthest-point placement

inside:
0.78R.

Split total damaged-cell count
as evenly as possible
across:
requested patches.

Each patch:
selects nearest currently unused cells
to:
its center.

The realized initial Moore-connected component count
is recorded.

Sanity execution confirms:
1,2,4,8,16 requested patches
remain:
1,2,4,8,16 initial wound components
in the checked non-evidence worlds.

AXIS C FIXED-MACRO-AREA REALIZATION

Reference macro body:

R_base = 15
at:
g=1.

For cell scale g:

R(g) =
round(15 / g).

Thus:
body-cell count scales approximately
as:
1/g^2

while:
macro radius is held fixed
in relative units.

Primary Axis-C lesion:
CENTER COMPACT.

f_damage(g) =
0.10 * g^beta.

No latent repair information
other than:
the declared missing-body membership
is introduced.

AXIS D MULTI-WOUND REALIZATION

Body:
R=30.

Each requested focus:
ceil(0.02N)
damaged cells.

Requested focus counts:
1,2,4,8,16,32.

Centers use:
deterministic farthest-point placement
inside:
0.84R.

Damage is allocated:
compactly around each center
without duplicate damaged cells.

GEOMETRIC SATURATION CLARIFICATION

At:
32 requested 2%-body foci,

declared damage is approximately:
64% of the body.

Under:
Moore connectivity,

it is not geometrically possible
to guarantee:
32 disconnected compact wounds
at that occupancy.

Therefore:

requested_patch_count
and:
actual_initial_connected_components

are both recorded.

Bandwidth allocation uses:
the ACTUAL current
Moore-connected missing components.

The 32-focus condition is interpreted as:
a deliberate geometric saturation regime,

not:
as proof that 32 independent wounds remain disconnected.

No primary Axis-D level is removed
or retuned.

BOUNDED REPAIR BANDWIDTH

Per repair step:

at most:

floor(0.10N)

with minimum 1

missing cells
may receive:
repair opportunities.

When raw frontier demand
exceeds capacity:

- compute current Moore-connected missing components;
- allocate opportunity slots:
  round-robin across components;
- rotate the round-robin start
  by repair step;
- randomize frontier order
  only within each component
  from the world repair RNG.

UNLIMITED LOCAL:

every frontier-eligible missing cell
receives:
one opportunity.

RANDOMNESS

Primary world seeds remain:
exactly the preregistered H150 families.

Lesion geometry consumes:
the primary world RNG.

Repair Bernoulli scheduling uses:
a deterministic SHA-256-derived
sub-seed
from:
world seed
and:
the literal domain tag
"repair".

CONTROLS

After primary:

repair probability controls
use only:
disjoint 20260919695xxx
non-primary seeds.

Stratified control subset:

Axis A:
R = 6,15,30;
damage = 2%,10%,40%;
lesion = CENTER, IRREGULAR;
50 worlds / cell.

Axis C:
g = 1.0,0.5,0.25;
beta = 0,1,2;
100 worlds / cell.

Control repair probabilities:

1.0
and:
0.25.

SANITY RESULTS — NON-EVIDENCE

Representative Axis-B sanity:

20% total damage.

1 patch:
median T90 approximately 8.5 steps.

2:
7.

4:
5.

8:
4.

16:
4.

Opportunity count remained:
approximately flat
across:
the split conditions.

Representative Axis-D sanity:

1..8 requested 2% foci:
bounded 10% repair bandwidth
did not materially bind.

16 foci:
median T90
increased from:
5
to:
7 steps
under bounded bandwidth.

32 requested foci:
geometric merging occurred
and:
bounded-bandwidth median T90
increased from:
5
to:
12 steps.

These sanity outputs are:
NON-EVIDENCE.

No H150 acceptance threshold
was selected
from:
these values.

FROZEN SANDBOX HARNESS SHA-256

51be6032bda5f3a42ca922bdef4cc62eb3d7f9c1c405380711fb0892b5fc646d

No execution-semantic change is permitted
after:
the first held-out H150 primary world
is executed.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.



FINAL PRIMARY CLOSURE — REGENERATION SCALING

DATE:
2026-09-19.

STATUS:
PRIMARY COMPLETE / POSITIVE WITH LOCALIZATION REQUIREMENT.

ACCEPTED PRIMARY

Axis A:
12,600 worlds.

Axis B:
1,000 worlds.

Axis C:
7,500 worlds.

Axis D:
2,400 worlds.

Total:
23,500 held-out primary worlds.

All:
unique replacement seeds.

256-step censoring:
0 worlds.

POST-PRIMARY ROBUSTNESS

4,320 fresh worlds.

Censoring:
0.

AXIS A — BODY SIZE / PATCH SIZE

Median log-log T90 body-size exponent
across patch fractions:

approximately 0.27.

Observed range:

approximately 0.16 .. 0.36.

Thus:
recovery latency grows:
sublinearly
with:
cell count
in this local-frontier geometry.

Small patches recover much faster
than:
large patches.

At radius 30
(2821 cells):

1% lesion:
median T90 = 4.

2%:
5.

5%:
6.

20%:
10.

40%:
14.

60%:
19.

The same qualitative ordering:
holds across:
all tested body sizes.

AXIS B — SAME DAMAGE / MANY MICRO-PATCHES

Body:
1373 cells.

Total damage:
approximately 20%.

Median T90:

1 patch:
8.

2 patches:
6.

4 patches:
5.

8 patches:
4.

16 patches:
4.

Median repair opportunities remain:
approximately constant
at:
546..554.

Median macro downtime:

1 patch:
0.931 body-fraction-steps.

16 patches:
0.437.

Thus:
splitting equal damage
into:
many separated local wounds

approximately halves:
T90
and:
integrated downtime

without:
materially increasing
repair opportunities.

The mechanism is:
parallel local frontier area.

AXIS C — GRANULARITY / LOCALIZATION BREAK-EVEN

At:
g = 1,

body:
709 cells.

10% macro defect:
approximately 71 damaged cells.

Primary median:

T90:
5.

repair opportunities:
approximately 141.

macro downtime:
approximately 0.289.

NO LOCALIZATION IMPROVEMENT

beta = 0.

At:
g = 0.25,

body:
11289 cells.

Damage remains:
10%.

Damaged cells:
1129.

Median:

T90:
14.

repair opportunities:
2258.

This is:
strongly worse.

Therefore:

MORE SMALL CELLS
BY ITSELF
IS NOT
A REGENERATION ADVANTAGE.

LINEAR LOCALIZATION

beta = 1.

At:
g = 0.25:

damage:
approximately 2.5%.

damaged cells:
283.

T90:
8.

repair opportunities:
566.

Still worse than:
g = 1.

AREA-PROPORTIONAL LOCALIZATION

beta = 2.

At:
g = 0.50:

body:
2821.

damage:
approximately 2.5%.

damaged cells:
71.

T90:
5.

repair opportunities:
approximately 142.

macro downtime:
approximately 0.073.

At:
g = 0.25:

body:
11289.

damage:
approximately 0.63%.

damaged cells:
71.

T90:
5.

repair opportunities:
approximately 143.

macro downtime:
approximately 0.018.

Thus:

beta approximately 2
is:
the measured break-even.

Finer cells:
do not yet repair the damaged cell set faster,

but:
they preserve:
approximately constant repair work
and:
constant T90

while:
shrinking
the fraction of the macro-organ
that is functionally unavailable.

SUPER-LOCALIZATION

beta = 2.5.

At:
g = 0.50:

T90:
4.

repair opportunities:
approximately 100.

At:
g = 0.25:

T90:
4.

repair opportunities:
approximately 70.

Thus:
actual repair-latency improvement
appears only when:
functional localization improves
faster than:
simple area scaling.

PRIMARY BREAK-EVEN

beta*:
approximately 2.0.

AXIS D — PARALLEL REPAIR BANDWIDTH

10% of body cells / step
was the frozen bounded opportunity cap.

Median T90,
unlimited versus bounded:

1 patch:
5 / 5.

2:
5 / 5.

4:
5 / 5.

8:
5 / 5.

16:
6 / 7.

32:
9 / 12.

Bandwidth contention therefore:
appears after:
roughly 8 concurrent 2% wounds
in this 2821-cell body.

It degrades:
but does not erase:
parallel micro-patch benefit.

For comparison:

32 bounded micro-patches
cover:
approximately 64.7% of the body

and recover to T90:
12.

A single compact:
60% lesion
in the same-size Axis-A body

has median T90:
19.

ROBUSTNESS — UPDATE RATE

Fresh stratified robustness used:

p:
0.25,
0.50,
1.00.

At:
beta = 2,

g = 0.50
and:
g = 0.25

retain:
approximately the same T90
as:
g = 1

at each tested update rate,

while:
macro downtime remains:
substantially lower
and:
repair opportunities remain:
approximately comparable.

Therefore:
the beta approximately 2
break-even
is not:
an artifact
of:
p = 0.50 alone.

PRIMARY ACCEPTANCE REVIEW

SUPPORTED:

1.
Small 1%..5% lesions:
recover materially faster
than:
20%..60% lesions.

2.
Four or more separated micro-patches:
reduce T90
relative to:
one compact patch
at:
fixed total damage.

3.
The parallel advantage:
survives:
bounded repair bandwidth,
though:
it saturates.

4.
A beta <=2
break-even exists.

Measured:
beta approximately 2.

5.
The architecture does not require:
beta >2
merely to gain:
macro downtime advantage.

6.
The area-localization break-even:
survives:
p = 0.25..1.00
robustness.

FINAL INTERPRETATION

H150 is:

POSITIVE
FOR
GEOMETRIC / RESOURCE PLAUSIBILITY
OF
COGNITIVE MICRO-PATCHING.

But:
the result is conditional.

The useful architecture is NOT:

MAKE CELLS SMALLER
AND REGENERATION
AUTOMATICALLY GETS FASTER.

The supported architecture is:

MAKE CELLS SMALLER
ONLY IF
FUNCTIONAL FAILURE
CAN BE LOCALIZED
AT LEAST
APPROXIMATELY
WITH CELL AREA.

At:
area-proportional localization,

more numerous smaller cells
can:
hold repair work roughly constant

while:
reducing:
functional blast radius
and:
integrated downtime.

If:
localization becomes:
better than area-proportional,

actual repair latency:
can also improve.

This converts:
cell granularity

from:
an aesthetic architectural choice

into:
a measurable trade:

granularity
x
functional localization
x
repair bandwidth.

NEXT CLEAN QUESTION

H151 —
FUNCTIONAL COGNITIVE MICRO-PATCH.

Does:
the beta approximately 2
localization assumption
actually hold
for:
distributed computational function?

A functional experiment must:

- assign measurable computational specialization
  to local cell colonies;
- lesion:
  1%..20%
  of participating cells;
- produce:
  a meaningful task-performance drop;
- regenerate:
  without restoring saved mutable cell state;
- measure:
  functional T50 / T90;
- compare:
  no repair,
  random replacement,
  exact-state reload,
  and:
  developmental local regeneration;
- test:
  whether smaller cells
  reduce the functional blast radius
  enough to realize:
  H150's geometric benefit.

H150 DOES NOT AUTHORIZE

- production cell granularity;
- learned cognitive regeneration claims;
- biological claims;
- STAB-18-R1 execution;
- runtime activation.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
