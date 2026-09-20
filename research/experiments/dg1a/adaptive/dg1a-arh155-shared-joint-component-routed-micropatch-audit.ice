TITLE: DG-1A-AR-H155 — Shared Joint Solve / Component-Routed Functional Micro-Patch Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh154-residual-directed-component-local-repair-audit.ice

PURPOSE

H154 established:

LOCAL FUNCTIONAL RESIDUALS
CAN:
IDENTIFY
WHERE ERROR IS OBSERVED

but:

FUNCTIONAL PARAMETER ERROR
IS NOT:
STRICTLY SEPARABLE
BY:
WOUND COMPONENT.

The negative result was:
structural.

Independent component solves
discarded:
cross-component information
carried by:
the shared RBF readout.

H155 tests the direct correction:

ROUTE QUERIES LOCALLY.

SOLVE PARAMETERS JOINTLY.

All acquired training feedback,
regardless of:
which wound component generated it,

enters:
one coupled ridge solve
over:
all regenerated lesion coefficients.

Component validation residuals
are used only for:

- query routing;
- stop / reopen;
- diagnostic attribution.

They do NOT:
partition:
parameter inference.

BOUNDARY

Synthetic research only.

No:
production model repair,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or:
runtime activation.

PARENT MODEL

Reuse:
H151 / H152
colony mechanics.

R=8.
N approximately 197.
Gaussian RBF sigma=0.22.
repair p=0.50.
12 post-membership maturation steps.
ridge lambda=0.10.

Contexts:

SMOOTH,
MIXED,
SCRAMBLED.

Damage:

1%,
2%,
5%,
10%.

Geometry:

COMPACT,
FOUR-PATCH.

Surviving original coefficients:
remain immutable.

Lost original coefficients:
are never supplied
outside:
CHECKPOINT-ORACLE.

COMPONENT FEEDBACK POOLS

At lesion creation:

compute:
actual Moore-connected missing components.

Each component receives:
32 deterministic local query-target candidates.

Query:

- choose one member
  from:
  the component;
- use:
  its normalized response center;
- add:
  Gaussian jitter
  sd=0.12;
- reject:
  outside:
  unit disk.

Targets:

pre-lesion function
at:
that query.

Target becomes available:
only when:
the query is acquired.

TRAIN / VALIDATION SPLIT

Within each component pool:

0-based even candidate indices:
TRAIN.

0-based odd:
VALIDATION.

TRAIN:
enters:
the joint solve.

VALIDATION:
never enters:
the solve.

Validation is used only for:
component residual estimation,
routing,
stop,
and:
reopen.

JOINT PARAMETER SOLVE

Let:

L =
all regenerated lesion cells.

Let:

T =
all acquired TRAIN queries
from:
all lesion components.

Solve:

argmin_w_L

||Phi_L(T) w_L - r(T)||^2

+
0.10 ||w_L - w_context||^2.

Residual target r(T):

feedback target
minus:
the immutable surviving-cell contribution.

All lesion coefficients
are:
optimized jointly.

No:
component-isolated solve.

No:
lost coefficient checkpoint.

CONTEXT PRIOR

w_context:

the current
H151 context-harmonic
reconstruction
for:
all regenerated lesion cells.

Before:
each functional solve,

one ordinary H151
context-refinement step
is applied.

COMPONENT VALIDATION RESIDUAL

For each component c:

R_c =

current validation MSE
/
original-lesion validation MSE

on:
that component's
acquired VALIDATION queries.

R_c=0:
full correction
on:
the local validation set.

R_c=1:
no improvement
over:
the lesioned baseline.

STOP / REOPEN

A component is:
VALIDATED_RECOVERED

when:

- it has:
  at least two VALIDATION observations;

- R_c <=0.10;

- condition holds:
  two consecutive maturation steps.

Reopen:

R_c >0.15.

The query controller stops globally
only when:

all actual lesion components
are:
VALIDATED_RECOVERED

or:
the policy feedback cap
is exhausted.

ROUTING

Bootstrap priority:

1.
component with:
no TRAIN observation;

2.
component with:
no VALIDATION observation.

After bootstrap:

route next query
to:
the unstopped component
with:
largest observed R_c.

Tie:

larger component,
then:
lower stable component ID.

Priority:
recomputed
after:
each acquisition.

PRIMARY POLICIES

A — CONTEXT0

H151 context-only parent.

B — H152-FIXED-FB2

Frozen H152
shared-pool,
joint-lesion solve.

2 generated-order observations / step.

Maximum:
24.

Direct quality comparator.

C — JOINT-RR-FB2

Joint coupled solve.

2 observations / step.

Maximum:
24.

Round-robin
component query routing.

No:
adaptive stopping.

Isolates:
component-aware routing
without:
residual adaptation.

