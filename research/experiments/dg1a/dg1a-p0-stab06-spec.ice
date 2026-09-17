TITLE: DG-1A-P0-STAB-06 — Threshold-Aligned Background Alive-Margin Control
DATE: 2026-09-17
STATUS: PREREGISTERED EXPLORATORY ABLATION
TRACK: DG-1A
CONFIDENCE: PLAUSIBLE

QUESTION
Does replacing STAB-05's continuous target-background alpha-energy penalty with a threshold-aligned differentiable alive-margin penalty produce bounded active support, acceptable global morphology, meaningful damage, stable persistence, and stable regeneration under the canonical H96/M16 envelope?

MOTIVATION
Canonical full-grid P0 remains unresolved, but STAB-05 narrowed the failure.

STAB-04:
- GlobalVisibleMSE + ForegroundVisibleMSE avoided death;
- pre-damage active cells: 1578 / 1600;
- pre-lesion global morphology MSE: 0.1845480204;
- the evaluation lesion improved morphology.

STAB-05 OCC-A1:
- added target-background alpha-energy pressure;
- pre-damage active cells fell to 1206 / 1600;
- pre-lesion global morphology MSE fell to 0.0701904967;
- both changes were directionally favorable;
- persistence still expanded from 1140 to 1378 active cells;
- final recovery activity was 1329 / 1600;
- the evaluation lesion still improved morphology.

STAB-05 therefore established that occupancy-specific pressure is relevant, but also exposed a mismatch between continuous alpha energy and the repository's thresholded active-cell semantics.

REPOSITORY LIVENESS SEMANTICS
The model defines:
- alpha/liveness channel: 3;
- maturity threshold: alpha > 0.1;
- neighborhood survival mask: 3 x 3 max-pool alpha > 0.1;
- reported active-cell count: per-cell alpha > 0.1.

The hard active-cell count is therefore thresholded and non-differentiable.
STAB-05's BackgroundAlphaMSE = mean(alpha^2) is differentiable but not threshold-aligned: many cells can remain just above 0.1 while paying relatively small alpha-squared cost.

MECHANISTIC BASIS
Growing Neural Cellular Automata assigns alpha a special liveness role and uses alpha > 0.1 to define mature/living cells and their local support.

General sparsity literature also motivates differentiable surrogates when the desired count/cardinality objective is discrete and non-differentiable. That literature motivates the mechanism class only; it does not establish this experiment's exact margin or predict success.

REFERENCES
- Mordvintsev, Randazzo, Niklasson, Levin. Growing Neural Cellular Automata. Distill, 2020.
- Louizos, Welling, Kingma. Learning Sparse Neural Networks through L0 Regularization. ICLR, 2018. General precedent for differentiable surrogates of discrete sparsity objectives; not an NCA-specific prescription.

CONTROL / PRIOR FRONTIER
Canonical H96/M16 full-grid seed-0 regeneration control:
- pre-lesion global morphology MSE: 0.0241090059;
- DamageEffect: 0.0026036687;
- RelativeDamageEffect: 0.1079956895;
- pre-damage active cells: 130 / 1600;
- active-cell removal fraction: 0.4307692308;
- bounded final RecoveryFraction: 0.4230230485;
- stable T50: not attained;
- final active cells: 502 / 1600.

STAB-05 OCC-A1 negative result:
- pre-damage active cells: 1206 / 1600;
- pre-lesion global morphology MSE: 0.0701904967;
- DamageEffect: -0.0144327730;
- RelativeDamageEffect: -0.2056228929;
- final active cells: 1329 / 1600;
- persistence final active cells: 1378 / 1600;
- candidate worth widening: NO.

CANDIDATE AM-05
Relative to STAB-05, replace exactly one occupancy-control mechanism.

Remove from the active candidate objective:
BackgroundAlphaMSE = mean(state_alpha^2 over target-background pixels)

Replace it with:
BackgroundAliveMarginLoss = mean(
    (ReLU(state_alpha - margin_floor) / margin_width)^2
    over target-background pixels
)

Fixed constants:
- alive_threshold = 0.1
- margin_floor = 0.05
- margin_width = alive_threshold - margin_floor = 0.05
- BackgroundAliveMarginLoss coefficient = 1.0

Target foreground:
- target alpha > 0.1.

Target background:
- target alpha <= 0.1.

