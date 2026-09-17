TITLE: DG-1A-P0-STAB-07 — One-Cell Target-Support Halo Occupancy Control
DATE: 2026-09-17
STATUS: PREREGISTERED EXPLORATORY ABLATION
TRACK: DG-1A
CONFIDENCE: PLAUSIBLE

QUESTION
Can canonical P0 preserve meaningful viable target support while bounding excess occupancy if background occupancy pressure is restricted to far-field cells outside the target's own one-neighborhood support halo?

MOTIVATION
STAB-04 and STAB-05 failed on the overgrowth side of the objective bracket. STAB-06 failed on the opposite near-dead side.

STAB-04 FG+1:
- pre-damage active cells: 1578 / 1600;
- pre-lesion global MSE: 0.1845480204;
- lesion improved morphology.

STAB-05 OCC-A1:
- continuous target-background alpha-energy penalty;
- pre-damage active cells: 1206 / 1600;
- pre-lesion global MSE: 0.0701904967;
- occupancy and morphology improved substantially relative to STAB-04;
- persistence/recovery still expanded;
- lesion still improved morphology.

STAB-06 AM-05:
- threshold-aligned target-background alive-margin penalty;
- pre-damage active cells: 3 / 1600;
- pre-lesion global MSE: 0.0283585768;
- RelativeDamageEffect: 0.0062380726;
- final recovery active cells: 0;
- near-dead false-positive regime.

The next experiment must therefore change spatial support semantics rather than simply interpolate a scalar coefficient between STAB-05 and STAB-06.

REPOSITORY LIVENESS / LOCALITY BASIS
The NCA update rule is local. Its liveness mechanism uses a 3 x 3 max-pool neighborhood around the alpha channel, with alive threshold 0.1. A cell can therefore be dynamically supported by immediate neighbors even when those neighbors are outside the visible target foreground.

A target-background penalty applied uniformly to every background pixel may suppress exactly the narrow near-target scaffold that the local automaton can use to sustain and repair the visible morphology.

The original Growing Neural Cellular Automata formulation likewise gives alpha a special liveness role and relies on local neighboring living cells.

REFERENCE
Mordvintsev, Randazzo, Niklasson, Levin. Growing Neural Cellular Automata. Distill, 2020.

CANDIDATE
HALO-1

TARGET FOREGROUND
ForegroundMask = target alpha > 0.1

TARGET SUPPORT HALO
SupportHaloMask = 3 x 3 max-pool dilation of ForegroundMask with stride 1 and padding 1.

This is exactly one Chebyshev-neighborhood cell around the target foreground. No repeated dilation is permitted.

For the frozen 40 x 40 radius-6 disk target:
- target foreground cells: 113;
- one-cell support-halo cells including foreground: 169;
- support-ring-only cells: 56;
- far-field cells outside the support halo: 1431.

FAR-FIELD OCCUPANCY TERM
FarFieldBackgroundAlphaMSE = mean(
    state_alpha^2
    over target-background pixels outside SupportHaloMask
)

The support halo receives NO dedicated occupancy penalty.
The visible global loss still evaluates every pixel.
The foreground term still directly protects the visible target foreground.

TRAINING OBJECTIVE
TrainingMorphologyLoss =
    GlobalVisibleMSE
    + 1.0 * ForegroundVisibleMSE
    + 1.0 * FarFieldBackgroundAlphaMSE

Total training loss remains:
TrainingLoss = TrainingMorphologyLoss + existing hidden-state L2 term.

The STAB-06 BackgroundAliveMarginLoss term is NOT retained in HALO-1.
The STAB-05 all-background BackgroundAlphaMSE term is NOT retained in HALO-1.
No coefficient sweep, halo-radius sweep, threshold sweep, or alternate geometry is permitted inside STAB-07.

SINGLE-FACTOR CONTRACT
Relative to STAB-05 OCC-A1, the scientific change is spatial support geometry: the continuous background alpha-energy penalty applies only to far-field cells outside the one-cell support halo rather than every target-background cell.

Relative to STAB-06, HALO-1 intentionally removes threshold-aligned alive-margin pressure; this is not coefficient interpolation. It tests whether preserving one local support neighborhood resolves the observed viability/occupancy conflict.

Do not change:
- foreground coefficient;
- far-field occupancy coefficient;
- target foreground threshold;
- support halo radius;
- alive threshold;
- model architecture;
- optimizer;
- training iterations;
- learning rate;
- development-step range;
- state pool;
- training-damage probability or geometry;
- training maturity threshold;
- hidden-state L2 weight;
- target;
- evaluation horizon;
- evaluation lesion;
- common global evaluation metric.

DEAD-STATE SANITY
For the all-zero phenotype:
- GlobalVisibleMSE is approximately 0.02957421875;
- ForegroundVisibleMSE is approximately 0.41875;
- FarFieldBackgroundAlphaMSE is 0.0;
- composite morphology loss is approximately 0.44832421875.

Therefore the all-dead phenotype remains explicitly expensive through the frozen foreground term.

MEANINGFUL VIABILITY FLOOR
The frozen radius-6 target contains exactly 113 target-foreground cells.

A phenotype with fewer than 113 hard-active cells cannot possibly have every target-foreground cell alive simultaneously.

STAB-07 therefore strengthens the viability requirement before execution:
- pre-damage active cells >= 113;
- final recovery active cells >= 113;
- final persistence active cells >= 113.

This lower bound is target-derived, not fitted to STAB-07 results.

The existing occupancy ceiling remains:
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

HALO-1 is a training intervention and training telemetry addition only.

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
HALO-1 is worth widening only if every preregistered requirement above passes.

In compact form, all must be true:
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
- the frozen config cannot be reproduced;
- checkpoint integrity fails;
- a code/test failure appears and cannot be repaired without changing the preregistered scientific factor.

If the candidate completes but any improvement-rule gate fails:
- record CLOSED NEGATIVE;
- do not widen to additional seeds;
- do not tune halo radius or coefficient inside STAB-07.

IMPLEMENTATION REQUIREMENTS BEFORE RUN
- add one explicit far-field background alpha helper;
- add one explicit historical training-loss mode for HALO-1;
- preserve all five prior training-loss modes unchanged;
- add normal and resumable training telemetry for the far-field term;
- add frozen config validation;
- add additive unit/integration tests for exact support-halo geometry and formula;
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
