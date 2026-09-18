TITLE: DG-1A-P0-STAB-12 — CEIL-800 + ATTRACT-16 Formation Occupancy Constraint Preregistration
DATE: 2026-09-17
STATUS: PREREGISTERED — NOT YET EXECUTED
TRACK: DG-1A
CANDIDATE: CEIL-800 + ATTRACT-16
CONFIDENCE: MECHANISTICALLY MOTIVATED / SINGLE-CANDIDATE TEST

QUESTION
Can canonical P0 retain the long-horizon contraction signal discovered in STAB-11 while preventing the phenotype from entering persistence already severely overgrown, by adding a one-sided formation-stage hard-occupancy ceiling constraint that is inactive everywhere inside the already accepted occupancy range?

PRIOR MECHANISTIC BRACKET
STAB-11 ATTRACT-16 produced the strongest long-horizon attractor-direction signal so far:
- persistence active cells: 1160 -> 592;
- persistence active-cell drift: -568;
- persistence MSE: 0.0616273582 -> 0.0547853708.

But it still failed canonical P0 because formation was severely overgrown:
- pre-damage active cells: 1252;
- persistence initial active cells: 1160;
- persistence peak active cells: 1335;
- lesion removed 44.01% of active cells and improved morphology;
- 9 / 14 preregistered gates failed.

Therefore STAB-12 changes formation-stage occupancy control while preserving ATTRACT-16 exactly.

EXTERNAL RESEARCH BASIS
Growing Neural Cellular Automata (Mordvintsev et al., Distill 2020, DOI 10.23915/distill.00023) uses an alpha-channel liveness threshold of 0.1 and frames persistence training as learning an attractor toward the target pattern.

Constrained-CNN losses for weakly supervised segmentation (Kervadec et al., Medical Image Analysis 2019, DOI 10.1016/j.media.2019.02.009) demonstrates that differentiable global inequality penalties can directly constrain region size/cardinality and specifically address over-segmentation.

Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation (Bengio, Leonard, Courville 2013, arXiv:1308.3432) introduces the straight-through estimator as a heuristic way to pass gradients through a discrete operation.

The STAB-12 straight-through path is therefore explicitly treated as a biased surrogate gradient. Scientific evaluation remains based on the exact hard alpha > 0.1 occupancy metric, not the surrogate.

SELECTED MECHANISM
CEIL-800 + ATTRACT-16

STAB-11 ATTRACT-16 remains unchanged.

Exactly one new scientific factor is added:
a formation-stage one-sided hard-active occupancy ceiling penalty.

THE CEILING IS NOT A NEW TUNED PARAMETER
The occupancy ceiling is inherited unchanged from the existing preregistered canonical viability/occupancy gate:

maximum accepted active cells = 800

No alternate ceiling is permitted inside STAB-12.

FORMATION HARD OCCUPANCY
For each normal rollout result sample:

alpha = result alpha channel
HardAlive = 1(alpha > 0.1)
HardActiveCount = sum(HardAlive over all grid cells)

The forward HardActiveCount must exactly equal the existing hard active-cell definition used by evaluation.

TARGET-BACKGROUND-ONLY STRAIGHT-THROUGH GRADIENT
The forward count remains exact and discrete.

Gradient is supplied only through cells that are:
- currently hard-active;
- target-background pixels.

Target foreground pixels receive zero gradient from the occupancy-ceiling term.

Inactive background pixels also receive zero gradient from the occupancy-ceiling term.

Define:

TargetBackground = 1(target alpha <= 0.1)

ActiveBackground = HardAlive * TargetBackground

SurrogateCorrection =
    sum(
        (alpha - stop_gradient(alpha))
        * ActiveBackground
    )

STEActiveCount =
    HardActiveCount
    + SurrogateCorrection

Forward semantics:
STEActiveCount == HardActiveCount exactly.

Backward semantics:
- derivative 1 through currently active target-background alpha cells;
- derivative 0 through target-foreground cells;
- derivative 0 through inactive target-background cells.

This is a deliberately local surrogate for the discrete hard-count constraint.
It must not be described as an exact gradient.

FORMATION OCCUPANCY CEILING LOSS
For each sample:

NormalizedExcess =
    ReLU(STEActiveCount - 800) / 800

FormationOccupancyCeilingLoss =
    mean(NormalizedExcess^2 across batch)

Properties required by contract:
- exact forward loss = 0 whenever hard active count <= 800;
- no occupancy-ceiling gradient when hard active count <= 800;
- no occupancy-ceiling gradient to target foreground;
- no occupancy-ceiling gradient to inactive target background;
- positive gradient only through active target-background cells when count > 800;
- maximum possible normalized excess on the canonical 1600-cell grid is 1.0.

