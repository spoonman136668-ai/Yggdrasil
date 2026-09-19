TITLE: DG-1A-AR-H1 — Heritable Micro-Genome Timescale Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE-BUT-CONDITIONAL INHERITANCE AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arc4-dynamic-sensor-lineage-audit.ice

PURPOSE
Test when a tiny heritable modulation vector provides real adaptive value versus:
- a globally optimized fixed generalist;
- equal-variance non-heritable variation.

Primary question:
WHEN DOES INTERGENERATIONAL MEMORY HELP?

This is the first explicit slow-timescale inheritance audit.

BOUNDARY
This is synthetic.

It does not:
- evolve Yggdrasil network weights;
- allocate real micro-genome channels;
- alter or execute STAB-18-R1;
- claim useful heritable adaptation in a real NCA;
- authorize unbounded self-modification.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

MICRO-GENOME
Four bounded scalar modulation dimensions.

Conceptually they correspond to future candidate sensitivities such as:
- growth responsiveness;
- relay responsiveness;
- inhibitor/repair responsiveness;
- dormancy/resource responsiveness.

No per-cell neural network is evolved.

The shared developmental engine remains conceptually fixed.

ENVIRONMENTAL REGIMES
Six synthetic regime optima in the four-dimensional modulation space.

Each regime requires a different useful sensitivity profile.

GLOBAL GENERALIST
The fixed control uses the exact mean optimum across the six regimes.

Under squared-error loss and equal regime frequency,
this is the globally optimal single fixed vector.

Therefore the inheritance candidate is NOT being compared against an arbitrary weak baseline.

POPULATION
256 synthetic cells/lineages.

Generations:
600

Burn-in:
100

Selection:
fitness decreases exponentially with mean squared distance from current regime optimum.

Selection strength:
18.

Offspring inherit parent micro-genome plus bounded Gaussian mutation.

PRIMARY HERITABLE MUTATION SWEEP
mutation sigma tested:

0.005
0.010
0.020
0.040
0.080

ENVIRONMENTAL PERSISTENCE
At each generation:
remain in same regime with probability p_stay.

If switching:
choose another regime uniformly.

p_stay tested:

0.00
0.25
0.50
0.75
0.90
0.97
0.99

Approximate mean regime dwell:

p=0.00:
1 generation

p=0.25:
1.33 generations

p=0.50:
2 generations

p=0.75:
4 generations

p=0.90:
10 generations

p=0.97:
33.3 generations

p=0.99:
100 generations

SEEDS
8 matched synthetic seeds per condition.

PRIMARY CONTROL 1 — FIXED GENERALIST
Every cell always uses the globally optimal fixed generalist vector.

PRIMARY CONTROL 2 — NON-HERITABLE VARIATION
Every generation:
sample the same-size population around the fixed generalist.

Variation is not inherited.

Mutation/variation sigma is swept over the same candidate set.

This control asks:
is benefit caused merely by having a diverse population,
or specifically by carrying information across generations?

BEST HERITABLE RESULTS

p_stay  best_sigma  inherited_loss  fixed_loss  inheritance_vs_fixed

0.00    0.005       0.050992        0.048771    -4.55%
0.25    0.005       0.050895        0.048828    -4.23%
0.50    0.005       0.050148        0.048627    -3.13%
0.75    0.005       0.049153        0.048478    -1.39%
0.90    0.040       0.044392        0.048824    +9.08%
0.97    0.040       0.025196        0.046958    +46.34%
0.99    0.040       0.019382        0.051122    +62.09%

Interpretation:
positive percentages mean lower loss than the fixed generalist.

NON-HERITABLE CONTROL
The best non-heritable variation control selected:
sigma = 0.005
throughout this sweep.

Its loss stayed essentially equal to the fixed generalist.

Inherited improvement versus best non-heritable control:

p=0.00:
-4.50%

p=0.25:
-4.18%

p=0.50:
-3.07%

p=0.75:
-1.34%

p=0.90:
+9.13%

p=0.97:
+46.37%

p=0.99:
+62.11%

PRIMARY RESULT
VARIATION ALONE IS NOT THE ADVANTAGE.

The large benefit appears only when useful state persists across generations.

Inheritance becomes useful when environmental persistence exceeds the adaptation lag of the lineage.

FAST ENVIRONMENT NEGATIVE
When regimes switch every 1..4 generations,
inheritance is slightly WORSE than the globally optimized fixed generalist.

Reason:
the lineage retains information about an environment that has already changed.

This is evolutionary/adaptive lag.

Therefore:
HERITABILITY IS NOT MONOTONICALLY GOOD.

MUTATION LOAD / EXPLORATION TRADE
Selected inherited losses:

p_stay = 0.97

sigma 0.005:
0.042748

