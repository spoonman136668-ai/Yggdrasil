TITLE: DG-1A-P0-STAB-11 — ATTRACT-16 Mature Persistence Target-Trajectory Preregistration
DATE: 2026-09-17
STATUS: PREREGISTERED — NOT YET EXECUTED
TRACK: DG-1A
CANDIDATE: ATTRACT-16
CONFIDENCE: MECHANISTICALLY MOTIVATED / SINGLE-CANDIDATE TEST

QUESTION
Can canonical P0 preserve viable growth and repair while producing a bounded long-horizon target attractor if mature states are trained directly against the target across a fixed future persistence trajectory, rather than merely suppressing local positive background-alpha velocity?

PRIOR MECHANISTIC BRACKET
STAB-09 HOME-1 showed that a one-step mature-only local velocity penalty could improve the nominal 96-step snapshot but did not create a bounded persistence attractor.

STAB-10 HOME-T16 extended the same local velocity mechanism to exactly 16 virtual steps and still failed:
- pre-damage active cells: 1407;
- pre-lesion MSE: 0.0883897096;
- persistence active cells: 1360 -> 1353;
- persistence peak active cells: 1501;
- lesion improved morphology;
- 10 / 14 preregistered gates failed.

The slightly negative STAB-10 final active drift occurred around a grossly overgrown state and therefore does not establish bounded homeostasis.

STAB-11 changes objective architecture while holding the virtual horizon fixed at 16.
It does not reopen HOME-1/HOME-T16 horizon or coefficient searches.

EXTERNAL RESEARCH BASIS
Growing Neural Cellular Automata (Mordvintsev et al., Distill 2020, DOI 10.23915/distill.00023) explicitly frames persistence training as making the target pattern an attractor. It notes that longer evolution intervals with repeated target losses can encourage the dynamics to return toward the target, while state-pool propagation approximates longer-horizon supervision under practical memory limits.

Learning spatio-temporal patterns with Neural Cellular Automata (Richardson et al., PLOS Computational Biology 2024, DOI 10.1371/journal.pcbi.1011589) trains against multiple temporal transitions and reports that propagating intermediate states supports longer-term dynamics.

Stability and Geometry of Attractors in Neural Cellular Automata (Kvalsund and Stovold, arXiv 2604.12720, 2026) cautions that apparently persistent NCAs need not be fixed-point attractors and can exhibit oscillatory, periodic, or quasi-periodic behavior. This motivates judging the whole persistence trajectory rather than only endpoint drift.

These references motivate trajectory-level target supervision and persistence diagnostics.
They do not determine the STAB-11 gates or establish that ATTRACT-16 will succeed.

SELECTED MECHANISM
ATTRACT-16

Only one scientific mechanism is introduced:
direct target supervision across a fixed 16-step mature virtual persistence trajectory.

The virtual horizon remains exactly 16, matching STAB-10.
This isolates the change from local velocity regularization to target-attractor supervision.

BASE STATIC OBJECTIVE
For any state x:

StaticMorphologyLoss(x, target) =
    GlobalVisibleMSE(x, target)
    + ForegroundVisibleMSE(x, target)
    + BackgroundAlphaMSE(x, target)

All three coefficients remain 1.0.

FROZEN MATURITY RULE
A rollout sample is mature when:

hard active cells >= immutable target foreground cardinality

Canonical radius-6 target foreground cardinality:
113 cells.

Only mature samples enter the virtual persistence trajectory.
If no sample is mature, the ATTRACT-16 auxiliary term is differentiable zero.

VIRTUAL TRAJECTORY CONTRACT
For the mature subset only:

1. snapshot the normal device RNG state;
2. set virtual_state_0 = mature rollout result;
3. run exactly 16 sequential NCA steps:
   virtual_state_t = NCA.step(virtual_state_{t-1})
   for t = 1..16;
4. require every virtual state to be finite;
5. restore the normal device RNG state after the complete trajectory;
6. never write virtual_state_1..virtual_state_16 into the persistent state pool;
7. keep the normal pool update bound to the original rollout result;
8. keep the complete 16-step path differentiable for the ATTRACT-16 gradient.

ATTRACT-16 AUXILIARY TERM
For the mature subset:

AttractorTrajectoryLoss =
mean(
    StaticMorphologyLoss(virtual_state_1, mature_target),
    ...,
    StaticMorphologyLoss(virtual_state_16, mature_target)
)

