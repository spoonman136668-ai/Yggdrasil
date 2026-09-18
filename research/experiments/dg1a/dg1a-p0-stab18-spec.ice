TITLE: DG-1A-P0-STAB-18 — CAUSAL-LATENT-DROPOUT25-PRUNE-T16 Preregistration
DATE: 2026-09-18
STATUS: PREREGISTERED — NOT YET EXECUTED
TRACK: DG-1A
CANDIDATE: CAUSAL-LATENT-DROPOUT25-PRUNE-T16 + FRONTIER-FLOOR-113 + LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16
CONFIDENCE: MECHANISTICALLY MOTIVATED / SINGLE-CANDIDATE TEST

QUESTION
Can canonical P0 preserve STAB-16's viable decoupled hidden-life substrate while reducing morphologically redundant support by pruning mature latent support whose controlled virtual removal does not worsen future target-visible morphology?

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

STAB-17 remains historical compatibility only.
Do NOT carry MATURE-VIS-ANCHOR-R1 into STAB-18.

WHY STAB-17 IS NOT THE BASELINE
STAB-17 showed that simple R1 proximity between hidden life and visible alpha was already satisfied for most mature checkpoints and did not improve canonical morphology or lesion salience.

Therefore STAB-18 returns to STAB-16's decoupled-life architecture and replaces the failed proximity proxy with one controlled causal intervention.

EXTERNAL RESEARCH BASIS
Growing Neural Cellular Automata treats hidden channels as internal signaling/state used by local cells to coordinate development and regeneration (Mordvintsev et al., Distill 2020, DOI 10.23915/distill.00023).

Adversarial Reprogramming of Neural Cellular Automata demonstrates that perturbing internal cell state can causally alter global morphology and behavior, supporting intervention rather than static correlation as a probe of hidden-state function (Randazzo et al., Distill 2021).

Self-Organising Textures reports organized latent structure and explicitly motivates perturbing hidden states to understand their morphological role (Niklasson et al., Distill 2021).

Structured Fluctuations and the Information Dynamics of Self-Maintenance in Growing Neural Cellular Automata reports that suppressing distributed internal update activity can impair repair, further supporting causal perturbation as a way to distinguish functionally relevant latent dynamics (Masumori, Sato, Ikegami, arXiv:2607.12403, 2026).

These sources motivate intervention as the mechanism class only.
They do not determine gates and do not establish success.

SELECTED MECHANISM
CAUSAL-LATENT-DROPOUT25-PRUNE-T16

Exactly one new scientific factor is added to STAB-16:
a mature-only, RNG-neutral counterfactual latent-state dropout probe whose detached causal outcome gates a one-sided hidden-life pruning straight-through gradient.

The probe asks:
"If a distributed subset of this mature organism's latent support is removed while its current visible RGBA phenotype is initially held fixed, does its future visible target trajectory get worse?"

If YES:
the probed support group is treated as beneficial and receives ZERO causal-prune gradient.

If NO:
the probed support group is treated as non-beneficial/harmful and receives a downward gradient only through hidden life channel 4 at the probed cells.

The mechanism NEVER rewards a larger damage effect.
It only prunes support that fails the causal usefulness test.

MATURITY
Use the unchanged STAB-16 decoupled maturity condition:

HardAlive =
    Life4 > 0.1

HardLifeCount =
    sum(HardAlive)

Mature =
    HardLifeCount >= 113

The causal probe is inactive for immature samples.

DROPOUT PROBE FRACTION
Fixed latent dropout fraction:

CAUSAL_DROPOUT_FRACTION = 0.25

Derivation:
the inherited canonical training lesion occupies 0.5 x 0.5 of the active bounding box, corresponding to an area fraction of 0.25.

The STAB-18 0.25 value is therefore inherited from the existing canonical damage envelope, not tuned from STAB-18 results.

No fraction sweep is permitted.

RNG-NEUTRAL DISTRIBUTED PROBE MASK
For each mature sample:

RandomValue[y,x] ~ Uniform(0,1)
ProbeDrop[y,x] =
    HardAlive[y,x]
    AND RandomValue[y,x] < 0.25

The random probe must:
- use the existing device generator;
- save generator state before mask sampling;
- restore it immediately afterward;
- therefore consume ZERO durable RNG state;
- be exactly reproducible from a checkpoint;
- not alter normal rollout randomness.

The actual dropped-cell fraction is recorded because Bernoulli 0.25 is not an exact-count sampler.

