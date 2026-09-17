TITLE: DG-1A-P0 Full-Grid Seed-0 Exploratory Bring-Up
DATE: 2026-09-17
STATUS: PREREGISTERED EXPLORATORY RUN
TRACK: DG-1A
CONFIDENCE: SUPPORTED AS NEXT SCALE STEP

QUESTION
Does the small-grid growth-versus-regeneration separation survive an initial scale-up to the repository's 40 x 40 P0 envelope without numerical or resource failure?

PURPOSE
Scale only the already-observed P0 mechanism. This is not a new cognitive task and does not open DG-1B.

EVIDENCE CLASS
EXPLORATORY.

SEED
0 only for bring-up.

VARIANTS
growth_only
maturity-gated regeneration

MODEL
Grid: 40 x 40
State channels: 16
Hidden channels: 128
Fire rate: 0.5
Alive threshold: 0.1
Maximum development steps: 256

TARGET
Repository-native disk
Radius: 6
RGBA: [0.15, 0.75, 0.30, 1.0]

TRAINING
Iterations: 200
Learning rate: 0.001
Development horizon: uniformly sampled 64..96
Batch size: 8
Pool size: 64 for regeneration
Gradient clip: 1.0
Hidden-state L2 weight: 0.00001

REGENERATION CURRICULUM
Damage probability: 0.5
Maturity threshold: 16 active cells
Training center-lesion fraction: 0.50 x 0.50

The training lesion remains 0.50 to preserve the mechanism used in the successful small-grid sandbox family. Calibration changed the EVALUATION lesion, not this training curriculum.

EVALUATION
Growth horizon: 96
Recovery horizon: 96
Center-lesion fraction: 0.60 x 0.60

LESION VALIDITY
Unchanged:
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10;
- finite states.

RESUMABILITY
The run may execute in deterministic segments using ResumableTrainingSession.

A segmented run is valid for exploratory comparison only if repository tests establish:
1. uninterrupted ResumableTrainingSession matches existing train() semantics;
2. checkpoint/restore produces identical model state and recorded history to uninterrupted resumable training;
3. phenotype-pool state is included and deep-copied;
4. optimizer and RNG states are restored.

Segment boundaries must not reset optimizer, state pool, RNG, or model state.

PRIMARY OBSERVATIONS
- training finite/non-finite status;
- final and minimum recorded morphology loss;
- pre/post lesion error;
- lesion validity;
- bounded RecoveryFraction;
- stable T50/T90;
- recovery AUC;
- final active cells;
- resource snapshot;
- accumulated training wall-clock;
- checkpoint size where measured.

BRING-UP INTERPRETATION
This single seed does not support or disprove H-P0-3 by itself.

Useful outcomes:
- both variants train and evaluate finitely;
- lesion protocol remains measurable;
- regeneration does not collapse merely because grid/horizon/hidden width increased;
- resource use remains within the home-hardware research envelope.

FAILURE RECORDING
Any OOM, non-finite state, unstable runaway, invalid lesion, or resume mismatch is retained as a negative result. Do not reduce assertions or silently change the configuration to make the run pass.

FIBONACCI RELATION
No Fibonacci scheduling is introduced. FIB1 remains a later ablation against a stabilized P0 substrate.

NEXT ACTION
Execute growth-only and regeneration seed 0 in deterministic resume segments and record complete evidence before widening to additional full-grid seeds.