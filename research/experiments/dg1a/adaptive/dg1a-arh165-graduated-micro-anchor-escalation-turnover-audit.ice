TITLE: DG-1A-AR-H165 — Graduated Micro-Anchor / Escalation Turnover Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh164-sentinel-triggered-functional-anchor-turnover-audit.ice

PURPOSE

H164 established:

a cheap local sentinel
can preserve:
long-horizon functional safety

but:

the detection-only controller
is:
measurement-inefficient.

Its two sentinel observations
are:

observed,
used to classify,
then discarded

before:
a triggered cycle acquires:
24 additional repair observations.

H165 tests:

GRADUATED FUNCTIONAL REPAIR.

Instead of:

CONTEXT
->
SENTINEL
->
DISCARD
->
FULL ANCHOR,

use:

CONTEXT
->
2-OBSERVATION MICRO-ANCHOR
->
LEAVE-ONE-OUT CHECK
->
FULL ESCALATION
ONLY IF NEEDED.

Question:

CAN
THE CHEAP DETECTION SIGNAL

ALSO:
DO USEFUL REPAIR WORK

SO THAT:

- full-anchor duty falls;
- total external observations fall;
- H164 safety is preserved;
- no hidden long-horizon drift appears?

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
H164 / H163 / H162
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

PERSISTENT STATE

Every non-oracle policy
carries:
its repaired coefficient vector

directly:
cycle to cycle.

No:
global reset.

No:
checkpoint restore
outside:
LOCAL-CHECKPOINT-ORACLE.

MICRO-ANCHOR OBSERVATIONS

Every H165 micro-anchor cycle
acquires:

exactly:
2
lesion-local functional observations.

Query generator:

same:
H164 sentinel query generator.

Each query:

- chooses:
  one lesion member;
- centers on:
  that member's normalized coordinate;
- adds:
  Gaussian jitter sd=0.12;
- rejects:
  outside unit disk.

Target:

immutable original task function.

Noise:

eta =
0,
0.25.

The two observed targets:

ARE:
repair data.

They are NOT:
detection-only.

MICRO-ANCHOR SOLVE

After:
100%
membership return

and:
before:
post-membership maturation,

perform:
one joint ridge solve
over:
all restored lesion coefficients.

Prior:

current context-repaired lesion state.

lambda:

0.01.

Training set:

the two micro-anchor observations.

Surviving coefficients:

fixed.

No:
lost original coefficient
or:
held-out evaluation target

enters:
the solve.

ESCALATION TEST

The same two observations
are also used:
for:
two-point leave-one-out
predictive validation.

For observation 1:

fit:
the lesion coefficients

using:
observation 2 only,

with:
the same current
context prior
and:
lambda=0.01.

Predict:
observation 1.

For observation 2:

fit:
using observation 1 only.

Predict:
observation 2.

Define:

E_LOO =
mean squared
leave-one-out
prediction error.

Define:

E_LESION =
mean squared error

of:
the immediate post-lesion
pre-regeneration model

on:
the same two observed targets.

Define:

rho_micro =
E_LOO
/
max(
E_LESION,
1e-14
).

Escalate to:
FULL FUNCTIONAL ANCHOR

iff:

rho_micro
>
0.10.

Threshold:

0.10.

This is:
the same fixed
90%-recovery standard
used:
in H164.

It is NOT:
selected from:
H165 sanity.

FULL ESCALATION

If:
rho_micro >0.10,

the two micro-anchor observations
remain:
part of:
the repair solve.

Acquire:

up to:
22 additional
lesion-local observations.

Thus:

maximum total
external observations
inside:
one escalated cycle

=
24,

not:
26.

Additional query pool:

same:
H164
64-query local pool.

Selection:

global leverage /
greedy D-optimal.

The information matrix
is initialized with:

the two
micro-anchor query rows.

Then:

22 additional queries
are selected

to maximize:
new information
conditional on:
the already acquired
micro-anchor data.

Acquisition batch:

up to 6
new additional observations
per:
post-membership maturation step

