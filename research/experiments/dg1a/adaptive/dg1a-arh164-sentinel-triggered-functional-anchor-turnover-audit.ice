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


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — SENTINEL-TRIGGERED ANCHOR HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H164 HELD-OUT PRIMARY EXECUTION.

SCHEMA-ONLY SANITY REPAIR

The first sandbox wrapper:

h164_sentinel_anchor_v1.py

executed:
the sentinel policies

but:
failed while writing:
mixed parent / sentinel rows

because:
sentinel rows contained:
frac_ge20

while:
parent H163 rows
ended at:
frac_ge10.

This was:
a CSV schema mismatch only.

No:
sentinel trigger,
repair,
noise,
query,
threshold,
policy,
or:
scientific calculation

was changed.

The incomplete first sanity output
is:
NON-EVIDENCE.

FINAL H164 SANDBOX HARNESS

File:

h164_sentinel_anchor_v2.py

SHA-256:

f606744bf16c3cae3c38c5d227c8ba7a7d5ba75f009a95f0cb98f9f3181c77d4.

The only v1 -> v2 change:

drop:
frac_ge20

from:
the sentinel CSV row schema

so:
all six policies
share:
one output schema.

PARENT HASHES

H161:

ae89e645e9f00f33a581c05298a0b2e930b450bbc9a55f0e0f46f87de86a8248.

H162:

2a8e405055d88906285934778898b02072dcdf683afd8cbc4d8f392c7461ae2c.

H163:

553a1edf2da195aff37a3a4ee6dcfa0f6072b2945bee8b46d64e916791edd5c2.

SENTINEL MECHANICS

Sentinel counts:

2
and:
4.

Sentinel queries:

lesion-local,
member-centered,
Gaussian jitter sd=0.12.

Sentinel observations:

detection-only.

They NEVER:
enter:
the full ridge solve.

Trigger metric:

rho =
E_context
/
max(
E_lesion,
1e-14
).

Full functional anchor
iff:

rho > 0.10.

Threshold:

unchanged
from:
preregistration.

Trigger evaluation occurs:

after:
100%
membership return

and:
before:
post-membership
functional-anchor correction.

No:
held-out evaluation target
or:
lost coefficient

enters:
the trigger.

FULL ANCHOR

Triggered cycles use:

- lambda=0.01;
- global leverage local query design;
- 24-observation cap;
- 6 observations / maturation step;
- complete restored lesion
  as:
  joint variable domain;
- surviving coefficients fixed.

NOISE

Sentinel target noise
and:
full-anchor target noise

use:
independent deterministic potentials

at:
the same eta:

0,
0.25.

SENTINEL FALSE-NEGATIVE DIAGNOSTIC

For:
an untriggered cycle,

count:
false negative

iff:

the policy's:
post-cycle GlobalFidelity

drops:
by:
more than 0.01

relative to:
that policy's
previous post-cycle fidelity.

This is:
diagnostic only.

FALSE-POSITIVE DIAGNOSTIC

Noise-free sentinel target values
are used:
analysis-only

to ask:

whether:
a noisy trigger
would have:
rho_true <=0.10.

This diagnostic
does NOT:
affect:
repair authority.

SANITY

Disjoint family:

20260921390000...

6 representative
condition-world lifetimes.

36 policy lifetimes.

Mechanical checks:

- exactly six policies / sanity seed;
- exact six sanity seeds;
- LOCAL-CHECKPOINT-ORACLE:
  final fidelity exactly 1.0;
- sentinel policies:
  max full-anchor observations / triggered cycle = 24;
- no sentinel observation
  enters:
  the full solve;
- sentinel and parent policies
  share:
  one CSV schema;
- zero sentinel false negatives
  in:
  the disjoint sanity matrix.

Accepted sanity-output SHA-256:

b192cff335197ebc527e9ff404e1e86ec3a9b095c54ea4d38e3c99907cf47717.

NON-EVIDENCE SIGNAL

Coarse:
g=1,
ROAMING,
eta=0.

SENTINEL2:

final fidelity:
approximately 0.9987.

full-anchor duty:
0.60.

SENTINEL4:

approximately 0.9973.

duty:
0.55.

Coarse:
ROAMING,
eta=0.25.

SENTINEL2:

final fidelity:
approximately 0.9939.

duty:
0.55.

SENTINEL4:

approximately 0.99935.

duty:
0.75.

Fine:
g=0.25,
ROAMING,
eta=0.

SENTINEL2:

final fidelity:
approximately 0.99994.

duty:
approximately 0.281.

SENTINEL4:

approximately 0.99993.

duty:
approximately 0.260.

Fine:
ROAMING,
eta=0.25.

SENTINEL2:

duty:
approximately 0.411.

SENTINEL4:

approximately 0.435.

Fine:
HOTSPOT,
eta=0.25.

SENTINEL2:

duty:
approximately 0.086.

SENTINEL4:

approximately 0.062.

Sanity therefore suggests:

- sentinel gating can remain:
  functionally safe;
