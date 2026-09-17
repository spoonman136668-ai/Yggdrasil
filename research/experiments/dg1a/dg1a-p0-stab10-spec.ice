TITLE: DG-1A-P0-STAB-10 — Fixed 16-Step Mature Virtual Homeostasis Trajectory Preregistration
DATE: 2026-09-17
STATUS: PREREGISTERED — NOT YET EXECUTED
TRACK: DG-1A
CANDIDATE: HOME-T16
CONFIDENCE: MECHANISTICALLY MOTIVATED / SINGLE-CANDIDATE TEST

QUESTION
Can canonical P0 preserve meaningful growth and repair while preventing the long-horizon support expansion observed in STAB-09 if the mature-only HOME-1 control signal is extended from one virtual step to one fixed short virtual persistence trajectory?

SCIENTIFIC SEAM
STAB-09 established that a one-step mature-only positive target-background alpha velocity penalty can improve the nominal 96-step growth snapshot but does not produce a bounded 96-step persistence attractor.

STAB-09 measured:
- pre-damage active cells: 993;
- pre-lesion global MSE: 0.0524558015;
- persistence active cells: 941 -> 1406;
- persistence peak active cells: 1490;
- persistence active-cell drift: +465;
- final persistence global MSE: 0.0822274983;
- lesion invalid because damage improved morphology.

Therefore STAB-10 tests temporal horizon directly.
It does not reopen static occupancy, threshold, margin, support-halo, target-distance, or HOME-1 coefficient searches.

EXTERNAL RESEARCH BASIS
Growing Neural Cellular Automata (Mordvintsev et al., Distill 2020, DOI 10.23915/distill.00023) explicitly identifies long-run instability after endpoint training and motivates longer temporal supervision / pool propagation to encourage target-attractor behavior.

Learning spatio-temporal patterns with Neural Cellular Automata (Richardson et al., PLOS Computational Biology 2024, DOI 10.1371/journal.pcbi.1011589) trains across multiple temporal transitions and reports that propagating intermediate states supports learning longer-term dynamics.

These references motivate temporal supervision as a mechanism class. They do not determine the STAB-10 gates or establish that HOME-T16 will succeed.

SELECTED MECHANISM
HOME-T16

Only one scientific factor changes relative to HOME-1:

HOME-1:
- exactly one virtual mature persistence step.

HOME-T16:
- exactly sixteen sequential virtual mature persistence steps.

All other canonical scientific factors remain frozen unless explicitly listed below.

WHY SIXTEEN STEPS
The horizon is fixed before implementation or execution.

Sixteen steps is:
- materially longer than the rejected one-step local derivative;
- one sixth of the 96-step canonical persistence evaluation horizon;
- small enough to remain a bounded probe rather than duplicating the full evaluation trajectory inside every training iteration;
- approximately a 16 / 80 = 20% nominal extra NCA-step burden when all samples are mature, relative to an 80-step midpoint training rollout, before implementation overhead.

No alternate horizon will be tested inside STAB-10.
If 16 steps is infeasible under the existing resource envelope, STAB-10 must close as an implementation/resource failure or a new packet must be preregistered. Do not shorten the horizon after observing feasibility or scientific behavior.

FROZEN MATURITY RULE
A rollout sample is mature when:

hard active cells >= immutable target foreground cardinality

Canonical radius-6 target foreground cardinality:
113 cells.

Only mature samples enter the virtual trajectory.
If no sample is mature, the HOME-T16 term is differentiable zero.

VIRTUAL TRAJECTORY CONTRACT
For the mature subset only:

1. snapshot the normal device RNG state;
2. set virtual_state_0 = mature rollout result;
3. run exactly 16 sequential NCA steps:
   virtual_state_t = NCA.step(virtual_state_{t-1})
   for t = 1..16;
4. require every virtual state to be finite;
5. restore the normal device RNG state after the complete trajectory;
6. never write virtual_state_1..virtual_state_16 into the state pool;
7. keep the normal pool update bound to the original rollout result;
8. keep the complete 16-step path differentiable for the HOME-T16 gradient.

The virtual trajectory is diagnostic/training-only and has no execution authority over the persistent state pool.

HOME-T16 DYNAMIC TERM
For each transition t = 1..16:

StepPositiveBackgroundVelocity_t =
mean(
    ReLU(
        virtual_alpha_t
        - virtual_alpha_{t-1}
    ) / 0.1
    over immutable target-background pixels
)

Then:

HomeostasisTrajectoryVelocityLoss =
mean(
    StepPositiveBackgroundVelocity_1,
    ...,
    StepPositiveBackgroundVelocity_16
)

The arithmetic mean over transitions is required.
Do not sum the 16 terms.

RATIONALE FOR STEPWISE MEAN
Using the same positive-background velocity quantity at each transition preserves the HOME-1 signal scale while changing temporal horizon.
This minimizes confounding between:
- longer temporal observation;
and
- an implicit coefficient increase.

The loss remains one-sided:
- positive target-background alpha expansion is penalized;
- no-growth and contraction contribute zero.

BASE STATIC OBJECTIVE
Retain STAB-05 / STAB-09 static terms unchanged:

StaticMorphologyLoss =
    GlobalVisibleMSE
    + ForegroundVisibleMSE
    + BackgroundAlphaMSE

FINAL TRAINING OBJECTIVE
TrainingMorphologyLoss =
    StaticMorphologyLoss
    + HomeostasisTrajectoryVelocityLoss

All objective coefficients:
1.0

No coefficient sweep is permitted.

NEW HISTORICAL TRAINING MODE
Add exactly one new mode:

global_plus_foreground_bg_alpha_homeostasis_t16

Preserve unchanged:
1. global_mse
2. balanced_fg_bg
3. global_plus_foreground
4. global_plus_foreground_bg_alpha
5. global_plus_foreground_bg_alive_margin
6. global_plus_foreground_farfield_bg_alpha
7. global_plus_foreground_graded_bg_alpha
8. global_plus_foreground_bg_alpha_homeostasis

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

FIXED STAB-10 FACTOR
virtual mature persistence horizon: 16 steps

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
- no non-finite state during training, virtual probing, growth, damage, recovery, or persistence.

IMPROVEMENT RULE
HOME-T16 is worth widening only if every preregistered gate passes.

Exactly one fresh seed-0 candidate is permitted in STAB-10.
No second seed.
No second candidate.
No horizon sweep.
No coefficient sweep.

TRAINING TELEMETRY REQUIREMENTS
Record at normal reporting cadence:
- global_morphology_mse;
- foreground_morphology_mse;
- background_alpha_mse;
- homeostasis_trajectory_velocity_loss;
- homeostasis_mature_samples;
- homeostasis_probe_steps = 16;
- total morphology loss;
- hidden penalty;
- gradient norm.

IMPLEMENTATION REQUIREMENTS BEFORE SCIENTIFIC RUN
- add one explicit trajectory velocity helper or equivalent directly testable unit;
- add one RNG-neutral 16-step virtual trajectory helper;
- preserve HOME-1 one-step helper and semantics unchanged;
- add exactly one historical HOME-T16 loss mode;
- implement HOME-T16 in both normal and resumable training;
- preserve pool update semantics: original rollout result only;
- add fail-closed validation for the HOME-T16 mode/horizon contract;
- add additive tests for:
  * differentiable zero when no mature sample exists;
  * exact 16-step horizon;
  * exact arithmetic-mean trajectory formula;
  * contraction/no-growth zero behavior;
  * exact full HOME-T16 objective;
  * RNG-state restoration after all 16 virtual steps;
  * virtual trajectory pool isolation;
  * normal training telemetry;
  * resumable training telemetry;
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
- non-finite rollout or virtual state appears;
- non-finite loss appears;
- fixed 16-step probe cannot be executed under the current resource envelope;
- frozen config cannot be reproduced;
- checkpoint integrity fails;
- RNG-neutrality cannot be preserved;
- pool isolation cannot be preserved;
- a code/test failure cannot be repaired without changing the preregistered scientific factor.

If HOME-T16 completes but any scientific gate fails:
- record CLOSED NEGATIVE;
- do not widen;
- do not change the 16-step horizon, maturity rule, normalization, coefficients, target, envelope, or gates inside STAB-10.

DISCRIMINATING INTERPRETATION
If HOME-T16 materially controls persistence while HOME-1 did not, that supports the hypothesis that HOME-1 failed primarily because one-step local control was temporally myopic.

If HOME-T16 still shows strong long-horizon expansion, close this mechanism class rather than ratcheting nearby probe horizons. The next packet should reconsider the objective architecture, likely toward an explicit persistence curriculum / attractor-state training term rather than another local velocity horizon tweak.

If HOME-T16 suppresses expansion by collapsing viability, record that as the dynamic analogue of the STAB-06 bracket; do not weaken viability gates.

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
