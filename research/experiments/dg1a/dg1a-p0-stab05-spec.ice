TITLE: DG-1A-P0-STAB-05 — Background-Alpha Occupancy Suppression
DATE: 2026-09-17
STATUS: PREREGISTERED EXPLORATORY ABLATION
TRACK: DG-1A
CONFIDENCE: PLAUSIBLE

QUESTION
Does adding one explicit target-background alpha/liveness penalty to the STAB-04 composite training objective suppress the repeated overgrown phenotype while preserving foreground viability, acceptable global morphology, a valid lesion, and stable full-grid regeneration under the canonical H96/M16 envelope?

MOTIVATION
The full-grid objective problem is now bracketed by repeated opposite degeneracies.

STAB-02:
- global visible-channel MSE alone made the sparse-target all-dead state competitive;
- the zero phenotype has global target loss approximately 0.02957421875 on the 40 x 40 radius-6 target.

STAB-03:
- equal 0.5/0.5 foreground/background visible-region weighting avoided death;
- it produced 1579 / 1600 pre-damage active cells;
- damage improved the common global morphology metric.

STAB-04:
- GlobalVisibleMSE + ForegroundVisibleMSE also avoided death;
- it produced 1578 / 1600 pre-damage active cells;
- pre-lesion global MSE was 0.1845480204;
- removing 36.50% of active cells improved global MSE by 0.0661034361;
- the lesion was invalid and the candidate failed.

STAB-03 and STAB-04 therefore indicate that strong foreground protection without an explicit occupancy control can make excessive active structure competitive.

LITERATURE / MECHANISTIC BASIS
The original Growing Neural Cellular Automata formulation gives alpha a special liveness role: cells with alpha > 0.1 are mature/living and empty cells are zeroed when they lack a mature neighbor.

Later NCA work explicitly identifies sparsity regularisation as a plausible means of encouraging parsimonious learned dynamics.

STAB-05 applies that general principle narrowly to the already-defined liveness variable rather than changing architecture, curriculum, evaluation, or foreground coefficient.

This literature motivates the mechanism class; it does not establish the exact coefficient or predict success.

REFERENCES
- Mordvintsev, Randazzo, Niklasson, Levin. Growing Neural Cellular Automata. Distill, 2020.
- Richardson et al. Learning spatio-temporal patterns with Neural Cellular Automata. 2024. Discussion notes sparsity regularisation as a possible complexity control.

CONTROL / PRIOR FRONTIER
Canonical H96/M16 full-grid seed-0 regeneration control:
- training morphology objective: global visible-channel MSE;
- training development steps: 64..96;
- pre-lesion global morphology MSE: approximately 0.0241090;
- valid 0.60 evaluation lesion;
- final bounded RecoveryFraction: approximately 0.423023;
- stable T50: not attained;
- final active cells: 502 / 1600.

STAB-04 FG+1 negative result:
- pre-damage active cells: 1578 / 1600;
- pre-lesion global morphology MSE: 0.1845480204;
- DamageEffect: -0.0661034361;
- RelativeDamageEffect: -0.3581909788;
- final active cells: 1073 / 1600;
- candidate worth widening: NO.

CANDIDATE OCC-A1
Relative to STAB-04, change exactly one training-objective mechanism: add one background-alpha occupancy term.

Foreground definition:
- target alpha > 0.1.

Background definition:
- target alpha <= 0.1.

Global visible morphology loss:
- mean squared error over all visible channels and all pixels.

Foreground visible morphology loss:
- mean squared error over visible channels on foreground pixels only.

Background alpha occupancy loss:
BackgroundAlphaMSE = mean(state_alpha^2 over target-background pixels)

Because target alpha is zero on target-background pixels, this is equivalent to target-background alpha MSE.

TrainingMorphologyLoss = GlobalVisibleMSE + 1.0 * ForegroundVisibleMSE + 1.0 * BackgroundAlphaMSE

Total training loss remains:
TrainingLoss = TrainingMorphologyLoss + existing hidden-state L2 term.

The new BackgroundAlphaMSE coefficient is fixed at 1.0 before execution.
No coefficient sweep is permitted inside STAB-05.

WHY THIS IS NOT A FOREGROUND-WEIGHT SWEEP
The STAB-04 foreground coefficient remains exactly 1.0.
The new factor penalizes the liveness/occupancy variable specifically on target background.
It therefore introduces explicit structural occupancy pressure rather than merely changing the relative weight of the existing foreground term.

DEAD-STATE SANITY
The 40 x 40 radius-6 target contains 113 foreground pixels out of 1600.
For an all-zero phenotype:
- GlobalVisibleMSE is approximately 0.02957421875;
- ForegroundVisibleMSE is 0.41875;
- BackgroundAlphaMSE is 0.0;
- composite morphology loss is therefore approximately 0.44832421875.