- trigger duty may be:
  scale / regime / noise dependent;
- some groups may fail:
  the preregistered cost targets.

No:
sentinel count,
rho threshold,
noise rule,
repair rule,
sample size,
or:
acceptance gate

was changed
from:
these NON-EVIDENCE results.

PRIMARY FAMILY

20260921300000..20260921300119.

120 held-out condition-world lifetimes.

6 policies.

720 policy lifetimes.

H164 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H164 lifetime.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — SENTINEL-TRIGGERED FUNCTIONAL ANCHORING

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-POSITIVE FOR ADAPTIVE SAFETY / NEGATIVE FOR MEASUREMENT ECONOMY.

FINAL H164 HARNESS SHA-256

f606744bf16c3cae3c38c5d227c8ba7a7d5ba75f009a95f0cb98f9f3181c77d4.

ACCEPTED PRIMARY MATRIX SHA-256

dbb9e31fc9380085414dabef52a9efd871273ad83b7c1ad92279b49e8e96c7f9.

ACCEPTED PRIMARY FAMILY

20260921300000..20260921300119.

PRIMARY MATRIX

120 held-out condition-world lifetimes.

6 policies.

720 policy lifetimes.

Validation:

- exactly 120 unique held-out seeds;
- exact accepted seed interval;
- exactly six policy rows / seed;
- zero duplicate seed x policy rows;
- no missing accepted seeds;
- no post-primary sentinel tuning.

EVERY1 BASELINE

Minimum group median
FINAL GlobalFidelity:

approximately:
0.999907.

Minimum group
world fraction
FINAL >=0.95:

100%.

PASS.

SENTINEL SAFETY

SENTINEL2
minimum group median
FINAL fidelity:

approximately:
0.998370.

SENTINEL4:

approximately:
0.998416.

Both exceed:
the frozen:
0.98
quality floor

in:
every:
g x regime x eta group.

PASS.

WORLD RELIABILITY

SENTINEL2:

100%
of worlds
finish:
>=0.95

in:
every group.

SENTINEL4:

100%.

Frozen target:
>=90%.

PASS.

HALF-TO-FINAL DRIFT

Maximum group-median
HALF minus FINAL
fidelity loss:

SENTINEL2:

approximately:
0.000242.

SENTINEL4:

approximately:
0.000229.

Frozen limit:
0.01.

PASS.

Thus:

sentinel gating
does NOT:
produce:
long-horizon target drift

under:
the accepted primary.

COARSE FULL-ANCHOR DUTY

Frozen target:

median full-anchor duty
<0.50

for:
both regimes
and:
both eta classes.

SENTINEL2:

HOTSPOT,
eta=0:
0.40.

HOTSPOT,
eta=.25:
0.50.

ROAMING,
eta=0:
0.50.

ROAMING,
eta=.25:
0.45.

FAIL:

2 / 4
groups sit:
at:
the 0.50 boundary

rather than:
strictly below.

SENTINEL4:

0.55,
0.50,
0.45,
0.45.

FAIL:

HOTSPOT
does not:
beat:
the fixed 50%
anchor-duty comparator.

FINE FULL-ANCHOR DUTY

Frozen target:

<=0.15
for:
every:
g=.25
regime x eta group.

SENTINEL2:

approximately:

0.264,
0.168,
0.236,
0.223.

FAIL:
0 / 4.

SENTINEL4:

approximately:

0.253,
0.188,
0.226,
0.236.

FAIL:
0 / 4.

Thus:

the simple instantaneous
rho>0.10 trigger

is:
too conservative
for:
the H163
fine-scale
10%-or-lower
anchor-duty regime.

TOTAL EXTERNAL OBSERVATION COST

Frozen requirement:

lower than:
EVERY2

in:
every group.

SENTINEL2:

coarse:

HOTSPOT clean:
232
versus:
240.

HOTSPOT noisy:
280
versus:
240.

ROAMING clean:
280
versus:
240.

ROAMING noisy:
256
versus:
240.

Fine:

all four groups
are:
below:
EVERY2,

with:
median reductions
approximately:
30.6%..49.8%.

FAIL:
all-group economy.

SENTINEL4:

coarse:

296..344
versus:
240.

Fine:

reductions:
approximately:
16.0%..29.0%.

FAIL.

POOLED COST REDUCTION

Relative to:
EVERY2.

SENTINEL2:

g=1:
approximately:
-12.8%.

That is:

12.8%
MORE
external observations.

g=.25:

approximately:
35.1%
fewer.

Frozen targets:

>=20%
reduction
at:
g=1

and:
>=50%
at:
g=.25.

FAIL both.

SENTINEL4:

g=1:

approximately:
28.8%
MORE.

g=.25:

approximately:
16.6%
fewer.

FAIL.

LATE-LIFE SELF RECOVERY

Minimum group-median
late-life SelfRecovery:

SENTINEL2:

approximately:
0.9786.

SENTINEL4:

approximately:
0.9646.

Frozen target:
>=0.95.

