TITLE: DG-1A-P0-STAB-04 — Global + Foreground Supplemental Morphology Training Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
EVIDENCE CLASS: MEASURED SANDBOX

QUESTION
Does retaining global visible-channel morphology MSE while adding one fixed foreground-visible MSE supplement prevent both sparse-target death and foreground-overgrowth failure modes, while producing a valid lesion and stable full-grid regeneration under the canonical H96/M16 envelope?

PREREGISTERED CANDIDATE
FG+1

TrainingMorphologyLoss = GlobalVisibleMSE + 1.0 * ForegroundVisibleMSE

Total training loss retained the existing hidden-state L2 term.

The global visible-channel morphology MSE remained unchanged as the evaluation metric.

PREREGISTRATION
research/experiments/dg1a/dg1a-p0-stab04-spec.ice

SOURCE / PROVENANCE
Implementation-and-test source revision used as the reconstruction basis:

c90809c9b0c793f003e398731e931aa6a7058f5e

Sandbox execution was performed from a semantic reconstruction of connected GitHub readbacks of that revision because the sandbox could not resolve GitHub directly for a native checkout.

Therefore:
- source_revision_verified_checkout: NO
- sandbox_source_byte_identity: NO
- scientific status: MEASURED SANDBOX, not commit-bound confirmatory acceptance

The limitation is recorded explicitly in machine evidence and does not alter the preregistered thresholds.

TEST SURFACE
Before the scientific candidate was executed, the reconstructed source/test surface completed:

61 passed
0 failed
Python 3.13.5
PyTorch 2.10.0+cpu

This comprises the prior 54-test surface plus 7 STAB-04 tests covering:
- exact GlobalMSE + ForegroundMSE formula;
- target-alpha foreground mask semantics;
- empty-foreground fail-closed behavior;
- unchanged global_mse behavior;
- unchanged balanced_fg_bg behavior;
- STAB-04 config validation;
- runner evidence recording of the effective loss mode;
- finite new-mode loss behavior.

EXECUTION CONTRACT
Exactly one fresh seed-0 FG+1 candidate was executed.

Training used the preregistered 200-iteration H96/M16 regeneration envelope.

The long-running job used a single writer and bounded resumable checkpoints. No concurrent worker touched the checkpoint. The candidate was not restarted or widened.

MEASURED TRAINING RESULT
training iterations:       200 / 200
initial recorded loss:     0.4459555447
minimum recorded loss:     0.0645382553
final recorded loss:       0.0687634796
training loss mode:        global_plus_foreground
training elapsed:          279.830171 s
non-finite state:          NO

MEASURED EVALUATION RESULT
pre-lesion global MSE:     0.1845480204
post-lesion global MSE:    0.1184445843
final recovery global MSE: 0.0662040040

DamageEffect:              -0.0661034361
RelativeDamageEffect:      -0.3581909788

pre-damage active cells:   1578 / 1600
post-damage active cells:  1002 / 1600
active-cell removal:       0.3650190114
final active cells:        1073 / 1600

bounded RecoveryFraction:  undefined
stable T50:                NOT ATTAINED / undefined
stable T90:                NOT ATTAINED / undefined
normalized recovery AUC:   undefined

PREREGISTERED GATE APPLICATION
PASS  pre-damage active cells > 0
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
OVERGROWN / POOR-MORPHOLOGY PHENOTYPE WITH INVALID LESION

The phenotype was highly active before damage: 1578 / 1600 cells.

The evaluation lesion removed 576 active cells, approximately 36.50% of the active phenotype, but the unchanged global morphology MSE improved from 0.1845480204 to 0.1184445843.

Therefore the intervention did not produce a valid morphology loss to regenerate from. Stable recovery thresholds and normalized recovery quantities are not meaningful for this lesion under the preregistered metric contract.

INTERPRETATION
STAB-04 does not rescue the objective-balancing problem.

The added foreground term prevented the sparse all-dead exploit in this run, but it did not preserve acceptable morphology or occupancy. The resulting phenotype remained excessively active and globally inaccurate.

Together with STAB-03, this is evidence that simply adding strong target-foreground pressure while leaving occupancy/background control implicit is insufficient for canonical P0 stabilization.

This does not establish that every possible foreground coefficient fails. STAB-04 was explicitly not a coefficient sweep, and its 1.0 coefficient must not be tuned retroactively.

DECISION
- CLOSE STAB-04 as negative.
- DO NOT widen FG+1 to additional seeds.
- DO NOT tune the FG coefficient inside STAB-04.
- DO NOT replace the global evaluation metric.
- DO NOT reopen STAB-03 BAL-50.
- Preserve global_mse, balanced_fg_bg, and global_plus_foreground for historical reproducibility.

NEXT RESEARCH ACTION
Remain inside canonical DG-1A P0 objective/viability characterization.

Before any further execution, preregister a new bounded experiment packet rather than continuing ad-hoc coefficient tuning. The next packet should target the now-repeated occupancy/overgrowth failure directly while preserving the common global evaluation metric and the H96/M16 envelope unless a separately preregistered reason justifies a change.

Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling from this result.

MACHINE EVIDENCE
evidence/dg1a/p0_stab04_sandbox.json

Machine-evidence SHA-256 before GitHub serialization:
0a1634efcd92d4f611dc75ecf1a6d4fe77814a922ed40e79f786985049df6a51

SCIENTIFIC BOUNDARY
This remains morphology reproduction/regeneration research. The negative result is about the current P0 training objective under the frozen envelope; it says nothing by itself about cognition, specialization, continual learning, ancestor inheritance, or general intelligence.
