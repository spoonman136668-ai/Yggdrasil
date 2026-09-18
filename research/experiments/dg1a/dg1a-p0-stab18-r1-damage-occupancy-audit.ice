TITLE: DG-1A-P0-STAB-18-R1 — Damage-Occupancy Relation Audit
DATE: 2026-09-18
STATUS: POST-HOC CROSS-CANDIDATE EMPIRICAL AUDIT — NOT A SCIENTIFIC GATE
TRACK: DG-1A
PARENT_CANDIDATE: CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP

PURPOSE
Test whether the repeated observation that lesions improve morphology is systematically related to mature overgrowth across the viable STAB series, and determine what that relation implies for interpreting STAB-18-R1.

THIS RECORD DOES NOT
- alter or execute STAB-18-R1;
- change the frozen 800-cell occupancy ceiling;
- create a new target occupancy;
- establish a causal law;
- authorize parameter tuning;
- treat candidate runs as independent IID samples;
- preregister STAB-19.

DATASET
Measured seed-0 candidate results, common canonical lesion evaluation:

Candidate | pre-lesion active | RelativeDamageEffect
STAB-04   | 1578              | -0.3581909788
STAB-05   | 1206              | -0.2056228929
STAB-07   | 1094              | -0.1497727759
STAB-08   | 1440              | -0.2683228925
STAB-09   | 993               | -0.0469960330
STAB-10   | 1407              | -0.2100049851
STAB-11   | 1252              | -0.1535342344
STAB-12   | 857               | +0.0010864774
STAB-13   | 1193              | -0.1305462783
STAB-14   | 1097              | -0.0852672125
STAB-16   | 1082              | -0.0768766287
STAB-17   | 1038              | -0.1224298101

EXCLUDED FROM VIABLE FIT
STAB-06:
- pre-lesion active = 3
- RelativeDamageEffect = +0.0062380726
- known near-dead sparse-target degeneracy

STAB-15:
- pre-lesion hidden life = 1
- RelativeDamageEffect = +0.0095902033
- known LIFE4-collapse degeneracy

These two results remain important negative knowledge, but they are not samples of the viable mature-phenotype regime being tested here.

FULL VIABLE SERIES — STAB-04 THROUGH STAB-17
n = 12

Pearson correlation:
r = -0.9491605169

Spearman rank correlation:
rho = -0.9440559441

Ordinary least-squares descriptive fit:
RelativeDamageEffect =
0.3917388832
- 0.0004570728 * PreLesionActiveCells

OLS zero crossing:
approximately 857.06 active cells

Theil-Sen robust slope:
-0.0004385136 RelativeDamageEffect per active cell

Theil-Sen slope interval from the computational diagnostic:
[-0.0005593723, -0.0003643274]

IMPORTANT STATISTICAL BOUNDARY
The nominal correlation p-values from an IID regression are NOT treated as confirmatory evidence because:
- candidates share architecture lineage;
- candidates share seed 0;
- mechanisms were chosen sequentially using prior results;
- observations are therefore neither randomized nor independent.

The correlation coefficients are used only as descriptive effect-size diagnostics.

NESTED-WINDOW STABILITY
The relation remains strong when progressively earlier candidates are excluded.

STAB-10 through STAB-17, excluding collapsed STAB-15:
- n = 7
- Pearson r = -0.94854
- Spearman rho = -0.89286
- OLS zero crossing = 825.52 cells

STAB-07 through STAB-17, excluding collapsed STAB-15:
- n = 10
- Pearson r = -0.93988
- Spearman rho = -0.91515
- OLS zero crossing = 838.97 cells

STAB-04 through STAB-17, excluding STAB-06 and STAB-15:
- n = 12
- Pearson r = -0.94916
- Spearman rho = -0.94406
- OLS zero crossing = 857.06 cells

LEAVE-ONE-CANDIDATE-OUT STABILITY
Across the 12 viable candidates:
- minimum OLS zero crossing after dropping one candidate: 834.42
- maximum: 875.29
- mean: 856.19
- standard deviation: 11.50 cells
- leave-one-out Pearson r range: approximately -0.959 to -0.921

Interpretation:
The occupancy/lesion-sign relation is not being driven by one obvious candidate.

