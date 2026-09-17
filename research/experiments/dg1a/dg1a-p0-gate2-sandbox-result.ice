TITLE: DG-1A-P0 Gate 2 Sandbox Result — Calibrated 0.60 Evaluation Lesion
DATE: 2026-09-17
STATUS: NUMERICAL SUPPORT RULE MET IN SANDBOX — CONFIRMATORY STATUS OPEN
TRACK: DG-1A
CONFIDENCE: SUPPORTED AS A REPLICATED SANDBOX PATTERN; NOT CONFIRMATORY

QUESTION
Under the calibrated 0.60 evaluation-lesion protocol, does maturity-gated regeneration outperform growth-only development across the preregistered five-seed matched family?

EVIDENCE CLASS
MEASURED SANDBOX RESULT.

PROVENANCE LIMIT
Execution occurred in an isolated reconstructed ChatGPT CPU workspace, not an authenticated commit-bound repository checkout. This run may evaluate the frozen numerical rule but cannot by itself promote H-P0-3 to confirmatory SUPPORTED status.

MACHINE-READABLE EVIDENCE
evidence/dg1a/p0_gate2_sandbox.json

PROTOCOL CLARIFICATION
DAMAGE-CAL-01 explicitly fixed the existing regeneration training family while varying candidate EVALUATION lesions. The Gate 2 sandbox measurements therefore used:

REGENERATION TRAINING DAMAGE
- center lesion 0.50 x 0.50;
- damage probability 0.50;
- maturity threshold 16 active cells.

EVALUATION DAMAGE — BOTH VARIANTS
- center lesion 0.60 x 0.60 of active bounding box.

The measurements summarized below were generated directly with TrainingConfig damage fractions 0.50 and evaluate_growth_and_recovery lesion fractions 0.60. They did not train the regeneration curriculum with 0.60 lesions.

A runner/config coupling capable of confusing these two values was later identified before repository Gate 2 execution support was finalized. Confirmatory Amendment 03 freezes the separation and the runner now records effective training and evaluation damage independently. Historical measurements below are unchanged.

SHARED ENVELOPE
Seeds: 0, 1, 2, 3, 4
Variants: growth_only and maturity-gated regeneration
Grid: 20 x 20
State channels: 16
Hidden channels: 32
Training iterations: 200
Development horizon: 8..12
Evaluation growth horizon: 12
Recovery horizon: 16
Target: repository-native radius-4 disk
Precision: float32
Device: CPU

FROZEN VALIDITY RULE
- positive DamageEffect;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10;
- finite state.

FROZEN DATA-ADEQUACY RULE
At least 4 of 5 matched pairs must have valid lesions in both variants.

FROZEN NUMERICAL SUPPORT RULE
If data adequacy is met:
- at least 4 valid matched pairs favor regeneration;
- median DeltaRecovery >= 0.25;
- regeneration has no greater non-finite failure count;
- no undamaged saved phenotype is restored during repair.

MEASURED PAIRS
Seed 0
Growth: valid lesion, bounded recovery 0.0, final active cells 400.
Regeneration: valid lesion, bounded recovery 1.0, stable T50 4, stable T90 7, final active cells 254.
RelativeDamageEffect regeneration: 0.23139.
DeltaRecovery = +1.0.

Seed 1
Growth: valid lesion, bounded recovery 0.0, final active cells 400.
Regeneration: valid lesion, bounded recovery 1.0, stable T50 3, stable T90 5, final active cells 165.
RelativeDamageEffect regeneration: 0.14116.
DeltaRecovery = +1.0.

Seed 2
Growth: valid lesion, bounded recovery 0.0.
Regeneration: INVALID lesion for paired inference because RelativeDamageEffect = 0.09603 < 0.10, despite 40.91% active-cell removal and bounded recovery 1.0.
This pair is retained but excluded from the primary comparison.

Seed 3
Growth: valid lesion, bounded recovery 0.0, final active cells 398.
Regeneration: valid lesion, bounded recovery 1.0, stable T50 3, stable T90 5, final active cells 161.
RelativeDamageEffect regeneration: 0.15910.
DeltaRecovery = +1.0.

Seed 4
Growth: valid lesion, bounded recovery 0.0, final active cells 399.
Regeneration: valid lesion, bounded recovery 1.0, stable T50 4, stable T90 6, final active cells 103.
RelativeDamageEffect regeneration: 0.12511.
DeltaRecovery = +1.0.

AGGREGATE
Valid matched pairs: 4 / 5
Minimum required: 4 / 5
Valid pairs favoring regeneration: 4 / 4
Median DeltaRecovery: +1.0
Median regeneration RecoveryFraction among valid lesions: 1.0
Regeneration valid lesions attaining stable T50: 4 / 4
Median AUC advantage across valid pairs: approximately +0.820
Numerical support rule met: YES
Non-finite failures observed: none in either compared variant.

GROWTH-ONLY REPLICATED FAILURE MODE
All five growth-only models fail to recover and expand to 398..400 active cells out of the 400-cell grid after lesion. This is now a repeated multi-seed failure pattern rather than a single-seed anomaly.

REGENERATION REPLICATED PATTERN
All five regeneration-trained models reach bounded RecoveryFraction 1.0 and stable recovery thresholds within the declared window. Four of the five lesions satisfy the frozen functional-loss criterion and therefore contribute to the primary comparison.

INTERPRETATION
The calibrated protocol clears the preregistered numerical gate in the sandbox environment. The result is consistent with maturity-gated regeneration training producing qualitatively and quantitatively different repair dynamics than growth-only training on the P0 morphology task.

CLAIM BOUNDARY
Do NOT mark H-P0-3 confirmatory SUPPORTED yet.

The missing gate is source provenance: the exact repository revision must be captured by execution from an actual checkout or equivalently authenticated commit-bound environment.

Allowed statement:
The P0 five-seed sandbox replication meets the preregistered numerical regeneration criterion using 0.50 training damage and calibrated 0.60 evaluation damage.

Not yet allowed:
Yggdrasil has confirmatorily established H-P0-3.

DECISION
1. Keep the 0.50 regeneration training lesion frozen for this P0 family.
2. Keep the 0.60 evaluation lesion protocol frozen.
3. Preserve seed 2 as an invalid-lesion pair; do not lower the threshold.
4. Treat the growth-only full-grid expansion as a documented negative control behavior requiring no assertion weakening.
5. Proceed to commit-bound reproduction when an authorized execution path is available.
6. In parallel, exploratory full-size 40 x 40 P0 work may proceed because the small substrate has replicated the intended qualitative mechanism, but full-size results remain exploratory until provenance/acceptance closes.
7. DG-1A-FIB1 remains blocked from altering P0 and will use P0 as a later scheduling control.

NEXT EXPERIMENT
Bounded full-size P0 exploratory bring-up using the repository base envelope, beginning with one seed and regeneration/growth controls before widening. Do not jump directly to DG-1B or ancestor inheritance.
