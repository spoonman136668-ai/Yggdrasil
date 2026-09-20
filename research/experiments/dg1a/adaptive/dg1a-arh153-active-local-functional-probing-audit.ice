TITLE: DG-1A-AR-H153 — Active Local Functional Probing / Uncertainty-Bounded Micro-Patch Feedback Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh152-context-functional-feedback-micropatch-audit.ice

PURPOSE

H152 established:

LOCAL DEVELOPMENTAL PRIOR
+
BOUNDED LOCAL FUNCTIONAL FEEDBACK

can:
raise MIXED
1%..5%
median functional recovery

above:
0.90

without:
restoring lost mutable coefficients.

H152 also failed:

- world-level T90 reliability;
- 24-observation efficiency versus 48 observations;
- FOUR-PATCH functional-feedback non-interference.

The next question is:

CAN
THE SAME LOCAL FEEDBACK BUDGET
BE SPENT
MORE INTELLIGENTLY?

H153 tests:

ACTIVE LOCAL PROBING

where:
the controller chooses
which local functional query
to request next

from:
an already-local candidate pool

using only:
known basis geometry
and:
posterior uncertainty.

It does NOT use:

- lost original coefficients;
- held-out evaluation targets;
- latent repair labels;
- global retraining.

BOUNDARY

Synthetic research only.

No:
production model repair,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or runtime activation.

PARENT MODEL

Reuse H152 exactly:

- R=8 lattice disk;
- N=197;
- sigma=0.22 RBF readout;
- SMOOTH / MIXED / SCRAMBLED state classes;
- 1%,2%,5%,10% damage;
- COMPACT / FOUR-PATCH lesion geometry;
- H150/H151 membership regeneration;
- repair p=0.50;
- 12 post-membership maturation steps;
- ridge lambda=0.10;
- 64 local candidate feedback queries;
- 256 disjoint held-out evaluation queries.

ACTIVE QUERY RULE

For lesion-cell coefficient vector w_R,
let selected feedback design matrix be P.

Posterior geometry proxy:

A =
P^T P
+
lambda I.

For each unqueried candidate feedback row p_j:

u_j =
p_j^T A^-1 p_j.

Select:
the candidate with maximum u_j.

IMPORTANT:

query selection may read:
candidate query coordinates,
basis responses,
lesion geometry,
and previously selected query identities.

It may NOT read:
the target output of an unselected query.

The target:
becomes available only after:
the query is selected.

COMPONENT-BALANCED ACTIVE QUERY

Map each lesion member
to:
its initial Moore-connected wound component.

Each candidate feedback query
inherits:
the component of
the lesion member
around which it was generated.

For:
multi-component lesions,

allocate successive query slots:
round-robin across components
that still have:
unselected candidate queries.

Inside:
the selected component,

choose:
maximum posterior uncertainty u_j.

This tests:

whether:
explicit information allocation
across wounds

removes:
the H152 FOUR-PATCH interference.

FUNCTIONAL POLICIES

A — RANDOM24

Frozen H152-style:
2 local feedback observations / maturation step.

Maximum:
24.

Candidate queries consumed:
in deterministic generated order.

B — ACTIVE24

Context prior.

2 observations / step.

Maximum:
24.

Global:
maximum posterior-uncertainty selection.

C — COMPONENT24

Context prior.

2 observations / step.

Maximum:
24.

Component-balanced uncertainty selection.

D — COMPONENT-STOP24

Same as:
COMPONENT24

but:
may stop acquiring feedback early
from:
a frozen posterior-uncertainty rule
selected only on:
disjoint sanity seeds.

Maximum:
24.

No held-out functional metric
may drive:
stopping.

E — COMPONENT48

Context prior.

4 observations / step.

Maximum:
48.

Component-balanced uncertainty selection.

Budget-ceiling comparator.

F — FBONLY-ACTIVE24

No developmental context prior.

Zero prior.

2 observations / step.

Maximum:
24.

Uses:
the same active uncertainty rule.

Isolates:
developmental-prior value.

G — CHECKPOINT-ORACLE

