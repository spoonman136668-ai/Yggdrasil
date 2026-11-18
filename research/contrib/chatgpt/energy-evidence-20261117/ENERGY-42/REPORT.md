# ENERGY-42 — Corrected contrastive learning of transferable graph-reliability structure

**Date:** 2026-11-18. **FROZEN PRIMARY: DEVELOPMENT_NO_GO (four of eight gates PASS).** No native Yggdrasil training, scientific first-use, promotion, merge or deployment.

## Why this is a new experiment
The frozen ENERGY-41 implementation had inverted the learned contrastive energy difference, making its 48-world result **INVALID**. The source at ENERGY-41 and negative evidence were preserved at commit `ed1d67984413e438a941efed3a6029b8f02d07c5`. ENERGY-42 fixes the mathematical sign, adds first-principles signed-derivative checks for every demonstration graph, changes the deterministic source version and selects **three fresh, disjoint seeds**. All other model hyperparameters, supervised training budget, controls, cold test worlds and eight gates remain unchanged.

**Pinned preprimary custody:** corrected source+independent auditor `babdcc3b8a0b8c2471a0ab16926045fb80782957`; preregistered fresh seeds, all eight gates and negative-stop rule `efe557e5383b96ccee247c3ddcc9f8f7c55c3cf1`. Exactly one primary scoring on seeds **8501, 8521, 8537** after prereg. Excluded smoke seed 99773 passed 23,762 audit checks before this freeze.

## Hypothesis and causal-content limitation
Each seed has **16 supervised training graphs (n=20)** on erdos and modular topologies. Training includes the true complete binary node assignments and three classes of observed noisy XOR constraints (ring links, short links and long links), giving all learners **exactly the same observed training information**. The structured-energy candidate learns three reusable positive weights by minimizing a 96-epoch supervised structured margin loss on differences in violated factors when a single node is counterfactually flipped.

Held evaluation includes **four disjoint familiar graphs per seed** (12 total, 480 held node-pair relations) and **twelve cold novel graphs per seed** (36 total, 1,440 held node-pair relations), with never-trained sizes 36 and 52 and never-trained lattice topology. Each method gets identical test graph constraints without test truth, uses the same 8-start, 24-sweep deterministic local-search inference, and must predict XOR relations on 40 held node pairs **not in the graph**. Thus the measured signal is gauge-invariant, out-of-graph relational reconstruction. **The structural group features are supplied by design, not autonomously discovered**, and training demos expose source truth. This is not native Yggdrasil general intelligence or lifelong learning.

Strong information-matched controls: Laplace-smoothed Bayesian group reliability, regularized group logistic regression, fixed uniform weights and label-group-shuffled structured learning. The privileged oracle, given the true synthetic noise probabilities, is diagnostic only and excluded from strongest-control criteria.

## Complete aggregate outcome

| Fitted factors / 8-start solver | Novel correct / 1440 | Old correct / 480 | Unseen lattice correct / 480 | n52 correct / 720 |
|---|---:|---:|---:|---:|
| **Corrected structured energy** | **1006 (69.86%)** | **377** | 390 | 493 |
| Matched Bayesian reliability | 995 (69.10%) | 377 | **397** | **494** |
| Matched logistic regression | 995 (69.10%) | 377 | **397** | **494** |
| Uniform weights | 887 (61.60%) | 290 | 368 | 399 |
| Group-shuffled structured energy | 910 (63.19%) | 322 | 388 | 442 |
| Privileged true-noise oracle (not matched) | 994 (69.03%) | 367 | 409 | 491 |

Energy gained **11/1440 = 0.76 percentage points** over the strongest learned conventional baseline, which fails the required +2pp gate. It gained +119/1440 **(+8.26pp)** over fixed uniform and +96/1440 **(+6.67pp)** over sham group-shuffled training, suggesting the corrected system learned some useful recurring constraint reliability. It preserved the old-domain score (377/480) on par with Bayes/logistic, passing retention.

However, the unseen lattice topology lost **7/480** to Bayes/logistic, and 52-node graphs lost **1/720**. Seed-wise energy margins versus strongest matched alternatives were **+1, −12, +22** novel relations, clearing the weak two-positive-seeds gate without proving stable superiority. Energy's weights for group0,1,2 consistently reflect cleaner ring constraints over noisy long-range constraints, but they do not improve sufficiently over simple group-frequency learning.