TrainingMorphologyLoss =
    GlobalVisibleMSE
    + 1.0 * ForegroundVisibleMSE
    + 1.0 * BackgroundAliveMarginLoss

Total training loss remains:
TrainingLoss = TrainingMorphologyLoss + existing hidden-state L2 term.

The STAB-05 BackgroundAlphaMSE term is NOT retained in AM-05.
No coefficient, threshold, or margin sweep is permitted inside STAB-06.

WHY margin_floor = 0.05
The margin floor is fixed at one-half of the repository maturity threshold before execution.
This creates a safety band from alpha 0.05 to the hard active threshold 0.1.

Properties:
- target-background alpha <= 0.05 receives zero margin penalty;
- target-background alpha = 0.1 receives normalized penalty exactly 1.0 before background averaging;
- every target-background cell with alpha > 0.1 receives normalized penalty > 1.0;
- exact target-background alpha = 0 remains an exact optimum of this term;
- unlike a sigmoid occupancy surrogate, the term does not continuously reward driving already-safe target-background alpha negative.

CARDINALITY RELATION
Let N_bg be the number of target-background pixels and N_active_bg the number of those pixels whose alpha > 0.1.

Because every hard-active target-background pixel contributes > 1.0 before averaging:

BackgroundAliveMarginLoss > N_active_bg / N_bg

whenever N_active_bg > 0.

Thus the term directly upper-bounds a differentiable threshold-margin surrogate of background active fraction more closely than alpha-energy MSE does.
It is still not identical to hard cardinality and may fail.

DEAD-STATE SANITY
For the all-zero phenotype:
- GlobalVisibleMSE is approximately 0.02957421875;
- ForegroundVisibleMSE is 0.41875;
- BackgroundAliveMarginLoss is 0.0;
- composite morphology loss is approximately 0.44832421875.

Therefore AM-05 does not make the all-dead phenotype numerically attractive relative to STAB-04/STAB-05's explicit foreground protection.

EVALUATION CONTRACT
Do not change the established global visible-channel morphology MSE used for:
- pre/post lesion morphology;
- DamageEffect;
- RelativeDamageEffect;
- RecoveryFraction;
- stable T50/T90;
- persistence;
- historical cross-experiment comparison.

BackgroundAliveMarginLoss is a TRAINING term and diagnostic telemetry only.

SINGLE-FACTOR CONTRACT
Relative to STAB-05 OCC-A1, the only intended scientific factor is replacement of continuous target-background alpha-energy loss with the fixed threshold-aligned alive-margin loss.

Do not change:
- foreground coefficient;
- occupancy-term coefficient;
- alive threshold;
- model architecture;
- optimizer;
- training iterations;
- learning rate;
- development-step range;
- state pool;
- training-damage probability or geometry;
- maturity threshold;
- hidden-state L2 weight;
- target;
- evaluation horizon;
- evaluation lesion;
- common evaluation metric.

FIXED ENVELOPE
Seed: 0
Variant: regeneration
Grid: 40 x 40
State channels: 16
Hidden channels: 128
Fire rate: 0.5
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

PRIMARY METRIC
Stable T50 within the 96-step recovery window.

SECONDARY METRICS
- bounded final RecoveryFraction;
- stable T90;
- normalized recovery AUC;
- pre-lesion global morphology MSE;
- post-lesion global morphology MSE;
- DamageEffect;
- RelativeDamageEffect;
- ActiveCellRemovalFraction;
- pre/post/final active cells;
- persistence initial/final/max global error;
- persistence initial/final active cells;
- effective training loss mode;
- composite training morphology loss;
- global training morphology MSE telemetry;
- foreground training morphology MSE telemetry;
- background alive-margin telemetry;
- training wall-clock;
- checkpoint size;
- finite-state status.

VALID LESION REQUIREMENT
All must hold:
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10;
- finite state.

VIABILITY REQUIREMENT
Pre-damage active cells > 0.
An all-dead phenotype fails immediately regardless of numerical loss.

OCCUPANCY REQUIREMENT
Both must hold:
- pre-damage active cells <= 800 / 1600;
- final recovery active cells <= 800 / 1600.

MORPHOLOGY REQUIREMENT
Pre-lesion global morphology MSE <= 0.0361635.
This remains the previously frozen 1.5x H96 control threshold.