D — JOINT-ADAPT-FB2

PRIMARY CANDIDATE.

Joint coupled solve.

2 observations / step.

Maximum:
24.

Residual-directed:
component query routing.

Per-component:
validation stop / reopen.

Global early stop:
only when:
all components
are validated recovered.

E — JOINT-ADAPT-FB4

Same:
joint solve
and:
residual routing.

4 observations / step.

Maximum:
48.

Budget-ceiling comparator.

F — CHECKPOINT-ORACLE

Exact lost-state restoration.

Evaluation ceiling only.

PRIMARY FACTORIAL

3 contexts
x
4 damage fractions
x
2 geometries
x
100 worlds

=
2,400 underlying worlds.

6 policies.

14,400 policy-world evaluations.

PRIMARY METRICS

1.
final functional recovery;

2.
T50 / T90 / T99;

3.
T90-world fraction;

4.
functional downtime;

5.
feedback observations;

6.
feedback / missing coefficient;

7.
actual lesion component count;

8.
validated-recovered component count;

9.
component reopen count;

10.
routing entropy;

11.
median component stop step;

12.
max final component residual ratio;

13.
COMPACT / FOUR-PATCH interaction;

14.
JOINT-ADAPT-FB2
versus:
H152-FIXED-FB2;

15.
JOINT-ADAPT-FB2
versus:
JOINT-RR-FB2;

16.
JOINT-ADAPT-FB2
versus:
JOINT-ADAPT-FB4;

17.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H155 supports:
SHARED JOINT INFERENCE
WITH
COMPONENT-ROUTED FEEDBACK

if:

1.
MIXED 1%..5%,
JOINT-ADAPT-FB2
median final recovery
>=0.93.

2.
MIXED 1%..5%,
T90-world fraction
>=0.70
for:
all three fractions

and:
>=0.75
pooled.

This is:
a staged reliability improvement
over:
H152 / H154.

3.
Relative to:
H152-FIXED-FB2,

JOINT-ADAPT-FB2
improves:
T90-world fraction
by:
>=5 percentage points

in:
at least two of:
MIXED 1%,2%,5%,

OR:

matches:
T90-world fraction
within:
5 points

while:
using:
>=20%
fewer median observations.

4.
FOUR-PATCH,
MIXED 1%..5%:

T90-world fraction
is:
within:
10 percentage points
of:
COMPACT

in:
at least:
two of three
damage fractions.

5.
MIXED 1%..5%:

JOINT-ADAPT-FB2
uses:
<24
median observations

in:
at least:
two of three
fractions.

6.
At:
1% MIXED,

median feedback observations
<=12.

7.
JOINT-RR-FB2
does NOT:
materially underperform
H152-FIXED-FB2
in:
median final recovery.

Defined:

no more than:
0.02 lower
for:
at least:
two of three
MIXED 1%..5%
fractions.

This tests:
whether:
local routing
is compatible
with:
joint inference.

8.
JOINT-ADAPT-FB2
is:
within:
0.03
median final recovery
of:
JOINT-ADAPT-FB4

for:
at least:
two of:
MIXED 1%,2%,5%.

9.
SMOOTH 1%..5%
median final recovery
>=0.95.

10.
SCRAMBLED
remains:
materially below:
SMOOTH

under:
JOINT-ADAPT-FB2.

11.
CHECKPOINT-ORACLE
remains:
the ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H155 as:
mixed / negative
if:

- joint inference
  does not recover:
  H152-level quality;

- component routing
  lowers:
  distributed-patch reliability;

- component residuals
  remain:
  poorly calibrated
  for:
  query allocation;

- adaptive stopping
  still spends:
  the full 24
  on:
  nearly every small lesion;

- FB4
  remains:
  necessary
  for:
  reliable recovery;

- global joint solving
  produces:
  unstable cross-component updates;

- surviving original coefficients
  must be changed
  to:
  recover.

SANITY

Disjoint family:

20260920290000...

Representative cells:

MIXED 1% COMPACT;
MIXED 1% FOUR;
MIXED 2% FOUR;
MIXED 5% COMPACT;
MIXED 5% FOUR;
SMOOTH 2% FOUR;
SCRAMBLED 5% FOUR.

20 worlds / cell.

Sanity outputs:
NON-EVIDENCE.

No:
threshold,
budget,
lambda,
routing rule,
or:
acceptance gate
may change
from:
sanity results.

PRIMARY SEEDS

20260920200000
through:
20260920202399.

No execution-semantic change
after:
the first held-out H155 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_SHARED_JOINT_COMPONENT_ROUTED_MICROPATCH

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — SHARED JOINT / COMPONENT ROUTING

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H155 HELD-OUT PRIMARY EXECUTION.

No H155 primary world
has been executed.

SANDBOX HARNESS SHA-256

