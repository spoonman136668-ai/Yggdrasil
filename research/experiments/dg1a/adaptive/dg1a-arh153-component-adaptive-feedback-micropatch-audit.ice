TITLE: DG-1A-AR-H153 — Component-Aware Adaptive Functional Feedback Micro-Patch Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh152-context-functional-feedback-micropatch-audit.ice

PURPOSE

H152 established:

bounded local functional feedback
can:
raise MIXED
micro-patch recovery

above:
0.90
at:
the median

with:
24 observations.

H152 also exposed:

FIXED FEEDBACK BUDGETING
IS:
WASTEFUL
AND:
POORLY ROUTED.

At:
1% damage,
24 observations
can be:
12x
the missing coefficient count.

At:
FOUR-PATCH
1% / 2%,
a shared fixed feedback pool
created:
large T90 penalties
relative to:
COMPACT.

H153 asks:

CAN
YGGDRASIL
ALLOCATE
FUNCTIONAL FEEDBACK

BY:
DAMAGED COMPONENT NEED

AND:
STOP
SPENDING
ON:
ALREADY-RECOVERED COMPONENTS?

BOUNDARY

Synthetic research only.

No:
production model,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or:
runtime activation.

PARENT MODEL

Reuse:
H152 / H151
without modification:

- R=8 colony;
- N approximately 197;
- Gaussian RBF sigma=0.22;
- SMOOTH / MIXED / SCRAMBLED state classes;
- 1%,2%,5%,10% lesions;
- COMPACT / FOUR-PATCH;
- p=0.50 membership regeneration;
- H151 context-harmonic prior;
- 12 post-membership maturation steps;
- surviving original coefficients immutable.

COMPONENT DEFINITION

At lesion creation:

compute:
Moore-connected components
of:
the missing-cell set.

Use:
actual connected components,

not:
requested patch count.

Each component owns:
its own
local feedback stream.

COMPONENT FEEDBACK POOL

For each actual lesion component:

pre-generate:
32 local query-target pairs.

Query generation:

- choose:
  one member
  of:
  that component;
- use:
  its normalized response center;
- add:
  Gaussian jitter
  sd=0.12;
- reject:
  outside:
  unit disk.

Target:

pre-lesion function output
at:
that query.

Pools:
are disjoint
from:
held-out evaluation queries.

All feedback observations,
including:
validation observations,
count against:
the feedback budget.

COMPONENT SOLVE

Each damaged component
is solved:
independently.

Only:
coefficients belonging to:
that lesion component

may be updated
by:
that component's feedback.

Ridge objective:

||Phi_C w_C - r_C||^2
+
0.10
||w_C - context_prior_C||^2.

Surviving coefficients:
fixed.

Other lesion components:
use:
their current reconstructed values
when:
computing residual contribution.

No lost original coefficient:
is read.

TRAIN / VALIDATION SPLIT

Within each component's
feedback stream:

odd-numbered acquired observations:
TRAIN.

even-numbered:
VALIDATION.

TRAIN observations:
enter:
the ridge solve.

VALIDATION observations:
do NOT:
enter:
the solve.

They are used only for:
routing
and:
stopping.

COMPONENT VALIDATION ERROR

For one component:

compute:

validation MSE
of:
current output

divided by:

validation MSE
of:
the original lesioned output

on:
the same acquired
component validation queries.

Define:

local residual ratio.

A component is:
VALIDATED_RECOVERED

when:

- it has:
  at least 2 validation observations;

- local residual ratio
  <=0.10;

- this condition holds
  at:
  two consecutive
  post-membership maturation steps.

Once:
VALIDATED_RECOVERED,

the component receives:
no additional feedback

unless:
its residual ratio
later rises:
above 0.15.

This hysteresis:
is frozen.

ROUTING

At each:
post-membership maturation step,

primary adaptive policy
may acquire:
at most 2
new observations total.

Priority:

1.
components with:
no TRAIN observation;

2.
components with:
no VALIDATION observation;

3.
among:
non-validated components,

choose:
highest local residual ratio;

4.
ties:
largest missing coefficient count;

5.
final tie:
lowest component ID.

Two acquisitions
within:
one maturation step
re-evaluate:
priority
after:
the first acquisition.

PRIMARY POLICIES

A — CONTEXT-0

H151 parent.

No:
functional feedback.

B — H152-FIXED-FB2

Frozen H152
CONTEXT-FB2 comparator.

Shared:
24-observation
feedback budget.

No:
component routing.

C — COMPONENT-FIXED-FB2

Context prior.

