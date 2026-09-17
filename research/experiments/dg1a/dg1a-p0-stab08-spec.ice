TITLE: DG-1A-P0-STAB-08 — Graded Immutable Target-Distance Occupancy Control
DATE: 2026-09-17
STATUS: PREREGISTERED EXPLORATORY ABLATION
TRACK: DG-1A
CONFIDENCE: PLAUSIBLE

QUESTION
Can canonical P0 preserve meaningful target viability while bounding excess support if target-background occupancy pressure is graded continuously by immutable distance from the target instead of applied uniformly or exempted by a binary halo?

MOTIVATION
The full-grid canonical P0 objective is experimentally bracketed:

STAB-05 OCC-A1
- continuous alpha-energy pressure on every target-background cell;
- pre-damage active cells: 1206 / 1600;
- pre-lesion global MSE: 0.0701904967;
- remained overgrown and expansive.

STAB-06 AM-05
- strong threshold-aligned background occupancy pressure;
- pre-damage active cells: 3 / 1600;
- final recovery active cells: 0;
- crossed into near-death.

STAB-07 HALO-1
- one target-derived 3 x 3 support halo fully exempted from dedicated alpha pressure;
- pre-damage active cells: 1094 / 1600;
- pre-lesion global MSE: 0.0625592172;
- final recovery active cells: 1232 / 1600;
- persistence final active cells: 1276 / 1600;
- restored robust viability but remained overgrown.

The binary STAB-07 support exemption materially changed viability, establishing that spatial support semantics matter. It did not bound support. The next discriminating experiment therefore removes the binary exempt/penalized boundary and replaces it with a deterministic graded target-distance field.

LOCALITY BASIS
The repository NCA update rule uses a local 3 x 3 neighborhood and alpha-based liveness. Growing Neural Cellular Automata likewise treats alpha > 0.1 as mature/alive and permits neighboring cells to participate in continued growth.

References:
- Mordvintsev, Randazzo, Niklasson, Levin. Growing Neural Cellular Automata. Distill, 2020.
- Adversarial Reprogramming of Neural Cellular Automata. Distill, 2021.

CANDIDATE
DIST-1

TARGET FOREGROUND
ForegroundMask = target alpha > 0.1

IMMUTABLE SUPPORT DISTANCE
For every grid cell, define d as Chebyshev distance to the nearest target-foreground cell.

- target foreground cells have d = 0;
- immediate 3 x 3-neighborhood support ring has d = 1;
- subsequent square-neighborhood rings have d = 2, 3, ...;
- d is derived only from the immutable target;
- phenotype state may not alter the distance field.

For the frozen 40 x 40 radius-6 disk target:
- foreground cells d=0: 113
- d=1: 56
- d=2: 64
- d=3: 72
- d=4: 80
- d=5: 88
- d=6: 96
- d=7: 104
- d=8: 112
- d=9: 120
- d=10: 128
- d=11: 136
- d=12: 144
- d=13: 152
- d=14: 102
- d=15: 28
- d=16: 5
Total background cells: 1487.

GRADED OCCUPANCY WEIGHT
For background cells only:

DistanceWeight(d) = d / (d + 1)

Therefore:
- d=1 -> 0.500000
- d=2 -> 0.666667
- d=3 -> 0.750000
- d=4 -> 0.800000
- d=8 -> 0.888889
- d=16 -> 0.941176

The function contains no learned or swept parameter.
There is no support-radius parameter.
There is no distance cap.
There is no coefficient schedule.
The weight is monotonic, bounded in (0, 1), and approaches the STAB-05 all-background pressure with distance.

For the frozen target, mean DistanceWeight over all background cells is approximately 0.8635463277.

GRADED BACKGROUND ALPHA TERM
GradedBackgroundAlphaMSE =
    mean(
        DistanceWeight(d) * state_alpha^2
        over target-background cells
    )

Foreground cells are excluded from this dedicated term.
The unchanged global visible loss continues to evaluate every grid cell.

TRAINING OBJECTIVE
TrainingMorphologyLoss =
    GlobalVisibleMSE
    + 1.0 * ForegroundVisibleMSE
    + 1.0 * GradedBackgroundAlphaMSE

Total training loss remains:
TrainingLoss = TrainingMorphologyLoss + existing hidden-state L2 term.

The STAB-06 BackgroundAliveMarginLoss term is NOT retained.
The STAB-07 binary halo exemption is NOT retained.
The STAB-05 uniform all-background alpha weight is NOT retained.

SINGLE-FACTOR CONTRACT
Relative to STAB-05, the scientific change is immutable spatial weighting of the same continuous alpha-energy pressure.

Relative to STAB-07, the scientific change is replacing binary one-cell exemption with a continuous target-distance weighting that partially penalizes near-target support and increasingly penalizes distant support.

This is not a coefficient sweep or halo-radius sweep.

Do not change:
- foreground coefficient;
- graded occupancy coefficient;
- distance weighting function;
- target foreground threshold;
- alive threshold;
- model architecture;
- optimizer;
- training iterations;
- learning rate;
- development-step range;
- state pool;
- training-damage probability or geometry;
- training maturity threshold;
- gradient clipping;
- hidden-state L2 weight;
- target;
- evaluation horizon;
- evaluation lesion;
- common global evaluation metric.