until:
22 additional observations
have been acquired.

At:
every maturation step:

- context refinement;
- joint lesion solve
  using:
  all micro-anchor
  plus:
  all additional
  observations acquired so far.

If:
no escalation:

the same:
two micro-anchor observations

remain:
active repair constraints

through:
all 12
post-membership
maturation steps.

Thus:

NO micro-anchor information
is discarded.

POLICIES

A — EVERY1

H163 full functional anchor
every repair cycle.

INTERLEAVED24 parent baseline.

B — EVERY2

H163 fixed 50%
full-anchor cadence comparator.

C — H164-SENTINEL2

Exact H164
detection-only
2-sentinel controller.

Comparator for:
information reuse.

D — MICRO2-ESCALATE

PRIMARY CANDIDATE.

2 observations
every cycle.

Use them:
for:
micro repair
and:
LOO escalation.

At most:
22 additional observations
when:
rho_micro >0.10.

E — MICRO2-ONLY

2-observation micro-anchor
every cycle.

Never:
full escalation.

Diagnostic:

tests whether:
the micro-anchor alone
is sufficient.

F — CONTEXT-ONLY

No:
external functional observation.

G — LOCAL-CHECKPOINT-ORACLE

Exact target coefficient
restore
on:
membership return.

Evaluation ceiling only.

COST ACCOUNTING

Report:

- micro-anchor observations;
- additional full-anchor observations;
- total external observations;
- escalation-cycle count;
- escalation duty;
- observations per:
body-equivalent turnover.

MICRO2-ESCALATE:

minimum external cost:

2 * cycles.

Maximum:

24 * cycles.

MICRO2-ONLY:

exactly:
2 * cycles.

H164-SENTINEL2:

same parent H164 cost:

2 * cycles
+
24 * triggered cycles.

FALSE-NEGATIVE DIAGNOSTIC

For:
a MICRO2-ESCALATE
non-escalated cycle,

count:
false negative

iff:

post-cycle GlobalFidelity

drops:
by:
more than:
0.01

relative to:
the previous
post-cycle fidelity.

Evaluate:

cycle-weighted
false-negative rate

inside:
each:
g x regime x eta group.

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
late-life SelfRecovery;

5.
cumulative absolute error exposure;

6.
rho_micro;

7.
escalation count;

8.
escalation duty;

9.
micro observations;

10.
additional observations;

11.
total external observations;

12.
cost relative to:
EVERY2;

13.
cost relative to:
H164-SENTINEL2;

14.
false-negative rate;

15.
MICRO2-ONLY
fidelity;

16.
coarse / fine
interaction;

17.
ROAMING / HOTSPOT
interaction;

18.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H165 supports:
GRADUATED
MICRO-ANCHOR
FUNCTIONAL REPAIR

if:

1.
EVERY1
reproduces:
H163/H164-level quality.

Median FINAL:
>=0.98

and:
>=90%
of worlds final >=0.95

for:
every group.

2.
MICRO2-ESCALATE

median FINAL fidelity
>=0.98

for:
every:
g x regime x eta group.

3.
MICRO2-ESCALATE

>=90%
of worlds
finish:
>=0.95

for:
every group.

4.
MICRO2-ESCALATE

does NOT:
lose:
more than:
0.01
median GlobalFidelity

from:
HALF
to:
FINAL

for:
any group.

5.
MICRO2-ESCALATE

median escalation duty:

<0.50

for:
every:
g=1
regime x eta group.

6.
MICRO2-ESCALATE

median escalation duty:

<=0.15

for:
every:
g=0.25
regime x eta group.

7.
MICRO2-ESCALATE

TOTAL external observations

are:
lower than:
EVERY2

in:
every group.

8.
MICRO2-ESCALATE

reduces:
pooled TOTAL external observations

relative to:
EVERY2

by:
>=20%

at:
g=1

and:
>=50%

at:
g=0.25.

9.
MICRO2-ESCALATE

reduces:
pooled TOTAL external observations

relative to:
H164-SENTINEL2

by:
>=10%

