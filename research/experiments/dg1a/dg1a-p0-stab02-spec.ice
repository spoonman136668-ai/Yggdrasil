TITLE: DG-1A-P0-STAB-02 — Development-Horizon Stabilization
DATE: 2026-09-17
STATUS: PREREGISTERED EXPLORATORY ABLATION
TRACK: DG-1A
CONFIDENCE: PLAUSIBLE

QUESTION
Does exposing the full-grid regeneration curriculum to longer developmental trajectories reduce late post-repair relapse while preserving meaningful lesion sensitivity and pre-lesion morphology?

MOTIVATION
The 40 x 40 M16 control is trained with randomized development horizons of 64..96 steps and evaluated for 96 additional post-lesion recovery steps.

The control reaches transient T50/T90 but later relapses, ending with RecoveryFraction approximately 0.423 and no stable T50.

STAB-01 showed that simply increasing the maturity threshold does not solve this problem.

HYPOTHESIS
The training distribution may underconstrain long-horizon dynamics. Extending the maximum sampled training trajectory may teach the shared local rule to remain stable after repair instead of continuing to drift.

CONTROL H96
Existing M16 full-grid seed-0 control:
- training development steps: 64..96;
- maturity threshold: 16;
- training lesion: 0.50;
- evaluation lesion: 0.60.

CANDIDATE H128
Change only:
- training development steps: 64..128.

All other parameters remain identical to H96.

WHY ONE CANDIDATE
STAB-02 is a discriminating single-factor test. Additional horizon ranges will not be inserted after the result is inspected. If H128 fails, a different mechanism requires a new packet.

FIXED ENVELOPE
Seed: 0
Variant: regeneration
Grid: 40 x 40
State channels: 16
Hidden channels: 128
Fire rate: 0.5
Training iterations: 200
Learning rate: 0.001
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
- pre-lesion morphology error;
- RelativeDamageEffect;
- ActiveCellRemovalFraction;
- final active cells;
- training final/minimum loss;
- training wall-clock;
- checkpoint size.

VALID LESION REQUIREMENT
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10;
- finite state.

IMPROVEMENT RULE
H128 is worth widening only if all are true:
1. lesion is valid;
2. stable T50 is attained;
3. bounded final RecoveryFraction > 0.423023, the H96 control;
4. pre-lesion error <= 0.0361635, equal to 1.5x the H96 control pre-error;
5. final active cells <= 800 / 1600;
6. no non-finite state occurs.

RESOURCE NOTE
H128 necessarily consumes more developmental work per training update on average. If it improves repair, that improvement must later be weighed against added training/development cost. STAB-02 does not assume the extra cost is acceptable for the Yggdrasil north star.

FAILURE INTERPRETATION
If H128 fails, do not extend the horizon again inside STAB-02. Record whether failure is caused by:
- invalid lesion / excessive robustness;
- morphology degradation;
- continued relapse;
- active-cell explosion;
- numerical instability;
- no material change.

FIBONACCI RELATION
No Fibonacci schedule is introduced. FIB1 remains a later repair-budget ablation after canonical P0 dynamics are characterized.

NEXT ACTION
Train H128 from fresh initialization on seed 0, retain the result, and apply the improvement rule exactly as written.