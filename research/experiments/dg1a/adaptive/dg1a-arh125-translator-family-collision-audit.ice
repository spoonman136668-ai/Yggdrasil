TITLE: DG-1A-AR-H125 — Translator-Family False Sharing / Interface Grammar Collision Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE FAMILY-SPLIT + RESIDUAL RESULT + RARE-SEMANTIC COLLISION LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh124-interface-ecology-memory-audit.ice

PURPOSE
H124 compresses:
many direct interface bridges

into:
shared translator families
plus:
exact residuals.

H125 attacks:
the family-sharing assumption.

Question:

WHAT IF
TWO INTERFACES
LOOK IDENTICAL
ON:
COMMON TRAFFIC

but:
differ
in:
a rare semantic edge case?

A shared family translator
can then:
introduce:
common-mode translation error.

BOUNDARY
This is synthetic.

It does not:
- freeze family size;
- freeze six semantic contexts;
- prove rare canaries are sufficient;
- freeze residual/split rules;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

INTERFACE POPULATION
96 bridges.

Four true translator families.

Six semantic contexts
per bridge.

Five:
ordinary / common contexts.

One:
rare edge context.

COMMON FAMILY STRUCTURE
Most members of one family
share:
very similar translation behavior.

Family ordinary-context success:
approximately 0.78..0.96.

Rare-context family behavior:
approximately 0.82..0.95.

SEMANTIC COLLISION BRIDGES
Approximately:
14%
of bridges

look:
family-consistent
across:
all five common contexts

but:
their rare-context semantics
differ strongly.

Rare-context success:
approximately 0.12..0.35.

Thus:
ordinary traffic
cannot:
separate them
from:
their family.

PRIMARY TRAINING
25 observations
per:
common context.

No rare edge evidence
during:
initial family assignment.

This intentionally makes:
family sharing look:
safe.

COMPARATORS

FLAT EXACT BRIDGE
Store:
all six context parameters
per bridge.

Also receives:
20 direct rare-context observations.

NAIVE FAMILY SHARING
Store:
one six-context translator
per family.

No per-bridge residual.

FAMILY + PER-BRIDGE RESIDUAL
Use:
shared family structure

plus:
one rare-context residual parameter
for:
confirmed family violators.

FAMILY SPLIT
Persistent confirmed violators
within:
the same family

can form:
a semantic subfamily
sharing:
their alternate rare-context behavior.

PRIMARY RARE CANARY
First:
6 rare-context observations
per bridge.

Nominate mismatch if:

absolute rare-context deviation
from:
family prediction
>
0.25.

SECOND VALIDATION
8 independent rare-context observations.

Confirm only if:

absolute deviation
>
0.20

again.

Thus:
family violation requires:
persistent independent evidence.

PRIMARY CONFIRMATION
1,200 synthetic interface ecologies.

COLLISION PREVALENCE
mean:
13.96%.

CONFIRMED COLLISION DETECTION

true-positive rate:
95.24%.

false-confirmation rate
among ordinary family members:
0.318%.

PRIMARY RARE-CANARY POSITIVE
A bridge can:
look perfectly family-like
under:
ordinary traffic

while:
remaining:
semantically different
in:
one rare context.

Targeted rare canaries
recover:
that hidden mismatch.

OVERALL WEIGHTED PREDICTION MSE
Context weights:

five common contexts:
0.19 each.

rare context:
0.05.

FLAT EXACT

0.004438.

NAIVE FAMILY

0.003382.

FAMILY + RESIDUAL

0.000640.

FAMILY SPLIT

0.000644.

PRIMARY SHARING INTERPRETATION
Naive family sharing
can appear:
very good
on:
aggregate ordinary traffic

because:
shared estimation
denoises:
common contexts.

That aggregate score hides:
the rare semantic failure.

RARE-CONTEXT MSE

FLAT EXACT:
0.005515.

NAIVE FAMILY:
0.060073.

FAMILY + RESIDUAL:
0.005242.

FAMILY SPLIT:
0.005330.

PRIMARY RARE-EDGE NEGATIVE
Naive family compression increases:
rare-context error
by:
roughly an order of magnitude.

Thus:

GOOD AVERAGE FAMILY FIT
DOES NOT PROVE:
RARE SEMANTIC EQUIVALENCE.

PER-BRIDGE RESIDUAL POSITIVE
Once:
rare mismatch
is confirmed,

store:
only:
the semantic difference
that violates:
the family model.

