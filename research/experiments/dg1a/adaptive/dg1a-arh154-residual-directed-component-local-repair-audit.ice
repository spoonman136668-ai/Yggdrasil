TITLE: DG-1A-AR-H154 — Residual-Directed Component-Local Functional Repair Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh153-active-local-functional-probing-audit.ice

PURPOSE

H153 established:

posterior geometric uncertainty
improves:
query allocation modestly,

but:
does NOT close
world-level T90 reliability

and:
does NOT remove
FOUR-PATCH functional interference.

H153 also showed:

24 active observations
are already within:
0.03 median final recovery
of:
48 observations

for:
MIXED 1%..5%.

Therefore:

the main missing variable
is not:
more total feedback.

H154 asks:

CAN
FUNCTIONAL REPAIR
BE ROUTED
BY:
THE ACTUAL OBSERVED
RESIDUAL ERROR
OF:
EACH WOUND COMPONENT?

CORE IDEA

For multi-wound damage:

treat each initial wound component
as:
an independently repairable
functional block.

Each component receives:

- its own local feedback-query pool;
- its own training observations;
- its own held-out local validation observations;
- its own local ridge solve;
- its own stop/reopen state.

Only:
the selected component's
regenerated coefficients
may change
during:
that component solve.

Surviving original coefficients
and:
other wound-component estimates
remain fixed.

This tests:

whether:
functional micro-patching
should be:
COMPONENT-LOCAL
and:
RESIDUAL-DIRECTED

rather than:
one global lesion solve.

BOUNDARY

Synthetic research only.

No:
production model repair,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or runtime activation.

PARENT MODEL

Reuse H152/H153 colony mechanics:

R=8.
N=197.
sigma=0.22.
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

COMPONENT FEEDBACK POOL

For each:
initial Moore-connected lesion component,

generate:
32 local candidate queries.

Query generation:

- choose one member
  from:
  that component;
- use:
  its normalized response center;
- add:
  Gaussian jitter
  sd=0.12;
- reject:
  outside unit disk.

Each component pool
has:
its own deterministic RNG domain.

Targets:

pre-lesion function
at:
the queried local point.

Target becomes:
available only when:
the query is acquired.

TRAIN / VALIDATION SPLIT

Within:
each component pool,

acquired query indices
alternate:

even index:
TRAIN.

odd index:
VALIDATION.

Validation targets
are:
never used
to fit:
that component's coefficients.

They are used only for:

- residual estimation;
- stop;
- reopen;
- routing priority.

COMPONENT-LOCAL SOLVE

For selected component c:

hold fixed:

- all surviving original cells;
- all regenerated coefficients
  outside c.

Solve only:
coefficients inside c.

Objective:

||Phi_c w_c - residual_target||^2
+
0.10 ||w_c - context_prior_c||^2.

No:
lost original coefficient
is read.

RESIDUAL RATIO

For acquired validation queries
of:
component c:

R_c =
current validation MSE
/
lesioned-baseline validation MSE.

R_c = 0:
full correction
on:
that local validation set.

R_c = 1:
no improvement
over:
the lesioned baseline.

STOP

A component is:
locally validated recovered

when:

- at least two validation observations exist;
- R_c <=0.10
  for:
  two consecutive maturation steps.

REOPEN

A stopped component
reopens
when:

R_c >0.15.

The 0.10 stop threshold
matches:
the functional T90 concept.

The 0.15 reopen threshold
provides:
fixed hysteresis.

These values are:
frozen before:
sanity and primary.

RESIDUAL-DIRECTED ROUTING

Bootstrap priority:

1.
components with:
no training observation;

2.
components with:
no validation observation.

After bootstrap:

route next feedback
to:
the unstopped component
with:
largest R_c.

No hidden target
from:
an unacquired query
may influence routing.

FUNCTIONAL POLICIES

A — CONTEXT0

H151 context-harmonic parent.

No:
functional feedback.

B — H152-FIXED-FB2

Frozen H152 comparator.

