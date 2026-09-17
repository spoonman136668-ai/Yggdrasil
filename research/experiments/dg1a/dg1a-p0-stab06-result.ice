TITLE: DG-1A-P0-STAB-06 — Threshold-Aligned Background Alive-Margin Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
EVIDENCE CLASS: MEASURED SANDBOX

QUESTION
Does replacing STAB-05's continuous target-background alpha-energy penalty with a threshold-aligned differentiable alive-margin penalty produce bounded active support, acceptable global morphology, meaningful damage, stable persistence, and stable regeneration under the canonical H96/M16 envelope?

PREREGISTERED CANDIDATE
AM-05

BackgroundAliveMarginLoss = mean(
    (ReLU(state_alpha - 0.05) / 0.05)^2
    over target-background pixels
)

TrainingMorphologyLoss =
    GlobalVisibleMSE
    + ForegroundVisibleMSE
    + BackgroundAliveMarginLoss

The alive threshold remained 0.1.
The margin floor remained 0.05.
The alive-margin coefficient remained 1.0.
The STAB-05 continuous BackgroundAlphaMSE term was not retained in the active candidate.
The common global visible-channel morphology MSE remained unchanged for evaluation.

PREREGISTRATION
research/experiments/dg1a/dg1a-p0-stab06-spec.ice

SOURCE / PROVENANCE
Implementation-and-test source revision used as the reconstruction basis:

6e8d79b0fd47b7031b05f03b395bf49c1649f00e

Sandbox execution was performed from a semantic reconstruction of connected GitHub readbacks of that revision rather than a native byte-identical checkout.

Therefore:
- source_revision_verified_checkout: NO
- sandbox_source_byte_identity: NO
- scientific status: MEASURED SANDBOX, not commit-bound confirmatory acceptance

TEST SURFACE
Before the scientific candidate was executed, the reconstructed source/test surface completed:

79 passed
0 failed
Python 3.13.5
PyTorch 2.10.0+cpu

The additive STAB-06 tests covered:
- alive-margin boundary semantics;
- target-background-only behavior;
- missing-background fail-closed behavior;
- invalid margin fail-closed behavior;
- exact AM-05 objective formula;
- finite new-mode loss behavior;
- preregistered all-dead loss sanity;
- frozen STAB-06 config validation;
- normal-training component telemetry;
- resumable-training component telemetry;
- runner evidence recording of the effective mode and alive-margin telemetry.

No existing assertion was weakened, skipped, disabled, or modified merely to obtain the result.

EXECUTION CONTRACT
Exactly one fresh seed-0 AM-05 candidate was executed.

Training used the preregistered 200-iteration H96/M16 regeneration envelope.
The run used one writer and bounded resumable checkpoints.
When a multi-segment sandbox call exceeded the call window, only the last confirmed written checkpoint was accepted. No unconfirmed partial progress was assumed.
No concurrent worker touched the checkpoint.
No second candidate, new seed, coefficient change, threshold change, margin change, or gate change was introduced.

MEASURED TRAINING RESULT
training iterations:       200 / 200
initial recorded loss:     0.4459555447
minimum recorded loss:     0.3612360060
final recorded loss:       0.3881474733
training loss mode:        global_plus_foreground_bg_alive_margin
training elapsed:          306.5588479 s
non-finite state:          NO

Final recorded component telemetry:
- global morphology MSE:       0.0261610318
- foreground morphology MSE:   0.3596556187
- background alive-margin:     0.0023307728
- composite morphology loss:   0.3881474435

Two large recorded optimization transients occurred early:
- iteration 10: background alive-margin approximately 2.5370; gradient norm approximately 673.55;
- iteration 40: background alive-margin approximately 7.6314; gradient norm approximately 686.45.

These transients are observations only. This packet does not establish that they caused the final phenotype.

MEASURED EVALUATION RESULT
pre-lesion global MSE:     0.0283585768
post-lesion global MSE:    0.0285354797
final recovery global MSE: 0.0295742173

DamageEffect:              0.0001769029
RelativeDamageEffect:      0.0062380726

pre-damage active cells:      3 / 1600
post-damage active cells:     2 / 1600
active-cell removal:          0.3333333333
final active cells:           0 / 1600

bounded RecoveryFraction:  0.0
raw RecoveryFraction:     -5.8717964917
stable T50:                NOT ATTAINED
stable T90:                NOT ATTAINED
normalized recovery AUC:   0.0036180955

The recovery trajectory reached zero active cells and remained dead. The final global MSE converged to approximately 0.0295742, the already-known near-all-zero sparse-target loss regime.

PERSISTENCE OBSERVATION
initial persistence error: 0.0283863526
maximum degradation:       0.0001858249
final persistence error:   0.0271319859
initial active cells:      2
final active cells:        5
active-cell drift:         +3
visible-state drift MSE:   0.0007795979

These persistence numbers satisfy the preregistered numerical bounds but describe persistence of an almost-dead phenotype. They are not evidence of a viable stable target morphology.

