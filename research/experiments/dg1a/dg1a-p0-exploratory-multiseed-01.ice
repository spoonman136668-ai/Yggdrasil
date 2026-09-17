TITLE: DG-1A-P0 Exploratory Multi-Seed 01 — Matched Growth vs Regeneration
DATE: 2026-09-17
STATUS: EXPLORATORY MEASURED RESULT — INCONCLUSIVE UNDER FROZEN DATA-ADEQUACY GATE
TRACK: DG-1A
CONFIDENCE: SUPPORTED AS A REPLICATED SANDBOX PATTERN; NOT CONFIRMATORY

QUESTION
Does the maturity-gated regeneration curriculum reproduce its single-seed recovery advantage over growth-only training across seeds 0..4 under the frozen lesion-validity rules?

EVIDENCE CLASS
MEASURED SANDBOX RESULT.

PROVENANCE LIMIT
Execution occurred in an isolated ChatGPT CPU workspace reconstructed from connected-GitHub source and test contents. It was not an authenticated repository checkout and therefore is not commit-bound acceptance.

Intended source reference at run start:
daf759dcabae637e7bb8ae197c1c823960b3e5e1

The reconstructed source exercised the same declared P0 training/recovery interfaces and the 42-test equivalent sandbox surface was green, but this result must remain exploratory until repeated from commit-bound source.

MACHINE-READABLE EVIDENCE
evidence/dg1a/p0_multiseed_exploratory_01.json

ENVIRONMENT
Device: CPU
PyTorch: 2.10.0+cpu
Precision: float32

MATCHED ENVELOPE
Seeds: 0, 1, 2, 3, 4
Variants: growth_only, regeneration
Grid: 20 x 20
State channels: 16
Hidden channels: 32
Training iterations: 200
Development horizon: 8..12 steps
Batch size: 4
Pool size: 16
Evaluation growth horizon: 12 steps
Recovery horizon: 16 steps
Center lesion: 50% x 50% of active bounding box
Regeneration maturity gate: 16 active cells

FROZEN LESION VALIDITY RULE
A lesion is valid only when:
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10;
- states remain finite.

No threshold was changed after inspecting these runs.

RESULT SUMMARY
Seed 0:
- growth lesion valid; bounded recovery 0.0;
- regeneration lesion valid; bounded recovery 1.0;
- DeltaRecovery = +1.0;
- regeneration stable T50 = 3; stable T90 = 5.

Seed 1:
- growth lesion valid; bounded recovery 0.0;
- regeneration lesion valid; bounded recovery 1.0;
- DeltaRecovery = +1.0;
- regeneration stable T50 = 2; stable T90 = 3.

Seed 2:
- growth lesion valid;
- regeneration lesion INVALID because RelativeDamageEffect = 0.08343 < 0.10;
- regeneration removed 36.36% of active cells and later reached bounded recovery 1.0, but this apparent repair is excluded from the paired regeneration inference by the frozen rule.

Seed 3:
- growth lesion valid; bounded recovery 0.0;
- regeneration lesion valid; bounded recovery 1.0;
- DeltaRecovery = +1.0;
- regeneration stable T50 = 2; stable T90 = 3.

Seed 4:
- growth lesion valid;
- regeneration lesion INVALID because RelativeDamageEffect = 0.08879 < 0.10;
- regeneration removed 37.50% of active cells and later reached bounded recovery 1.0, but this apparent repair is excluded from the paired regeneration inference by the frozen rule.

AGGREGATE
Valid matched pairs: 3 / 5
Frozen minimum for interpretation: 4 / 5
Valid pairs favoring regeneration: 3 / 3
Median DeltaRecovery among valid pairs: +1.0
Minimum data adequacy met: NO

GROWTH-ONLY FAILURE PATTERN
Every growth-only seed received a valid lesion and finished with bounded RecoveryFraction 0.0.

Final active-cell counts were 400, 400, 400, 398, and 399 out of 400 grid positions respectively. This replicates the earlier qualitative failure mode: post-lesion developmental expansion fills almost the entire grid while morphology error worsens rather than repairs.

REGENERATION PATTERN
Every regeneration seed reached bounded RecoveryFraction 1.0 and stable T50/T90 inside the recovery window.

However, only seeds 0, 1, and 3 satisfy the frozen lesion-validity rule. Seeds 2 and 4 are robustness/weak-damage cases for purposes of this gate and must not be counted as regeneration successes.

INTERPRETATION
The replicated pattern strongly motivates continued investigation of maturity-gated regeneration training. Across every seed, its post-lesion dynamics are qualitatively different from the growth-only collapse.

Nevertheless, the preregistered data-adequacy condition is not met. Therefore H-P0-3 remains INCONCLUSIVE at this gate.

Do not relabel the result SUPPORTED by ignoring seeds 2 and 4 or lowering the 10% threshold.

DIAGNOSTIC FINDING
The limiting factor is now lesion calibration for compact regeneration-trained phenotypes, not observed repair dynamics.

Seeds 2 and 4 lose more than one-third of their active cells under the 50% center lesion yet incur only 8.34% and 8.88% relative morphology-error increases. This suggests the trained phenotype can distribute visible function such that a geometrically substantial lesion is functionally mild under the current morphology metric.

That may indicate useful robustness, but it prevents regeneration inference under the current protocol.

DECISION
1. Retain the frozen 10% RelativeDamageEffect criterion.
2. Do not count weak-damage seeds as regeneration evidence.
3. Do not modify P0 training to add Fibonacci scheduling.
4. Perform a bounded lesion-severity calibration as a NEW exploratory experiment, using stronger center lesions while retaining all results.
5. Freeze the selected severity in a new amendment before the next multi-seed gate.

NEXT EXPERIMENT
DG-1A-P0 DAMAGE-CAL-01.

Evaluate the existing matched P0 family at center-lesion fractions 0.50, 0.60, and 0.70. The goal is not to maximize damage. Select the smallest severity that produces valid functional loss across the required seed fraction without trivially annihilating the phenotype.

No confirmatory claim is authorized from calibration runs.