Global lesion solve.

2 generated-order observations / step.

Maximum:
24.

C — COMP-FIXED2

Component-local solves.

2 observations / step.

Maximum:
24.

Round-robin component routing.

No:
residual adaptation.

D — COMP-ADAPT2

PRIMARY CANDIDATE.

Component-local solves.

2 observations / step.

Maximum:
24.

Residual-directed routing.

Per-component:
stop / reopen.

E — COMP-ADAPT4

Same:
residual-directed mechanism.

4 observations / step.

Maximum:
48.

Budget-ceiling comparator.

F — CHECKPOINT-ORACLE

Exact lost-state restore.

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

1. final functional recovery;
2. T50/T90/T99;
3. T90 world fraction;
4. functional downtime;
5. feedback observations;
6. feedback observations / missing coefficient;
7. number of lesion components;
8. validated-recovered component count;
9. component reopen count;
10. routing entropy;
11. median component stop step;
12. max final component residual ratio;
13. compact / four-patch interaction;
14. COMP-ADAPT2 versus H152-FIXED-FB2;
15. COMP-ADAPT2 versus COMP-FIXED2;
16. COMP-ADAPT2 versus COMP-ADAPT4;
17. oracle gap.

PRIMARY ACCEPTANCE SHAPE

H154 supports:
RESIDUAL-DIRECTED COMPONENT-LOCAL REPAIR

if:

1.
MIXED 1%..5%,
COMP-ADAPT2
median final recovery >=0.93.

2.
MIXED 1%..5%,
COMP-ADAPT2
T90 world fraction >=0.85
for all three damage fractions

and:
>=0.90
for at least two of three.

3.
Relative to:
H152-FIXED-FB2,

COMP-ADAPT2
improves:
T90 world fraction
by:
>=10 percentage points

in:
at least two of:
MIXED 1%,2%,5%.

4.
For:
MIXED 1%..5%,

FOUR-PATCH
median T90
is:
no more than 20%
worse than:
COMPACT

and:
FOUR-PATCH T90-world fraction
is:
within 10 percentage points
of:
COMPACT

in:
at least two of three
damage fractions.

5.
COMP-ADAPT2
uses:
<=18
median feedback observations
for:
MIXED 1%..5%

in:
at least two of three
damage fractions.

6.
COMP-ADAPT2
is within:
0.03
median final recovery
of:
COMP-ADAPT4

for:
at least two of:
MIXED 1%,2%,5%.

7.
Residual-directed routing
beats:
COMP-FIXED2

on:
FOUR-PATCH T90-world fraction
by:
>=10 percentage points

in:
at least two of:
MIXED 1%,2%,5%.

8.
SMOOTH 1%..5%
median final recovery
remains:
>=0.95.

9.
CHECKPOINT-ORACLE
remains:
the ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H154 as:
mixed / negative
if:

- component-local solves
  do not improve:
  multi-wound reliability;
- residual routing
  does not beat:
  fixed component routing;
- component validation
  stops too early
  and:
  harms held-out recovery;
- stopped components
  repeatedly reopen;
- 24 observations
  still behave:
  materially worse
  than:
  48;
- feedback cost remains:
  near the full 24
  for almost every small lesion;
- local validation residual
  does not predict:
  held-out functional recovery.

SANITY

Disjoint sanity family:

20260920190000...

Declared cells:

MIXED 1% COMPACT;
MIXED 1% FOUR;
MIXED 2% FOUR;
MIXED 5% COMPACT;
MIXED 5% FOUR;
SMOOTH 2% FOUR;
SCRAMBLED 5% FOUR.

20 worlds / cell.

Sanity:
NON-EVIDENCE.

No:
threshold,
budget,
or:
acceptance gate
may change
from:
sanity outcomes.

PRIMARY SEEDS

20260920100000
through:
20260920102399.

No execution-semantic change
after:
the first held-out H154 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_RESIDUAL_DIRECTED_COMPONENT_LOCAL_MICROPATCH

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false
