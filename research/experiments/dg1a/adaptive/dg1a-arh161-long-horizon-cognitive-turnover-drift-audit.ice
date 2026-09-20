TITLE: DG-1A-AR-H161 — Long-Horizon Repeated Cognitive Turnover / Micro-Patch Drift Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh160-small-cell-functional-micropatch-scale-transfer-audit.ice

PURPOSE

H160 established:

a larger macro body
can be represented by:
many more,
smaller,
computational cells

while:
a beta=2 localized defect
keeps:
the absolute micro-patch burden
approximately bounded.

H160 also established:

functional quality
and:
stable-T90 reliability
transfer
from:
N approximately 197

to:
N approximately 3209.

The next risk is:
LONG-HORIZON DRIFT.

A regenerative cognitive architecture
is not useful if:

each individual repair looks healthy

while:

many repairs
slowly move:
the learned function
away from:
its original capability.

H161 asks:

CAN
YGGDRASIL
REPEATEDLY
LOSE,
REGROW,
AND:
RE-SPECIALIZE
LOCAL COGNITIVE CELLS

WITHOUT:

- checkpoint-restoring their lost mutable state;
- changing surviving cells;
- global retraining;
- cumulative capability drift?

BOUNDARY

Synthetic research only.

No:
production model repair,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or runtime activation.

PARENT REPRESENTATION

Reuse:
H160 resolution-invariant macro field.

Cell scales:

g =
1.00,
0.50,
0.25.

Corresponding body sizes:

approximately:
197,
797,
3209 cells.

Context classes:

SMOOTH,
MIXED.

Functional readout:

Gaussian RBF,
sigma=0.22
in normalized macro coordinates.

Evaluation:

256 held-out macro queries
fixed for:
the entire life of one world.

TARGET FUNCTION

At:
world initialization,

sample:
one immutable developmental target field
using:
the H160 continuous-field generator.

Let:

w_target =
the original learned specialization field.

Let:

Y_target =
the original colony output
on:
the fixed evaluation queries.

Non-oracle repair policies
may NOT read:

- lost w_target values;
- Y_target
  on:
  held-out evaluation queries.

Y_target is:
evaluation-only.

Local functional feedback
may query:
the original task function
at:
declared local feedback points,

as in:
H152-H160.

This represents:
environment / task feedback,

not:
a coefficient checkpoint.

PERSISTENT MUTABLE STATE

Each repair policy owns:
one current mutable coefficient vector.

After:
each repair cycle,

the repaired coefficient vector
becomes:
the starting state
for:
the next cycle.

There is:

NO:
global reset
to:
w_target.

Therefore:

repair error
can:
accumulate,
cancel,
or:
propagate
across:
cycles.

PRIMARY LOCAL DAMAGE

Base macro defect:

f0 =
0.05.

Localization:

beta=2.

For scale g:

f_damage =
0.05 * g^2.

Damage count:

ceil(
N(g) * f_damage
).

Expected:

approximately:
10..11 cells / event

across:
all three scales.

Each cycle:

the selected cells
lose:
their current mutable state.

Their lost current coefficient
is:
not available
to:
non-oracle repair.

TURNOVER REGIMES

R0 — ROAMING

At every cycle:

draw:
a new macro lesion center

uniformly
inside:
normalized radius 0.65.

Damage:

compact nearest-cell patch
around:
that center.

This drives:
distributed turnover
across:
the organism.

R1 — HOTSPOT

At world initialization:

draw:
one macro hotspot center
inside:
normalized radius 0.50.

Each cycle:

lesion center =
hotspot center
+
Gaussian macro jitter

sd:
0.08.

Reject:
outside:
radius 0.75.

This drives:

REPEATED
LOCAL TURNOVER

inside:
one cognitive micro-organ.

It tests:

whether:
the same local function
can:
be regenerated
many times

without:
progressive state corruption.

PRIMARY LIFETIME

40 repair cycles.

Every cycle
uses:

- a fresh membership-repair schedule;
- a fresh local feedback-query pool;
- fresh feedback-noise potentials;
- the same immutable task target;
- the policy's current mutable state
  as:
  the pre-damage organism.