218273da8e2a8bb91793a24c54e2f4c19e28f594bc49cc9a31dccf1a92ab3b4f.

JOINT SOLVE

All acquired TRAIN observations
from:
all actual lesion components

enter:
one ridge solve
over:
all regenerated lesion coefficients.

Ridge lambda:
0.10.

Surviving original coefficients:
fixed.

Context-harmonic current reconstruction:
joint prior.

No lost coefficient:
is read.

COMPONENT ROUTING

Actual:
Moore-connected lesion components.

Stable ordering:
ascending minimum member ID.

Each component:
32 deterministic local query candidates.

TRAIN:
0-based even candidate index.

VALIDATION:
0-based odd.

Adaptive bootstrap:

- no TRAIN first;
- then no VALIDATION;
- then largest observed validation residual ratio.

Tie:

larger component,
then:
lower component ID.

STOP / REOPEN

Component recovered:

>=2 validation observations

AND:

residual ratio <=0.10

for:
two consecutive maturation steps.

Reopen:

ratio >0.15.

JOINT-ADAPT-FB2
stops acquiring
only when:
all actual components
are stopped

or:
24 total observations
are spent.

JOINT-RR-FB2

2 observations / step.

24 total.

Round-robin:
component routing.

No:
adaptive stop.

JOINT-ADAPT-FB4

4 observations / step.

48 total.

Same:
joint solve
and:
adaptive routing.

PARENT COMPARATOR

H152-FIXED-FB2
uses:
the exact inherited H152
shared feedback-pool
joint lesion solve.

SANITY

Disjoint:
20260920290000...
family.

140 underlying worlds.

840 policy-world evaluations.

NON-EVIDENCE.

Mechanical checks passed:

- all frozen policies completed;
- only lesion coefficients changed;
- query routing remained component-local;
- all training data entered:
  one joint solve;
- validation targets never entered:
  the solve;
- no lost coefficients entered:
  non-oracle repair.

Scientific sanity signal:

- SMOOTH remained:
  highly recoverable;

- MIXED compact wounds
  sometimes reduced:
  feedback use;

- MIXED FOUR-PATCH
  remained:
  difficult;

- more feedback
  did not:
  obviously resolve:
  validation/routing mismatch.

No:
threshold,
budget,
lambda,
routing rule,
sample size,
or:
acceptance gate

was changed
from:
sanity results.

PRIMARY FAMILY REMAINS

20260920200000..20260920202399.

No execution-semantic change
after:
the first held-out H155 primary world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — SHARED JOINT / COMPONENT-ROUTED FUNCTIONAL MICRO-PATCH

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / NEGATIVE.

FROZEN HARNESS SHA-256

218273da8e2a8bb91793a24c54e2f4c19e28f594bc49cc9a31dccf1a92ab3b4f.

ACCEPTED PRIMARY FAMILY

20260920200000..20260920202399.

PRIMARY MATRIX

2,400 underlying worlds.

6 policies.

14,400 policy-world evaluations.

Validation:

- exactly 2,400 unique held-out seeds;
- exact accepted seed interval;
- exactly six policy rows per seed;
- no accepted-seed gaps;
- no accepted-seed duplicates;
- zero functionally-trivial worlds;
- no post-primary parameter tuning.

PRIMARY CANDIDATE

JOINT-ADAPT-FB2.

MIXED 1%..5%
median final recovery:

1%:
0.8927.

2%:
0.8632.

5%:
0.8843.

Required:
>=0.93.

FAIL:
all three.

MIXED T90-world fraction:

1%:
54.0%.

2%:
46.0%.

5%:
52.0%.

Required:

>=70%
for all three

and:
>=75%
pooled.

FAIL.

PARENT H152 FIXED SHARED-POOL COMPARATOR

H152-FIXED-FB2
median final recovery:

1%:
0.9425.

2%:
0.9099.

5%:
0.9378.

T90-world fraction:

1%:
67.0%.

2%:
54.0%.

5%:
66.0%.

Thus:

the H155 adaptive component router
is:
materially worse
than:
the simpler H152
shared-pool joint solve.

LOCAL ROUTING VERSUS H152

JOINT-ADAPT-FB2
does NOT:

improve:
T90 world fraction

by:
>=5 points

in:
two small-lesion groups.

Observed differences:

1%:
-13 points.

2%:
-8.

5%:
-14.

It also:

does NOT:
match within 5 points

while:
saving >=20%
observations.

Pooled median observations:

1%:
24.

2%:
24.

5%:
24.

FAIL.

FOUR-PATCH RELIABILITY

JOINT-ADAPT-FB2
T90-world fraction:

MIXED 1%:

COMPACT:
65%.

FOUR:
43%.

gap:
22 points.

MIXED 2%:

COMPACT:
70%.

