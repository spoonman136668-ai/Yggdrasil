TITLE: DG-1A-P0 Confirmatory Criteria Amendment
DATE: 2026-09-17
STATUS: PREREGISTERED FOR FUTURE CONFIRMATORY RUNS
TRACK: DG-1A
CONFIDENCE: SUPPORTED AS A MEASUREMENT CONTRACT

PURPOSE
Freeze numeric interpretation rules after exploratory mechanism development and before any multi-seed confirmatory evaluation. These criteria apply prospectively. They must not be used to retroactively relabel earlier exploratory observations as confirmatory evidence.

SCOPE
Initial confirmatory family:
- fixed 20 x 20 grid;
- 16 state channels;
- 32 hidden channels;
- deterministic disk target radius 4;
- training horizon 200 iterations;
- development horizon 8..12 steps per training update;
- evaluation growth horizon 12 steps;
- persistence evaluation horizon 16 additional steps;
- recovery evaluation horizon 16 steps;
- center lesion 50% x 50% of active bounding box;
- regeneration maturity gate: at least 16 active cells;
- float32;
- matched seeds across V0/V1/V2.

VARIANTS
V0 = growth_only
V1 = persistence
V2 = regeneration with maturity-gated damage

SEED FAMILY
Use five paired training seeds: 0, 1, 2, 3, 4.
Do not drop unstable or unfavorable seeds.

MEANINGFUL DAMAGE CRITERION
For a recovery observation to count as a regeneration trial, immediate lesion damage must satisfy:

DamageEffect = post_damage_error - pre_error

DamageEffect >= max(0.005, 0.10 * pre_error)

Rationale:
A lesion that barely changes task error tests robustness, not regeneration. This threshold was selected after exploratory work and is therefore valid only for future runs.

PERSISTENCE METRIC
Primary persistence degradation per seed:

PersistenceMaxDegradation = max(error_curve) - initial_error

This uses the worst degradation over the declared persistence window rather than only the final point, preventing transient instability from being hidden by later recovery.

H-P0-2 CONFIRMATORY SUPPORT RULE
H-P0-2 is supported for this configuration family only if all are true:
1. V0 median PersistenceMaxDegradation across the five seeds is at least 0.01, so the comparison is informative.
2. V1 median PersistenceMaxDegradation is <= 50% of the V0 median.
3. V1 has lower PersistenceMaxDegradation than paired V0 in at least 4 of 5 seeds.
4. V1 produces no non-finite state in any seed.

If V0 is already stable below the informative floor, H-P0-2 remains UNKNOWN for this family rather than being declared failed.

REGENERATION PRIMARY METRICS
Per seed:
- MeaningfulDamage: whether the damage criterion is met;
- bounded final RecoveryFraction in [0,1];
- normalized recovery AUC;
- stable T50;
- stable T90;
- final error;
- active-cell count and resource snapshot.

Stable threshold means the recovery threshold is reached and remains satisfied through the end of the declared recovery window.

H-P0-3 CONFIRMATORY SUPPORT RULE
H-P0-3 is supported for this configuration family only if all are true:
1. V2 meets MeaningfulDamage in at least 4 of 5 seeds.
2. Among V2 seeds meeting MeaningfulDamage, stable T50 is attained in at least 4 seeds.
3. V2 median bounded final RecoveryFraction across meaningful-damage seeds is >= 0.50.
4. V2 median normalized recovery AUC across meaningful-damage seeds exceeds the paired V0 median by at least 0.25.
5. V2 has better bounded final RecoveryFraction than paired V0 in at least 4 of 5 seeds where both produce MeaningfulDamage.
6. V2 produces no non-finite state in any seed.

T90 is reported but is not required for minimum H-P0-3 support. Requiring T90 at this stage would conflate strong recovery with the minimum question of whether damage-trained development materially improves repair.

FAILURE / INCONCLUSIVE RULES
- If fewer than 4 V2 seeds satisfy MeaningfulDamage, H-P0-3 is UNKNOWN for this lesion/configuration; change lesion severity only in a new exploratory packet.
- If implementation defects are found, fix root cause and invalidate affected runs. Do not weaken tests or thresholds.
- If V2 fails the support rules under a validated implementation, record the negative result. Do not silently retune the criteria.
- A result on the 20 x 20 probe family does not automatically generalize to the full 40 x 40 P0 family.

REPRODUCIBILITY REQUIREMENT
Confirmatory evidence must record:
- real repository source revision;
- config identity/hash;
- seed;
- device and precision;
- target identity;
- full per-seed metrics;
- all failed/unstable seeds.

Evidence from reconstructed source trees that report source_revision = UNKNOWN remains exploratory regardless of numerical outcome.

DECISION
The above criteria are frozen for the next confirmatory 20 x 20 P0 seed family. Any later change requires a new dated .ice amendment and cannot relabel prior runs.

NEXT EXPERIMENT
Execute the five paired seeds from a real repository checkout. Sandbox multi-seed runs may be used only as additional exploratory risk reduction and must retain that label.
