TITLE: DG-1A-AR-H130 — Meta-Family Reuse / Shared Translator Primitive Grammar Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE SHARED-PRIMITIVE-GRAMMAR RESULT + FAMILY-SPECIFIC MUTATION FALLBACK
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh129-version-fork-speciation-audit.ice

PURPOSE
H129 creates:
separate translator families
when:
regional semantic branches remain:
persistently incompatible.

H130 asks:

DO SPECIATED FAMILIES
STILL SHARE:
LOWER-LEVEL TRANSLATION SUBSTRUCTURE?

If yes,
full family independence
duplicates:
too much common machinery.

BOUNDARY
This is synthetic.

It does not:
- freeze 12 primitive translators;
- freeze sequence length 4;
- prove the inferred primitive basis is semantically interpretable;
- establish final grammar-learning machinery;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TRANSLATOR PRIMITIVE LIBRARY
12 latent primitive translator components.

Each primitive has:
six semantic parameters.

FAMILY COMPOSITION
48 translator families.

Each family
is built from:
a four-position composition
of:
translator primitives.

Position weights:

1.0,
0.8,
0.6,
0.4.

Thus:
different families
reuse:
the same lower-level translation components
in:
different combinations.

FAMILY-SPECIFIC MUTATION
Approximately:
15%
of families
contain:
an additional local semantic mutation
not explained by:
the shared primitive grammar.

This tests:
whether:
shared structure
can coexist with:
family-specific residuals.

OBSERVATION
Each family has:
noisy empirical translator estimates.

COMPARATORS

FULLY INDEPENDENT FAMILY
Store:
six direct parameters
per family.

GLOBAL ONE-TRANSLATOR
Use:
one shared translator
for:
all families.

SHARED PRIMITIVE GRAMMAR
Fit:
12 shared primitive parameter vectors.

Each family stores:
a short composition reference.

GRAMMAR + FAMILY RESIDUAL
Use:
shared primitive grammar

plus:
family-local residual
when:
independent validation
shows:
the family is:
off-grammar.

PRIMARY RESIDUAL GATE
Independent family validation
flags:
a family-specific residual
when:
its deviation from:
the grammar prediction
exceeds:
0.45
in:
the synthetic six-dimensional semantic norm.

PRIMARY CONFIRMATION
1,000 synthetic translator ecologies.

PREDICTION MSE

FULLY INDEPENDENT:
0.00993.

GLOBAL ONE-TRANSLATOR:
0.40054.

SHARED GRAMMAR:
0.01127.

GRAMMAR + RESIDUAL:
0.00529.

PRIMARY SHARED-STRUCTURE POSITIVE
The primitive grammar
approaches:
the prediction quality
of:
fully independent family copies

with:
far less permanent state.

When:
family-specific mutations
are represented explicitly,

the grammar + residual system
outperforms:
independent noisy family estimation.

STORAGE
Synthetic scalar-equivalent state.

FULL INDEPENDENT:
288.

SHARED GRAMMAR:
95.04.

GRAMMAR + RESIDUAL:
135.66.

PRIMARY MEMORY RESULT
The grammar + residual representation
uses:
less than half:
the permanent state
of:
fully independent families

while:
also producing:
lower prediction error
in:
the tested noisy-estimation regime.

This is the desired consequence of:

SHARE:
WHAT REPEATS.

STORE:
ONLY:
THE DIFFERENCE
THAT DOES NOT.

MUTATION DETECTION
Primary residual gate:

true family-specific mutation detection:
~73.98%.

false residual creation
among ordinary families:
~3.59%.

This is:
not perfect.

The gate deliberately:
misses:
some smaller mutations
to:
avoid:
residual-state explosion.

A later challenge can:
recruit:
a missed residual
if:
functional mismatch persists.

NEW FAMILY FROM KNOWN PRIMITIVES
A held-out translator family
is assembled from:
previously known primitive components
in:
a combination
not used:
during fitting.

Prediction MSE

GRAMMAR:
0.00733.

FROM-SCRATCH NOISY FAMILY ESTIMATE:
0.00974.

PRIMARY ZERO-SHOT FAMILY-ASSEMBLY POSITIVE
Known translator primitives
can:
support:
a new family composition

without:
requiring:
full family relearning.

This is:
the interface-family analogue
of:
H81 program recombination
and:
H100 theory recombination.