WHY THIS DIFFERS FROM STAB-06
STAB-06 penalized broad target-background alpha activity beginning below the alive threshold and crossed into near-death.

CEIL-800:
- is completely inactive throughout the accepted occupancy region up to 800 cells;
- does not penalize undergrown or merely viable states;
- does not penalize target foreground;
- does not penalize inactive/near-threshold background cells while the hard count is within the accepted ceiling;
- activates only when the exact evaluation-relevant hard occupancy violates the already frozen gate.

ATTRACT-16 CONTRACT — UNCHANGED FROM STAB-11
Maturity:
hard active count >= immutable target foreground cardinality 113.

For mature samples only:
- exactly 16 sequential RNG-neutral virtual NCA steps;
- virtual states remain differentiable;
- virtual states never enter persistent pool authority;
- future states 1..16 receive:
  GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAlphaMSE;
- future losses are arithmetic-mean reduced;
- auxiliary coefficient = 1.0.

If no sample is mature, ATTRACT-16 auxiliary is differentiable zero.

BASE STATIC OBJECTIVE
For the normal rollout endpoint:

StaticMorphologyLoss =
    GlobalVisibleMSE
    + ForegroundVisibleMSE
    + BackgroundAlphaMSE

FINAL TRAINING OBJECTIVE
TrainingMorphologyLoss =
    StaticMorphologyLoss
    + AttractorTrajectoryLoss
    + FormationOccupancyCeilingLoss

All coefficients:
1.0

The occupancy-ceiling term is endpoint/formation-only.
Do not apply it to the 16 virtual ATTRACT states inside STAB-12.
This isolates formation occupancy from the already tested future-target trajectory signal.

NEW HISTORICAL TRAINING MODE
Add exactly one new mode:

global_plus_foreground_bg_alpha_attractor_t16_ceil800

Preserve unchanged:
1. global_mse
2. balanced_fg_bg
3. global_plus_foreground
4. global_plus_foreground_bg_alpha
5. global_plus_foreground_bg_alive_margin
6. global_plus_foreground_farfield_bg_alpha
7. global_plus_foreground_graded_bg_alpha
8. global_plus_foreground_bg_alpha_homeostasis
9. global_plus_foreground_bg_alpha_homeostasis_t16
10. global_plus_foreground_bg_alpha_attractor_t16

Do not rewrite prior modes.

CANONICAL FROZEN ENVELOPE
seed:                     0
variant:                  regeneration
grid:                     40 x 40
state channels:           16
hidden channels:          128
fire rate:                0.5
alive channel:            3
alive threshold:          0.1
training iterations:      200
learning rate:            0.001
development steps:        64..96
batch size:               8
pool size:                64
training damage prob:     0.50
training lesion:          center 0.50 x 0.50
damage minimum active:    16
gradient clip:            1.0
hidden L2:                0.00001
target:                   deterministic radius-6 disk
target foreground cells:  113
evaluation growth:        96
persistence:              96
recovery:                 96
evaluation lesion:        center 0.60 x 0.60
model max steps:          256
precision:                float32
sandbox device:           CPU
common evaluation metric: global visible-channel MSE

FIXED STAB-12 FACTORS
ATTRACT future horizon:       16
ATTRACT reduction:            arithmetic mean
ATTRACT coefficient:          1.0
hard alive threshold:         0.1
formation occupancy ceiling:  800
ceiling normalization:        800
ceiling exponent:             square
ceiling coefficient:          1.0
STE gradient scope:           currently active target-background cells only

No alternate ceiling, normalization, exponent, gradient scope, coefficient, horizon, or reduction is permitted inside STAB-12.

VIABILITY / OCCUPANCY GATES
All must hold:
- 113 <= pre-damage active cells <= 800;
- 113 <= final recovery active cells <= 800;
- 113 <= final persistence active cells <= 800;
- maximum active cells anywhere in persistence <= 800;
- final persistence active-cell drift <= 0.

LESION VALIDITY GATES
All must hold:
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10.

RECOVERY GATES
All must hold:
- stable T50 attained;
- final bounded RecoveryFraction > 0.4230230485.

MORPHOLOGY GATES
All must hold:
- pre-lesion global MSE <= 0.0361635;
- final persistence global MSE <= 0.0361635;
- maximum persistence MSE <= 2.0 * initial persistence MSE.

FINITE-STATE GATE
- no non-finite state during training, virtual persistence, growth, damage, recovery, or persistence.

