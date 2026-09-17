TITLE: DG-1A-P0-STAB-03 — Foreground/Background-Balanced Morphology Training
DATE: 2026-09-17
STATUS: PREREGISTERED EXPLORATORY ABLATION
TRACK: DG-1A
CONFIDENCE: PLAUSIBLE

QUESTION
Does replacing the sole global unweighted morphology training loss with a fixed foreground/background-balanced morphology loss prevent the all-dead attractor and improve stable full-grid regeneration without degrading pre-lesion morphology or causing active-cell explosion?

MOTIVATION
STAB-02 exposed a concrete objective degeneracy. On the 40 x 40 radius-6 target, an all-zero phenotype obtains global visible-channel MSE approximately 0.0295742 because target foreground occupies only a small fraction of the grid.

H128 converged to that all-dead phenotype. Therefore longer developmental exposure cannot be interpreted cleanly until the training objective makes missing target foreground expensive enough that zero activity is not a competitive solution.

CONTROL G-MSE
Existing H96/M16 full-grid seed-0 regeneration control:
- training morphology objective: global visible-channel MSE;
- training development steps: 64..96;
- pre-lesion error: approximately 0.0241090;
- valid 0.60 evaluation lesion;
- final bounded RecoveryFraction: approximately 0.423023;
- stable T50: not attained;
- final active cells: 502 / 1600.

CANDIDATE BAL-50
Change only the morphology term used for TRAINING.

Foreground definition:
- target alpha > 0.1.

Foreground loss:
- mean squared error over visible channels on foreground pixels only.

Background loss:
- mean squared error over visible channels on non-foreground pixels only.

Balanced morphology loss:
BalancedMSE = 0.5 * ForegroundMSE + 0.5 * BackgroundMSE

The hidden-state L2 term remains unchanged.

EVALUATION CONTRACT
Do not replace the existing global morphology MSE used for evaluation, damage effect, recovery fraction, persistence, and comparison with earlier P0 evidence.

BAL-50 changes training pressure only. All reported P0 recovery criteria continue to use the established global evaluation metric.

WHY ONE CANDIDATE
The 0.5 / 0.5 weighting is fixed before execution to prevent weight tuning after inspection. No foreground-weight sweep is permitted inside STAB-03.

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
- RelativeDamageEffect;
- ActiveCellRemovalFraction;
- pre/final active cells;
- balanced training loss;
- global training morphology MSE retained as telemetry;
- training wall-clock;
- checkpoint size.

VALID LESION REQUIREMENT
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10;
- finite state.

VIABILITY REQUIREMENT
Pre-damage active cells > 0.
An all-dead phenotype fails immediately regardless of numerical loss.

IMPROVEMENT RULE
BAL-50 is worth widening only if all are true:
1. pre-damage active cells > 0;
2. evaluation lesion is valid;
3. stable T50 is attained;
4. bounded final RecoveryFraction > 0.423023, the H96 control;
5. pre-lesion global morphology MSE <= 0.0361635, equal to 1.5x the H96 control pre-error;
6. final active cells <= 800 / 1600;
7. no non-finite state occurs.

FAILURE INTERPRETATION
If BAL-50 fails, do not tune its weighting inside STAB-03. Record whether failure is caused by:
- all-dead phenotype persists;
- invalid lesion / excessive robustness;
- poor pre-lesion morphology;
- continued repair relapse;
- active-cell explosion;
- numerical instability;
- balanced loss materially worsens optimization.

IMPLEMENTATION REQUIREMENTS
- add a separately tested balanced morphology loss helper;
- preserve existing morphology_mse behavior unchanged;
- training loss mode must be explicit/configurable and default to existing global MSE for historical configs;
- evidence must record effective training loss mode;
- no existing assertions may be weakened or skipped.

SCIENTIFIC BOUNDARY
This is still morphology reproduction/regeneration work. A successful BAL-50 result does not establish cognition, specialization, continual learning, ancestor inheritance, or general intelligence.

FIBONACCI RELATION
No Fibonacci schedule is introduced. DG-1A-FIB1 remains a later repair-budget ablation after canonical P0 viability and regeneration are characterized.

NEXT ACTION
Implement BAL-50 behind an explicit training loss mode, add unit tests, run the complete test surface, then train one fresh seed-0 full-grid candidate and apply the improvement rule exactly as written.