FEEDBACK NOISE

eta:

0,
0.25.

Noise scale per cycle:

eta
*
sqrt(
MSE(
current lesioned output,
Y_target
)
).

Evaluation:
noise-free.

REPAIR POLICIES

A — CONTEXT-ONLY

Membership regeneration
plus:
H151 context-harmonic reconstruction.

No:
functional feedback.

Twelve:
post-membership context maturation steps.

This tests:

whether:
developmental locality alone
can:
survive repeated turnover.

B — SERIAL24

Membership regeneration.

Wait for:
100%
local membership return.

Then:

- lambda=0.01;
- global leverage local queries;
- 24-observation cap;
- 6 observations / active step;
- joint solve
  over:
  the current lesion cells;
- surviving cells fixed.

C — INTERLEAVED24

H159/H160 functional architecture.

Begin:
functional feedback

when:
50%
of:
local lesion membership
has regenerated.

Then:

- lambda=0.01;
- same:
  24-observation cap;
- 6 observations / active step;
- expanding joint solve;
- accumulated feedback reused;
- surviving cells fixed.

D — LOCAL-CHECKPOINT-ORACLE

Evaluation ceiling.

When:
a lesioned cell
returns,

restore:
its original
w_target coefficient.

Surviving cells:
remain unchanged.

This comparator:

does NOT:
globally reset
the organism.

It defines:
the no-local-state-loss ceiling
under:
the same repeated lesion schedule.

CYCLE HORIZON

Membership repair proceeds
until:
complete.

Then:

12 post-membership maturation steps

for:
A,
B,
C.

ORACLE:

is evaluated
through:
the same elapsed repair horizon

but:
does not:
modify surviving state.

COMMON-WORLD DISCIPLINE

One world defines:

- target continuous field;
- evaluation queries;
- turnover-regime macro centers;
- per-cycle lesion geometry;
- membership-repair potentials;
- feedback-query geometry;
- feedback target noise.

All policies
inside:
one g x eta condition

receive:
the same:
lesions,
membership schedules,
query coordinates,
and:
noise potentials

for:
matching cycles.

TARGET-FIDELITY METRIC

Let:

Var_target =
variance(
Y_target
).

At:
the end
of:
every repair cycle:

TargetMSE(c) =
MSE(
Y_current(c),
Y_target
).

GlobalFidelity(c) =

1 -
TargetMSE(c)
/ Var_target.

Report:

raw fidelity
and:
clipped [0,1]
where appropriate.

This metric
does NOT:
renormalize
to:
the current lesion.

It therefore reveals:
cumulative capability drift.

SELF-RECOVERY DIAGNOSTIC

For each cycle:

Y_pre =
policy output
immediately before:
that cycle's lesion.

Y_les =
output
immediately after:
lesion.

Y_post =
output
after:
repair / maturation.

SelfRecovery(c) =

1 -
MSE(
Y_post,
Y_pre
)
/
MSE(
Y_les,
Y_pre
).

This answers:

DID
THE PATCH
RESTORE
THE FUNCTION
IT INHERITED?

It is:
diagnostic only.

A policy can:

SelfRecovery approximately 1

while:
GlobalFidelity
slowly drifts.

That distinction is:
a central H161 question.

ABSOLUTE ERROR EXPOSURE

Across:
every repair step
and:
every cycle,

integrate:

MSE(
Y_step,
Y_target
)
/ Var_target.

This is:

cumulative normalized
absolute functional-error exposure.

Unlike:
lesion-normalized downtime,

it remains:
comparable
across:
cell scales
whose lesion impact differs.

TURNOVER ACCOUNTING

Track:

- total replacement events;
- unique cells ever replaced;
- unique-turnover fraction;
- body-equivalent turnover:
  total replacement events / N;
- per-cell replacement count;
- maximum per-cell replacement count;
- fraction of cells replaced:
  >=2,
  >=5,
  >=10 times.

PRIMARY FACTORIAL

Context:

