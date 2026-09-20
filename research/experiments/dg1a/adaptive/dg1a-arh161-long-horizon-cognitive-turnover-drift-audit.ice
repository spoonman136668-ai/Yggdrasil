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
