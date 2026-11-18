# ENERGY-04 — unknown parent-structure energy inference | local exploratory development

Date: 2026-11-17. Project affinity: Yggdrasil; source-free and outside native Yggdrasil.

## Custody

- Preregistration frozen before scored run: `prereg.json`, SHA-256 `5b3c195f31959c5a900a3a6dc5579793f4fd34f5694dd71f7237fd9414098d92`.
- Test implementation frozen before scored run: `experiment.py`, SHA-256 `de663729fd66898494897b99f120daccefb575516d258444b9879f34baa3b4e6`.
- Cohort: 12 independent generated worlds, seeds 17/29/43, 4 worlds/seed; 80 training + 16 validation + 32 heldout intervention questions/world.
- Separate unscored smoke: seed 999, excluded from primary evaluation.
- Independent post-result audit `audit.py` (no changes to scored implementation); 1,152 objective and outcome recomputation checks PASS, plus 12 cold serialized-factor restores and 12 fully distinct train/validation/test intervention partitions.

## Results (heldout 384)

| Method | Correct entire 3-bit state | Fit+inference on this CPU |
|---|---:|---:|
| Learned energy with four deterministic descent starts | 371/384 = 96.61% | 54.96 ms |
| Independent maximum-likelihood symbolic parity structure fit, followed by direct forward calculation | 384/384 = 100% | 18.50 ms |
| Trainable 4-update recurrent tanh network, Adam/early stopping | 195/384 = 50.78% | 2969.67 ms |
| Shuffled-training negative control | 101/384 = 26.30% | Inference only (negative fit not timed) |
| Exact exhaustive minimizer **of the energy learner's own fitted objective** | 371/384 = 96.61% | 19.57 ms including energy fitting |

- Energy found its own objective minimum on 384/384 cases. All 13 true-state errors came from corrupted downstream observation; direct forward prediction from the fitted energy structural rules was correct on 384/384.
- Syntactically exact true parent-mask+bias matched in 25/36 endogenous equations in both the learned energy and symbolic methods, while functional predictions generalized perfectly under direct forward evaluation. Parent-mask nonidentifiability remains because only exogenous variables were intervened upon. Do not claim learned unique direct causal graph.
- Every recurrent baseline stopped at the frozen 250-epoch minimum due to validation early stopping, with median validation BCE ~0.489. This control is trained but **not** a qualified strong recurrent comparator; its lower accuracy cannot support general speed/accuracy superiority.
- Reported whole-process time is the sum of per-world fit+test inference in local Python CPU, not wall clock of the entire experiment, memory use, FLOPs, GPU costs, scientific acceptance or CRAM/HRM/TRM timing. Models share examples but not equal compute, optimization convergence or capacity.

## Interpretation

**DEVELOPMENT NO-GO.** The frozen >=99% accuracy, matched accuracy against exact, >=2x whole-process advantage versus both comparators, and structural recovery criteria were not met. Exact symbolic fitting plus deterministic forward propagation is 3.0x faster and more accurate. The 13 misses are evidence-weight calibration/robustness failures, not local-minimum misses. This synthetic task permits direct forward solution without genuine latent causal inference. Freeze negative outcome.

## Future diagnostic — proposed only

ENERGY-05 should hide one exogenous state at query, supply imperfect but informative observations of endogenous variables, allow randomized interventions on endogenous nodes during *training* so direct and indirect parent structure is identifiable, fit evidence reliabilities from training/validation only, and compare to a fully qualified recurrent model plus exact symbolic marginal inference under matched information/action and compute budgets. Prespecify an exact oracle with abstention on nonidentifiable cases, novel latent intervention combinations, 99% exact solution accuracy and >=2x full-process advantage, and cold retention. This is a proposed future experiment, not an executed result.

## Repository / native status

- `spoonman136668-ai/Yggdrasil main` checked at `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Draft PR1201 ENERGY-01 checked at `69123bc92cad8bc14fe6596f42d9b2f4e71a2542`; no updates made.
- No GitHub mutation, scientific first-use, reserved data consumption, Yggdrasil native integration, FORGE integration, scheduler, controller, model deployment, or CI full regression.