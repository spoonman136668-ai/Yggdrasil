TITLE: DG-1A-P0-STAB-14 — BALANCED-HARD-ALLOC Spatial Living-Support Allocation Preregistration
DATE: 2026-09-17
STATUS: PREREGISTERED — NOT YET EXECUTED
TRACK: DG-1A
CANDIDATE: BALANCED-HARD-ALLOC + CEIL-800 + ATTRACT-16
CONFIDENCE: MECHANISTICALLY MOTIVATED / SINGLE-CANDIDATE TEST

QUESTION
Can canonical P0 retain STAB-12's near-bounded formation and contractive ATTRACT-16 dynamics while improving morphology and lesion salience by explicitly aligning the hard living-support mask with the target foreground, rather than adding more raw cardinality pressure?

BASELINE
STAB-12 is the scientific baseline.

Preserve unchanged:
- StaticMorphologyLoss =
  GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAlphaMSE;
- ATTRACT-16 exactly as preregistered in STAB-11;
- endpoint CEIL-800 exactly as preregistered in STAB-12;
- canonical envelope and all 14 evaluation gates.

Do NOT inherit STAB-13 TRACE-CEIL-800 into this candidate.

STAB-12 directional baseline:
- pre-damage active: 857;
- persistence: 799 -> peak 1015 -> 623;
- drift: -176;
- final recovery active: 655;
- DamageEffect: positive;
- stable T50: 59;
- RecoveryFraction: 1.0;
- 5 / 14 gates failed.

STAB-13 showed that extending raw CEIL-800 pressure across the future trajectory was harmful:
- pre-damage active: 1193;
- persistence: 1130 -> peak 1517 -> 1456;
- drift: +326;
- lesion invalid;
- 11 / 14 gates failed.

Therefore STAB-14 returns to STAB-12 and changes support allocation, not temporal cardinality pressure.

EXTERNAL RESEARCH BASIS
Region-overlap losses such as Generalized Dice are used specifically to counter severe foreground/background class imbalance and optimize spatial overlap rather than raw pixelwise accuracy (Sudre et al., 2017, arXiv:1707.03237).

Tversky-style objectives explicitly separate false-positive and false-negative contributions, allowing spatial precision/recall errors to be controlled rather than conflated with total region size (Salehi et al., 2017, arXiv:1706.05721).

Growing Neural Cellular Automata trains a local rule toward a target morphology attractor and uses alpha as the visible liveness/morphology channel (Mordvintsev et al., Distill 2020, DOI 10.23915/distill.00023).

STAB-14 adapts the overlap principle to the exact hard alpha > 0.1 living-support semantics already used by canonical P0 evaluation.
It does not import segmentation performance claims into the NCA result.

SELECTED MECHANISM
BALANCED-HARD-ALLOC

Exactly one new scientific factor is introduced:
a class-balanced hard living-support allocation loss on the normal rollout endpoint.

HARD SUPPORT DEFINITIONS
For each normal rollout sample:

HardAlive =
    1(result alpha > 0.1)

TargetForeground =
    1(target alpha > 0.1)

TargetBackground =
    NOT TargetForeground

FalsePositiveAlive =
    HardAlive AND TargetBackground

FalseNegativeAlive =
    NOT HardAlive AND TargetForeground

Foreground cardinality is immutable from the target:
113 cells.

Background cardinality on the canonical 40 x 40 grid:
1487 cells.

EXACT FORWARD ALLOCATION ERROR
For each sample:

FalsePositiveRate =
    count(FalsePositiveAlive)
    / count(TargetBackground)

FalseNegativeRate =
    count(FalseNegativeAlive)
    / count(TargetForeground)

BalancedHardAllocationError =
    0.5 * FalsePositiveRate
    + 0.5 * FalseNegativeRate

Batch loss:
BalancedHardAllocationLoss =
    mean(BalancedHardAllocationError)

Forward properties:
- exact range [0, 1];
- exact zero iff the hard alive mask equals the target foreground mask;
- all-dead state has loss 0.5;
- all-alive state has loss 0.5;
- false positives and false negatives are class-normalized before equal weighting;
- the much larger background class therefore cannot numerically drown target-foreground misses.

TARGETED STRAIGHT-THROUGH GRADIENT
The exact hard forward loss is discrete.

Use a zero-forward surrogate correction:

FPGradientCorrection =
    sum(
        (alpha - stop_gradient(alpha))
        * stop_gradient(FalsePositiveAlive)
    )
    / count(TargetBackground)

FNGradientCorrection =
    - sum(
        (alpha - stop_gradient(alpha))
        * stop_gradient(FalseNegativeAlive)
    )
    / count(TargetForeground)

SurrogateCorrection =
    0.5 * FPGradientCorrection
    + 0.5 * FNGradientCorrection

Final differentiable allocation loss:
BalancedHardAllocationLoss =
    stop_gradient(BalancedHardAllocationError)
    + SurrogateCorrection

Forward semantics remain exactly the hard balanced error.

Backward semantics:
- active target-background cells: positive derivative, pushing alpha downward;
- inactive target-foreground cells: negative derivative, pushing alpha upward;
- correctly active target-foreground cells: zero allocation derivative;
- correctly inactive target-background cells: zero allocation derivative;
- RGB and hidden channels: zero direct allocation derivative.

This is explicitly a biased straight-through surrogate, not an exact derivative.

WHY THIS DIFFERS FROM STAB-06
STAB-06 applied broad threshold-aligned background pressure and crossed the viability bracket toward near-death.