PASS.

FALSE-NEGATIVE SAFETY

Frozen metric:

UNTRIGGERED-CYCLE
false-negative rate

<=5%
for:
every group.

Cycle-weighted
accepted-primary
aggregate rates:

FINE:

0%
for:
all:
g=.25
regime x eta groups

under:
both sentinel counts.

COARSE HOTSPOT:

SENTINEL2:

clean:
approximately 1.28%.

eta=.25:
approximately 1.32%.

SENTINEL4:

clean:
approximately 1.30%.

eta=.25:
approximately 1.27%.

COARSE ROAMING:

0%.

PASS:
every group.

Important:

some individual
HOTSPOT worlds
have:
high per-world ratios

because:
they contain:
very few untriggered cycles.

The preregistered
untriggered-cycle rate
is therefore evaluated:
over:
the group cycle population,

not:
the maximum
single-world denominator.

SENTINEL FALSE POSITIVES

Analysis-only.

At:
eta=0:

false-positive rate:
0%.

At:
eta=.25:

noise causes:
measurable extra triggering.

Representative
cycle-weighted rates:

SENTINEL2:

approximately:
8.5%..21.0%
depending on:
group.

SENTINEL4:

approximately:
10.3%..16.3%.

This helps explain:
the failed economy gates.

SENTINEL COUNT ROBUSTNESS

Maximum absolute difference
between:
SENTINEL2
and:
SENTINEL4

group-median
FINAL fidelity:

approximately:
0.00025.

Frozen limit:
0.02.

PASS.

Therefore:

four sentinel observations
do NOT:
provide:
materially better
functional safety
than:
two.

ORACLE

LOCAL-CHECKPOINT-ORACLE
FINAL GlobalFidelity:

exactly:
1.0

through:
the accepted matrix.

PASS.

PREREGISTERED GATE REVIEW

PASS:

1.
EVERY1 baseline quality / reliability.

2.
At least one sentinel policy:
median FINAL >=0.98
every group.

Both pass.

3.
At least one sentinel policy:
>=90%
world reliability
every group.

Both pass.

4.
HALF-to-FINAL drift <=0.01.

Both pass.

9.
Late-life SelfRecovery.

Both pass.

10.
Cycle-weighted false-negative rate <=5%.

Both pass.

11.
SENTINEL2 / SENTINEL4
final-fidelity robustness.

PASS.

12.
Oracle ceiling.

PASS.

FAIL / MIXED:

5.
Coarse full-anchor duty
strictly <0.50
for:
every group.

FAIL.

6.
Fine full-anchor duty
<=0.15
for:
every group.

FAIL.

7.
Total external observations
below:
EVERY2
for:
every group.

FAIL.

8.
Required pooled
20% coarse
and:
50% fine
observation reduction.

FAIL.

FINAL INTERPRETATION

H164 is:

MIXED-POSITIVE
for:

ADAPTIVE ANCHOR SAFETY

and:

NEGATIVE
for:

MEASUREMENT ECONOMY.

A cheap local sentinel
CAN:

decide:
many cycles
do not need:
a full functional anchor

without:
allowing:
meaningful long-horizon drift.

But:

the present controller:

OBSERVE
->
CLASSIFY
->
DISCARD SENTINEL DATA
->
OPTIONALLY ACQUIRE 24 NEW OBSERVATIONS

is:
economically inefficient.

The strongest architectural finding is:

SENTINEL INFORMATION
SHOULD NOT:
BE WASTED.

Two sentinel observations
provide:
essentially the same
long-horizon safety

as:
four.

Yet:

under H164
they are:
detection-only

and:
cannot help:
repair.

That design creates:
a supervision tax
on:
every cycle.

NOISE
also causes:
false-positive triggering

without:
a corresponding
safety gain.

NEXT SCOPED DIRECTION

Do NOT:

increase:
sentinel count.

Do NOT:

simply loosen:
rho=0.10
post hoc.

Instead:

make:
the cheap sentinel observations

the FIRST
FUNCTIONAL MICRO-ANCHOR.

If:
two sentinel observations
already indicate:
small residual error,

let them:
participate directly
in:
a weak local correction

and:
avoid:
the full anchor.

If:
residual error remains
large after:
that micro-correction,

escalate:
to:
the full 24-observation solve.

This creates:
a graduated repair hierarchy:

CONTEXT REPAIR

->

2-OBSERVATION
MICRO-ANCHOR

->

FULL 24-OBSERVATION
ANCHOR
ONLY IF NEEDED.

The next experiment
should test:

whether:
the same:
2 cheap observations / cycle

can:

- reduce:
  false-positive full anchors;
- preserve:
  H164 safety;
- lower:
  coarse total observation cost
  below:
  EVERY2;
- push:
  fine total supervision
  materially below:
  H164;
- avoid:
  a new hidden drift channel.

NEXT:

H165 —
GRADUATED
MICRO-ANCHOR /
ESCALATION
TURNOVER AUDIT.

H164 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- global retraining;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
