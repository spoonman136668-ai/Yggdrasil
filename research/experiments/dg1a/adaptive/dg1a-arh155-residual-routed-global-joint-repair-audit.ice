TITLE: DG-1A-AR-H155 — Residual-Routed Global Joint Functional Micro-Patch Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh154-residual-directed-component-local-repair-audit.ice

PURPOSE

H154 established:

FUNCTIONAL ERROR
CAN BE:
LOCALLY OBSERVED

without:
being:
PARAMETER-SEPARABLE
BY WOUND.

Independent component solves:
underperformed
the H152 global lesion solve.

H155 therefore keeps:

LOCAL QUERY ROUTING

but restores:

ONE GLOBAL JOINT SOLVE
OVER:
ALL REGENERATED LESION COEFFICIENTS.

Question:

CAN
OBSERVED PER-WOUND
FUNCTIONAL RESIDUAL

DECIDE:
WHERE TO SPEND
THE NEXT LOCAL FEEDBACK QUERY

while:

JOINT INFERENCE
preserves:
cross-wound coupling?

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
H152/H153/H154.

R=8.
N=197.
sigma=0.22.
repair p=0.50.
ridge lambda=0.10.
12 post-membership maturation steps.

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

COMPONENT FEEDBACK POOLS

Each initial Moore-connected wound component
receives:
32 deterministic
local candidate queries.

Jitter:
0.12 body-radius units.

Candidate query targets
are hidden
until:
that query is selected.

ALL ACQUIRED QUERIES
ARE TRAINING DATA.

H155 does NOT:
reserve half the feedback budget
for:
validation.

This is:
a deliberate correction
to:
H154's information inefficiency.

GLOBAL JOINT SOLVE

After:
each acquired feedback query,

solve:

all lesion coefficients
jointly.

Objective:

||Phi_R w_R - residual_target||^2
+
0.10 ||w_R - w_prior||^2.

Surviving original coefficients:
remain fixed.

No:
lost coefficient
is read.

No:
held-out evaluation target
is read.

WITHIN-COMPONENT QUERY CHOICE

For the selected wound component:

choose:
the unqueried candidate
with:
maximum posterior leverage

u_j =
phi_j,R^T
(Phi_R^T Phi_R + 0.10 I)^-1
phi_j,R.

Thus:

component routing uses:
functional residual
or:
uncertainty comparator,

while:
query location inside the component
uses:
geometric information value.

OBSERVED PREFIT RESIDUAL

When query j
is selected:

before:
including its target
in:
the fit,

compute:

e_j =
(y_j - yhat_j)^2.

Compute:
the lesioned-baseline error
for:
the same query:

b_j =
(y_j - y_lesion_j)^2.

Normalized innovation:

z_j =
e_j
/
(b_j + 1e-12).

Clip:
z_j
to:
[0,10].

Each component maintains:

s_c =
EWMA
of:
its acquired z_j

with:
alpha = 0.50.

This score uses only:
already-acquired feedback.

No:
unacquired target
enters:
routing.

BOOTSTRAP

Before:
residual routing,

every wound component
must receive:
at least one acquired query

when:
budget allows.

After bootstrap:

route:
the next query

to:
the component
with:
largest s_c

that still has:
unqueried candidates.

UNCERTAINTY ROUTING COMPARATOR

Component uncertainty score:

mean posterior coefficient variance
over:
lesion coefficients
inside:
that component.

Route:
the next query
to:
largest uncertainty score.

This provides:
a same-pool,
same-global-solve
comparison
against:
residual routing.

FUNCTIONAL POLICIES

A — CONTEXT0

No functional feedback.

B — H152-FIXED-FB2

Frozen H152 comparator.

Generated-order shared local pool.

Global solve.

24 observations.

C — JOINT-FIXED24

Component pools.

Round-robin component routing.

Within component:
maximum leverage query.

Global joint solve.

24 observations.

D — JOINT-UNCERT24

Component pools.

Posterior-uncertainty component routing.

Within component:
maximum leverage.

Global joint solve.

24 observations.

E — JOINT-RESID24

PRIMARY CANDIDATE.

Component pools.

Observed residual component routing.

Within component:
maximum leverage.

Global joint solve.

24 observations.

F — JOINT-RESID48

Same:
residual routing.

48-observation ceiling comparator.

G — CHECKPOINT-ORACLE

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

7 policies.

16,800 policy-world evaluations.

PRIMARY METRICS

1. final functional recovery;
2. T50/T90/T99;
3. T90 world fraction;
4. functional downtime;
5. feedback observations;
6. observations / missing coefficient;
7. residual-routing score trajectory;
8. routing entropy across wound components;
9. query count per component;
10. compact/four interaction;
11. JOINT-RESID24 versus H152-FIXED;
12. JOINT-RESID24 versus JOINT-FIXED24;
13. JOINT-RESID24 versus JOINT-UNCERT24;
14. JOINT-RESID24 versus JOINT-RESID48;
15. lesion-weight RMSE, analysis only;
16. oracle gap.

PRIMARY ACCEPTANCE SHAPE

H155 supports:
RESIDUAL-ROUTED GLOBAL JOINT REPAIR

if:

1.
MIXED 1%..5%,
JOINT-RESID24
median final recovery >=0.94.

2.
MIXED 1%..5%,
JOINT-RESID24
T90 world fraction >=0.85
for all three damage fractions

and:
>=0.90
for at least two of three.

3.
Relative to:
H152-FIXED-FB2,

JOINT-RESID24
improves:
T90 world fraction
by:
>=10 percentage points

in:
at least two of:
MIXED 1%,2%,5%.

4.
Relative to:
JOINT-FIXED24,

JOINT-RESID24
improves:
FOUR-PATCH
T90 world fraction
by:
>=10 percentage points

in:
at least two of:
MIXED 1%,2%,5%.

5.
For:
MIXED 1%..5%,

FOUR-PATCH
median functional T90
is:
no more than 20%
worse than:
COMPACT

in:
at least two of three
damage fractions.

6.
JOINT-RESID24
is within:
0.03
median final recovery
of:
JOINT-RESID48

for:
at least two of:
MIXED 1%,2%,5%.

7.
JOINT-RESID24
matches or exceeds:
JOINT-UNCERT24
T90 world fraction

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

Treat H155 as:
mixed / negative
if:

- residual routing
  does not beat:
  fixed routing;
- residual routing
  does not beat:
  uncertainty routing;
- multi-wound T90 interference
  remains;
- only 48 observations
  provide reliable recovery;
- global joint solve
  becomes unstable
  under residual-prioritized sampling;
- residual score
  repeatedly starves:
  one wound component;
- surviving original coefficients
  must change.

SANITY

Disjoint sanity family:

20260920290000...

20 worlds / cell:

MIXED 1% COMPACT;
MIXED 1% FOUR;
MIXED 2% FOUR;
MIXED 5% COMPACT;
MIXED 5% FOUR;
SMOOTH 2% FOUR;
SCRAMBLED 5% FOUR.

Sanity:
NON-EVIDENCE.

No:
threshold,
budget,
routing alpha,
or:
acceptance gate
may change
from:
sanity outcomes.

PRIMARY SEEDS

20260920200000
through:
20260920202399.

No execution-semantic change
after:
the first held-out H155 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_RESIDUAL_ROUTED_GLOBAL_JOINT_MICROPATCH

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false
