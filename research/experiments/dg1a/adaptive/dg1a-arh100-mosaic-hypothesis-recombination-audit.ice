TITLE: DG-1A-AR-H100 — Mosaic Hypothesis Recombination / Multi-Parent Causal Assembly Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE MULTI-PARENT THEORY-ASSEMBLY RESULT + MODULE-IDENTIFIABILITY LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh99-hypothesis-speciation-audit.ice

PURPOSE
H99 assumes:
one closest parent theory.

H100 tests a stronger developmental idea:

A NEW CAUSAL REGIME
MAY BE
A MOSAIC
OF MECHANISMS
THAT ALREADY EXIST
IN DIFFERENT OLD THEORIES.

Question:

Can a newborn hypothesis
reuse:
mechanism fragments
from multiple parents

and learn only:
the genuinely novel residual?

BOUNDARY
This is synthetic.

It does not:
- infer arbitrary causal graph modules;
- freeze eight mechanism dimensions;
- prove mechanism independence;
- freeze confidence thresholds;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PRIMARY DISTINCT PARENTS
Two existing parent hypotheses.

PARENT A:

[0.10,
 0.20,
 0.30,
 0.40,
 0.80,
 0.75,
 0.70,
 0.65].

PARENT B:

[0.85,
 0.75,
 0.70,
 0.65,
 0.20,
 0.25,
 0.30,
 0.35].

NEW MOSAIC REGIME
Seven of eight mechanisms
are copied exactly
from:
A
or
B.

One mechanism is:
genuinely new.

Target:

[A0,
 B1,
 A2,
 B3,
 A4,
 B5,
 NEW6,
 B7].

New dimension 6:
0.95.

Thus:
the full model
has never existed before,

but:
most of its local mechanism fragments
already exist.

DIAGNOSTIC BUDGET
64 total observations.

Initial sentinel:

5 observations
per dimension.

Cost:
40.

Remaining:
24.

COMPARATORS

FROM SCRATCH
Spread:
the full 64-observation budget
across:
all eight mechanisms.

NEAREST-PARENT MUTATION
Choose:
the single closest parent

then:
patch residual dimensions.

MULTI-PARENT RECOMBINATION
For each mechanism dimension:

compare:
parent predictions
with:
sentinel evidence.

If:
one parent is clearly better

and
fits within:
the residual tolerance,

inherit:
that mechanism.

If:
parent identity is ambiguous
or
neither parent fits,

estimate:
that mechanism directly
from:
the remaining diagnostic budget.

PRIMARY CONFIDENCE GATE

parent-distance fit threshold:
0.12.

best-vs-second parent distance gap:
0.12.

This is:
an exploratory working point.

PRIMARY MONTE CARLO
30,000 matched synthetic mosaic births.

DISTINCT-PARENT RESULT

FROM SCRATCH
prediction MSE:
0.016658.

NEAREST PARENT
0.017807.

CONFIDENCE-GATED MOSAIC
0.014440.

PRIMARY RECOMBINATION POSITIVE
Multi-parent reuse reduces:
prediction error

by approximately:

13.3%
vs:
from-scratch learning

and

18.9%
vs:
nearest-parent mutation.

At:
the same evidence budget.

Thus:

KNOWN MECHANISMS
IN
A NEW COMBINATION

can be learned:
more efficiently
than:
a whole new theory.

INHERITANCE FRACTION
Mean fraction of mechanism dimensions
inherited directly:

0.5803.

Mean directly estimated / residual dimensions:

3.358
of 8.

The true theory contains:
only one genuinely new mechanism.

The larger estimated count occurs because:
the confidence gate deliberately refuses:
uncertain inheritance.

This costs:
evidence

but:
protects against:
incorrect chimeric assembly.

MODULE-IDENTIFIABILITY STRESS
A second pair of parent hypotheses
has:
much more overlapping predictions.

The same mosaic principle is tested.

64-observation budget.

FROM SCRATCH:
0.016871 MSE.

NEAREST PARENT:
0.018400.

CONFIDENCE-GATED RECOMBINATION:
0.016911.

PRIMARY IDENTIFIABILITY RESULT
When:
parent fragments are difficult to distinguish,

recombination no longer provides:
a material sample-efficiency gain.

But:
the confidence gate prevents:
a major chimera failure.

The policy falls back toward:
direct estimation.

Thus:

