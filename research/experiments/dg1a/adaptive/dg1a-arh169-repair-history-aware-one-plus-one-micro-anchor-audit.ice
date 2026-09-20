TITLE: DG-1A-AR-H169 — Repair-History-Aware One-Plus-One Micro-Anchor Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh168-geometric-one-plus-one-micro-anchor-audit.ice

PURPOSE

H168 established:

target-blind query geometry
can:
selectively buy:
a second micro-anchor observation

and:
substantially reduce:
fine-scale transient error exposure.

But:

one group remained outside:
the strict exposure envelope:

g=1.00
+
ROAMING
+
eta=0.25.

The reason is:

coarse query geometry
correctly indicates:
one query is locally informative,

but:

query geometry alone
does NOT encode:

HOW MUCH
NEW COGNITIVE TERRITORY
THE WOUND
IS MOVING THROUGH.

H169 adds:

TARGET-BLIND
REPAIR-HISTORY NOVELTY.

Question:

CAN
RECENT
STRUCTURAL TURNOVER HISTORY

identify:
coarse roaming cycles
that deserve:
a second functional observation

without:

- buying extra queries
  for stable hotspots;
- increasing:
  fine-scale duty;
- reading:
  functional targets
  to:
  decide query count?

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
H168
matched-turnover
persistent-state architecture.

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

g=.25:
292 cycles.

No:
global reset.

No:
checkpoint restore
outside:
LOCAL-CHECKPOINT-ORACLE.

FIRST / SECOND QUERY GEOMETRY

Identical to:
H168.

q1:

maximum leverage
under:
A0=lambda I.

q2:

maximum remaining leverage
after:
q1
rank-one information update.

rho_geom:

L2 / L1.

lambda:

0.01.

RECENT REPAIR FOOTPRINT

Maintain:

the lesion membership set
from:
the previous:
5 repair cycles.

For:
cycle c >1,

recent_footprint =
union(
lesion sets
from:
max(1,c-5)
through:
c-1
).

Let:

current_lesion

be:
the current cycle's
damaged-cell set.

Define:

overlap_fraction =
|current_lesion
 intersect
 recent_footprint|
/
|current_lesion|.

Define:

novelty5 =
1 -
overlap_fraction.

For:

cycle 1,

history novelty
does NOT:
trigger:
a second query.

Only:
rho_geom
applies.

HISTORY PURCHASE RULE

PRIMARY CANDIDATE:

HIST-GEOM-1PLUS1.

Always:
acquire q1.

Acquire q2
iff:

A.

rho_geom >=0.98

OR:

B.

rho_geom <=0.50

AND:

novelty5 >=0.75.

Interpretation:

A:
fine / high-remaining-information
geometry.

B:
coarse geometry
with:
high repair-footprint novelty.

Both conditions are:
TARGET-BLIND.

RATIONALE

H168 accepted-development data
showed:

coarse:
rho_geom
approximately:
0.35..0.46.

fine:
approximately:
0.94..0.99.

Thus:

rho_geom <=0.50

restricts:
the novelty rule

to:
the coarse-information regime.

H168 structural-history analysis
showed:

coarse ROAMING,
cycle >1:

novelty5 >=0.75

in:
approximately:
44%..50%
of cycles.

Coarse HOTSPOT:

approximately:
0%.

Therefore:

novelty5 >=0.75

is:
a round
repair-history threshold

that:
separates:
moving damage
from:
repeated local turnover

in:
development data

without:
functional targets.

No:
H169 held-out seed

was used:
to select:
these thresholds.

REPAIR

Same:
H168.

After:
100%
membership return:

- acquire q1;
- conditionally acquire q2;
- joint-solve:
  restored lesion coefficients;
- lambda=0.01;
- context state:
  ridge prior;
- surviving coefficients:
  fixed;
- selected observations:
  active constraints
  through:
  12 post-membership
  maturation steps.

