TITLE: DG-1A-AR-H81 — Zero-Shot Grammatical Recombination / Novel Program Assembly Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE REUSABLE-SUBSTRUCTURE GENERALIZATION RESULT + NON-UNIVERSAL-HIERARCHY ADVANTAGE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh80-developmental-macro-grammar-audit.ice

PURPOSE
H80 showed that:
a memory-priced grammar can store more reusable macro structure than a flat macro set under the same permanent-memory budget.

H81 asks the generativity question:

DOES STORED SUBSTRUCTURE HELP WITH
PROGRAMS THE ORGANISM HAS NEVER EXECUTED BEFORE?

This is the distinction between:

COMPRESSION OF OLD TASKS

and

GENERATIVE RECOMBINATION.

BOUNDARY
This is synthetic.

It does not:
- solve open-ended program synthesis;
- infer primitive semantics from raw data;
- freeze the greedy grammar learner;
- prove hierarchical grammar always beats flat reusable chunks;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PRIMITIVE ALPHABET
15 primitive transformation symbols.

KNOWN REUSABLE MOTIFS
Eight latent motifs from H80.

TRAINING PROGRAMS
16 successful program types.

The training set contains:
all eight known motifs

but only:
a subset of their possible combinations.

HELD-OUT PROGRAMS
8 additional program types.

None is presented during training.

They contain:
known motifs
in
new combinations.

TRAINING MEMORY BUDGET
55 synthetic storage units.

COMPARATORS

PRIMITIVE ONLY

No learned executable memory.

EXACT-TASK MEMORY
Store full previously observed programs
until memory budget is exhausted.

This is episodic / task-specific compilation.

FLAT REUSABLE CHUNKS
Store useful contiguous subsequences under:
the same memory budget.

No hierarchical definition reuse.

REUSABLE GRAMMAR
Store reusable chunks,
where:
larger definitions may reference
existing lower-level chunks.

Same approximate memory budget.

PRIMARY LEARNED MEMORY

EXACT TASK MEMORY

stored full programs:
6.

storage:
54.

FLAT CHUNKS

stored chunks:
13.

storage:
54.

GRAMMAR

stored macros:
18.

storage:
54.

The grammar stores:
3x as many executable structures
as
full-task memory
under:
the same permanent memory budget.

HELD-OUT NOVEL COMBINATIONS
Mean executable action count.

PRIMITIVE ONLY

9.625 actions / program.

EXACT-TASK MEMORY

7.875.

FLAT REUSABLE CHUNKS

5.000.

REUSABLE GRAMMAR

4.875.

PRIMARY ZERO-SHOT POSITIVE
The held-out programs were:
never executed during training.

Yet reusable substructure immediately reduces:
their execution description length.

Compared with primitives:

grammar:
approximately 49.4%
fewer actions.

Compared with exact-task memory:

approximately 38.1%
fewer.

Thus:
stored developmental structure can support:
new composition

rather than:
only replay.

WHY EXACT TASK MEMORY HELPS AT ALL
Some held-out programs contain:
training-program substrings
that happen to match
a stored full-program macro prefix / segment
under the synthetic segmentation model.

But:
exact memory cannot systematically cover:
new motif orderings.

Its improvement is much smaller than:
subsequence-based memory.

STRICT NEW-ORDER TEST
A separate set of 8 programs is built from:
known motifs

but in:
orders not seen in training.

MEAN ACTIONS

PRIMITIVE:
8.625.

EXACT-TASK:
8.625.

FLAT CHUNKS:
4.875.

GRAMMAR:
4.875.

PRIMARY REORDER RESULT
Exact episodic program memory provides:
zero benefit

when:
the full stored tasks do not appear as reusable substrings.

Reusable substructure cuts:
execution length by approximately 43.5%.

Thus:
compositional memory generalizes across:
ordering.

UNKNOWN-MOTIF STRESS
Insert one completely unseen primitive motif:

J =
three new primitive operators.

The surrounding program still uses:
known motifs.

MEAN ACTIONS

PRIMITIVE:
12.625.

EXACT TASK:
12.625.

FLAT:
8.125.

GRAMMAR:
7.875.

PRIMARY FALLBACK POSITIVE
The reusable grammar does NOT need:
the whole new program
to already exist.

It uses:
known macros

around:
the unknown region

and falls back to:
primitive execution
for:
the new motif.

This is the desired architecture:

KNOWN SUBSTRUCTURE
->
reuse.

UNKNOWN SUBSTRUCTURE
->
local primitive fallback.

Do not discard:
the entire learned program representation.

