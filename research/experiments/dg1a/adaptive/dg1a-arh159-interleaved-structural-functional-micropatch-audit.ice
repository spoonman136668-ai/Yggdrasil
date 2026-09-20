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
