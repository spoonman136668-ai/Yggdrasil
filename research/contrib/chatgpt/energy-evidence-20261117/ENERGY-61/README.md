# ENERGY-61 — Compositional causal operator induction

**Scope:** independent, external, synthetic causal-learning research evidence; not Yggdrasil native weights, scientific first-use, production or loop control. The experiment follows ENERGY-60's negative learned-latent-state filter and ENERGY-55/57/58/59's limits on memory and higher-level representation.

## Question

Can a persistent causal-program search reconstruct unseen nonlinear relationships from consequences of `do` interventions, without being given a named 4/5-way operator or planted support, and improve cold-transfer predictions over **fully trained conventional learners with the same observations and same expressive feature bank**?

The candidate learns a four-term Boolean AST predictor from generic **AND/XOR over pairs of observed action bits, then AND/XOR of nonoverlapping pair expressions**. There are 12,012 static candidate expressions; the high-level planted operators (XOR-of-AND, AND-of-XOR and 5-way conditional gates) are not passed as labels or named templates. Nevertheless the generic primitive operations, maximum depth, total feature bank, search heuristic and four-term capacity are **supplied by the researcher**, not learned from scratch; 5-way conditional gates exceed the depth-two expression bank. The independent synthetic generator plants one shared mechanism plus a changed stage-specific mechanism. Two nuisance variables change correlation across OLD and NEW and are independent during COLD testing.

Each generated world uses exactly **352 unique underlying 10-bit randomized intervention assignments**: 80 OLD training, 80 NEW training, and 64 held OLD/NEW/COLD. Source-only hidden factor identities and all held outcomes are excluded from learner training. All models have identical 160 factual labels; some controls deliberately ignore OLD labels. All methods have equal input information, but not equal parameter counts or fitting cost.

**Candidate:** preserve the OLD fitted program unchanged for historical readout; carry two OLD-selected generic factors into NEW, reweight them and greedily induce two new generic factors from NEW consequences. All model fitting uses only witnessed outcomes, never held labels. Compare against (i) freshly fitted four-term matching-bank OMP, (ii) pooled-bank OMP, (iii) **fully fitted matching-bank ElasticNet** (strongest direct expressive control), (iv) fourth-degree full-input polynomial ElasticNet, (v) 96-tree ExtraTrees, (vi) HistGradientBoosting, (vii) RBF KernelRidge, (viii) ordinary training-loss-softmax weighting of OLD and NEW program snapshots, (ix) frozen old/no-update, and (x) shuffled-new-label negative. There are 11 arms total.

**Provenance:** `source_manifest.json` contains exact immutable experiment/auditor/archive SHA-256 and Git blobs. `source.tar.bz2` is reproducible, deterministic (`mtime=0`) and contains both independently authored code files. Auditor implements a separate generator, Boolean expression evaluation, greedy refits and all conventional model refits without importing experiment.py; it still shares third-party NumPy/scikit-learn solvers. Independent audit is not an independent scientific replication.

Excluded developer smoke `999001`, three worlds, was evaluated BEFORE source/prereg freeze and did not support candidate superiority; the source was updated before freeze to add the full-bank ElasticNet control and immutable old readout, both disclosed here. It is not used as confirmation. **Frozen prospective screening seeds 103301 and 103319, world IDs 0–1 and all three families, remain unscored at source freeze.** Reserved primary seeds 103401/103419/103433 may be used only if the separately frozen screening gates qualify. Do not retune consumed screens.

CPU-only reproduction, Python 3.13, NumPy 2.3.5, SciPy 1.17.0, sklearn 1.8.0:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
tar -xjf source.tar.bz2
python -B experiment.py --seeds 103301 103319 --world-ids 0 1 --out screen.json
python -B audit.py screen.json --out screen_audit.json
```

The precise scientific decision gates are in separately committed `prereg.json` and must precede scoring. Whole-process energy usage and native Yggdrasil capabilities are **not** measured.
