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


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — MINIMAL MICRO-ANCHOR BUDGET HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H166 HELD-OUT PRIMARY EXECUTION.

FINAL H166 SANDBOX HARNESS

File:

h166_micro_budget_v1.py

SHA-256:

1adf59a6d4ef84cb84165e78334b3c3ac8db9ac07bb3d1f4a03d0523c662a164.

PARENT HASHES

H161:
ae89e645e9f00f33a581c05298a0b2e930b450bbc9a55f0e0f46f87de86a8248.

H162:
2a8e405055d88906285934778898b02072dcdf683afd8cbc4d8f392c7461ae2c.

H163:
553a1edf2da195aff37a3a4ee6dcfa0f6072b2945bee8b46d64e916791edd5c2.

H164:
f606744bf16c3cae3c38c5d227c8ba7a7d5ba75f009a95f0cb98f9f3181c77d4.

H165:
69e3a195ae9485b153a7a6efba254e5b68837359f0a0f5eb022108b1d5ede808.

MICRO-ANCHOR MECHANICS

Anchored micro-cycle:

- complete membership regeneration;
- context-repair lesion;
- acquire:
  policy-declared
  1 or 2
  local functional observations;
- joint solve:
  restored lesion coefficients;
- lambda=0.01;
- current context state:
  ridge prior;
- surviving coefficients:
  fixed;
- same micro observations
  remain:
  active constraints
  through:
  all 12
  post-membership
  maturation steps.

Unanchored cycle:

- context reconstruction;
- zero:
  external functional observations;
- 12:
  post-membership
  context maturation steps.

No:
raw observations
are reused
across:
different repair cycles.

Persistent repaired state:

does:
carry forward.

POLICY REALIZATION

MICRO2-EVERY1:

2 observations
every cycle.

MICRO1-EVERY1:

1 every cycle.

MICRO2-EVERY2:

2 on:
cycle 1,3,5,...

MICRO1-EVERY2:

1 on:
cycle 1,3,5,...

MICRO2-EVERY5:

2 on:
cycle 1,6,11,...

CONTEXT-ONLY:

0.

LOCAL-CHECKPOINT-ORACLE:

target coefficient restore
on:
membership return.

LINEAGE CHECK

On:
all six
H166 sanity worlds,

H166:
MICRO2-EVERY1

was compared
against:
H165:
MICRO2-ONLY

using:
the same:
world,
lesion,
membership,
query,
noise,
and:
repair mechanics.

Maximum numerical difference
across:
FINAL fidelity,
HALF fidelity,
minimum fidelity,
late-life SelfRecovery,
cumulative error exposure,
and:
total observation count:

approximately:
1.11e-16.

Therefore:

MICRO2-EVERY1
is:
a faithful
H165 baseline carry-forward.

SANITY

Disjoint family:

20260921590000...

6 representative
condition-world lifetimes.

7 policies.

42 policy lifetimes.

Mechanical checks:

- exactly seven policies / seed;
- exact six sanity seeds;
- LOCAL-CHECKPOINT-ORACLE:
  final fidelity exactly 1.0;
- observation counts:
  match:
  frozen cadence formulas;
- no policy exceeds:
  declared per-cycle
  micro-anchor count;
- no:
  lost target coefficient,
  held-out evaluation target,
  or:
  latent context label

enters:
non-oracle repair.

Accepted sanity-output SHA-256:

dcb17eb9028a42355de8b7178f0095f2f8c53a6be7f23445d97489b6df9a17eb.

NON-EVIDENCE SIGNAL

Coarse ROAMING,
eta=0:

MICRO2-EVERY1:

FINAL:
approximately 0.9978.

late-life SelfRecovery:
approximately 0.988.

MICRO1-EVERY1:

FINAL:
approximately 0.9966.

SelfRecovery:
approximately 0.856.

MICRO2-EVERY2:

FINAL:
approximately 0.9843.

SelfRecovery:
approximately 0.961.

MICRO1-EVERY2:

FINAL:
approximately 0.9793.

MICRO2-EVERY5:

approximately 0.9772.

Coarse HOTSPOT,
eta=.25:

MICRO1-EVERY1:

FINAL:
approximately 0.9988.

MICRO2-EVERY2:

approximately 0.9903.

Fine:
g=.25

remains:
highly stable
across:
all tested micro-anchor budgets
in:
the sanity worlds.

These values are:

NON-EVIDENCE.

They suggest:

- temporal regularity
  may matter
  at:
  coarse scale;
- one observation / cycle
  may be:
  safer
  than:
  the same average budget
  delivered:
  as two observations
  every two cycles;
- sub-one-observation schedules
  may:
  approach:
  coarse-scale limits.

No:
observation count,
cadence,
lifetime,
cell scale,
noise rule,
qualification rule,
or:
acceptance criterion

is changed.

PRIMARY FAMILY

20260921500000..20260921500119.

120 held-out
condition-world lifetimes.

7 policies.

840 policy lifetimes.

H166 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H166 lifetime.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — MINIMAL MICRO-ANCHOR BUDGET

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / NEGATIVE FOR SUB-TWO EXPOSURE-SAFE GLOBAL QUALIFICATION / POSITIVE TEMPORAL-REGULARITY RESULT.

FINAL H166 HARNESS SHA-256

1adf59a6d4ef84cb84165e78334b3c3ac8db9ac07bb3d1f4a03d0523c662a164.

ACCEPTED PRIMARY MATRIX SHA-256

de24c68be7043d246a3bc3555b02441d18c08034c311191acaa57118ba476bdc.

ACCEPTED PRIMARY FAMILY

20260921500000..20260921500119.

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
- no post-primary budget / cadence tuning.

BASELINE

MICRO2-EVERY1.

Minimum group median
FINAL GlobalFidelity:

approximately:
0.998288.

World fraction
FINAL >=0.95:

100%
in:
every group.

Maximum group-median
HALF-to-FINAL loss:

approximately:
0.00102.

Minimum group-median
late-life SelfRecovery:

approximately:
0.9875.

PASS:

H165 secondary safety
is:
reproduced.

MICRO1-EVERY1

1 observation
every repair cycle.

END-STATE QUALITY

Minimum group median
FINAL fidelity:

approximately:
0.996244.

World fraction
FINAL >=0.95:

100%
in:
every group.

Maximum group-median
HALF-to-FINAL loss:

approximately:
0.00200.

Minimum group-median
late-life SelfRecovery:

approximately:
0.9753.

Thus:

FINAL quality,
world reliability,
drift,
and:
late-life SelfRecovery

all satisfy:
their frozen thresholds.

However:

CUMULATIVE ABSOLUTE ERROR EXPOSURE

relative to:
MICRO2-EVERY1

has:
group-median ratios

up to:

approximately:
1.77
at:
fine scale

and:
approximately:
1.48
at:
coarse scale.

Frozen limit:
1.25.

FAIL.

Therefore:

ONE OBSERVATION
EVERY CYCLE

is:
sufficient
for:
long-horizon
END-STATE FIDELITY

but:

not:
for:
the preregistered
EXPOSURE-SAFE
qualification.

MICRO2-EVERY2

Same average budget:

approximately:
1 observation / cycle,

delivered as:

2 observations
every:
2 cycles.

Minimum group median
FINAL:

approximately:
0.99069.

World reliability:
100%.

But:

minimum group-median
late-life SelfRecovery:

approximately:
0.9278.

Exposure ratio
versus:
MICRO2-EVERY1:

up to:
approximately 2.92.

FAIL.

Thus:

the same average supervision budget
is NOT:
equivalent
under:
different temporal delivery.

TEMPORAL REGULARITY RESULT

Compare:

MICRO1-EVERY1

versus:

MICRO2-EVERY2.

Both use:
approximately:
1 observation / cycle
on average.

At:
g=1,

total cumulative error exposure
summed across:
the accepted policy worlds

is:

approximately:
37.95%
LOWER

for:
MICRO1-EVERY1.

At:
g=.25,

the difference is:
much smaller:

approximately:
3.43%
lower

for:
MICRO1-EVERY1.

Interpretation:

at:
coarse scale,

DISTRIBUTING
small functional corrections
through:
every repair cycle

is:
materially safer

than:

batching:
the same average
observation budget
into:
alternating cycles.

This supports:

continuous tiny anchoring

over:

intermittent larger
micro-anchors.

SUB-ONE-OBSERVATION POLICIES

MICRO1-EVERY2

average:
0.5 observations / cycle.

End-state medians remain:
high

but:

late-life SelfRecovery
and:
cumulative error exposure

fail:
the global qualification.

MICRO2-EVERY5

average:
approximately:
0.4 observations / cycle.

Coarse ROAMING
fails:
multiple gates.

Median FINAL:

clean:
approximately 0.9794.

eta=.25:
approximately 0.9754.

World fraction
FINAL >=0.95:

approximately:
86.7%
clean

and:
73.3%
noisy.

HALF-to-FINAL loss:

up to:
approximately 0.0156.

FAIL.

GLOBAL QUALIFICATION

The frozen rule requires:

- median FINAL >=0.98;
- >=90% world reliability;
- HALF-to-FINAL loss <=0.01;
- late-life SelfRecovery >=0.95;
- cumulative exposure <=1.25x
  MICRO2-EVERY1;

for:
EVERY group.

Globally qualified:

MICRO2-EVERY1:
YES.

MICRO1-EVERY1:
NO,
exposure gate.

MICRO2-EVERY2:
NO.

MICRO1-EVERY2:
NO.

MICRO2-EVERY5:
NO.

Therefore:

no policy
with:
average supervision <=1.0
observation / cycle

is:
GLOBALLY QUALIFIED.

Primary H166 support condition:

FAIL.

STRONG / ULTRA-SPARSE SUPPORT

No:
<=0.5 observation/cycle
policy
qualifies globally.

FAIL.

SCALE-SPECIFIC QUALIFICATION

Under:
the full frozen qualification rule,

no:
sub-two-observation policy

qualifies
even:
at:
g=.25,

because:

the same-scale
relative exposure limit
is:
strict.

Important:

fine-scale
absolute error exposure
remains:
small

in:
physical / macro terms,

but:

the H166 gate
compares:
against:
the already very low
MICRO2-EVERY1
fine-scale baseline.

This result
is:
reported as frozen.

It is NOT:
retroactively relaxed.

CONTEXT-ONLY

Fine scale:

retains:
high FINAL fidelity

but:
has:
3x..8x
the cumulative error exposure
of:
MICRO2-EVERY1.

Coarse ROAMING:

FINAL reliability
and:
drift
degrade substantially.

Confirms:

end-state function alone
is:
not enough
to choose:
a supervision budget.

ORACLE

LOCAL-CHECKPOINT-ORACLE:

FINAL fidelity
exactly:
1.0.

PASS.

FINAL INTERPRETATION

H166 is:

NEGATIVE
for:

SUB-TWO
EXPOSURE-SAFE
GLOBAL SUPERVISION.

The current measured
exposure-safe baseline remains:

2 LOCAL FUNCTIONAL OBSERVATIONS
PER:
REPAIR CYCLE.

But:

H166 also establishes:

1 OBSERVATION / CYCLE

is:
already sufficient

for:
high:
end-state fidelity,
world reliability,
and:
median late-life recovery.

The missing benefit
of:
the second observation

is primarily:

REDUCING
CUMULATIVE FUNCTIONAL ERROR
DURING:
THE REPAIR LIFETIME,

not:

preventing:
catastrophic final drift.

ARCHITECTURAL CONSEQUENCE

The next controller
should NOT:

simply delete:
the second observation.

It should ask:

WHICH CYCLES
ACTUALLY NEED:
A SECOND OBSERVATION?

Start with:

ONE
functional micro-anchor
every cycle.

Then:

acquire:
a SECOND observation

only when:
the first observation
or:
the current repair geometry

indicates:
high residual uncertainty / error risk.

This preserves:

the temporal regularity
that H166 found valuable

while:

making:
the second observation

an:
exception path.

NEXT:

H167 —
ADAPTIVE
ONE-PLUS-ONE
MICRO-ANCHOR
EXPOSURE-CONTROL AUDIT.

Primary target:

average:
<2
observations / cycle

while:

retaining:
MICRO2-EVERY1-level
cumulative error exposure

and:
H165-level
long-horizon fidelity.

