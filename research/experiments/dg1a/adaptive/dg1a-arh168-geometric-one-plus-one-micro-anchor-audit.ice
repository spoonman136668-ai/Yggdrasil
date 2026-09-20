TITLE: DG-1A-AR-H168 — Geometric One-Plus-One Micro-Anchor Exposure-Control Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh167-single-observation-information-design-micro-anchor-audit.ice

PURPOSE

H167 established:

one leverage-selected
functional observation
per:
repair cycle

is:
fully qualified
at:
g=1.00

and:
nearly qualified
at:
g=.25.

The only H167 failure:

two fine-scale groups
exceeded:
the frozen
1.25x
transient-error exposure ceiling

by:
small margins.

H167 also established:

a second:
leverage-selected observation

materially reduces:
error exposure.

Therefore:

the next question is:

CAN
THE ORGANISM
BUY:
THE SECOND QUERY

ONLY WHEN:
THE QUERY GEOMETRY
SAYS:
IT IS STILL
HIGHLY INFORMATIVE?

This must be:

TARGET-BLIND.

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
H167/H166
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

COMMON CANDIDATE POOL

Each repair cycle:

64 deterministic
lesion-local candidate queries.

No:
candidate target value

may enter:
query ranking
or:
the second-query decision.

FIRST QUERY

Choose:

q1

by:
maximum leverage

under:

A0 =
lambda I.

lambda:

0.01.

Let:

L1 =
q1^T
A0^-1
q1.

Update:

A1 =
A0
+
q1 q1^T.

SECOND-QUERY VALUE SCORE

Among:
all unselected candidates,

choose:
q2

with:
maximum leverage
under:
A1.

Let:

L2 =
q2^T
A1^-1
q2.

Define:

rho_geom =
L2 / L1.

Interpretation:

rho_geom
measures:

how much:
target-blind
information value

remains
after:
the first selected query.

GEOMETRIC PURCHASE RULE

PRIMARY CANDIDATE:

GEOM-1PLUS1-098.

Always:
acquire q1.

Acquire q2
iff:

rho_geom
>=
0.98.

Threshold:

0.98.

This threshold
is:
frozen
before:
H168 sanity.

RATIONALE

H167 accepted-development data
showed:

coarse-scale
rho_geom

approximately:
0.35..0.46.

Fine-scale
rho_geom

approximately:
0.94..0.99,

with:
median
near:
0.982.

Thus:

0.98

is:
a round
geometry-only
value threshold

that:
does NOT:
read:
functional targets

and:
creates:
a falsifiable
fresh-seed
generalization test.

No:
H168 held-out seed

was used:
to select:
0.98.

REPAIR

After:
100%
membership return:

- acquire:
  q1 target;
- acquire:
  q2 target
  only if:
  rho_geom >=0.98;
- joint-solve:
  all restored lesion coefficients;
- lambda=0.01;
- current context state:
  ridge prior;
- surviving coefficients:
  fixed;
- selected observation(s)
  remain:
  active constraints
  through:
  all 12
  post-membership
  maturation steps.

No:
raw observation
is reused
across:
different repair cycles.

Mutable repaired state:
persists.

POLICIES

A — MICRO2-LEVERAGE

H167
two information-designed
observations
every cycle.

Exposure-safe reference.

B — MICRO1-LEVERAGE

H167
one information-designed
observation
every cycle.

Low-cost comparator.

C — GEOM-1PLUS1-098

PRIMARY CANDIDATE.

Always:
one leverage query.

Second:
iff:

rho_geom >=0.98.

D — CONTEXT-ONLY

Zero:
functional observations.

E — LOCAL-CHECKPOINT-ORACLE

Exact target coefficient restore
on:
membership return.

Evaluation ceiling only.

COST ACCOUNTING

Report:

- first-query count;
- second-query count;
- second-query duty;
- total observations;
- average observations / cycle;
- observations per:
  body-equivalent turnover.

GEOM-1PLUS1:

minimum:
1.0 obs / cycle.

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
5.

Policy lifetimes:

600.

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
rho_geom distribution;

8.
second-query duty;

9.
total observations;

10.
average observations / cycle;

11.
exposure ratio
versus:
MICRO2-LEVERAGE;

12.
exposure ratio
versus:
MICRO1-LEVERAGE;

13.
coarse / fine
duty interaction;

14.
ROAMING / HOTSPOT
interaction;

15.
eta interaction;

16.
oracle gap.

GLOBAL SAFETY RULE

GEOM-1PLUS1-098
is:
SAFETY-QUALIFIED

iff:

1.
median FINAL GlobalFidelity
>=0.98
for:
every group;

2.
>=90%
of worlds
finish:
FINAL >=0.95
for:
every group;

3.
group-median
HALF-to-FINAL loss
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

GEOM-1PLUS1-098
is:
EXPOSURE-QUALIFIED

iff:

group-median
cumulative absolute error exposure

is:
no more than:
1.25x

MICRO2-LEVERAGE

for:
every group.

MICRO2-LEVERAGE
is:
the stronger
H167
information-designed
two-query reference.

PRIMARY ACCEPTANCE SHAPE

H168 supports:
GEOMETRIC
ONE-PLUS-ONE
MICRO-ANCHORING

if:

1.
MICRO2-LEVERAGE
reproduces:
H167-level safety.

2.
GEOM-1PLUS1-098
is:
SAFETY-QUALIFIED.