PERSISTENCE REQUIREMENT
All must hold across the fixed 96-step persistence window:
- final persistence active cells <= 800 / 1600;
- final persistence global morphology MSE <= 0.0361635;
- maximum persistence global morphology MSE <= 2.0 * initial persistence global morphology MSE;
- finite state.

The factor-of-two transient bound is fixed before execution and is scale-relative rather than an after-the-fact absolute threshold.

IMPROVEMENT RULE
AM-05 is worth widening only if all are true:
1. pre-damage active cells > 0;
2. pre-damage active cells <= 800 / 1600;
3. evaluation lesion is valid:
   - DamageEffect > 0;
   - RelativeDamageEffect >= 0.10;
   - ActiveCellRemovalFraction >= 0.10;
4. stable T50 is attained;
5. bounded final RecoveryFraction > 0.4230230485, the H96 control;
6. pre-lesion global morphology MSE <= 0.0361635;
7. final recovery active cells <= 800 / 1600;
8. persistence final active cells <= 800 / 1600;
9. persistence final global morphology MSE <= 0.0361635;
10. persistence maximum global morphology MSE <= 2.0 * its initial persistence global morphology MSE;
11. no non-finite state occurs.

FAILURE INTERPRETATION
If AM-05 fails, do not tune its coefficient, margin floor, margin width, or threshold inside STAB-06.
Record which preregistered constraints fail and classify the dominant observed failure without rewriting thresholds after inspection.

Candidate failure classes include:
- all-dead phenotype;
- threshold-aligned suppression still permits overgrowth;
- margin penalty suppresses necessary foreground/support dynamics;
- acceptable hard occupancy but poor global morphology;
- acceptable endpoint occupancy but unstable persistence;
- invalid lesion / damage improves morphology;
- insufficient damage effect;
- stable T50 not attained;
- recovery not above H96 control;
- numerical instability;
- optimization failure;
- background alpha stays below threshold while harmful visible/hidden support remains distributed elsewhere.

IMPLEMENTATION REQUIREMENTS
- add a separately tested target-background alive-margin helper;
- target background must be defined from immutable target alpha <= 0.1;
- helper must use the model alpha/liveness channel only;
- default experimental constants must be explicit, not inferred from data;
- empty target background must fail closed;
- invalid margin configuration must fail closed;
- add explicit training loss mode global_plus_foreground_bg_alive_margin;
- exact formula must be GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAliveMarginLoss;
- preserve historical global_mse behavior unchanged;
- preserve historical balanced_fg_bg behavior unchanged;
- preserve historical global_plus_foreground behavior unchanged;
- preserve historical global_plus_foreground_bg_alpha behavior unchanged;
- config validation must accept only supported explicit modes;
- training history/evidence must expose alive-margin telemetry for the new mode without changing the common evaluation metric;
- finite-loss behavior must be tested;
- threshold/margin boundary behavior must be tested explicitly;
- no existing assertions may be weakened, skipped, disabled, or altered merely to make the experiment pass.

EXECUTION CONTRACT
1. Commit this preregistration before implementation or execution.
2. Independently read it back and verify branch HEAD.
3. Implement only the alive-margin helper, explicit loss mode, telemetry, config, and required tests.
4. Run the complete test surface.
5. Execute exactly one fresh seed-0 STAB-06 candidate.
6. Use one writer for resumable checkpoints; never run concurrent workers against the same checkpoint.
7. Apply the preregistered improvement rule exactly as written.
8. Record machine evidence at evidence/dg1a/p0_stab06_sandbox.json.
9. Record the human-readable result at research/experiments/dg1a/dg1a-p0-stab06-result.ice.
10. Reconcile research/status/dg1a-p0-status.ice and research/status/dg1-current-status.ice.
11. Independently read back all writes and final branch HEAD.

SCIENTIFIC BOUNDARY
This remains morphology reproduction/regeneration work. Success would not establish cognition, functional specialization, continual learning, ancestor inheritance, structural growth, or general intelligence.

FIBONACCI RELATION
No Fibonacci schedule, capacity rule, topology prior, repair budget, or module-size vocabulary is introduced. DG-1A-FIB1 remains a separate later ablation after canonical P0 viability/objective behavior is adequately characterized.

STOP / NEXT RULE
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling as part of this packet.
Complete and classify STAB-06 first.