2 observations / step.

Maximum:
24.

Round-robin:
across actual lesion components.

Per-component:
train / validation split.

No:
adaptive stopping.

Tests:
routing alone.

D — COMPONENT-ADAPTIVE-FB2

PRIMARY CANDIDATE.

Context prior.

Maximum:
2 observations / step.

Maximum:
24 total.

Component-aware:
priority routing.

Validation-based:
early stop.

E — COMPONENT-ADAPTIVE-FB4

Same:
adaptive controller

but:
maximum 4 observations / step

and:
48 total.

Reference for:
whether:
extra budget
still materially improves
reliability.

F — CHECKPOINT-ORACLE

Upper-bound comparator.

PRIMARY FACTORIAL

Context:

SMOOTH,
MIXED,
SCRAMBLED.

Damage:

1%,
2%,
5%,
10%.

Geometry:

COMPACT,
FOUR-PATCH.

100 worlds / cell.

2,400 underlying worlds.

6 policies.

14,400 policy-world evaluations.

PRIMARY METRICS

1.
final functional recovery;

2.
functional T90;

3.
T90-world fraction;

4.
functional downtime;

5.
feedback observations consumed;

6.
feedback observations / missing coefficient;

7.
component count;

8.
components validated recovered;

9.
component stop step;

10.
component reopen count;

11.
routing entropy
across:
components;

12.
final local residual ratio;

13.
COMPACT / FOUR-PATCH gap;

14.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H153 supports:
ADAPTIVE COMPONENT-AWARE
MICRO-PATCH CONTROL

if:

1.
MIXED,
1%..5%:

COMPONENT-ADAPTIVE-FB2
median final recovery
>=0.90.

2.
MIXED,
1%..5%:

T90-world fraction
>=80%

for:
each fraction

and:
>=85%
pooled.

This is:
a staged improvement
from:
H152
50.5%..66%,
not:
a claim
that:
90%
has already been reached.

3.
FOUR-PATCH,
MIXED 1%..5%:

median T90
is:
no more than:
20%
worse
than:
COMPACT.

4.
At:
1% damage,

adaptive FB2
uses:
median
<=8 observations.

5.
At:
2% damage,

adaptive FB2
uses:
median
<=12 observations.

6.
Across:
MIXED 1%..5%,

adaptive FB2
uses:
fewer median observations
than:
H152 fixed FB2

while:
final recovery
is:
no more than:
0.02 lower.

7.
COMPONENT-FIXED-FB2
improves:
FOUR-PATCH
T90
relative to:
H152-FIXED-FB2

in:
at least:
two of:
three
MIXED small-damage fractions.

This isolates:
routing value.

8.
Adaptive FB4
improves:
MIXED pooled T90-world fraction
by:
<0.10 absolute
relative to:
adaptive FB2

OR:

uses:
>1.5x
the feedback observations.

This gate asks:
whether:
FB2 is:
near:
the useful budget frontier.

9.
SMOOTH 1%..5%:

adaptive FB2
median final recovery
>=0.95.

10.
SCRAMBLED
does not:
reach:
SMOOTH-level recovery
under:
adaptive FB2.

MIXED / NEGATIVE CONDITIONS

Treat H153 as:
mixed / negative
if:

- routing does not:
  improve:
  distributed-patch latency;

- adaptive stopping
  cuts:
  feedback too early
  and:
  lowers:
  MIXED final recovery
  below:
  0.90;

- tiny patches
  still consume:
  near:
  24 observations;

- components:
  repeatedly reopen;

- adaptive routing
  starves:
  one component;

- FB4 remains:
  necessary
  for:
  reliable recovery;

- validation queries
  become:
  a hidden unbounded cost.

PRIMARY SEEDS

20260920000000
through:
20260920002399.

SANITY SEEDS

20260920090000
family.

No execution-semantic change
after:
the first held-out H153 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_COMPONENT_ADAPTIVE_FUNCTIONAL_FEEDBACK_MICROPATCH

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false


PRE-PRIMARY IMPLEMENTATION FREEZE 01

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H153 HELD-OUT PRIMARY EXECUTION.

No H153 primary world
has been executed.

H153 SANDBOX HARNESS SHA-256

e8f353f6e5d38a5732eb1c9c47778103134c6d7e331c53efb5b6005974637f71.

PARENT HASHES

H151:
3f6042716b4e5a26f41569376a4dca833f5bae5f3c053aa2280615bfadb32e37.

H152:
e8be77384de4fef8a6b8eda875575f581edfc97794d5060e57e4e3bfa7b3b4e3.

