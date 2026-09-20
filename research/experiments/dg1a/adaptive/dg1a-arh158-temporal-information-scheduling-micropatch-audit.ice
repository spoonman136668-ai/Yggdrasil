TITLE: DG-1A-AR-H158 — Temporal Information Scheduling / Front-Loaded Functional Micro-Patch Feedback Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh157-adaptive-prior-authority-audit.ice

PURPOSE

H157 established:

the tested micro-patch inverse problem
does NOT benefit from:
increasing developmental-prior authority
as local feedback becomes noisier.

Both:
local LOOCV
and:
the non-deployable oracle-lambda diagnostic

selected:
lambda approximately 0.01

through:
eta=0.25.

H157 also established:

24 information-designed local observations
can produce:
high final recovery
and:
high T90-world reliability.

The remaining issue is:
LATENCY,
especially:
for distributed multi-wound repair.

H158 asks:

WITH:
THE SAME 24 LOCAL OBSERVATIONS,
THE SAME QUERY DESIGN,
AND:
THE SAME WEAK PRIOR,

DOES:
ACQUIRING INFORMATION EARLIER

REDUCE:
FUNCTIONAL MICRO-PATCH LATENCY

WITHOUT:
SACRIFICING
FINAL QUALITY
OR:
RELIABILITY?

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
H151/H152/H156/H157.

Colony:
R=8,
N=197.

Gaussian RBF readout:
sigma=0.22.

Membership repair:
p=0.50.

Post-membership maturation:
12 steps.

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

FEEDBACK

Local H152-style candidate pool:
64 queries.

Feedback target noise:

eta=0
and:
eta=0.25.

Noise scaling and common-policy discipline:
reuse H157.

All non-oracle policies use:

global leverage /
greedy D-optimal query selection.

Fixed developmental-prior strength:

lambda=0.01.

Maximum acquired observations:

24.

TEMPORAL POLICIES

A — EVEN2

2 new observations
per:
maturation step

for:
12 steps.

Schedule:

2 x 12.

This is:
the evenly distributed weak-prior baseline.

B — FRONT4

4 new observations
per step

for:
6 steps,

then:
no new observations
for:
6 steps.

Schedule:

4 x 6.

C — FRONT6

6 new observations
per step

for:
4 steps,

then:
8 no-acquisition steps.

D — FRONT8

8 new observations
per step

for:
3 steps,

then:
9 no-acquisition steps.

E — FRONT12

12 new observations
per step

for:
2 steps,

then:
10 no-acquisition steps.

F — BURST24

24 observations
at:
the first post-membership maturation step,

then:
11 no-acquisition steps.

G — CHECKPOINT-ORACLE

Exact lost coefficient restore.

Evaluation ceiling only.

CRITICAL CONTROL

All non-oracle policies:

- use the same lambda=0.01;
- select queries by the same leverage rule;
- have the same 24-observation cap;
- receive the same candidate pool;
- receive the same noisy target potential;
- alter only regenerated lesion coefficients;
- keep surviving original coefficients fixed.

Because:
query selection depends only on:
basis geometry,
selected-query identity,
and:
fixed lambda,

the first 24 selected query identities
should be identical
across:
A..F.

This equality is:
a mechanical audit gate.

The experiment therefore isolates:
ACQUISITION TIME.

POST-ACQUISITION RE-SOLVE

At every:
post-membership maturation step:

1.
apply:
one H151 context-harmonic refinement step;

2.
acquire:
the policy-declared number
of:
new local observations,
subject to:
the 24 cap;

3.
solve:
all regenerated lesion coefficients
jointly
using:
ALL observations acquired so far

with:
lambda=0.01
and:
the current context state
as:
the ridge prior.

If:
a policy has already acquired
all 24 observations,

step 3 still runs
using:
the same 24 observations
and:
the current developmental prior.

Thus:

front-loading changes:
when evidence becomes available,

not:
whether accumulated evidence
can continue to constrain:
later maturation.

COMMON-WORLD DISCIPLINE

Primary structural world:

context
x damage
x geometry
x world index.

Each structural world
is evaluated under:

eta=0
and:
eta=0.25

using:
the same colony,
coefficient field,
lesion,
membership schedule,
candidate query geometry,
and:
held-out evaluation queries.

Only:
the feedback-noise potential
changes by:
eta domain.

All temporal policies
within:
one eta condition

receive:
identical noisy feedback targets
for:
matching query IDs.

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

3 x 3 x 2 x 100
=
1,800.

Noise classes:
2.

Condition-worlds:
3,600.

Policies:
7.

