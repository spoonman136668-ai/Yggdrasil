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
