TITLE: DG-1A-P0-STAB-05 — Background-Alpha Occupancy Suppression Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
EVIDENCE CLASS: MEASURED SANDBOX

QUESTION
Does adding one explicit target-background alpha/liveness penalty to the STAB-04 composite training objective suppress the repeated overgrown phenotype while preserving foreground viability, acceptable global morphology, a valid lesion, and stable full-grid regeneration under the canonical H96/M16 envelope?

PREREGISTERED CANDIDATE
OCC-A1

TrainingMorphologyLoss = GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAlphaMSE

BackgroundAlphaMSE = mean(state_alpha^2 over target-background pixels)

Target background remained defined as target alpha <= 0.1.
The foreground coefficient remained 1.0.
The new background-alpha coefficient was fixed at 1.0 before execution.
The existing hidden-state L2 term remained unchanged.
The common global visible-channel morphology MSE remained unchanged for evaluation.

PREREGISTRATION
research/experiments/dg1a/dg1a-p0-stab05-spec.ice

SOURCE / PROVENANCE
Implementation-and-test source revision used as the reconstruction basis:

8c1acff13ec5d6e43b7520793555dbc9ac849f34

Sandbox execution was performed from a semantic reconstruction of connected GitHub readbacks of that revision because the sandbox did not have a native byte-identical checkout.

Therefore:
- source_revision_verified_checkout: NO
- sandbox_source_byte_identity: NO
- scientific status: MEASURED SANDBOX, not commit-bound confirmatory acceptance

This limitation does not alter the preregistered thresholds or measured values.

TEST SURFACE
Before the scientific candidate was executed, the reconstructed source/test surface completed:

69 passed
0 failed
Python 3.13.5
PyTorch 2.10.0+cpu

The additive STAB-05 tests covered:
- background-alpha helper target-background semantics;
- alpha-only occupancy measurement;
- missing-background fail-closed behavior;
- exact OCC-A1 objective formula;
- finite new-mode loss behavior;
- preregistered all-dead loss sanity;
- frozen STAB-05 config validation;
- normal-training component telemetry;
- resumable-training component telemetry;
- runner evidence recording of the effective mode and occupancy telemetry.

No existing assertion was weakened, skipped, disabled, or modified merely to obtain the result.

EXECUTION CONTRACT
Exactly one fresh seed-0 OCC-A1 candidate was executed.

Training used the preregistered 200-iteration H96/M16 regeneration envelope.
The run used one writer and bounded resumable checkpoints.
A longer attempted segment exceeded the sandbox call window without producing a new confirmed checkpoint; the run resumed only from the last confirmed checkpoint and returned to the proven bounded cadence.
No concurrent worker touched the checkpoint.
No second candidate, restart-with-new-seed, coefficient change, or threshold change was introduced.

MEASURED TRAINING RESULT
training iterations:       200 / 200
initial recorded loss:     0.4459555447
minimum recorded loss:     0.1833379418
final recorded loss:       0.1999244839
training loss mode:        global_plus_foreground_bg_alpha
training elapsed:          290.4802501 s
non-finite state:          NO

Final recorded component telemetry:
- global morphology MSE:   0.0582330227
- foreground morphology:   0.0783901364
- background alpha MSE:    0.0633000508
- composite morphology:    0.1999232173

MEASURED EVALUATION RESULT
pre-lesion global MSE:     0.0701904967
post-lesion global MSE:    0.0557577237
final recovery global MSE: 0.0893541500

DamageEffect:              -0.0144327730
RelativeDamageEffect:      -0.2056228929

pre-damage active cells:   1206 / 1600
post-damage active cells:   654 / 1600
active-cell removal:       0.4577114428
final active cells:        1329 / 1600

bounded RecoveryFraction:  undefined
stable T50:                NOT ATTAINED / undefined
stable T90:                NOT ATTAINED / undefined
normalized recovery AUC:   undefined

PERSISTENCE OBSERVATION
initial persistence error: 0.0642844662
maximum degradation:       0.0595339239
final persistence error:   0.1067116261
initial active cells:      1140
final active cells:        1378
active-cell drift:         +238
visible-state drift MSE:   0.0271932986

The phenotype therefore remained dynamically unstable/expansive under the fixed persistence window rather than settling into a bounded target-like morphology.

PREREGISTERED GATE APPLICATION
PASS  pre-damage active cells > 0
FAIL  pre-damage active cells <= 800 / 1600
FAIL  DamageEffect > 0
FAIL  RelativeDamageEffect >= 0.10
PASS  ActiveCellRemovalFraction >= 0.10
FAIL  stable T50 attained
FAIL  final RecoveryFraction > 0.423023
FAIL  pre-lesion global MSE <= 0.0361635
FAIL  final active cells <= 800 / 1600
PASS  no non-finite state

