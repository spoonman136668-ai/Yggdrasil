TITLE: DG-1A-CLR3-H188 — Capability Hibernation / Active-Compute Scaling Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / CAPABILITY HIBERNATION / ACTIVE-COMPUTE SCALING
BRANCH: dg1a-ar
PARENT: dg1a-clr3-h187-shared-basis-warp-capability-reliability-audit.ice

PURPOSE

H187 established:

- three learned capabilities A+B+C can reach:
  90% world-level joint competence;

- physical active structure can remain:
  the original 3209-cell parent body
  plus only:
  48 B daughter cells;

- capability B uses:
  those 48 daughter cells
  plus:
  a five-parameter shared basis warp;

- capability C can live as:
  48 context-gated role coefficients
  on:
  already-active parent cells;

- physical active-cell growth:
  approximately 1.50%
  for:
  a three-capability phenotype.

H188 asks the next North-Star question:

CAN:
ALL THREE CAPABILITIES
REMAIN STORED

WHILE:
ONLY THE CURRENTLY NEEDED
CAPABILITY SUBSTRATE

IS:
COMPUTATIONALLY ACTIVE?

This separates:

STORED CAPABILITY / MEMORY

from:

ACTIVE COMPUTE.

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT PHENOTYPE

Reuse:
the accepted H187
WARP48_ROLE48_C architecture.

A:

- original:
  3209 parent-cell
  learned coefficients;
- frozen;
- trained:
  to be:
  context-silent
  on:
  right-side future contexts.

B:

- 48 physical daughter cells;
- H181 coverage-balanced morphology;
- six-parameter learned B router;
- five-parameter shared B basis warp;
- frozen after training.

C:

- zero new physical C cells;
- 48 C-specific role coefficients
  stored on:
  selected active parent cells;
- six-parameter learned C router;
- frozen after training.

All:
A,
B,
C
parameters

remain:
stored
through:
all hibernation tests.

No:
retraining
occurs
inside:
H188.

FULL PHENOTYPE REFERENCE

For input x:

f_full(x)
=
f_A(x)
+
f_B(x)
+
f_C(x).

This is:
the accepted:
all-stored,
all-contributions
H187 phenotype.

BRANCH OUTPUTS

Define:

f_A_branch(x)
=
f_A(x).

f_B_branch(x)
=
f_B(x).

f_C_branch(x)
=
f_C(x).

These use:
the exact:
stored H187 coefficients,
routers,
and:
B warp.

No:
coefficient is:
refit.

KNOWN-CONTEXT SCHEDULED MODE

For:
A-context input:

evaluate:
A branch only.

For:
B-context input:

evaluate:
B branch only.

For:
C-context input:

evaluate:
C branch only.

This is:
an oracle:
context-label
compute ceiling.

It tests:

whether:
context-silence
and:
routing

have made:
the non-target branches
dispensable
at:
inference time.

LEARNED-ROUTER SCHEDULED MODE

For:
each input:

first evaluate:

B router
and:
C router.

Routing rule:

if:
B_gate >=0.5
AND:
B_gate >= C_gate:

activate:
B branch only.

Else if:
C_gate >=0.5:

activate:
C branch only.

Else:

activate:
A branch only.

Then:
evaluate:
ONLY:
the selected
functional branch.

A branch
has:
no additional learned router.

This uses:

12:
always-active
routing parameters

and:
no:
task-output label
at inference.

TWO-BRANCH MODES

Report:
the exact prediction
and:
compute cost
when:

A+B active,
C dormant.

A+C active,
B dormant.

B+C active,
A dormant.

For:
each context,
the active mode output
is:
the sum
of:
the declared active branches.

ALL-BRANCH MODE

A+B+C active:

identical:
to:
f_full.

HIBERNATION

Hibernating:
one capability

means:

its:
functional branch
is:
not evaluated.

Its:

- coefficients;
- warp parameters;
- router parameters;
- role state

remain:
stored
and:
unchanged.

No:
parameter deletion.

No:
state decay.

No:
retraining.

REACTIVATION

Reactivating:
one capability

means:

restore:
its evaluation branch

using:
the already stored
state.

No:
optimization.

No:
data access.

No:
warmup learning.

SWITCH SEQUENCE

For:
each world,

construct:
a deterministic
300-step
context-switch sequence:

A,
B,
C,
A,
B,
C,
...

100 complete:
A->B->C cycles.

At:
each switch:

evaluate:
32 held-out inputs
from:
the activated context

using:

1.
full phenotype reference;

2.
known-context scheduled branch;

3.
learned-router scheduled branch.

No:
model state
changes
between:
switches.

PRIMARY METRICS

STORED COMPETENCE

- full A held-out R^2;
- full B held-out R^2;
- full C held-out R^2;
- world-level joint competence.

SCHEDULED COMPETENCE

For:
known-context scheduled:

- A R^2;
- B R^2;
- C R^2.

For:
learned-router scheduled:

- A R^2;
- B R^2;
- C R^2;
- routing accuracy.

PREDICTION FIDELITY

Per context:

normalized MSE:

MSE(
scheduled_prediction,
full_prediction
)
/
Var(
full_prediction
).

Report:
known-context
and:
learned-router
values.

ACTIVE COMPUTE MODEL

Count:
basis-response
evaluations
plus:
small routing / warp
operations.

A branch:

3209:
parent basis responses.

B branch:

48:
daughter basis responses

+
5:
shared warp operations
proxy

+
6:
B router parameter operations.

C branch:

48:
parent-role basis responses

+
6:
C router operations.

Learned router scheduler:

12:
router parameter operations
are:
always active

before:
branch selection.

Do NOT:
count:
stored dormant coefficients
as:
active compute.

