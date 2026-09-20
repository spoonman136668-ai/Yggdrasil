TITLE: DG-1A-AR-H159 — Interleaved Structural-Functional Micro-Patch Regeneration Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh158-temporal-information-scheduling-micropatch-audit.ice

PURPOSE

H158 established:

front-loading:
the same 24 functional observations

reduces:
post-membership latency

without:
reducing:
final quality
or:
reliability.

But:

the measured gain
is bounded by:
a serial pipeline.

Current pipeline:

1.
regenerate:
all missing membership;

2.
only then:
begin:
functional calibration.

In many H158 worlds:

once membership is complete,
functional T90 is:
only one additional step away.

H159 asks:

CAN
FUNCTIONAL CALIBRATION
BEGIN
WHILE:
THE MICRO-PATCH
IS STILL:
STRUCTURALLY REGENERATING?

The target architecture is:

GROW
AND
RE-SPECIALIZE
CONCURRENTLY.

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
H151/H152/H157/H158.

Colony:

R=8,
N=197.

Gaussian RBF readout:

sigma=0.22.

Contexts:

SMOOTH,
MIXED,
SCRAMBLED.

Damage:

1%,
2%,
5%.

Geometry:

COMPACT,
FOUR-PATCH.

Membership regeneration:

H150/H151 frontier rule.

p=0.50.

Post-membership maturation:

continue until:
12 total maturation-equivalent steps
after:
membership completion,

subject to:
the inherited functional horizon.

FUNCTIONAL FEEDBACK

Candidate pool:

64 H152-style
lesion-local queries.

Fixed developmental-prior authority:

lambda=0.01.

Total observation cap:

24.

Feedback noise:

eta=0
and:
eta=0.25.

QUERY IDENTITY CONTROL

Before:
repair execution,

compute:
one ordered
24-query leverage sequence

using:

- full declared lesion geometry;
- full lesion coefficient column set;
- lambda=0.01;
- basis geometry only.

No:
feedback target
is used
to:
construct this sequence.

Every H159 non-oracle policy
receives:
the same ordered 24 query identities.

Policies differ only in:

WHEN
that sequence
begins to be acquired.

This preserves:
the H158 information-content control.

PARTIAL FUNCTIONAL SOLVE

At any repair step:

only:
lesion cells
whose membership
has already regenerated

may:
receive mutable coefficients
and:
enter the active solve.

Lesion cells
not yet regenerated:

remain:
absent
and:
their output contribution is zero.

Surviving original cells:

remain fixed.

The active joint solve uses:

- all feedback acquired so far;
- all currently regenerated lesion coefficients
  as variables;
- current context-harmonic state
  as:
  the lambda=0.01 ridge prior.

As:
new lesion cells regenerate,

the variable domain expands.

All previous feedback
is reused
inside:
the enlarged solve.

No:
lost original coefficient
is read.

This directly tests:

whether:
early calibrated cells
can safely relinquish:
temporary compensation

as:
missing neighbors
re-enter:
the repair domain.

INTERLEAVING POLICIES

All policies acquire:

6 new observations / active step

until:
the 24-observation cap.

A — START100

Begin functional feedback
only when:

100%
of lesion membership
has regenerated.

Serial baseline.

B — START75

Begin when:

restored lesion fraction
>=75%.

C — START50

Begin when:

restored lesion fraction
>=50%.

D — START25

Begin when:

restored lesion fraction
>=25%.

E — CHECKPOINT-ORACLE

Exact lost coefficient restore
on:
membership return.

Evaluation ceiling only.

START THRESHOLD

Once:
a policy becomes active,

it remains:
feedback-active.

At:
each subsequent repair
or:
maturation step:

1.
membership restoration occurs;

2.
new cells initialize from:
live-neighbor context;

3.
all regenerated lesion cells receive:
one context refinement;

4.
if policy is active:
   acquire:
   up to 6 next queries
   from:
   the frozen common 24-query sequence;

5.
jointly solve:
   all currently regenerated lesion coefficients
   using:
   all acquired feedback.

After:
24 observations
are acquired,

step 5 continues:
every later step

with:
the same 24 observations
and:
the current expanded repair domain.

FUNCTIONAL LATENCY

Report:

FIRST T90

first step
with:
FunctionalRecovery >=0.90.

Also report:

STABLE T90

the earliest step
such that:

FunctionalRecovery >=0.90

and:

never falls below:
0.90
for:
the remainder
of:
the world.

This distinction is:
critical.

An early policy
that temporarily overcompensates
for:
not-yet-regenerated cells

must NOT:
receive full credit
for:
a transient T90 crossing.