at:
both:
g=1
and:
g=0.25.

10.
Late-life SelfRecovery
group median:

>=0.95

for:
every group.

11.
Cycle-weighted
false-negative rate

on:
non-escalated cycles

<=5%

for:
every group.

12.
LOCAL-CHECKPOINT-ORACLE
remains:
the capability ceiling.

SECONDARY MICRO-ANCHOR RESULT

If:

MICRO2-ONLY

has:
median FINAL >=0.98

and:
>=90%
world reliability

for:
every group,

then:

full-anchor escalation
is:
not required
under:
the tested one-body-equivalent lifetime.

That would be:

a stronger result
than:
the primary hypothesis.

If:

MICRO2-ESCALATE
passes safety

but:
cost gates fail,

H165 is:

MIXED-POSITIVE
for:
information reuse

but:
negative
for:
supervision economy.

MIXED / NEGATIVE CONDITIONS

Treat H165 as:
mixed / negative
if:

- the two-point micro-anchor
  destabilizes:
  context repair;

- two-point LOO
  misses:
  coarse roaming drift;

- micro correction
  lowers:
  the trigger score
  without:
  preserving:
  original-task fidelity;

- escalation duty
  remains:
  near H164;

- total observation cost
  remains:
  above EVERY2;

- MICRO2-ONLY
  looks locally healthy
  while:
  target function drifts;

- fine-scale
  still requires:
  >15%
  full escalation duty.

PRIMARY WORLD SEEDS

20260921400000
through:
20260921400119.

SANITY WORLD SEEDS

20260921490000...

Sanity:
NON-EVIDENCE.

No:
micro-anchor count,
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
the first held-out H165 lifetime.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_GRADUATED_MICRO_ANCHOR_TURNOVER

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — GRADUATED MICRO-ANCHOR HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H165 HELD-OUT PRIMARY EXECUTION.

FINAL H165 SANDBOX HARNESS

File:

h165_micro_anchor_v1.py

SHA-256:

69e3a195ae9485b153a7a6efba254e5b68837359f0a0f5eb022108b1d5ede808.

PARENT HASHES

H161:

ae89e645e9f00f33a581c05298a0b2e930b450bbc9a55f0e0f46f87de86a8248.

H162:

2a8e405055d88906285934778898b02072dcdf683afd8cbc4d8f392c7461ae2c.

H163:

553a1edf2da195aff37a3a4ee6dcfa0f6072b2945bee8b46d64e916791edd5c2.

H164:

f606744bf16c3cae3c38c5d227c8ba7a7d5ba75f009a95f0cb98f9f3181c77d4.

MICRO-ANCHOR IMPLEMENTATION

Two lesion-local observations
are acquired:
after:
100%
membership return.

They are:
immediately used
in:
a joint lesion solve

with:

lambda=0.01.

Current:
context-repaired lesion state

is:
the ridge prior.

Surviving coefficients:

fixed.

The same:
two observations

are used:
for:
two-point leave-one-out
predictive checking.

For each observation:

fit:
using:
the other observation only;

predict:
the held-out observation.

Define:

rho_micro =
E_LOO
/
max(
E_LESION,
1e-14
).

Escalate:

iff:

rho_micro >0.10.

Threshold:

unchanged
from:
preregistration.

FULL ESCALATION

The two:
micro-anchor observations

remain:
active repair data.

Acquire:

at most:
22
additional observations.

The:
22-query
additional leverage sequence

is computed:
conditional on:
the two already-observed
micro-anchor design rows.

Thus:

maximum total
external observations
inside:
one escalated cycle

=
24.

No:
micro-anchor observation
is discarded.

NO ESCALATION

The two:
micro-anchor observations

remain:
active constraints

through:
all:
12
post-membership
maturation steps.

MICRO2-ONLY

Uses:
the same:
2-observation micro-anchor

every cycle

and:
never escalates.

COMPARATORS

EVERY1,
EVERY2:

exact H163
fixed-cadence policies.

H164-SENTINEL2:

exact H164
detection-only
2-sentinel controller.

CONTEXT-ONLY:

exact H163.

LOCAL-CHECKPOINT-ORACLE:

exact H163/H162
local target-state ceiling.

SANITY

Disjoint family:

20260921490000...

6 representative
condition-world lifetimes.

7 policies.

42 policy lifetimes.

Mechanical checks:

- exactly seven policies / seed;
- exact six sanity seeds;
- LOCAL-CHECKPOINT-ORACLE
  final fidelity:
  exactly 1.0;
- MICRO2-ESCALATE
  maximum external observations / cycle:
  24;
- MICRO2-ONLY:
  exactly two observations / cycle;
- all micro-anchor data:
  remains:
  active repair evidence;
- no:
  lost target coefficient;
  held-out evaluation target;
  latent context label

enters:
non-oracle repair.

Accepted sanity-output SHA-256:

875b24210eca12797280727fe25a4cd8843e0f697e3805be8a25689971632da8.

NON-EVIDENCE SIGNAL

Coarse ROAMING,
eta=0:

MICRO2-ESCALATE:

final fidelity:
approximately 0.99920.

escalation duty:
0.05.

total external observations:
62.

MICRO2-ONLY:

final fidelity:
approximately 0.99910.

total observations:
40.

Coarse ROAMING,
eta=.25:

MICRO2-ESCALATE:

final:
approximately 0.99975.

duty:
0.20.

observations:
128.

MICRO2-ONLY:

approximately 0.99941.

Coarse HOTSPOT,
eta=.25:

MICRO2-ESCALATE:

final:
approximately 0.99997.

duty:
0.35.

MICRO2-ONLY:

approximately 0.99997.

Fine ROAMING,
eta=0:

MICRO2-ESCALATE:

final:
approximately 0.99998.

duty:
approximately 0.137.

observations:
1464.

MICRO2-ONLY:

approximately 0.99997.

Fine ROAMING,
eta=.25:

MICRO2-ESCALATE:

final:
approximately 0.99999.

duty:
approximately 0.103.

MICRO2-ONLY:

approximately 0.99998.

Fine HOTSPOT,
eta=.25:

MICRO2-ESCALATE:

final:
approximately 1.0.

duty:
approximately 0.668.

MICRO2-ONLY:

approximately 0.999995.

This final sanity cell
suggests:

the two-point LOO trigger
can:
be conservative

even when:
the micro-anchor itself
appears:
functionally sufficient.

This is:
a held-out
primary hypothesis.

No:

- micro-anchor count;
- rho threshold;
- query rule;
- escalation cap;
- noise rule;
- lifetime;
- sample size;
- acceptance gate

is changed.

PRIMARY FAMILY

20260921400000..20260921400119.

120 held-out condition-world lifetimes.

7 policies.

840 policy lifetimes.

H165 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H165 lifetime.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — GRADUATED MICRO-ANCHOR / ESCALATION TURNOVER

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-POSITIVE PRIMARY ESCALATION / POSITIVE SECONDARY MICRO2-ONLY DISCOVERY.

FINAL H165 HARNESS SHA-256

69e3a195ae9485b153a7a6efba254e5b68837359f0a0f5eb022108b1d5ede808.

ACCEPTED PRIMARY MATRIX SHA-256

54498206d44e3885b3d70b2bafa71337a537337582fdd9a7bb69f2bcf70f194c.

ACCEPTED PRIMARY FAMILY

20260921400000..20260921400119.

PRIMARY MATRIX

120 held-out condition-world lifetimes.

7 policies.

840 policy lifetimes.

Validation:

- exactly 120 unique held-out seeds;
- exact accepted seed interval;
- exactly seven policy rows / seed;
- zero duplicate seed x policy rows;
- no missing accepted seeds;
- no post-primary threshold tuning.

PRIMARY CANDIDATE

MICRO2-ESCALATE.

PRIMARY SAFETY

Minimum group median
FINAL GlobalFidelity:

approximately:
0.999327.

Frozen target:
>=0.98.

