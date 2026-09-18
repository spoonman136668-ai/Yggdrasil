TITLE: DG-1A-P0-STAB-17 — MATURE-VIS-ANCHOR-R1 Latent-Support / Visible-Morphology Coupling Preregistration
DATE: 2026-09-17
STATUS: PREREGISTERED — NOT YET EXECUTED
TRACK: DG-1A
CANDIDATE: MATURE-VIS-ANCHOR-R1 + FRONTIER-FLOOR-113 + LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16
CONFIDENCE: MECHANISTICALLY MOTIVATED / SINGLE-CANDIDATE TEST

QUESTION
Can canonical P0 preserve STAB-16's viable decoupled hidden-life substrate while improving formation occupancy, morphology, and lesion salience by making mature hidden life remain locally anchored to the organism's own visible phenotype rather than to the target mask?

SCIENTIFIC BASELINE
STAB-16 is the architectural baseline.

Preserve unchanged:
- visible morphology channels 0..3;
- visible alpha channel 3;
- hidden life channel 4;
- life threshold 0.1;
- FRONTIER-FLOOR-113;
- CEIL-800;
- ATTRACT-16;
- hidden L2 = 0.00001;
- canonical seed-0 envelope;
- all 14 scientific gates.

STAB-16 result:
- hidden-life collapse was eliminated;
- pre-damage hidden-life cells: 1082;
- final recovery hidden-life cells: 797;
- persistence: 1047 -> peak 1049 -> 750;
- persistence drift: -297;
- pre-lesion visible MSE: 0.0673088878;
- final persistence visible MSE: 0.0488450378;
- DamageEffect: -0.0051744804;
- RelativeDamageEffect: -0.0768766287;
- stable T50: not attained;
- 8 / 14 gates failed.

Interpretation:
decoupled hidden liveness is viable when given a minimal locally reachable floor, but much of the sustained hidden life remains morphologically redundant or negatively coupled to visible form.

STAB-12 remains the best overall phenotype by gate count.
STAB-17 tests the narrowed decoupled-life seam only.

EXTERNAL RESEARCH BASIS
Growing Neural Cellular Automata uses a local 3x3 neighborhood for life propagation and treats the visible alpha channel as the original coupling between viability and visible form (Mordvintsev et al., Distill 2020, DOI 10.23915/distill.00023).

Self-Organising Textures reports that unconstrained hidden channels organize structures and halos alongside visible features, suggesting that useful latent support can remain spatially related to visible morphology without being identical to it (Niklasson et al., Distill 2021).

Transient State Reorganization and Cell Differentiation in the Developmental Dynamics of Growing Neural Cellular Automata reports hidden-channel modularization and spatially coherent mature cell types developing in parallel with visible form (Sato, Masumori, Ikegami, arXiv:2607.15726, 2026).

Neural Cellular Automata: From Cells to Pixels maps local NCA cell states to appearance through a lightweight local decoder, further motivating local latent-to-visible coupling rather than global support-count pressure (Pajouheshgar et al., arXiv:2506.22899, 2025).

These references motivate the mechanism class only.
They do not determine gates or establish success.

SELECTED MECHANISM
MATURE-VIS-ANCHOR-R1

Exactly one new scientific factor is added to STAB-16:
a mature-only hidden-life anchoring loss that penalizes hard-alive hidden-life cells lacking any hard visible-alpha cell in their immediate 3x3 neighborhood.

The loss uses the organism's CURRENT visible alpha.
It does NOT use target geometry.

HARD STATE DEFINITIONS
For each normal-rollout sample:

Life =
    result channel 4

VisibleAlpha =
    result channel 3

HardAlive =
    1(Life > 0.1)

HardVisible =
    1(VisibleAlpha > 0.1)

HardLifeCount =
    sum(HardAlive)

Mature =
    HardLifeCount >= 113

VISIBLE NEIGHBORHOOD
Define:

VisibleNeighborhood =
    max_pool2d(
        HardVisible,
        kernel = 3,
        stride = 1,
        padding = 1
    ) > 0

This is a radius-1 Chebyshev neighborhood and matches the NCA's local 3x3 interaction geometry.

