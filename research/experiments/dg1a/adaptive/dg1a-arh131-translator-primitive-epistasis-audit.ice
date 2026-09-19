TITLE: DG-1A-AR-H131 — Translator-Primitive Epistasis / Ordered Composition Grammar Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE ORDERED-PAIR GRAMMAR RESULT + FULL-HIGHER-ORDER STATE-EXPLOSION LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh130-translator-primitive-grammar-audit.ice

PURPOSE
H130 reuses:
translator primitives
across:
specciated families.

H131 attacks:
context-free composition.

Question:

WHAT IF
THE SAME PRIMITIVE
CHANGES:
ITS EFFECT

depending on:
position,
neighbor,
or:
higher-order sequence?

Then:
primitive reuse
must preserve:
interaction structure.

BOUNDARY
This is synthetic.

It does not:
- freeze sequence length 4;
- freeze eight primitive IDs;
- prove adjacent pair interactions are sufficient;
- establish a production symbolic grammar;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TRANSLATOR PROGRAM
Length:
4 primitive operations.

Primitive vocabulary:
8.

Semantic output:
four-dimensional synthetic translator consequence.

TRUE GENERATIVE STRUCTURE
Each program contains:

primitive base effect

+

position-specific primitive effect

+

ordered adjacent-pair interaction

+

rare triple interaction.

Thus:

A then B

can differ from:

B then A.

And:
some:
A-B-C
triples
carry:
extra semantics
not explained by:
pair effects.

COMPARATORS

BAG OF PRIMITIVES
Count:
which primitives occur.

Ignore:
position and order.

POSITIONAL GRAMMAR
Retain:
primitive identity
at:
each position.

ORDERED-PAIR GRAMMAR
Add:
adjacent ordered pair
interaction terms.

FULL TRIPLE GRAMMAR
Add:
all possible:
position-specific triple interaction features.

PRIMARY TRAIN / TEST
800 training sequences.

400 held-out sequences.

150 matched synthetic worlds.

OVERALL TEST MSE

BAG:
0.03388.

POSITIONAL:
0.01493.

ORDERED PAIR:
0.003383.

FULL TRIPLE:
0.004573.

PRIMARY ORDER POSITIVE
Primitive identity alone
is:
not enough.

Position
and:
neighbor relationship
carry:
major semantic information.

The ordered-pair grammar
reduces:
held-out error
by:
approximately 77%
relative to:
position-only representation.

FULL TRIPLE OVERFIT
The full triple model
has:
more representational power

but:
worse overall held-out error
than:
the simpler pairwise grammar.

STATE DIMENSIONS
Synthetic coefficient-state units
for:
four semantic outputs.

BAG:
32.

POSITIONAL:
128.

ORDERED PAIR:
896.

FULL TRIPLE:
4992.

PRIMARY STATE-EXPLOSION NEGATIVE
Representing:
EVERY POSSIBLE
higher-order interaction

causes:
rapid grammar growth.

More expressive state
is not:
automatically better
under:
finite evidence.

RARE TRUE TRIPLE INTERACTIONS
Only:
approximately 1.90%
of held-out sequences
contain:
a planted high-order triple effect.

MSE on:
those rare sequences

BAG:
~0.1217.

POSITIONAL:
~0.0992.

PAIR:
~0.0597.

FULL TRIPLE:
~0.0316.

PRIMARY RARE-INTERACTION RESULT
Higher-order state
can:
matter
greatly
for:
the small subset
where:
a real interaction exists.

The failure is not:
TRIPLES ARE USELESS.

It is:

STORE ALL POSSIBLE TRIPLES
IS TOO EXPENSIVE
AND
DATA-HUNGRY.

SPARSE HIGHER-ORDER RESIDUAL
A second audit uses:

1200 training sequences.

600 test sequences.

Start with:
the ordered-pair grammar.

Group:
persistent residuals
by:
observed triple identity.

Promote:
a triple residual term
only when:

it appears:
at least four times

and:

mean residual norm
exceeds:
0.18.

300 matched worlds.

PAIR BASELINE

