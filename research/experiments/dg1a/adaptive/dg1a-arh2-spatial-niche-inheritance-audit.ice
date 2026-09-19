TITLE: DG-1A-AR-H2 — Spatial Niche Inheritance / Canalization Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE-BUT-CANALIZED NICHE AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh1-heritable-microgenome-timescale-audit.ice

PURPOSE
Extend H1 from one global environment to spatially distinct local niches.

Question:
Can inherited micro-genome bias accelerate local specialization without preventing cells from adapting when:
- lineages migrate;
- niche boundaries move;
- or a former niche disappears?

BOUNDARY
This is synthetic.

It does not:
- implement lineage inheritance in Yggdrasil;
- evolve neural-network weights;
- alter or execute STAB-18-R1;
- prove that spatial niches correspond to future Yggdrasil roles.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SPATIAL BODY
1D periodic local-reproduction lattice.

Cells:
192

Local parent neighborhood:
radius 2

Each offspring selects a parent from:
self +/- 2 positions

based on local fitness.

Generations:
260

Niche change:
generation 130

MICRO-GENOME
Four bounded modulation dimensions.

Two local niche optima:

NICHE A
[0.8, 0.2, 0.2, 0.1]

NICHE B
[0.2, 0.25, 0.8, 0.15]

Global prior/generalist:
mean(A,B).

Mutation sigma:
0.03

Selection strength:
20.

SEEDS
Primary table:
6 seeds per condition.

Recovery-latency confirmation:
12 seeds.

INHERITANCE STRENGTH
h tested:

0.00
0.50
0.75
0.90
1.00

Offspring:

g_child =
g_prior
+
h * (g_parent - g_prior)
+
bounded mutation.

h=0:
no heritable deviation.

h=1:
full inherited deviation.

INITIAL NICHE MAP
First half of lattice:
A

Second half:
B

This allows lineage-local specialization.

SCENARIO 1 — BOUNDARY SHIFT
At generation 130:
rotate the A/B boundary by 48 cells.

This changes niche for part of the population while preserving both niche types.

STEADY PRE-SHIFT LOSS

h=0.00:
0.046196

h=0.50:
0.045691

h=0.75:
0.043847

h=0.90:
0.035658

h=1.00:
0.012544

Full inheritance creates much deeper local specialization.

IMMEDIATE POST-SHIFT LOSS
mean first 15 post-change generations:

h=0.00:
0.046213

h=0.50:
0.045804

h=0.75:
0.044708

h=0.90:
0.042526

h=1.00:
0.058264

Full inheritance becomes temporarily worse than several weaker-inheritance populations immediately after niche displacement.

LATE POST-SHIFT LOSS

h=0.00:
0.046200

h=0.50:
0.045701

h=0.75:
0.043929

h=0.90:
0.035591

h=1.00:
0.013220

Given enough time,
full inheritance reconstructs deep niche specialization.

RECOVERY LATENCY
criterion:
return to within 10% of each seed's pre-shift loss
for 10 consecutive generations.

12-seed confirmation:

h=0.75:
median 0 generations
12/12 recovered

h=0.90:
median 11 generations
12/12 recovered

h=1.00:
median 69 generations among recovered
8/12 recovered within the 130-generation post-change horizon.

PRIMARY RESULT
Deep inheritance produces:
better specialization
but
slower niche reassignment.

SCENARIO 2 — FULL NICHE SWAP
At generation 130:
every A site becomes B
and
every B site becomes A.

This is the strongest migration/canalization stress.

PRE-SWAP LOSS

h=0.75:
0.043847

h=0.90:
0.035658

h=1.00:
0.012544

IMMEDIATE POST-SWAP LOSS

h=0.75:
0.045406

h=0.90:
0.048573

h=1.00:
0.108151

Full inheritance suffers an approximately 8.6x increase relative to its own prior loss.

LATE POST-SWAP LOSS

h=0.75:
0.043835

h=0.90:
0.035494

h=1.00:
0.013585

RECOVERY LATENCY
12-seed confirmation:

h=0.75:
median 2 generations
12/12 recovered

h=0.90:
median 16.5 generations
12/12 recovered

h=1.00:
median 99 generations among recovered
7/12 recovered within horizon.

This is the clearest CANALIZATION result.

SCENARIO 3 — NICHE COLLAPSE
At generation 130:
all positions become niche A.

This tests whether old B-specialized lineage memory can be retired when a niche disappears entirely.

IMMEDIATE POST-COLLAPSE LOSS

h=0.75:
0.044520

h=0.90:
0.041641

h=1.00:
0.058132

LATE LOSS

h=0.75:
0.043692

h=0.90:
0.034667

h=1.00:
0.011060

RECOVERY LATENCY
12-seed confirmation:

h=0.75:
median 0

h=0.90:
median 9.5

h=1.00:
median 32

all listed conditions:
12/12 recovery.

INTERPRETATION
Full inheritance is excellent when:
- local niches remain stable;
- lineages stay in compatible locations;
- specialization has time to mature.

Full inheritance is costly when:
- niche identity moves faster than lineage re-adaptation;
- descendants enter a different local functional demand;
- a strong inherited bias becomes temporarily wrong.

This is developmental canalization.

PARETO FRONTIER
There is no single best h.

Higher h:
- lowers long-run local mismatch;
- increases short-term relocation shock;
- lengthens functional reassignment.

Lower h:
- preserves reversibility;
- limits achievable specialization depth.

Therefore future inheritance should be evaluated on BOTH:

SPECIALIZATION QUALITY

and

REASSIGNMENT LATENCY.

Do not optimize only steady-state fitness.

INTEGRATION WITH AR-U2
AR-U2 showed that non-heritable soft role state can relocate in about 60 synthetic steps after demand moves.

H2 shows that a slow inherited bias can either:
- accelerate reacquisition of a stable niche;
or
- resist role relocation if it is too strong.

Therefore the layers should not be collapsed.

Preferred conceptual ordering:

HERITABLE MICRO-GENOME
biases propensity

FAST SOFT ROLE STATE
expresses current local function

LOCAL UTILITY / CONSEQUENCE
can override obsolete inherited bias.

This gives:

inheritance as prior

not:

inheritance as command.

DESIGN CONSEQUENCE
A daughter should inherit:
a bias toward a function

not:
an irreversible role identity.

Potential future form:

effective_role_drive =
local_utility
+
bounded_inherited_bias

with:
- capped inherited influence;
- relaxation;
- confidence-dependent forgetting.

Do not implement coefficients yet.

COMMON-MODE FAILURE CONNECTION
If an entire lineage inherits the same wrong bias,
many descendants can fail together.

Therefore:
lineage expansion
does not create independent adaptive evidence.

This matches C4 sensor provenance.

HERITABLE diversity must not be counted as functional redundancy unless descendants actually decorrelate in consequence/error behavior.

NEXT
AR-H3 — INHERITED PRIOR + FAST LOCAL UTILITY

Directly combine:
- slow inherited micro-genome bias;
- fast utility-driven soft role state.

Test whether:
1. stable niches specialize faster than utility-only control;
2. moved niches still recover near utility-only speed;
3. inherited bias does not override strong contradictory local evidence;
4. useful lineage memory survives temporary noise but retires under sustained mismatch.

This is the decisive integration test for the proposed:
slow prior
+
fast role
architecture.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
cells = 192
generations = 260
primary_seeds = 6
latency_confirmation_seeds = 12
micro_genome_dimensions = 4