UNANCHORED HIDDEN LIFE
UnanchoredAlive =
    HardAlive AND NOT VisibleNeighborhood

A hidden-life cell is therefore considered spatially anchored if visible alpha >0.1 exists at that cell or any of its eight immediate neighbors.

The visible-alpha mask is a hard, detached routing mask for this loss.
MATURE-VIS-ANCHOR-R1 supplies NO direct gradient to visible alpha.

EXACT FORWARD ANCHOR ERROR
For each mature sample:

HardUnanchoredCount =
    sum(UnanchoredAlive)

HardUnanchoredFraction =
    HardUnanchoredCount / HardLifeCount

For immature samples:
the anchor loss is inactive.

Forward properties:
- exact range [0, 1];
- exact zero when every hard-alive hidden-life cell is within R1 of current hard visible alpha;
- no target mask enters the calculation;
- no fixed target support count is imposed;
- a visible one-cell support halo is permitted;
- auxiliary life inside that halo is permitted.

STRAIGHT-THROUGH GRADIENT
The exact hard forward fraction is discrete.

For each mature sample define:

AnchorCorrection =
    sum(
        (Life - stop_gradient(Life))
        * stop_gradient(UnanchoredAlive)
    )
    / stop_gradient(HardLifeCount)

Differentiable per-sample anchor loss:

MatureVisibleAnchorLoss =
    stop_gradient(HardUnanchoredFraction)
    + AnchorCorrection

Batch loss:
arithmetic mean over mature samples only.

If no samples are mature:
return differentiable zero.

Backward semantics:
- hard-alive hidden-life cells with no visible-alpha neighbor receive positive dL/dLife;
- gradient descent therefore pushes only unanchored hidden life downward;
- anchored hidden-life cells receive zero anchor gradient;
- dead hidden-life cells receive zero anchor gradient;
- visible alpha receives zero direct anchor gradient;
- RGB channels receive zero direct anchor gradient;
- other hidden channels receive zero direct anchor gradient.

This is explicitly a biased straight-through surrogate, not an exact derivative of hard thresholding.

WHY MATURE-ONLY
STAB-15 established that decoupled life collapses without positive viability support.
STAB-16 established FRONTIER-FLOOR-113 as the minimal positive viability mechanism.

Applying an anchor before viability is established could oppose the floor while visible morphology is still absent.

Therefore MATURE-VIS-ANCHOR-R1 activates only after the existing 113-cell maturity floor is reached.

This introduces no new maturity threshold.

WHY THIS IS NOT STAB-14
STAB-14 forced hard living support toward the TARGET foreground mask.

MATURE-VIS-ANCHOR-R1:
- never reads target geometry;
- anchors life to the organism's CURRENT visible phenotype;
- permits an R1 auxiliary support halo;
- does not penalize visible-target misses directly;
- does not require exact life/visible overlap;
- supplies gradient only to hidden life.

WHY THIS IS NOT STAB-07 / STAB-08
STAB-07 and STAB-08 altered static target-background visible-alpha weighting.

MATURE-VIS-ANCHOR-R1:
- leaves visible morphology loss unchanged;
- uses no target-distance map;
- penalizes only morphologically disconnected hidden life;
- operates on the decoupled hidden-life architecture.

WHY THIS IS NOT MORE RAW CARDINALITY PRESSURE
The anchor loss is a fraction of mature hidden life that is spatially disconnected from CURRENT visible alpha.

It is zero for any mature hidden-life count if all life is visibly anchored.

It does not change the 113 floor or 800 ceiling.
It does not add trajectory-wide raw count pressure.

CANONICAL CAPACITY SANITY CHECK
The canonical radius-6 visible target contains:
113 foreground cells.

Its radius-1 Chebyshev dilation on the 40 x 40 grid contains:
169 cells.

Therefore the fixed R1 anchor geometry has enough spatial capacity to satisfy the 113-cell viability floor around an ideal target-visible phenotype without requiring exact life-mask equality.

This is a preregistered feasibility observation only.
The number 169 is NOT used in the loss or as a gate.