REGRESSION METRIC

T90 regression world:

a world where:

FunctionalRecovery
reaches:
>=0.90

and later:
falls below:
0.90.

Also report:

maximum post-crossing drop.

COMMON-WORLD DISCIPLINE

Structural world:

context
x damage
x geometry
x world index.

The same structural seed
is evaluated under:

eta=0
and:
eta=0.25.

All policies share:

- colony;
- coefficient field;
- lesion;
- membership schedule;
- ordered 24-query identity sequence;
- feedback targets
  for:
  matching query / eta;
- held-out evaluation queries.

PRIMARY FACTORIAL

Contexts:
3.

Damage:
3.

Geometry:
2.

Structural worlds / cell:
100.

Structural worlds:

1,800.

Noise classes:

2.

Condition-worlds:

3,600.

Policies:

5.

Executed policy-condition evaluations:

18,000.

PRIMARY METRICS

1.
final functional recovery;

2.
first T50 / T90 / T99;

3.
stable T90;

4.
T90-world fraction;

5.
stable-T90 world fraction;

6.
fraction reaching:
stable T90
before:
membership completion;

7.
functional downtime;

8.
membership completion time;

9.
feedback start step;

10.
observations acquired
by:
membership completion;

11.
feedback observations total;

12.
T90 regression rate;

13.
maximum post-crossing drop;

14.
final held-out MSE ratio;

15.
lesion-weight RMSE,
analysis only;

16.
COMPACT / FOUR interaction;

17.
eta interaction;

18.
query-sequence identity audit;

19.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H159 supports:
INTERLEAVED
STRUCTURAL-FUNCTIONAL
MICRO-PATCH REGENERATION

if:

1.
START100 baseline,
MIXED 1%..5%:

median final recovery
>=0.97
for:
eta=0

and:
>=0.95
for:
eta=0.25.

2.
START100
stable-T90 world fraction:

>=0.90
for:
all six
MIXED
eta x damage groups.

3.
At least one:
early policy

START75,
START50,
or:
START25

reduces:
MIXED FOUR-PATCH
median STABLE T90

by:
>=20%
relative to:
START100

in:
at least:
two of three
damage fractions
for:
eta=0

and:
at least:
two of three
for:
eta=0.25.

4.
The same policy
does NOT reduce:
stable-T90 world fraction

by:
more than:
3 percentage points

relative to:
START100

in:
any:
MIXED eta x damage group.

5.
The same policy
does NOT reduce:
median final recovery

by:
more than:
0.02

relative to:
START100

in:
any:
MIXED eta x damage group.

6.
The same policy
reduces:
MIXED FOUR-PATCH
median functional downtime

by:
>=15%

in:
at least:
four of:
six eta x damage groups.

7.
T90 regression rate
under:
the same early policy

is:
<=10%

for:
every:
MIXED eta x damage group.

8.
The same early policy
reaches:
stable T90

before:
membership completion

in:
>=20%
of:
MIXED FOUR-PATCH worlds

for:
at least:
two of three
damage fractions
under:
eta=0.

This gate establishes:
true pipeline overlap,

not:
merely:
faster post-membership solving.

9.
Every non-oracle policy
uses:
the identical ordered
24-query identity sequence

inside:
every accepted structural world.

10.
SMOOTH 1%..5%
median final recovery
under:
the qualifying early policy

>=0.98
for:
both eta classes.

11.
CHECKPOINT-ORACLE
remains:
the ceiling.

POLICY SELECTION RULE

If:
multiple early policies
pass:
all gates,

select:

the policy with:
largest pooled reduction
in:
MIXED FOUR-PATCH
median stable T90.

Tie:

prefer:
the later start threshold

to:
minimize:
early-repair coupling.

MIXED / NEGATIVE CONDITIONS

Treat H159 as:
mixed / negative
if:

- early calibration
  is erased
  when:
  new cells join;

- temporary compensation
  creates:
  frequent T90 regression;

- early policies
  lower:
  final recovery;

- no policy
  reaches:
  stable T90
  before:
  membership completion;

- eta=0.25
  removes:
  the interleaving advantage;

- the final query sequence
  differs:
  across policies;

- START25
  behaves like:
  unstable partial-model overfitting.

PRIMARY STRUCTURAL SEEDS

20260920800000
through:
20260920801799.

Noise eta:
deterministic domain
on:
the same structural seed.

SANITY STRUCTURAL SEEDS

20260920890000...

Sanity outputs:
NON-EVIDENCE.

No:
start threshold,
batch size,
lambda,
noise level,
query sequence,
budget,
or:
acceptance gate