Executed policy-condition evaluations:

25,200.

PRIMARY METRICS

1.
final functional recovery;

2.
T50,
T90,
T99;

3.
T90-world fraction;

4.
functional downtime;

5.
membership completion time;

6.
step reaching:
12 acquired observations;

7.
step reaching:
24 acquired observations;

8.
observations acquired / step;

9.
final held-out MSE ratio;

10.
lesion-weight RMSE,
analysis only;

11.
COMPACT / FOUR-PATCH interaction;

12.
eta interaction;

13.
query-set identity hash;

14.
final query-set equality
across:
A..F;

15.
oracle gap.

PRIMARY QUESTIONS

Q1.

Does:
front-loading
the same information

reduce:
functional T90

for:
distributed micro-patches?

Q2.

Is:
moderate front-loading

better than:
an all-at-once
24-query burst

because:
developmental context
continues to mature?

Q3.

Does:
front-loading
preserve:
the high H157 reliability

under:
eta=0.25?

Q4.

Does:
earlier evidence
reduce:
functional downtime

even when:
final recovery
is unchanged?

PRIMARY ACCEPTANCE SHAPE

H158 supports:
TEMPORALLY FRONT-LOADED
FUNCTIONAL MICRO-PATCH FEEDBACK

if:

1.
EVEN2 baseline,
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
EVEN2 baseline,
MIXED 1%..5%:

T90-world fraction
>=0.90
for:
all six
eta x damage groups.

3.
At least one:
MODERATE FRONT-LOAD policy

from:
FRONT4,
FRONT6,
FRONT8

reduces:
FOUR-PATCH
MIXED
median functional T90

by:
>=20%
relative to:
EVEN2

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
The same qualifying policy
does NOT reduce:
MIXED T90-world fraction

by:
more than:
3 percentage points

relative to:
EVEN2

in:
any:
eta x damage group.

5.
The same qualifying policy
does NOT reduce:
MIXED median final recovery

by:
more than:
0.02

relative to:
EVEN2

in:
any:
eta x damage group.

6.
The same qualifying policy
reduces:
MIXED FOUR-PATCH
median functional downtime

by:
>=15%

in:
at least:
four of:
the six
eta x damage groups.

7.
All non-oracle temporal policies
finish with:
the same 24 query identities

inside:
every accepted world.

Any mismatch:
invalidates:
the timing-only interpretation.

8.
SMOOTH 1%..5%
median final recovery
under:
the qualifying policy
remains:
>=0.98
for:
both noise classes.

9.
CHECKPOINT-ORACLE
remains:
the ceiling.

SCHEDULE SELECTION RULE

If:
multiple moderate front-load policies
pass:
all gates,

select:

the policy with:
largest median
MIXED FOUR-PATCH
functional-downtime reduction

pooled across:
damage and eta.

Tie:

choose:
the smaller acquisition batch.

This rule is:
frozen before primary.

DIAGNOSTIC EXTREMES

FRONT12
and:
BURST24

are:
stress comparators.

A result where:

moderate front-loading passes

but:
BURST24 degrades

supports:
a temporal-information knee

rather than:
"earlier is always better."

MIXED / NEGATIVE CONDITIONS

Treat H158 as:
mixed / negative
if:

- earlier acquisition
  does not reduce:
  multi-wound T90;

- reliability falls
  as:
  evidence is front-loaded;

- final recovery drops
  because:
  later context maturation
  erases:
  early functional correction;

- BURST24 is required
  for:
  meaningful latency improvement;

- eta=0.25
  removes:
  the latency advantage;

- query sets differ
  across temporal policies,
  confounding:
  timing with:
  information content.

PRIMARY STRUCTURAL SEEDS

20260920700000
through:
20260920701799.

One seed
per:
structural world.

Noise eta
is:
a deterministic domain
applied to:
the same structural seed.

SANITY STRUCTURAL SEEDS

20260920790000...

Sanity outputs:
NON-EVIDENCE.

No:
schedule,
lambda,
noise level,
query rule,
budget,
or:
acceptance gate

may change
after:
the first held-out H158 primary condition-world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_TEMPORAL_INFORMATION_SCHEDULING_MICROPATCH

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — TEMPORAL SCHEDULING HARNESS

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H158 HELD-OUT PRIMARY EXECUTION.

DISCARDED SANDBOX DRAFT

A concurrent pre-primary draft:

h158_temporal_schedule_frozen_v1.py

is:
NON-EVIDENCE /
NOT THE H158 HARNESS.

It differed from:
the preregistration by:

- using A-optimal rather than leverage selection;
- omitting eta=0.25;
- adding CONTEXT0 as an extra primary policy;
- using the wrong sanity seed family.

No H158 held-out primary world
was executed
under:
that draft.

FINAL H158 SANDBOX HARNESS

File:

h158_temporal_schedule_frozen_v2.py

SHA-256:

af3af9f9c1fa8b8e550578150db5a29fdea822f5dd7dce7755c0f84b5032698e.

PARENT MECHANICS

H151:
3f6042716b4e5a26f41569376a4dca833f5bae5f3c053aa2280615bfadb32e37.

H152:
e8be77384de4fef8a6b8eda875575f581edfc97794d5060e57e4e3bfa7b3b4e3.

H158 fixed prior:

lambda=0.01.

Query design:

global leverage /
greedy D-optimal proxy.

Feedback cap:

24.

SCHEDULES

EVEN2:
2 x 12.

FRONT4:
4 x 6.

FRONT6:
6 x 4.

FRONT8:
8 x 3.

FRONT12:
12 x 2.

BURST24:
24 x 1.

After:
all 24 observations
have been acquired,

every later maturation step
still:

- performs context refinement;
- re-solves the coupled lesion coefficients
  using:
  all 24 accumulated observations
  and:
  the current context prior.

Thus:

information remains:
an active constraint

after:
acquisition stops.

NOISE

eta:

0,
0.25.

Noise is:
deterministic
from:
structural world seed,
eta domain,
and:
query identity.

All timing policies
receive:
the same observed target
for:
the same query
inside:
one condition-world.

COMMON STRUCTURAL WORLDS

The same structural seed
is evaluated
at:
both eta values.

Thus:

noise-class comparisons
share:

- colony;
- learned field;
- lesion;
- membership schedule;
- candidate query geometry;
- evaluation queries.

SANITY

Structural seed family:

20260920790000...

140 structural worlds.

280 condition-worlds.

1,960 policy-condition evaluations.

Mechanical checks:

- exactly 7 policies / condition;
- all sanity conditions complete;
- zero query-set hash mismatches
  among:
  EVEN2,
  FRONT4,
  FRONT6,
  FRONT8,
  FRONT12,
  BURST24;
- all non-oracle policies acquire:
  exactly 24 observations;
- no policy modifies:
  surviving original coefficients;
- no functionally-trivial sanity world observed.

NON-EVIDENCE SIGNAL

Representative MIXED FOUR-PATCH sanity:

2%,
eta=0:

EVEN2 median T90:
5.

FRONT6 / FRONT8:
4.

2%,
eta=0.25:

EVEN2:
5.

FRONT8:
4.

5%,
eta=0:

EVEN2:
6.

FRONT4..BURST24:
approximately 5.

5%,
eta=0.25:

EVEN2:
6.

FRONT4..BURST24:
approximately 5.

Median final recovery
remained:
essentially unchanged

inside:
these representative sanity cells.

No:
schedule,
threshold,
lambda,
noise level,
sample size,
or:
acceptance gate

was changed
from:
sanity outcomes.

PRIMARY STRUCTURAL FAMILY

20260920700000..20260920701799.

1,800 held-out structural worlds.

3,600 eta condition-worlds.

25,200 policy-condition evaluations.

H158 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H158 condition-world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — TEMPORAL SCHEDULING HARNESS

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H158 HELD-OUT PRIMARY EXECUTION.

FINAL PINNED EXECUTABLE

h158_temporal_schedule_frozen_v2.py

SHA-256:

af3af9f9c1fa8b8e550578150db5a29fdea822f5dd7dce7755c0f84b5032698e.

IMPLEMENTATION

lambda:
0.01.

Query design:

global leverage /
greedy D-optimal.

Candidate pool:

64 H152-style
lesion-local queries.

All non-oracle temporal policies:

- consume exactly 24 queries;
- select the same query identities;
- alter only acquisition cadence;
- retain every acquired query
  as:
  an active constraint;
- re-solve:
  the full lesion coefficient vector
  after:
  every post-membership
  context-refinement step.

Schedules:

EVEN2:
2 x 12.

FRONT4:
4 x 6.

FRONT6:
6 x 4.

FRONT8:
8 x 3.

FRONT12:
12 x 2.

BURST24:
24 x 1.

Feedback noise:

eta=0
and:
eta=0.25.

Noise potential:

deterministic
per:
structural seed
and:
eta domain.

Held-out evaluation:
noise-free.

CORRECTED SANITY MATRIX

Disjoint structural family:

20260920790000...

7 declared structural cells.

