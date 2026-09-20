TITLE: DG-1A-AR-H167 — Single-Observation Information-Design Micro-Anchor Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh166-minimal-micro-anchor-budget-turnover-audit.ice

PURPOSE

H166 established:

one local functional observation
on:
EVERY repair cycle

preserves:
high final task fidelity,
world reliability,
and:
long-horizon drift control.

But:

MICRO1-EVERY1
fails:
the frozen transient-error
exposure envelope

relative to:
MICRO2-EVERY1.

H166 also established:

the same average budget
delivered:
less regularly

is:
materially worse.

Therefore:

cadence is:
already correct.

The remaining question is:

CAN
ONE OBSERVATION
PER:
REPAIR CYCLE

BE:
SELECTED
MORE INTELLIGENTLY

SO THAT:

- final fidelity stays high;
- late-life SelfRecovery stays high;
- cumulative absolute error exposure
  returns inside:
  the H166
  1.25x envelope;
- the second observation
  becomes unnecessary?

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

20 repair cycles.

g=0.25:

292 repair cycles.

No:
global reset.

No:
checkpoint restore
outside:
LOCAL-CHECKPOINT-ORACLE.

COMMON MICRO-ANCHOR POOL

Every repair cycle:

construct:
the exact H166
lesion-local candidate pool.

Candidate count:

64.

Each candidate:

- selects:
  one lesion member;
- centers on:
  its normalized location;
- adds:
  Gaussian jitter sd=0.12;
- rejects:
  outside:
  the unit disk.

Target values:

immutable original task function

with:
the declared eta noise.

QUERY SELECTION MUST BE
TARGET-BLIND.

No:
candidate target value,
lost coefficient,
held-out evaluation output,
or:
latent context label

may enter:
query ranking.

ONE-QUERY LEVERAGE RULE

Let:

Phi_L

be:
the 64 x K
candidate design matrix

restricted to:
the K
restored lesion coefficients.

Let:

A =
lambda * I.

lambda:

0.01.

For candidate row q_j:

score_j =
q_j^T
A^-1
q_j.

Select:

argmax_j score_j.

Tie:

lowest deterministic
candidate index.

Because:

A =
lambda I

and:
only one query
is selected,

one-shot:
A-optimal
trace reduction

is:
monotonic in:
the same q_j norm

and therefore:
produces:
the same ordering.

H167 does NOT:
treat:
one-query A-opt
as:
an independent policy.

MICRO-ANCHOR REPAIR

After:
100%
membership return:

- acquire:
  the policy-selected
  1 or 2
  functional observations;
- jointly solve:
  all restored lesion coefficients;
- lambda=0.01;
- current context state:
  ridge prior;
- surviving coefficients:
  fixed;
- retain:
  those observations
  as:
  active constraints
  through:
  all 12
  post-membership
  maturation steps.

No:
observation
is reused
across:
different repair cycles.

The repaired coefficient state:
does persist.

POLICIES

A — MICRO2-EVERY1

Exact H166
two-observation-every-cycle
baseline.

Uses:
the first two
deterministic H166
micro-anchor queries.

B — MICRO1-FIRST

Exact H166
MICRO1-EVERY1.

Uses:
the first
deterministic
micro-anchor query.

C — MICRO1-LEVERAGE

PRIMARY CANDIDATE.

Uses:
one
target-blind
maximum-leverage query

from:
the same 64-query
candidate pool.

D — MICRO2-LEVERAGE

Diagnostic.

Choose:
two queries
greedily by:
leverage / D-optimal
rank-one updates.

Tests:

whether:
information design
also improves:
the two-observation
reference.

E — CONTEXT-ONLY

Zero:
functional observations.

F — LOCAL-CHECKPOINT-ORACLE

Exact target coefficient
restore
on:
membership return.

Evaluation ceiling only.

MICRO2-LEVERAGE

For:
query 1:

select:
maximum leverage
under:
A=lambda I.

Update:

A
with:
the selected query outer product.

For:
query 2:

select:
maximum leverage
under:
the updated A.

No:
target value
enters:
selection.

COST

MICRO2 policies:

2 observations / cycle.

MICRO1 policies:

1 observation / cycle.

No:
escalation.

No:
full 24-observation anchor.

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
HALF-to-FINAL drift;

8.
query identity;

9.
selected leverage score;

10.
total observations;

11.
MICRO1-LEVERAGE
versus:
MICRO1-FIRST;

12.
MICRO2-LEVERAGE
versus:
MICRO2-EVERY1;

13.
coarse / fine interaction;

14.
ROAMING / HOTSPOT interaction;

15.
oracle gap.

GLOBAL QUALIFICATION RULE

A one-observation policy
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

H167 supports:
SINGLE-OBSERVATION
INFORMATION-DESIGNED
MICRO-ANCHORING

if:

1.
MICRO2-EVERY1
reproduces:
H166 baseline qualification.

2.
MICRO1-LEVERAGE
is:
GLOBALLY QUALIFIED.

3.
MICRO1-LEVERAGE
cumulative absolute error exposure

is:
lower than:
MICRO1-FIRST

in:
at least:
6 of:
8
g x regime x eta groups.

4.
Pooled:
MICRO1-LEVERAGE
absolute error exposure

is:
at least:
10%
lower
than:
MICRO1-FIRST

at:
g=1.00

and:
at least:
10%
lower

at:
g=0.25.

5.
MICRO1-LEVERAGE
does NOT:

reduce:
median FINAL fidelity

by:
more than:
0.005

relative to:
MICRO1-FIRST

in:
any group.

6.
MICRO1-LEVERAGE
does NOT:

reduce:
late-life SelfRecovery

by:
more than:
0.02

relative to:
MICRO1-FIRST

in:
any group.

7.
MICRO2-LEVERAGE
does NOT:
perform worse
than:
MICRO2-EVERY1

by:
more than:

0.005
median FINAL fidelity

or:

25%
cumulative exposure

in:
any group.

8.
LOCAL-CHECKPOINT-ORACLE
remains:
the capability ceiling.

STRONG SUPPORT

H167 receives:
STRONG support

if:

MICRO1-LEVERAGE
is:
GLOBALLY QUALIFIED

and:

its pooled cumulative
absolute error exposure

is:
within:
10%
of:
MICRO2-EVERY1

at:
both scales.

SCALE-SPECIFIC RESULT

Independently report:

whether:
MICRO1-LEVERAGE

qualifies:
within:
g=1.00

and:
within:
g=0.25

using:
the same:
quality,
reliability,
drift,
SelfRecovery,
and:
exposure rules

restricted to:
that scale.

MIXED / NEGATIVE CONDITIONS

Treat H167 as:
mixed / negative
if:

- leverage selection
  does not:
  reduce:
  one-observation
  exposure;

- leverage improves:
  exposure
  but:
  harms:
  final fidelity;

- one query
  remains:
  outside:
  the 1.25x exposure envelope;

- coarse roaming
  remains:
  the limiting case;

- fine scale
  unexpectedly needs:
  two observations;

- two-query leverage
  is:
  materially worse
  than:
  the deterministic
  H166 two-query baseline.

PRIMARY WORLD SEEDS

20260921600000
through:
20260921600119.

SANITY WORLD SEEDS

20260921690000...

Sanity:
NON-EVIDENCE.

No:
query-selection rule,
observation count,
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
the first held-out H167 lifetime.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_SINGLE_OBSERVATION_INFORMATION_DESIGN_TURNOVER

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — SINGLE-OBSERVATION INFORMATION-DESIGN HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H167 HELD-OUT PRIMARY EXECUTION.

FINAL H167 SANDBOX HARNESS

File:

h167_single_obs_info_v1.py

SHA-256:

f9c1689f1ca9112b3c698d401a7f20308d1f70b7285be13ca3fb852bd5c2733d.

