TITLE: DG-1A-P0-STAB-09 — Mature One-Step Background Homeostasis Velocity Control
DATE: 2026-09-17
STATUS: PREREGISTERED EXPLORATORY ABLATION
TRACK: DG-1A
CONFIDENCE: PLAUSIBLE

QUESTION
Can canonical P0 preserve meaningful growth and repair while preventing post-viability support expansion if the established continuous background-alpha objective is augmented with a one-step, maturity-gated homeostasis-velocity penalty?

MOTIVATION
STAB-05 through STAB-08 establish that static endpoint occupancy/spatial penalties are insufficient:

STAB-05 — uniform continuous target-background alpha pressure:
- pre-damage active: 1206 / 1600;
- pre-lesion global MSE: 0.0701904967;
- remained expansive.

STAB-06 — threshold-aligned pressure:
- pre-damage active: 3 / 1600;
- final recovery active: 0;
- crossed into near-death.

STAB-07 — binary one-cell support-halo exemption:
- pre-damage active: 1094;
- final recovery active: 1232;
- persistence active: 1005 -> 1276;
- restored viability but remained overgrown.

STAB-08 — smooth static target-distance weighting:
- pre-damage active: 1440;
- pre-lesion MSE: 0.1016835570;
- persistence active: 1348 -> 1102;
- later support contracted but morphology remained poor and lesion-invalid.

The common failure is increasingly dynamic. Endpoint penalties do not reliably produce a bounded post-growth attractor. STAB-09 therefore targets the local developmental derivative after a viable rollout rather than introducing another static spatial weighting.

CANDIDATE
HOME-1

BASE STATIC OBJECTIVE
Retain the STAB-05 continuous occupancy objective exactly:

StaticMorphologyLoss =
    GlobalVisibleMSE
    + 1.0 * ForegroundVisibleMSE
    + 1.0 * BackgroundAlphaMSE

BackgroundAlphaMSE is computed over all target-background pixels exactly as in STAB-05.

TARGET-DERIVED MATURITY
For each training sample after the normal 64..96-step rollout:

TargetForegroundCount =
    number of immutable target pixels with target alpha > 0.1

Canonical radius-6 target:
TargetForegroundCount = 113

A rollout sample is HOME-1-mature iff:

HardActiveCells(result) >= TargetForegroundCount

where hard active means result alpha > the frozen alive threshold 0.1.

This maturity gate:
- is derived from the immutable target;
- has no fitted parameter;
- is not differentiated through;
- generalizes to small test targets through their own foreground cardinality.

VIRTUAL HOMEOSTASIS PROBE
For HOME-1-mature rollout samples only, evaluate exactly ONE additional NCA developmental step:

probe = model.step(result)

The probe is a virtual training diagnostic:
- probe is NOT written into the state pool;
- pool update remains the original rollout result;
- probe is NOT used as the endpoint morphology state;
- evaluation protocol remains unchanged.

RNG-NEUTRALITY CONTRACT
The normal device RNG state is saved immediately before the virtual probe and restored immediately after the probe.

Therefore:
- the probe may use the same stochastic update semantics as a normal model step;
- the probe does not advance or perturb the main training RNG stream;
- subsequent normal training rollouts retain the same RNG sequence they would have had without the probe, conditional on the learned parameter trajectory.

HOMEOSTASIS VELOCITY TERM
For each HOME-1-mature sample and each immutable target-background pixel:

PositiveBackgroundAlphaVelocity =
    ReLU(probe_alpha - result_alpha) / alive_threshold

Frozen alive_threshold = 0.1.

A background cell whose alpha rises by exactly one alive-threshold unit in the probe contributes 1.0 before averaging.

HomeostasisBackgroundVelocityLoss =
    mean(
        PositiveBackgroundAlphaVelocity
        over target-background pixels of HOME-1-mature samples
    )

If a training batch contains zero HOME-1-mature samples:
- HomeostasisBackgroundVelocityLoss = differentiable zero;
- no background-velocity penalty is applied to that batch.

The loss penalizes positive background alpha velocity only.
It does NOT penalize:
- background alpha contraction;
- zero background alpha velocity;
- positive foreground alpha velocity;
- immature rollout samples.

TRAINING OBJECTIVE
For HOME-1:

TrainingMorphologyLoss =
    GlobalVisibleMSE
    + ForegroundVisibleMSE
    + BackgroundAlphaMSE
    + HomeostasisBackgroundVelocityLoss

Total TrainingLoss =
    TrainingMorphologyLoss
    + existing hidden-state L2 term.

All four morphology/homeostasis coefficients are fixed at 1.0.
No coefficient sweep is permitted.

SINGLE-FACTOR CONTRACT
Relative to STAB-05, the only scientific addition is the maturity-gated one-step background homeostasis-velocity term.

STAB-05's static global + foreground + all-background-alpha objective is retained exactly.

HOME-1 is NOT:
- a static coefficient sweep;
- a threshold sweep;
- a margin sweep;
- a halo-radius sweep;
- a target-distance weighting;
- an alternate evaluation metric.

DYNAMIC ISOLATION CONTRACT
The virtual probe must not change state-pool progression or the main stochastic training stream.

Implementation must therefore:
1. run the normal rollout exactly as before;
2. save the device RNG state;
3. evaluate the one-step probe;
4. restore the device RNG state;
5. compute the HOME-1 velocity loss;
6. backpropagate through the probe and rollout;
7. update the pool with the original rollout result, never the probe.