LATENT-ONLY INTERVENTION
For ProbeDrop cells:

Preserve channels 0..3 exactly at intervention time.

Set channels 4..15 to zero.

Thus:
- current RGB is not directly erased;
- current visible alpha is not directly erased;
- hidden life channel 4 is removed;
- all other hidden/latent channels are removed.

This isolates the future causal role of latent support rather than trivially scoring direct deletion of visible phenotype.

Call the resulting state:

CounterfactualStart

MATCHED FUTURE TRAJECTORIES
Use the existing fixed ATTRACT-16 horizon.

For each mature sample compute:

IntactTrajectory =
    16 RNG-neutral future model steps from MatureResult

CounterfactualTrajectory =
    16 RNG-neutral future model steps from CounterfactualStart

Both trajectories MUST use the exact same stochastic update sequence.

The existing RNG-neutral trajectory helper restores generator state after each trajectory.
No RNG-consuming operation may occur between the saved starting state and the two matched virtual trajectories except an RNG-neutral probe-mask helper that also restores generator state.

Neither virtual trajectory may be written to the training pool.

PER-SAMPLE VISIBLE TARGET LOSS
For each future state and sample compute exactly the same three visible components used by ATTRACT-16:

GlobalVisibleMSE
+ ForegroundVisibleMSE
+ BackgroundAlphaMSE

Average over the 16 future steps separately for each sample.

Define:

IntactFutureLoss[i]

CounterfactualFutureLoss[i]

CausalDelta[i] =
    stop_gradient(
        CounterfactualFutureLoss[i]
        - IntactFutureLoss[i]
    )

Interpretation:
- CausalDelta > 0:
  removing the sampled latent support worsened future target-visible morphology;
  sampled group is BENEFICIAL.
- CausalDelta <= 0:
  removing the sampled latent support did not worsen future target-visible morphology;
  sampled group is NON-BENEFICIAL for this intervention.

The exact threshold is 0.
No epsilon or margin is introduced.

ONE-SIDED CAUSAL PRUNING GATE
For mature sample i:

NonBeneficial[i] =
    1(CausalDelta[i] <= 0)

DroppedAliveCount[i] =
    sum(ProbeDrop[i])

HardLifeCount[i] =
    sum(HardAlive[i])

HardPruneFraction[i] =
    NonBeneficial[i]
    * DroppedAliveCount[i]
    / HardLifeCount[i]

The causal outcome and all hard masks are detached for the pruning surrogate.

STRAIGHT-THROUGH PRUNING GRADIENT
Let Life denote result channel 4.

For mature sample i:

PruneCorrection[i] =
    sum(
        (Life - stop_gradient(Life))
        * stop_gradient(ProbeDrop)
        * stop_gradient(NonBeneficial[i])
    )
    / stop_gradient(HardLifeCount[i])

PerSampleCausalPruneLoss[i] =
    stop_gradient(HardPruneFraction[i])
    + PruneCorrection[i]

Batch loss:
arithmetic mean over mature samples only.

If no samples are mature:
return differentiable zero.

If a mature sample happens to draw zero probed live cells:
its causal prune contribution is differentiable zero and it is excluded from causal-delta classification telemetry.

BACKWARD SEMANTICS
CAUSAL-LATENT-DROPOUT25-PRUNE-T16 supplies direct gradient ONLY to:
- channel 4;
- currently hard-alive cells;
- cells selected by ProbeDrop;
- samples whose CausalDelta <= 0.

Gradient sign:
positive dL/dLife4 at those cells;
gradient descent pushes their life value downward.

The causal-prune term supplies ZERO direct gradient to:
- beneficial probed groups;
- unprobed live cells;
- dead cells;
- visible RGBA channels;
- hidden channels 5..15;
- target tensor;
- intact virtual trajectory;
- counterfactual virtual trajectory.

The counterfactual trajectories are measurement-only for the causal gate.
No gradient from CounterfactualFutureLoss is added to the training objective.

WHY THIS DOES NOT DIRECTLY REWARD FRAGILITY
STAB-18 does NOT maximize CausalDelta.

A beneficial group with positive CausalDelta receives zero causal-prune gradient whether its delta is:
+0.000001
or
+100.

There is no reward for making the organism more dependent on a cell.

The only causal-prune action is:
remove life support that, when virtually removed as part of the sampled group, does not worsen future target-visible morphology.

