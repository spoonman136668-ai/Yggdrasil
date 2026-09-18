TITLE: DG-1A-P0-STAB-18-R1 — Injury-Recruitment Gap Audit
DATE: 2026-09-18
STATUS: POST-HOC COMPARATIVE MECHANISTIC AUDIT — NOT A NEW CANDIDATE RESULT
TRACK: DG-1A
PARENT_CANDIDATE: CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP

PURPOSE
Determine whether the STAB-15/16 architectural decoupling of hidden liveness from visible alpha introduced a second failure mode beyond redundant latent overgrowth: loss of damage-conditioned recruitment.

THIS RECORD DOES NOT
- alter or execute STAB-18-R1;
- change any frozen scientific gate;
- authorize tuning;
- establish a wound-response mechanism;
- preregister STAB-19.

MEASURED SOURCE RESULTS
STAB-12 result SHA:
fbee4a1108070f404bee260758318e2bfb13273e

STAB-16 result SHA:
52e772e7b21d61e1c5ed333d05740929e31b4a10

STAB-17 result SHA:
06e8146f26b661c5c9e315b79c05d3e5c217e129

REFERENCE ARCHITECTURAL DIFFERENCE
STAB-12 used the pre-decoupling alpha-linked life regime.
STAB-16 and STAB-17 used dedicated hidden LIFE4 liveness plus:
- FRONTIER-FLOOR-113 as a positive minimum-viability signal;
- CEIL-800 as a one-sided upper occupancy signal;
- ATTRACT-16 for visible target-state dynamics.

FRONTIER-FLOOR-113 is exactly zero whenever hidden-life count is >=113.

MEASURED LESION / RECOVERY POPULATION RESPONSE
Candidate | pre-lesion life | post-lesion life | removed | final life | regrown | fraction of removed restored
STAB-12   | 857             | 435              | 422     | 655        | 220     | 52.13%
STAB-16   | 1082            | 795              | 287     | 797        | 2       | 0.70%
STAB-17   | 1038            | 650              | 388     | 681        | 31      | 7.99%

Population growth from immediate post-lesion state:
- STAB-12: +50.57%
- STAB-16: +0.25%
- STAB-17: +4.77%

KEY CONTROL-LOGIC OBSERVATION
Immediate post-lesion hidden-life counts were:
- STAB-16: 795
- STAB-17: 650

Both are far above the FRONTIER-FLOOR-113 activation threshold.
Therefore the explicit positive viability mechanism is silent throughout the immediate canonical recovery starting condition.

STAB-16 begins recovery only five cells below the CEIL-800 boundary.
STAB-17 begins 150 cells below it.

The fixed deadband therefore does not encode:
- amount of tissue just lost;
- local wound location;
- need for temporary repair capacity;
- need to reconstitute a particular latent role;
- transition from maintenance mode into repair mode.

VISIBLE MORPHOLOGY RESPONSE
Candidate | pre MSE | post-lesion MSE | final recovery MSE | lesion change | post->final improvement
STAB-12   | 0.0456747562 | 0.0457243808 | 0.0318049565 | +0.11% worse | 30.44% improvement
STAB-16   | 0.0673088878 | 0.0621344075 | 0.0442852266 | -7.69% better | 28.73% improvement
STAB-17   | 0.0655461326 | 0.0575213321 | 0.0569460019 | -12.24% better | 1.00% improvement

INTERPRETATION
STAB-16 and STAB-17 contain two simultaneous signals:

1. REDUNDANT / NEGATIVELY COUPLED BULK
The lesion immediately improves visible morphology in both decoupled LIFE4 candidates.
This supports the existing R1 hypothesis that some mature latent support is redundant or harmful to the visible phenotype.

2. LOST DAMAGE-CONDITIONED RECRUITMENT
After losing 287 hidden-life cells, STAB-16 restores only 2.
After losing 388, STAB-17 restores only 31.
This is qualitatively different from STAB-12, which restores 220 of 422 removed active cells.

The decoupled system therefore does not presently behave like a latent reserve that is actively recruited by injury.

STAB-16'S SPECIAL CASE
STAB-16 improves visible MSE by another 28.73% after the lesion while regrowing only 2 cells.

This means its visible correction is not driven by bulk life replacement.
The more plausible interpretation is reorganization/contraction of surviving state toward a better visible attractor.

This strengthens, rather than weakens, the redundant-bulk hypothesis, but also shows that cardinality restoration and morphology restoration are distinct control problems.

STAB-17'S SPECIAL CASE
STAB-17 has:
- strong immediate lesion improvement;
- modest LIFE4 regrowth;
- only 1% post-lesion visible improvement.

The visible-anchor mechanism therefore does not restore an effective damage response even though almost all mature LIFE4 cells are geometrically adjacent to visible alpha.

CONTROL-SEAM CONCLUSION
The current architecture has a maintenance deadband but no explicit repair-state transition.

A robust developmental substrate may require two different resource regimes:
MAINTENANCE:
- bounded, economical, potentially synergy-dominant latent support.