FULL ALL-BRANCH
per-sample compute proxy:

A
+
B
+
C
+
routers / warp.

KNOWN-CONTEXT
per-sample compute:

the selected:
branch only.

LEARNED-SCHEDULED
per-sample compute:

12 router ops
+
selected:
branch compute.

WORKLOADS

Report:
compute per sample
for:

1.
A-only workload.

2.
B-only.

3.
C-only.

4.
A/B:
50/50.

5.
A/C:
50/50.

6.
B/C:
50/50.

7.
A/B/C:
equal thirds.

For:
mixed workloads:

average:
the scheduled
per-context compute.

ACTIVE STATE

Report:

physical cells
whose basis functions
must be evaluated

per:
context.

A:

3209.

B:

48.

C:

48 reused-parent
role sites.

The physical:
3209 parent body
still exists

when:
A is dormant,

but:
its A-role basis evaluation
is:
not:
performed.

Thus:

ACTIVE COMPUTE
and:
PHYSICAL STORED STRUCTURE

are:
reported separately.

STORED MEMORY

Count:

- A coefficients;
- B daughter coefficients;
- C role coefficients;
- B warp parameters;
- B/C router parameters;
- structural coordinate / topology state
  as:
  a separate fixed-body cost.

Report:

functional learned-state
parameter count

separately
from:
fixed structural coordinates.

WAKE COST

Report:

parameter-state
reactivation count

and:
first-evaluation
compute proxy.

Because:
state is:
already stored,

wake learning cost:

must be:
ZERO.

WAKE PREDICTION RETURN

Across:
all:
100 switch cycles

and:
all activated-context
probe batches,

compare:
each activated branch

to:
its own:
first-cycle
prediction
on:
the same deterministic
probe index.

No:
drift
is allowed.

PRIMARY FACTORIAL

Held-out worlds:

20.

One:
stored H187 phenotype
per world.

Modes / workload analyses:

deterministic
within:
each world.

PRIMARY ACCEPTANCE SHAPE

H188 supports:
CAPABILITY HIBERNATION /
ACTIVE-COMPUTE SCALING

if:

1.
Stored full phenotype:

median:
A,
B,
C
held-out R^2
>=0.90.

2.
Stored world-level joint competence:

>=90%
of worlds
have:
A,
B,
C
all:
R^2 >=0.85.

3.
KNOWN-CONTEXT SCHEDULE:

median:
A,
B,
C
R^2

are:
each
no more than:
0.02
below:
the full phenotype
for:
the same capability.

4.
KNOWN-CONTEXT
prediction fidelity:

median normalized MSE
relative to:
full phenotype

<=0.02

for:
A,
B,
C.

5.
LEARNED-ROUTER SCHEDULE:

median:
routing accuracy
>=0.95.

6.
LEARNED-SCHEDULED:

median:
A,
B,
C
R^2

are:
each
no more than:
0.03
below:
full phenotype.

7.
LEARNED-SCHEDULED
prediction fidelity:

median normalized MSE
<=0.03

for:
A,
B,
C.

8.
B-ONLY COMPUTE:

learned-scheduled
median:
active compute

<=5%
of:
FULL ALL-BRANCH
per-sample compute.

9.
C-ONLY COMPUTE:

<=5%
of:
FULL.

10.
ABC EQUAL-MIX
COMPUTE:

learned-scheduled
median:
average active compute

<=40%
of:
FULL all-branch compute.

11.
HIBERNATION MEMORY:

dormant capability
parameters

remain:
stored
and:
bitwise / numerically unchanged

through:
the full:
300-switch sequence.

12.
WAKE LEARNING COST:

ZERO:

no:
gradient,
ridge fit,
router fit,
or:
parameter update

on:
reactivation.

13.
WAKE PREDICTION RETURN:

maximum normalized
reactivation drift

<=1e-12

across:
all:
switch cycles.

14.
TWO-BRANCH MODES:

hibernating:
the third capability

does NOT:
change:
the two active branches'
stored predictions

beyond:
floating-point tolerance

relative to:
their:
same branch sum.

15.
STORED MEMORY:

functional learned-state
parameter count

remains:
the H187 count;

hibernation
must NOT:
duplicate:
parameters.

16.
PHYSICAL STRUCTURE:

remains:
N + 48
physical cells.

No:
hibernation mode
adds:
physical cells.

STRONG SUPPORT

H188 receives:
STRONG support

if:

all primary gates pass

AND:

learned-scheduled
ABC equal-mix
active compute

<=35%
of:
FULL all-branch compute.

MIXED / NEGATIVE CONDITIONS

Treat H188 as:
mixed / negative
if:

- dropping:
  context-silent branches
  materially changes:
  capability outputs;

- learned routing
  chooses:
  the wrong branch
  too often;

- hibernated state
  needs:
  recomputation
  before:
  useful reactivation;

- stored memory
  secretly duplicates:
  active state;

- active compute
  remains:
  proportional
  to:
  all stored capabilities.

NEXT

If H188 succeeds:

proceed to:

CLR3-H189 —
FOURTH-CAPABILITY
ROLE / BASIS REUSE

under:
the accepted:
hibernation
and:
active-compute
architecture.

Primary North-Star question:

as:
stored capabilities
increase,

can:
active compute
remain:
near:
one-capability
cost

for:
single-context use?

SANITY WORLD SEEDS

20260923790000...

PRIMARY WORLD SEEDS

20260923700000
through:
20260923700019.

Sanity:
NON-EVIDENCE.

No:
parent phenotype,
routing rule,
branch definition,
compute accounting,
switch sequence,
threshold,
or:
acceptance gate

may change
after:
the first held-out H188 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_CAPABILITY_HIBERNATION_ACTIVE_COMPUTE_SCALING

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