Persistent repaired state:
carries forward.

POLICIES

A — MICRO2-LEVERAGE

Two leverage queries
every cycle.

Exposure-safe reference.

B — H168-GEOM-1PLUS1

Exact H168
rho_geom>=0.98
controller.

C — HIST-GEOM-1PLUS1

PRIMARY CANDIDATE.

rho_geom rule
plus:
coarse novelty5 rule.

D — MICRO1-LEVERAGE

One leverage query
every cycle.

E — CONTEXT-ONLY

Zero:
functional observations.

F — LOCAL-CHECKPOINT-ORACLE

Evaluation ceiling.

COST ACCOUNTING

Report:

- geometry-triggered
  second queries;
- history-triggered
  second queries;
- total:
  second-query count;
- second-query duty;
- average observations / cycle;
- total observations
  per:
  body-equivalent turnover.

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
late-life SelfRecovery;

5.
cumulative absolute error exposure;

6.
rho_geom;

7.
novelty5;

8.
geometry-trigger count;

9.
history-trigger count;

10.
second-query duty;

11.
average observations / cycle;

12.
exposure ratio
versus:
MICRO2-LEVERAGE;

13.
exposure improvement
versus:
H168-GEOM-1PLUS1;

14.
ROAMING / HOTSPOT
duty separation;

15.
coarse / fine
interaction;

16.
eta interaction;

17.
oracle gap.

GLOBAL SAFETY RULE

HIST-GEOM-1PLUS1
is:
SAFETY-QUALIFIED

iff:

1.
median FINAL
>=0.98
every group;

2.
>=90%
worlds FINAL >=0.95
every group;

3.
group-median
HALF-to-FINAL loss
<=0.01
every group;

4.
group-median
late-life SelfRecovery
>=0.95
every group.

EXPOSURE RULE

HIST-GEOM-1PLUS1
is:
EXPOSURE-QUALIFIED

iff:

group-median
cumulative absolute error exposure

<=1.25x

MICRO2-LEVERAGE

for:
every group.

PRIMARY ACCEPTANCE SHAPE

H169 supports:
REPAIR-HISTORY-AWARE
ONE-PLUS-ONE
MICRO-ANCHORING

if:

1.
MICRO2-LEVERAGE
reproduces:
H168/H167 safety.

2.
HIST-GEOM-1PLUS1
is:
SAFETY-QUALIFIED.

3.
HIST-GEOM-1PLUS1
is:
EXPOSURE-QUALIFIED.

4.
Coarse HOTSPOT:

median second-query duty
<=0.10

for:
both eta classes.

5.
Coarse ROAMING:

median second-query duty

between:
0.25
and:
0.70

for:
both eta classes.

6.
Coarse ROAMING
second-query duty

exceeds:
corresponding
coarse HOTSPOT duty

by:
>=0.20

for:
both eta classes.

7.
Fine-scale:

HIST-GEOM-1PLUS1

median second-query duty
does NOT exceed:
H168-GEOM-1PLUS1

by:
more than:
0.05

in:
any:
regime x eta group.

8.
Pooled observation reduction
versus:
MICRO2-LEVERAGE

>=25%
at:
g=1.00

and:
>=15%
at:
g=.25.

9.
HIST-GEOM-1PLUS1
cumulative exposure

is:
at least:
5%
lower

than:
H168-GEOM-1PLUS1

in:
both:
coarse ROAMING
eta groups.

10.
HIST-GEOM-1PLUS1
does NOT:
increase:
cumulative exposure

by:
>5%

versus:
H168-GEOM-1PLUS1

in:
either:
coarse HOTSPOT group.

11.
LOCAL-CHECKPOINT-ORACLE
remains:
the capability ceiling.

STRONG SUPPORT

H169 receives:
STRONG support

if:

all primary gates pass

and:

HIST-GEOM-1PLUS1
pooled exposure

is:
within:
10%
of:
MICRO2-LEVERAGE