PASS:
8 / 8 groups.

World fraction
FINAL >=0.95:

100%
in:
every group.

PASS.

Maximum group-median
HALF-to-FINAL
fidelity loss:

approximately:
0.000238.

Frozen limit:
0.01.

PASS.

COARSE ESCALATION DUTY

MICRO2-ESCALATE
median escalation duty:

g=1.

HOTSPOT,
eta=0:
0.10.

HOTSPOT,
eta=.25:
0.25.

ROAMING,
eta=0:
0.20.

ROAMING,
eta=.25:
0.35.

Frozen target:

strictly <0.50.

PASS:
4 / 4.

FINE ESCALATION DUTY

g=.25.

Median duty:

HOTSPOT,
eta=0:
approximately 0.192.

HOTSPOT,
eta=.25:
approximately 0.216.

ROAMING,
eta=0:
approximately 0.175.

ROAMING,
eta=.25:
approximately 0.171.

Frozen target:
<=0.15.

FAIL:
0 / 4.

Thus:

micro-repair
substantially lowers:
full escalation duty

relative to:
H164,

but:
not enough
to satisfy:
the frozen fine-scale
15% ceiling.

TOTAL OBSERVATION COST
VERSUS:
EVERY2

MICRO2-ESCALATE
median external observations:

g=1:

84,
150,
128,
194

depending on:
regime / eta

versus:
240
for:
EVERY2.

g=.25:

1684..1970

versus:
3504.

Lower than:
EVERY2
in:
EVERY group.

PASS.

POOLED COST REDUCTION
VERSUS:
EVERY2

g=1:

approximately:
35.36%
fewer observations.

Frozen target:
>=20%.

PASS.

g=.25:

approximately:
48.38%
fewer.

Frozen target:
>=50%.

FAIL,
narrowly:

short by:
approximately:
1.62 percentage points.

COST VERSUS:
H164 SENTINEL2

MICRO2-ESCALATE
reduces:
pooled total external observations

relative to:
the exact
detection-only H164 SENTINEL2
comparator

by:

g=1:

approximately:
46.28%.

g=.25:

approximately:
21.54%.

Frozen target:
>=10%
at:
both scales.

PASS.

This directly confirms:

REUSING
THE CHEAP SENTINEL DATA
AS:
REPAIR DATA

is:
materially more efficient

than:
H164's:

observe
->
classify
->
discard.

LATE-LIFE SELF RECOVERY

Minimum group median:

approximately:
0.9911.

Frozen target:
>=0.95.

PASS.

FALSE-NEGATIVE SAFETY

Cycle-weighted
non-escalated-cycle
false-negative rate:

maximum group rate:

approximately:
0.42%.

Frozen limit:
5%.

PASS:
all groups.

ORACLE

LOCAL-CHECKPOINT-ORACLE:

FINAL fidelity
exactly:
1.0.

PASS.

PRIMARY GATE REVIEW

PASS:

1.
EVERY1 baseline.

2.
MICRO2-ESCALATE
median FINAL quality.

3.
world reliability.

4.
HALF-to-FINAL drift.

5.
coarse escalation duty.

7.
lower total observations
than:
EVERY2
in:
every group.

9.
>=10%
cost reduction
versus:
H164 SENTINEL2
at:
both scales.

10.
late-life SelfRecovery.

11.
false-negative safety.

12.
oracle ceiling.

FAIL / MIXED:

6.
fine escalation duty
<=15%.

Observed:
approximately:
17%..22%.

8.
pooled fine-scale
>=50%
observation reduction
versus:
EVERY2.

Observed:
approximately:
48.38%.

PRIMARY INTERPRETATION

MICRO2-ESCALATE
is:

MIXED-POSITIVE.

The graduated controller:

CONTEXT
->
2-OBSERVATION MICRO-ANCHOR
->
OPTIONAL ESCALATION

is:
safer
and:
substantially more efficient

than:

the H164
detection-only sentinel.

But:

the two-point LOO score
still:
over-escalates
at:
fine scale.