Thus the new occupancy term does not make the all-dead state numerically attractive by itself; the explicit foreground term continues to make missing target foreground expensive.

EVALUATION CONTRACT
Do not change the established global visible-channel morphology MSE used for:
- pre/post lesion morphology;
- DamageEffect;
- RelativeDamageEffect;
- RecoveryFraction;
- stable T50/T90;
- persistence;
- historical cross-experiment comparison.

BackgroundAlphaMSE is a TRAINING term and diagnostic telemetry only.

SINGLE-FACTOR CONTRACT
Relative to STAB-04 FG+1, the only intended scientific factor is the addition of BackgroundAlphaMSE with coefficient 1.0.

Do not change:
- foreground coefficient;
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
- effective training loss mode;
- composite training morphology loss;
- global training morphology MSE telemetry;
- foreground training morphology MSE telemetry;
- background-alpha occupancy telemetry;
- persistence error/drift;
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
Because this packet directly targets overgrowth, both must hold:
- pre-damage active cells <= 800 / 1600;
- final active cells <= 800 / 1600.

The ceiling is intentionally generous and is fixed before execution. It preserves the existing STAB-03/STAB-04 final-cell ceiling while extending the same ceiling to the pre-lesion phenotype so a grossly overgrown organism cannot pass by shrinking only after lesion/recovery.

IMPROVEMENT RULE
OCC-A1 is worth widening only if all are true:
1. pre-damage active cells > 0;
2. pre-damage active cells <= 800 / 1600;
3. evaluation lesion is valid:
   - DamageEffect > 0;
   - RelativeDamageEffect >= 0.10;
   - ActiveCellRemovalFraction >= 0.10;
4. stable T50 is attained;
5. bounded final RecoveryFraction > 0.423023, the H96 control;
6. pre-lesion global morphology MSE <= 0.0361635, equal to 1.5x the H96 control pre-error;
7. final active cells <= 800 / 1600;
8. no non-finite state occurs.

FAILURE INTERPRETATION
If OCC-A1 fails, do not tune its coefficient inside STAB-05. Record which preregistered constraints fail and classify the dominant observed failure without rewriting thresholds after inspection.

Candidate failure classes include:
- all-dead phenotype;
- overgrowth persists;
- occupancy suppression damages foreground viability;
- acceptable occupancy but poor global morphology;
- invalid lesion / damage improves morphology;
- insufficient damage effect;
- stable T50 not attained;
- recovery not above H96 control;
- numerical instability;
- optimization failure;
- alpha-specific suppression produces pathological low-alpha visible/hidden structure without solving morphology.

IMPLEMENTATION REQUIREMENTS
- add a separately tested target-background alpha MSE helper;
- target background must be defined from immutable target alpha <= 0.1;
- background loss must use the model alpha/liveness channel only;
- empty target background must fail closed;
- add explicit training loss mode global_plus_foreground_bg_alpha;
- exact formula must be GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAlphaMSE;
- preserve historical global_mse behavior unchanged;
- preserve historical balanced_fg_bg behavior unchanged;
- preserve historical global_plus_foreground behavior unchanged;
- config validation must accept only supported explicit modes;
- training history/evidence must expose background-alpha telemetry for the new mode without changing the common evaluation metric;
- finite-loss behavior must be tested;
- no existing assertions may be weakened, skipped, disabled, or altered merely to make the experiment pass.

EXECUTION CONTRACT
1. Commit this preregistration before implementation or execution.
2. Independently read it back and verify branch HEAD.
3. Implement only the new occupancy helper, explicit loss mode, telemetry, config, and required tests.
4. Run the complete test surface.
5. Execute exactly one fresh seed-0 STAB-05 candidate.
6. Use one writer for resumable checkpoints; never run concurrent workers against the same checkpoint.
7. Apply the preregistered improvement rule exactly as written.
8. Record machine evidence at evidence/dg1a/p0_stab05_sandbox.json.
9. Record the human-readable result at research/experiments/dg1a/dg1a-p0-stab05-result.ice.
10. Reconcile research/status/dg1a-p0-status.ice and research/status/dg1-current-status.ice.
11. Independently read back all writes and final branch HEAD.

SCIENTIFIC BOUNDARY
This remains morphology reproduction/regeneration work. Success would not establish cognition, functional specialization, continual learning, ancestor inheritance, structural growth, or general intelligence.

FIBONACCI RELATION
No Fibonacci schedule, capacity rule, topology prior, repair budget, or module-size vocabulary is introduced. DG-1A-FIB1 remains a separate later ablation after canonical P0 viability/objective behavior is adequately characterized.

STOP / NEXT RULE
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling as part of this packet.
Complete and classify STAB-05 first.