SMOOTH,
MIXED.

Cell scale:

1.00,
0.50,
0.25.

Turnover regime:

ROAMING,
HOTSPOT.

Feedback eta:

0,
0.25.

Worlds / cell:

30.

Condition-worlds:

2 x 3 x 2 x 2 x 30
=
720.

Policies:

4.

Primary policy-world lifetimes:

2,880.

Repair cycles:

40 / lifetime.

Total policy repair cycles:

115,200.

PRIMARY METRICS

1.
final GlobalFidelity at cycle 40;

2.
GlobalFidelity at:
cycles 10,
20,
30,
40;

3.
minimum post-cycle GlobalFidelity;

4.
TargetMSE trajectory;

5.
drift slope
over:
cycles 20..40;

6.
fraction of worlds
with:
final GlobalFidelity >=0.95;

7.
fraction
with:
final GlobalFidelity >=0.90;

8.
SelfRecovery trajectory;

9.
cumulative absolute error exposure;

10.
per-cycle stable T90
when defined;

11.
per-cycle feedback observations;

12.
total feedback observations;

13.
membership-repair latency;

14.
unique-turnover fraction;

15.
body-equivalent turnover;

16.
maximum cell replacement count;

17.
HOTSPOT repeat-load distribution;

18.
INTERLEAVED24 versus SERIAL24;

19.
CONTEXT-ONLY drift gap;

20.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H161 supports:
LONG-HORIZON
REGENERATIVE COGNITIVE TURNOVER

if:

1.
MIXED,
INTERLEAVED24:

median final GlobalFidelity
at:
cycle 40

>=0.98

for:
every:
g,
turnover regime,
and:
eta.

2.
MIXED,
INTERLEAVED24:

>=90%
of worlds

finish:
cycle 40

with:
GlobalFidelity >=0.95

for:
every:
g,
regime,
eta.

3.
MIXED,
INTERLEAVED24:

median GlobalFidelity
does NOT fall

by:
more than 0.01

from:
cycle 20
to:
cycle 40

for:
every:
g,
regime,
eta.

This is:
the cumulative-drift gate.

4.
MIXED,
HOTSPOT:

INTERLEAVED24
median final GlobalFidelity
>=0.98

even when:
the maximum per-cell
replacement count

exceeds:
10
in:
the median world.

This tests:
deep repeated local turnover.

5.
MIXED:

INTERLEAVED24
beats:
CONTEXT-ONLY

in:
median final GlobalFidelity

by:
>=0.05

in:
at least:
8 of:
12
g x regime x eta groups

OR:

CONTEXT-ONLY
already achieves:
>=0.98
in:
a group,
in which case:
that group is:
neutral
rather than:
a required win.

6.
INTERLEAVED24
median final GlobalFidelity

is:
within:
0.01
of:
SERIAL24

for:
every:
MIXED
g x regime x eta group.

This requires:
interleaving
to preserve:
long-horizon quality.

7.
INTERLEAVED24
cumulative absolute error exposure

is:
no more than:
10%
above:
SERIAL24

in:
every:
MIXED
g x regime x eta group

and:

is lower
in:
at least:
6 of:
12 groups.

8.
Fine-scale transfer:

MIXED
g=0.25
INTERLEAVED24

median final GlobalFidelity

is:
no more than:
0.01 below:
g=1.00

for:
both regimes
and:
both eta classes.

9.
MIXED
INTERLEAVED24:

median SelfRecovery
across:
cycles 21..40

>=0.95

for:
every:
g,
regime,
eta.

10.
No non-oracle policy
uses:
more than:
24 feedback observations
inside:
one repair cycle.

11.
SMOOTH
INTERLEAVED24:

median final GlobalFidelity
>=0.99

for:
every:
g,
regime,
eta.

12.
LOCAL-CHECKPOINT-ORACLE
remains:
the capability ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H161 as:
mixed / negative
if:

- per-cycle repair looks successful
  while:
  original-task fidelity
  drifts;

- HOTSPOT turnover
  accumulates:
  local specialization error;

