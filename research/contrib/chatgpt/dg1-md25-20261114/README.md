# DG1-MD25 — learned intervention-site versus strong blind control

## Provenance and frozen boundaries

- Repository: `spoonman136668-ai/Yggdrasil`, isolated stacked external-research branch, MD24 base `ea9ceca774a50bb3126bdf066120cb32ea4ddec5`. Preregistration-only SHA `f8b4d11855918a987144885f4885f0598d271136` predates all MD25 implementation and toy outcomes; registered cohorts in `prereg.json` have **not been used**.
- Fixed code: bounded non-transformer/non-token action-effect counts; scripted public-view map/navigation scaffold; pinned MiniGrid 3.2.0 / Gymnasium 1.4.0 / NumPy 2.3.4; no mission string or hidden environmental state for policies.
- Source files `md25.py` and `test_md25.py` are scoped to disjoint, preapproved toy seeds 41, 43, 47, 53, 59, 61; there is **no registered first-use entry point**, official-primary PR-opened workflow or scheduled runner.

## Measured new development result (physical MiniGrid toy cohort)

The inherited MD24 toy failed all 36 blocked-family episodes, even though the candidate and blind generic policy each removed six obstacles. MD25 separates the common navigator repair from the learned site-selection ablation. It fixes the non-goal branch after an unlocked door (novel policy name had overridden the MD23 event-graph case) and stops seeking a second unknown object after a physically confirmed removal. These are **shared scripted code changes** applied equally to `causal_site`, `blind_site`, and `permuted_site`. They are NOT counted as learned adaptation.

The same earlier-family public-view teacher generated 6/6 rewarded DoorKey and 6/6 rewarded UnlockPickup toy demonstrations (265 actual charged physical training actions); event memory observed 18 actual pickup-clears and 6 actual drop-places. On six separately reset BlockedUnlockPickup toy cases:

| policy | novel goals | physical actions | obstacle removals |
|---|---:|---:|---:|
| learned causal-site effect | 6/6 | 202 | 6 |
| blind generic site (strong nonlearning control) | 6/6 | 202 | 6 |
| permuted effect | 0/6 | 1,536 | 0 |
| prior MD23 causal | 0/6 | 1,536 | 0 |
| trained tabular-Q | 0/6 | 1,536 | 0 |
| trained recurrent imitation | 0/6 | 1,536 | 0 |

The **six paired complete physical action/reward SHA-256 hashes are all identical** between the learned candidate and blind generic control. Some internal proposed-site counters differ, but that is **not** evidence of different charged actions; action/reward traces control the scientific judgment. Thus the improvement belongs to the shared navigation repair, not a demonstrated learning-specific site decision. The original frozen toy gate requires >=2 distinct paired action hashes; it is **not met**, notwithstanding candidate 6/6 task coverage. Classification: `TOY_COVERAGE_NO_GO` under the pre-registered full gate. Do not convert this into a positive scientific first use.

## Decision

Engineering qualification and scientific advancement are separate. Preserve the toy falsification with byte-level receipts in GitHub CI, run full final inherited 54-test regression and exact G29 atlas on both platforms, and retain the MD23 + MD24 predecessor history. No original MD25 registered seeds, official novel-family evaluation, scientific acceptance, native substrate change, merge, promotion, Forge owner/control loop change, or deployment has occurred or is authorized by this result.

A new independently frozen hypothesis must test learning-specific intervention value under **matched true action/geometry controls**, ideally using intervention uncertainty to change the physical action *before* an episode is solved by a scripted scaffold. Keep the fixed pathfinding repair as an explicit baseline and require positive transfer beyond its strong nonlearning performance.