RECOMBINE
ONLY
WHERE
PARENTAGE IS IDENTIFIABLE.

NAIVE RECOMBINATION NEGATIVE
Exploratory per-dimension recombination
without:
parent-confidence gating

performed substantially worse
under overlapping-parent conditions.

The mechanism selected:
whichever parent happened to look closer
under:
small-sample noise.

This creates:
a theory made of:
individually plausible
but
incorrectly inherited fragments.

Therefore:

COMPOSITIONAL MODEL MEMORY
NEEDS
INTERFACE / PARENTAGE CONFIDENCE.

UNKNOWN-MECHANISM HANDLING
The genuinely new dimension
is not:
forced
into:
A
or
B.

When:
neither parent is sufficiently supported,

the mechanism becomes:
a residual-estimation site.

This preserves:
open-world H98 behavior
inside:
multi-parent theory assembly.

THEORY LINEAGE
H100 now permits:
a hypothesis to have:

MULTIPLE PARENTS.

A conceptual model record may carry:

CHILD MODEL ID

+

PARENT SET

+

PER-MECHANISM ORIGIN

+

DIRECTLY ESTIMATED RESIDUALS

+

PARENTAGE CONFIDENCE

+

MODEL-FIT CONFIDENCE.

Internal causal memory can therefore become:
a recombinable lineage graph

rather than:
a flat list.

RELATION TO H81
H81:
known program fragments
can be:
recombined
into:
unseen executable programs.

H100:
known causal-model fragments
can be:
recombined
into:
unseen explanatory models.

This is the scientific-model analogue
of:
compositional program generativity.

RELATION TO H86
H86:
future-reachability portfolios
benefit from:
structurally diverse retained options.

H100:
that diversity can later become:
raw material
for:
new model composition.

Dormant diversity is useful not only:
as backup

but:
as:
recombinable structure.

IMPORTANT LIMIT
H100 assumes:
mechanism dimensions
can be:
inherited independently.

That is a strong assumption.

Real causal mechanisms may interact:

MODULE A
works differently
when paired with:
MODULE B.

This creates:
epistasis / interface incompatibility.

That is:
the next clean failure to test.

GENERAL PRINCIPLE
NEW THEORY
DOES NOT ALWAYS REQUIRE:

NEW EVERYTHING.

When:
mechanism identity is reliable,

assemble:

KNOWN CAUSAL SUBSTRUCTURE

+

SMALL NOVEL RESIDUAL.

When:
parentage is ambiguous,

fall back to:
direct evidence.

DECISION
AR-H100 is POSITIVE WITH A MODULE-IDENTIFIABILITY LIMIT.

Supported synthetically:

- unseen causal models can be assembled from multiple known parents;
- multi-parent recombination can reduce diagnostic sample cost;
- nearest-parent-only inheritance leaves useful structure unused;
- confidence gating protects against noisy parent-fragment selection;
- genuinely novel dimensions can remain residual-learning sites;
- overlapping parents erase most recombination advantage rather than requiring forced chimeras.

Not demonstrated:

- interacting causal mechanisms;
- graph-structured module inheritance;
- hidden-variable compatibility;
- distributed recombination;
- more than two parents;
- online theory lineage management.

NEXT HIGH-VALUE MOVE
AR-H101 — CAUSAL MODULE EPISTASIS / INTERFACE-COMPATIBILITY AUDIT

H100 assumes:
mechanism fragments compose independently.

Question:

WHAT IF
TWO CORRECT MODULES
BECOME WRONG
WHEN COMBINED?

Candidate stress:

parent A contains:
module X.

parent B:
module Y.

X and Y are each:
valid in their original parent contexts.

But:
X + Y together
changes:
a downstream interaction term.

Compare:

A.
naive fragment recombination;

B.
module-interface validation;

C.
joint canary challenge;

D.
residual interaction term;

E.
one pair incompatible,
another pair compatible.

Desired:

VALID MODULE
+
VALID MODULE

should NOT imply:

VALID COMPOSITION.

The organism should be able to:
reuse modules

while:
treating
their interface
as:
a new hypothesis requiring evidence.

This would be the causal-theory analogue of:
software ABI/interface compatibility
and
biological epistasis.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_model_dimensions = 8
primary_diagnostic_budget = 64
primary_matched_births = 30000
scratch_mse = 0.016658
nearest_parent_mse = 0.017807
mosaic_mse = 0.014440