- fine-grained bodies
  only appear stable
  because:
  they experience:
  less body-equivalent turnover;

- INTERLEAVED24
  accumulates:
  more drift
  than:
  SERIAL24;

- functional feedback
  repeatedly corrects:
  the immediate lesion
  but:
  leaves:
  long-horizon target error;

- the 24-query local budget
  becomes:
  insufficient
  after:
  many cycles;

- surviving cells
  must be:
  globally retrained.

POST-PRIMARY STRESS
ONLY IF PRIMARY SUPPORTS

A matched:
one-body-equivalent turnover
stress test

may:
be designed

after:
primary closure

to separate:

fixed operational event count

from:

matched cumulative turnover fraction.

Do NOT:
spend that stress family
before:
primary closure.

PRIMARY WORLD SEEDS

20260921000000
through:
20260921000719.

SANITY WORLD SEEDS

20260921090000...

Sanity:
NON-EVIDENCE.

No:
cycle count,
f0,
beta,
g,
turnover regime,
lambda,
feedback budget,
noise level,
or:
acceptance gate

may change
after:
the first held-out H161 lifetime.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_LONG_HORIZON_COGNITIVE_TURNOVER

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — RECONSTRUCTED LONG-HORIZON TURNOVER HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H161 HELD-OUT PRIMARY EXECUTION.

RUNTIME RECOVERY NOTE

The earlier H161 sandbox harness
did not survive:
the runtime transition.

No H161 held-out primary lifetime
had been executed.

The harness was therefore:
reconstructed

from:

- the accepted H160
  resolution-invariant field mechanics;
- the accepted H159
  START50 interleaving mechanics;
- this H161 preregistration.

The reconstruction was tested only on:
the disjoint H161 sanity family

before:
this freeze.

FINAL H161 SANDBOX HARNESS

File:

h161_turnover_reconstructed_v1.py

SHA-256:

ae89e645e9f00f33a581c05298a0b2e930b450bbc9a55f0e0f46f87de86a8248.

WORLD / BODY REALIZATION

Cell scales:

g =
1.00,
0.50,
0.25.

R(g) =
round(
8 / g
).

Body:
integer lattice disk.

Continuous target field:

exact H160
SMOOTH / MIXED
macro-anchor construction.

Evaluation:

256 fixed macro query points
per:
lifetime.

REPAIR EVENT

Damage:

f0=0.05.

beta=2.

damage count:

ceil(
N(g) * 0.05 * g^2
).

Thus:
approximately 10..11 cells / event.

ROAMING:

new compact macro-center
each cycle
inside:
normalized radius 0.65.

HOTSPOT:

one macro hotspot
inside:
radius 0.50;

cycle center =
hotspot
+
Gaussian jitter
sd=0.08,

rejected outside:
radius 0.75.

MEMBERSHIP

H150/H151 Moore-frontier repair.

p=0.50.

Fresh deterministic schedule
per:
world seed x cycle.

CONTEXT

New cell:

mean
of:
currently live Moore-neighbor
mutable coefficients.

Every repair / maturation step:

regenerated lesion cells
receive:
one synchronous

0.50 current
+
0.50 live-neighbor mean

context refinement.

Surviving cells:

immutable
inside:
that repair cycle.

FUNCTIONAL FEEDBACK

64 lesion-local candidate queries
per:
cycle.

Query generation:

- choose one lesion member;
- center on:
  its normalized macro coordinate;
- Gaussian jitter:
  sd=0.12;
- reject outside:
  unit disk.

Query design:

global leverage /
greedy D-optimal proxy.

lambda:

0.01.

Maximum selected queries:

24.

Batch:

6 observations / active step.

The leverage sequence:

uses:
full declared lesion geometry

and:
basis geometry only.

No target value
enters:
query selection.

SERIAL24:

functional calibration begins
after:
100%
membership return.

INTERLEAVED24:

functional calibration begins
when:
restored lesion membership
reaches:
50%.

At:
each active step:

all currently regenerated lesion coefficients
are:
joint variables.

All acquired feedback
is reused
as:
the variable domain expands.