PREREGISTERED GATE APPLICATION
PASS  pre-damage active cells > 0
PASS  pre-damage active cells <= 800 / 1600
PASS  DamageEffect > 0
FAIL  RelativeDamageEffect >= 0.10
PASS  ActiveCellRemovalFraction >= 0.10
FAIL  stable T50 attained
FAIL  final RecoveryFraction > 0.4230230485
PASS  pre-lesion global MSE <= 0.0361635
PASS  final recovery active cells <= 800 / 1600
PASS  persistence final active cells <= 800 / 1600
PASS  persistence final global MSE <= 0.0361635
PASS  persistence maximum MSE <= 2x initial persistence MSE
PASS  no non-finite state

CANDIDATE WORTH WIDENING: NO

PRIMARY FAILURE MODE
OVER-SUPPRESSED / NEAR-DEAD PHENOTYPE WITH INSUFFICIENT LESION EFFECT AND ZERO REGENERATION.

The numerical global morphology metric alone is misleading here if read without viability telemetry. Pre-lesion MSE 0.0283585768 is below the morphology gate, but only three cells were active. This is close to the previously characterized sparse-target all-dead regime whose global target loss is approximately 0.0295742.

The lesion technically increased error, but the RelativeDamageEffect was only approximately 0.00624, far below the preregistered 0.10 requirement. A 1-cell reduction from three active cells is not a meaningful morphology-damage event for regeneration inference.

Recovery then collapsed the phenotype completely to zero active cells and produced no stable T50.

DIRECTIONAL COMPARISON
STAB-04 FG+1:
- pre-damage active cells: 1578
- pre-lesion global MSE: 0.1845480204
- lesion improved morphology.

STAB-05 OCC-A1:
- pre-damage active cells: 1206
- pre-lesion global MSE: 0.0701904967
- lesion improved morphology.

STAB-06 AM-05:
- pre-damage active cells: 3
- pre-lesion global MSE: 0.0283585768
- RelativeDamageEffect: 0.0062380726
- final recovery active cells: 0.

The threshold-aligned margin intervention therefore moved the system across the occupancy failure bracket rather than solving it: severe overgrowth was replaced by near-death.

CURRENT SCIENTIFIC BRACKET
The full-grid objective/viability problem is now experimentally bracketed more tightly:

1. Global occupancy-weighted morphology MSE can make the sparse-target dead state competitive.
2. Strong foreground protection avoids death but permits severe overgrowth.
3. Continuous target-background alpha-energy pressure partially suppresses overgrowth but remains insufficient.
4. The tested normalized threshold-aligned alive-margin pressure suppresses background occupancy strongly enough to reopen the near-dead attractor.

This is stronger evidence that canonical P0 requires an objective/mechanism that preserves meaningful foreground/support viability while bounding excess occupancy, rather than simply increasing or decreasing one side of the same scalar pressure.

NEGATIVE KNOWLEDGE RETAINED
1. AM-05 at fixed margin floor 0.05 and coefficient 1.0 is not a viable canonical P0 objective under H96/M16.
2. Threshold alignment can dramatically alter thresholded active-cell cardinality compared with raw alpha-energy regularization.
3. Low global morphology MSE is insufficient evidence of viable morphology on a sparse target.
4. Viability telemetry and meaningful lesion-effect gates remain necessary to reject near-dead false positives.
5. Persistence metrics can also appear numerically acceptable for an almost-dead phenotype and must be interpreted jointly with viability.
6. The P0 search is now bracketed between overgrowth and near-death under the tested objective mechanisms.

DECISION
- CLOSE STAB-06 as negative.
- DO NOT widen AM-05 to additional seeds.
- DO NOT tune its coefficient, margin floor, margin width, or alive threshold inside STAB-06.
- DO NOT weaken the viability, lesion-validity, recovery, morphology, occupancy, persistence, or finite-state gates.
- DO NOT replace the common global evaluation metric; retain it alongside viability telemetry.
- Preserve global_mse, balanced_fg_bg, global_plus_foreground, global_plus_foreground_bg_alpha, and global_plus_foreground_bg_alive_margin for historical reproducibility.
- Retain the near-dead result as first-class negative mechanistic knowledge.

NEXT RESEARCH ACTION
Remain inside canonical DG-1A P0 objective/viability characterization.

Open a new preregistered packet, provisionally DG-1A-P0-STAB-07, before any further scientific execution.

STAB-07 should target the newly demonstrated need to preserve meaningful foreground/support viability while bounding excessive occupancy. Plausible design classes include a coupled viability/occupancy constraint or a support-geometry objective, but NO STAB-07 mechanism is selected by this result record.

Do not turn STAB-07 into an after-the-fact sweep of AM-05's coefficient or margin.
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling from this result.

MACHINE EVIDENCE
evidence/dg1a/p0_stab06_sandbox.json

Full local sandbox evidence SHA-256:
ba29d40ae653d61a6bee97668e402158d4f42f235502b3925280a1136cf6bf59

SCIENTIFIC BOUNDARY
This remains morphology reproduction/regeneration research. The result concerns the tested P0 objective and fixed envelope only. It does not establish or refute cognition, functional specialization, continual learning, ancestor inheritance, structural growth, or general intelligence.
