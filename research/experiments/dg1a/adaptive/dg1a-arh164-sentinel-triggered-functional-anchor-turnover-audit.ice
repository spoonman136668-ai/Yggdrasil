TITLE: DG-1A-AR-H164 — Sentinel-Triggered Functional Anchor Turnover Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh163-intermittent-functional-anchor-turnover-audit.ice

PURPOSE

H163 established:

one fixed functional-anchor duty
is:
not scale invariant.

Coarse:
g=1.00
required:
approximately 50%
full-anchor duty
for:
all-scale safety.

Fine:
g=0.25
remained:
stable
at:
approximately 10%
full-anchor duty.

H164 asks:

CAN
A CHEAP,
LOCAL,
FUNCTIONAL SENTINEL

DECIDE:

WHICH
REPAIR CYCLES

ACTUALLY NEED:

THE FULL
24-OBSERVATION
FUNCTIONAL ANCHOR?

The target is:

retain:
H163 safety

while:

reducing:
unnecessary
full functional correction

without:

- latent labels;
- held-out evaluation access;
- checkpoint restoration;
- global retraining.

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
H163 / H162
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

Lifetime:

matched:
approximately one
body-equivalent turnover.

g=1.00:

20 cycles.

g=0.25:

292 cycles.

BASE REPAIR

Every non-oracle cycle:

1.
apply:
membership regeneration;

2.
initialize / refine:
reappearing cells
from:
developmental context;

3.
when:
100%
lesion membership
has returned,

evaluate:
the cycle's
local functional sentinel;

4.
if:
the sentinel triggers,

run:
full local functional correction
during:
the 12 post-membership
maturation steps;

5.
otherwise:

continue:
context-only
post-membership maturation.

SENTINEL QUERIES

Sentinel query pool:

separate
from:
the full anchor pool.

For each cycle:

draw:

S
local functional sentinel queries

using:
the same:
lesion-member-centered
query generator

with:
Gaussian macro jitter
sd=0.12.

Primary S:

2
and:
4.

Sentinel query targets:

the immutable
original task function

at:
those local points.

Sentinel targets
are:

external functional observations.

They count:
toward:
total external supervision cost.

Sentinel observations:

NEVER:
enter:
the full ridge solve.

They are:
detection only.

SENTINEL TRIGGER METRIC

For:
the sentinel query set,

let:

E_lesion =
MSE(
immediate post-lesion
sentinel predictions,
observed sentinel targets
).

Let:

E_context =
MSE(
post-membership,
pre-functional-anchor
sentinel predictions,
observed sentinel targets
).

Define:

rho_sentinel =
E_context
/
max(
E_lesion,
1e-14
).

Trigger:

FULL FUNCTIONAL ANCHOR

iff:

rho_sentinel
>
0.10.

Interpretation:

the developmental repair
must demonstrate:

at least:
90%
local functional-error reduction

relative to:
the same cycle's
lesioned baseline

to:
avoid:
full task-feedback correction.

The threshold:

0.10

is:
fixed from:
the existing T90
functional-recovery standard.

It is NOT:
selected from:
H164 sanity.

NOISE

Sentinel targets
and:
full-anchor targets

receive:

the same:
eta class

and:
independent deterministic
noise potentials.

eta:

0,
0.25.

Sentinel trigger
uses:

only:
the noisy sentinel targets
actually observed.

No:
noise-free target
enters:
the trigger.

FULL ANCHOR

When triggered:

use:

- lambda=0.01;
- global leverage
  local query design;
- 24-observation cap;
- 6 observations / maturation step;
- joint solve
  over:
  the complete restored lesion;
- surviving coefficients fixed.

Because:
the trigger occurs
at:
100%
membership return,

the H164 full anchor
is:
post-structural.

H164 therefore tests:

ANCHOR DUTY / DRIFT CONTROL,

not:

the H159
interleaving latency advantage.

POLICIES

A — EVERY1

H163 every-cycle
INTERLEAVED24
full-anchor baseline.

B — EVERY2

H163 fixed:
50%
full-anchor comparator.

C — SENTINEL2

2 detection observations
every repair cycle.

Full 24-observation anchor
only when:

rho_sentinel >0.10.

D — SENTINEL4

4 detection observations
per cycle.

Same:
rho threshold.

E — CONTEXT-ONLY

No:
functional observations.

F — LOCAL-CHECKPOINT-ORACLE

Exact target coefficient
restore
on:
membership return.

Evaluation ceiling only.

COST ACCOUNTING