FOUR:
22%.

gap:
48 points.

MIXED 5%:

COMPACT:
74%.

FOUR:
30%.

gap:
44 points.

Required:

FOUR
within:
10 points
of:
COMPACT

in:
at least two of three.

FAIL:
0 / 3.

Thus:

global joint parameter inference
alone
does NOT:
remove:
the distributed-wound feedback-allocation failure.

FEEDBACK COST

JOINT-ADAPT-FB2
pooled median observations:

1%:
24.

2%:
24.

5%:
24.

Required:

<24
for:
at least two of three.

FAIL.

At:
1% MIXED,

required:
<=12.

Observed pooled:
24.

FAIL.

Compact-only
can stop earlier:

1% compact:
18.

2% compact:
20.

5% compact:
18.

But:
FOUR-PATCH
drives:
the pooled behavior
back to:
the full cap.

ROUND-ROBIN JOINT COMPATIBILITY

JOINT-RR-FB2
median final recovery:

1%:
0.9075.

2%:
0.8746.

5%:
0.9116.

H152-FIXED-FB2:

1%:
0.9425.

2%:
0.9099.

5%:
0.9378.

Deficits:

approximately:
0.0350,
0.0354,
0.0263.

Required:

no more than:
0.02
in:
at least two of three.

FAIL.

Therefore:

the information loss
is not:
only the adaptive routing rule.

Partitioning the feedback stream
into:
component-local TRAIN / VALIDATION pools

already:
reduces:
joint inference quality.

FB2 VERSUS FB4

JOINT-ADAPT-FB4
median final recovery:

1%:
0.8642.

2%:
0.8619.

5%:
0.8860.

Absolute FB2 / FB4 gaps:

1%:
approximately 0.0284.

2%:
approximately 0.0013.

5%:
approximately 0.0017.

Thus:

FB2 is:
within 0.03
of:
FB4

for:
all three.

PASS.

But:

the absolute quality
of:
both
is:
below target.

More observations
do NOT:
repair:
the architecture.

SMOOTH

JOINT-ADAPT-FB2
median final recovery:

1%:
0.9866.

2%:
0.9828.

5%:
0.9768.

PASS:
all >=0.95.

SCRAMBLED

JOINT-ADAPT-FB2
median final recovery:

1%:
0.3568.

2%:
0.2230.

5%:
0.4121.

Remains:
materially below:
SMOOTH.

PASS:
mechanism specificity remains.

CHECKPOINT-ORACLE

Remains:
the ceiling
at:
1.0.

PASS.

PREREGISTERED GATE REVIEW

PASS:

1.
FB2 is:
within 0.03
of:
FB4
for:
all three small MIXED damage fractions.

2.
SMOOTH
1%..5%
final recovery
>=0.95.

3.
SCRAMBLED
remains:
materially below:
SMOOTH.

4.
CHECKPOINT-ORACLE
remains:
the ceiling.

FAIL:

1.
MIXED final-recovery target.

2.
MIXED T90 reliability target.

3.
Improvement / efficient-match
versus:
H152 fixed.

4.
FOUR-PATCH reliability parity.

5.
<24 observation target.

6.
1% <=12 observation target.

7.
Round-robin joint compatibility
with:
H152 fixed.

FINAL INTERPRETATION

H155 is:

NEGATIVE.

H154 correctly identified:
that parameter inference
must preserve:
cross-wound coupling.

H155 confirms:

A GLOBAL JOINT SOLVE
IS NECESSARY

but:

IT IS NOT SUFFICIENT.

The new failure is:

FEEDBACK PARTITIONING.

The component-routed design
spends:
approximately half
of:
its local feedback stream

on:
VALIDATION-only observations

that:
do not train:
the joint solve.

It also:

allocates training data
through:
component-local pools

whose sampling distribution
can be:
less informative
than:
H152's shared local pool.

The result:

simpler H152
shared-pool feedback

beats:
both:
adaptive
and:
round-robin
component-routed H155.

ARCHITECTURAL CONSEQUENCE

Do NOT:

return to:
independent component parameter solves.

Do NOT:

increase:
the observation cap
as:
the first response.

Next:

retain:

- joint inference;
- component identity;
- local candidate pools;

but:

make:
EVERY ACQUIRED QUERY
TRAIN:
the shared solve.

Use:

the PRE-FIT
observed task residual
of:
each acquired local query

to update:
a component need score.

Then:

route:
the next query

toward:
the component
with:
highest observed residual pressure.

This avoids:

- validation-only information waste;
- independent parameter decomposition;
- hidden-target routing.

The already-preregistered
residual-routed global-joint design
captures:
this correction

and should be:
reissued
under:
the next unused experiment identifier

rather than:
running a second H155 primary.

H155 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- global retraining;
- biological claims;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