FINAL TRAINING OBJECTIVE
TrainingMorphologyLoss =
    StaticMorphologyLoss
    + AttractorTrajectoryLoss
    + FormationLifeOccupancyCeilingLoss
    + FrontierFloorLoss
    + MatureVisibleAnchorLoss

All coefficients = 1.0.

StaticMorphologyLoss remains:
GlobalVisibleMSE
+ ForegroundVisibleMSE
+ BackgroundAlphaMSE

TEMPORAL SCOPE
MATURE-VIS-ANCHOR-R1 is applied to the normal rollout endpoint only.

Do NOT apply it to ATTRACT-16 future states inside STAB-17.

FRONTIER-FLOOR-113
Preserve STAB-16 exactly.

CEIL-800
Preserve STAB-16 exactly.

ATTRACT-16
Preserve STAB-16 exactly.

HIDDEN L2
Preserve 0.00001 exactly.

NEW HISTORICAL TRAINING MODE
Add exactly one mode:

global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_visanchor_r1

Preserve all prior historical modes unchanged.

CANONICAL FROZEN ENVELOPE
seed:                     0
variant:                  regeneration
grid:                     40 x 40
state channels:           16
hidden channels:          128
fire rate:                0.5
visible alpha channel:    3
alive channel:            4
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
target visible foreground:113
evaluation growth:        96
persistence:              96
recovery:                 96
evaluation lesion:        center 0.60 x 0.60
model max steps:          256
precision:                float32
sandbox device:           CPU
common morphology metric: global visible-channel MSE

FIXED STAB-17 FACTORS
life channel:                  4
visible alpha channel:         3
hard life threshold:           0.1
hard visible threshold:        0.1
anchor neighborhood:           exact 3x3 / R1 Chebyshev
anchor maturity floor:         113
anchor forward reduction:      unanchored / hard alive
anchor batch reduction:        arithmetic mean over mature samples
anchor coefficient:            1.0
anchor temporal scope:         normal endpoint only
viability floor:               113
occupancy ceiling:             800
ATTRACT horizon:               16
ATTRACT coefficient:           1.0
hidden L2:                     0.00001

No threshold, radius, coefficient, reduction, temporal-scope, floor, ceiling, hidden-L2, or ATTRACT sweep is permitted.

VIABILITY / OCCUPANCY GATES
All counts use hidden life channel 4:
- 113 <= pre-damage active cells <= 800;
- 113 <= final recovery active cells <= 800;
- 113 <= final persistence active cells <= 800;
- maximum active cells anywhere in persistence <= 800;
- final persistence active-cell drift <= 0.

LESION VALIDITY GATES
Visible morphology:
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10.

RECOVERY GATES
- stable T50 attained;
- final bounded RecoveryFraction > 0.4230230485.

MORPHOLOGY GATES
- pre-lesion global visible MSE <= 0.0361635;
- final persistence global visible MSE <= 0.0361635;
- maximum persistence MSE <= 2.0 * initial persistence MSE.

FINITE-STATE GATE
- no non-finite state during training, virtual persistence, growth, damage, recovery, or persistence.

IMPROVEMENT RULE
MATURE-VIS-ANCHOR-R1 is worth widening only if every preregistered gate passes.

Exactly one fresh seed-0 candidate.
No second seed.
No second candidate.
No anchor-radius sweep.
No visible-threshold sweep.
No coefficient sweep.
No target-mask anchor variant.
No future-trajectory anchor variant.
No floor/ceiling tuning.
No hidden-L2 tuning.

TRAINING TELEMETRY REQUIREMENTS
Record:
- global_morphology_mse;
- foreground_morphology_mse;
- background_alpha_mse;
- attractor_trajectory_loss;
- attractor_mature_samples;
- attractor_probe_steps = 16;
- formation_occupancy_ceiling_loss;
- formation_active_cells_mean;
- formation_active_cells_max;
- frontier_floor_loss;
- frontier_cells_mean;
- mature_visible_anchor_loss;
- anchor_mature_samples;
- unanchored_life_fraction_mean;
- unanchored_life_cells_mean;
- life_viability_floor = 113;
- formation_occupancy_ceiling = 800;
- life_channel = 4;
- visible_alpha_channel = 3;
- hidden penalty;
- gradient norm.

