# ENERGY-47 — Protected ElasticNet head with contradiction-repair routing

**2026-11-18 — DEVELOPMENT_SCREEN_NO_GO (pre-primary).** Not a preregistered scientific primary and **not** native Yggdrasil training.

## Hypothesis and method

ENERGY-46 failed to beat the strongest conventional ElasticNet baseline and lost old-context accuracy. The next smallest coherent experiment protected an old-context ElasticNet head (fitted once on 96 old randomized intervention consequences) and used a disjoint **outer 76/20 split of the 96 new training outcomes** to choose a new-context specialist: joint ElasticNet, new-only ElasticNet, conventional new-only OMP4, or contradiction-gated structural support replacement. The repair candidate made its own independent **56/20 inner selection** within the first 76, avoiding reuse of the 20 outer selection labels. Once a model was chosen, its parameters were refitted on all allowed new training examples. The old ElasticNet head stayed frozen.

A **matched two-model ElasticNet-only router** used the same 76/20 outer decision, old protected head and exactly the same witness outcomes. Further controls were joint ElasticNet (all 192 observations), new-only ElasticNet, conventional OMP4, OMP structural memory7, all-new gated replacement, no repair, shuffled new labels, full OMP7 and a 60-tree random forest. All methods share exactly 96 old and 96 new training labels per world; disjoint old/new/cold held consequences were evaluator-only. Each world has 12 binary intervention variables, three shared hidden causal factors, old-only/new-only factors and an author-specified **364-feature parity/AND grammar**. No open-world mechanism invention, genuine autonomous intervention, model checkpoint or persistent Yggdrasil research-state change was tested.

## Two independent excluded screening cohorts

| Metric | Seed 99891 (6 worlds) | Seed 99897 (6 worlds) |
|---|---:|---:|
| Candidate protected-head router cold MSE | 0.0974 | **0.3958** |
| Joint ElasticNet cold MSE | 0.1358 | **0.1393** |
| Matched ElasticNet-only router cold MSE | 0.1464 | 0.1401 |
| Standalone gated replacement cold MSE | 0.0974 | 0.0863 |
| Development screen checks passed | **5/10** | **3/10** |
| Independent, full 11-arm refit audit checks passed | **25,469** | **25,469** |

**Important:** The routed-model result is not a reliable energy-specific gain. It chose `gate` in **2 of 12 worlds**, conventional OMP in nine, and joint ElasticNet in one; it chose standalone new-only ElasticNet in none. In the second cohort, ordinary OMP routing misgeneralized on cold cases while the standalone gated model would have performed substantially better. The outer 20-sample training validation was not a reliable selector of unfamiliar cold-environment generalization.

The old-context prediction checkpoint was unchanged by new-world fitting, but the frozen old-only ElasticNet was not consistently competitive with the conventional, fully trained cumulative ElasticNet. This distinction is crucial: **zero parameter drift does not mean good retained knowledge**.

## Scientific controls and decision

The two independent smoke/cohort runs and all **50,938** independent model-refit and per-held-case checks passed. The independent auditor reconstructs worlds from an independently written source generator, fits all 11 methods and checks all held predictions, route decisions, frozen old checkpoint hashes and ten decision rules. The auditor does not import ENERGY-47 `experiment.py`; it does share NumPy and sklearn backend libraries. Source/evidence original and compressed SHA-256 custody is in `result.json`. Timings are single-threaded local Python CPU fit+predict, not controlled full-system compute.

**STOP WITHOUT RUNNING PRIMARY.** The reserved primary seeds **9001, 9011, 9023** were not scored. These screens are preliminary DEV evidence only. They are **not** SCIENTIFIC_PASS, nor a full prospectively preregistered-development qualification. No post-hoc hyperparameters or extra primary attempts are justified by the failed independent screen. Retain the strong joint ElasticNet and standalone gated-repair controls. A future *different* hypothesis should test causal intervention selection or actual learned causal factor validity rather than spend more data on a validation-only model router.

## Reproduce

Extract `source.tar.bz2` and the archived ENERGY-46 `experiment.py` + `audit.py` alongside the ENERGY-47 folder (see pinned original SHA256 in `result.json`). Set `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1` with Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0. Run `experiment.py --smoke --out smoke_replay.json`. To replicate excluded second screen, use `experiment.run((99897,),(0,3),'smoke2')` without touching primary seeds. Run independently authored `audit.py smoke_replay.json --out replay_audit.json`. `verify_archive.py` checks exact original score and audit receipts. Neither experiment is intended for accepted native Yggdrasil qualification.

**ENGINEERING:** local source, independent 11-arm refit and archive custody PASS; GitHub code-atlas CI remains separately unverified until exact candidate checked. **SCIENTIFIC:** development screening NO-GO. **DEPLOYMENT:** none. PR #1210 remains draft; `main`, owner, controller, scheduler and Yggdrasil state untouched.
