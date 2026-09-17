TITLE: DG-1A-P0 Confirmatory Amendment 01 — Lesion Validity and Multi-Seed Regeneration Gate
DATE: 2026-09-17
STATUS: PREREGISTERED FOR NEXT P0 MULTI-SEED GATE
TRACK: DG-1A
CONFIDENCE: SUPPORTED AS MEASUREMENT DISCIPLINE

PURPOSE
Freeze the minimum lesion-validity rule and the next matched multi-seed regeneration comparison after exploratory implementation validation and before confirmatory interpretation.

PROVENANCE
This amendment is intentionally informed by the single-seed exploratory probe recorded in dg1a-p0-exploratory-probe-01.ice.

The exploratory result showed that a persistence-trained phenotype can appear to recover strongly when the lesion causes almost no measurable loss. Therefore lesion validity must be determined before recovery quality is interpreted.

NO POST-HOC RULE
The thresholds below are frozen before the next multi-seed comparison and must not be changed after inspecting those runs. If the thresholds prove unsuitable, the run family remains evidence under these thresholds and any replacement threshold requires a new amendment and new runs.

NEW LESION VALIDITY METRICS
For a lower-is-better morphology error:

DamageEffect = post_damage_error - pre_error

RelativeDamageEffect = DamageEffect / max(pre_error, 1e-12)

ActiveCellRemovalFraction = max(0, pre_damage_active_cells - post_damage_active_cells) / max(pre_damage_active_cells, 1)

VALID LESION
A lesion is valid for regeneration interpretation only when all conditions hold:

1. DamageEffect > 0.
2. RelativeDamageEffect >= 0.10.
3. ActiveCellRemovalFraction >= 0.10.
4. Pre-damage, post-damage, and recovery states remain finite.

RATIONALE
The relative error criterion prevents negligible perturbations from being labeled regeneration events merely because later development improves ordinary task error.

The active-cell criterion verifies that the intervention removed a non-trivial portion of the developed phenotype rather than only changing a numerically sensitive but structurally negligible region.

The thresholds are deliberately modest. They validate that genuine loss occurred; they are not themselves success thresholds for recovery.

MULTI-SEED FAMILY
Matched seeds:
0, 1, 2, 3, 4

Variants:
- growth_only
- regeneration with the adopted maturity-gated damage curriculum

Persistence remains relevant to H-P0-2 but is not part of the primary H-P0-3 paired recovery comparison in this amendment.

MATCHING RULE
For each seed pair, hold constant:
- model dimensions;
- grid dimensions;
- target identity;
- optimizer family and learning rate;
- training iterations;
- development horizon distribution;
- evaluation growth horizon;
- lesion geometry;
- recovery horizon;
- resource ceilings.

Only the curriculum differs between growth_only and regeneration.

PRIMARY CONFIRMATORY METRIC
Paired bounded RecoveryFraction difference:

DeltaRecovery(seed) = RecoveryFraction_regeneration(seed) - RecoveryFraction_growth_only(seed)

Only pairs in which both variants receive a valid lesion may contribute to the primary paired recovery comparison.

SECONDARY METRICS
- stable T50 attainment;
- stable T90 attainment;
- normalized recovery AUC;
- final recovery error;
- active-cell trajectory;
- catastrophic expansion to grid capacity;
- numerical instability/non-finite events;
- training and repair wall-clock;
- state/genome resource accounting.

MINIMUM DATA ADEQUACY
Do not interpret H-P0-3 confirmatorily unless at least 4 of the 5 seed pairs have valid lesions in both compared variants.

H-P0-3 SUPPORT RULE FOR THIS GATE
If minimum data adequacy is met, H-P0-3 is supported at this P0 morphology stage only when:

1. at least 4 of 5 valid matched seed pairs have DeltaRecovery > 0; and
2. the median DeltaRecovery across valid pairs is at least 0.25; and
3. regeneration has no greater non-finite failure count than growth_only; and
4. regeneration does not achieve the apparent advantage solely through an invalid lesion or saved-state restoration.

Stable T90 is reported as an important secondary indicator but is not required in every seed because the fixed recovery window may censor slower valid repair.

FAILURE / INCONCLUSIVE RULES
- fewer than 4 valid matched pairs: INCONCLUSIVE, not disproven;
- median DeltaRecovery < 0.25 or fewer than 4/5 pairs favor regeneration: H-P0-3 NOT SUPPORTED under this configuration family;
- non-finite regeneration failures in otherwise matched runs: record as negative evidence and investigate root cause without weakening tests or exclusions;
- apparent recovery after invalid lesion: exclude from regeneration inference but retain the full run evidence.

CLAIM BOUNDARY
Even if H-P0-3 is supported here, the allowed claim is limited to the declared P0 morphology task and configuration family.

It does not establish cognitive regeneration, task-general repair, continual learning, ancestor inheritance, or consumer-hardware scaling advantage.

FIBONACCI RELATION
DG-1A-FIB1 remains blocked during this confirmatory gate. Fibonacci scheduling must not alter these P0 runs because P0 is the canonical reference against which later repair-scheduling ablations will be compared.

NEXT ACTION
Add the lesion-validity telemetry to P0 evidence, run the matched five-seed family from commit-bound source, and interpret only under this frozen amendment.