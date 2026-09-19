TITLE: DG-1A-AR-H99 — Hypothesis Speciation / Residual-Directed Model Mutation Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE RESIDUAL-DIRECTED THEORY-INHERITANCE RESULT + BROAD-MISMATCH SPECIATION LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh98-residual-driven-hypothesis-birth-audit.ice

PURPOSE
H98 creates:
a new tabular hypothesis
from scratch

when:
no retained model fits.

H99 asks a more developmental question:

SHOULD A NEW THEORY
DESCEND FROM
THE CLOSEST OLD THEORY?

Candidate rule:

preserve:
the parts that still predict well;

mutate:
only the dimensions
with:
persistent residual mismatch.

This creates:
hypothesis lineages.

BOUNDARY
This is synthetic.

It does not:
- infer arbitrary causal graphs;
- freeze eight model dimensions;
- freeze residual threshold 0.24;
- prove model inheritance is always preferable;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PARENT HYPOTHESIS
Eight Bernoulli consequence dimensions.

Parent vector:

[0.15,
 0.30,
 0.45,
 0.60,
 0.75,
 0.25,
 0.55,
 0.80].

Each dimension represents:
one local predictive / causal mechanism
in the toy.

TWO NOVEL DESCENDANTS

LOCALIZED CHANGE

Only two dimensions change:

dimension 1:
0.30 -> 0.75.

dimension 6:
0.55 -> 0.15.

The other six mechanisms remain:
exactly parent-like.

BROAD CHANGE

Five dimensions change:

0:
0.15 -> 0.70.

1:
0.30 -> 0.78.

3:
0.60 -> 0.18.

5:
0.25 -> 0.75.

6:
0.55 -> 0.10.

Thus:
the closest old theory is still informative

but:
much less so.

DIAGNOSTIC BUDGET
Primary:

96 total Bernoulli observations.

RESIDUAL SENTINEL
First:

5 observations
per dimension.

Total sentinel cost:
40.

A dimension is flagged:
locally mismatched

if:

absolute smoothed empirical difference
from parent
>
0.24.

Remaining observations:
56.

They are allocated:
only to flagged dimensions
under:
residual-directed mutation.

COMPARATORS

CLONE ONLY
Use:
the parent model unchanged.

FROM SCRATCH
Spread:
the full observation budget
across all eight dimensions.

RANDOM MUTATION
Use:
the same number of mutated dimensions
as:
the residual detector

but choose:
which dimensions to mutate
at random.

RESIDUAL-DIRECTED MUTATION
Keep:
parent values
for unflagged mechanisms.

Re-estimate:
flagged mechanisms.

BREADTH-GATED HYBRID
If:
residual mismatch spans
many dimensions,

stop pretending:
the change is local.

Use:
deeper / from-scratch speciation.

Primary diagnostic gate:
four or more flagged dimensions.

PRIMARY MONTE CARLO
20,000 matched synthetic offspring.

LOCALIZED CHANGE

mean flagged dimensions:
2.49.

true changed-dimension detection:

first changed dimension:
89.78%.

second:
83.45%.

unchanged false-flag rate:
12.67%.

PREDICTION MSE

CLONE ONLY:
0.04531.

FROM SCRATCH:
0.01264.

RANDOM MUTATION:
0.03343.

RESIDUAL-DIRECTED:
0.00836.

PRIMARY LOCAL-INHERITANCE POSITIVE
When:
most of the parent theory remains valid,

residual-directed inheritance
uses:
the old model as:
compressed prior structure.

Prediction error improves by:

approximately 33.9%
relative to:
from-scratch estimation

at:
the same total diagnostic budget.

Compared with:
random mutation,

error is:
approximately 75%
lower.

Thus:

MUTATION SHOULD FOLLOW
STRUCTURED RESIDUALS,

not:
random theory churn.

BROAD CHANGE

mean flagged dimensions:
4.83.

true changed-dimension detection:

approximately:
78%..97%
depending on dimension.

unchanged false-flag rate:
11.22%.

PREDICTION MSE

CLONE:
0.14522.

FROM SCRATCH:
0.01230.

RANDOM MUTATION:
0.06308.

RESIDUAL-DIRECTED:
0.01868.

PRIMARY BROAD-MISMATCH NEGATIVE
When:
most of the mechanism has changed,

local patching retains:
too much obsolete parent structure.

Residual-directed inheritance is:
still far better than:
random mutation

but:
worse than:
relearning the whole model.

Thus:

INHERITANCE
CAN BECOME:
ANCESTRAL BIAS.

BREADTH-GATED SPECIATION
Primary gate:

if:
4 or more dimensions
are flagged,

switch from:
local residual mutation

to:
deeper from-scratch re-estimation.

LOCALIZED CHANGE