20 worlds / cell.

2 noise classes.

7 policies.

140 structural worlds.

280 condition-worlds.

1,960 policy-condition evaluations.

Validation:

- exact declared matrix;
- zero functionally-trivial worlds;
- all A..F temporal policies
  finish with:
  identical 24-query hashes
  inside:
  every sanity condition;
- accumulated feedback
  remains active
  after:
  acquisition ends;
- ORACLE remains:
  evaluation-only.

NON-EVIDENCE SANITY SIGNAL

MIXED 1% FOUR:

eta=0:

EVEN2 median T90:
5.

FRONT4:
4.5.

FRONT6:
4.

FRONT8:
4.

FRONT12:
4.

BURST24:
3.5.

eta=0.25:

EVEN2:
5.

FRONT4:
4.

FRONT6:
3.

FRONT8:
3.

FRONT12:
3.

BURST24:
3.

MIXED 2% FOUR:

eta=0:

EVEN2:
5.

FRONT4:
4.5.

FRONT6:
4.

FRONT8:
4.

eta=0.25:

EVEN2:
5.

FRONT4:
4.5.

FRONT6:
4.5.

FRONT8:
4.

MIXED 5% FOUR:

EVEN2:
6

versus:

FRONT4:
5

for:
both noise classes.

Median final recovery
remained:
effectively unchanged

between:
EVEN2
and:
front-loaded schedules.

The sanity matrix
therefore supports:
executing the already-preregistered
temporal hypothesis.

No:
schedule,
lambda,
noise level,
query rule,
budget,
sample size,
or:
acceptance gate
is changed.

PRIMARY FAMILY

20260920700000..20260920701799.

Repository / sandbox check:

no H158 held-out primary output
from:
this family
exists
at:
this freeze.

No execution-semantic change
is permitted
after:
the first accepted H158 primary condition-world.

H158 accepted primary status:

NOT STARTED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — TEMPORAL INFORMATION SCHEDULING

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-NEGATIVE FOR PREREGISTERED FRONT-LOAD MAGNITUDE / POSITIVE LATENCY SIGNAL.

FINAL PINNED HARNESS SHA-256

af3af9f9c1fa8b8e550578150db5a29fdea822f5dd7dce7755c0f84b5032698e.

ACCEPTED PRIMARY STRUCTURAL FAMILY

20260920700000..20260920701799.

PRIMARY MATRIX

1,800 held-out structural worlds.

2 feedback-noise classes.

3,600 condition-worlds.

7 policies.

25,200 policy-condition evaluations.

Validation:

- exactly 1,800 unique structural seeds;
- exactly 3,600 seed x eta conditions;
- exactly seven policy rows / condition;
- zero functionally-trivial worlds;
- zero final query-set hash mismatches
  among:
  EVEN2,
  FRONT4,
  FRONT6,
  FRONT8,
  FRONT12,
  BURST24;
- all timing policies consume:
  the same 24 final query identities;
- no post-primary parameter tuning.

EVEN2 BASELINE

MIXED pooled geometry.

eta=0:

1%:
median final recovery 0.9973.
T90-world fraction 96.0%.

2%:
0.9916.
97.5%.

5%:
0.9952.
100%.

eta=0.25:

1%:
0.9972.
95.5%.

2%:
0.9904.
97.5%.

5%:
0.9936.
100%.

Baseline quality / reliability gates:

PASS.

FOUR-PATCH TEMPORAL RESULT

MIXED eta=0.

Median functional T90:

1%:
EVEN2 4.
FRONT4 3.
FRONT6 3.
FRONT8 3.
FRONT12 3.
BURST24 3.

2%:
EVEN2 6.
FRONT4 5.
FRONT6 5.
FRONT8 5.
FRONT12 4.
BURST24 4.

5%:
EVEN2 6.
FRONT4 5.5.
FRONT6 5.
FRONT8 5.
FRONT12 5.
BURST24 5.

MIXED eta=0.25.

1%:
EVEN2 4.
FRONT4 3.
FRONT6 3.
FRONT8 3.
FRONT12 3.
BURST24 3.

2%:
EVEN2 6.
FRONT4 5.
FRONT6 5.
FRONT8 5.
FRONT12 4.
BURST24 4.

5%:
EVEN2 6.
FRONT4 5.
FRONT6 5.
FRONT8 5.
FRONT12 5.
BURST24 5.

Thus:

earlier evidence
does:
reduce latency.

But:

FRONT4,
FRONT6,
and:
FRONT8

reach:
the preregistered >=20%
median-T90 improvement