SECONDARY MICRO2-ONLY RESULT

The preregistered
stronger secondary condition
is:

MICRO2-ONLY

median FINAL fidelity
>=0.98

and:
>=90%
world reliability

for:
EVERY group.

Observed:

minimum group median
FINAL fidelity:

approximately:
0.998490.

World fraction
FINAL >=0.95:

100%
in:
every group.

PASS.

MICRO2-ONLY COST

Exactly:

2 observations
per:
repair cycle.

Matched-turnover lifetime:

g=1:

40 observations.

g=.25:

584 observations.

Relative to:
EVERY2:

g=1:

40
versus:
240.

Reduction:
83.33%.

g=.25:

584
versus:
3504.

Reduction:
83.33%.

This is:
a stronger architectural discovery
than:
the primary escalation hypothesis.

Under:
the tested
one-body-equivalent lifetime,

A TWO-OBSERVATION
FUNCTIONAL MICRO-ANCHOR
ON EVERY REPAIR CYCLE

IS SUFFICIENT
TO PRESERVE:

high:
original-task fidelity

without:

full 24-observation
functional-anchor escalation.

MICRO2-ONLY GROUP MEDIANS

MIXED:

g=.25:

median FINAL
approximately:
0.999935..0.999988.

g=1:

approximately:
0.998490..0.999645.

All:
well above:
the secondary threshold.

IMPORTANT CAVEAT

The secondary gate
was intentionally limited to:

FINAL fidelity
and:
world-level reliability.

MICRO2-ONLY
also shows:

one accepted coarse noisy-roaming world
with:
FINAL fidelity
approximately:
0.9785,

still:
above:
the 0.95 world-reliability threshold.

Some individual worlds
show:
larger:
HALF-to-FINAL
or:
per-cycle SelfRecovery
variation

than:
the group medians.

Therefore:

H165 does NOT prove:

that:
two observations / cycle

are:
the minimal safe
long-horizon supervision budget.

It proves:

that:
full anchors
are not required
under:
the tested lifetime.

FINAL INTERPRETATION

H165 changes:
the architecture substantially.

The emerging hierarchy is no longer:

CONTEXT
->
SENTINEL
->
FULL ANCHOR.

It is:

CONTEXT REGENERATION

->

TINY
FUNCTIONAL MICRO-ANCHOR

as:
the NORMAL repair path.

Full functional anchoring
becomes:

an exception path

whose necessity
has NOT:
been demonstrated
by:
H165.

NEXT HIGH-LEVERAGE QUESTION

Find:

THE MINIMUM
FUNCTIONAL MICRO-ANCHOR
BUDGET.

The next experiment should compare:

- 0 observations / cycle;
- 1 observation / cycle;
- 2 observations / cycle;
- 2 observations every 2 cycles;
- 2 observations every 5 cycles;
- possibly:
  a tiny accumulated
  functional-debt trigger.

Keep:

matched body-equivalent turnover.

Do NOT:

reintroduce:
24-observation full anchors
as:
the default.

NEXT:

H166 —
MINIMAL MICRO-ANCHOR
DUTY / OBSERVATION-BUDGET
TURNOVER AUDIT.

H165 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- global retraining;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — GRADUATED MICRO-ANCHOR / ESCALATION TURNOVER

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-POSITIVE PRIMARY / STRONG POSITIVE SECONDARY MICRO2-ONLY RESULT.

FINAL H165 HARNESS SHA-256

69e3a195ae9485b153a7a6efba254e5b68837359f0a0f5eb022108b1d5ede808.

ACCEPTED PRIMARY MATRIX SHA-256

3a1a14ef14b792dac16920002c22afcfc73f1d002e897c12c139acbb018e90bb.

ACCEPTED PRIMARY FAMILY

20260921400000..20260921400119.

PRIMARY MATRIX

120 held-out condition-world lifetimes.

7 policies.

840 policy lifetimes.

Validation:

- exactly 120 unique held-out seeds;
- exact accepted seed interval;
- exactly seven policy rows / seed;
- zero duplicate seed x policy rows;
- no missing accepted seeds;
- no post-primary micro-anchor tuning.