Do not change:
- model architecture;
- optimizer;
- training iterations;
- learning rate;
- rollout range;
- pool size;
- training-damage probability or geometry;
- training maturity threshold for damage;
- gradient clipping;
- hidden-state L2;
- target;
- evaluation growth horizon;
- persistence horizon;
- recovery horizon;
- evaluation lesion;
- common global evaluation metric.

DEAD / IMMATURE SANITY
An all-dead or otherwise sub-113-cell canonical rollout is HOME-1-immature.

Therefore:
- HomeostasisBackgroundVelocityLoss = 0 for that rollout;
- the unchanged foreground term continues to make the all-dead target solution expensive;
- HOME-1 does not directly penalize the background-growth velocity of an immature organism that has not yet reached target-derived viability.

This is intentional: the dynamic term is a homeostasis constraint after viability, not a growth-suppression term before viability.

FIXED ENVELOPE
Seed: 0
Variant: regeneration
Grid: 40 x 40
State channels: 16
Hidden channels: 128
Fire rate: 0.5
Alive channel: 3
Alive threshold: 0.1
Training iterations: 200
Learning rate: 0.001
Training development steps: 64..96
Batch size: 8
Pool size: 64
Training damage probability: 0.50
Training damage geometry: center 0.50 x 0.50
Training damage minimum active cells: 16
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

COMMON EVALUATION CONTRACT
Global visible-channel morphology MSE remains unchanged for:
- pre/post lesion morphology;
- DamageEffect;
- RelativeDamageEffect;
- RecoveryFraction;
- stable T50/T90;
- persistence;
- historical comparison.

HOME-1 changes training only.

VIABILITY / OCCUPANCY REQUIREMENT
Retain the target-derived viability floor and frozen occupancy ceiling:

Growth/recovery:
- 113 <= pre-damage active cells <= 800;
- 113 <= final recovery active cells <= 800.

Persistence:
- 113 <= final persistence active cells <= 800;
- maximum active cells anywhere in the 96-step persistence window <= 800;
- final persistence active-cell drift <= 0.

The maximum-persistence occupancy and non-positive final drift requirements are new preregistered homeostasis gates for this dynamic packet.

VALID LESION REQUIREMENT
All must hold:
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10;
- finite state.

MORPHOLOGY REQUIREMENT
Pre-lesion global morphology MSE <= 0.0361635.

PERSISTENCE MORPHOLOGY REQUIREMENT
All must hold:
- final persistence global MSE <= 0.0361635;
- maximum persistence global MSE <= 2.0 * initial persistence global MSE;
- finite state.

RECOVERY REQUIREMENT
All must hold:
- stable T50 attained;
- bounded final RecoveryFraction > 0.4230230485.

IMPROVEMENT RULE
HOME-1 is worth widening only if every preregistered requirement passes.

Compact gate list:
1. 113 <= pre-damage active cells <= 800;
2. DamageEffect > 0;
3. RelativeDamageEffect >= 0.10;
4. ActiveCellRemovalFraction >= 0.10;
5. stable T50 attained;
6. bounded final RecoveryFraction > 0.4230230485;
7. pre-lesion global morphology MSE <= 0.0361635;
8. 113 <= final recovery active cells <= 800;
9. 113 <= final persistence active cells <= 800;
10. maximum persistence active cells <= 800;
11. final persistence active-cell drift <= 0;
12. final persistence global MSE <= 0.0361635;
13. maximum persistence global MSE <= 2x initial persistence global MSE;
14. no non-finite state.

TRAINING TELEMETRY REQUIREMENT
HOME-1 training history must record:
- foreground_morphology_mse;
- background_alpha_mse;
- homeostasis_background_velocity_loss;
- homeostasis_mature_samples;
- original global_morphology_mse;
- total morphology loss;
- hidden penalty;
- gradient norm.

The one-step probe must be finite.

STOP RULES
Stop and record negative immediately if:
- non-finite rollout or probe state appears;
- non-finite loss appears;
- frozen config cannot be reproduced;
- checkpoint integrity fails;
- RNG-neutrality contract cannot be preserved;
- a code/test failure cannot be repaired without changing the preregistered scientific factor.

If HOME-1 completes but any improvement-rule gate fails:
- record CLOSED NEGATIVE;
- do not widen to additional seeds;
- do not alter the maturity rule, probe horizon, velocity normalization, coefficients, or gates inside STAB-09.

IMPLEMENTATION REQUIREMENTS BEFORE RUN
- add one explicit HOME-1 background-velocity helper;
- add target-derived mature-sample counting;
- add one explicit historical HOME-1 training-loss mode;
- preserve all seven prior modes unchanged;
- add RNG-neutral virtual one-step probe in normal and resumable training;
- keep pool update bound to original rollout result;
- add normal and resumable HOME-1 telemetry;
- add frozen config validation;
- add tests for:
  * immature differentiable-zero behavior;
  * target-derived maturity;
  * positive-background-velocity formula;
  * contraction/no-growth zero behavior;
  * exact full HOME-1 formula;
  * RNG-state restoration;
  * pool/result semantics;
  * normal and resumable telemetry;
  * frozen config;
  * runner evidence;
- full reconstructed regression must be green before scientific execution.

PROVENANCE CONTRACT
If native byte-identical checkout remains unavailable:
- record exact connected-GitHub implementation/test revision used as reconstruction basis;
- source_revision_verified_checkout = false;
- sandbox_source_byte_identity = false;
- classify scientific result as MEASURED SANDBOX.

BOUNDARY
This packet remains canonical DG-1A P0 morphology/developmental-substrate research.
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling from this packet.