STABLE COMPONENT ORDER

Actual Moore-connected lesion components
are:

- rooted from:
  lowest remaining cell ID;
- traversed with:
  sorted neighbor IDs;
- ordered by:
  lowest member ID.

This makes:
component identity
deterministic.

COMPONENT FEEDBACK RNG

For component c:

SHA-256-derived
from:

world seed,
"component_feedback",
component ID.

32 feedback queries
per:
actual component.

TRAIN / VALIDATION INDEXING

Within a component pool:

0-based even query indices:
TRAIN.

0-based odd:
VALIDATION.

Thus:

first acquisition:
TRAIN.

second:
VALIDATION.

Both:
count against:
feedback budget.

COMPONENT SOLVE

Only:
that component's lesion coefficients
are variables.

All:
surviving cells

and:

all other lesion components
use:
their current coefficients

when:
forming:
the functional residual.

Ridge lambda:

0.10.

Prior:

the current:
context-harmonic
component coefficients.

ADAPTIVE PRIORITY

For each acquisition:

1.
unstopped component
with:
no TRAIN;

2.
unstopped component
with:
no VALIDATION;

3.
otherwise:
highest:
current validation residual ratio;

4.
then:
largest component;

5.
then:
lowest stable component ID.

Priority is:
recomputed
after:
every acquisition.

VALIDATION / STOP

At:
the end of:
each post-membership maturation step,

component residual ratio:

current validation MSE
/
original-lesion validation MSE.

Validated recovered:

>=2 validation observations

AND:

ratio <=0.10

for:
two consecutive
maturation steps.

Reopen:

ratio >0.15.

Reopen count:
is recorded.

COMPONENT-FIXED-FB2

2 observations / maturation step.

24 total maximum.

Round-robin:
stable component order.

No:
early stop.

COMPONENT-ADAPTIVE-FB2

2 observations / step.

24 total maximum.

Adaptive:
routing
and:
stopping.

COMPONENT-ADAPTIVE-FB4

4 observations / step.

48 total maximum.

Same:
routing / stopping.

H152 FIXED COMPARATOR

H152_FIXED_FB2
uses:
the exact frozen H152
shared-pool
CONTEXT-FB2 mechanics.

SANITY

Disjoint:
20260920090000...
family.

Six representative underlying worlds.

NON-EVIDENCE examples:

MIXED 1% COMPACT:

CONTEXT0:
approximately 0.943.

H152 fixed FB2:
approximately 0.991
with:
24 observations.

COMP_ADAPT2:
approximately 0.943
with:
6 observations.

MIXED 1% FOUR:

COMP_ADAPT2:
approximately 0.925
with:
16 observations.

MIXED 5% FOUR:

COMP_ADAPT2:
approximately 0.947
with:
24 observations.

SMOOTH 2% FOUR:

COMP_ADAPT2:
approximately 0.993.

SCRAMBLED 5% FOUR:

COMP_ADAPT2:
approximately 0.

No:
routing rule,
threshold,
budget,
hysteresis,
lambda,
sample size,
or:
acceptance gate

was changed
from:
sanity outcomes.

PRIMARY FAMILY REMAINS

20260920000000..20260920002399.

No execution-semantic change
after:
the first held-out H153 primary world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — COMPONENT-AWARE ADAPTIVE FUNCTIONAL FEEDBACK

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-NEGATIVE.

FROZEN HARNESS SHA-256

e8f353f6e5d38a5732eb1c9c47778103134c6d7e331c53efb5b6005974637f71.

ACCEPTED PRIMARY FAMILY

20260920000000..20260920002399.

PRIMARY MATRIX

2,400 underlying worlds.

6 frozen policies.

14,400 unique policy-world evaluations.

PROVENANCE AUDIT

A post-freeze sandbox script mutation was detected
before:
the affected shard was accepted.

The mutated:
600..899
shard
was:
DISCARDED / NON-EVIDENCE.

The exact frozen H153 harness
was reconstructed
at:
the preregistered SHA-256.

A replay of:
accepted seed 0
was:
byte-for-byte identical
to:
the original accepted output.

Accepted evidence therefore uses only:

- worlds 0..599 from the original exact-hash execution;
- worlds 600..2399 replayed from the restored exact-hash harness.

Final matrix validation:

- exactly 2,400 unique held-out seeds;
- exact seed interval;
- exactly six frozen policies / seed;
- no missing policy cells;
- no duplicate seed-policy cells;
- contaminated seven-policy / theta-bearing shard excluded.