The arithmetic mean over the 16 future states is required.
Do not sum the 16 losses.
Do not include virtual_state_0 in the auxiliary mean because its static objective is already present in the base training loss.

FINAL TRAINING OBJECTIVE
TrainingMorphologyLoss =
    StaticMorphologyLoss(normal rollout result, full target batch)
    + AttractorTrajectoryLoss

ATTRACT-16 coefficient:
1.0

If there are zero mature samples:
TrainingMorphologyLoss =
    StaticMorphologyLoss(normal rollout result, full target batch)
    + differentiable zero

RATIONALE
STAB-10 penalized a local derivative:
positive target-background alpha change.

ATTRACT-16 instead penalizes actual future target error across the same 16-step horizon:
- foreground loss directly protects target morphology;
- background-alpha loss directly penalizes future excess support;
- global visible MSE preserves the common morphology objective;
- repeated future target supervision asks the learned rule to move and remain near the target, not merely reduce one local expansion signal.

Keeping the 16-step horizon unchanged makes STAB-11 a cleaner test of objective architecture rather than horizon length.

NEW HISTORICAL TRAINING MODE
Add exactly one new mode:

global_plus_foreground_bg_alpha_attractor_t16

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

FIXED STAB-11 FACTOR
mature virtual target-attractor horizon: 16 future steps
trajectory reduction: arithmetic mean
auxiliary coefficient: 1.0

No alternate horizon, reduction, or coefficient is permitted inside STAB-11.

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
ATTRACT-16 is worth widening only if every preregistered gate passes.

Exactly one fresh seed-0 candidate is permitted in STAB-11.
No second seed.
No second candidate.
No horizon sweep.
No coefficient sweep.
No loss-reduction sweep.

TRAINING TELEMETRY REQUIREMENTS
Record at normal reporting cadence:
- global_morphology_mse;
- foreground_morphology_mse;
- background_alpha_mse;
- attractor_trajectory_loss;
- attractor_mature_samples;
- attractor_probe_steps = 16;
- total morphology loss;
- hidden penalty;
- gradient norm.

IMPLEMENTATION REQUIREMENTS BEFORE SCIENTIFIC RUN
- add one explicit trajectory static-morphology helper or directly testable equivalent;
- reuse or add one RNG-neutral fixed 16-step virtual trajectory helper without changing HOME-T16 semantics;
- preserve HOME-1 and HOME-T16 helpers and semantics unchanged;
- add exactly one historical ATTRACT-16 loss mode;
- implement ATTRACT-16 in both normal and resumable training;
- preserve pool update semantics: original rollout result only;
- add fail-closed validation for the new mode/horizon contract;
- add additive tests for:
  * differentiable zero when no mature sample exists;
  * exact 16-step horizon;
  * exact arithmetic-mean future-target formula;
  * full objective = current static objective + trajectory auxiliary;
  * RNG-state restoration after all 16 virtual steps;
  * virtual trajectory pool isolation;
  * normal training telemetry;
  * resumable training telemetry;
  * frozen config;
  * runner evidence mode/telemetry;
  * HOME-1 and HOME-T16 compatibility;
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
- the fixed 16-step virtual trajectory cannot execute under the current resource envelope;
- frozen config cannot be reproduced;
- checkpoint integrity fails;
- RNG-neutrality cannot be preserved;
- pool isolation cannot be preserved;
- a code/test failure cannot be repaired without changing the preregistered scientific factor.

If ATTRACT-16 completes but any scientific gate fails:
- record CLOSED NEGATIVE;
- do not widen;
- do not change the 16-step horizon, coefficient, reduction, maturity rule, target, envelope, or gates inside STAB-11.

DISCRIMINATING INTERPRETATION
If ATTRACT-16 satisfies all gates where HOME-1 and HOME-T16 failed, that supports the hypothesis that direct future target-state supervision is required to make the target morphology a bounded attractor.

If ATTRACT-16 remains severely overgrown or lesion-invalid, do not ratchet nearby trajectory horizons or coefficients. The next packet should reconsider how viability/support are represented in the objective or state dynamics rather than continuing the same trajectory-loss family.

If ATTRACT-16 collapses viability, record that as an attractor-training version of the STAB-06 bracket; do not weaken viability gates.

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
