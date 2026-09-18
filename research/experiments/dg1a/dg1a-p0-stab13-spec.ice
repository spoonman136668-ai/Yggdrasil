TITLE: DG-1A-P0-STAB-13 — TRACE-CEIL-800 Persistence-Trajectory Occupancy Preregistration
DATE: 2026-09-17
STATUS: PREREGISTERED — NOT YET EXECUTED
TRACK: DG-1A
CANDIDATE: TRACE-CEIL-800 + CEIL-800 + ATTRACT-16
CONFIDENCE: MECHANISTICALLY MOTIVATED / SINGLE-CANDIDATE TEST

QUESTION
Can canonical P0 eliminate the remaining transient persistence occupancy overshoot while preserving STAB-12's near-bounded formation, contractive persistence, positive lesion sign, and viable recovery by applying the already-frozen CEIL-800 constraint across the same 16-step virtual persistence trajectory already used by ATTRACT-16?

PRIOR MECHANISTIC BRACKET
STAB-12 substantially narrowed the P0 failure:
- pre-damage active cells: 857;
- persistence initial active cells: 799;
- persistence peak active cells: 1015;
- persistence final active cells: 623;
- active drift: -176;
- final recovery active cells: 655;
- DamageEffect became positive;
- stable T50 = 59;
- RecoveryFraction = 1.0;
- 5 / 14 gates failed.

The persistence occupancy trace is diagnostic:
799 -> 810 -> ... -> 1015 -> ... -> 623.

The trajectory violates the <=800 canonical maximum almost immediately even though both the start and endpoint are near/inside the desired regime.

The corresponding persistence morphology MSE rises:
0.0444691367 -> peak 0.0736930072 -> 0.0434814841.

Therefore STAB-13 targets the already-observed transient support overshoot rather than tightening the endpoint ceiling.

EXTERNAL RESEARCH BASIS
Growing Neural Cellular Automata (Mordvintsev et al., Distill 2020, DOI 10.23915/distill.00023) argues that applying losses across longer evolution intervals helps mold the dynamics toward a target attractor rather than supervising only an endpoint.

Learning spatio-temporal patterns with Neural Cellular Automata (Richardson et al., PLOS Computational Biology 2024, DOI 10.1371/journal.pcbi.1011589) explicitly treats NCA behavior as trajectories and trains transition paths by averaging losses at multiple temporal targets.

Stability and Geometry of Attractors in Neural Cellular Automata (Kvalsund and Stovold, arXiv:2604.12720, 2026) shows that NCA attractors can be oscillatory, periodic, or quasi-periodic rather than simple fixed points, supporting evaluation and control of the trajectory rather than relying only on endpoint state.

Transient State Reorganization and Cell Differentiation in the Developmental Dynamics of Growing Neural Cellular Automata (Sato, Masumori, Ikegami, arXiv:2607.15726, 2026) reports that morphological convergence can proceed non-monotonically through transient intermediate configurations.

STAB-13 does not assume non-monotonicity is intrinsically bad.
It targets the specific preregistered P0 maximum-occupancy gate that STAB-12 violated and whose violation was already observed within the first 16 persistence steps.

SELECTED MECHANISM
TRACE-CEIL-800

STAB-12 remains intact.

Exactly one new scientific factor is added:
apply the existing CEIL-800 occupancy loss to every future state of the already-existing 16-step ATTRACT trajectory, then arithmetic-mean reduce those 16 ceiling losses.

NO NEW OCCUPANCY PARAMETER
The ceiling remains:
800 hard-active cells.

The hard alive threshold remains:
alpha > 0.1.

The straight-through gradient mask remains:
currently hard-active target-background cells only.

The normalization remains:
800.

The exponent remains:
square.

The coefficient remains:
1.0.

No alternate value is permitted inside STAB-13.

EXISTING ENDPOINT CEIL-800 — UNCHANGED
For the normal rollout endpoint:
- hard active count is exact alpha > 0.1 occupancy;
- endpoint loss is zero for count <=800;
- excess is ReLU(STEActiveCount - 800) / 800;
- endpoint CEIL loss is mean squared normalized excess;
- surrogate gradient is restricted to currently active target-background cells.

ATTRACT-16 — UNCHANGED
Maturity:
hard active count >= immutable target foreground cardinality 113.

For mature samples:
- exactly 16 sequential RNG-neutral virtual future steps;
- virtual states remain differentiable;
- virtual states never enter persistent pool authority;
- each future state receives:
  GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAlphaMSE;
- the 16 target losses are arithmetic-mean reduced;
- ATTRACT coefficient = 1.0.

TRACE-CEIL-800
For the same mature future states virtual_state_1 ... virtual_state_16:

TraceCeilingLoss_t =
    FormationOccupancyCeilingLoss(
        virtual_state_t,
        mature_target,
        occupancy_ceiling = 800
    )

using exactly the same:
- hard-count forward semantics;
- alpha threshold;
- target-background mask;
- straight-through gradient scope;
- normalization;
- squared excess.

Then:

TraceCeilingLoss =
mean(
    TraceCeilingLoss_1,
    ...,
    TraceCeilingLoss_16
)

Do not sum.
Do not use max reduction.
Do not add additional trajectory steps.
Do not include virtual_state_0 in TraceCeilingLoss because the normal endpoint already receives the existing CEIL-800 term.

