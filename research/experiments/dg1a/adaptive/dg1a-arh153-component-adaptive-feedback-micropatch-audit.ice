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
