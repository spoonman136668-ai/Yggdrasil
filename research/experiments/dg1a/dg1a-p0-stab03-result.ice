TITLE: DG-1A-P0-STAB-03 Result — Foreground/Background-Balanced Morphology Training
DATE: 2026-09-17
STATUS: EXPLORATORY NEGATIVE RESULT
TRACK: DG-1A
CONFIDENCE: SUPPORTED FOR THIS SINGLE-SEED ABLATION

QUESTION
Does replacing the sole global unweighted morphology training loss with a fixed 0.5/0.5 foreground/background-balanced morphology loss prevent the all-dead attractor and improve stable full-grid regeneration without degrading pre-lesion morphology or causing active-cell explosion?

EVIDENCE CLASS
MEASURED SANDBOX RESULT.

PROVENANCE LIMIT
Execution occurred in an isolated reconstructed ChatGPT CPU workspace, not a commit-bound repository checkout.
The intended source revision at execution was:
a80abd3b95dc455dcd4b335207f797409f8005f6

Therefore this result is mechanism-selection evidence only and may not be promoted to confirmatory P0 support.

TEST SURFACE
54 tests passed.
0 failed.
Environment: Python 3 / PyTorch 2.10.0+cpu.

No assertions were disabled, skipped, weakened, or modified merely to obtain the result.

MACHINE-READABLE EVIDENCE
evidence/dg1a/p0_stab03_sandbox.json

PREREGISTERED CANDIDATE
BAL-50

Only the TRAINING morphology objective changed relative to the H96/M16 full-grid regeneration control.

Training morphology objective:
BalancedMSE = 0.5 * ForegroundMSE + 0.5 * BackgroundMSE

Foreground definition:
target alpha > 0.1

The established global visible-channel morphology MSE remained unchanged for evaluation, lesion validity, persistence, recovery, and cross-experiment comparison.

FIXED ENVELOPE
Seed: 0
Variant: regeneration
Grid: 40 x 40
State channels: 16
Hidden channels: 128
Fire rate: 0.5
Training iterations: 200
Learning rate: 0.001
Training development steps: 64..96
Batch size: 8
Pool size: 64
Training damage probability: 0.50
Training damage geometry: center 0.50 x 0.50
Training maturity threshold: 16 active cells
Gradient clip norm: 1.0
Hidden-state L2 weight: 0.00001
Target: deterministic radius-6 disk
Evaluation growth horizon: 96
Recovery horizon: 96
Evaluation lesion: center 0.60 x 0.60
Precision: float32
Device family: CPU

MEASURED TRAINING
Initial recorded balanced loss: 0.2082687914
Minimum recorded loss: 0.0323105827
Final recorded loss: 0.0373177007
Final recorded balanced morphology term: 0.0373161845
Final recorded global morphology MSE telemetry: 0.0580844432
Accumulated training wall-clock: 232.9832269 seconds

The balanced objective optimized substantially below its initial value and did not collapse to the all-dead solution observed in STAB-02.

MEASURED EVALUATION
Pre-lesion global morphology error: 0.1411564797
Post-lesion global morphology error: 0.1050053090
DamageEffect: -0.0361511707
RelativeDamageEffect: -0.2561070579

Pre-damage active cells: 1579 / 1600
Post-damage active cells: 1003 / 1600
ActiveCellRemovalFraction: 0.3647878404
Final active cells after recovery window: 1164 / 1600
Final recovery error: 0.0702440962

Bounded RecoveryFraction: UNDEFINED
Raw RecoveryFraction: UNDEFINED
Normalized recovery AUC: UNDEFINED
Stable T50: NOT ATTAINED
Stable T90: NOT ATTAINED

WHY RECOVERY IS UNDEFINED
The declared lesion improved the established global morphology metric rather than degrading it.

DamageEffect < 0.

Although the lesion removed approximately 36.48% of active cells, global morphology MSE fell by approximately 25.61% relative to the pre-lesion error.

Therefore the pre-lesion phenotype contained substantial harmful/excess activity. Removing structure made it closer to the target.

This is not a regeneration trial under the frozen protocol because there is no measured function/morphology loss to recover.

PERSISTENCE OBSERVATION
Initial persistence error: 0.1344809532
Maximum transient degradation above initial error: 0.0322378278
Final persistence error: 0.0968587473
Initial active cells: 1554
Final active cells: 1244

