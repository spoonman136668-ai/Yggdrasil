TITLE: DG-1A-P0-STAB-01 — Full-Grid Regeneration Maturity-Gate Stabilization Ablation
DATE: 2026-09-17
STATUS: PREREGISTERED EXPLORATORY ABLATION
TRACK: DG-1A
CONFIDENCE: PLAUSIBLE

QUESTION
Does scaling the regeneration-training maturity threshold with phenotype size reduce post-repair relapse at the 40 x 40 P0 envelope without degrading pre-lesion morphology or causing active-cell explosion?

MOTIVATION
Full-grid seed 0 with damage_min_active_cells = 16 produced:
- a valid 0.60 evaluation lesion;
- first T50 at step 15 and first T90 at step 31;
- no stable T50/T90 by the end of the 96-step recovery window;
- bounded final RecoveryFraction approximately 0.423;
- final active cells 502 / 1600.

The small-grid probe used the same fixed 16-cell maturity threshold on a 20 x 20 grid. At full scale this threshold may permit lesion training on states that are too immature relative to the developed phenotype.

HYPOTHESIS
A higher minimum-active-cell threshold for applying regeneration-training damage will bias repair examples toward more mature phenotypes and may improve long-horizon repair stability.

This is a mechanism hypothesis, not an assumed improvement.

CONTROL
M16
- damage_min_active_cells = 16
Existing full-grid seed-0 result is the control and will not be rerun unless implementation invalidation is discovered.

CANDIDATE M32
- damage_min_active_cells = 32

CANDIDATE M64
- damage_min_active_cells = 64

WHY THESE VALUES
They are powers-of-two scaling probes chosen before candidate outcomes are inspected. They approximately test 2x and 4x the existing threshold while remaining below the seed-0 mature pre-damage active population observed in the control.

No additional thresholds may be inserted into STAB-01 after results are inspected.

FIXED ENVELOPE
Seed: 0
Variant: regeneration only
Grid: 40 x 40
State channels: 16
Hidden channels: 128
Fire rate: 0.5
Training iterations: 200
Learning rate: 0.001
Training development horizon: 64..96
Batch size: 8
Pool size: 64
Training damage probability: 0.50
Training damage geometry: center 0.50 x 0.50
Gradient clip norm: 1.0
Hidden-state L2 weight: 0.00001
Target: deterministic radius-6 disk
Evaluation growth horizon: 96
Recovery horizon: 96
Evaluation lesion: center 0.60 x 0.60
Precision: float32
Device family: CPU for immediate sandbox execution

PRIMARY METRIC
Stable T50 within the 96-step recovery horizon.

SECONDARY METRICS
- bounded final RecoveryFraction;
- stable T90;
- normalized recovery AUC;
- pre-lesion morphology error;
- RelativeDamageEffect;
- ActiveCellRemovalFraction;
- final active cells;
- maximum/final active-cell behavior;
- training minimum/final loss;
- training wall-clock;
- checkpoint/state-pool size.

VALID LESION REQUIREMENT
The evaluation lesion must satisfy the existing P0 validity rule:
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10;
- finite state.

If a candidate fails this rule, stable-recovery interpretation is invalid for that candidate.

CANDIDATE IMPROVEMENT RULE
A candidate is considered worth widening only if all are true:
1. evaluation lesion is valid;
2. stable T50 is attained;
3. bounded final RecoveryFraction > the M16 control value of 0.423023;
4. pre-lesion error is not worse than 1.5x the M16 control pre-error of 0.0241090;
5. final active cells do not exceed 800 / 1600;
6. no non-finite state occurs.

SELECTION RULE
If both M32 and M64 satisfy the improvement rule, select the lower threshold M32 for widening unless M64 improves final RecoveryFraction by at least 0.15 absolute over M32.

If neither satisfies the rule, record STAB-01 negative and test a different stabilization factor in a new preregistered packet rather than adding thresholds post hoc.

CLAIM BOUNDARY
STAB-01 is exploratory single-seed mechanism selection.
It cannot establish full-grid H-P0-3 support.

FIBONACCI RELATION
No Fibonacci schedule is used in STAB-01. Keeping the canonical stabilization test separate prevents Fibonacci priors from being credited for a repair-stability effect that may be explained by ordinary curriculum maturity.

If canonical stabilization remains unresolved after bounded P0 mechanisms are tested, the relapse phenotype may become a useful later FIB1-R scheduling target.

NEXT ACTION
Execute M32 and M64 from fresh model initialization under seed 0. Retain both results regardless of outcome. Apply the selection rule exactly as written.