Surviving coefficients
remain:
fixed.

FEEDBACK NOISE

A deterministic standard-normal
noise potential

is common by:

world seed,
cycle,
eta,
feedback-query index.

Per:
the H161 declared noise definition,

the potential is scaled
inside each policy by:

eta
*
sqrt(
MSE(
that policy's current lesioned output,
Y_target
)
).

Thus:

noise potentials
are common-world,

while:
the declared current-lesion scaling
can differ slightly
after policies accumulate:
different historical drift.

No:
true lost coefficient
or:
held-out evaluation target

enters:
non-oracle repair.

LOCAL-CHECKPOINT-ORACLE

On:
membership return,

restore:
the immutable original
w_target coefficient

for:
that returned cell.

No global reset.

Oracle remains:
evaluation ceiling only.

PERSISTENT STATE

Every non-oracle policy:

carries:
its repaired coefficient vector

directly into:
the next cycle.

There is:
no:
global reset,
target-state reset,
or:
checkpoint restore.

GLOBAL FIDELITY

After:
every cycle:

1 -
MSE(
current evaluation output,
immutable Y_target
)
/
Var(
Y_target
).

SELF RECOVERY

Per cycle:

1 -
MSE(
post-repair output,
pre-lesion policy output
)
/
MSE(
lesioned output,
pre-lesion policy output
).

ABSOLUTE ERROR EXPOSURE

Accumulated over:

- the immediate lesion state;
- every membership-repair step;
- every post-membership maturation step

as:

MSE(
current output,
Y_target
)
/
Var(
Y_target
).

TURNOVER

Track:

- total cell-replacement events;
- unique cells touched;
- body-equivalent turnover;
- maximum repeat count;
- >=2,
  >=5,
  >=10
  replacement fractions.

SANITY

Disjoint family:

20260921090000...

12 representative lifetimes.

48 policy lifetimes.

40 repair cycles each.

Mechanical checks:

- exactly four policies / sanity lifetime;
- LOCAL-CHECKPOINT-ORACLE
  final fidelity:
  exactly 1.0
  in every sanity lifetime;
- SERIAL24 / INTERLEAVED24
  max observations per cycle:
  24;
- persistent mutable state
  carried across:
  all 40 cycles;
- no target coefficient
  entered:
  non-oracle repair;
- no global state reset.

NON-EVIDENCE SCIENTIFIC SIGNAL

MIXED,
g=1,
ROAMING,
eta=0:

CONTEXT-ONLY
final GlobalFidelity:

approximately:
0.817.

SERIAL24:

approximately:
0.99996.

INTERLEAVED24:

approximately:
0.99996.

MIXED,
g=1,
HOTSPOT,
eta=0:

maximum single-cell
replacement count:

approximately:
40.

INTERLEAVED24
final GlobalFidelity:

approximately:
0.99999.

MIXED,
g=0.25,
HOTSPOT:

maximum single-cell
replacement count:

approximately:
12
in:
the representative sanity lifetimes,

with:
INTERLEAVED24
final GlobalFidelity
approximately:
1.0.

These sanity outputs are:

NON-EVIDENCE.

No:

- cycle count;
- f0;
- beta;
- cell scale;
- turnover regime;
- lambda;
- feedback budget;
- noise level;
- acceptance gate

was changed.

PRIMARY FAMILY

20260921000000..20260921000719.

720 held-out condition-world lifetimes.

4 policies.

2,880 policy lifetimes.

115,200 repair cycles.

H161 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H161 lifetime.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — LONG-HORIZON REPEATED COGNITIVE TURNOVER

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / POSITIVE.

FINAL PINNED HARNESS SHA-256

ae89e645e9f00f33a581c05298a0b2e930b450bbc9a55f0e0f46f87de86a8248.

ACCEPTED PRIMARY MATRIX SHA-256

26ef063183123e4e18458d2c04d6b6198369c71d9a3e1fdf1679b1ade655f366.

ACCEPTED PRIMARY FAMILY

20260921000000..20260921000719.

PRIMARY MATRIX