IMPLEMENTATION REQUIREMENTS
Before scientific execution:
- add one directly testable current-visible R1 neighborhood helper or equivalent;
- add one directly testable mature visible-anchor loss helper;
- hard life must use channel 4 >0.1;
- hard visible support must use channel 3 >0.1;
- neighborhood must be exact 3x3 max-pool / R1 Chebyshev;
- target tensor must not participate in anchor value or gradient;
- anchor must be inactive below 113 hard life cells;
- anchor forward error must equal unanchored hard-life fraction;
- anchor direct gradient must reach only hard-alive unanchored life-channel cells;
- visible channels must receive zero direct anchor gradient;
- preserve FRONTIER-FLOOR-113 unchanged;
- preserve CEIL-800 unchanged;
- preserve ATTRACT-16 unchanged;
- preserve hidden L2 unchanged;
- preserve normal and resumable training parity;
- preserve original-rollout-only pool updates;
- preserve RNG-neutral virtual trajectory;
- add additive tests for:
  * exact visible R1 neighborhood geometry;
  * same-cell visible alpha anchors life;
  * diagonal visible alpha anchors life;
  * distance-2 visible alpha does not anchor life;
  * immature samples produce differentiable zero anchor loss;
  * exact mature unanchored-fraction forward formula;
  * zero anchor loss when all life is R1-visible anchored;
  * positive life gradient only on hard-alive unanchored cells;
  * zero anchor gradient on anchored life;
  * zero anchor gradient on dead life;
  * zero direct visible/RGB/other-hidden gradient;
  * changing target geometry cannot change anchor value or gradient;
  * full objective formula;
  * STAB-16 compatibility;
  * normal telemetry;
  * resumable telemetry;
  * virtual-trajectory pool isolation;
  * frozen config;
  * runner evidence;
- complete reconstructed regression with zero failures.

TEST DISCIPLINE
Never disable, skip, comment out, or weaken a failing test.
Fix root cause.
If repair changes the preregistered scientific factor, stop and explicitly supersede or close STAB-17.

EXECUTION / PROVENANCE
Before execution:
1. implementation and tests committed;
2. exact GitHub source frozen;
3. complete reconstructed regression zero failures.

If native byte identity remains unavailable:
source_revision_verified_checkout = false
sandbox_source_byte_identity = false
evidence_class = MEASURED_SANDBOX

Use deterministic single-writer resumable checkpoints.
Never infer progress beyond the latest durable checkpoint.

STOP RULES
Stop and record negative immediately if:
- target geometry enters the anchor computation;
- visible channels receive direct anchor gradient;
- anchor acts on immature samples;
- anchor radius differs from exact R1 / 3x3;
- anchored life receives anchor gradient;
- dead life receives anchor gradient;
- FRONTIER-FLOOR, CEIL-800, ATTRACT-16, hidden L2, or canonical gates change;
- non-finite state/loss appears;
- checkpoint/config integrity fails;
- RNG neutrality or pool isolation fails;
- tests cannot be repaired without changing the scientific factor.

DISCRIMINATING INTERPRETATION
If hidden life remains viable/bounded while formation occupancy, visible morphology, and lesion salience improve, this supports the hypothesis that STAB-16's remaining defect is spatial disconnection between latent support and expressed morphology.

If hidden life collapses, mature-only visible anchoring is still too restrictive or destabilizes the viability band; do not reduce anchor coefficient or radius post-result.

If hidden life remains viable but visible morphology does not improve, simple R1 spatial anchoring is not sufficient evidence of functional usefulness; the next seam should move from spatial proximity to causal contribution.

If background visible-alpha artifacts rise while hidden life appears more anchored, the organism is gaming the endogenous anchor through visible output; do not switch to target-mask anchoring inside STAB-17.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling.

Fibonacci remains separate DG-1A-FIB1.

EXECUTION STATE
PREREGISTERED ONLY.
Do not execute until this exact spec is independently read back and branch HEAD independently verified.
