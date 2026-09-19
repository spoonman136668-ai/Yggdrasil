TITLE: DG-1A-AR-H80 — Macro Ecology / Memory-Priced Developmental Grammar Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE REUSABLE-GRAMMAR RESULT + COMPILE-EVERYTHING MEMORY-EXPLOSION LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh79-reversible-compositional-chunking-audit.ice

PURPOSE
H79 showed that repeatedly useful primitive compositions can become:
reversible macro-operators.

H80 asks the scaling question:

WHAT HAPPENS IF EVERY REPEATEDLY USEFUL SEQUENCE
TRIES TO BECOME A MACRO?

A developmental organism must avoid:
turning learning into an ever-growing flat library of compiled fragments.

H80 explores a different representation:

DEVELOPMENTAL GRAMMAR.

Common substructure can be stored once
and
larger macros can reference:
existing lower-level chunks.

BOUNDARY
This is synthetic.

It does not:
- prove a production grammar-induction algorithm;
- freeze macro lengths 2..6;
- freeze the memory price;
- establish optimal Minimum Description Length;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PRIMITIVE ALPHABET
15 primitive operator symbols.

REUSABLE MOTIFS
Eight latent reusable subsequences.

Examples include:
three-symbol,
two-symbol,
and
closely related variant motifs.

PROGRAM POPULATION
24 synthetic successful task programs.

Programs are built from:
different combinations
of
shared motifs.

Program lengths are approximately:
8..12 primitive operations.

The controller is NOT given:
motif labels.

CANDIDATE MACROS
Every contiguous successful subsequence of length:

2..6

is eligible for nomination.

Total unique candidates:

250.

EXECUTION MODEL
Without a macro:
each primitive costs:
1 execution action.

A stored macro:
executes its entire represented sequence
as:
1 action.

Execution cost for a program is computed by:
best available segmentation into:
primitives
and
macros.

WORKLOAD PHASES

PHASE 0
favors:
A-family
and
B/C reusable motifs.

PHASE 1
shifts toward:
D-family
E/F/H compositions.

PHASE 2
returns toward:
the original phase-0 task family
with a small variation.

This tests:
recurrence
and
macro reuse.

POLICIES

COMPILE EVERYTHING
Store all 250 candidate macros.

No memory price.

FIXED TOP-10
Store the 10 chunks with highest:
observed occurrence
*
primitive actions saved.

FLAT MEMORY-PRICED
Memory budget:
55 synthetic storage units.

Flat macro definition cost:

macro length
+
1 header.

Greedy selection by:
expected action savings / storage.

REUSABLE GRAMMAR
Same approximate:
55-unit memory budget.

But a new macro definition may reference:
already stored macros.

Definition cost:

1 header
+
shortest representation of the macro body using:
primitives
or
existing macros.

Selection is a greedy synthetic grammar heuristic.

It is not globally optimal.

MEMORY PRICE FOR COMBINED DIAGNOSTIC
0.01 synthetic execution-equivalent units
per storage unit.

This is used only to show:
memory/execution tradeoff.

PRIMARY PHASE-0 RESULTS

COMPILE EVERYTHING

macros:
250.

storage:
1333.

execution actions / task:
2.000.

combined cost:
15.330.

PRIMARY MEMORY-EXPLOSION NEGATIVE
Flat universal compilation minimizes:
execution steps

but:
creates enormous permanent macro state.

At the tested memory price,
its total cost is:
almost 3x
the compact policies.

Thus:

FAST EXECUTION
CAN BE
A BAD DEVELOPMENTAL MEMORY POLICY.

FIXED TOP-10

macros:
10.

storage:
53.

actions/task:
4.9844.

combined:
5.5144.

FLAT MEMORY-PRICED

macros:
13.

storage:
54.

actions:
4.6263.

combined:
5.1663.

REUSABLE GRAMMAR

macros:
17.

storage:
53.

actions:
4.5657.

combined:
5.0957.

PRIMARY GRAMMAR POSITIVE
At essentially the same permanent storage:

53
vs
54 units,

the grammar can retain:

17 reusable macros

vs
13 flat macros.

It also lowers:
execution cost.

The gain is modest in phase 0,
but demonstrates:
shared substructure reduces the cost of keeping a richer macro repertoire.

PHASE-1 SHIFT

COMPILE EVERYTHING

actions:
2.000.

storage:
1333.

combined:
15.330.

FIXED TOP-10

actions:
5.0509.

storage:
57.

combined:
5.6209.

FLAT MEMORY-PRICED

actions:
4.8715.

storage:
54.

combined:
5.4115.

REUSABLE GRAMMAR

actions:
4.4841.

storage:
53.

combined:
5.0141.

PRIMARY SHIFT RESULT
Under the shifted task family,
shared grammatical structure becomes more valuable.

At nearly identical storage,
grammar execution is:

approximately 7.9%
lower action cost