PRIMARY CANDIDATE

MICRO2-ESCALATE.

FUNCTIONAL QUALITY

Minimum group median
FINAL GlobalFidelity:

approximately:
0.999327.

Frozen target:
>=0.98.

PASS:
8 / 8
g x regime x eta groups.

WORLD-LEVEL RELIABILITY

Fraction:
FINAL >=0.95:

100%
in:
every group.

Frozen target:
>=90%.

PASS.

HALF-TO-FINAL DRIFT

Maximum group-median
HALF minus FINAL
fidelity decline:

approximately:
0.000238.

Frozen limit:
0.01.

PASS.

COARSE ESCALATION DUTY

g=1.00.

Median escalation duty:

HOTSPOT,
eta=0:
0.10.

HOTSPOT,
eta=.25:
0.25.

ROAMING,
eta=0:
0.20.

ROAMING,
eta=.25:
0.35.

Frozen limit:
<0.50
for:
every coarse group.

PASS:
4 / 4.

FINE ESCALATION DUTY

g=0.25.

Median escalation duty:

HOTSPOT,
eta=0:
approximately 0.192.

HOTSPOT,
eta=.25:
approximately 0.216.

ROAMING,
eta=0:
approximately 0.175.

ROAMING,
eta=.25:
approximately 0.171.

Frozen limit:
<=0.15.

FAIL:
0 / 4.

Thus:

the two-point LOO escalation test
remains:
too conservative
at:
fine scale

despite:
excellent final safety.

TOTAL EXTERNAL OBSERVATION COST
VERSUS EVERY2

Median group costs:

all:
MICRO2-ESCALATE
<
EVERY2.

PASS:
8 / 8 groups.

Pooled reduction:

g=1:

median:
approximately 37.5%.

mean:
approximately 35.4%.

Frozen target:
>=20%.

PASS.

g=0.25:

median:
approximately 50.7%.

mean:
approximately 48.4%.

Frozen target:
>=50%.

PASS
by:
the preregistered pooled-median criterion.

TOTAL COST
VERSUS H164-SENTINEL2

Pooled median reduction:

g=1:

approximately 43.4%.

g=0.25:

approximately 23.1%.

Frozen target:
>=10%
at:
both scales.

PASS.

Thus:

REUSING
the two cheap local observations

as:
repair data

materially improves:
measurement economy

over:
H164's
observe-classify-discard design.

LATE-LIFE SELF RECOVERY

Minimum group median:

approximately:
0.9911.

Frozen target:
>=0.95.

PASS.

FALSE-NEGATIVE SAFETY

Cycle-weighted
false-negative rate
among:
non-escalated cycles:

fine scale:

0%
all groups.

coarse HOTSPOT:

0%.

coarse ROAMING,
eta=0:

1 false-negative
among:
239 non-escalated cycles

=
approximately 0.42%.

coarse ROAMING,
eta=.25:

0%.

Frozen limit:
<=5%.

PASS:
every group.

MAXIMUM PER-CYCLE EXTERNAL COST

MICRO2-ESCALATE:

24.

PASS.

ORACLE

LOCAL-CHECKPOINT-ORACLE:

FINAL GlobalFidelity
exactly:
1.0

through:
the accepted primary.

PASS.

PRIMARY GATE REVIEW

PASS:

1.
EVERY1 parent baseline.

2.
MICRO2-ESCALATE median FINAL >=0.98.

3.
MICRO2-ESCALATE
>=90%
world reliability.

4.
HALF-to-FINAL drift.

5.
Coarse escalation duty <0.50.

7.
TOTAL cost below EVERY2
every group.

8.
Pooled observation reduction:
>=20% coarse
and:
>=50% fine
by:
the frozen pooled-median rule.

9.
>=10%
cost reduction
versus:
H164-SENTINEL2
at:
both scales.

10.
Late-life SelfRecovery.

11.
False-negative rate.

12.
Oracle ceiling.

