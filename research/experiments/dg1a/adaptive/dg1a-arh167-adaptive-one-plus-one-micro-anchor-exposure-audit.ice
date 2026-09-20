TITLE: DG-1A-AR-H167 — Adaptive One-Plus-One Micro-Anchor Exposure-Control Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh166-minimal-micro-anchor-budget-turnover-audit.ice

PURPOSE

H166 established:

- two local functional observations
  every repair cycle
  are:
  exposure-safe;

- one observation
  every repair cycle
  preserves:
  end-state fidelity
  and:
  world reliability;

- but:
  one observation / cycle
  raises:
  cumulative absolute target-error exposure;

- delivering:
  the same average budget
  as:
  two observations every two cycles
  is:
  materially worse
  at:
  coarse scale.

Therefore:

TEMPORAL REGULARITY
MATTERS.

H167 asks:

CAN
THE ORGANISM
ALWAYS TAKE:
ONE
FUNCTIONAL MICRO-ANCHOR

AND:

BUY:
A SECOND
OBSERVATION

ONLY ON:
HIGH-RISK
REPAIR CYCLES

SO THAT:

- average supervision
  falls below:
  2 observations / cycle;

- cumulative error exposure
  remains:
  near:
  MICRO2-EVERY1;

- final target fidelity
  remains:
  high;

- no hidden drift channel
  is introduced?

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
H166
matched-turnover
persistent-state mechanics.

Context:

MIXED only.

Cell scales:

g =
1.00,
0.25.

Turnover regimes:

ROAMING,
HOTSPOT.

Feedback eta:

0,
0.25.

Matched lifetime:

g=1.00:
20 cycles.

g=0.25:
292 cycles.

No:
global reset.

No:
checkpoint restore
outside:
LOCAL-CHECKPOINT-ORACLE.

FIRST MICRO-ANCHOR

Every adaptive repair cycle:

after:
100%
membership return
and:
context reconstruction,

acquire:
exactly ONE
lesion-local functional observation.

Query:

the first deterministic
H165/H166
micro-anchor query.

Target:

immutable original task function.

Noise:

eta =
0,
0.25.

Immediately:

jointly solve:
all restored lesion coefficients

using:
that one observation,
lambda=0.01,
current context state
as:
ridge prior,
surviving coefficients fixed.

The first observation
remains:
an active repair constraint

through:
all 12
post-membership
maturation steps.

SECOND-OBSERVATION RISK SCORE

Before:
the one-observation solve,

evaluate:

e_lesion =
squared error
between:

the immediate post-lesion
pre-regeneration prediction

and:
the observed first target.

After:
membership / context reconstruction
but:
before:
functional micro-anchor repair,

evaluate:

e_context =
squared error
between:

the context-repaired prediction

and:
the same observed target.

Define:

rho1 =
e_context
/
max(
e_lesion,
1e-14
).

This score uses:

- one observed functional target;
- the current policy state;
- the current lesion state;
- the current context-repaired state.

It may NOT use:

- lost target coefficients;
- held-out evaluation queries;
- a second unacquired target;
- future cycle outcomes;
- latent context labels.

ADAPTIVE SECOND OBSERVATION

ADAPT-1PLUS1:

acquire:
the second deterministic
micro-anchor observation

iff:

rho1 > 0.10.

Threshold:

0.10.

This is:
the same inherited
90%-recovery standard
used in:
H164/H165.

It is:
FROZEN
before:
H167 sanity.

If:
a second observation
is acquired:

re-solve:
the restored lesion coefficients
jointly
using:
both observations.

Both remain:
active constraints

through:
all:
12
post-membership
maturation steps.

If:
no second observation:

continue:
with:
the one-observation solve

through:
all:
12
maturation steps.

No:
full 24-observation anchor
exists
in:
H167 primary policies.

FIXED SAME-BUDGET COMPARATOR

FIXED-1P5:

odd-numbered cycles:

1 observation.

even-numbered cycles:

2 observations.

Thus:

average supervision
is:
approximately 1.5
observations / cycle.

This schedule:

- anchors:
  every cycle;
- has:
  no adaptive trigger;
- provides:
  a regular deterministic
  same-order comparison
  near:
  the intended adaptive budget.

At:
g=1,
20 cycles:

exact:
30 observations / lifetime.

At:
g=.25,
292 cycles:

exact:
438 observations / lifetime.

POLICIES

A — MICRO2-EVERY1

H166 exposure-safe baseline.

2 observations / cycle.

B — MICRO1-EVERY1

H166 one-observation
end-state-safe comparator.

1 observation / cycle.

C — FIXED-1P5

Alternating:
1,
2,
1,
2,...

Average:
1.5 observations / cycle.

D — ADAPT-1PLUS1

PRIMARY CANDIDATE.

Always:
first observation.

Second observation
iff:

rho1 >0.10.

E — CONTEXT-ONLY

0 observations.

F — LOCAL-CHECKPOINT-ORACLE

Exact immutable
target coefficient restore
on:
membership return.

Evaluation ceiling only.

COMMON-WORLD DISCIPLINE

All non-oracle policies
inside:
one condition-world

share:

- target field;
- evaluation queries;
- lesion centers;
- membership-repair potentials;
- first / second micro-anchor query coordinates;
- functional target noise potentials.