hybrid MSE:
~0.00918.

FROM SCRATCH:
~0.01264.

RESIDUAL:
~0.00836.

The hybrid preserves:
most
of the local-inheritance gain.

BROAD CHANGE

hybrid:
~0.01484.

FROM SCRATCH:
~0.01230.

RESIDUAL:
~0.01868.

Thus:
the breadth gate recovers:
much of the broad-change loss

without:
abandoning inheritance
for:
small changes.

SAMPLE-BUDGET SWEEP
LOCALIZED CHANGE

BUDGET 48

from scratch:
~0.0212.

residual:
~0.0146.

BUDGET 64

0.0172
vs
0.0107.

BUDGET 80

0.0146
vs
0.0093.

BUDGET 96

0.0125
vs
0.0085.

BUDGET 128

0.0098
vs
0.0076.

PRIMARY SAMPLE-EFFICIENCY RESULT
Parent inheritance is most valuable when:

the change is sparse

and

evidence is expensive.

The old theory acts as:
compressed reusable causal structure.

BROAD CHANGE SAMPLE SWEEP
Across:
48..128 observations,

from-scratch learning remains:
better
than:
residual-only mutation.

Thus:
the failure is:
structural,

not:
just insufficient sampling.

PARENT RETENTION
Speciation creates:
a child hypothesis.

It does NOT:
overwrite
or
delete:
the parent.

Therefore:
if the old regime returns,

the parent can:
reactivate.

This preserves:
H97 dormant-regime value.

CURRENT THEORY-LINEAGE OBJECT
A hypothesis may now carry:

PARENT MODEL ID

+

INHERITED MECHANISMS

+

MUTATED RESIDUAL DIMENSIONS

+

MUTATION BREADTH

+

CURRENT FIT

+

SLOW RETENTION VALUE

+

CHILDREN / DESCENDANT REFERENCES.

This begins to make:
internal scientific theories
developmental objects.

RELATION TO H6
H6:
do not rewrite:
all inherited prior
for:
short local contradiction.

H99:
do not relearn:
an entire model

when:
only a small causal subset
changed.

Both rely on:

PRESERVE WHAT STILL FITS.

RELATION TO H36-H40
Generative memory:
shared basis
+
small lineage coordinates.

H99:
causal theory:
shared parent mechanisms
+
small residual mutation.

The same compression principle
appears again.

RELATION TO H98
H98:
persistent mismatch
can create:
a new theory.

H99:
new theory birth
need not mean:
blank slate.

Small change:

inherit.

Large change:

speciate.

GENERAL PRINCIPLE
MODEL EVOLUTION SHOULD ASK:

HOW MUCH
OF THE OLD EXPLANATION
STILL WORKS?

If:
most works

mutate:
the residual.

If:
little works

create:
a deeper branch.

Do not force:
every novelty
into:
either
complete cloning
or
complete restart.

DECISION
AR-H99 is POSITIVE WITH A BROAD-MISMATCH SPECIATION LIMIT.

Supported synthetically:

- residual-directed model mutation strongly improves sample efficiency under localized causal change;
- random mutation is inefficient;
- inherited unchanged structure acts as useful prior information;
- broad causal change makes parent inheritance harmful;
- residual breadth can indicate when to switch to deeper speciation;
- parent retention preserves regime recurrence value.

Not demonstrated:

- causal-graph mutation;
- latent-variable birth;
- structural mechanism reuse;
- model mating / recombination;
- online mutation breadth estimation under correlated noise;
- distributed theory lineage.

NEXT HIGH-VALUE MOVE
AR-H100 — HYPOTHESIS RECOMBINATION / MOSAIC CAUSAL MODEL ASSEMBLY

H99 assumes:
one closest parent.

But:
a genuinely new regime may combine:

mechanism A
from:
old theory 1

and

mechanism B
from:
old theory 2.

Question:

CAN A NEW THEORY
BE ASSEMBLED
FROM
MULTIPLE OLD PARENTS?

Candidate setup:

existing hypotheses
each explain:
different mechanism subsets.

New regime is:
a mosaic combination
never previously observed
as one model.

Compare:

A.
from-scratch model birth;

B.
nearest-parent mutation;

C.
per-dimension best-parent recombination;

D.
recombination + residual validation;

E.
parents with correlated errors;

F.
one malicious / stale parent.

Desired:

KNOWN MECHANISMS
IN
NEW COMBINATION

->
fast theory assembly.

UNKNOWN MECHANISM

->
residual mutation
only for:
the genuinely new part.

This would make:
internal science
compositional
at:
the model level.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
model_dimensions = 8
primary_budget = 96
localized_residual_mse = 0.00836
localized_from_scratch_mse = 0.01264
broad_residual_mse = 0.01868
broad_from_scratch_mse = 0.01230