sigma 0.010:
0.035768

sigma 0.020:
0.026930

sigma 0.040:
0.025196

sigma 0.080:
0.032171

There is an interior optimum.

Too little mutation:
lineage adapts too slowly.

Too much mutation:
offspring lose useful accumulated information.

This is the classic:
exploration
vs
inheritance fidelity

trade-off in the synthetic model.

PARTIAL-INHERITANCE / FORGETTING AUDIT
A second experiment introduces inheritance strength h:

offspring =
generalist
+
h * (parent - generalist)
+
mutation

h = 0:
no intergenerational memory.

h = 1:
full parent deviation inheritance.

mutation sigma fixed:
0.040

h tested:
0
0.25
0.50
0.75
0.90
1.00

RESULTS

p_stay = 0.75
h=0.00:
0.050093

h=0.75:
0.049087

h=0.90:
0.048858

h=1.00:
0.055610

At short/moderate persistence:
full inheritance is actively harmful.
A strong but decaying memory is safer.

p_stay = 0.90
h=0.00:
0.050432

h=0.75:
0.047210

h=0.90:
0.042037

h=1.00:
0.044392

At approximately 10-generation dwell:
partial inheritance h=0.90 outperforms full inheritance.

p_stay = 0.97
h=0.00:
0.048578

h=0.90:
0.032202

h=1.00:
0.025196

At approximately 33-generation dwell:
full inheritance is better.

p_stay = 0.99
h=0.00:
0.052717

h=0.90:
0.031493

h=1.00:
0.019382

At approximately 100-generation dwell:
full inheritance is strongly favored.

SECOND PRIMARY RESULT
The best inheritance timescale should track environmental persistence.

A single permanent inheritance strength is unlikely to be optimal across all regimes.

ARCHITECTURAL CONSEQUENCE
Do not define the future micro-genome as:
permanent immutable daughter copy
plus random mutation.

Prefer a bounded slow state with THREE mechanisms:

1. INHERITANCE
carry useful parent modulation forward.

2. MUTATION / VARIATION
explore nearby developmental biases.

3. RELAXATION / FORGETTING
decay inherited deviation toward a stable shared prior when evidence no longer supports it.

Conceptually:

g_child =
g_prior
+
h * (g_parent - g_prior)
+
bounded_mutation

where h may itself be:
- globally fixed initially;
- later modulated by confidence/environmental persistence.

Do not meta-adapt h yet.

HARD SAFETY / STABILITY BOUND
The micro-genome should modulate:
- thresholds;
- sensitivities;
- local gains;
- plasticity rates;

not replace the shared update network.

This preserves the central developmental bottleneck:

ONE SHARED ENGINE
+
TINY HERITABLE MODULATION.

COMMON-MODE FAILURE CONNECTION
C4 showed that lineage duplication does not create independent sensor evidence.

H1 adds:
a lineage can also preserve a BAD developmental bias after the environment changes.

Therefore inheritance must carry:
useful memory
without turning lineage continuity into unquestioned authority.

Confidence/freshness from U11-U13 becomes relevant here.

Potential future rule:

low novelty
+
stable consequence improvement
->
retain inherited bias

high sustained novelty
or
persistent local consequence deterioration
->
increase relaxation / exploration.

This is a hypothesis only.

Do not implement yet.

LITERATURE ALIGNMENT
Meta-Learning an Evolvable Developmental Encoding
arXiv:2406.09020

demonstrates that meta-learning can produce an evolvable NCA developmental encoding in which cells read different parts of a compact genome to grow different structures.

Learning to acquire novel cognitive tasks with evolution, plasticity and meta-meta-learning
ICML 2023

shows that evolution can shape plastic systems that acquire new tasks during their lifetime.

2025 work on developmental plasticity and developmental bias also supports treating plasticity and inherited developmental structure as coupled rather than independent phenomena.

These are plausibility anchors only.

CURRENT YGGDRASIL RESULT
The measured synthetic result supports:

bounded heritable modulation
CAN add value

when:
environmental/task structure persists long enough.

It also supports an equally important negative:

heritable state CAN REDUCE performance
when conditions change faster than the inherited adaptation timescale.

NEXT
AR-H2 — HERITABILITY UNDER LOCAL NICHE STRUCTURE

The current H1 environment is global.

Real Yggdrasil cells occupy different spatial niches.

Test:
- stable local niches;
- moving niche boundaries;
- lineage migration;
- injury-created temporary niches;
- inherited bias vs local role utility.

Question:
can tiny inherited modulation accelerate local specialization
without preventing cells from changing function when they move or the niche disappears?

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
population = 256
generations = 600
burn_in = 100
seeds_per_condition = 8
micro_genome_dimensions = 4
