TITLE: DG-1A-P0-STAB-16 — FRONTIER-FLOOR-113 Hidden-Life Viability Band Preregistration
DATE: 2026-09-17
STATUS: PREREGISTERED — NOT YET EXECUTED
TRACK: DG-1A
CANDIDATE: FRONTIER-FLOOR-113 + LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16
CONFIDENCE: MECHANISTICALLY MOTIVATED / SINGLE-CANDIDATE TEST

QUESTION
Can a decoupled hidden-life architecture avoid the STAB-15 collapse if it receives a target-derived minimum viable cardinality signal through only the locally reachable growth frontier, while retaining the STAB-12 upper occupancy bound and ATTRACT-16 visible-morphology attractor supervision?

PRIOR MECHANISTIC BRACKET
STAB-15 LIFE4-DECOUPLE:
- hidden life channel 4;
- visible morphology channels 0..3;
- no direct life target;
- unchanged hidden L2;
- CEIL-800 upper bound;
- mature-only ATTRACT-16.

Result:
- hidden life never reached maturity;
- pre-damage life count: 1;
- persistence: 1 -> 0;
- recovery final: 0;
- foreground morphology MSE remained ~0.406;
- global visible MSE looked low only because near-blank output is cheap on the sparse target;
- 6 / 14 gates failed.

Interpretation:
an upper bound cannot create missing viability, and mature-only ATTRACT cannot help if the organism never reaches maturity.

STAB-16 preserves the decoupled architecture and adds exactly one positive viability mechanism.

EXTERNAL RESEARCH BASIS
Growing Neural Cellular Automata defines liveness locally: a cell can participate when a mature live cell exists in its 3x3 neighborhood, and empty cells are zeroed. This makes the immediate live-neighborhood frontier the mechanically reachable growth surface.

From Cells to Societies describes NCA cells as target channels, a living channel, and hidden memory channels, supporting a dedicated living-channel formulation.

These references motivate a local growth-frontier viability signal.
They do not determine STAB-16 gates or establish success.

SELECTED MECHANISM
FRONTIER-FLOOR-113

Exactly one new scientific factor is added to STAB-15:
a one-sided hidden-life minimum cardinality constraint whose surrogate gradient is restricted to the immediate locally reachable life frontier.

The lower bound is not tuned.
It is inherited from the canonical viability floor and visible-target foreground cardinality:

minimum viable hidden-life cells = 113

LIFE ARCHITECTURE
Preserve STAB-15:
- visible morphology channels: 0..3;
- visible alpha channel: 3;
- hidden life channel: 4;
- life threshold: 0.1;
- target channel 4: zero;
- seed: channel 4 center = 1.0 only;
- hidden L2 unchanged at 0.00001;
- all canonical active-cell metrics use channel 4.

HARD LIFE COUNT
For each normal rollout result sample:

Life = result channel 4
HardAlive = 1(Life > 0.1)
HardLifeCount = sum(HardAlive)

The forward count must exactly match canonical active_cell_count(... alive_channel=4, alive_threshold=0.1).

LOCALLY REACHABLE GROWTH FRONTIER
Define:

LiveNeighborhood =
    max_pool2d(HardAlive, kernel=3, stride=1, padding=1) > 0

GrowthFrontier =
    LiveNeighborhood AND NOT HardAlive

Properties:
- hard-active cells are not frontier;
- only dead cells directly neighboring current hard life are frontier;
- cells with no live neighbor receive zero floor gradient;
- target geometry is NOT used to choose frontier cells.

This matches the existing NCA masking geometry: only cells in a live neighborhood can retain/update state and become new organism cells.

STRAIGHT-THROUGH FLOOR COUNT
Forward semantics remain exact hard cardinality.

Define zero-forward frontier correction:

FrontierCorrection =
    sum(
        (Life - stop_gradient(Life))
        * GrowthFrontier
    )

STEFloorCount =
    HardLifeCount + FrontierCorrection

Forward:
STEFloorCount == HardLifeCount exactly.

Backward:
derivative 1 only through hidden-life values on GrowthFrontier cells.

This is explicitly a biased surrogate gradient, not an exact derivative of hard count.

FRONTIER-FLOOR-113 LOSS
For each sample:

NormalizedDeficit =
    ReLU(113 - STEFloorCount) / 113

FrontierFloorLoss =
    mean(NormalizedDeficit^2 across batch)

coefficient = 1.0

Required properties:
- exact forward loss = 0 when hard life count >=113;
- positive loss when hard life count <113;
- zero floor gradient when count >=113;
- zero floor gradient through already-live cells;
- zero floor gradient through non-frontier dead cells;
- negative dL/dLife on frontier cells while count <113, so gradient descent pushes locally reachable life upward;
- no visible channel receives direct floor gradient;
- no target-visible spatial mask enters this loss.

WHY THIS IS NOT A LIFE TARGET MASK
FRONTIER-FLOOR-113 specifies only a minimum global viable cardinality and local growth reachability.

It does NOT specify:
- which 113 cells must be alive;
- that life must equal visible foreground;
- that life must be confined to visible target geometry;
- a target value for channel 4.

Visible morphology remains governed by the existing visible losses.

VIABILITY BAND
STAB-16 therefore creates the existing canonical viability band:

lower bound:
FRONTIER-FLOOR-113

upper bound:
CEIL-800

Both are zero inside the accepted 113..800 occupancy interval.

