TITLE: DG-1A-AR-H163 — Intermittent Functional-Anchor / Sparse-Supervision Turnover Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh162-matched-body-equivalent-turnover-stress.ice

PURPOSE

H161 / H162 established:

repeated local cognitive micro-patching
can preserve:
original-task function

through:
fixed-event
and:
matched-body-equivalent
turnover

when:
every repair cycle
may acquire:
up to 24
local task-feedback observations.

That assumption is:
expensive
and:
architecturally strong.

H163 asks:

HOW OFTEN
MUST:
A REGENERATIVE COGNITIVE ORGANISM

RECEIVE:
EXTERNAL FUNCTIONAL ANCHORING

to prevent:
long-horizon drift

when:
most local repairs
must rely first on:
developmental context?

The target is:

SPARSE
FUNCTIONAL SUPERVISION,

not:

continuous:
global retraining.

BOUNDARY

Synthetic research only.

No:
production model repair,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or runtime activation.

PARENT MODEL

Reuse:
H162 matched-body-equivalent
persistent-state turnover.

Context:

MIXED only.

Cell scales:

g =
1.00,
0.25.

Bodies:

approximately:
197,
3209 cells.

Damage:

f0=0.05.

beta=2.

Turnover regimes:

ROAMING,
HOTSPOT.

Feedback eta:

0,
0.25.

LIFETIME

Use:
the same:
approximately one
body-equivalent turnover
lifetime

as:
H162.

g=1.00:

20 cycles.

g=0.25:

292 cycles.

Mutable state:

persists:
cycle to cycle.

No:
global reset.

ANCHOR EVENT

An:
ANCHORED
repair cycle

uses:
the H162
INTERLEAVED24 policy:

- membership regeneration;
- begin:
  functional recalibration
  at:
  50%
  local membership return;
- lambda=0.01;
- 24-observation cap;
- 6 observations / active step;
- global leverage
  query selection;
- expanding joint solve;
- surviving cells fixed.

An:
UNANCHORED
repair cycle

uses:

- the same:
  membership regeneration;
- the same:
  H151 context-harmonic
  initialization / refinement;
- 12 post-membership
  context maturation steps;
- ZERO:
  functional task-feedback observations.

Thus:

unanchored repair is:
not frozen.

It still performs:
developmental regeneration.

It simply lacks:
external functional correction.

ANCHOR CADENCE POLICIES

A — EVERY1

Anchor:
every repair cycle.

This is:
the H162 full-feedback baseline.

B — EVERY2

Anchor:

cycle 1,
3,
5,
...

approximately:
50%
anchor duty cycle.

C — EVERY5

Anchor:

cycle 1,
6,
11,
...

approximately:
20%.

D — EVERY10

Anchor:

cycle 1,
11,
21,
...

approximately:
10%.

E — CONTEXT-ONLY

No:
functional-anchor cycle.

F — LOCAL-CHECKPOINT-ORACLE

Exact immutable
target coefficient

is restored
when:
a lesioned cell returns.

Evaluation ceiling only.

CADENCE RULE

For cadence n:

anchor cycle c
iff:

(c - 1) mod n
=
0.

Cycle 1
is therefore:
anchored
for:
all feedback policies.

No held-out result
may:
change:
the cadence schedule.

FUNCTIONAL FEEDBACK

Anchored cycles:

same:
H162
24-query
local task-feedback mechanism.

Feedback target:

the immutable
original task function.

eta:

0,
0.25.

Unanchored cycles:

receive:
NO:
functional target output.

No policy may:
cache:
raw feedback observations
from:
a previous repair cycle

for:
use
as:
new measurements
inside:
a later wound's solve.

The repaired coefficient state
itself:

does persist.

FEEDBACK COST

Track:

- anchored cycles;
- anchor duty fraction;
- total feedback observations;
- feedback observations
  per:
  body-equivalent turnover.

Maximum:

24 observations
per:
anchored cycle.

PRIMARY FACTORIAL

Cell scale:
2.

Turnover regime:
2.

eta:
2.

Worlds / cell:
15.

Condition-world lifetimes:

2 x 2 x 2 x 15
=
120.

Policies:
6.