IMPROVEMENT RULE
CEIL-800 + ATTRACT-16 is worth widening only if every preregistered gate passes.

Exactly one fresh seed-0 candidate is permitted in STAB-12.
No second seed.
No second candidate.
No ceiling sweep.
No coefficient sweep.
No STE variant sweep.
No ATTRACT horizon/reduction sweep.

TRAINING TELEMETRY REQUIREMENTS
Record at normal reporting cadence:
- global_morphology_mse;
- foreground_morphology_mse;
- background_alpha_mse;
- attractor_trajectory_loss;
- attractor_mature_samples;
- attractor_probe_steps = 16;
- formation_occupancy_ceiling_loss;
- formation_active_cells_mean;
- formation_active_cells_max;
- formation_occupancy_ceiling = 800;
- total morphology loss;
- hidden penalty;
- gradient norm.

IMPLEMENTATION REQUIREMENTS BEFORE SCIENTIFIC RUN
- add one directly testable formation occupancy-ceiling helper;
- helper forward count must exactly match hard alpha > 0.1 occupancy;
- helper backward must be restricted to active target-background cells when ceiling is violated;
- preserve ATTRACT-16 helper and semantics unchanged;
- preserve HOME-1 and HOME-T16 semantics unchanged;
- add exactly one historical STAB-12 loss mode;
- implement in normal and resumable training;
- preserve pool update semantics: original rollout result only;
- add additive tests for:
  * exact zero loss at 800 active cells;
  * exact positive formula above 800;
  * exact hard-count forward semantics;
  * zero gradient at/below ceiling;
  * zero target-foreground gradient above ceiling;
  * zero inactive-background gradient above ceiling;
  * positive active-background gradient above ceiling;
  * full objective formula;
  * ATTRACT-16 compatibility;
  * normal telemetry;
  * resumable telemetry;
  * virtual trajectory pool isolation remains unchanged;
  * frozen config;
  * runner evidence mode/telemetry;
- run the complete reconstructed regression with zero failures before scientific execution.

TEST DISCIPLINE
Never disable, skip, comment out, or weaken a failing test.
Fix the root cause.
If a code/test failure cannot be repaired without changing the preregistered scientific factor, stop and close or supersede this packet explicitly.

EXECUTION / PROVENANCE CONTRACT
Before scientific execution:
1. implementation and tests must be committed;
2. exact GitHub source revision must be frozen;
3. complete reconstructed regression must report zero failures.

If native byte-identical checkout remains unavailable:
- source_revision_verified_checkout = false;
- sandbox_source_byte_identity = false;
- evidence_class = MEASURED_SANDBOX;
- record exact connected-GitHub revision used as reconstruction basis.

Use deterministic single-writer resumable checkpoints for the canonical 200-iteration run.
Never infer progress beyond the latest durable checkpoint.

STOP RULES
Stop and record negative immediately if:
- hard-count forward semantics diverge from evaluation active-cell semantics;
- STE gradient leaks into target foreground or inactive background;
- non-finite rollout, virtual state, or loss appears;
- frozen config cannot be reproduced;
- checkpoint integrity fails;
- RNG-neutrality cannot be preserved;
- pool isolation cannot be preserved;
- a code/test failure cannot be repaired without changing the preregistered scientific factor.

If STAB-12 completes but any scientific gate fails:
- record CLOSED NEGATIVE;
- do not widen;
- do not change the ceiling, normalization, exponent, STE scope, coefficient, ATTRACT horizon, target, envelope, or gates inside STAB-12.

DISCRIMINATING INTERPRETATION
If CEIL-800 + ATTRACT-16 preserves STAB-11's contractive persistence while bringing formation occupancy inside <=800 and restoring lesion validity/morphology, that supports the hypothesis that STAB-11's main remaining defect was excessive formation support rather than the attractor direction itself.

If formation occupancy remains >800, the hard-ceiling surrogate is too weak or poorly aligned; do not tune it inside STAB-12.

If viability collapses despite the term being forward-zero below 800, record the failure and inspect surrogate/dynamics interactions in a new packet rather than weakening gates.

If occupancy becomes bounded but lesion/morphology remain invalid, the next seam is morphology/support allocation rather than raw cardinality.

BOUNDARY
This packet remains canonical DG-1A P0 morphology/developmental-substrate research only.

Do not begin:
- DG-1B functional computation;
- ancestor inheritance;
- structural growth;
- developmental adapters;
- Fibonacci scheduling.

Fibonacci remains separate DG-1A-FIB1.

EXECUTION STATE
PREREGISTERED ONLY.
Do not execute until this exact spec has been independently read back and branch HEAD has been independently verified.
