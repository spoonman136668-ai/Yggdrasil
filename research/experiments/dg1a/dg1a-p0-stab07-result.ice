TITLE: DG-1A-P0-STAB-07 — One-Cell Target-Support Halo Occupancy Control Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
EVIDENCE CLASS: MEASURED SANDBOX

QUESTION
Can canonical P0 preserve meaningful viable target support while bounding excess occupancy if background occupancy pressure is restricted to far-field cells outside the target's own one-neighborhood support halo?

PREREGISTERED CANDIDATE
HALO-1

ForegroundMask = target alpha > 0.1
SupportHaloMask = one 3 x 3 max-pool dilation of ForegroundMask
FarFieldBackgroundAlphaMSE = mean(state_alpha^2 over target-background cells outside SupportHaloMask)

TrainingMorphologyLoss =
    GlobalVisibleMSE
    + ForegroundVisibleMSE
    + FarFieldBackgroundAlphaMSE

The foreground coefficient remained 1.0.
The far-field coefficient remained 1.0.
The support radius remained exactly one cell.
The target/alive threshold remained 0.1.
The common global visible-channel morphology MSE remained unchanged for evaluation.

FROZEN SUPPORT GEOMETRY
For the 40 x 40 radius-6 target:
- target foreground cells: 113;
- one-cell support-halo cells including foreground: 169;
- support-ring-only cells: 56;
- far-field cells: 1431.

The 56-cell support ring received no dedicated occupancy penalty. The global visible loss continued to evaluate every grid cell.

PREREGISTRATION
research/experiments/dg1a/dg1a-p0-stab07-spec.ice

SOURCE / PROVENANCE
Implementation-and-test source revision used as the reconstruction basis:

5635413653888f36e85305877be95b587c017d70

Sandbox execution was performed from a semantic reconstruction of connected GitHub readbacks of that revision rather than a native byte-identical checkout.

Therefore:
- source_revision_verified_checkout: NO
- sandbox_source_byte_identity: NO
- scientific status: MEASURED SANDBOX, not commit-bound confirmatory acceptance

TEST SURFACE
Before scientific execution, the full reconstructed source/test surface completed:

89 passed
0 failed
pytest return code: 0
Python 3.13.5
PyTorch 2.10.0+cpu

The additive HALO-1 tests covered:
- foreground and one-cell support-halo exemption;
- exact radius-6 support geometry of 113 / 169 / 56 / 1431 cells;
- missing-foreground fail-closed behavior;
- missing-far-field fail-closed behavior;
- exact HALO-1 objective formula;
- finite new-mode loss behavior;
- preregistered all-dead loss sanity;
- frozen STAB-07 config validation;
- normal-training component telemetry;
- resumable-training component telemetry;
- runner evidence recording of the effective mode and far-field telemetry.

No existing assertion was weakened, skipped, disabled, or modified merely to obtain the result.

EXECUTION CONTRACT
Exactly one fresh seed-0 HALO-1 candidate was executed.

Training used the frozen 200-iteration H96/M16 regeneration envelope.
The run used one writer and deterministic resumable checkpoints in bounded 10-iteration segments.
No concurrent worker touched the checkpoint.
No second candidate, new seed, coefficient change, halo-radius change, threshold change, or gate change was introduced.

MEASURED TRAINING RESULT
training iterations:       200 / 200
initial recorded loss:     0.4459555447
minimum recorded loss:     0.1897521913
final recorded loss:       0.2067640871
training loss mode:        global_plus_foreground_farfield_bg_alpha
training elapsed:          275.6193747 s
non-finite state:          NO

Final recorded component telemetry:
- global morphology MSE:       0.0509372130
- foreground morphology MSE:   0.1108182743
- far-field background alpha:  0.0450081341
- composite morphology loss:   0.2067636251
- hidden penalty:              0.0458556637
- gradient norm:               0.5220074058

MEASURED EVALUATION RESULT
pre-lesion global MSE:     0.0625592172
post-lesion global MSE:    0.0531895496
final recovery global MSE: 0.0762912259

DamageEffect:              -0.0093696676
RelativeDamageEffect:      -0.1497727759

pre-damage active cells:   1094 / 1600
post-damage active cells:   570 / 1600
active-cell removal:       0.4789762340
final active cells:        1232 / 1600

bounded RecoveryFraction:  undefined
raw RecoveryFraction:      undefined
stable T50:                NOT ATTAINED / undefined
stable T90:                NOT ATTAINED / undefined
normalized recovery AUC:   undefined

PERSISTENCE OBSERVATION
initial persistence error: 0.0572690740
maximum degradation:       0.0546591282
final persistence error:   0.0921664238
initial active cells:      1005
final active cells:        1276
active-cell drift:         +271
visible-state drift MSE:   0.0299066454
mean step update magnitude:0.0041742743

The phenotype remained expansive under the fixed persistence window rather than settling into bounded target support.

PREREGISTERED GATE APPLICATION
PASS  pre-damage active cells >= 113
FAIL  pre-damage active cells <= 800
FAIL  DamageEffect > 0
FAIL  RelativeDamageEffect >= 0.10
PASS  ActiveCellRemovalFraction >= 0.10
FAIL  stable T50 attained
FAIL  final RecoveryFraction > 0.4230230485
FAIL  pre-lesion global MSE <= 0.0361635
PASS  final recovery active cells >= 113
FAIL  final recovery active cells <= 800
PASS  persistence final active cells >= 113
FAIL  persistence final active cells <= 800
FAIL  persistence final global MSE <= 0.0361635
PASS  persistence maximum MSE <= 2x initial persistence MSE
PASS  no non-finite state

