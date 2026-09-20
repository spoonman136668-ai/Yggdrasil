TITLE: DG-1A-CLR3-H189 — Dormancy Cross-Branch Residual Distillation Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / CAPABILITY HIBERNATION / SLEEP COMPENSATION
BRANCH: dg1a-ar
PARENT: dg1a-clr3-h188-hibernation-active-compute-scaling-audit.ice

PURPOSE

H188 established:

- three learned capabilities can remain stored;
- B-only and C-only scheduled inference can run at approximately 2% of full all-branch compute;
- equal A/B/C scheduled inference can run at approximately 33.6% of full compute;
- routing accuracy is high;
- wake learning cost is zero;
- state and predictions do not drift through repeated hibernation/reactivation.

But:

strict branch decomposability fails for B.

The full phenotype contains a small, useful cross-capability residual
that is lost when all non-B branches are hibernated.

H189 asks:

CAN:
THAT CROSS-BRANCH RESIDUAL

BE:
SELF-DISTILLED

INTO:
A TINY
BRANCH-LOCAL
SLEEP-COMPENSATION STATE

USING:

- unlabeled context coordinates;
- the model's own stored full predictions;

WITHOUT:

- task target replay;
- coefficient retraining;
- extra physical cells;
- reactivating all dormant branches at inference?

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT PHENOTYPE

Reuse:
the exact H188/H187
WARP48_ROLE48_C
stored phenotype.

No:
A,
B,
C
functional coefficient
is:
modified.

No:
B warp parameter
is:
modified.

No:
router
is:
modified.

SLEEP-COMPENSATION TARGET

For:
capability context T
in:
{A,B,C},

define:

r_T(x)
=
f_full(x)
-
f_T_branch(x).

This is:

the contribution
of:
all other stored branches

to:
the full phenotype
inside:
context T.

The target:

is produced
by:
the model itself.

No:
ground-truth task output
is required.

UNLABELED DISTILLATION INPUTS

For:
each capability context:

sample:
128 deterministic
context coordinates

from:
the exact:
A,
B,
or:
C
context distribution.

These coordinates are:

disjoint from:

- capability training sets;
- validation sets;
- held-out test sets;
- H188 switch probes.

At:
these coordinates:

evaluate:

f_full(x)
and:
f_T_branch(x).

Compute:

r_T(x).

No:
teacher / task target
is read.

COMPENSATION FEATURE MAP

For input:
(x,y),

features:

[1,
 x,
 y,
 x^2,
 x*y,
 y^2].

Standardize:
non-bias features

using:
the 128
distillation coordinates
for:
that capability only.

Fit:
one:
six-parameter
ridge model

per:
capability.

Ridge alpha:

0.001.

Thus:

total:
sleep-compensation parameters

=
18.

No:
hidden layer.

No:
new cell.

No:
task-specific basis population.

COMPENSATED SCHEDULED OUTPUT

Known-context:

f_T_sleep(x)
=
f_T_branch(x)
+
c_T(x).

Learned-router scheduled:

1.
use:
the exact H188
B/C routing rule;

2.
select:
one capability branch;

3.
evaluate:
that branch;

4.
add:
that selected capability's
six-parameter
sleep compensation.

Dormant:
other capability branches

remain:
unevaluated.

COMPENSATION MEMORY

All:
18 compensation parameters

remain:
stored.

They are:

tiny:
non-cellular
sleep-state summaries.

They do NOT:
replace:
the full stored
A/B/C model state.

They only:
permit:
inactive branch compute
to:
remain asleep

while:
preserving:
the full phenotype's
local prediction.

COMPARATORS

A — NO_COMP

Exact:
H188
scheduled inference.

B — COMP6

PRIMARY CANDIDATE.

Six:
quadratic compensation parameters
per capability.

C — COMP3_LINEAR

Diagnostic.

Features:

[1,x,y].

Three parameters
per capability.

Tests:
whether:
even smaller
sleep state
is sufficient.

FULL PHENOTYPE

Reference only.

All:
A+B+C branches active.

PRIMARY METRICS

Per capability:

- full held-out R^2;
- no-comp known-schedule R^2;
- COMP6 known-schedule R^2;
- COMP3 known-schedule R^2;
- no-comp learned-schedule R^2;
- COMP6 learned-schedule R^2;
- COMP3 learned-schedule R^2.

Prediction fidelity:

normalized MSE
versus:
full phenotype

for:
known-context
and:
learned-router
scheduled outputs.

Residual-distillation fidelity:

held-out:
MSE(
compensation,
true cross-branch residual
)
/
Var(
true cross-branch residual
).

Report:
absolute residual MSE
when:
residual variance
is:
very small.

ROUTING

Exact:
H188.

No:
routing update.

COMPUTE

Full all-branch:

same:
H188:
3322 proxy units / sample.

COMP6 learned-scheduled:

router overhead:
12.

Selected branch:

A:
3209.

B:
53.

C:
48.

Plus:
6:
compensation operations.

Thus:

A:
3227.

B:
71.

C:
66.

Equal:
A/B/C:

approximately:
1121.3.

Ratio:
approximately:
33.75%
of:
full.

B-only:

approximately:
2.14%.

C-only:

approximately:
1.99%.

COMP3:

uses:
3 compensation ops
instead.

MEMORY

H188 learned-state:

3322
functional parameters.

COMP6 adds:

18.

Total:

3340.

Increment:

approximately:
0.54%.

No:
physical cells
are:
added.

DISTILLATION COST

Report:

- full-model evaluations:
  128
  per:
  capability;

- branch-only evaluations:
  128
  per:
  capability;

- six-parameter
  ridge solve.

This is:
one-time
sleep preparation.

No:
task label
is required.

WAKE / SWITCH

Repeat:
the H188
300-switch
A->B->C
sequence.

Use:
COMP6
learned-scheduled output.

No:
parameter update.

No:
compensation refit
during:
switching.

PRIMARY FACTORIAL

Held-out worlds:
20.

Contexts:
3.

Methods:

NO_COMP,
COMP6,
COMP3.

60:
context worlds

with:
method-specific
evaluation columns.

PRIMARY ACCEPTANCE SHAPE

H189 supports:
DORMANCY
CROSS-BRANCH
RESIDUAL DISTILLATION

if:

1.
Stored full phenotype:

median:
A,
B,
C
R^2 >=0.90.

2.
Stored joint competence:

>=90%
of worlds
have:
A,
B,
C
all:
R^2 >=0.85.

3.
COMP6
KNOWN-CONTEXT
prediction fidelity:

median normalized MSE
versus:
full

<=0.01

for:
A,
B,
C.

4.
COMP6
LEARNED-SCHEDULED
prediction fidelity:

median normalized MSE
<=0.02

for:
A,
B,
C.

5.
COMP6
known-context
task R^2:

median drop
from:
full

<=0.01

for:
A,
B,
C.

6.
COMP6
learned-scheduled
task R^2:

median drop
from:
full

<=0.02

for:
A,
B,
C.

7.
ROUTING:

median learned-route
accuracy
>=0.95.

8.
B-ONLY COMPUTE:

COMP6 learned-scheduled
<=2.5%
of:
full.

9.
C-ONLY COMPUTE:

<=2.5%.

10.
EQUAL A/B/C COMPUTE:

<=35%
of:
full.

11.
SLEEP-STATE MEMORY:

18 compensation parameters

add:
<=0.60%
to:
the H188
learned-state count.

12.
ZERO TASK-TARGET REPLAY:

distillation
uses:
only:
model predictions
and:
unlabeled context coordinates.

13.
WAKE LEARNING COST:

0.

14.
SWITCH DRIFT:

maximum normalized
prediction drift
across:
300 switches

<=1e-12.

15.
PHYSICAL STRUCTURE:

remains:
3257 cells.

16.
COMP3 diagnostic:

if:
COMP3
also passes:
all:
fidelity / task gates,

report:
three-parameter
sleep compensation
as:
sufficient.

STRONG SUPPORT

H189 receives:
STRONG support

if:

all COMP6 gates pass

AND:

COMP6
learned-scheduled
B and C
prediction fidelity

both:
<=0.01.

MIXED / NEGATIVE CONDITIONS

Treat H189 as:
mixed / negative
if:

- six quadratic parameters
  cannot:
  reconstruct:
  the cross-branch residual;

- compensation preserves:
  full predictions
  only by:
  materially degrading:
  task performance;

- sleep-state memory
  grows:
  into:
  a hidden duplicate
  of:
  dormant branch state;

- learned routing
  remains:
  the dominant source
  of:
  prediction mismatch;

- compensation
  must:
  be refit
  after:
  every wake cycle.

NEXT

If H189 succeeds:

proceed to:

CLR3-H190 —
FOURTH-CAPABILITY
ACCUMULATION UNDER:
HIBERNATION /
ROLE REUSE /
SLEEP COMPENSATION.

Primary North-Star question:

can:
stored capability count
increase:
from:
3
to:
4

while:

- physical active structure
  remains:
  near:
  H187 levels;
- single-context
  active compute
  remains:
  near:
  one-capability cost;
- dormant capabilities
  remain:
  exact / cheaply compensable?

SANITY WORLD SEEDS

20260923890000...

PRIMARY WORLD SEEDS

20260923800000
through:
20260923800019.

Sanity:
NON-EVIDENCE.

No:
parent phenotype,
distillation sample count,
feature map,
ridge,
routing rule,
compute accounting,
or:
acceptance gate

may change
after:
the first held-out H189 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_DORMANCY_CROSS_BRANCH_RESIDUAL_DISTILLATION

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