MEMORY-BUDGET SWEEP
The hierarchy itself is NOT universally superior.

Held-out mean actions.

BUDGET 25

flat:
6.000.

grammar:
5.625.

BUDGET 35

flat:
5.625.

grammar:
5.500.

BUDGET 45

flat:
5.000.

grammar:
5.375.

BUDGET 55

flat:
5.000.

grammar:
4.875.

BUDGET 70

flat:
4.875.

grammar:
4.875.

PRIMARY NON-UNIVERSAL-HIERARCHY RESULT
The tested greedy grammar induction heuristic does NOT dominate:
flat reusable chunks

at every memory budget.

At budget 45:
flat chunks are better.

At budget 70:
they are equal.

Therefore:

HIERARCHY
IS NOT AUTOMATICALLY
GENERATIVE INTELLIGENCE.

The value depends on:
which reusable units are selected
and
their dependency structure.

This negative must remain.

GRAMMAR SIZE / EXPRESSIVITY TRADEOFF
At memory budget 55:

flat:
13 executable chunks.

grammar:
18.

The grammar represents:
a richer reusable vocabulary

but introduces:
definition dependencies.

A poor hierarchical decomposition can:
waste memory
or
create brittle shared dependencies.

Thus:
substructure selection matters at least as much as:
hierarchical representation.

ZERO-SHOT INTERPRETATION
H81 does NOT mean:
the organism inferred an unknown task goal with no evidence.

It means:

once a new functional program is being assembled / demanded,
known transformations can be:
reused immediately

without:
relearning every lower-level sequence.

This is:
structural transfer,
not:
magical zero-shot semantics.

RELATION TO H36
H36:
shared generative lineage structure
allows old capabilities to be reconstructed from:
common basis
+
small lineage coordinates.

H81:
shared executable grammar
allows new programs to be assembled from:
common computational substructure
+
novel composition.

These are parallel memory principles.

RELATION TO H78-H80
H78:
discover useful primitive pathways.

H79:
compile repeated sequences.

H80:
organize macros into reusable memory.

H81:
reuse that memory in:
unseen compositions.

The progression now reaches:
COMPOSITIONAL GENERATIVITY.

GENERAL PRINCIPLE
PERMANENT MEMORY SHOULD STORE:

WHAT REPEATS ACROSS TASKS,

not merely:

WHAT HAPPENED BEFORE.

Then:

NOVEL PROGRAM
can be represented as:

KNOWN STRUCTURE
+
SMALL NOVEL RESIDUAL.

This is the executable analogue of:
generative developmental memory.

DECISION
AR-H81 is POSITIVE FOR REUSABLE-SUBSTRUCTURE GENERALIZATION,
with a NON-UNIVERSAL HIERARCHY ADVANTAGE.

Supported synthetically:

- reusable executable chunks generalize to held-out program combinations;
- exact full-task memory generalizes poorly to reordered unseen tasks;
- known substructure can surround an unknown primitive motif without retraining the whole program;
- hierarchical grammar can store more executable units under a fixed budget;
- the tested grammar modestly improves held-out action count at the primary budget;
- hierarchical grammar is not consistently superior to flat reusable chunks at every budget.

Not demonstrated:

- autonomous task-goal discovery;
- new primitive invention;
- online search over arbitrary compositions;
- semantic equivalence between different programs;
- real execution speedup;
- safe distributed grammar sharing.

NEXT HIGH-VALUE MOVE
AR-H82 — FUNCTIONAL EQUIVALENCE / MULTIPLE PROGRAMS FOR THE SAME OUTCOME

H81 assumes:
one primitive sequence
is the desired program.

A more interesting system should discover that:

DIFFERENT COMPUTATIONAL PATHS
CAN PRODUCE
THE SAME FUNCTION.

Question:

Can Yggdrasil preserve:
multiple functionally equivalent implementations

and choose among them according to:
local resource metabolism?

Example:

PATH A:
compute-heavy / memory-light.

PATH B:
memory-heavy / compute-light.

PATH C:
communication-heavy but fast.

Compare:

A.
retain only the historically best program;

B.
retain an equivalence class of programs;

C.
resource-priced implementation choice;

D.
one path becomes unavailable;

E.
novel resource regime;

F.
macro-memory cost of redundant implementations.

Desired:

FUNCTION IDENTITY
should be separated from:
IMPLEMENTATION IDENTITY.

This would connect:
H68 metabolic transformation

with:
H78-H81 program development.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
training_programs = 16
heldout_programs = 8
memory_budget = 55
primary_grammar_storage = 54
primary_grammar_macro_count = 18
