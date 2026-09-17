TITLE: DG-1A-P0 Confirmatory Amendment 03 — Separate Training and Evaluation Lesion Severity
DATE: 2026-09-17
STATUS: PREREGISTERED PROTOCOL CLARIFICATION BEFORE GATE 2 EXECUTION
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FROM DAMAGE-CAL-01 CONTRACT

PURPOSE
Prevent an implementation coupling from silently changing the regeneration training curriculum when applying the 0.60 evaluation lesion selected by DAMAGE-CAL-01.

DISCOVERY
The current P0 runner historically sourced TrainingConfig damage_height_fraction and damage_width_fraction from recovery.lesion.*.

That was harmless while training and evaluation both used 0.50, but it becomes invalid for Gate 2 because DAMAGE-CAL-01 explicitly states:
- FIXED TRAINING FAMILY;
- candidate EVALUATION lesions 0.50, 0.60, 0.70;
- each trained seed is evaluated at each candidate severity from the same post-training model parameters.

Therefore the calibration selected an evaluation intervention severity. It did not authorize changing the regeneration curriculum damage severity.

FROZEN GATE 2 TRAINING DAMAGE
Regeneration training center lesion:
- height fraction: 0.50
- width fraction: 0.50
- probability: 0.50
- maturity threshold: 16 active cells

FROZEN GATE 2 EVALUATION DAMAGE
Center lesion:
- height fraction: 0.60
- width fraction: 0.60

IMPLEMENTATION REQUIREMENT
The P0 configuration/runner must expose training lesion geometry independently from recovery/evaluation lesion geometry.

For historical configs that omit explicit training lesion geometry, backward-compatible interpretation may use recovery.lesion.* only to reproduce those historical runs.

All new Gate 2 configs must specify training damage geometry explicitly.

NO SCIENTIFIC THRESHOLD CHANGE
This amendment changes no success, lesion-validity, or data-adequacy threshold.
It only preserves the fixed training family required by the already-preregistered calibration protocol.

UNCHANGED GATE 2 ENVELOPE
- seeds: 0,1,2,3,4;
- variants: growth_only and regeneration;
- grid: 20 x 20;
- state channels: 16;
- hidden channels: 32;
- training iterations: 200;
- learning rate: 0.001;
- development horizon: 8..12;
- batch size: 4;
- pool size: 16 where applicable;
- evaluation growth horizon: 12;
- recovery horizon: 16;
- target: repository-native radius-4 disk;
- float32 CPU for immediate sandbox replication.

VALIDITY AND SUPPORT RULES
Unchanged from Confirmatory Amendment 02.

FIBONACCI RELATION
No Fibonacci scheduling is introduced into P0. DG-1A-FIB1 remains a post-P0 ablation and will use the characterized P0 protocol as its reference substrate.

NEXT ACTION
1. Separate training and evaluation lesion fields in the implementation.
2. Add regression tests proving the runner/config can represent 0.50 training damage with 0.60 evaluation damage.
3. Create new Gate 2 configs rather than rewriting historical 0.50 probe configs.
4. Execute seeds 0..4 and retain all results.