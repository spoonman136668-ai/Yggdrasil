TITLE: DG-1A-AR-H166 — Minimal Micro-Anchor Duty / Observation-Budget Turnover Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh165-graduated-micro-anchor-escalation-turnover-audit.ice

PURPOSE

H165 established:

two local functional observations
per:
repair cycle

can:
preserve:
original-task fidelity

through:
approximately one
body-equivalent turnover

without:
full 24-observation anchors.

The next question is:

HOW LITTLE
EXTERNAL FUNCTIONAL SUPERVISION
IS ACTUALLY REQUIRED?

H166 separates:

OBSERVATION COUNT

from:

ANCHOR CADENCE.

It asks:

- is one observation every cycle enough?
- is two observations every two cycles equivalent?
- does temporal regularity matter at the same average cost?
- can sub-one-observation-per-cycle supervision remain safe?
- does the minimum safe budget depend on cell scale?

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
H165/H164/H163/H162
matched-turnover
persistent-state model.

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

20 repair cycles.

g=0.25:

292 repair cycles.

No:
global reset.

No:
checkpoint restore
outside:
LOCAL-CHECKPOINT-ORACLE.

MICRO-ANCHOR MECHANICS

An anchored micro-cycle:

1.
membership regenerates;

2.
context reconstruction
reaches:
100%
membership return;

3.
acquire:
the policy-declared number
of:
lesion-local functional observations;

4.
jointly solve:
all restored lesion coefficients

with:

lambda=0.01;

current context state
as:
the ridge prior;

surviving coefficients:
fixed;

5.
retain:
those observations
as:
active repair constraints

through:
all 12
post-membership
maturation steps.

An unanchored cycle:

uses:
context reconstruction
and:
12 post-membership
context maturation steps

with:
zero
functional observations.

No:
raw observation
is cached
for:
a later wound.

The repaired coefficient state:
does persist.

QUERY GENERATOR

Same:
H165
lesion-local micro-anchor
query generator.

Each observation:

- chooses one lesion member;
- centers on:
  its normalized location;
- adds:
  Gaussian jitter sd=0.12;
- rejects:
  outside:
  the unit disk.

If:
two observations
are requested,

use:
the first two
deterministic micro-anchor queries.

If:
one observation,

use:
the first.

Target:

immutable original task function.

Noise:

eta =
0,
0.25.

POLICIES

A — MICRO2-EVERY1

H165
MICRO2-ONLY
exact baseline.

2 observations
every repair cycle.

Average:

2.0
observations / cycle.

B — MICRO1-EVERY1

1 observation
every repair cycle.

Average:

1.0
observation / cycle.

C — MICRO2-EVERY2

2 observations
on:

cycle 1,
3,
5,
...

Zero
on:
alternating cycles.

Average:

approximately:
1.0
observation / cycle.

D — MICRO1-EVERY2

1 observation
on:

cycle 1,
3,
5,
...

Zero
on:
alternating cycles.

Average:

approximately:
0.5
observation / cycle.

E — MICRO2-EVERY5

2 observations
on:

cycle 1,
6,
11,
...

Average:

approximately:
0.4
observation / cycle.

F — CONTEXT-ONLY

0 observations.

G — LOCAL-CHECKPOINT-ORACLE

Exact target coefficient
restore
on:
membership return.

Evaluation ceiling only.

CADENCE RULE

For:
EVERY-n

a micro-anchor occurs
iff:

(cycle - 1) mod n
=
0.

Cycle 1:
anchored
for:
all micro-anchor policies.

COST ACCOUNTING

Report:

- anchored micro-cycles;
- total observations;
- average observations / cycle;
- observations per:
body-equivalent turnover.

Expected maximum lifetime totals:

g=1
20 cycles:

MICRO2-EVERY1:
40.

MICRO1-EVERY1:
20.

MICRO2-EVERY2:
20.

MICRO1-EVERY2:
10.