The existing:
- viability floor;
- occupancy ceiling;
- ATTRACT-16 target trajectory;
- regeneration curriculum;
- and canonical damage/recovery gates
remain responsible for preventing collapse or brittle minimal-support solutions.

WHY THIS IS NOT STAB-13
STAB-13 applied raw occupancy pressure across future trajectories.

STAB-18:
- does not penalize future active count;
- uses future trajectories only to measure intervention outcome;
- applies pruning only at sampled endpoint life cells whose latent removal is non-beneficial.

WHY THIS IS NOT STAB-14
STAB-14 used direct target-mask support allocation.

STAB-18:
- never compares hidden-life geometry with the target mask;
- uses target only through scalar visible morphology error after a controlled intervention;
- does not require any cell to live at a target foreground coordinate.

WHY THIS IS NOT STAB-17
STAB-17 asked whether life is spatially near visible alpha.

STAB-18 asks whether removing sampled latent state causes future visible target morphology to worsen.

The criterion is causal effect, not proximity.

WHY LATENT-ONLY RATHER THAN FULL-CELL ABLATION
Full-cell deletion would erase current visible RGBA directly and could trivially label visibly expressed cells as important.

STAB-18 preserves channels 0..3 at intervention time and removes channels 4..15 only.

Any later visible difference must therefore emerge through the altered latent/life dynamics.

FINAL TRAINING OBJECTIVE
TrainingMorphologyLoss =
    StaticMorphologyLoss
    + AttractorTrajectoryLoss
    + FormationLifeOccupancyCeilingLoss
    + FrontierFloorLoss
    + CausalLatentPruneLoss

All coefficients = 1.0.

StaticMorphologyLoss remains:
GlobalVisibleMSE
+ ForegroundVisibleMSE
+ BackgroundAlphaMSE

ATTRACT-16
Preserve unchanged.

The intact 16-step trajectory may be reused for both:
- existing ATTRACT-16 objective;
- detached STAB-18 per-sample causal comparison.

FRONTIER-FLOOR-113
Preserve STAB-16 exactly.

CEIL-800
Preserve STAB-16 exactly.

HIDDEN L2
Preserve 0.00001 exactly.

MATURE-VIS-ANCHOR-R1
NOT included in the STAB-18 objective.

NEW HISTORICAL TRAINING MODE
Add exactly one mode:

global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16

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

FIXED STAB-18 FACTORS
life channel:                       4
visible channels preserved:         0..3
latent channels ablated:            4..15
hard life threshold:                0.1
causal maturity floor:              113
causal latent dropout fraction:     0.25
causal future horizon:              16
causal future loss:                 ATTRACT-16 visible loss components
causal decision threshold:          0
causal prune coefficient:           1.0
causal probe scope:                 normal endpoint, mature samples only
causal probe gradient path:         detached outcome -> life4 STE only
viability floor:                    113
occupancy ceiling:                  800
ATTRACT horizon:                    16
ATTRACT coefficient:                1.0
hidden L2:                          0.00001

No fraction, horizon, threshold, coefficient, latent-channel range, maturity, floor, ceiling, hidden-L2, or ATTRACT sweep is permitted.

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
- no non-finite state during training, intact virtual trajectory, counterfactual virtual trajectory, growth, damage, recovery, or persistence.

IMPROVEMENT RULE
CAUSAL-LATENT-DROPOUT25-PRUNE-T16 is worth widening only if every preregistered gate passes.

Exactly one fresh seed-0 candidate.
No second seed.
No second candidate.
No dropout-fraction sweep.
No horizon sweep.
No causal-margin sweep.
No full-cell ablation variant.
No target-mask variant.
No positive-delta reward variant.
No future occupancy variant.
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
- causal_latent_prune_loss;
- causal_probe_mature_samples;
- causal_probe_classified_samples;
- causal_probe_nonbeneficial_samples;
- causal_probe_nonbeneficial_fraction;
- causal_probe_dropped_cells_mean;
- causal_probe_actual_drop_fraction_mean;
- causal_delta_mean;
- causal_delta_min;
- causal_delta_max;
- causal_intact_future_loss_mean;
- causal_counterfactual_future_loss_mean;
- causal_dropout_fraction = 0.25;
- causal_probe_steps = 16;
- life_viability_floor = 113;
- formation_occupancy_ceiling = 800;
- life_channel = 4;
- visible_alpha_channel = 3;
- hidden penalty;
- gradient norm.