## Whole-policy compute / efficiency
The measured cumulative `training graph generation + model fitting + all held graph generation + held inference` wall time was **0.46620 s** for energy and **0.44132 s** for Bayes across all three seeds. Correct novel relations per measured policy second: **≈2158** for energy versus **≈2255** Bayes, or **0.957×** Bayes; the frozen requirement was ≥1.2×. This is **local single-run Python component timing**, not physical Joules or full workstation/CI runtime. No energy inference or whole-process efficiency advantage is demonstrated.

## All eight frozen gates

| Gate | Frozen result |
|---|---|
| Novel ≥2pp over strongest matched learner | **FAIL**, +0.76pp |
| Novel ≥3pp over uniform | **PASS**, +8.26pp |
| Old knowledge regression ≤1pp vs best matched | **PASS**, tied 377/480 |
| Novel ≥5pp over group-shuffled negative | **PASS**, +6.67pp |
| Unseen lattice ≥1pp over Bayes | **FAIL**, −1.46pp |
| n52 ≥1pp over Bayes | **FAIL**, −0.14pp |
| Positive gain versus strongest matched learner on 2/3 seeds | **PASS**, +1, −12, +22 |
| Novel relations per wall second ≥1.2× Bayes | **FAIL**, 0.957× |

**Valid synthetic result: DEVELOPMENT_NO_GO.** No post-primary tuning of learning rate, margin, source label groupings, solver restarts or stop thresholds. Keep all null/negative results.

## Engineering and independent science receipts
- Original local full primary `scored.json`, **1,076,735 bytes**, SHA-256 `b06d8a885f69f75c7ee938df97949df406e51673f022953024f5a827bf5a38b2`, held in isolated local research workspace **not** deposited in repo.
- The **entire 48-world per-arm exact correct-score record** is in `case_scores.csv.bz2` (1,958 bytes), with world IDs, graph/truth/probe SHA-256 prefixes and all six correctness counts; uncompressed SHA-256 `493abe98fdb9ffc14de6f4a291e9b453e89d7bd521c8e1d4aabd8a3cad31b575`, compressed SHA-256 `57f02c63eab7d409f59ec7d4d6ea5734e7f6a6775abb0ebed7fa8eff0ab2e0c9`. Exact source and committed seeds can regenerate the more detailed full primary case data.
- **Independent audit PASS: 71,609 checks**, recreating all 48 training + 48 evaluation worlds, all six models' weight refits and final bit assignments, the 40 never-witnessed relation probes per evaluation world, and **2,880 first-principles signed `V(flip)−V(true)` invariants**. It does not import the original scorer but reuses third-party NumPy/sklearn estimator internals. This is an isolated engineering qualification, **not** cross-platform native acceptance.
- Unchanged frozen original source rerun produced byte-identical canonical non-timing JSON (175,441 bytes), SHA-256 `48d46a9d52739bf373ce31018a44aba67c5a857d8003025029f9db6251d7e25f`. Timing fields are excluded from this replay because wall clocks differ.
- Local Linux CPU Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0, single-threaded BLAS. No protected original Yggdrasil model weights, GPU, paid API, autonomous owner, or native runner were used.

## Reproduction
Checkout the exact evidence SHA. Decompress and SHA-verify `experiment.py.bz2` and `audit.py.bz2` as instructed in README.md, then run:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out replay.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py replay.json --out independent_audit.json
python -B verify_archive.py
```

## Decision
The **corrected** model shows limited transfer and accurate weighting of noisy structural constraints, but no verified superiority over a simple supervised reliability estimator, no stable novel-topology advantage, and no end-to-end efficiency benefit. Stop tuning this candidate on consumed seeds. A distinct future mechanism would need to **learn new factor primitives** (instead of training on supplied edge groups), show retained cold causal relationships, and compare against a fully trained matched conventional baseline. No merges or original model/training-loop integration justified.

**ENGINEERING: local independent audit/replay PASS; mandatory native CI/full regression UNVERIFIED. SCIENCE: DEVELOPMENT_NO_GO. DEPLOYMENT: NONE.**
