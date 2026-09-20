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


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — MATCHED BODY-EQUIVALENT STRESS HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H162 HELD-OUT PRIMARY EXECUTION.

PARENT HARNESS

H161:

h161_turnover_reconstructed_v1.py

SHA-256:

ae89e645e9f00f33a581c05298a0b2e930b450bbc9a55f0e0f46f87de86a8248.

H162 WRAPPER

File:

h162_matched_turnover_v1.py

SHA-256:

2a8e405055d88906285934778898b02072dcdf683afd8cbc4d8f392c7461ae2c.

The H162 wrapper:

imports:
the pinned H161 repair mechanics

and changes only:

- lifetime cycle count
  as:
  a deterministic function
  of:
  body size / patch size;

- matched-turnover checkpoints;

- long-lifetime summary metrics.

No H161:

- field generator;
- lesion realization;
- membership rule;
- context rule;
- query pool;
- leverage rule;
- lambda;
- feedback budget;
- feedback-noise rule;
- repair policy

is altered.

MATCHED LIFETIMES

Observed:

g=1.00:

N=197.
damage=10.
cycles=20.
body-equivalent turnover:
approximately 1.01523.

g=0.50:

N=797.
damage=10.
cycles=80.
body-equivalent turnover:
approximately 1.00376.

g=0.25:

N=3209.
damage=11.
cycles=292.
body-equivalent turnover:
approximately 1.00094.

SANITY

Disjoint family:

20260921190000...

6 representative
condition-world lifetimes.

24 policy lifetimes.

Mechanical checks:

- exactly four policies / sanity lifetime;
- matched body-equivalent turnover
  realized at:
  all three scales;
- SERIAL24 / INTERLEAVED24
  never exceed:
  24 observations / cycle;
- LOCAL-CHECKPOINT-ORACLE
  finishes:
  exactly 1.0
  fidelity;
- mutable state persists
  through:
  the complete:
  20 / 80 / 292
  cycle lifetime;
- no global reset.

NON-EVIDENCE SIGNAL

MIXED,
g=1,
ROAMING,
eta=0:

INTERLEAVED24
final fidelity:

approximately:
0.999993.

g=0.50,
ROAMING,
eta=0:

approximately:
0.999983.

g=0.25,
ROAMING,
eta=0:

approximately:
0.999997.

HOTSPOT
maximum single-cell repeat load
in representative sanity:

g=1:
20.

g=0.50:
47.

g=0.25:
56.

INTERLEAVED24
final fidelity remains:

approximately:
0.99996..1.0

in those hotspot sanity lifetimes.

These values are:

NON-EVIDENCE.

No:
cycle formula,
f0,
beta,
cell scale,
turnover regime,
lambda,
feedback budget,
noise level,
sample size,
or:
acceptance gate

was changed.

PRIMARY FAMILY

20260921100000..20260921100239.

240 held-out
condition-world lifetimes.

960 policy lifetimes.

125,440
policy repair cycles.

H162 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H162 lifetime.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — MATCHED BODY-EQUIVALENT TURNOVER STRESS

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-POSITIVE.

FINAL H162 WRAPPER SHA-256

2a8e405055d88906285934778898b02072dcdf683afd8cbc4d8f392c7461ae2c.

PARENT H161 HARNESS SHA-256

ae89e645e9f00f33a581c05298a0b2e930b450bbc9a55f0e0f46f87de86a8248.

ACCEPTED PRIMARY MATRIX SHA-256

e4114b321ec8e26a7b2ae5eb3ed1a3a2d6a0bd313fb875ff017a595715de0b08.

ACCEPTED PRIMARY FAMILY

20260921100000..20260921100239.

PRIMARY MATRIX

240 held-out condition-world lifetimes.

4 policies.

960 policy lifetimes.

Matched turnover:

g=1.00:
20 cycles.

g=0.50:
80 cycles.

g=0.25:
292 cycles.

Total:

125,440 policy repair cycles.

Validation:

- exactly 240 unique held-out seeds;
- exact accepted seed interval;
- exactly four policy rows / seed;
- zero duplicate seed x policy rows;
- no missing accepted seeds;
- no post-primary parameter tuning.

