TITLE: DG-1A-P0 DAMAGE-CAL-01 — Center-Lesion Severity Calibration
DATE: 2026-09-17
STATUS: PREREGISTERED EXPLORATORY CALIBRATION
TRACK: DG-1A
CONFIDENCE: SUPPORTED AS PROTOCOL REFINEMENT

QUESTION
What is the smallest center-lesion severity that produces a valid measurable loss across at least 4 of 5 maturity-gated regeneration seeds without trivially annihilating the developed phenotype?

PURPOSE
The preceding five-seed exploratory replication was inconclusive because regeneration seeds 2 and 4 lost more than one-third of active cells but incurred only 8.34% and 8.88% relative morphology-error increases, below the frozen 10% functional-loss criterion.

This calibration changes lesion severity, not the lesion-validity threshold.

EXPLORATORY STATUS
DAMAGE-CAL-01 is calibration only. It may select a lesion geometry for a later preregistered matched comparison but may not itself support H-P0-3.

FIXED TRAINING FAMILY
Use the existing maturity-gated regeneration curriculum and the same 20 x 20 P0 probe envelope:
- seeds: 0, 1, 2, 3, 4;
- state channels: 16;
- hidden channels: 32;
- training iterations: 200;
- development steps: 8..12;
- batch size: 4;
- pool size: 16;
- damage_min_active_cells: 16;
- evaluation growth horizon: 12;
- recovery horizon: 16.

CANDIDATE EVALUATION LESIONS
Square center lesions relative to the active bounding box:
- 0.50 x 0.50;
- 0.60 x 0.60;
- 0.70 x 0.70.

Each trained seed is evaluated independently at every candidate severity from the same post-training model parameters and fresh seed-grown phenotype. Evaluation RNG is reset consistently per severity so schedule order does not create an RNG-state advantage.

LESION VALIDITY RULE — UNCHANGED
A candidate lesion on a seed is functionally valid only when all conditions hold:
1. DamageEffect > 0;
2. RelativeDamageEffect >= 0.10;
3. ActiveCellRemovalFraction >= 0.10;
4. states remain finite.

NON-ANNIHILATION RULE
A candidate lesion is non-annihilating only when:
- post_damage_active_cells > 0; and
- post_damage_active_cells / pre_damage_active_cells >= 0.20.

This rule prevents selection of a severity that obtains a valid error increase merely by reducing the phenotype to a trivial remnant.

SEVERITY SELECTION RULE
Select the SMALLEST candidate severity for which:
- at least 4 of 5 regeneration seeds have a valid lesion; and
- at least 4 of 5 regeneration seeds satisfy the non-annihilation rule.

If no candidate satisfies both requirements, record DAMAGE-CAL-01 as unsuccessful and design a new lesion family rather than lowering the frozen validity threshold.

SECONDARY OBSERVATIONS
Record for every seed and severity:
- pre-error;
- post-damage error;
- RelativeDamageEffect;
- pre/post active cells;
- ActiveCellRemovalFraction;
- bounded RecoveryFraction;
- stable T50/T90;
- recovery AUC;
- final active cells;
- non-finite events.

RECOVERY IS NOT A SELECTION CRITERION
Severity is selected only for producing meaningful, non-annihilating loss. Do not choose a lesion because it makes regeneration look better or worse.

CONTROL RELATION
Growth-only already produced valid lesions on all five seeds at 0.50 in Exploratory Multi-Seed 01. The selected regeneration-calibrated severity will later be applied identically to both growth-only and regeneration in the next matched gate.

FIBONACCI RELATION
No Fibonacci or golden-ratio mechanism is introduced here. DG-1A-FIB1 remains blocked until P0 is characterized and will use the final P0 protocol as its control substrate.

NEXT ACTION
Run the five regeneration seeds at 0.50, 0.60, and 0.70 under this frozen calibration rule; retain all candidate results; select severity mechanically from the rule above.