Exact lost coefficient restore.

Evaluation ceiling only.

EARLY-STOP SANITY SELECTION

Candidate normalized uncertainty thresholds:

0.50,
0.25,
0.10.

Let:

rho =
max candidate posterior uncertainty
/
initial max candidate uncertainty.

Minimum observations before stopping:
4.

Using only:
disjoint sanity worlds,

choose:
the LARGEST threshold

that keeps:
COMPONENT-STOP24

within:
0.03
median final functional recovery
of:
COMPONENT24

on every declared MIXED sanity cell.

If:
no candidate qualifies,

use:
0.10.

Freeze:
the chosen threshold
before:
held-out primary execution.

PRIMARY FACTORIAL

Context:
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

100 underlying worlds / cell.

2,400 underlying worlds.

7 policies.

16,800 policy-world evaluations.

COMMON-WORLD DISCIPLINE

All policies in one world share:

- colony;
- coefficient field;
- lesion;
- membership schedule;
- candidate feedback pool;
- feedback targets;
- evaluation queries.

Only:
query allocation,
feedback budget,
prior,
or oracle access
differs.

PRIMARY METRICS

1. final functional recovery;
2. functional T50/T90/T99;
3. T90 world fraction;
4. functional downtime;
5. feedback observations consumed;
6. feedback observations per missing coefficient;
7. held-out MSE ratio;
8. lesion-weight RMSE, analysis only;
9. context value versus FBONLY-ACTIVE24;
10. active value versus RANDOM24;
11. component-balance value versus ACTIVE24;
12. COMPONENT24 versus COMPONENT48 gap;
13. early-stop savings;
14. FOUR-PATCH T90 interaction;
15. oracle gap;
16. posterior uncertainty trajectory.

PRIMARY ACCEPTANCE SHAPE

H153 supports:
ACTIVE LOCAL FUNCTIONAL PROBING

if:

1.
MIXED 1%..5%,
COMPONENT24 median final recovery >=0.92.

2.
MIXED 1%..5%,
COMPONENT24 T90 world fraction >=0.85
for all three damage fractions

and:
>=0.90
for at least two of three.

3.
Relative to RANDOM24,
COMPONENT24 improves:
T90 world fraction
by:
>=10 percentage points

in at least:
two of:
MIXED 1%,2%,5%.

4.
FOUR-PATCH
does not incur:
>20%
median functional-T90 penalty
versus:
COMPACT

for:
MIXED 1%..5%.

5.
COMPONENT24
is within:
0.03
median final recovery
of:
COMPONENT48

for:
at least two of:
MIXED 1%,2%,5%.

6.
COMPONENT-STOP24
uses:
<=16
median feedback observations

while remaining:
within 0.03
median final recovery
and:
within 10 percentage points
T90-world fraction
of:
COMPONENT24

for:
at least two of:
MIXED 1%,2%,5%.

7.
For:
SMOOTH and MIXED
1%..5%,

COMPONENT24
beats:
FBONLY-ACTIVE24
by:
>=0.05
median final recovery

in:
at least four of six groups.

8.
CHECKPOINT-ORACLE
remains:
the ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H153 as:
mixed / negative
if:

- active selection does not improve reliability;
- component balancing does not improve FOUR-PATCH behavior;
- early stopping saves little or causes material recovery loss;
- only 48 observations produce reliable recovery;
- active feedback without context matches context+active feedback;
- query selection needs hidden target values;
- surviving original coefficients must change.

SANITY CELLS

Disjoint sanity family:

20260920090000...

20 worlds each:

MIXED 1% COMPACT;
MIXED 1% FOUR;
MIXED 2% FOUR;
MIXED 5% COMPACT;
MIXED 5% FOUR;
SMOOTH 5% FOUR;
SCRAMBLED 5% COMPACT.

Sanity outputs:
NON-EVIDENCE.

PRIMARY SEEDS

20260920000000
through:
20260920002399.

No primary threshold
or policy parameter
may change
after:
the first held-out H153 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_ACTIVE_LOCAL_FUNCTIONAL_PROBING

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false