Policy lifetimes:

720.

Repair cycles:

g=1:
60 condition-worlds
x
20
x
6
=
7,200.

g=0.25:

60
x
292
x
6
=
105,120.

Total:

112,320 policy repair cycles.

PRIMARY METRICS

1.
FINAL GlobalFidelity;

2.
HALF GlobalFidelity;

3.
minimum post-cycle fidelity;

4.
second-half drift slope;

5.
fraction final >=0.95;

6.
late-life SelfRecovery;

7.
cumulative absolute error exposure;

8.
anchored-cycle count;

9.
anchor duty fraction;

10.
total feedback observations;

11.
feedback observations
per:
body-equivalent turnover;

12.
maximum per-cell
replacement count;

13.
CONTEXT-ONLY drift gap;

14.
coarse / fine transfer;

15.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H163 supports:
SPARSE FUNCTIONAL ANCHORING

if:

1.
EVERY1
reproduces:
H162-level quality.

Specifically:

median FINAL fidelity
>=0.98

and:
>=90%
of worlds
finish >=0.95

for:
every group.

2.
EVERY2:

median FINAL fidelity
>=0.98

for:
every:
g x regime x eta group.

3.
EVERY2:

>=90%
of worlds
finish:
>=0.95

for:
every group.

4.
At least one:
SPARSE policy

EVERY5
or:
EVERY10

achieves:

median FINAL fidelity
>=0.98

for:
every group.

5.
The same qualifying
SPARSE policy

has:
>=90%
of worlds
finish:
>=0.95

for:
every group.

6.
The same qualifying policy

does NOT:
lose:
more than 0.01
median GlobalFidelity

from:
HALF
to:
FINAL

for:
any group.

7.
Fine-scale transfer:

for:
both regimes
and:
both eta classes,

g=0.25
median FINAL fidelity

is:
no more than:
0.01 below:
g=1.00

for:
the qualifying sparse policy.

8.
The qualifying sparse policy

reduces:
total functional-feedback observations

by:
>=70%

relative to:
EVERY1

inside:
both scales.

This means:

EVERY5
or sparser
must qualify

for:
the strongest H163 support.

9.
Late-life SelfRecovery

under:
the qualifying sparse policy

has:
group median
>=0.95

for:
every group.

10.
HOTSPOT:

qualifying sparse policy
median FINAL fidelity
>=0.98

for:
both scales / eta values

under:
naturally repeated
local turnover.

11.
No:
feedback policy

uses:
more than:
24
observations
in:
one anchored cycle.

12.
LOCAL-CHECKPOINT-ORACLE
remains:
the capability ceiling.

SECONDARY DUTY-CYCLE RESULT

If:

EVERY2
passes

but:
EVERY5 / EVERY10
fail,

H163 is:
MIXED-POSITIVE

and:
the measured safe anchor duty
is:
approximately 50%.

If:

EVERY5 passes
but:
EVERY10 fails,

the measured safe anchor duty
is:
approximately 20%.

If:

EVERY10 passes,

the measured safe anchor duty
is:
approximately 10%
or less

and:
a lower-duty follow-up
may be justified.

MIXED / NEGATIVE CONDITIONS

Treat H163 as:
mixed / negative
if:

- every-cycle feedback
  is required;

- sparse anchoring
  preserves:
  local SelfRecovery
  while:
  original-task fidelity
  drifts;

- HOTSPOT turnover
  requires:
  much denser anchoring
  than:
  ROAMING;

- g=0.25
  requires:
  a higher anchor duty
  than:
  g=1.00;

- noisy feedback
  makes:
  sparse anchoring
  unstable;

- unanchored cycles
  need:
  hidden target information
  to:
  remain stable.

PRIMARY WORLD SEEDS

20260921200000
through:
20260921200119.

SANITY WORLD SEEDS

20260921290000...

Sanity:
NON-EVIDENCE.

No:
anchor cadence,
lifetime,
f0,
beta,
cell scale,
regime,
lambda,
feedback budget,
noise level,
or:
acceptance gate

may change
after:
the first held-out H163 lifetime.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_INTERMITTENT_FUNCTIONAL_ANCHOR_TURNOVER

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