FAIL / MIXED:

6.
Fine-scale escalation duty
<=0.15.

Observed:
approximately:
0.171..0.216.

FAIL.

FINAL PRIMARY INTERPRETATION

H165 primary candidate is:

MIXED-POSITIVE.

The graduated controller is:

SAFE,
LOW-DRIFT,
AND:
MEASUREMENT-CHEAPER

than:
both:

- fixed EVERY2 anchoring;
- H164 detection-only sentinel gating.

But:

its two-point LOO escalation test
still requests:
more fine-scale
full-anchor cycles

than:
the frozen target allows.

SECONDARY MICRO2-ONLY RESULT

The preregistered
stronger secondary condition
is:
SUPPORTED.

MICRO2-ONLY

uses:

exactly:
2 external functional observations
per:
repair cycle.

No:
full escalation.

Median FINAL GlobalFidelity:

g=.25 HOTSPOT eta=0:
approximately 0.999984.

g=.25 HOTSPOT eta=.25:
approximately 0.999988.

g=.25 ROAMING eta=0:
approximately 0.999941.

g=.25 ROAMING eta=.25:
approximately 0.999935.

g=1 HOTSPOT eta=0:
approximately 0.999645.

g=1 HOTSPOT eta=.25:
approximately 0.999619.

g=1 ROAMING eta=0:
approximately 0.999454.

g=1 ROAMING eta=.25:
approximately 0.998490.

Minimum group median:

approximately:
0.998490.

Required:
>=0.98.

PASS:
8 / 8.

WORLD RELIABILITY

FINAL >=0.95:

100%
in:
every group.

PASS.

Thus:

under:
the tested
one-body-equivalent
matched-turnover lifetime,

FULL 24-OBSERVATION
ESCALATION
IS NOT REQUIRED.

A:
TWO-OBSERVATION
MICRO-ANCHOR
ON EVERY REPAIR CYCLE

is sufficient
to preserve:

- original-task fidelity;
- matched-turnover stability;
- coarse and fine scale;
- ROAMING and HOTSPOT turnover;
- eta=0.25 noisy supervision.

COST

MICRO2-ONLY:

g=1:

40 observations / lifetime.

EVERY2:

240.

Reduction:

83.3%.

g=0.25:

584
versus:
3504.

Reduction:

83.3%.

This is:
a stronger supervision-economy result
than:
the H165 primary escalation controller.

ARCHITECTURAL CONSEQUENCE

The current best measured
repair hierarchy simplifies to:

CONTEXT REGENERATION

->

2 LOCAL
FUNCTIONAL OBSERVATIONS

->

JOINT MICRO-PATCH
CORRECTION

with:

NO ROUTINE
FULL-ANCHOR ESCALATION

required
inside:
the tested regime.

This is:
a major reduction
from:

24 observations
per:
fully anchored cycle.

IMPORTANT LIMIT

H165 has tested:

2 observations
per:
EVERY repair cycle.

It does NOT establish:

- whether one observation
  is sufficient;
- whether two-observation
  micro-anchors can themselves
  be intermittent;
- whether longer than:
  one body-equivalent turnover
  eventually accumulates drift;
- whether real learned
  semantic functions
  behave similarly.

NEXT HIGH-LEVERAGE QUESTION

The next experiment should locate:

THE MINIMUM
FUNCTIONAL REFERENCE RATE.

Do NOT:
optimize the failed
fine-scale escalation threshold.

Instead compare:

- MICRO1:
  1 functional observation
  every cycle;

- MICRO2:
  2 every cycle;

- MICRO2-EVERY2:
  2 observations
  every second repair cycle;

- MICRO2-EVERY5:
  2 every fifth cycle;

against:
CONTEXT-ONLY
and:
MICRO2-EVERY1.

This determines whether:

the effective external supervision floor
is:

2 observations / cycle,

or:

substantially lower.

NEXT:

H166 —
MINIMUM MICRO-ANCHOR
REFERENCE-RATE
TURNOVER AUDIT.

H165 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- global retraining;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