PRIMARY CANDIDATE

COMPONENT-ADAPTIVE-FB2.

MIXED CONTEXT — PRIMARY TARGET

Median final functional recovery:

1%:
0.8802.

2%:
0.8805.

5%:
0.8574.

10%:
0.8691.

Required:
>=0.90
for:
1%..5%.

FAIL.

H152 shared-pool fixed-FB2 comparator
on the same H153 worlds:

1%:
0.9370.

2%:
0.9283.

5%:
0.9235.

Thus:

strict component isolation
REDUCES:
functional recovery

despite:
more explicit routing.

MIXED T90 WORLD FRACTION

COMPONENT-ADAPTIVE-FB2:

1%:
53.5%.

2%:
50.5%.

5%:
41.5%.

Pooled:
48.5%.

Required:

>=80%
each

and:
>=85%
pooled.

FAIL.

H152 shared-pool comparator:

1%:
65.5%.

2%:
63.0%.

5%:
62.5%.

Pooled:
63.67%.

Thus:

component isolation
does not:
solve
the H152 reliability limit.

It worsens it.

FEEDBACK USE

MIXED
COMPONENT-ADAPTIVE-FB2
median observations:

1%:
24.

2%:
24.

5%:
24.

Required:

1%:
<=8.

2%:
<=12.

FAIL.

The adaptive controller
almost always:
spends the full budget
on:
MIXED state.

The stopping rule therefore:
does not discover
a cheap reconstruction regime
for:
the cases that need feedback most.

COMPONENT VALIDATION

Across:
MIXED
1%..5%,

median number
of:
validated-recovered components

under:
COMPONENT-ADAPTIVE-FB2

is:
0.

Median reopen count:

0.

Interpretation:

the problem is NOT:
oscillatory reopening.

The controller simply:
rarely reaches
its component validation criterion
before:
budget exhaustion.

GEOMETRY / ROUTING

MIXED
COMPONENT-ADAPTIVE-FB2.

1%:

COMPACT:
final recovery 0.8887,
T90 5,
T90-world fraction 64%.

FOUR-PATCH:
final recovery 0.8746,
T90 3,
T90-world fraction 43%.

2%:

COMPACT:
final recovery 0.9037,
T90 4.5,
T90-world fraction 76%.

FOUR-PATCH:
final recovery 0.8441,
T90 3,
T90-world fraction 25%.

5%:

COMPACT:
final recovery 0.8722,
T90 7,
T90-world fraction 53%.

FOUR-PATCH:
final recovery 0.8471,
T90 4,
T90-world fraction 30%.

The frozen
FOUR-PATCH median-T90
non-inferiority gate
technically passes

among:
worlds that reach T90.

But:

the T90-world fraction
collapses.

Therefore:

the apparent latency advantage
is:
survivor-selected

and:
does NOT represent
reliable distributed-patch recovery.

ROUTING-ONLY COMPARATOR

COMPONENT-FIXED-FB2
versus:
H152 shared-pool fixed-FB2
on:
FOUR-PATCH
MIXED small damage.

Median T90:

1%:
3
versus:
4.

2%:
4.5
versus:
6.

5%:
5
versus:
9.

Thus:

the preregistered
routing-latency isolation gate
passes
for:
3 / 3 fractions

among:
successful worlds.

However:

T90-world fraction
for:
COMPONENT-FIXED-FB2

is:

44%,
28%,
33%

versus:
H152 shared-pool:

57%,
37%,
57%.

And:
median final recovery
is lower
for:
all three fractions.

Therefore:

routing alone
accelerates:
the easier solved cases

while:
strict component solves
strand:
a larger unsolved tail.

H152 COMPARATOR LOSS

MIXED
COMPONENT-ADAPTIVE-FB2
versus:
H152 fixed-FB2:

1%:

final:
0.8802
versus:
0.9370.

2%:

0.8805
versus:
0.9283.

5%:

0.8574
versus:
0.9235.

Adaptive observations:

24,
24,
24.

H152:

24,
24,
24.

Thus:

H153 does NOT:
use fewer observations

and:

loses:
approximately
0.048..0.066
median recovery.

FAIL.

FB4 FRONTIER

MIXED pooled
1%..5%
T90-world fraction:

ADAPTIVE-FB2:
48.5%.

ADAPTIVE-FB4:
57.67%.

Absolute improvement:

approximately:
9.17 percentage points.

This is:
<0.10.

Therefore:
the frozen
near-budget-frontier
OR gate
technically passes.

Median observations:

FB2:
24.

FB4:
approximately 32..36
by fraction.