720 held-out condition-world lifetimes.

4 policies.

2,880 policy lifetimes.

40 repair cycles / lifetime.

115,200 total policy repair cycles.

Validation:

- exactly 720 unique held-out seeds;
- exact accepted seed interval;
- exactly four policy rows / seed;
- zero duplicate seed x policy rows;
- no missing accepted seeds;
- no post-primary parameter tuning.

PRIMARY CANDIDATE

INTERLEAVED24.

MIXED LONG-HORIZON FIDELITY

Across all:
3 cell scales
x
2 turnover regimes
x
2 noise classes,

minimum group median
cycle-40 GlobalFidelity:

0.9998858.

Frozen target:
>=0.98.

PASS:
12 / 12 groups.

WORLD-LEVEL FIDELITY

Fraction of MIXED INTERLEAVED24 worlds
finishing:
cycle 40

with:
GlobalFidelity >=0.95:

100%
in:
every
g x regime x eta group.

Frozen target:
>=90%.

PASS:
12 / 12.

The worst accepted individual
MIXED INTERLEAVED24
cycle-40 fidelity:

approximately:
0.999660.

CUMULATIVE DRIFT

Maximum group-median decline:

median GF20
minus:
median GF40

across:
all MIXED groups:

approximately:
4.6e-6.

Frozen limit:
0.01.

PASS.

Thus:

there is:
no measurable cumulative
capability erosion

over:
cycles 20..40

at:
the preregistered scale.

HOTSPOT REPEAT LOAD

Median maximum
single-cell replacement count
under:
MIXED HOTSPOT INTERLEAVED24:

g=1.00:
39.

g=0.50:
25.

g=0.25:
12.

All:
exceed 10.

Median cycle-40 GlobalFidelity
remains:

g=1.00:
approximately 0.99999
clean

and:
approximately 0.99997
at eta=0.25.

g=0.50:
approximately 0.999998.

g=0.25:
approximately 1.0.

PASS.

Repeated repair
of:
the same local cognitive micro-organ

does NOT:
produce progressive specialization loss
under:
this 40-cycle protocol.

CONTEXT-ONLY COMPARATOR

Context-only behavior
is:
strongly scale dependent.

At:
fine scales,

the small beta=2 wound
can be:
so locally constrained
that:
context alone
often remains near:
target function.

At:
g=1.0 ROAMING,

context-only
median cycle-40 fidelity:

eta=0:
approximately 0.871.

eta=0.25:
approximately 0.896.

One accepted context-only world
fell to:

approximately:
0.445
cycle-40 GlobalFidelity

while:
its self-recovery metric
remained locally plausible.

This directly confirms:
the H161 warning.

A patch can:
approximately restore
the function it inherited

while:
the original task function
quietly drifts.

Gate 5:

INTERLEAVED24
beats:
CONTEXT-ONLY
by:
>=0.05

in:
the two non-neutral
coarse roaming groups.

All other:
10 / 12 groups

already have:
CONTEXT-ONLY
median fidelity >=0.98

and:
are neutral
under:
the frozen rule.

PASS.

SERIAL VERSUS INTERLEAVED
LONG-HORIZON QUALITY

Maximum absolute difference
between:
MIXED INTERLEAVED24
and:
SERIAL24

group-median
cycle-40 fidelity:

approximately:
2.5e-8.

Frozen limit:
0.01.

PASS:
12 / 12.

Thus:

interleaving does NOT:
trade away:
long-horizon fidelity.

ABSOLUTE ERROR EXPOSURE

INTERLEAVED24
median cumulative
absolute error exposure

is:
LOWER
than:
SERIAL24

in:
12 / 12
MIXED groups.

INTERLEAVED / SERIAL
median exposure ratio:

best:
approximately 0.663.

worst:
approximately 0.971.

Equivalent exposure reduction:

approximately:
2.9%
to:
33.7%.

Median reduction:

approximately:
16.1%.

Frozen gate:

no group
>10%
above serial

and:
lower
in:
at least 6 / 12.

PASS:
lower in:
12 / 12.

