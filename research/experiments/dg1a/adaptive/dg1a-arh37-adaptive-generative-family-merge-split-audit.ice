TITLE: DG-1A-AR-H37 — Adaptive Generative-Family Merge / Split Under Memory Pressure
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE MEMORY-PRICED MERGE/SPLIT RESULT + PERSISTENCE REQUIREMENT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh36-shared-generative-template-lineage-compression-audit.ice

PURPOSE
H36 showed that many related retired lineages can share one compact generative basis,
but forcing unrelated lineage families into one basis creates severe regenerative interference.

H37 asks:

WHEN SHOULD TWO GENERATIVE FAMILIES MERGE TO SAVE MEMORY,
AND WHEN SHOULD THEY SPLIT BECAUSE FORCED SHARING COSTS TOO MUCH FUNCTION?

BOUNDARY
This is synthetic.

It does not:
- freeze a production merge threshold;
- freeze a family rank;
- establish permanent semantic family labels;
- require PCA/SVD in the implementation;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

STATE SPACE
12 dimensions.

Per-family true generative rank:
3.

Lineage-specific residual SD:
0.08.

Template observation noise SD:
0.03.

PRIMARY FAMILY GEOMETRY
Two related families are constructed from rank-3 subspaces with controlled angular separation.

A third unrelated family is retained in the broader memory accounting,
but the merge decision is evaluated on the candidate pair.

CANDIDATE MERGE
SEPARATE representation:

two rank-3 family bases.

MERGED representation:

one rank-3 shared basis.

A merge saves one family-template overhead:

12-D mean
+
12 x 3 basis

=
48 scalar-equivalent permanent values.

Lineage coefficients remain 3 per lineage in either case.

MEMORY PRICE
Exploratory scalar-equivalent storage price:

0.004 synthetic loss units per stored scalar.

For the two-family 120-lineage comparison,
the saved family-template overhead corresponds to an average merge benefit of approximately:

0.0016 reconstruction-loss units per lineage.

Thus merge if:

held-out reconstruction penalty
<
0.0016.

This threshold is a synthetic working point only.

HELD-OUT MERGE TEST
Each candidate family contributes:

80 fitting lineages

and

80 fresh validation lineages

per decision.

The controller sees:
held-out reconstruction error

not:
true subspace angle.

ANGLE SWEEP
300 matched populations per separation.

MEAN MERGED-MINUS-SEPARATE HELD-OUT MSE
and
fraction of runs in which merge is memory-beneficial.

0 degrees:

penalty:
approximately -0.00015.

merge:
100%.

3 degrees:

0.000025.

merge:
100%.

5 degrees:

0.000338.

merge:
100%.

8 degrees:

0.001099.

merge:
100%.

10 degrees:

0.001800.

merge:
18%.

12 degrees:

0.002656.

merge:
0%.

15 degrees:

0.004227.

merge:
0%.

20 degrees:

0.007599.

merge:
0%.

PRIMARY POSITIVE
A memory-priced held-out reconstruction criterion creates an adaptive merge boundary without semantic lineage-family labels.

Closely related families:
share one basis.

Distinct families:
retain separate bases.

The transition is not infinitely sharp under finite data,
which is appropriate.

At approximately 10 degrees,
the evidence is near the synthetic cost boundary.

GENERAL MERGE RULE
Do not merge because:

the families are both old

or

their labels look similar.

Merge when:

THE FUNCTIONAL / RECONSTRUCTION COST OF SHARING
IS LOWER THAN
THE PERMANENT MEMORY SAVED.

FORCED GLOBAL-MERGE NEGATIVE
H36's unrelated-family stress remains the hard control.

One global rank-3 basis across two genuinely distinct rank-3 families:

MSE:
approximately 0.10216.

Separate family bases:

approximately 0.00470.

Thus memory pressure must not force destructive representational collapse.

SPLIT QUESTION
A family that was once safely merged can later diverge.

H37 tests:

brief novelty

vs

persistent generative separation.

BASELINE
Two families begin at:

8-degree separation.

At this geometry,
merge is consistently memory-beneficial.

FALSE-NOVELTY BURST
After ten stable structural decision blocks,
the apparent separation jumps to:

25 degrees

for only:

2 blocks,

then returns to 8 degrees.

Later,
a real persistent divergence to:

25 degrees

begins and remains for:

8 blocks.

No semantic transition label is given.