CEIL-800
Preserve STAB-15 exactly:
- count hidden-life channel 4;
- ceiling = 800;
- target visible-alpha geometry protects target-foreground positions from downward ceiling gradient;
- active target-background life receives downward STE pressure only when hard life count >800;
- coefficient 1.0.

No ceiling tuning.

ATTRACT-16
Preserve STAB-15 exactly:
- maturity when hidden-life hard count >= visible target foreground cardinality 113;
- 16 RNG-neutral future steps;
- visible morphology loss only on channels 0..3;
- no hidden-life target;
- arithmetic mean;
- coefficient 1.0;
- pool isolation unchanged.

STATIC VISIBLE OBJECTIVE
StaticMorphologyLoss =
GlobalVisibleMSE
+ ForegroundVisibleMSE
+ BackgroundAlphaMSE

FINAL TRAINING OBJECTIVE
TrainingMorphologyLoss =
StaticMorphologyLoss
+ AttractorTrajectoryLoss
+ FormationLifeOccupancyCeilingLoss
+ FrontierFloorLoss

All coefficients = 1.0.

If hidden life is below 113:
- ATTRACT remains inactive;
- FRONTIER-FLOOR supplies the positive viability signal.

When hidden life reaches 113:
- FRONTIER-FLOOR becomes zero;
- ATTRACT can activate;
- CEIL remains zero until count exceeds 800.

NEW HISTORICAL TRAINING MODE
Add exactly one new mode:

global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800

Preserve all prior modes unchanged.

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

FIXED STAB-16 FACTORS
life channel:                  4
life threshold:                0.1
viability floor:               113
floor normalization:           113
floor exponent:                square
floor coefficient:             1.0
floor gradient scope:          dead cells in 3x3 hard-life neighborhood only
occupancy ceiling:             800
ceiling coefficient:           1.0
ATTRACT horizon:               16
ATTRACT coefficient:           1.0
hidden L2:                     0.00001

No alternate floor, normalization, exponent, frontier radius, frontier definition, coefficient, life channel, threshold, ceiling, hidden-L2 treatment, ATTRACT horizon, or reduction is permitted.

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
FRONTIER-FLOOR-113 + LIFE4 is worth widening only if every preregistered gate passes.

Exactly one fresh seed-0 candidate.
No second seed.
No floor sweep.
No frontier-radius sweep.
No coefficient sweep.
No hidden-L2 tuning.
No direct life target.
No visible-alpha reseeding.

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
- life_viability_floor = 113;
- life_channel = 4;
- visible_alpha_channel = 3;
- total morphology loss;
- hidden penalty;
- gradient norm.

IMPLEMENTATION REQUIREMENTS
Before scientific execution:
- add one directly testable hidden-life frontier helper;
- add one directly testable FRONTIER-FLOOR-113 loss helper;
- hard count must exactly match channel-4 active-cell metric;
- frontier must be 3x3 hard-live neighborhood minus hard-live cells;
- floor gradient must be restricted to frontier hidden-life values;
- no visible direct gradient from floor;
- preserve LIFE4 decoupling;
- preserve CEIL-800;
- preserve ATTRACT-16;
- preserve hidden L2;
- preserve pool semantics and RNG neutrality;
- implement normal and resumable training;
- add additive tests for:
  * single seed produces eight-cell geometric frontier around center;
  * hard-active center excluded from frontier;
  * remote dead cell excluded;
  * exact hard-count forward semantics;
  * exact floor formula at counts 1, 112, 113;
  * floor zero and zero gradient at >=113;
  * negative life gradient only on frontier below floor;
  * zero gradient on live cells;
  * zero visible-channel gradient;
  * target geometry does not alter frontier-floor value/gradient;
  * CEIL and ATTRACT semantics unchanged;
  * full objective formula;
  * normal telemetry;
  * resumable telemetry;
  * frozen config;
  * runner evidence;
  * historical modes remain compatible;
- complete reconstructed regression with zero failures.

TEST DISCIPLINE
Never disable, skip, comment out, or weaken a failing test.
Fix root cause.
If repair changes the preregistered factor, stop and explicitly supersede or close STAB-16.

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

STOP RULES
Stop and record negative immediately if:
- frontier geometry differs from 3x3 hard-life neighborhood minus live cells;
- floor direct gradient reaches visible channels or non-frontier cells;
- floor remains nonzero at hard count >=113;
- canonical active-cell paths cease using channel 4;
- target channel 4 becomes supervised/populated;
- hidden L2 is changed;
- non-finite state/loss appears;
- checkpoint/config integrity fails;
- RNG neutrality or pool isolation fails;
- tests require changing the scientific factor.

DISCRIMINATING INTERPRETATION
If hidden life reaches and remains within 113..800 and visible morphology/lesion gates improve, this supports the hypothesis that decoupled life is viable when given only a minimal local positive viability constraint.

If hidden life still collapses, a simple cardinality floor on the reachable frontier is insufficient; do not increase its coefficient or radius inside STAB-16.

If hidden life explodes above 800, the viability floor destabilizes occupancy despite CEIL-800; do not tune the band post-result.

If life becomes viable but visible morphology remains poor, hidden-life collapse was only one problem and the next seam is functional coupling between latent support and visible morphology.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling.

Fibonacci remains separate DG-1A-FIB1.

EXECUTION STATE
PREREGISTERED ONLY.
Do not execute until exact spec is independently read back and branch HEAD independently verified.