The phenotype remains dynamically active and later reduces global error, but this does not rescue the regeneration interpretation because the starting 96-step phenotype already violates the preregistered morphology and active-cell limits.

PREREGISTERED IMPROVEMENT RULE
BAL-50 required all of:
1. pre-damage active cells > 0;
2. valid evaluation lesion;
3. stable T50 attained;
4. bounded final RecoveryFraction > 0.423023;
5. pre-lesion global morphology MSE <= 0.0361635;
6. final active cells <= 800 / 1600;
7. finite state.

MEASURED RULE RESULT
1. VIABILITY: PASS
   Pre-damage active cells = 1579.

2. VALID LESION: FAIL
   DamageEffect is negative.

3. STABLE T50: FAIL / NOT DEFINED
   No valid loss exists to recover.

4. RECOVERY > CONTROL: FAIL / NOT DEFINED

5. PRE-LESION MORPHOLOGY LIMIT: FAIL
   0.1411564797 > 0.0361635.

6. FINAL ACTIVE-CELL LIMIT: FAIL
   1164 > 800.

7. FINITE STATE: PASS
   No non-finite state was observed.

OVERALL RESULT
FAIL.

FAILURE MODE
OVERGROWN / POOR-MORPHOLOGY PHENOTYPE WITH DAMAGE IMPROVING THE PRIMARY EVALUATION METRIC.

INTERPRETATION
BAL-50 solves the specific STAB-02 dead-state degeneracy but overcorrects the objective in the opposite direction.

STAB-02 failure:
- foreground pressure too weak under global occupancy-weighted MSE;
- all-dead phenotype becomes competitive.

STAB-03 BAL-50 failure:
- foreground receives equal aggregate weight to the vastly larger background region;
- the learned organism remains viable but expands active structure across almost the entire grid;
- the resulting morphology is sufficiently poor that deleting a large central region improves global MSE.

The evidence therefore identifies an objective-balancing problem rather than a simple binary choice between global MSE and equalized foreground/background MSE.

NEGATIVE KNOWLEDGE RETAINED
1. Equal 0.5/0.5 foreground/background weighting is not a viable full-grid P0 training objective under the tested envelope.
2. Preventing the all-dead attractor is necessary but insufficient; an objective must also preserve strong pressure against unnecessary background activity.
3. Active-cell viability alone cannot be treated as developmental success. BAL-50 is highly viable but morphologically poor.
4. Large geometric damage is not automatically functionally harmful. In this run, removal of 36.48% of active cells improved the declared morphology metric.
5. The lesion-validity contract correctly prevents post-lesion improvement from being mislabeled as regeneration.
6. The unchanged global evaluation metric was essential for discovering the overgrowth problem. Replacing evaluation with the balanced training metric would have obscured cross-experiment comparability.

DECISION
Close STAB-03 as a negative result.
Do not tune the 0.5/0.5 weighting inside STAB-03.
Do not widen BAL-50 to additional seeds.
Do not introduce Fibonacci scheduling yet.
Return to the H96/M16 canonical development horizon and regeneration curriculum for the next objective-design experiment.

NEXT MECHANISM
Open a new preregistered packet rather than modifying STAB-03 after inspection.

Recommended next discriminating objective:
GLOBAL + FOREGROUND SUPPLEMENT.

Conceptually:
TrainingMorphologyLoss = GlobalVisibleMSE + ForegroundVisibleMSE

Rationale:
- retain the original global MSE so background/excess activity remains expensive in proportion to grid occupancy;
- add an explicit foreground term so the all-dead phenotype is no longer competitive merely because foreground occupies a small fraction of the grid;
- change one objective mechanism without introducing an arbitrary post-result BAL-50 weight sweep;
- preserve the existing global evaluation metric unchanged.

This should be a new experiment, provisionally DG-1A-P0-STAB-04, with one fixed coefficient selected before execution and explicit active-cell/morphology gates.

SCIENTIFIC BOUNDARY
This remains morphology reproduction/regeneration work. The result does not establish or refute cognition, functional specialization, continual learning, ancestor inheritance, or general intelligence.

FIBONACCI RELATION
DG-1A-FIB1 remains preserved as a later bounded scheduling/topology/module-sizing ablation. It should not be introduced until a viable canonical P0 phenotype and damage/recovery protocol exist, because otherwise schedule effects would be confounded by the unresolved training objective.