at:
both scales.

MIXED / NEGATIVE CONDITIONS

Treat H169 as:
mixed / negative
if:

- novelty5
  does not:
  distinguish:
  moving from:
  repeated local damage;

- history rule
  buys:
  second queries
  in:
  coarse hotspots;

- history rule
  inflates:
  fine-scale query duty;

- the coarse noisy-roaming
  exposure miss
  remains;

- extra queries
  reduce cost efficiency
  without:
  reducing exposure;

- target-blind repair history
  is:
  insufficient
  to:
  predict:
  functional-anchor demand.

PRIMARY WORLD SEEDS

20260921800000
through:
20260921800119.

SANITY WORLD SEEDS

20260921890000...

Sanity:
NON-EVIDENCE.

No:
rho_geom threshold,
novelty window,
novelty threshold,
query rule,
observation cap,
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
the first held-out H169 lifetime.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_REPAIR_HISTORY_AWARE_ONE_PLUS_ONE_MICRO_ANCHOR

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — REPAIR-HISTORY-AWARE ONE-PLUS-ONE HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H169 HELD-OUT PRIMARY EXECUTION.

FINAL H169 SANDBOX HARNESS

File:

h169_history_1plus1_v1.py

SHA-256:

fda1fe47f3a77ef449a642193c5ab3a9c67a439909a0b8f297c0544d2e5fc0d3.

PARENT H168 HARNESS

SHA-256:

85053ccadd5557d57f1590fc1a99653acd2352f3823f56499b7165d0dfb3e83e.

PURCHASE RULE

Always:

one:
maximum-leverage
target-blind query.

Second query
iff:

rho_geom >=0.98

OR:

cycle >1

AND:

rho_geom <=0.50

AND:

novelty5 >=0.75.

novelty5:

1 -
fraction
of:
current lesion cells

contained in:
the union
of:
the previous
five lesion sets.

No:
functional target
enters:
rho_geom
or:
novelty5.

REPAIR

Identical to:
H168.

Selected query target(s):

- acquired only
  after:
  purchase decision;
- used:
  in:
  one joint lesion solve;
- retained:
  as:
  active constraints
  through:
  12 post-membership
  maturation steps.

lambda:

0.01.

Persistent mutable state:
carries forward.

SANITY

Disjoint family:

20260921890000...

6 representative
condition-world lifetimes.

6 policies.

36 policy lifetimes.

Mechanical checks:

- exactly six policies / seed;
- exact six sanity seeds;
- LOCAL-CHECKPOINT-ORACLE
  final fidelity exactly 1.0;
- fine-scale
  HIST-GEOM
  matches:
  H168-GEOM
  duty / behavior
  because:
  novelty trigger
  is:
  gated to:
  rho_geom<=0.50;
- no:
  target value
  enters:
  purchase decision;
- no global reset.

Accepted sanity matrix
SHA-256:

71bf89c76a239980b41945af25db0e5df3878b72c865e0c1c5a34f3f0b8f50b8.

NON-EVIDENCE SIGNAL

Coarse ROAMING:

eta=0:

H168-GEOM:

second duty:
0.

exposure:
approximately 1.568.

HIST-GEOM:

second duty:
0.45.

history-trigger count:
9 / 20.

exposure:
approximately 1.520.

MICRO2-LEVERAGE:

approximately 1.469.

eta=.25:

H168-GEOM:

duty:
0.

exposure:
approximately 1.456.

HIST-GEOM:

duty:
0.55.

history-trigger count:
11 / 20.

exposure:
approximately 1.030.

MICRO2-LEVERAGE:

approximately 1.051.

Coarse HOTSPOT,
eta=.25:

HIST-GEOM:

second duty:
0.

history-trigger count:
0.

Behavior:
identical
to:
H168-GEOM.

Fine:

HIST-GEOM

matches:
H168-GEOM

in:
all three
representative
fine sanity lifetimes.