in only:
1 / 3
damage fractions
per noise class.

Required:
2 / 3
for:
both eta classes.

FAIL.

RELIABILITY

For:
all MIXED
eta x damage groups,

front-loaded policies
retain:
essentially the same
T90-world fraction
as:
EVEN2.

No moderate schedule
loses:
>3 percentage points.

PASS.

FINAL RECOVERY

Median final recovery
is:
effectively invariant
across:
the temporal policies.

No moderate schedule
loses:
>0.02
relative to:
EVEN2.

PASS.

FUNCTIONAL DOWNTIME

FOUR-PATCH
median downtime reduction
relative to:
EVEN2.

FRONT4:

>=15%
in:
1 / 6
eta x damage groups.

FRONT6:

2 / 6.

FRONT8:

2 / 6.

Required:

4 / 6
for:
the same qualifying
moderate schedule.

FAIL.

Diagnostic extremes:

FRONT12
and:
BURST24

provide:
larger latency / downtime reductions

without:
material quality loss.

But:

even these extremes
do not establish:
the preregistered
moderate-schedule
downtime gate.

NO TEMPORAL QUALITY PENALTY

The feared failure:

early evidence
being erased by:
later context maturation

is:
NOT observed.

Because:

accumulated functional evidence
remains:
an active constraint
and:
the lesion is re-solved
after:
each later context step,

front-loaded correction
remains stable.

SMOOTH CONTROL

Across:
1%..5%
and:
eta=0 / 0.25,

EVEN2,
FRONT8,
and:
BURST24

all retain:
median final recovery
approximately:
0.9990..0.9998.

No smooth-state destabilization.

CHECKPOINT-ORACLE

Remains:
the final-recovery ceiling
at:
1.0.

PRIMARY ACCEPTANCE REVIEW

PASS:

1.
EVEN2 final-quality baseline.

2.
EVEN2 T90 reliability baseline.

4.
Front-loading does not:
materially reduce reliability.

5.
Front-loading does not:
materially reduce final recovery.

7.
Timing-only query identity control.

8.
SMOOTH quality.

9.
ORACLE ceiling.

FAIL:

3.
Moderate front-loading
does not reach:
the frozen >=20%
FOUR-PATCH T90 reduction
in:
2 / 3
damage fractions
for:
each noise class.

6.
Moderate front-loading
does not reach:
the frozen >=15%
downtime reduction
in:
4 / 6
eta x damage groups.

FINAL INTERPRETATION

H158 is:

MIXED-NEGATIVE
for:
the preregistered
front-loading effect size.

But:

the directional result
is:
clean and useful.

EARLIER INFORMATION
DOES:
HELP.

It does so:

- without changing:
  final query content;
- without increasing:
  observation count;
- without reducing:
  reliability;
- without reducing:
  final recovery;
- without becoming fragile
  at:
  eta=0.25.

The reason H158
does not become:
a strong positive

is:
a LATENCY FLOOR.

For:
FOUR-PATCH MIXED worlds,

membership completion itself
typically consumes:

approximately:
2 steps
at:
1%,

3 steps
at:
2%,

and:
4..5 steps
at:
5%.

After:
membership completion,

front-loaded policies
often reach:
functional T90

within:
the first:
post-membership step.

Thus:

there is:
little remaining
post-membership latency
for:
temporal scheduling alone
to remove.

ARCHITECTURAL CONSEQUENCE

The next experiment
should NOT:

increase:
the feedback budget,

or:
front-load:
more aggressively.

H158 indicates:

the structural / functional pipeline
is now:
serially gated.

Current order:

1.
finish:
membership regeneration;

2.
then:
begin:
functional evidence correction.

The next high-leverage question is:

CAN
FUNCTIONAL CALIBRATION
BEGIN
WHILE:
MEMBERSHIP IS STILL
REGENERATING?

That would overlap:

STRUCTURAL REGENERATION

with:

FUNCTIONAL SPECIALIZATION
RECOVERY.

NEXT SCOPED EXPERIMENT

H159 —
INTERLEAVED STRUCTURAL-FUNCTIONAL
MICRO-PATCH REGENERATION.

Primary direction:

- same lambda=0.01;
- same 24-observation cap;
- same leverage query design;
- permit feedback only for:
  currently regenerated lesion support;
- progressively expand:
  the coupled solve
  as:
  new cells reappear;
- compare:
  feedback start at:
  25%,
  50%,
  75%,
  100%
  membership restoration;
- measure:
  end-to-end T90
  and:
  whether early partial solves
  remain stable
  as:
  the repair domain grows.

H158 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