may change
after:
the first held-out H159 condition-world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_INTERLEAVED_STRUCTURAL_FUNCTIONAL_MICROPATCH

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — INTERLEAVED REGENERATION HARNESS

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H159 HELD-OUT PRIMARY EXECUTION.

FINAL H159 SANDBOX HARNESS

File:

h159_interleaved_frozen_v1.py

SHA-256:

a38c58d2a15cb7125dc3e02199ea8bbd0de0e14c937e1e7e6d87c13d54ba99e8.

PARENT MECHANICS

H151:
3f6042716b4e5a26f41569376a4dca833f5bae5f3c053aa2280615bfadb32e37.

H152:
e8be77384de4fef8a6b8eda875575f581edfc97794d5060e57e4e3bfa7b3b4e3.

H159:

lambda=0.01.

Total feedback cap:
24.

Acquisition batch:
6 observations / active step.

COMMON QUERY SEQUENCE

For each structural world:

one ordered:
24-query
global-leverage sequence

is computed
before:
repair execution

using:

- full lesion geometry;
- full lesion coefficient column set;
- lambda=0.01;
- basis geometry only.

No feedback target
enters:
query sequence construction.

START100,
START75,
START50,
START25

all use:
the identical ordered sequence.

PARTIAL SOLVE

At:
each repair / maturation step:

1.
scheduled membership returns;

2.
new cells initialize:
from live-neighbor context;

3.
all regenerated lesion cells:
context-refine;

4.
if:
the policy's membership threshold
has been reached,

acquire:
the next:
up to 6
query-target pairs;

5.
jointly solve:
ALL currently regenerated lesion coefficients

using:
all acquired feedback

and:
the current context state
as:
lambda=0.01 prior.

Not-yet-regenerated lesion cells:

remain:
absent
with:
zero output contribution.

Surviving original cells:

remain fixed.

As:
new cells join,

the joint variable domain expands

and:
all prior feedback
is reused.

STABLE T90

STABLE T90
is:
the first step
at which:

FunctionalRecovery >=0.90

and:

all subsequent steps
remain:
>=0.90.

T90 REGRESSION

A world is:
T90_REGRESSION

when:

first T90 is reached

and:

a later step
falls:
below 0.90.

Maximum post-crossing drop
is:
peak-minus-trough recovery
from:
the first T90 step onward.

PRE-PRIMARY GATE-8 CLARIFICATION

Sanity revealed:

START100
can occasionally reach:
stable T90

before:
formal membership completion

from:
context / surviving-function recovery alone,

even though:
START100 feedback
has not yet begun.

Therefore:

the preregistered Gate 8 phrase:

"true pipeline overlap"

is operationalized as:

an early policy world counts
toward:
the >=20%
overlap fraction

only when:

1.
the early policy reaches:
STABLE T90
before:
membership completion;

AND

2.
its STABLE T90
is:
at least one full step earlier
than:
the paired START100 world

with:
the same structural seed
and:
eta.

This clarification:

does NOT change:
the 20% threshold,
the damage groups,
the eta requirement,
or:
any policy behavior.

It prevents:
context-only pre-completion recovery
from being mislabeled as:
an interleaving benefit.

SANITY

Disjoint structural family:

20260920890000...

140 structural worlds.

280 eta condition-worlds.

1,400 policy-condition evaluations.

Mechanical checks:

- exact 5 policies / condition;
- zero common-query-sequence mismatches;
- only regenerated lesion coefficients
  enter:
  non-oracle solves;
- missing lesion cells
  remain:
  absent;
- surviving original coefficients
  remain:
  fixed;
- no functionally-trivial world observed.

NON-EVIDENCE SIGNAL

Representative MIXED FOUR-PATCH:

2% eta=0:

START100
median stable T90:
4.

START75:
3.

START50:
3.

START25:
3.

2% eta=0.25:

START100:
4.

START75:
3.

START50:
3.

START25:
3.

5% eta=0:

START100:
4.5.

START75:
3.

START50:
2.

START25:
2.

5% eta=0.25:

START100:
5.

START75:
3.

START50:
2.

START25:
2.

No representative sanity group
showed:
material final-recovery loss
or:
T90 regression.

These outputs are:
NON-EVIDENCE.

No:
start threshold,
batch size,
lambda,
noise level,
query sequence,
budget,
sample size,
or:
acceptance threshold

is changed.

PRIMARY STRUCTURAL FAMILY

20260920800000..20260920801799.

1,800 held-out structural worlds.

3,600 eta condition-worlds.

18,000 policy-condition evaluations.

H159 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H159 condition-world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