3.
GEOM-1PLUS1-098
is:
EXPOSURE-QUALIFIED.

4.
Median second-query duty

<=0.10

for:
every:
g=1.00
regime x eta group.

5.
Median second-query duty

is:
>0.10
and:
<0.90

for:
at least:
three of:
four
g=.25
regime x eta groups.

This tests:
true:
selective
fine-scale purchase

rather than:
always-two.

6.
Average observations / cycle

<2.0
for:
every group.

7.
Pooled:
total observation reduction

relative to:
MICRO2-LEVERAGE

>=40%

at:
g=1.00

and:
>=15%

at:
g=.25.

8.
GEOM-1PLUS1
cumulative exposure

is:
lower than:
MICRO1-LEVERAGE

in:
at least:
three of:
four
fine-scale groups.

9.
Pooled:
fine-scale exposure

is:
at least:
5%
lower
than:
MICRO1-LEVERAGE.

10.
LOCAL-CHECKPOINT-ORACLE
remains:
the capability ceiling.

STRONG SUPPORT

H168 receives:
STRONG support

if:

all primary gates pass

and:

GEOM-1PLUS1
pooled exposure

is:
within:
10%
of:
MICRO2-LEVERAGE

at:
both scales.

MIXED / NEGATIVE CONDITIONS

Treat H168 as:
mixed / negative
if:

- rho_geom
  fails to:
  separate:
  coarse and fine
  information demand;

- second-query duty
  approaches:
  100%
  at:
  fine scale;

- observation savings
  disappear;

- exposure remains:
  above:
  the 1.25x envelope;

- geometric selection
  saves observations
  but:
  harms:
  final fidelity;

- target-blind geometry
  does not:
  predict:
  which repair cycles
  need:
  the second observation.

PRIMARY WORLD SEEDS

20260921700000
through:
20260921700119.

SANITY WORLD SEEDS

20260921790000...

Sanity:
NON-EVIDENCE.

No:
rho_geom threshold,
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
the first held-out H168 lifetime.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_GEOMETRIC_ONE_PLUS_ONE_MICRO_ANCHOR_EXPOSURE_CONTROL

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — GEOMETRIC ONE-PLUS-ONE HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H168 HELD-OUT PRIMARY EXECUTION.

FINAL H168 SANDBOX HARNESS

File:

h168_geom_1plus1_v1.py

SHA-256:

85053ccadd5557d57f1590fc1a99653acd2352f3823f56499b7165d0dfb3e83e.

PARENT H167 HARNESS

SHA-256:

f9c1689f1ca9112b3c698d401a7f20308d1f70b7285be13ca3fb852bd5c2733d.

GEOMETRIC PURCHASE RULE

Always:

select:
q1

as:
maximum-leverage
target-blind query.

Compute:

q2

as:
maximum remaining leverage
after:
rank-one
information update.

Define:

rho_geom =
L2 / L1.

Acquire:
q2

iff:

rho_geom >=0.98.

No:
functional target value

enters:
rho_geom.

REPAIR

Selected:
one or two
functional observations

are:
used
in:
one joint lesion solve

after:
100%
membership return.

lambda:

0.01.

Current context state:

ridge prior.

Selected observations
remain:
active constraints
through:
all 12
post-membership
maturation steps.

Mutable repaired state:
persists
cycle to cycle.

SANITY

Disjoint family:

20260921790000...

6 representative
condition-world lifetimes.

5 policies.

30 policy lifetimes.

Mechanical checks:

- exactly five policies / seed;
- exact six sanity seeds;
- LOCAL-CHECKPOINT-ORACLE
  final fidelity exactly 1.0;
- MICRO1-LEVERAGE:
  exactly one observation / cycle;
- MICRO2-LEVERAGE:
  exactly two / cycle;
- GEOM-1PLUS1:
  one or two only;
- no target value
  enters:
  query purchase decision;
- no global reset.

Accepted sanity matrix
SHA-256:

a916f25dfec5a29237a167ebe4eafc14322faa04b89da5399293427875b9193b.

NON-EVIDENCE SIGNAL

Coarse:
g=1.

GEOM-1PLUS1
second-query duty:

0
in:
all three
representative coarse sanity lifetimes.

Therefore:

it behaves:
identically
to:
MICRO1-LEVERAGE

on:
those coarse geometries.

Fine:
g=.25.

Second-query duty:

approximately:
0.616
to:
0.623

in:
the three
representative fine-scale
sanity lifetimes.

Thus:

the geometry-only
rho threshold

creates:
selective:
one-plus-one behavior

rather than:
always-two.

Representative fine exposure:

ROAMING,
eta=0:

MICRO1-LEVERAGE:
approximately 0.304.

GEOM-1PLUS1:
approximately 0.209.

MICRO2-LEVERAGE:
approximately 0.170.

ROAMING,
eta=.25:

approximately:
0.435
->
0.305
->
0.241.

HOTSPOT,
eta=.25:

approximately:
0.437
->
0.287
->
0.239.

One:
fine noisy sanity cell

remains:
slightly above:
the frozen
1.25x
MICRO2-LEVERAGE
exposure envelope.

This is:
NON-EVIDENCE.

No:

- rho threshold;
- query rule;
- observation cap;
- sample size;
- exposure ceiling;
- acceptance gate

is changed.

PRIMARY FAMILY

20260921700000..20260921700119.

120 held-out
condition-world lifetimes.

5 policies.

600 policy lifetimes.

H168 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H168 lifetime.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