These outputs are:

NON-EVIDENCE.

No:

- rho_geom threshold;
- novelty window;
- novelty threshold;
- query rule;
- observation cap;
- sample size;
- acceptance gate

is changed.

PRIMARY FAMILY

20260921800000..20260921800119.

120 held-out
condition-world lifetimes.

6 policies.

720 policy lifetimes.

H169 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H169 lifetime.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — REPAIR-HISTORY-AWARE ONE-PLUS-ONE MICRO-ANCHOR

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-POSITIVE.

FINAL H169 HARNESS SHA-256

fda1fe47f3a77ef449a642193c5ab3a9c67a439909a0b8f297c0544d2e5fc0d3.

ACCEPTED PRIMARY MATRIX SHA-256

65da2a3a142ce0b2dfa24da6f944492b60c64eb5ab641ceeb64dde55987dfdb8.

ACCEPTED PRIMARY FAMILY

20260921800000..20260921800119.

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
- no post-primary novelty / geometry tuning.

PRIMARY CANDIDATE

HIST-GEOM-1PLUS1.

SAFETY

Minimum group median
FINAL GlobalFidelity:

approximately:
0.998989.

World fraction
FINAL >=0.95:

100%
in:
every group.

Maximum group-median
HALF-to-FINAL loss:

approximately:
0.000329.

Minimum group-median
late-life SelfRecovery:

remains:
above:
the frozen 0.95 floor.

PASS.

GLOBAL EXPOSURE QUALIFICATION

Cumulative absolute error exposure
relative to:
MICRO2-LEVERAGE.

Median ratios:

fine:

HOTSPOT clean:
approximately 1.140.

HOTSPOT eta=.25:
1.151.

ROAMING clean:
1.152.

ROAMING eta=.25:
1.169.

coarse:

HOTSPOT clean:
approximately 1.040.

HOTSPOT eta=.25:
1.096.

ROAMING clean:
1.033.

ROAMING eta=.25:
1.043.

Frozen ceiling:

<=1.25
for:
EVERY group.

PASS:
8 / 8.

Thus:

repair-history novelty
closes:
the single H168
coarse noisy-roaming
exposure failure

without:
breaking:
fine-scale exposure safety.

SECOND-QUERY DUTY

COARSE HOTSPOT

median duty:

0
for:
both eta classes.

Frozen target:
<=0.10.

PASS.

COARSE ROAMING

median duty:

0.45
for:
eta=0

and:
0.45
for:
eta=.25.

Frozen range:
0.25..0.70.

PASS.

Difference versus:
coarse HOTSPOT:

+0.45
for:
both eta classes.

Frozen minimum:
+0.20.

PASS.

Thus:

the target-blind
repair-history signal

correctly distinguishes:

MOVING DAMAGE

from:

REPEATED LOCAL HOTSPOT
TURNOVER.

FINE SCALE

HIST-GEOM duty
matches:
H168-GEOM duty

because:
the novelty branch
is:
gated to:
rho_geom<=0.50.

Median duty:

approximately:
0.620..0.644.

No:
>0.05
fine-scale duty inflation.

PASS.

OBSERVATION COST

Pooled observation reduction
relative to:
MICRO2-LEVERAGE:

g=1.00:

approximately:
41.25%
median reduction.

Frozen target:
>=25%.

PASS.

g=.25:

approximately:
18.66%.

Frozen target:
>=15%.

PASS.

EXPOSURE IMPROVEMENT
VERSUS:
H168-GEOM

COARSE ROAMING

eta=0:

median exposure reduction:

approximately:
4.30%.

Frozen target:
>=5%.

FAIL,
narrowly.

eta=.25:

approximately:
5.94%.

PASS.

Thus:

repair history
provides:
the intended
coarse-roaming
exposure improvement,

but:

the clean-roaming
effect-size gate
misses
by:
approximately:
0.70 percentage points.