Policy state
may diverge
because:
repair histories differ.

No:
policy receives:
another policy's state.

COST ACCOUNTING

Report:

- first-observation count;
- second-observation count;
- second-observation duty;
- total observations;
- average observations / repair cycle;
- observations per:
body-equivalent turnover.

ADAPT-1PLUS1:

minimum:
1.0 observation / cycle.

maximum:
2.0.

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

120.

Policies:
6.

Policy lifetimes:

720.

PRIMARY METRICS

1.
FINAL GlobalFidelity;

2.
HALF GlobalFidelity;

3.
fraction final >=0.95;

4.
minimum post-cycle fidelity;

5.
late-life SelfRecovery;

6.
cumulative absolute error exposure;

7.
rho1 distribution;

8.
second-observation duty;

9.
total observations;

10.
average observations / cycle;

11.
HALF-to-FINAL drift;

12.
ADAPT-1PLUS1
versus:
MICRO2-EVERY1
exposure ratio;

13.
ADAPT-1PLUS1
versus:
FIXED-1P5
exposure ratio;

14.
same-cost efficiency;

15.
coarse / fine interaction;

16.
ROAMING / HOTSPOT interaction;

17.
eta interaction;

18.
oracle gap.

GLOBAL SAFETY RULE

ADAPT-1PLUS1
is:
SAFETY-QUALIFIED

iff:

1.
median FINAL GlobalFidelity
>=0.98

for:
every:
g x regime x eta group;

2.
>=90%
of worlds
finish:
FINAL >=0.95

for:
every group;

3.
group-median
HALF-to-FINAL
fidelity loss
<=0.01

for:
every group;

4.
group-median
late-life SelfRecovery
>=0.95

for:
every group.

EXPOSURE RULE

ADAPT-1PLUS1
is:
EXPOSURE-QUALIFIED

iff:

its group-median
cumulative absolute error exposure

is:
no more than:
1.25x

MICRO2-EVERY1

for:
every group.

This is:
the exact H166
exposure-safety ceiling.

PRIMARY ACCEPTANCE SHAPE

H167 supports:
ADAPTIVE ONE-PLUS-ONE
MICRO-ANCHORING

if:

1.
MICRO2-EVERY1
reproduces:
H166-level baseline safety.

2.
ADAPT-1PLUS1
is:
SAFETY-QUALIFIED.

3.
ADAPT-1PLUS1
is:
EXPOSURE-QUALIFIED.

4.
ADAPT-1PLUS1
group-median
average observations / cycle

<2.0

for:
every group.

5.
Pooled:
average observations / cycle

<=1.60

at:
g=1

and:
<=1.60

at:
g=.25.

This corresponds to:
at least:
20%
observation reduction

relative to:
MICRO2-EVERY1.

6.
ADAPT-1PLUS1
uses:
fewer total observations
than:
FIXED-1P5

OR:

if:
it uses:
within 5%
of:
FIXED-1P5 total observations,

its pooled cumulative exposure
must be:
>=10%
lower

at:
at least one scale

without:
being:
>5%
higher
at:
the other scale.

This tests:
adaptive value
beyond:
a fixed 1.5-observation schedule.

7.
Second-observation duty
must be:
higher
in:
at least one
coarse ROAMING
group

than:
the corresponding
fine-scale ROAMING group.

This tests:
whether:
the observable risk score
responds
to:
the scale-dependent
drift boundary
found in:
H163-H166.

8.
LOCAL-CHECKPOINT-ORACLE
remains:
the capability ceiling.

STRONG SUPPORT

H167 receives:
STRONG support

if:

ADAPT-1PLUS1
is:
SAFETY + EXPOSURE qualified

and:

pooled average observations / cycle
<=1.40

at:
both scales.

MIXED / NEGATIVE CONDITIONS

Treat H167 as:
mixed / negative
if:

- adaptive second-observation duty
  remains:
  near 100%;

- rho1
  fails to:
  distinguish:
  coarse high-risk
  from:
  fine low-risk turnover;

- final fidelity passes
  while:
  cumulative exposure
  exceeds:
  the H166 1.25x ceiling;

- adaptive observation savings
  are:
  smaller than:
  a simple fixed 1.5 schedule;

- noisy feedback
  causes:
  excessive second-observation purchases;

- one observed target
  is:
  too noisy
  to:
  support:
  reliable risk gating.

FALSE-NEGATIVE DIAGNOSTIC

For:
an ADAPT-1PLUS1
cycle
that:
does NOT
buy:
the second observation,

count:
a false negative

iff:

post-cycle GlobalFidelity

drops:
by:
more than:
0.01

relative to:
the previous
post-cycle fidelity.

Report:
cycle-weighted group rate.

This diagnostic:
does NOT:
change:
repair authority.

PRIMARY WORLD SEEDS

20260921600000
through:
20260921600119.

SANITY WORLD SEEDS

20260921690000...

Sanity:
NON-EVIDENCE.

No:
rho threshold,
micro-anchor count,
fixed comparator cadence,
lifetime,
cell scale,
regime,
lambda,
noise level,
or:
acceptance rule

may change
after:
the first held-out H167 lifetime.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_ADAPTIVE_ONE_PLUS_ONE_MICRO_ANCHOR_EXPOSURE_CONTROL

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