MICRO2-EVERY5:
8.

g=.25
292 cycles:

MICRO2-EVERY1:
584.

MICRO1-EVERY1:
292.

MICRO2-EVERY2:
292.

MICRO1-EVERY2:
146.

MICRO2-EVERY5:
118.

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
7.

Policy lifetimes:

840.

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
micro-anchor cycle count;

8.
total observations;

9.
average observations / cycle;

10.
HALF-to-FINAL drift;

11.
coarse / fine interaction;

12.
ROAMING / HOTSPOT interaction;

13.
same-average comparison:
MICRO1-EVERY1
versus:
MICRO2-EVERY2;

14.
oracle gap.

GLOBAL QUALIFICATION RULE

A non-oracle
micro-anchor policy
is:
GLOBALLY QUALIFIED

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
every group;

5.
cumulative absolute error exposure
is:
no more than:
25%
above:
MICRO2-EVERY1

for:
every group.

PRIMARY ACCEPTANCE SHAPE

H166 supports:
SUB-TWO-OBSERVATION
MICRO-ANCHORING

if:

1.
MICRO2-EVERY1
reproduces:
H165 secondary safety.

2.
At least one:
policy
with:
average supervision
<=1.0
observation / cycle

is:
GLOBALLY QUALIFIED.

This may be:

MICRO1-EVERY1

or:

MICRO2-EVERY2.

3.
If both:
1-observation/cycle policies
qualify,

compare:
their cumulative error exposure.

If:

one is:
>10%
lower
pooled,

that cadence:
is preferred.

Otherwise:

prefer:
MICRO1-EVERY1

because:
it spreads:
functional anchoring
more evenly
through:
turnover.

STRONG SUPPORT

H166 receives:
STRONG support

if:

at least one:
policy
with:
average supervision
<=0.5
observation / cycle

is:
GLOBALLY QUALIFIED.

Candidate:

MICRO1-EVERY2.

ULTRA-SPARSE SUPPORT

If:

MICRO2-EVERY5

is:
GLOBALLY QUALIFIED,

then:

approximately:
0.4
observations / repair cycle

is:
sufficient
under:
the tested lifetime.

SCALE-SPECIFIC RESULT

Independently report:

the lowest-cost policy
that qualifies
within:
g=1

and:
within:
g=.25.

A policy is:
SCALE-QUALIFIED

using:
the same quality,
reliability,
drift,
SelfRecovery,
and:
exposure rules

restricted to:
that scale.

This result is:
important even if:
no one policy
qualifies globally.

CONTEXT-ONLY

CONTEXT-ONLY
is:
a zero-supervision comparator.

It does NOT:
define:
success.

If:
it qualifies
within:
a fine-scale group,

report:
that result

without:
allowing it
to waive:
coarse safety requirements.

ORACLE

LOCAL-CHECKPOINT-ORACLE
must remain:
the capability ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H166 as:
mixed / negative
if:

- two observations
  every cycle
  remain necessary;

- one observation
  every cycle
  looks healthy
  at FINAL
  while:
  cumulative exposure
  or:
  late-life SelfRecovery
  degrades;

- batching:
  two observations
  every two cycles
  is materially worse
  than:
  spreading:
  one per cycle;

- coarse roaming
  requires:
  >1 observation / cycle;

- fine-scale
  needs:
  denser supervision
  than:
  coarse scale;

- sub-one-observation schedules
  accumulate:
  original-task drift.

PRIMARY WORLD SEEDS

20260921500000
through:
20260921500119.

SANITY WORLD SEEDS

20260921590000...

Sanity:
NON-EVIDENCE.

No:
micro-anchor count,
cadence,
lifetime,
cell scale,
regime,
lambda,
noise level,
or:
acceptance rule

may change
after:
the first held-out H166 lifetime.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_MINIMAL_MICRO_ANCHOR_BUDGET_TURNOVER

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