CANDIDATE WORTH WIDENING: NO

PRIMARY FAILURE MODE
VIABLE BUT OVERGROWN / EXPANSIVE PHENOTYPE WITH INVALID LESION.

HALO-1 clearly avoided STAB-06's near-dead failure. The phenotype exceeded the preregistered target-derived viability floor at growth, recovery, and persistence.

However, it did not solve bounded support:
- pre-damage activity was 1094, far above the 800 ceiling;
- final recovery activity expanded to 1232;
- persistence expanded from 1005 to 1276 active cells;
- persistence morphology error worsened from 0.0572691 to 0.0921664.

The evaluation lesion removed 524 active cells, approximately 47.90% of the active phenotype, yet global morphology MSE improved from 0.0625592 to 0.0531895.

Therefore substantial harmful/excess structure remained before damage. There was no valid morphology-loss event from which to infer regeneration.

DIRECTIONAL COMPARISON WITH STAB-05
STAB-05 OCC-A1, all target-background cells penalized:
- pre-damage active cells: 1206;
- pre-lesion global MSE:   0.0701904967;
- final recovery active:   1329;
- persistence final active:1378.

STAB-07 HALO-1, one-cell target-support halo exempted:
- pre-damage active cells: 1094;
- pre-lesion global MSE:   0.0625592172;
- final recovery active:   1232;
- persistence final active:1276.

Observed directional change relative to STAB-05:
- pre-damage activity reduced by 112, approximately 9.29%;
- pre-lesion global MSE reduced by approximately 10.87%;
- final recovery activity reduced by 97;
- persistence final activity reduced by 102.

These are directionally favorable but remain far from the absolute preregistered gates. This packet does not authorize widening or halo-radius tuning.

DIRECTIONAL COMPARISON WITH STAB-06
STAB-06 AM-05 threshold-aligned pressure:
- pre-damage active cells: 3;
- final recovery active cells: 0;
- near-dead phenotype.

STAB-07 HALO-1:
- pre-damage active cells: 1094;
- final recovery active cells: 1232.

Thus preserving the one-neighborhood target support region radically changed viability relative to AM-05. The intervention crossed back into viable-but-overgrown behavior rather than finding bounded viable support.

CURRENT SCIENTIFIC BRACKET
The accumulated full-grid evidence now separates several mechanism effects:

1. Global sparse-target morphology MSE alone can make death competitive.
2. Strong foreground protection can preserve viability while permitting severe overgrowth.
3. Continuous alpha-energy pressure across all background cells partially suppresses overgrowth but remains insufficient.
4. Strong threshold-aligned occupancy pressure can suppress support into near-death.
5. Exempting one local target-support halo restores robust viability but still permits excessive global support and expansion.

This argues against treating canonical P0 as a simple one-dimensional regularization-strength problem. Spatial support structure matters, but a binary exempt-versus-penalized one-cell halo is not sufficient by itself.

NEGATIVE KNOWLEDGE RETAINED
1. HALO-1 at support radius 1 and far-field coefficient 1.0 is insufficient for canonical P0 stabilization under H96/M16.
2. A target-derived support halo can preserve viability relative to threshold-aligned suppression.
3. Preserving local support does not automatically bound far-field active-cell cardinality.
4. The one-cell halo produced modest directional improvement over all-background continuous alpha pressure, but not a valid lesion or bounded morphology.
5. Low/medium training objective values remain insufficient without active-cell, persistence, lesion-validity, and recovery telemetry.
6. The failure remains dynamic: occupancy expands after nominal growth and after damage.

DECISION
- CLOSE STAB-07 as negative.
- DO NOT widen HALO-1 to additional seeds.
- DO NOT tune its halo radius, far-field coefficient, foreground coefficient, or thresholds inside STAB-07.
- DO NOT weaken the target-derived 113-cell viability floor or existing occupancy/morphology/recovery gates.
- DO NOT replace the common global evaluation metric.
- Preserve all six implemented historical training-loss modes for reproducibility.
- Retain HALO-1's support-geometry result as first-class mechanistic negative knowledge.

NEXT RESEARCH ACTION
Remain inside canonical DG-1A P0 objective/viability characterization.

Open a new preregistered packet, provisionally DG-1A-P0-STAB-08, before any further scientific execution.

The next design should use the STAB-05/06/07 bracket to test one fixed mechanism that constrains support geometry or occupancy while explicitly preserving meaningful target viability. Plausible mechanism classes include graded support geometry or a coupled target-support/occupancy objective, but NO STAB-08 mechanism is selected by this result record.

Do not turn STAB-08 into an after-the-fact coefficient or halo-radius sweep of STAB-07.
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling from this result.

MACHINE EVIDENCE
evidence/dg1a/p0_stab07_sandbox.json

The durable GitHub evidence is a compact summary of the full sandbox evidence.
Full local sandbox evidence SHA-256:
7c239b160e65c5bbf42e85657262c551853f6b42d98946cd47b5a10c0a5823b4

SCIENTIFIC BOUNDARY
This remains morphology reproduction/regeneration research. The result concerns the tested P0 objective and fixed envelope only. It does not establish or refute cognition, functional specialization, continual learning, ancestor inheritance, structural growth, or general intelligence.
