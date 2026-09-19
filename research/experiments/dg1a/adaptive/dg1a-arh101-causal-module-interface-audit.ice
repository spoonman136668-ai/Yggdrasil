TITLE: DG-1A-AR-H101 — Causal Module Epistasis / Interface-Compatibility Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE INTERFACE-VALIDATION RESULT + VALID-MODULE COMPOSITION FAILURE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh100-mosaic-hypothesis-recombination-audit.ice

PURPOSE
H100 assumes:
mechanism fragments
can be inherited
independently.

H101 attacks that assumption.

QUESTION
What if:

MODULE X
is valid,

and

MODULE Y
is valid,

but:

X + Y TOGETHER

changes:
the downstream causal behavior?

This is:
causal epistasis
or
interface incompatibility.

BOUNDARY
This is synthetic.

It does not:
- infer arbitrary nonlinear interactions;
- freeze Bernoulli interface models;
- freeze 20 interface samples;
- prove all interactions can be localized to pairwise interfaces;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PARENT MODULES

MODULE X
validated in its parent context.

success probability:
0.75.

MODULE Y
validated in its parent context.

success:
0.72.

No evidence suggests:
either module is individually broken.

NAIVE COMPOSITION PREDICTION
A simple inherited composition predicts:

joint X+Y success:
0.90.

TWO TRUE JOINT CONDITIONS

COMPATIBLE COMPOSITION

true joint success:
0.88.

The inherited prediction:
0.90

is:
essentially correct.

INCOMPATIBLE COMPOSITION

true joint success:
0.35.

Both component modules
remain individually valid.

Only:
their combination
is wrong.

PRIMARY JOINT CANARY
Execute:
the combined X+Y interface

for:
20 Bernoulli trials.

Smoothed empirical joint consequence
is compared with:
the inherited composition prediction.

Primary compatibility tolerance:

absolute difference
<=
0.20.

MONTE CARLO
40,000 matched compositions
per condition
for the primary acceptance result.

COMPATIBLE PAIR

accepted:
97.315%.

false rejection:
2.685%.

INCOMPATIBLE PAIR

incorrectly accepted:
0.025%.

rejected:
99.975%.

PRIMARY INTERFACE POSITIVE
A small amount of:
JOINT evidence

almost perfectly distinguishes:

VALID COMPOSITION

from:

TWO VALID PARTS
WITH
INVALID INTERACTION.

This is a crucial H100 correction.

PARENT CANARY LIMIT
Testing:

X alone

and

Y alone

cannot reveal:
the incompatible interaction

because:
both individual mechanisms
remain:
correct.

Thus:

MODULE VALIDATION
DOES NOT SUBSTITUTE FOR:
INTERFACE VALIDATION.

NAIVE-COMPOSITION ERROR
INCOMPATIBLE case.

Predicted joint success:
0.90.

True:
0.35.

squared prediction error:
0.3025.

This is:
large
despite:
both parent modules being correct.

INTERFACE-RESIDUAL LEARNING
Instead of:
discarding X
and
Y,

retain:
both inherited modules

and learn:
a residual joint-interface consequence

from:
the 20 combined observations.

INCOMPATIBLE residual-predictor MSE:
~0.00953
for the joint term.

COMPATIBLE:
~0.00562.

Thus:
the interaction can be:
localized

without:
rewriting:
the component mechanisms.

WHOLE-MODEL SAMPLE EFFICIENCY
Consider:
three behaviors
that must be represented:

X alone,

Y alone,

X+Y.

INHERITED + INTERFACE LEARNING

reuse:
X
and
Y
from parents.

Collect:
20 observations
only for:
X+Y.

Average three-behavior prediction MSE:

COMPATIBLE:
~0.00185.

INCOMPATIBLE:
~0.00319.

FROM SCRATCH

collect:
20 observations
for each of:
X,
Y,
and
X+Y.

Total:
60 observations.

Average MSE:

COMPATIBLE:
~0.00747.

INCOMPATIBLE:
~0.00881.

PRIMARY SAMPLE-EFFICIENCY RESULT
Reusing:
validated component mechanisms

and learning only:
the interface

produces:
lower total model error

with:
one-third the diagnostic observations.

This is:
causal compositional reuse
with:
explicit interface uncertainty.

INTERFACE AS FIRST-CLASS STATE
A recombined theory should not store only:

MODULE X

MODULE Y.

It may also require:

INTERFACE X:Y

containing:

- compatibility confidence;
- residual interaction model;
- tested context manifold;
- sample support;
- freshness;
- provenance.

Thus:
causal theory structure is closer to:

MODULE GRAPH
+
EDGE / INTERFACE STATE

than:
a bag of independent mechanism fragments.

RELATION TO H100
H100:

known causal modules
can be recombined.

H101:

recombination is safe only if:
the new interfaces
are:
validated.

The new theory should inherit:

known nodes

but treat:

new edges

as:
new hypotheses.

RELATION TO H83
H83:
functional equivalence is:
context-bounded.

H101:
interface compatibility
should also be:
context-bounded.

A module pair that composes correctly
in one regime
may:
interact differently
elsewhere.

RELATION TO SOFTWARE COMPOSITION
The useful analogy is:

two individually valid components
can fail at:
their interface.

This is similar to:
ABI,
protocol,
or
contract mismatch.

The analogy is:
architectural inspiration only.

H101 evidence remains:
synthetic.

GENERAL PRINCIPLE
VALID PART
+
VALID PART

DOES NOT IMPLY:

VALID WHOLE.

When:
old modules are recombined,

treat:
THE NEW RELATION BETWEEN THEM

as:
new evidence-bearing state.

DECISION
AR-H101 is POSITIVE WITH A VALID-MODULE COMPOSITION FAILURE.

Supported synthetically:

- individually correct causal modules can interact incompatibly;
- parent-module canaries cannot detect interaction failure;
- a small joint-interface challenge strongly discriminates compatible from incompatible composition;
- interface residuals can be learned without rewriting valid component modules;
- modular inheritance plus interface learning is substantially more sample-efficient than full relearning.

Not demonstrated:

- higher-order interactions among 3+ modules;
- context-varying interface terms;
- graph-structured causal-module induction;
- latent confounders at module interfaces;
- distributed interface testing;
- dynamic interface inheritance.

NEXT HIGH-VALUE MOVE
AR-H102 — LATENT INTERACTION CONTEXT / WHEN THE SAME INTERFACE CHANGES BEHAVIOR

H101 assumes:
X:Y
has:
one interaction behavior.

A more difficult case:

the SAME module pair
can be:

compatible
in one hidden context

and

incompatible
in another.

Question:

Can repeated interface residuals
cause:
a new latent context variable
to be discovered

rather than:
averaging incompatible behaviors
into:
one noisy edge model?

Candidate setup:

X and Y individually stable.

Their joint outcome depends on:
an unlabelled latent mode Z.

Some local observable cues
weakly correlate with:
Z.

Compare:

A.
one averaged interface model;

B.
more noise / uncertainty only;

C.
residual clustering;

D.
latent-context split
with:
reversible context fit;

E.
false cluster under ordinary noise.

Desired:

SYSTEMATIC MULTIMODAL RESIDUAL

->
CONTEXT SPLIT

not:

MORE VARIANCE.

This begins moving:
internal science

from:
parameter adaptation

toward:
latent-variable discovery.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
component_x_success = 0.75
component_y_success = 0.72
predicted_joint_success = 0.90
compatible_joint_success = 0.88
incompatible_joint_success = 0.35
primary_joint_trials = 20