REPAIR:
- injury-triggered local recruitment / temporary redundancy;
- followed by contraction back toward economical maintenance.

This is consistent with recent GNCA evidence reporting increased redundancy during recovery and spatially differentiated repair information flow, but the Yggdrasil result is presently only a mechanistic hypothesis.

RELATION TO STAB-18-R1
Do not alter R1.

R1 still answers an essential prior question:
Can causal pressure remove redundant mature LIFE4 support without destroying useful morphology?

However, even a successful R1 occupancy result may leave recovery invalid if the architecture still lacks damage-conditioned recruitment.

EXPECTED RESULT BRANCHES
A. R1 reduces occupancy and improves morphology, but recovery remains invalid:
   strongest next seam = injury-conditioned latent recruitment.

B. R1 causes collapse/regression under strong prune pressure:
   strongest next seam = localized causal attribution before any repair controller.

C. R1 shows mostly positive causal deltas and little prune pressure:
   latent support is broadly useful under the global intervention; investigate dynamic maintenance-vs-repair role switching rather than bulk pruning.

D. R1 improves occupancy, morphology, and valid recovery:
   do not introduce a wound controller; replicate the simpler mechanism first.

PROSPECTIVE MECHANISM CLASS — NOT YET PREREGISTERED
If branch A is observed, the next mechanism should NOT be a lower global floor or looser ceiling.

A scientifically discriminating repair signal should be:
- damage-conditioned;
- local or locally propagating;
- target-geometry-free;
- inactive in undamaged maintenance;
- able to temporarily license latent recruitment after injury;
- followed by autonomous contraction after repair.

A temporal wound signal based on sudden local visible-state loss is conceptually cleaner than a static occupancy threshold because ordinary external background is persistently absent while a wound represents a state change.

No implementation or coefficient is selected here.

LITERATURE CONTEXT
Canonical Growing Neural Cellular Automata uses alpha as the living-cell marker, directly coupling visible morphology and liveness.
Recent 2026 GNCA self-maintenance analysis reports that damage induces a collective-state displacement, spatially differentiated repair flow, and a shift from synergy-dominant resting dynamics toward redundancy-enhanced recovery.

These observations support investigating state-dependent repair dynamics but do not establish Yggdrasil equivalence.

NO POST-HOC TUNING
The canonical STAB-18-R1 candidate, seed, 200-iteration budget, causal fraction, horizon, coefficient, floor, ceiling, hidden L2, and 14 gates remain frozen.

PROVENANCE
evidence_class = CROSS_CANDIDATE_MEASURED_RESULT_ANALYSIS
canonical_scientific_execution = false
new_training_run = false


BROAD PRE-DECOUPLING RECOVERY BASELINE
The initial audit used STAB-12 as the closest near-bound architectural reference.
A wider post-hoc check now includes all viable pre-LIFE4 stabilization candidates with comparable lesion population telemetry from STAB-07 through STAB-14.

Candidate | removed cells | post-lesion regrowth | fraction of removed population restored
STAB-07   | 524           | 662                   | 126.34%
STAB-08   | 576           | 231                   | 40.10%
STAB-09   | 482           | 882                   | 182.99%
STAB-10   | 576           | 508                   | 88.19%
STAB-11   | 551           | 181                   | 32.85%
STAB-12   | 422           | 220                   | 52.13%
STAB-13   | 552           | 798                   | 144.57%
STAB-14   | 484           | 465                   | 96.07%

Pre-decoupling summary:
- mean fraction restored = 95.41%
- median fraction restored = 92.13%
- observed range = 32.85% to 182.99%

Decoupled LIFE4:
STAB-16:
- removed = 287
- regrown = 2
- fraction restored = 0.70%

STAB-17:
- removed = 388
- regrown = 31
- fraction restored = 7.99%

Decoupled mean/median fraction restored:
4.34%

Ratio:
decoupled median / pre-decoupling median = approximately 0.0471.

Equivalently, the typical removed-population restoration response is roughly twenty-one times smaller after LIFE4 decoupling in this historical series.

INTERPRETATION OF THE WIDER BASELINE
The low STAB-16/17 recruitment response is not explained by selecting STAB-12 as an unusually regenerative comparator.

Every viable pre-decoupling candidate in STAB-07..14 restored at least 32.85% of the removed population.
Both decoupled candidates are far below that historical range.

The pre-decoupling candidates often over-regrew and were scientifically unsuccessful, so greater regrowth is NOT itself a desirable outcome.
What changes sharply after decoupling is the existence of a strong population response to injury.

This strengthens the architectural hypothesis:
visible-alpha/liveness coupling carried an implicit lesion-responsive growth signal.
LIFE4 decoupling removed that incidental coupling.
FRONTIER-FLOOR-113 restored baseline viability, but because it is a static minimum-population mechanism, it did not restore damage-conditioned recruitment when post-lesion LIFE4 remained above 113.

This remains observational across sequential seed-0 candidates and is not a randomized architectural ablation.