PARENT HASHES

H161:

ae89e645e9f00f33a581c05298a0b2e930b450bbc9a55f0e0f46f87de86a8248.

H162:

2a8e405055d88906285934778898b02072dcdf683afd8cbc4d8f392c7461ae2c.

H165:

69e3a195ae9485b153a7a6efba254e5b68837359f0a0f5eb022108b1d5ede808.

H166:

1adf59a6d4ef84cb84165e78334b3c3ac8db9ac07bb3d1f4a03d0523c662a164.

QUERY DESIGN

Each repair cycle:

construct:
64 deterministic
lesion-local candidate queries.

Selection:

MICRO1-FIRST:

exact H166
first deterministic candidate.

MICRO1-LEVERAGE:

one target-blind query
maximizing:

q^T
(lambda I)^-1
q.

MICRO2-LEVERAGE:

two target-blind queries
selected greedily

with:
rank-one information-matrix updates.

lambda:

0.01.

No:

- candidate functional target;
- lost coefficient;
- held-out evaluation target;
- latent context label

enters:
query ranking.

Only:
the selected query target(s)

are:
used as:
repair evidence

and:
charged:
to supervision cost.

ONE-QUERY A-OPT NOTE

Under:

A =
lambda I

and:
one selected query,

A-optimal
trace reduction

is:
monotonic
in:
the same candidate
row norm

as:
one-query leverage.

Therefore:

one-query A-optimal
is:
not treated
as:
an independent policy.

REPAIR

All micro-anchor policies:

- wait for:
  100% membership return;
- joint-solve:
  the restored lesion coefficients;
- current context state:
  ridge prior;
- surviving coefficients:
  fixed;
- retain:
  selected observation(s)
  as:
  active constraints
  through:
  all 12
  post-membership
  maturation steps;
- persist:
  repaired mutable state
  into:
  later repair cycles.

No:
raw observation
is reused
across:
different wounds.

SANITY

Disjoint family:

20260921690000...

6 representative
condition-world lifetimes.

6 policies.

36 policy lifetimes.

Mechanical checks:

- exactly six policies / seed;
- exact six sanity seeds;
- LOCAL-CHECKPOINT-ORACLE
  final fidelity:
  exactly 1.0;
- MICRO1 policies:
  exactly one external observation / cycle;
- MICRO2 policies:
  exactly two / cycle;
- target-blind query ranking;
- no global reset.

A first sanity build
used:
Python's process-randomized
hash()

only for:
a query-identity
diagnostic column.

Before:
any H167 primary world,

that diagnostic
was replaced with:
deterministic SHA-256.

No:

repair,
query ranking,
functional target,
observation count,
or:
scientific metric

changed.

Accepted sanity output
SHA-256:

d2fad4e22c60cff87ea7b46ba29a7f606066ee117b11c05b9f59eb15370c961a.

NON-EVIDENCE SIGNAL

Across:
all six
representative sanity lifetimes,

MICRO1-LEVERAGE

had:
lower cumulative
absolute error exposure

than:
MICRO1-FIRST.

Representative:

g=1
ROAMING
eta=0:

MICRO1-FIRST exposure:
approximately 1.250.

MICRO1-LEVERAGE:
approximately 1.039.

g=1
ROAMING
eta=.25:

approximately:
1.233
->
0.813.

g=.25
ROAMING
eta=0:

approximately:
0.304
->
0.229.

g=.25
ROAMING
eta=.25:

approximately:
0.369
->
0.287.

Final fidelity
remained:
near:
the two-observation baseline.

These outputs are:

NON-EVIDENCE.

No:
query rule,
observation count,
cadence,
sample size,
exposure threshold,
or:
acceptance gate

was changed.

PRIMARY FAMILY

20260921600000..20260921600119.

120 held-out condition-world lifetimes.

6 policies.

720 policy lifetimes.

H167 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H167 lifetime.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