UNKNOWN-PRIMITIVE STRESS
One position
in:
a held-out family
is replaced by:
a genuinely new primitive
not present:
in:
the shared grammar.

GRAMMAR-ONLY MSE:
0.11698.

PRIMARY OPEN-WORLD NEGATIVE
A compositional grammar
cannot:
reconstruct:
a primitive
it has never represented.

The grammar's confidence
must:
fall
when:
the new family lies:
off:
the primitive span.

LOCAL RESIDUAL FALLBACK
A limited local family observation
estimates:
the unexplained residual.

MSE after:
local fallback:
0.01425.

Thus:
the architecture can:
retain:
known primitive composition

and learn:
only:
the missing local component.

It does not need:
to discard:
the whole grammar.

META-FAMILY INTERPRETATION
H129 creates:
separate translator families.

H130 suggests:
family separation
can happen at:
the level that actually differs.

Families can share:

LOW-LEVEL TRANSLATOR PRIMITIVES

while keeping:

FAMILY-SPECIFIC COMPOSITION

and:

LOCAL SEMANTIC RESIDUALS.

This is:
hierarchical speciation.

RELATION TO H80-H81
Executable program memory
became:
a reusable grammar
rather than:
a flat macro library.

H130:
interface-family memory
does the same.

Both support:

KNOWN SUBSTRUCTURE

+

NOVEL COMPOSITION

+

LOCAL FALLBACK.

RELATION TO H36
H36:
shared lineage basis
compresses:
related generative state.

H130:
shared translator primitive basis
compresses:
related interface state.

The same developmental memory law
continues:
reappearing.

RELATION TO H125
H125:
false family sharing
requires:
residuals / subfamilies.

H130:
speciated families
can still:
share:
lower-level pieces

if:
the sharing occurs:
below
the semantic difference.

GENERAL PRINCIPLE
SPECIATION
SHOULD SEPARATE:

WHAT DIFFERS,

NOT:
DUPLICATE:
EVERYTHING.

Use:

COMMON PRIMITIVES

+

FAMILY-SPECIFIC COMPOSITION

+

LOCAL RESIDUAL.

DECISION
AR-H130 is POSITIVE
for:
SHARED TRANSLATOR PRIMITIVE GRAMMAR
ACROSS:
SPECIATED FAMILIES

WITH:
AN UNKNOWN-PRIMITIVE FALLBACK LIMIT.

Supported synthetically:

- translator families can share substantial lower-level structure;
- one global translator is grossly insufficient;
- primitive grammar greatly reduces memory;
- grammar + local residual outperforms independent family estimation in the tested noisy regime;
- new family combinations of known primitives transfer immediately;
- a genuinely new primitive creates clear off-grammar error;
- local residual learning repairs unknown structure without discarding known grammar.

Not demonstrated:

- online primitive discovery;
- primitive ordering with stateful semantics;
- primitive interaction / epistasis;
- family-specific primitive mutation inheritance;
- multi-level grammar induction;
- distributed primitive ownership.

NEXT HIGH-VALUE MOVE
AR-H131 — TRANSLATOR-PRIMITIVE EPISTASIS / COMPOSITION-ORDER AUDIT

H130 assumes:
translator primitives
compose:
approximately independently.

Question:

WHAT IF
THE SAME TWO PRIMITIVES
MEAN:
DIFFERENT THINGS
WHEN:
THEIR ORDER
OR:
NEIGHBOR
CHANGES?

Potential failure:

A
then
B

is valid,

but:

B
then
A

or:

A
next to
C

changes:
the semantics.

Compare:

A.
bag-of-primitives grammar;

B.
ordered composition grammar;

C.
pairwise interface terms;

D.
rare higher-order interaction;

E.
independent validation;

F.
memory price
for:
interaction structure.

Desired:

REUSE PRIMITIVES

without:
assuming:
context-free composition.

This is:
the translator-grammar analogue
of:
H101 causal-module epistasis.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
translator_families = 48
primitive_count = 12
sequence_length = 4
independent_mse = 0.00993235
grammar_mse = 0.01126760
grammar_residual_mse = 0.00528961
independent_storage = 288
grammar_storage = 95.04
grammar_residual_storage = 135.66
known_new_family_grammar_mse = 0.00732853
unknown_primitive_grammar_mse = 0.11697805
unknown_primitive_residual_mse = 0.01425480