COARSE HOTSPOT
NON-REGRESSION

Exposure change
versus:
H168-GEOM:

approximately:
0%
in:
both eta classes.

Frozen maximum increase:
5%.

PASS.

ORACLE

LOCAL-CHECKPOINT-ORACLE:

FINAL GlobalFidelity
exactly:
1.0.

PASS.

PRIMARY GATE REVIEW

PASS:

1.
MICRO2-LEVERAGE baseline.

2.
HIST-GEOM safety qualification.

3.
HIST-GEOM global exposure qualification.

4.
Coarse HOTSPOT low second-query duty.

5.
Coarse ROAMING selective duty.

6.
ROAMING / HOTSPOT duty separation.

7.
No fine-scale duty inflation.

8.
Observation reduction:
coarse and fine.

10.
No coarse HOTSPOT exposure regression.

11.
Oracle ceiling.

FAIL / MIXED:

9.
>=5%
exposure reduction
versus:
H168-GEOM

in:
both coarse ROAMING eta groups.

Observed:

clean:
approximately 4.30%.

noisy:
approximately 5.94%.

FAIL:
1 / 2
by:
approximately 0.70 percentage points.

STRONG SUPPORT:

FAIL.

FINAL INTERPRETATION

H169 is:

MIXED-POSITIVE.

The important architectural question
is:
answered positively.

TARGET-BLIND
REPAIR HISTORY

adds:
useful functional-risk information

that:
query geometry alone
does not contain.

The combined controller:

- uses:
  one query
  in:
  coarse stable HOTSPOT repair;

- uses:
  approximately 1.45 queries / cycle
  in:
  coarse ROAMING repair;

- uses:
  approximately 1.62 queries / cycle
  at:
  fine scale;

- remains:
  globally exposure-qualified;

- preserves:
  near-perfect
  long-horizon task fidelity;

- does NOT:
  need:
  held-out task error
  to:
  choose:
  query count.

This is:
the first accepted controller
in this chain
that combines:

SCALE-AWARE
INFORMATION DEMAND

with:

TURNOVER-HISTORY
RISK

while:

remaining:
target-blind
at:
the query-purchase layer.

ARCHITECTURAL CONSEQUENCE

The synthetic repair-control stack
is now:

1.
detect / localize:
the lesion;

2.
regrow:
membership;

3.
use:
developmental context
as:
the local prior;

4.
always acquire:
one:
maximum-leverage
functional observation;

5.
buy:
a second
only when:

   a.
   geometric residual information
   is:
   high;

   OR:

   b.
   coarse repair history
   says:
   the wound
   is:
   moving through:
   novel cognitive territory;

6.
jointly solve:
the local lesion state;

7.
carry:
the repaired state
forward.

This is:
substantially cheaper
than:
the original:
24-observation
full-anchor architecture

and:
retains:
the transient-error
safety envelope.

RESEARCH PHASE CONSEQUENCE

At this point:

further tuning
of:
synthetic query-purchase thresholds

has:
diminishing architectural value.

The next major risk
is no longer:

HOW MANY
synthetic observations
to buy.

It is:

DO THESE
REGENERATIVE CONTROL LAWS
TRANSFER
TO:
ACTUALLY LEARNED
FUNCTIONAL SPECIALIZATION?

NEXT:

H170 —
LEARNED MICRO-FUNCTION
REGENERATION / TURNOVER
TRANSFER AUDIT.

The next model should:

- learn:
  local task specialization
  from data
  rather than:
  receive:
  an analytically generated
  coefficient field;

- preserve:
  small-cell
  local repair;

- remove:
  local learned state
  without:
  checkpoint restoration;

- regenerate:
  from:
  developmental context;

- use:
  the accepted:
  leverage + repair-history
  micro-anchor controller;

- test:
  whether:
  task accuracy,
  calibration,
  and:
  long-horizon turnover
  remain stable.

H169 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- global retraining;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
