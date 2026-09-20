TITLE: DG-1A-AR-H162 — Matched Body-Equivalent Cognitive Turnover Scale Stress
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh161-long-horizon-cognitive-turnover-drift-audit.ice

PURPOSE

H161 established:

repeated local cognitive micro-patching
can preserve:
original-task function

through:
40 repair events

without:
checkpoint restoration
or:
global retraining.

H161 also exposed:
a scale confound.

Because:
beta=2 localization
keeps:
absolute patch size
approximately constant,

40 repair events equal:

approximately:
2.03 body-equivalent turnover
at:
g=1.00,

0.50
at:
g=0.50,

and:
0.137
at:
g=0.25.

H162 removes:
that confound.

Question:

WHEN
EACH CELL SCALE
EXPERIENCES
APPROXIMATELY ONE
FULL BODY-EQUIVALENT
OF:
CUMULATIVE LOCAL REPLACEMENT,

DOES:
THE SMALL-CELL
COGNITIVE MICRO-PATCH
ARCHITECTURE

STILL:

- preserve original-task fidelity;
- avoid cumulative drift;
- retain the 24-observation repair budget;
- retain START50 interleaving quality;
- avoid fine-scale exposure blow-up?

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
the exact H161
persistent-state turnover mechanics.

Context:

MIXED only.

Cell scales:

g =
1.00,
0.50,
0.25.

Bodies:

approximately:
197,
797,
3209 cells.

Damage:

f0=0.05.

beta=2.

Expected patch sizes:

approximately:
10,
10,
11 cells.

Turnover regimes:

ROAMING,
HOTSPOT.

Feedback eta:

0,
0.25.

Policies:

A —
CONTEXT-ONLY.

B —
SERIAL24.

C —
INTERLEAVED24.

D —
LOCAL-CHECKPOINT-ORACLE.

All policy mechanics:
identical to:
H161.

MATCHED BODY-EQUIVALENT LIFETIME

For each g:

damage count:

k(g) =
ceil(
N(g) * 0.05 * g^2
).

Define:

cycles(g) =
ceil(
N(g) / k(g)
).

Thus:

total replacement events
per lifetime:

cycles(g) * k(g)

is:
at least:
one body cell count.

Frozen expected realization:

g=1.00:

N=197.
k=10.
cycles=20.

body-equivalent turnover:
200 / 197
approximately:
1.015.

g=0.50:

N=797.
k=10.
cycles=80.

body-equivalent turnover:
800 / 797
approximately:
1.004.

g=0.25:

N=3209.
k=11.
cycles=292.

body-equivalent turnover:
3212 / 3209
approximately:
1.001.

No scale:
receives fewer cycles
because:
its per-event repair is easier.

TARGET FUNCTION

Same:
immutable original target field
and:
held-out evaluation function
as:
H161.

Policy mutable state:

persists:
cycle to cycle.

No non-oracle policy
may read:

- lost target coefficients;
- held-out evaluation targets;
- checkpoint state.

Local task feedback:

targets:
the immutable original task function
at:
acquired local query points.

FEEDBACK

lambda:
0.01.

Candidate pool:
64 lesion-local queries.

Global leverage
query selection.

Maximum:
24 observations / cycle.

Batch:
6 / active step.

INTERLEAVED24 begins:
at:
50%
local membership return.

SERIAL24 begins:
after:
100%
membership return.

Surviving coefficients:
fixed
inside:
each cycle.

NOISE

eta:

0,
0.25.

Same:
H161 deterministic
noise-potential rule.

Scale:
per policy / cycle

by:
current lesioned
target-function MSE

as:
declared in H161.

PRIMARY FACTORIAL

Cell scale:
3.

Turnover regime:
2.

eta:
2.

Worlds / cell:
20.

Condition-world lifetimes:

3 x 2 x 2 x 20
=
240.

Policies:
4.

Policy lifetimes:

960.

Total repair cycles:

g=1:
80 condition-worlds
x
20 cycles
x
4 policies
=
6,400.

g=0.50:

80
x
80
x
4
=
25,600.

g=0.25:

80
x
292
x
4
=
93,440.

Total:

125,440 policy repair cycles.

MATCHED-TURNOVER CHECKPOINTS

