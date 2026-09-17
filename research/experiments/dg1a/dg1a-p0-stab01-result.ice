TITLE: DG-1A-P0-STAB-01 Result — Maturity-Gate Scaling
DATE: 2026-09-17
STATUS: EXPLORATORY NEGATIVE RESULT
TRACK: DG-1A
CONFIDENCE: SUPPORTED FOR THIS SINGLE-SEED ABLATION

QUESTION
Does increasing the regeneration-training maturity threshold from 16 active cells to 32 or 64 remove full-grid post-repair relapse under the frozen 40 x 40 seed-0 protocol?

EVIDENCE CLASS
MEASURED SANDBOX RESULT.

PROVENANCE LIMIT
Execution occurred in an isolated reconstructed ChatGPT CPU workspace, not a commit-bound checkout. This experiment is mechanism selection only.

MACHINE-READABLE EVIDENCE
evidence/dg1a/p0_stab01_sandbox.json

CONTROL M16
Valid evaluation lesion: YES
RelativeDamageEffect: 0.107996
Pre-lesion error: 0.0241090
Final bounded RecoveryFraction: 0.423023
Stable T50: NOT ATTAINED
Stable T90: NOT ATTAINED
Final active cells: 502 / 1600

CANDIDATE M32
Training maturity threshold: 32 active cells
Training final loss: 0.0291580
Training minimum loss: 0.0266972
Pre-lesion error: 0.0285268
Pre-damage active cells: 6
Post-damage active cells: 4
ActiveCellRemovalFraction: 0.33333
RelativeDamageEffect: 0.005672
Evaluation lesion valid: NO
Final bounded RecoveryFraction: 1.0
Stable T50: 58
Stable T90: 63
Final active cells: 7 / 1600

INTERPRETATION M32
The candidate appears numerically stable after damage, but the phenotype is too sparse / too insensitive to the declared lesion for regeneration inference. Only six cells are active before damage, and the lesion changes morphology error by about 0.57% relative.

The stable threshold crossings therefore do not satisfy the preregistered improvement rule. This is robustness/underdevelopment, not valid repair evidence.

CANDIDATE M64
Training maturity threshold: 64 active cells
Training final loss: 0.0280208
Training minimum loss: 0.0265542
Pre-lesion error: 0.0265135
Pre-damage active cells: 55
Post-damage active cells: 29
ActiveCellRemovalFraction: 0.47273
RelativeDamageEffect: 0.060339
Evaluation lesion valid: NO
Final bounded RecoveryFraction: 0.0
Raw RecoveryFraction: -0.77309
Stable T50: NOT ATTAINED
Stable T90: NOT ATTAINED
Recovery AUC: 0.13393
Final active cells: 158 / 1600

INTERPRETATION M64
The lesion removes nearly half the active cells, but the functional morphology-error increase remains below the frozen 10% validity threshold. The phenotype then worsens instead of recovering.

SELECTION RULE RESULT
M32: FAIL
M64: FAIL
Selected candidate: NONE

HYPOTHESIS RESULT
The simple hypothesis that a larger fixed maturity threshold would solve full-grid repair relapse is not supported by STAB-01.

The threshold changes substantially alter phenotype development and damage sensitivity rather than cleanly improving repair persistence.

NEGATIVE KNOWLEDGE RETAINED
1. Fixed maturity threshold is not a monotonic stabilization knob.
2. Raising the threshold can produce phenotypes too sparse or damage-insensitive for regeneration measurement.
3. Stable post-lesion trajectories are insufficient evidence when the lesion does not create meaningful functional loss.
4. The frozen lesion-validity gate successfully prevents M32 from being falsely interpreted as successful regeneration.

DECISION
Do not widen M32 or M64 to additional seeds.
Do not add intermediate maturity thresholds to this packet after seeing results.
Return the maturity threshold to the M16 P0 control for the next stabilization experiment.

NEXT MECHANISM
Test the training-horizon hypothesis separately.

Full-grid repair evaluation lasts 96 post-damage steps, while training trajectories are sampled only across 64..96 steps. A candidate curriculum with longer developmental trajectories may better constrain late repair dynamics without changing lesion geometry, maturity gating, resource limits, or target.

NEXT EXPERIMENT
DG-1A-P0-STAB-02 — Development-Horizon Stabilization.

Keep maturity threshold = 16 and all other full-grid P0 parameters fixed. Compare the M16 control against a preregistered longer-horizon regeneration curriculum. Do not introduce Fibonacci scheduling, active-cell penalties, structural growth, or P1 functionality in STAB-02.