SPLIT SIGNAL
At each structural block,
measure:

held-out merged error
-
held-out separate error.

Split evidence is positive when this exceeds the same memory-price threshold:

0.0016.

COMPARATORS
Split after:

1 positive block.

2 consecutive positive blocks.

3.

4.

5.

200 matched synthetic streams.

PERSISTENCE = 1

false split during transient burst:
100%.

The system never reaches the later persistent-divergence test as a merged family.

PERSISTENCE = 2

false split:
100%.

PERSISTENCE = 3

false split:
1%.

persistent divergence correctly split:
99%.

median split latency:
3 blocks.

PERSISTENCE = 4

false split:
0%.

persistent split:
100%.

median latency:
4 blocks.

PERSISTENCE = 5

false split:
0%.

persistent split:
100%.

median latency:
5 blocks.

PRIMARY PERSISTENCE RESULT
A merge/split controller needs hysteresis / persistence.

One or two high residual blocks are not enough to justify permanent family proliferation.

At the tested working point:

4-block persistence

fully rejected the two-block false novelty burst
and
split every genuinely persistent divergence after four blocks.

Do not freeze four blocks.

The principle is:

PERMANENT TEMPLATE-FAMILY GROWTH
SHOULD REQUIRE
PERSISTENT COST-JUSTIFIED MISFIT.

RELATION TO H8-H15
H8-H15 established structural growth/pruning principles:

- permanent capacity has cost;
- novelty must persist;
- correlated noise can create false growth;
- functional consequence must validate structure;
- cheap nomination should not directly authorize permanent state.

H37 applies the same architecture to:

GENERATIVE LINEAGE FAMILY COUNT.

A new template family is itself:
permanent structural capacity.

It therefore requires the same:
cost
+
persistence
+
fit
discipline.

RELATION TO H36
H36:
shared basis compression is powerful when lineages occupy compatible manifolds.

H37:
compatibility should be continuously priced,
not assumed forever.

A family relationship can:
merge
split
and potentially merge again.

Thus template-family identity should be:

REVERSIBLE STRUCTURAL STATE

not:
permanent taxonomy.

CURRENT GENERATIVE-FAMILY LIFECYCLE
NEW RETIRED LINEAGE

->
fit against existing template families

->
if compatible:
join shared family

->
if several families are mutually compatible and memory saving exceeds fit cost:
merge

->
if persistent held-out misfit exceeds saved memory value:
split

->
if misfit is brief:
retain current family and suppress structural reaction.

IMPORTANT FAILURE MODE
Noisy novelty can still trigger template-family proliferation if split persistence is too short.

Therefore family count itself can become a form of:

MEMORY LEAK.

The split gate is a permanent-memory budget control.

DECISION
AR-H37 is POSITIVE.

Supported synthetically:

- family merge can be decided from held-out reconstruction cost versus permanent memory price;
- closely related generative manifolds can share one compact basis;
- distinct manifolds should remain separate;
- merge/split identity can remain non-semantic;
- transient novelty can cause false template proliferation;
- persistence/hysteresis suppresses false splits;
- persistent divergence can trigger bounded family creation.

Not demonstrated:

- real Yggdrasil family-fit metric;
- online basis merge without replaying old lineage data;
- optimal memory price;
- automatic rank adjustment during merge;
- merge after prior split;
- protection against corrupted or malicious lineage updates.

NEXT CLEAN QUESTION
AR-H38 — SHARED TEMPLATE UPDATE POISONING / ROBUST FAMILY MEMORY

Question:

If many lineages share one generative family basis,
what happens when a small number of lineage updates are:
- corrupted;
- badly misfit;
- transiently adversarial;
- or generated from a broken local sensor?

A shared template creates leverage:

ONE BAD UPDATE
CAN POTENTIALLY DAMAGE
MANY RETIRED CAPABILITIES.

Compare:

A.
naive family-basis update from all lineage samples;

B.
fit-gated update admission;

C.
robust residual weighting;

D.
quarantine / provisional lineage state before family write;

E.
persistent legitimate family shift.

Desired:

isolated corrupt lineage
->
local quarantine
without poisoning shared family memory.

persistent population-wide shift
->
eventual family adaptation.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
state_dimensions = 12
family_rank = 3
heldout_lineages_per_family = 80
merge_angle_runs_per_condition = 300
split_streams = 200
memory_price_per_scalar = 0.004
tested_split_persistence = 1,2,3,4,5