IMPLEMENTATION REQUIREMENTS
Before scientific execution:
- add a directly testable RNG-neutral distributed live-cell probe-mask helper or equivalent;
- probe mask must sample only hard-alive channel-4 cells;
- probe fraction must be exactly 0.25;
- probe RNG state must be identical before and after mask generation;
- add a directly testable latent-only intervention helper or equivalent;
- intervention must preserve channels 0..3 bit-for-bit at t0;
- intervention must zero channels 4..15 only at probed live cells;
- add a directly testable per-sample 16-step visible target trajectory loss matching ATTRACT-16 components;
- intact and counterfactual virtual trajectories must use identical stochastic update sequences;
- causal delta must be detached;
- decision threshold must be exactly delta <= 0;
- positive delta must produce zero causal-prune gradient;
- non-positive delta must produce positive gradient only on probed hard-alive life4 cells;
- no direct causal-prune gradient may reach channels 0..3 or 5..15;
- no direct gradient may flow from counterfactual trajectory loss into training objective;
- causal probe must be inactive below 113 hard life cells;
- zero-probed-cell samples must fail safe to differentiable zero contribution;
- preserve FRONTIER-FLOOR-113 unchanged;
- preserve CEIL-800 unchanged;
- preserve ATTRACT-16 unchanged;
- preserve hidden L2 unchanged;
- preserve normal and resumable training parity;
- preserve original-rollout-only pool updates;
- preserve RNG-neutral virtual trajectory;
- add additive tests for:
  * probe selects only hard-alive life4 cells;
  * probe uses fixed 0.25 Bernoulli threshold;
  * probe RNG state is restored exactly;
  * latent intervention preserves RGBA exactly;
  * latent intervention zeros channels 4..15 at probed cells;
  * latent intervention does not change unprobed cells;
  * per-sample future loss matches scalar ATTRACT-16 reduction when averaged;
  * matched intact/counterfactual trajectories use identical stochastic update masks under identical starts;
  * immature sample gives differentiable zero causal-prune loss;
  * positive causal delta gives zero prune gradient;
  * zero causal delta is non-beneficial and gives prune gradient;
  * negative causal delta gives prune gradient;
  * prune gradient reaches only probed hard-alive life4;
  * no direct prune gradient reaches RGBA or hidden5..15;
  * full objective formula;
  * STAB-16 compatibility;
  * STAB-17 compatibility;
  * normal telemetry;
  * resumable telemetry;
  * pool isolation;
  * frozen config;
  * runner evidence;
- complete reconstructed regression with zero failures.

TEST DISCIPLINE
Never disable, skip, comment out, or weaken a failing test.
Fix root cause.
If repair changes the preregistered scientific factor, stop and explicitly supersede or close STAB-18.

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
- probe RNG changes durable RNG state;
- t0 RGBA is altered by the latent intervention;
- channels outside 4..15 are zeroed by the intervention;
- intact/counterfactual trajectories do not share the same stochastic update sequence;
- causal delta is not detached;
- positive delta receives pruning reward or gradient;
- pruning gradient reaches channels other than life4;
- probe acts on immature samples;
- counterfactual virtual states enter the training pool;
- FRONTIER-FLOOR, CEIL-800, ATTRACT-16, hidden L2, or canonical gates change;
- non-finite state/loss appears;
- checkpoint/config integrity fails;
- tests cannot be repaired without changing the scientific factor.

DISCRIMINATING INTERPRETATION
If hidden life becomes bounded and lesion/morphology/recovery gates improve while causal-prune activity is non-zero:
this supports the hypothesis that STAB-16 retained latent support whose controlled removal was non-beneficial and that intervention-guided one-sided pruning can concentrate function.

If causal-prune activity is nearly always zero because most sampled latent support has positive causal delta:
the remaining support is causally useful under this probe and the problem lies elsewhere; do not increase dropout fraction.

If causal-prune activity is high and life collapses toward 113 or below:
group-level causal pruning is too destructive or the distributed probe misattributes jointly useful support; do not lower the delta threshold or coefficient post-result.

If occupancy improves but morphology/lesion salience does not:
removing non-beneficial support is not sufficient to create target-critical morphology; the next seam should address organization of useful support rather than further pruning.

If morphology improves but recovery becomes brittle:
the one-sided causal criterion is selecting minimal support at the expense of robustness; canonical recovery gates take precedence and the candidate closes negative.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling.

Fibonacci remains separate DG-1A-FIB1.

EXECUTION STATE
PREREGISTERED ONLY.
Do not execute until this exact spec is independently read back and branch HEAD independently verified.