This restores:
rare-context accuracy

without:
discarding:
the shared translator.

STORAGE
Synthetic scalar-equivalent state.

FLAT EXACT:
576.

NAIVE FAMILY:
24.

FAMILY + RESIDUAL:
37.02.

FAMILY SPLIT:
29.37.

PRIMARY SUBFAMILY POSITIVE
Persistent repeated exceptions
can:
share:
their own residual structure.

A semantic subfamily
achieves:
nearly the same prediction quality
as:
per-bridge residuals

with:
less permanent state.

Mean:
3.42
new semantic subfamilies
per:
four-family ecology.

SINGLETON DISCIPLINE
If:
only one bridge
violates:
family semantics,

it remains:
an individual residual.

Do not create:
a new subfamily
for:
one anomaly.

This prevents:
family-count explosion.

COMMON-TRAFFIC BLIND SPOT
The collision bridge
is deliberately:
indistinguishable
from:
ordinary family members
on:
the common contexts.

Therefore:
more ordinary observations
do not solve:
the edge-case failure.

The missing evidence
must:
actually exercise:
the semantic distinction.

This repeats:
H83-H84.

MODEL-FIT AUTHORITY
Family membership
should carry:

COMMON-CONTEXT FIT

+

RARE / CHALLENGE SUPPORT

+

CURRENT CONTEXT FIT

+

RESIDUAL STATE

+

SUBFAMILY CANDIDACY.

Family identity
is:
a compression hypothesis,

not:
an ontology.

RELATION TO H36-H38
Shared lineage-family memory
can be:
poisoned
when:
outliers
are forced into:
one basis.

H125:
shared translator families
have:
the same failure.

The remedy is again:

FIT GATING

+

RESIDUAL STATE

+

SPLIT
when:
persistent coherent mismatch
appears.

RELATION TO H83
Functional equivalence
is:
context-bounded.

H125:
translator-family equivalence
is also:
context-bounded.

Common-case equivalence
does not guarantee:
rare-interface equivalence.

RELATION TO H124
H124:
shared translator grammar
reduces:
interface-memory cost.

H125:
that compression remains safe
only while:
member-specific residuals
and:
family splits
are allowed.

GENERAL PRINCIPLE
SHARE:
WHAT ACTUALLY GENERALIZES.

WHEN:
ONE MEMBER
REPEATEDLY VIOLATES
SHARED SEMANTICS,

DO NOT:
FORCE THE FAMILY.

STORE:
THE RESIDUAL

or:
SPLIT
THE FAMILY.

DECISION
AR-H125 is POSITIVE
for:
FIT-GATED TRANSLATOR FAMILIES
WITH:
RESIDUAL / SUBFAMILY ESCAPE

AND A HARD:
RARE-SEMANTIC COLLISION LIMIT.

Supported synthetically:

- common traffic can hide rare semantic incompatibility;
- naive family sharing has large rare-context error;
- two-stage rare challenge detects most true collisions with low false confirmation;
- per-bridge residuals recover edge-case accuracy cheaply;
- coherent persistent violators can form a lower-cost semantic subfamily;
- family identity should remain confidence-bounded and splittable.

Not demonstrated:

- learned rare-canary generation;
- stateful semantic protocols;
- multiple rare edge dimensions;
- family merge after convergence;
- malicious interface members;
- online subfamily retirement.

NEXT HIGH-VALUE MOVE
AR-H126 — SHARED TRANSLATOR UPDATE POISONING / VERSIONED INTERFACE FAMILY AUDIT

H125 protects:
member assignment.

But:
a shared translator family
may itself:
be updated
from:
new bridge traffic.

Question:

CAN ONE OR A FEW
BAD MEMBERS
POISON:
THE SHARED TRANSLATOR?

Compare:

A.
naive family update;

B.
member-fit-weighted update;

C.
quarantine outliers;

D.
shadow family candidate
+
independent interface canaries;

E.
legitimate population-wide semantic shift;

F.
slow in-family poison
that remains:
inside ordinary fit.

Desired:

SHARED INTERFACE STATE
should have:
LOWER WRITE AUTHORITY
than:
one member's provisional state.

This directly mirrors:
H38-H40
for:
generative family memory.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
interface_ecologies = 1200
bridges = 96
family_count = 4
collision_fraction = 0.13957
collision_tpr = 0.95235
ordinary_fpr = 0.00318
family_residual_storage = 37.02417
family_split_storage = 29.37279