MATCHED BODY-EQUIVALENT TURNOVER

Median realized turnover:

g=1.00:
approximately 1.01523.

g=0.50:
approximately 1.00376.

g=0.25:
approximately 1.00093.

Thus:

cross-scale cumulative replacement load
is:
successfully matched
to:
approximately one body equivalent.

PRIMARY CANDIDATE

INTERLEAVED24.

FINAL FIDELITY

Minimum group median
INTERLEAVED24
FINAL GlobalFidelity

across:
all
g x regime x eta groups:

approximately:
0.999886.

Frozen target:
>=0.98.

PASS:
12 / 12.

WORLD-LEVEL RELIABILITY

Fraction of:
INTERLEAVED24 worlds
finishing:
with:
GlobalFidelity >=0.95:

100%
in:
every group.

Frozen target:
>=90%.

PASS:
12 / 12.

SECOND-HALF DRIFT

Maximum:

median HALF fidelity
minus:
median FINAL fidelity

across:
all groups:

approximately:
4.72e-5.

Frozen limit:
0.01.

PASS.

Thus:

even:
292-cycle
fine-scale lifetimes

do NOT:
show:
meaningful
second-half capability drift.

SERIAL VERSUS INTERLEAVED

Maximum absolute difference
between:
INTERLEAVED24
and:
SERIAL24

group-median
FINAL fidelity:

approximately:
4.1e-8.

Frozen limit:
0.01.

PASS:
12 / 12.

Interleaving therefore:
preserves
matched-turnover
long-horizon quality.

ABSOLUTE ERROR EXPOSURE

INTERLEAVED24
cumulative absolute error exposure

is:
lower
than:
SERIAL24

in:
12 / 12 groups.

INTERLEAVED / SERIAL
median exposure ratio:

approximately:
0.634
to:
0.971.

PASS.

FINE-SCALE FINAL FIDELITY

For:
both:
ROAMING / HOTSPOT

and:
eta=0 / 0.25,

g=0.25
INTERLEAVED24

finishes:
slightly ABOVE

the corresponding:
g=1.00
median fidelity.

PASS:
4 / 4.

MATCHED-TURNOVER
FINE-SCALE ERROR EXPOSURE

g=0.25
INTERLEAVED24

relative to:
g=1.00

median cumulative
absolute error exposure:

ROAMING,
eta=0:
approximately 0.151.

ROAMING,
eta=0.25:
approximately 0.110.

HOTSPOT,
eta=0:
approximately 0.226.

HOTSPOT,
eta=0.25:
approximately 0.135.

Frozen limit:
<=1.25.

PASS:
4 / 4.

Thus:

once:
body-equivalent turnover
is matched,

fine-grained bodies
do NOT:
hide:
a cumulative error-exposure penalty.

They show:
substantially LOWER
absolute target-error exposure
than:
the coarse reference

under:
the beta=2
localized-repair regime.

LATE-LIFE SELF RECOVERY

Minimum group median
INTERLEAVED24
SelfRecovery

over:
the final 25%
of:
each lifetime:

approximately:
0.99819.

Frozen target:
>=0.95.

PASS.

HOTSPOT REPEAT LOAD

Median maximum
single-cell replacement count:

g=1.00:

approximately:
19..20.

g=0.50:

approximately:
49..50.

g=0.25:

approximately:
72..75.5.

All:
naturally exceed:
10.

INTERLEAVED24
median FINAL fidelity
remains:

approximately:
0.99998..1.0.

PASS.

CONTEXT-ONLY COMPARATOR

Most groups are:
neutral
under:
the frozen rule

because:
CONTEXT-ONLY
median FINAL fidelity
already exceeds:
0.98.

Coarse ROAMING:

g=1.00,
eta=0:

CONTEXT-ONLY:
approximately 0.96118.

INTERLEAVED24:
approximately 0.99998.

Gain:
approximately +0.0388.

Frozen comparator margin:
>=0.05.

FAIL.

g=1.00,
eta=0.25:

CONTEXT-ONLY:
approximately 0.94618.