If there are zero mature samples:
- AttractorTrajectoryLoss = differentiable zero;
- TraceCeilingLoss = differentiable zero.

FINAL TRAINING OBJECTIVE
TrainingMorphologyLoss =
    StaticMorphologyLoss(normal endpoint)
    + AttractorTrajectoryLoss
    + FormationOccupancyCeilingLoss(normal endpoint)
    + TraceCeilingLoss

All coefficients:
1.0

StaticMorphologyLoss remains:
GlobalVisibleMSE
+ ForegroundVisibleMSE
+ BackgroundAlphaMSE.

DISCRIMINATING CHANGE
STAB-12 constrained occupancy only at the sampled normal endpoint and supervised future morphology.

STAB-13 adds occupancy supervision to the same future states already generated for ATTRACT-16.

Therefore:
- architecture unchanged;
- virtual horizon unchanged;
- target objective unchanged;
- formation ceiling unchanged;
- only temporal scope of the established occupancy constraint changes.

This directly tests whether STAB-12's remaining occupancy failure is a trajectory-control problem.

WHY 16 STEPS ARE SUFFICIENT FOR THIS TEST
STAB-12 persistence begins at 799 and exceeds the 800 gate on the first measured persistence step.

Within the first 16 measured future steps it reaches at least 959 active cells.

Therefore the already-frozen 16-step virtual horizon spans a substantial part of the observed violation.
No longer horizon is required to test whether trajectory occupancy supervision changes the failure.

NEW HISTORICAL TRAINING MODE
Add exactly one new mode:

global_plus_foreground_bg_alpha_attractor_t16_ceil800_traceceil800

Preserve unchanged all eleven earlier modes.

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

FIXED STAB-13 FACTORS
ATTRACT horizon:                   16
ATTRACT reduction:                 arithmetic mean
ATTRACT coefficient:               1.0
endpoint occupancy ceiling:        800
endpoint ceiling coefficient:      1.0
trace occupancy ceiling:           800
trace ceiling normalization:       800
trace ceiling exponent:            square
trace ceiling reduction:           arithmetic mean
trace ceiling coefficient:         1.0
hard alive threshold:              0.1
STE gradient scope:                currently active target-background cells only

No horizon, ceiling, normalization, exponent, reduction, coefficient, or STE-scope sweep is permitted.

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
TRACE-CEIL-800 is worth widening only if every preregistered gate passes.

Exactly one fresh seed-0 candidate is permitted.
No second seed.
No second candidate.
No horizon sweep.
No ceiling sweep.
No coefficient sweep.
No reduction sweep.
No STE variant sweep.

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
- trace_occupancy_ceiling_loss;
- trace_active_cells_mean;
- trace_active_cells_max;
- trace_occupancy_ceiling = 800;
- total morphology loss;
- hidden penalty;
- gradient norm.

IMPLEMENTATION REQUIREMENTS BEFORE SCIENTIFIC RUN
- reuse the existing CEIL-800 helper unchanged;
- reuse the existing 16-step RNG-neutral trajectory unchanged;
- add one directly testable trace-ceiling reduction helper or equivalent;
- preserve ATTRACT-16 semantics unchanged;
- preserve endpoint CEIL-800 semantics unchanged;
- preserve HOME-1/HOME-T16 and every historical mode unchanged;
- add exactly one new historical loss mode;
- implement normal and resumable training;
- preserve original-rollout-only pool updates;
- add additive tests for:
  * exactly 16 future ceiling evaluations;
  * arithmetic-mean trace reduction;
  * trace loss zero when all future counts <=800;
  * trace loss positive when any future count >800;
  * future target-foreground gradient remains zero;
  * future inactive-background gradient remains zero;
  * positive future active-background gradient when ceiling violated;
  * full objective formula;
  * no-mature differentiable zero;
  * ATTRACT-16 compatibility;
  * endpoint CEIL-800 compatibility;
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
- trace CEIL hard-count forward semantics diverge from evaluation occupancy semantics;
- trace gradient leaks into target foreground or inactive background;
- endpoint CEIL-800 semantics change;
- ATTRACT-16 semantics change;
- non-finite rollout, virtual state, or loss appears;
- frozen config cannot be reproduced;
- checkpoint integrity fails;
- RNG-neutrality cannot be preserved;
- pool isolation cannot be preserved;
- a code/test failure cannot be repaired without changing the preregistered scientific factor.

If STAB-13 completes but any scientific gate fails:
- record CLOSED NEGATIVE;
- do not widen;
- do not change any frozen factor inside STAB-13.

DISCRIMINATING INTERPRETATION
If TRACE-CEIL-800 removes the 799 -> 1015 transient persistence overshoot while preserving formation/recovery viability and improves morphology/lesion salience, that supports the hypothesis that the remaining STAB-12 defect was insufficient occupancy control along the attractor trajectory.

If persistence still overshoots >800, do not lengthen the horizon or strengthen the coefficient inside STAB-13.

If occupancy becomes fully bounded but morphology and lesion salience remain poor, raw support count is no longer the dominant seam; the next packet should target spatial/morphological support allocation directly.

If viability collapses, record that trajectory-wide occupancy pressure crossed the viable bracket and do not weaken gates.

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