DEAD-STATE SANITY
For an all-zero phenotype:
- GradedBackgroundAlphaMSE = 0.0;
- GlobalVisibleMSE remains approximately 0.02957421875;
- ForegroundVisibleMSE remains approximately 0.41875;
- composite morphology loss remains approximately 0.44832421875.

Therefore DIST-1 does not make the all-dead phenotype cheaper than the foreground-protected STAB-04/05/07 family through its new term.

MEANINGFUL VIABILITY FLOOR
Retain the target-derived floor frozen in STAB-07:
- pre-damage active cells >= 113;
- final recovery active cells >= 113;
- final persistence active cells >= 113.

The radius-6 target contains exactly 113 target-foreground cells. A phenotype with fewer than 113 hard-active cells cannot have every target-foreground cell alive simultaneously.

OCCUPANCY CEILING
Retain:
- pre-damage active cells <= 800;
- final recovery active cells <= 800;
- final persistence active cells <= 800.

FIXED ENVELOPE
Seed: 0
Variant: regeneration
Grid: 40 x 40
State channels: 16
Hidden channels: 128
Fire rate: 0.5
Alive channel: 3
Alive threshold: 0.1
Training iterations: 200
Learning rate: 0.001
Training development steps: 64..96
Batch size: 8
Pool size: 64
Training damage probability: 0.50
Training damage geometry: center 0.50 x 0.50
Training maturity threshold: 16 active cells
Gradient clip norm: 1.0
Hidden-state L2 weight: 0.00001
Target: deterministic radius-6 disk
Evaluation growth horizon: 96
Persistence horizon: 96
Recovery horizon: 96
Evaluation lesion: center 0.60 x 0.60
Model maximum development steps: 256
Precision: float32
Device family: CPU for sandbox execution

EVALUATION CONTRACT
The common global visible-channel morphology MSE remains unchanged for:
- pre/post lesion morphology;
- DamageEffect;
- RelativeDamageEffect;
- RecoveryFraction;
- stable T50/T90;
- persistence;
- historical comparison.

DIST-1 is a training intervention and training telemetry addition only.

VALID LESION REQUIREMENT
All must hold:
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10;
- finite state.

MORPHOLOGY REQUIREMENT
Pre-lesion global morphology MSE <= 0.0361635.
This remains the frozen 1.5x H96-control threshold.

PERSISTENCE REQUIREMENT
All must hold across the fixed 96-step persistence window:
- 113 <= final persistence active cells <= 800;
- final persistence global morphology MSE <= 0.0361635;
- maximum persistence global morphology MSE <= 2.0 * initial persistence global morphology MSE;
- finite state.

RECOVERY / OCCUPANCY REQUIREMENT
All must hold:
- 113 <= pre-damage active cells <= 800;
- 113 <= final recovery active cells <= 800;
- stable T50 attained;
- bounded final RecoveryFraction > 0.4230230485, the historical H96-control value.

IMPROVEMENT RULE
DIST-1 is worth widening only if every preregistered requirement above passes.

Compact gate list:
1. 113 <= pre-damage active cells <= 800;
2. DamageEffect > 0;
3. RelativeDamageEffect >= 0.10;
4. ActiveCellRemovalFraction >= 0.10;
5. stable T50 attained;
6. bounded final RecoveryFraction > 0.4230230485;
7. pre-lesion global morphology MSE <= 0.0361635;
8. 113 <= final recovery active cells <= 800;
9. 113 <= final persistence active cells <= 800;
10. final persistence global MSE <= 0.0361635;
11. maximum persistence global MSE <= 2x initial persistence global MSE;
12. no non-finite state.

STOP RULES
Stop and record negative immediately if:
- non-finite state or loss appears;
- frozen config cannot be reproduced;
- checkpoint integrity fails;
- a code/test failure appears and cannot be repaired without changing the preregistered scientific factor.

If the candidate completes but any improvement-rule gate fails:
- record CLOSED NEGATIVE;
- do not widen to additional seeds;
- do not alter the distance function or coefficients inside STAB-08.

IMPLEMENTATION REQUIREMENTS BEFORE RUN
- add one explicit immutable Chebyshev target-distance weight helper;
- add one explicit graded background alpha helper;
- add one explicit historical training-loss mode for DIST-1;
- preserve all six prior training-loss modes unchanged;
- add normal and resumable training telemetry for the graded term;
- add frozen config validation;
- add additive tests for exact distance rings, weights, formula, dead-state sanity, telemetry, and evidence;
- full reconstructed regression must be green before scientific execution.

PROVENANCE CONTRACT
If native byte-identical checkout remains unavailable in the sandbox:
- record exact connected-GitHub source revision used as reconstruction basis;
- set source_revision_verified_checkout = false;
- set sandbox_source_byte_identity = false;
- classify result as MEASURED SANDBOX rather than commit-bound confirmatory acceptance.

BOUNDARY
This packet remains canonical DG-1A P0 morphology/developmental-substrate research.
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling from this packet.