CANDIDATE WORTH WIDENING: NO

PRIMARY FAILURE MODE
PARTIALLY SUPPRESSED BUT STILL OVERGROWN / POOR-MORPHOLOGY PHENOTYPE WITH INVALID LESION.

The evaluation lesion removed 552 active cells, approximately 45.77% of the active phenotype, but the unchanged global morphology MSE improved from 0.0701904967 to 0.0557577237.

Therefore the pre-lesion phenotype still contained substantial excess/harmful structure. There was no valid morphology loss from which to infer regeneration under the frozen evaluation contract.

DIRECTIONAL COMPARISON WITH STAB-04
STAB-04 FG+1:
- pre-damage active cells: 1578
- pre-lesion global MSE:   0.1845480204

STAB-05 OCC-A1:
- pre-damage active cells: 1206
- pre-lesion global MSE:   0.0701904967

Observed change:
- pre-damage active cells reduced by 372, approximately 23.57%;
- pre-lesion global MSE reduced by approximately 61.97%.

This is meaningful directional evidence that explicit target-background alpha pressure changes the learned phenotype in the intended direction.

It is not a successful P0 result:
- activity remained far above the preregistered 800-cell ceiling;
- global morphology remained nearly 1.94x above the 0.0361635 gate;
- damage still improved the common evaluation metric;
- post-lesion evolution expanded to 1329 active cells;
- persistence expanded from 1140 to 1378 active cells while morphology error worsened.

INTERPRETATION
STAB-05 provides evidence that explicit occupancy control is mechanistically relevant, but the tested alpha-energy penalty at fixed coefficient 1.0 is insufficient to produce a bounded canonical P0 phenotype.

The negative result is more informative than a simple repeat of STAB-03/STAB-04 because the intervention substantially reduced both active occupancy and pre-lesion global error while failing to cross the absolute gates.

The remaining failure cannot be cleanly described as 'foreground pressure inevitably causes maximal overgrowth.' Occupancy-specific pressure partially counteracted that behavior.

However, the result also shows that reducing continuous target-background alpha energy does not by itself guarantee bounded active-cell cardinality or stable support geometry. Alpha/liveness remained sufficiently distributed and dynamic for the organism to violate the occupancy ceiling and expand during persistence/recovery.

No conclusion is authorized about alternative occupancy penalties, coefficients, cardinality surrogates, support-geometry terms, or architectural mechanisms from this single candidate.

NEGATIVE KNOWLEDGE RETAINED
1. A coefficient-1.0 target-background alpha-energy penalty is insufficient for canonical P0 stabilization under H96/M16.
2. The intervention produces a substantial directional reduction in overgrowth and global morphology error relative to STAB-04.
3. Continuous alpha-energy suppression and thresholded active-cell cardinality are not interchangeable objectives.
4. A phenotype can improve substantially relative to the previous candidate and still remain invalid for regeneration inference.
5. The unchanged global evaluation metric again detects harmful/excess structure because lesioning improved morphology.
6. Persistence remains an essential discriminator: OCC-A1 expanded activity and worsened morphology after the nominal growth horizon.

DECISION
- CLOSE STAB-05 as negative.
- DO NOT widen OCC-A1 to additional seeds.
- DO NOT tune the background-alpha coefficient inside STAB-05.
- DO NOT change the foreground coefficient inside STAB-05.
- DO NOT replace the global evaluation metric.
- Preserve global_mse, balanced_fg_bg, global_plus_foreground, and global_plus_foreground_bg_alpha for historical reproducibility.
- Retain the directional occupancy result as first-class negative/mechanistic knowledge.

NEXT RESEARCH ACTION
Remain inside canonical DG-1A P0 objective/viability characterization.

Open a new preregistered packet, provisionally DG-1A-P0-STAB-06, before any additional scientific execution.

STAB-06 should be designed to discriminate the remaining mismatch between continuous alpha-energy pressure and actual bounded support/active-cell structure. Plausible mechanism classes for consideration include an explicit differentiable occupancy/cardinality surrogate or a support-geometry penalty, but NO STAB-06 mechanism is selected by this result record.

Do not convert STAB-06 into an after-the-fact sweep of STAB-05's coefficient.

Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling from this result.

MACHINE EVIDENCE
evidence/dg1a/p0_stab05_sandbox.json

The durable GitHub evidence is a compact summary of the full sandbox evidence.
Full local sandbox evidence SHA-256:
32108c4908e3328188dfe2223b032881bcd8944c73c22f1b41e96e6a7fb79f3c

SCIENTIFIC BOUNDARY
This remains morphology reproduction/regeneration research. The result concerns the tested P0 objective and fixed envelope only. It does not establish or refute cognition, functional specialization, continual learning, ancestor inheritance, structural growth, or general intelligence.