H166 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- global retraining;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — MINIMAL MICRO-ANCHOR DUTY / OBSERVATION BUDGET

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-NEGATIVE FOR SUB-TWO-OBSERVATION GLOBAL QUALIFICATION / POSITIVE CADENCE DISCOVERY.

FINAL H166 HARNESS SHA-256

1adf59a6d4ef84cb84165e78334b3c3ac8db9ac07bb3d1f4a03d0523c662a164.

ACCEPTED SANITY MATRIX SHA-256

dcb17eb9028a42355de8b7178f0095f2f8c53a6be7f23445d97489b6df9a17eb.

ACCEPTED PRIMARY MATRIX SHA-256

de24c68be7043d246a3bc3555b02441d18c08034c311191acaa57118ba476bdc.

ACCEPTED PRIMARY FAMILY

20260921500000..20260921500119.

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
- no post-primary observation-count or cadence tuning.

BASELINE

MICRO2-EVERY1.

Minimum group median
FINAL GlobalFidelity:

approximately:
0.998288.

Minimum:
world fraction FINAL >=0.95:

100%.

Maximum group-median
HALF-to-FINAL fidelity loss:

approximately:
0.001024.

Minimum group-median
late-life SelfRecovery:

approximately:
0.987546.

Exposure ratio
versus itself:

1.0.

Therefore:

MICRO2-EVERY1
is:
GLOBALLY QUALIFIED.

This faithfully reproduces:
the H165
two-observation-every-cycle
secondary result.

ONE OBSERVATION EVERY CYCLE

MICRO1-EVERY1.

Minimum group median
FINAL fidelity:

approximately:
0.996244.

World fraction
FINAL >=0.95:

100%
in:
every group.

Maximum group-median
HALF-to-FINAL loss:

approximately:
0.002001.

Minimum group-median
late-life SelfRecovery:

approximately:
0.975301.

Thus:

quality,
world reliability,
drift,
and:
late-life SelfRecovery

all:
PASS.

However:

cumulative absolute error exposure

relative to:
MICRO2-EVERY1

ranges:

approximately:
1.14
to:
1.77.

Worst group:

approximately:
1.769.

Frozen limit:

<=1.25
for:
EVERY group.

FAIL.

Therefore:

ONE OBSERVATION
EVERY CYCLE

preserves:
end-state capability

but:
does NOT:
meet:
the frozen transient-error
exposure requirement.

SAME AVERAGE BUDGET —
TEMPORAL REGULARITY

Compare:

MICRO1-EVERY1

versus:

MICRO2-EVERY2.

Both average:

approximately:
1 observation / repair cycle.

MICRO1-EVERY1
is:
consistently better.

MICRO2-EVERY2:

minimum group median
FINAL:

approximately:
0.990691.

World reliability:

100%.

Maximum HALF-to-FINAL loss:

approximately:
0.004990.

Minimum late-life SelfRecovery:

approximately:
0.927844.

FAIL:
SelfRecovery.

Worst exposure ratio
versus:
MICRO2-EVERY1:

approximately:
2.921.

FAIL.

At coarse scale:

MICRO1-EVERY1
also improves:
final fidelity
over:
MICRO2-EVERY2

by:
approximately:
0.0010
to:
0.0056

and:
improves:
late-life SelfRecovery

by:
approximately:
0.036
to:
0.048.

Thus:

AT THE SAME AVERAGE
SUPERVISION COST,

DISTRIBUTING:
ONE OBSERVATION
EVERY CYCLE

IS:
MATERIALLY SAFER

THAN:

BATCHING:
TWO OBSERVATIONS
EVERY OTHER CYCLE.

This is:
a primary architectural result.

SUB-ONE-OBSERVATION SCHEDULES

MICRO1-EVERY2:

average:
approximately 0.5 obs / cycle.

Minimum group median FINAL:

approximately:
0.986401.

World reliability:

100%.

Maximum HALF-to-FINAL loss:

approximately:
0.007900.

Minimum late-life SelfRecovery:

approximately:
0.930965.

Worst exposure ratio:

approximately:
3.231.

FAIL:
SelfRecovery
and:
exposure.

MICRO2-EVERY5:

average:
approximately 0.4 obs / cycle.

Minimum group median FINAL:

approximately:
0.975418.

Minimum group
world reliability:

approximately:
73.3%.

Maximum HALF-to-FINAL loss:

approximately:
0.015598.

Minimum late-life SelfRecovery:

approximately:
0.941263.

Worst exposure ratio:

approximately:
4.526.

FAIL:
quality,
reliability,
drift,
SelfRecovery,
and:
exposure.

GLOBAL QUALIFICATION

Globally qualified:

MICRO2-EVERY1
only.

NOT globally qualified:

MICRO1-EVERY1.

Reason:
exposure ceiling.

MICRO2-EVERY2.

Reasons:
SelfRecovery
and:
exposure.

MICRO1-EVERY2.

Reasons:
SelfRecovery
and:
exposure.

MICRO2-EVERY5.

Reasons:
quality,
reliability,
drift,
SelfRecovery,
exposure.

PRIMARY SUPPORT REVIEW

1.
MICRO2-EVERY1
reproduces:
H165 safety.

PASS.

2.
At least one policy
with:
average <=1.0 observation / cycle

is:
GLOBALLY QUALIFIED.

FAIL.

3.
Same-average comparison:

the two:
1-observation/cycle-equivalent
policies

do NOT:
both qualify.

However:

the diagnostic result
strongly favors:
MICRO1-EVERY1.

STRONG SUPPORT:

policy <=0.5 obs / cycle
globally qualified.

FAIL.

ULTRA-SPARSE:

MICRO2-EVERY5
globally qualified.

FAIL.

SCALE-SPECIFIC QUALIFICATION

Using:
the same full qualification rules
inside:
one scale,

no:
sub-two-observation policy

qualifies
at:
g=1.00

or:
g=0.25

because:
the frozen exposure ceiling

is exceeded
even where:
end-state fidelity
remains:
near-perfect.

Thus:

the current measured:
fully-qualified
minimum

remains:

2 observations
per:
repair cycle

at:
both tested scales.

FINAL INTERPRETATION

H166 is:

MIXED-NEGATIVE

for:

SUB-TWO-OBSERVATION
MICRO-ANCHOR QUALIFICATION.

But:

the experiment discovers
an important control law:

SUPERVISION REGULARITY
MATTERS.

A tiny:
one-observation
functional correction

on:
every repair cycle

is:
much safer

than:
the same average
observation budget

delivered:
in:
larger,
less frequent batches.

This means:

functional anchoring
behaves less like:

periodic retraining

and more like:

CONTINUOUS
LOW-BANDWIDTH
ERROR CONTROL.

SECOND IMPORTANT RESULT

The reason:
MICRO1-EVERY1
fails

is NOT:

terminal capability collapse.

Its final fidelity
and:
world-level reliability
remain:
strong.

It fails because:

TRANSIENT
ABSOLUTE FUNCTIONAL ERROR
ACCUMULATES
TOO MUCH

between / during:
local repairs

relative to:
the two-observation baseline.

Therefore:

the next experiment
should NOT:
simply increase:
anchor cadence.

One observation / cycle
already has:
the desirable cadence.

The open question is:

CAN
THAT ONE OBSERVATION
BE CHOSEN
MORE INTELLIGENTLY?

H166 currently uses:

the first deterministic
lesion-local micro-anchor query.

That is:
NOT:
information-designed.

NEXT SCOPED DIRECTION

H167 —
SINGLE-OBSERVATION
INFORMATION-DESIGN
MICRO-ANCHOR AUDIT.

Keep:

- one observation
  every repair cycle;
- matched body-equivalent turnover;
- same:
  lambda=0.01;
- same:
  persistent-state architecture.

Compare:

1.
current deterministic
single local observation;

2.
single:
global-leverage
selected observation
from:
the 64-query local pool;

3.
single:
A-optimal
trace-reduction
selected observation;

4.
possibly:
one query targeted at:
maximum predicted lesion-output variance

without:
reading:
the functional target.

Primary question:

CAN:
ONE
INFORMATION-DESIGNED
OBSERVATION / CYCLE

preserve:

the final-fidelity success
of:
MICRO1-EVERY1

while:

bringing:
cumulative absolute error exposure

inside:
the frozen:
1.25x
MICRO2-EVERY1
envelope?

H166 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- global retraining;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