FINE-SCALE TRANSFER

MIXED INTERLEAVED24
cycle-40 median fidelity

at:
g=0.25

is:
slightly ABOVE,
not below,

the corresponding:
g=1.0

median

for:
both turnover regimes
and:
both eta classes.

PASS:
4 / 4.

SELF-RECOVERY

Minimum group median
INTERLEAVED24
SelfRecovery

across:
cycles 21..40:

approximately:
0.99807.

Frozen target:
>=0.95.

PASS:
12 / 12.

FEEDBACK BUDGET

Maximum:
INTERLEAVED24
or:
SERIAL24
feedback observations
inside:
one repair cycle:

24.

PASS.

SMOOTH CONTROL

Minimum group median
SMOOTH INTERLEAVED24
cycle-40 GlobalFidelity:

approximately:
0.999898.

Frozen target:
>=0.99.

PASS.

LOCAL-CHECKPOINT-ORACLE

Final GlobalFidelity:

exactly:
1.0

through:
the accepted matrix.

Remains:
the capability ceiling.

PASS.

PREREGISTERED GATE REVIEW

PASS:

1.
MIXED median final fidelity.

2.
MIXED world-level >=0.95 reliability.

3.
No cycle-20 to cycle-40 cumulative drift.

4.
Deep HOTSPOT repeated turnover.

5.
Context-only comparison / neutral handling.

6.
Interleaved long-horizon quality
matches:
serial.

7.
Interleaved cumulative error exposure
beats:
serial.

8.
Fine-scale transfer.

9.
Late-life self-recovery.

10.
24-observation per-cycle ceiling.

11.
SMOOTH fidelity.

12.
Oracle ceiling.

ALL PRIMARY GATES PASS.

FINAL INTERPRETATION

H161 is:

POSITIVE.

Under:
the tested synthetic architecture,

repeated cognitive micro-patching
does NOT:
accumulate detectable
functional drift

over:
40 repair cycles

when:
local structural regeneration

is combined with:

- a weak developmental prior;
- bounded local task feedback;
- joint local-state inference;
- persistent repaired state;
- no global retraining;
- no checkpoint restoration
  of:
  lost mutable state.

The strongest architectural result is:

LOCAL SELF-RECOVERY
IS NOT:
A SUFFICIENT
LONG-HORIZON SAFETY METRIC.

CONTEXT-ONLY
can:
repair each local wound
plausibly

while:
original-task fidelity
drifts severely.

Therefore:

a regenerative intelligence system
needs:
an immutable or externally anchored
FUNCTIONAL REFERENCE CHANNEL

against which:
long-horizon capability drift
can be detected.

Functional feedback
serves:
that role
in:
H161.

IMPORTANT SCALE CAVEAT

The primary uses:
40 repair events
at:
every g.

Because:
beta=2 keeps
absolute patch size
approximately constant,

body-equivalent turnover
decreases
as:
the body becomes finer.

Median body-equivalent turnover
under:
INTERLEAVED24:

g=1.00:
approximately 2.03 body equivalents.

g=0.50:
approximately 0.50.

g=0.25:
approximately 0.137.

Median unique-turnover fraction:

g=1.00:
approximately 35.3%.

g=0.50:
approximately 16.6%.

g=0.25:
approximately 8.1%.

Therefore:

H161 strongly supports:

FIXED OPERATIONAL EVENT COUNT
long-horizon stability.

It does NOT yet prove:

MATCHED CUMULATIVE TURNOVER FRACTION
stability

across:
cell scales.

POST-PRIMARY STRESS IS NOW AUTHORIZED

Per:
the preregistration,

the next scoped stress
should match:

approximately one
BODY-EQUIVALENT
cumulative turnover

across:
g.

This specifically tests:

whether:
fine-scale bodies
remain stable

when:
they experience
enough repeated micro-patches

to replace:
an equivalent fraction
of:
their total computational cells.

NEXT:

H162 —
MATCHED BODY-EQUIVALENT
COGNITIVE TURNOVER
SCALE STRESS.

H161 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- global retraining;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