Report separately:

- sentinel observations;
- full-anchor observations;
- total external functional observations;
- full-anchor cycle count;
- full-anchor duty fraction;
- external observations
  per:
  body-equivalent turnover.

For:

EVERY1 / EVERY2,

sentinel observations:
0.

For:

SENTINEL2 / SENTINEL4,

sentinel cost
is paid:
every cycle.

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

Total repair cycles:

same order
as:
H163.

PRIMARY METRICS

1.
FINAL GlobalFidelity;

2.
HALF GlobalFidelity;

3.
fraction final >=0.95;

4.
late-life SelfRecovery;

5.
cumulative absolute error exposure;

6.
sentinel trigger count;

7.
sentinel trigger duty;

8.
sentinel observations;

9.
full-anchor observations;

10.
total external observations;

11.
external observations
per:
body-equivalent turnover;

12.
false-negative diagnostic:

untriggered cycles
whose post-cycle
GlobalFidelity decrement
exceeds:
0.01;

13.
false-positive diagnostic:

triggered cycles
whose post-context
noise-free sentinel ratio
would have:
<=0.10

for:
analysis only;

14.
coarse / fine
trigger-duty interaction;

15.
ROAMING / HOTSPOT
interaction;

16.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H164 supports:
SENTINEL-TRIGGERED
FUNCTIONAL ANCHORING

if:

1.
EVERY1
reproduces:
H163-level quality.

Median FINAL:
>=0.98

and:
>=90%
worlds final >=0.95
for:
every group.

2.
At least one:
sentinel policy

SENTINEL2
or:
SENTINEL4

has:

median FINAL
>=0.98

for:
every:
g x regime x eta group.

3.
The same policy
has:

>=90%
of worlds
finish:
>=0.95

for:
every group.

4.
The same policy
does NOT:
lose:
more than:
0.01
median fidelity

from:
HALF
to:
FINAL

for:
any group.

5.
Coarse scale:

g=1.00.

The same policy
has:
median full-anchor duty

<0.50

for:
both regimes
and:
both eta classes.

Thus:
it must improve
on:
the H163
EVERY2 duty.

6.
Fine scale:

g=0.25.

The same policy
has:
median full-anchor duty

<=0.15

for:
both regimes
and:
both eta classes.

7.
TOTAL external observations

including:
sentinels

must be:

lower than:
EVERY2

in:
every:
g x regime x eta group.

8.
The same policy
reduces:
TOTAL external observations

relative to:
EVERY2

by:
>=20%
pooled
at:
g=1.00

and:
>=50%
pooled
at:
g=0.25.

9.
Late-life SelfRecovery
group median:

>=0.95

for:
every group.

10.
Untriggered-cycle
false-negative rate:

<=5%

for:
every group.

11.
SENTINEL2
and:
SENTINEL4

do NOT:
differ
by:
>0.02
median FINAL fidelity

in:
any group.

This tests:
sentinel-count robustness.

12.
LOCAL-CHECKPOINT-ORACLE
remains:
the capability ceiling.

SECONDARY RESULT

If:

sentinel safety passes

but:
the total-observation
cost gates fail,

H164 is:

MIXED-POSITIVE
for:
adaptive anchor safety

but:

negative
for:
measurement economy.

If:

SENTINEL4 passes
and:
SENTINEL2 fails,

the minimum safe
sentinel count
is:
approximately 4.

If:

SENTINEL2 passes,

prefer:
SENTINEL2

unless:
SENTINEL4
reduces:
full-anchor duty
enough
to:
lower:
TOTAL observation cost.

MIXED / NEGATIVE CONDITIONS

Treat H164 as:
mixed / negative
if:

- noisy sentinel targets
  cause:
  excessive false triggering;

- sentinel gating
  misses:
  coarse roaming drift;

- fine-scale sentinel duty
  rises:
  toward:
  EVERY2 levels;

- total observation cost
  is not:
  lower
  than:
  fixed cadence;

- local sentinel recovery
  looks healthy
  while:
  original-task fidelity
  drifts;

- four sentinels
  are:
  materially safer
  than:
  two,
  indicating:
  high trigger variance.

PRIMARY WORLD SEEDS

20260921300000
through:
20260921300119.

SANITY WORLD SEEDS

20260921390000...

Sanity:
NON-EVIDENCE.

No:
sentinel count,
rho threshold,
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
the first held-out H164 lifetime.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_SENTINEL_TRIGGERED_FUNCTIONAL_ANCHOR_TURNOVER

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