INTERLEAVED24:
approximately 0.99989.

Gain:
approximately +0.0537.

PASS.

Therefore:

Gate 10
fails narrowly
in:
1 / 12 groups.

This miss
does NOT:
indicate:
INTERLEAVED24 drift.

It means:

the preregistered
minimum comparator-margin
was not reached
for:
one:
coarse clean roaming group.

The core matched-turnover
scale-stability hypothesis
remains:
strongly supported.

FEEDBACK CEILING

Maximum:
non-oracle feedback observations
inside:
one cycle:

24.

PASS.

ORACLE

LOCAL-CHECKPOINT-ORACLE:

FINAL GlobalFidelity
exactly:
1.0

through:
the accepted matrix.

PASS.

PREREGISTERED GATE REVIEW

PASS:

1.
FINAL median fidelity.

2.
World-level >=0.95 reliability.

3.
HALF-to-FINAL drift.

4.
Interleaved / serial quality parity.

5.
Interleaved exposure versus serial.

6.
Fine-scale final fidelity transfer.

7.
Matched-turnover
fine-scale exposure transfer.

8.
Late-life SelfRecovery.

9.
HOTSPOT repeat-load stability.

11.
24-observation cycle ceiling.

12.
Oracle ceiling.

FAIL / MIXED:

10.
CONTEXT-ONLY comparator margin.

Observed:
one non-neutral group
at:
+0.0388
versus:
required +0.05.

FINAL INTERPRETATION

H162 is:

MIXED-POSITIVE.

The central question is:
answered positively.

THE SMALL-CELL
COGNITIVE MICRO-PATCH
ARCHITECTURE

REMAINS:
FUNCTIONALLY STABLE

WHEN:
CUMULATIVE TURNOVER
IS MATCHED
ACROSS:
CELL SCALES.

This removes:
the principal scale caveat
from:
H161.

At:
g=0.25,

the organism survives:

292 consecutive
local repair cycles

representing:
approximately one:
full body-equivalent
replacement load

while:

- median original-task fidelity
  remains:
  approximately 1.0;
- every accepted world
  finishes:
  above 0.95 fidelity;
- late-life self-recovery
  remains:
  approximately 1.0;
- no fixed feedback-budget expansion
  is required;
- repeated HOTSPOT cells
  may be:
  replaced:
  more than 70 times
  in:
  the median world;
- cumulative absolute
  target-error exposure
  remains:
  materially BELOW:
  coarse scale.

OUT-OF-BOX ARCHITECTURAL RESULT

Smaller computational cells
do not merely:

permit:
more localized repair.

Under:
the tested beta=2 regime,

they also reduce:

THE ABSOLUTE
FUNCTIONAL DAMAGE
EXPOSED
PER:
BODY-EQUIVALENT
OF:
TURNOVER.

This is:
a stronger result
than:
H160's fixed-event-count scaling.

REMAINING DEPENDENCY

H161 / H162
assume:

every repair cycle
can obtain:

up to:
24 local task-feedback observations

anchored to:
the original target function.

A real regenerative cognitive system
may not always have:

immediate,
dense,
ground-truth
functional feedback.

Therefore:

the next high-leverage risk is:

FUNCTIONAL ANCHOR
AVAILABILITY.

NEXT SCOPED EXPERIMENT

H163 —
INTERMITTENT FUNCTIONAL-ANCHOR /
SPARSE-SUPERVISION TURNOVER AUDIT.

Question:

HOW OFTEN
MUST:
A REGENERATIVE COGNITIVE ORGANISM

RECEIVE:
EXTERNAL FUNCTIONAL ANCHORING

to prevent:
long-horizon drift

when:
most local patches
must rely first on:
developmental context?

Candidate regimes:

- feedback every repair cycle;
- every 2 cycles;
- every 5;
- every 10;
- event-triggered anchor
  from:
  a cheap sentinel error channel.

The primary objective is:

identify:
the minimum external
functional-reference duty cycle

that:
preserves:
the H161/H162
long-horizon stability

without:
turning:
micro-patching

into:
continuous global supervision.

H162 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- global retraining;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