than:
flat memory-priced chunks.

The macro ecology benefits from:
substructure reuse.

PHASE-2 RECURRENCE

FIXED TOP-10

actions:
5.0550.

storage:
53.

FLAT PRICED

4.7113.

storage:
53.

GRAMMAR

4.6452.

storage:
53.

Again:
the grammar retains the best compact execution of the tested policies.

RECURRING STRUCTURE
Compare macro sets selected independently for:
phase 0
and
phase 2.

Jaccard overlap:

FIXED TOP-10:
0.818.

FLAT MEMORY-PRICED:
0.857.

REUSABLE GRAMMAR:
1.000.

PRIMARY RECURRENCE POSITIVE
The grammar selects:
the exact same stored macro set

when the original task family returns.

This indicates the retained objects reflect:
reusable structural regularities

rather than:
only transient full-task frequency.

PHASE-0 GRAMMAR FROZEN INTO PHASE 1
If the phase-0 macro set is NOT updated:

phase-1 actions/task:

FIXED TOP-10:
6.7295.

FLAT PRICED:
5.7663.

GRAMMAR:
5.6494.

Thus:
the reusable grammar also degrades somewhat more gracefully under:
unanticipated shift.

It still needs:
adaptation.

GRAMMAR IS NOT FREE
The reusable representation introduces:
dependency structure.

A higher macro may depend on:
lower chunks.

Therefore:
retirement
or
corruption
of a submacro

can affect:
multiple higher-level compiled structures.

This is analogous to:
shared lineage template leverage
in H36-H40.

Macro dependency should therefore carry:
versioning
and
trust.

MACRO SET CHURN
Independent task phases select:
different grammar structure.

Phase-0 vs phase-1 grammar overlap:
approximately 0.214.

This is expected because:
the work ecology changes substantially.

Phase-0 vs phase-2:
1.000.

Thus:
some macro state should be:
retired/suppressed

while:
recurring structural grammar can remain.

RELATION TO H34-H40
Dormant lineages taught:

do not retain:
every complete old instance.

Retain:
shared generative structure
+
small specific state.

H80 finds the computational analogue:

do not retain:
every successful program as a flat macro.

Retain:
shared executable grammar
+
composable structure.

RELATION TO H79
H79:
one useful sequence can become:
a macro.

H80:
many useful macros should form:
a structured ecology
under:
memory pressure.

The progression is:

PRIMITIVES

->
MACROS

->
SHARED GRAMMAR.

OUTSIDE-STATUS-QUO IMPLICATION
Permanent learned computation might be represented less like:
a growing network of dedicated modules

and more like:
an evolving local grammar
of reusable transformations.

Mature capability can become:
compressed syntax.

Novel behavior can be:
generated by recombining
that syntax.

This begins to resemble:
developmental program induction

rather than:
parameter accumulation alone.

GENERAL PRINCIPLE
COMPILE REPEATED STRUCTURE

but

PRICE PERMANENT REPRESENTATION.

Then:

SHARE COMMON SUBSTRUCTURE

instead of:
duplicating every successful sequence.

DECISION
AR-H80 is POSITIVE WITH A MACRO-DEPENDENCY LEVERAGE LIMIT.

Supported synthetically:

- compiling every candidate chunk creates large permanent memory growth;
- memory pricing strongly changes the preferred macro repertoire;
- shared substructure allows more useful macros under the same storage budget;
- reusable grammar lowers execution cost relative to flat chunks;
- recurring task families recover the same grammar;
- a grammar learned in one regime retains some value after shift;
- hierarchical dependencies create new shared-state failure leverage.

Not demonstrated:

- online grammar induction;
- optimal hierarchical chunk structure;
- safe macro dependency updates;
- spatially distributed grammar;
- actual learned program semantics;
- zero-shot recombination into unseen functional programs.

NEXT HIGH-VALUE MOVE
AR-H81 — ZERO-SHOT GRAMMATICAL RECOMBINATION / NOVEL PROGRAM ASSEMBLY

H80 stores:
shared executable substructure.

The next question is critical:

DOES THAT STRUCTURE HELP WITH
A PROGRAM THE ORGANISM HAS NEVER EXECUTED BEFORE?

Construct:
novel held-out task sequences

using:
previously learned motifs
in
new combinations.

Compare:

A.
primitive-only search;

B.
flat task-specific macros;

C.
reusable grammar;

D.
novel task containing one unknown motif;

E.
novel task whose old motifs appear in a new order.

Desired:

known pieces,
new composition
->
much faster functional search.

unknown piece
->
fall back locally to primitives
without discarding:
known grammar.

This tests whether:
compressed developmental memory

becomes:
generative capability

rather than:
only compression.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primitive_symbols = 15
program_count = 24
candidate_macros = 250
memory_budget = 55
phase0_grammar_macros = 17
phase0_grammar_storage = 53
