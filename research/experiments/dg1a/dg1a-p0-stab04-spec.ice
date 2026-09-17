TITLE: DG-1A-P0-STAB-04 — Global + Foreground Supplemental Morphology Training
DATE: 2026-09-17
STATUS: PREREGISTERED EXPLORATORY ABLATION
TRACK: DG-1A
CONFIDENCE: PLAUSIBLE

QUESTION
Does retaining the established global visible-channel morphology MSE while adding one fixed foreground-visible MSE supplement prevent both sparse-target death and foreground-overgrowth failure modes, while recovering a valid lesion and improving stable full-grid regeneration under the canonical H96/M16 envelope?

MOTIVATION
STAB-02 showed that global unweighted morphology MSE alone can make the all-dead sparse-target phenotype competitive.

STAB-03 showed that equal 0.5/0.5 aggregate weighting of foreground and background prevents death but overcorrects toward an overgrown poor-morphology phenotype. In STAB-03, removing 36.48% of active cells improved the unchanged global morphology metric, invalidating regeneration inference.

The next discriminating intervention is therefore a composite TRAINING objective that preserves occupancy-proportional global pressure and adds explicit foreground protection without replacing the common evaluation metric.

CONTROL / PRIOR FRONTIER
Canonical H96/M16 full-grid seed-0 regeneration control:
- training morphology objective: global visible-channel MSE;
- training development steps: 64..96;
- pre-lesion global morphology MSE: approximately 0.0241090;
- valid 0.60 evaluation lesion;
- final bounded RecoveryFraction: approximately 0.423023;
- stable T50: not attained;
- final active cells: 502 / 1600.

STAB-03 BAL-50 negative result:
- pre-damage active cells: 1579 / 1600;
- pre-lesion global morphology MSE: 0.1411564797;
- DamageEffect: -0.0361511707;
- RelativeDamageEffect: -0.2561070579;
- final active cells: 1164 / 1600;
- stable T50: not attained / undefined;
- failure mode: overgrown / poor-morphology phenotype.

CANDIDATE FG+1
Change only the morphology term used for TRAINING.

Foreground definition:
- target alpha > 0.1.

Global visible morphology loss:
- mean squared error over all visible channels and all pixels.

Foreground visible morphology loss:
- mean squared error over visible channels on foreground pixels only.

TrainingMorphologyLoss = GlobalVisibleMSE + 1.0 * ForegroundVisibleMSE

Total training loss remains:
TrainingLoss = TrainingMorphologyLoss + existing hidden-state L2 term.

The coefficient 1.0 is fixed before execution. No coefficient sweep is permitted inside STAB-04.

EVALUATION CONTRACT
The established global visible-channel morphology MSE remains unchanged for evaluation, lesion validity, recovery fraction, persistence, and cross-experiment comparison.

STAB-04 changes training pressure only.

SINGLE-FACTOR CONTRACT
Relative to the canonical H96/M16 regeneration envelope, the only intended scientific factor is training morphology loss mode:
- historical/default mode: global_mse;
- STAB-03 historical mode retained: balanced_fg_bg;
- new STAB-04 mode: global_plus_foreground.

No other model, optimizer, curriculum, target, damage, evaluation, or resource parameter may be changed for this packet.

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
- post-lesion global morphology MSE;
- DamageEffect;
- RelativeDamageEffect;
- ActiveCellRemovalFraction;
- pre/post/final active cells;
- effective training loss mode;
- composite training morphology loss;
- global training morphology MSE telemetry;
- foreground training morphology MSE telemetry where available;
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

IMPROVEMENT RULE
FG+1 is worth widening only if all are true:
1. pre-damage active cells > 0;
2. evaluation lesion is valid:
   - DamageEffect > 0;
   - RelativeDamageEffect >= 0.10;
   - ActiveCellRemovalFraction >= 0.10;
3. stable T50 is attained;
4. bounded final RecoveryFraction > 0.423023, the H96 control;
5. pre-lesion global morphology MSE <= 0.0361635, equal to 1.5x the H96 control pre-error;
6. final active cells <= 800 / 1600;
7. no non-finite state occurs.

FAILURE INTERPRETATION
If FG+1 fails, do not tune the coefficient inside STAB-04. Record which preregistered constraints fail and classify the dominant observed failure without rewriting thresholds after inspection. Candidate categories include:
- all-dead phenotype;
- invalid lesion / damage improves morphology;
- insufficient damage effect;
- poor pre-lesion morphology;
- stable T50 not attained;
- recovery not above H96 control;
- active-cell overgrowth;
- numerical instability;
- optimization failure.

IMPLEMENTATION REQUIREMENTS
- add explicit training loss mode global_plus_foreground;
- exact formula must be GlobalVisibleMSE + ForegroundVisibleMSE;
- foreground mask definition must remain target alpha > 0.1;
- empty target foreground must fail closed rather than silently returning a misleading finite value;
- preserve historical global_mse behavior unchanged;
- preserve balanced_fg_bg behavior unchanged for reproducibility;
- config validation must accept only supported explicit modes;
- evidence must record the effective training loss mode;
- finite-loss behavior must be tested;
- no existing assertions may be weakened, skipped, disabled, or altered merely to make the experiment pass.

EXECUTION CONTRACT
1. Commit this preregistration before implementation or execution.
2. Implement only the new explicit loss mode and required test/config/evidence plumbing.
3. Run the complete test surface.
4. Execute exactly one fresh seed-0 STAB-04 candidate.
5. If execution is interrupted, resume from a single-writer checkpoint; never run concurrent workers against the same checkpoint.
6. Apply the preregistered improvement rule exactly as written.
7. Record machine evidence at evidence/dg1a/p0_stab04_sandbox.json.
8. Record the human-readable result at research/experiments/dg1a/dg1a-p0-stab04-result.ice.
9. Reconcile research/status/dg1a-p0-status.ice and research/status/dg1-current-status.ice.
10. Independently read back all writes and final branch HEAD.

SCIENTIFIC BOUNDARY
This remains morphology reproduction/regeneration work. Success would not establish cognition, functional specialization, continual learning, ancestor inheritance, structural growth, or general intelligence.

FIBONACCI RELATION
No Fibonacci schedule, capacity rule, topology prior, or module-size vocabulary is introduced. DG-1A-FIB1 remains a separate later ablation after canonical P0 viability/objective behavior is adequately characterized.

STOP / NEXT RULE
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling as part of this packet. Complete and classify STAB-04 first.
