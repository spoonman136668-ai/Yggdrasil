TITLE: DG-1A-AR-H83 — Functional Equivalence Discovery / Context-Bounded False-Equivalence Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE MULTI-CONTEXT EQUIVALENCE RESULT + HARD COMMON-CONTEXT FALSE-EQUIVALENCE LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh82-functional-degeneracy-audit.ice

PURPOSE
H82 assumed that several structurally different implementations were already known to perform:
the same function.

H83 removes that privilege.

QUESTION
Can Yggdrasil infer:
FUNCTIONAL EQUIVALENCE

from:
observed consequence fingerprints

without:
program semantic labels?

And:

how should it avoid declaring two programs:
universally equivalent

when they have only been tested in:
the same narrow context?

BOUNDARY
This is synthetic.

It does not:
- solve semantic program equivalence;
- prove finite canaries can establish universal equivalence;
- freeze the tolerance threshold;
- freeze six contexts;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

FUNCTIONAL FINGERPRINT
Each implementation is evaluated through:
local binary functional consequence

across:
six synthetic contexts.

The organism sees:
outcome statistics.

It does NOT receive:
a semantic function label.

IMPLEMENTATION A
Context success probabilities:

[0.90,
 0.88,
 0.92,
 0.90,
 0.85,
 0.87].

IMPLEMENTATION B — TRUE PRACTICAL EQUIVALENT

[0.89,
 0.89,
 0.91,
 0.91,
 0.86,
 0.86].

A and B differ only:
slightly
across all tested contexts.

They are treated as:
functionally equivalent within the experiment's tolerance.

IMPLEMENTATION C — CONTEXT-LIMITED IMPOSTOR

[0.90,
 0.88,
 0.92,
 0.90,
 0.35,
 0.30].

C is effectively identical to A in:
the four common contexts.

But:
it fails strongly in:
two rare / alternate contexts.

IMPLEMENTATION D — CLEARLY DIFFERENT

approximately:

[0.65,
 0.68,
 0.62,
 0.66,
 0.60,
 0.64].

CANARY SAMPLING
30 trials per tested context.

Equivalence decision:

maximum observed context-wise success-rate difference
<=
0.22.

The threshold is deliberately permissive enough to retain:
the slightly noisy A/B equivalent pair.

20,000 Monte Carlo equivalence trials per comparison.

ONE COMMON CONTEXT ONLY

A/B true equivalent accepted:
99.18%.

A/C false-equivalent accepted:
99.385%.

A/D different pair incorrectly accepted:
37.36%.

PRIMARY SINGLE-CONTEXT NEGATIVE
One canary context is nearly useless for:
general functional identity.

A and C are:
indistinguishable

because:
the test does not expose:
where they differ.

FOUR COMMON CONTEXTS

A/B accepted:
97.625%.

A/C accepted:
97.70%.

A/D accepted:
1.705%.

PRIMARY COMMON-CONTEXT LIMIT
More tests drawn from:
the same functional regime

strongly reject:
clearly different implementations.

But they do NOT reject:
a program that shares the same common-context behavior.

Thus:

MORE SAMPLES
DO NOT CREATE
MORE FUNCTIONAL COVERAGE.

This is the equivalence analogue of:
provenance diversity.

FIVE CONTEXTS
The fifth context is one of:
the rare discriminating regimes.

A/B accepted:
95.825%.

A/C false equivalence:
0.650%.

A/D:
0.610%.

PRIMARY MULTI-CONTEXT POSITIVE
Adding:
one genuinely different consequence context

reduces A/C false equivalence from:

97.7%
to
0.65%.

True A/B equivalence remains:
approximately 95.8%.

SIX CONTEXTS

A/B accepted:
94.40%.

A/C:
0%.

A/D:
0.270%.

This further increases:
functional-domain coverage

but also:
slightly raises false rejection of the true approximate equivalent

because:
more noisy dimensions must all satisfy the same threshold.

PRIMARY COVERAGE / CONFIDENCE TRADEOFF
More diverse canaries improve:
false-equivalence detection.

But:
every added noisy context creates:
another chance to reject a genuinely equivalent pair.

Equivalence therefore needs:
confidence
and
tolerance.

It should not be:
a permanent Boolean fact.

CONTEXT-BOUNDED EQUIVALENCE
The correct statement after only the first four contexts is:

A
and
C

ARE EQUIVALENT
WITHIN
THE CURRENTLY TESTED COMMON-CONTEXT DOMAIN.

The incorrect statement is:

A
and
C
ARE THE SAME FUNCTION
EVERYWHERE.

H83 strongly supports:
the first representation.

RESOURCE-SELECTION FAILURE
Suppose C is:
cheaper
than A

under:
a new local resource state.

If the system treats:
common-context equivalence

as:
universal identity,

it may preferentially switch:
A -> C

exactly when:
the rare functional context appears.

True rare-context success:

A:
approximately 0.85..0.87.

C:
0.30..0.35.

Thus:
false equivalence can turn:
resource optimization

into:
functional collapse.

This directly constrains H82.

EQUIVALENCE OBJECT
A function-equivalence relation should conceptually retain:

PROGRAM A

PROGRAM B

+

TESTED CONTEXT / CONSEQUENCE MANIFOLD

+

FUNCTIONAL TOLERANCE

+

SAMPLE SUPPORT

+

FRESHNESS

+

CANARY PROVENANCE

+

MODEL-FIT / CONTEXT-FIT CONFIDENCE.

Equivalence is:
evidence state,
not:
ontology.

RELATION TO H7
H7 established:
model-fit confidence is separate from:
stored prior confidence.

H83:

functional-equivalence confidence
must also depend on:
whether the current context lies inside:
the tested equivalence manifold.

RELATION TO H40
H40:
many canaries with the same failure provenance
do not create independent validation.

H83:
many canaries from the same functional context
do not create:
functional-domain coverage.

The recurring principle is:

DIVERSITY OF EVIDENCE
MATTERS MORE THAN:
RAW COUNT.

RELATION TO H82
H82:
multiple implementations can improve:
robustness
and
resource flexibility.

H83 adds:

ONLY GROUP IMPLEMENTATIONS
AS EQUIVALENT
WITHIN
THE DOMAIN ACTUALLY VALIDATED.

When context moves off that domain:

equivalence authority should:
drop
or
require challenge.

GENERAL PRINCIPLE
DO NOT STORE:

PROGRAM A == PROGRAM B.

Store something closer to:

PROGRAM A
≈
PROGRAM B

UNDER:
CONTEXT MANIFOLD M

WITH:
CONFIDENCE C
AND
TOLERANCE ε.

This is much safer
and
more expressive.

DECISION
AR-H83 is POSITIVE WITH A HARD COMMON-CONTEXT FALSE-EQUIVALENCE LIMIT.

Supported synthetically:

- functional equivalence can be estimated from outcome fingerprints without semantic program labels;
- one common context creates severe false-equivalence risk;
- repeated tests in the same context do not solve context-limited equivalence;
- one genuinely diverse context can sharply discriminate a hidden functional difference;
- true approximate equivalence can survive multi-context testing;
- equivalence should carry context fit, support, and confidence;
- universal equivalence claims are not justified by finite common-context evidence.

Not demonstrated:

- automatic selection of maximally discriminating contexts;
- continuous high-dimensional functional fingerprints;
- real task-function identity;
- equivalence under delayed consequences;
- equivalence discovery under corrupted canaries;
- semantic transfer across unrelated inputs.

NEXT HIGH-VALUE MOVE
AR-H84 — ACTIVE EQUIVALENCE CHALLENGE / INFORMATION-GAINED PROGRAM DISCRIMINATION

H83 uses:
a predefined set of test contexts.

Question:

Can the organism choose:
WHICH CONTEXT / CHALLENGE
is most valuable

for distinguishing:
two apparently equivalent programs?

Candidate principle:

find a local perturbation where:
their predicted consequences
diverge most.

Compare:

A.
repeat ordinary context;

B.
random context exploration;

C.
uncertainty-maximizing challenge;

D.
predicted-disagreement challenge;

E.
challenge cost / safety.

Desired:

equivalence uncertainty
->
select a small discriminating functional test

rather than:
collecting more redundant evidence.

This would connect:
H83 equivalence

with:
S4-S9 / H21-H22 value-of-information

and
H20 functional context validation.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
functional_contexts = 6
canary_trials_per_context = 30
monte_carlo_trials = 20000
equivalence_threshold = 0.22