BALANCED-HARD-ALLOC:
- acts only on hard misclassified support cells;
- does not push correctly inactive background;
- does not push correctly active target foreground;
- explicitly pushes missing target foreground upward;
- class-normalizes false positives and false negatives separately;
- therefore contains an intrinsic anti-death counterpressure absent from one-sided background suppression.

WHY THIS DIFFERS FROM STAB-07 / STAB-08
STAB-07 and STAB-08 changed continuous background-alpha spatial weighting.

BALANCED-HARD-ALLOC instead supervises the exact evaluation-relevant hard living-support classification at alpha > 0.1 and balances false-positive / false-negative rates.

It does not introduce a support halo or target-distance weighting.

FINAL TRAINING OBJECTIVE
TrainingMorphologyLoss =
    StaticMorphologyLoss(normal endpoint)
    + AttractorTrajectoryLoss
    + FormationOccupancyCeilingLoss
    + BalancedHardAllocationLoss

All coefficients:
1.0

ATTRACT-16 remains mature-only, exactly 16 future states, arithmetic-mean reduced.

CEIL-800 remains endpoint-only.

BALANCED-HARD-ALLOC is endpoint-only.
Do not apply it to ATTRACT future states inside STAB-14.

NEW HISTORICAL TRAINING MODE
Add exactly one new mode:

global_plus_foreground_bg_alpha_attractor_t16_ceil800_alloc_balanced_hard

Preserve all twelve previous modes unchanged, including the closed-negative STAB-13 mode.

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

FIXED STAB-14 FACTORS
hard alive threshold:          0.1
FP class weight:               0.5
FN class weight:               0.5
allocation coefficient:        1.0
allocation temporal scope:     normal endpoint only
ATTRACT horizon:               16
ATTRACT reduction:             arithmetic mean
ATTRACT coefficient:           1.0
endpoint occupancy ceiling:    800
endpoint ceiling coefficient:  1.0

No class-weight, coefficient, threshold, temporal-scope, ceiling, horizon, or reduction sweep is permitted.

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
BALANCED-HARD-ALLOC is worth widening only if every preregistered gate passes.

Exactly one fresh seed-0 candidate is permitted.
No second seed.
No second candidate.
No FP/FN weight sweep.
No coefficient sweep.
No threshold sweep.
No future-trajectory allocation variant inside STAB-14.

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
- support_allocation_loss;
- support_false_positive_rate;
- support_false_negative_rate;
- support_true_positive_cells_mean;
- total morphology loss;
- hidden penalty;
- gradient norm.

IMPLEMENTATION REQUIREMENTS BEFORE SCIENTIFIC RUN
- add one directly testable hard support-allocation helper;
- exact forward FP/FN rates must use alpha > 0.1;
- exact forward target classification must use target alpha > 0.1;
- class normalization must occur before 0.5/0.5 weighting;
- STE gradient must be restricted to hard FP and hard FN alpha cells only;
- preserve ATTRACT-16 semantics unchanged;
- preserve endpoint CEIL-800 semantics unchanged;
- preserve STAB-13 historical mode unchanged but do not use its TRACE loss;
- implement normal and resumable training;
- preserve original-rollout-only pool updates;
- add additive tests for:
  * exact zero on perfect hard support mask;
  * exact 0.5 all-dead forward loss;
  * exact 0.5 all-alive forward loss;
  * exact balanced FP/FN formula;
  * positive gradient only on hard FP alpha;
  * negative gradient only on hard FN alpha;
  * zero gradient on correct foreground/background;
  * zero direct RGB/hidden gradient;
  * full objective formula;
  * STAB-12 compatibility;
  * STAB-13 compatibility;
  * normal telemetry;
  * resumable telemetry;
  * pool isolation;
  * frozen config;
  * runner evidence mode/telemetry;
- run complete reconstructed regression with zero failures before scientific execution.

TEST DISCIPLINE
Never disable, skip, comment out, or weaken a failing test.
Fix the root cause.
If repair requires changing the preregistered scientific factor, stop and explicitly supersede/close the packet.

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
- hard support forward semantics diverge from alpha > 0.1 evaluation semantics;
- allocation gradient leaks into correctly classified cells, RGB, or hidden channels;
- ATTRACT-16 or endpoint CEIL-800 semantics change;
- non-finite rollout, virtual state, or loss appears;
- frozen config cannot be reproduced;
- checkpoint integrity fails;
- RNG-neutrality cannot be preserved;
- pool isolation cannot be preserved;
- a code/test failure cannot be repaired without changing the preregistered scientific factor.

If STAB-14 completes but any scientific gate fails:
- record CLOSED NEGATIVE;
- do not widen;
- do not change any frozen factor inside STAB-14.

DISCRIMINATING INTERPRETATION
If BALANCED-HARD-ALLOC preserves STAB-12 bounded/contractive behavior while reducing morphology error and increasing lesion salience, that supports the hypothesis that P0's remaining defect is spatial allocation of living support.

If viability collapses, the exact target-mask allocation pressure is too restrictive for the organism's required support structure; do not weaken gates or tune weights inside STAB-14.

If occupancy remains near-bounded but morphology/lesion salience do not improve, hard living-support overlap is not the dominant morphology seam.

If overgrowth returns, do not add more allocation pressure; inspect interaction between hard support classification and the developmental attractor in a new packet.

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
Do not execute until this exact spec has been independently read back and branch HEAD independently verified.