CRITICAL OBSERVATION
STAB-12 sits almost exactly at the descriptive zero crossing:
- pre-lesion active = 857
- observed RelativeDamageEffect = +0.001086
- full-series fit prediction at 857 = +0.0000275

STAB-12 is also the best canonical candidate by gate count:
5 / 14 failed.

This is a striking convergence, but it remains post-hoc.

MECHANISTIC INTERPRETATION
Across the viable P0 stabilization series, severe overgrowth predicts a lesion that improves visible morphology.

This supports a consistent interpretation:
- the mature organism carries excess support that is not merely unnecessary;
- enough of that support degrades the visible phenotype that broad lesioning can improve the evaluation metric;
- reducing overgrowth tends to move lesion response from beneficial toward neutral.

The pattern explains why STAB-12 was directionally important:
it moved occupancy near the current bounded regime and simultaneously moved DamageEffect to approximately neutral.

However, NEUTRAL lesion response is not the canonical goal.

The required RelativeDamageEffect is >= +0.10.
STAB-12 at 857 cells achieved only +0.0011.

Therefore occupancy reduction alone is unlikely to solve the full regeneration problem.

The remaining support must become FUNCTIONALLY NECESSARY:
removing a substantial fraction of the mature organism should measurably worsen visible morphology before recovery can be meaningfully assessed.

RELATION TO STAB-18-R1
This strengthens the rationale for causal latent-support testing.

R1 is not merely asking:
Can we reduce LIFE4 count?

The stronger question is:
Can causal pruning change the quality of the surviving LIFE4 population so that lower occupancy is accompanied by increased functional dependence of visible morphology on that population?

NON-GATING RESIDUAL DIAGNOSTIC
After R1 executes, its observed RelativeDamageEffect can be compared descriptively with the historical occupancy relation at its measured pre-lesion LIFE4 count.

Interpretation only:
- R1 near the historical line:
  lesion response changed mostly as expected from occupancy reduction alone.
- R1 materially above the historical line:
  evidence that surviving latent support became more functionally coupled than historical candidates with similar occupancy.
- R1 materially below the historical line:
  evidence that pruning damaged useful coupling or that the global group intervention selected poorly.

This residual is NOT a scientific gate and must not alter the 14 preregistered gates.

NO NEW OCCUPANCY TARGET
The descriptive OLS line predicts zero RelativeDamageEffect near 857 cells and a small positive value near 800.

This does NOT justify:
- changing the frozen 800 ceiling;
- choosing 857 as a new ceiling;
- extrapolating a cell-count target for RelativeDamageEffect >= 0.10;
- tuning R1 toward the fitted line.

There are no viable measured candidates between 857 and 993 cells except STAB-12 at the lower endpoint, so the crossing region is interpolated rather than densely observed.

CONNECTION TO INJURY-RECRUITMENT AUDIT
The damage-occupancy relation and the injury-recruitment gap describe different failure axes:

RESOURCE ECONOMY
Too much mature support correlates strongly with lesions improving morphology.

REPAIR-STATE RESPONSE
After LIFE4 decoupling, STAB-16/17 restored only a small fraction of removed hidden life because the fixed viability floor remained inactive after injury.

A successful architecture may therefore need both:
1. economical, causally useful maintenance support;
2. damage-conditioned temporary recruitment followed by contraction.

R1 addresses axis 1 first.
It should remain frozen.

CONCLUSION
The STAB-04..17 negative series now supports a coherent empirical progression:

OVERGROWTH
-> lesion removes harmful/excess support
-> damage appears beneficial

BOUNDED OCCUPANCY
-> lesion effect approaches neutral

FUNCTIONALLY COUPLED SUPPORT
-> required next transition
-> lesion should become meaningfully harmful
-> only then is regeneration a valid scientific measurement

This audit elevates lesion salience from a downstream pass/fail metric to a mechanistic diagnostic of whether the organism's maintained cellular substrate is actually necessary to its phenotype.

PROVENANCE
evidence_class = POST_HOC_CROSS_CANDIDATE_ANALYSIS
new_training_run = false
canonical_scientific_execution = false
source_results = measured STAB-04..17 result records
