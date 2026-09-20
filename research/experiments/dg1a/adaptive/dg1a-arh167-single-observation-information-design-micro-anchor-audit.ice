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
