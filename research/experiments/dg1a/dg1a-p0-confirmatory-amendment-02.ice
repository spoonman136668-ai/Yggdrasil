TITLE: DG-1A-P0 Confirmatory Amendment 02 — Calibrated Lesion Severity
DATE: 2026-09-17
STATUS: PREREGISTERED FOR NEXT MATCHED P0 GATE
TRACK: DG-1A
CONFIDENCE: SUPPORTED AS PROTOCOL SELECTION

PURPOSE
Freeze the center-lesion severity selected by the independently preregistered DAMAGE-CAL-01 procedure before the next matched growth-only versus maturity-gated-regeneration seed family.

CALIBRATION PROVENANCE
DAMAGE-CAL-01 compared center-lesion fractions 0.50, 0.60, and 0.70 under a rule requiring selection of the smallest candidate with:
- valid functional loss on at least 4/5 regeneration seeds; and
- non-annihilating damage on at least 4/5 regeneration seeds.

Measured candidate counts:
0.50 -> 3/5 valid, 5/5 non-annihilating
0.60 -> 4/5 valid, 5/5 non-annihilating
0.70 -> 5/5 valid, 5/5 non-annihilating

SEVERITY FROZEN FOR NEXT GATE
Center lesion height fraction: 0.60
Center lesion width fraction: 0.60

This value is selected mechanically because it is the smallest candidate satisfying the calibration rule.

UNCHANGED LESION VALIDITY RULE
A lesion contributes to regeneration inference only when all conditions hold:
1. DamageEffect > 0;
2. RelativeDamageEffect >= 0.10;
3. ActiveCellRemovalFraction >= 0.10;
4. relevant states remain finite.

UNCHANGED DATA-ADEQUACY RULE
At least 4 of 5 matched seed pairs must have valid lesions in both variants.

MATCHED SEEDS
0, 1, 2, 3, 4

VARIANTS
growth_only
regeneration with maturity-gated damage curriculum

MATCHED ENVELOPE
- grid: 20 x 20;
- state channels: 16;
- hidden channels: 32;
- training iterations: 200;
- learning rate: 0.001;
- development horizon: 8..12 steps;
- batch size: 4;
- pool size: 16 where applicable;
- regeneration damage probability: 0.5;
- regeneration maturity threshold: 16 active cells;
- evaluation growth horizon: 12;
- recovery horizon: 16;
- target: repository-native radius-4 disk;
- precision: float32 baseline;
- device family for the immediate sandbox replication: CPU.

PRIMARY METRIC
DeltaRecovery(seed) = bounded RecoveryFraction_regeneration - bounded RecoveryFraction_growth_only.

Only pairs valid in both variants contribute.

UNCHANGED NUMERICAL SUPPORT RULE
If at least 4 valid pairs exist:
- at least 4 of 5 valid matched seed pairs must have DeltaRecovery > 0;
- median DeltaRecovery across valid pairs must be >= 0.25;
- regeneration must not have a greater non-finite failure count than growth-only;
- no saved undamaged phenotype may be used for repair.

PROVENANCE GATE
A reconstructed/sandbox run may be used to test the protocol and report whether the numerical rule is met, but may not promote H-P0-3 to confirmatory SUPPORTED status.

Confirmatory support additionally requires execution from source whose exact repository revision is captured by the run evidence.

HISTORICAL PRESERVATION
Do not overwrite the 0.50 exploratory probe evidence or reinterpret it using the new severity. Amendment 02 defines a new gate prospectively.

FIBONACCI RELATION
DG-1A-FIB1 remains separate and blocked. The calibrated 0.60 P0 lesion becomes the reference damage protocol for later scheduling ablations if P0 closes successfully.

NEXT ACTION
Run the matched seeds 0..4 at the frozen 0.60 lesion severity. Retain every run. Apply the validity and support rules exactly as written above.