overall MSE:
0.002580.

rare-triple MSE:
0.05664.

PAIR + SPARSE TRIPLE RESIDUAL

overall:
0.002461.

rare:
0.04970.

mean promoted triple terms:
2.32.

Of those:
~1.86
are:
true planted triple interactions.

~0.46
are:
false residual promotions.

PRIMARY SPARSE-INTERACTION POSITIVE
The grammar can:
remain:
mostly pairwise

while:
learning:
small higher-order exceptions
where:
evidence repeatedly demands them.

This captures:
part of:
the rare-interaction value

without:
paying:
full cubic state cost.

INTERACTION STATE
A translator grammar should plausibly contain:

PRIMITIVE

+

POSITION / ROLE

+

ORDERED LOCAL INTERFACE TERMS

+

OPTIONAL SPARSE HIGHER-ORDER RESIDUALS

+

FIT / SUPPORT

+

MEMORY COST.

Thus:
composition is:
structured
rather than:
context-free.

RELATION TO H101
H101:
two valid modules
can:
interact incompatibly.

H131:
the same principle
appears:
inside:
translator primitive grammar.

The relation:
between primitives
is:
first-class state.

RELATION TO H104
H104:
unbounded feature construction
creates:
multiple-comparison pressure.

H131:
unbounded interaction grammar
creates:
the same problem.

Promote:
higher-order structure
only after:
persistent residual evidence.

RELATION TO H130
H130:
share:
lower-level translator primitives.

H131:
sharing remains safe
only when:
composition context
is represented
where:
it materially changes semantics.

GENERAL PRINCIPLE
REUSE:
PRIMITIVES.

BUT:
DO NOT ASSUME:
PRIMITIVES ARE
CONTEXT-FREE.

STORE:

COMMON LOW-ORDER INTERACTIONS

and:

RARE HIGHER-ORDER RESIDUALS
ONLY WHEN:
EVIDENCE
PAYS FOR THEM.

DECISION
AR-H131 is POSITIVE
for:
ORDERED LOCAL TRANSLATOR GRAMMAR
WITH:
SPARSE HIGHER-ORDER RESIDUALS

AND A HARD:
FULL-INTERACTION STATE-EXPLOSION LIMIT.

Supported synthetically:

- bag-of-primitives representation loses important order semantics;
- positional information materially improves prediction;
- ordered adjacent-pair interactions provide the strongest broad generalization;
- full triple grammar is expensive and overfits overall;
- rare true triple interactions remain important locally;
- sparse residual promotion captures part of higher-order value with very little added state.

Not demonstrated:

- interaction order beyond triples;
- stateful nonlinear translator semantics;
- online interaction birth/retirement;
- cross-family interaction reuse;
- active challenge for suspected interaction;
- distributed grammar execution.

NEXT HIGH-VALUE MOVE
AR-H132 — INTERACTION CHALLENGE / VALUE-GATED HIGHER-ORDER SEMANTIC TESTING

H131 detects:
higher-order interaction
from:
passive residual recurrence.

Question:

CAN THE ORGANISM
ACTIVE-TEST
A SUSPECTED:
PRIMITIVE INTERACTION

BEFORE:
PERMANENTLY ADDING
GRAMMAR STATE?

Candidate comparison:

A.
passive residual only;

B.
promote after:
training fit;

C.
targeted sequence challenge
where:
pairwise and triple models
predict:
different consequences;

D.
challenge cost;

E.
rare harmful triple
with:
high consequence;

F.
false residual caused by:
noise.

Desired:

NEW GRAMMAR STRUCTURE
should:
earn:
permanent state
through:
a discriminating semantic challenge

when:
the cost is:
worth paying.

This would connect:
H131
to:
H84 active discrimination
and:
H103 sensor audition.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primitive_count = 8
sequence_length = 4
bag_mse = 0.03388442
position_mse = 0.01493332
pair_mse = 0.00338291
full_triple_mse = 0.00457324
pair_state = 896
full_triple_state = 4992
sparse_promoted_triples_mean = 2.3233
sparse_pair_mse = 0.00246068