But:

FB4
does NOT:
restore:
the missing reliability.

More budget
inside:
the same
component-isolated solve
is:
not the main answer.

SMOOTH CONTEXT

COMPONENT-ADAPTIVE-FB2
median final recovery:

1%:
0.9836.

2%:
0.9851.

5%:
0.9751.

10%:
0.9636.

SMOOTH 1%..5%
all remain:
>=0.95.

PASS.

In:
SMOOTH state,

adaptive stopping
can sometimes:
reduce budget.

However:

this is:
the already-easy
locally smooth regime.

SCRAMBLED CONTEXT

COMPONENT-ADAPTIVE-FB2
median final recovery:

1%:
0.3984.

2%:
0.2001.

5%:
0.3394.

10%:
0.4028.

This remains:
far below:
SMOOTH.

PASS:
mechanism still depends
on:
representational organization.

PREREGISTERED GATE REVIEW

SUPPORTED

1.
FOUR-PATCH median T90
is not:
>20%
worse
than:
COMPACT

among:
successful MIXED worlds.

Qualified:
success fraction is poor.

2.
Routing-only
COMPONENT-FIXED-FB2
has:
lower median T90
than:
H152 fixed FB2
in:
3 / 3
FOUR-PATCH
MIXED small-damage groups.

Qualified:
final recovery
and:
success fraction
are worse.

3.
ADAPTIVE-FB4
improves:
pooled T90-world fraction
by:
<0.10 absolute

relative to:
ADAPTIVE-FB2.

4.
SMOOTH
1%..5%
final recovery
remains:
>=0.95.

5.
SCRAMBLED
does not:
reach:
SMOOTH-level recovery.

FAILED

1.
MIXED
1%..5%
median final recovery
>=0.90.

FAIL.

2.
MIXED
T90-world fraction:

>=80%
each
and:
>=85%
pooled.

FAIL.

3.
1%
median observations
<=8.

FAIL:
24.

4.
2%
median observations
<=12.

FAIL:
24.

5.
Adaptive FB2
uses:
less feedback
than:
H152 fixed FB2

while:
staying within:
0.02 recovery.

FAIL.

It uses:
the same feedback

and:
performs materially worse.

CORE FINDING

H153 is:

MIXED-NEGATIVE.

The failure is:
highly informative.

FUNCTIONAL MICRO-PATCHES
ARE NOT:
INDEPENDENT
MERELY BECAUSE:
THE DAMAGE GEOMETRY
IS DISCONNECTED.

The RBF functional readout
creates:
overlapping influence fields.

Therefore:

a query localized near:
one wound

can still contain:
information about:
coefficients
in:
another wound.

Likewise:

solving:
one lesion component

while:
treating:
other damaged components

as:
fixed current state

creates:
cross-component residual error.

STRICT COMPONENT ISOLATION
THROWS AWAY:
SHARED FUNCTIONAL INFORMATION.

This explains:

- faster T90
  among easy solved components;

- lower total success rate;

- worse median final recovery;

- failure of:
  adaptive early stopping;

- weak benefit
  from:
  simply doubling feedback budget.

ARCHITECTURAL UPDATE

Keep:

COMPONENT-AWARE
QUERY ROUTING.

Reject:

COMPONENT-INDEPENDENT
FUNCTIONAL SOLVES.

The next design should use:

A SHARED
COUPLED
FUNCTIONAL RESIDUAL MODEL

across:
all regenerated cells,

while:

using:
component-specific uncertainty
only to decide:

WHERE
THE NEXT QUERY
SHOULD COME FROM.

In other words:

ROUTE LOCALLY.

SOLVE JOINTLY.

This preserves:
cross-wound information

without:
returning to:
undirected fixed feedback.

NEXT SCOPED EXPERIMENT

H154 —
SHARED-RESIDUAL /
COMPONENT-ROUTED
FUNCTIONAL MICRO-PATCH.

Primary hypothesis:

- maintain:
  one coupled ridge solve
  over:
  all regenerated lesion coefficients;

- estimate:
  per-component validation residual;

- route:
  new functional queries
  toward:
  the highest-uncertainty component;

- scale:
  total feedback budget
  with:
  missing mutable-state dimension;

- stop:
  globally only when:
  every component
  passes:
  bounded validation.

Target:

recover:
H152 shared-solve quality

while:

- eliminating:
  FOUR-PATCH routing waste;

- reducing:
  tiny-patch observation cost;

- raising:
  MIXED T90-world reliability;

- preserving:
  fixed surviving state.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