For each lifetime:

HALF checkpoint:

cycle:
ceil(
cycles(g) / 2
).

FINAL checkpoint:

cycles(g).

Report:

GlobalFidelity
at:
HALF
and:
FINAL.

Also:

drift slope
over:
the second half
of:
the lifetime.

SELF-RECOVERY WINDOW

Report:

median SelfRecovery
over:
the final 25%
of:
repair cycles.

ABSOLUTE ERROR EXPOSURE

Accumulate:
the same H161
target-normalized
absolute functional error exposure.

Because:
body-equivalent turnover
is:
matched,

cross-scale exposure
is now:
directly interpretable

without:
the H161 fixed-event-count caveat.

TURNOVER ACCOUNTING

Track:

- total replacement events;
- body-equivalent turnover;
- unique-turnover fraction;
- maximum cell replacement count;
- >=2,
  >=5,
  >=10,
  >=20
  replacement fractions.

PRIMARY ACCEPTANCE SHAPE

H162 supports:
MATCHED-TURNOVER
SMALL-CELL
COGNITIVE REGENERATION

if:

1.
INTERLEAVED24
median FINAL GlobalFidelity

>=0.98

for:
every:
g x regime x eta group.

2.
>=90%
of:
INTERLEAVED24 worlds

finish:
with:
GlobalFidelity >=0.95

for:
every:
g x regime x eta group.

3.
INTERLEAVED24
median GlobalFidelity

does NOT fall
by:
more than:
0.01

from:
HALF
to:
FINAL

for:
every group.

4.
INTERLEAVED24
median FINAL fidelity

is:
within:
0.01
of:
SERIAL24

for:
every group.

5.
INTERLEAVED24
cumulative absolute error exposure

is:
no more than:
10%
above:
SERIAL24

for:
every group

and:

is lower
in:
at least:
6 of:
12 groups.

6.
Fine-scale final fidelity:

for:
both regimes
and:
both eta classes,

g=0.25
INTERLEAVED24

is:
no more than:
0.01 below:
g=1.00.

7.
Matched-turnover exposure:

for:
both regimes
and:
both eta classes,

g=0.25
INTERLEAVED24
median cumulative
absolute error exposure

is:
no more than:
25%
above:
g=1.00.

8.
INTERLEAVED24
median late-life SelfRecovery

>=0.95

for:
every group.

9.
HOTSPOT:

INTERLEAVED24
median FINAL fidelity
>=0.98

for:
all g / eta

when:
median maximum
per-cell replacement count
exceeds:
10.

If:
a fine-scale HOTSPOT group
does not:
naturally exceed 10

under:
one body-equivalent turnover,

that group is:
reported,
not:
forced.

10.
CONTEXT-ONLY
must NOT:
be used
to:
define success.

If:
CONTEXT-ONLY
drifts,

INTERLEAVED24
should exceed it
by:
>=0.05.

If:
CONTEXT-ONLY
already achieves:
>=0.98,

the group is:
neutral.

11.
No non-oracle policy
uses:
more than:
24 feedback observations
in:
one cycle.

12.
LOCAL-CHECKPOINT-ORACLE
remains:
the capability ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H162 as:
mixed / negative
if:

- fine-scale stability disappears
  once:
  body-equivalent turnover
  is matched;

- hundreds of:
  g=0.25
  micro-patches
  accumulate:
  original-task drift;

- fine-scale cumulative
  absolute error exposure
  grows:
  materially above:
  coarse scale;

- INTERLEAVED24
  accumulates:
  more drift
  than:
  SERIAL24;

- the fixed 24-observation budget
  becomes:
  insufficient
  late in:
  long fine-scale lifetimes;

- local self-recovery
  stays high
  while:
  original-task fidelity
  drifts.

PRIMARY WORLD SEEDS

20260921100000
through:
20260921100239.

SANITY WORLD SEEDS

20260921190000...

Sanity:
NON-EVIDENCE.

No:
cycle formula,
f0,
beta,
g,
regime,
lambda,
feedback budget,
noise level,
or:
acceptance gate

may change
after:
the first held-out H162 lifetime.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_MATCHED_BODY_EQUIVALENT_COGNITIVE_TURNOVER

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
