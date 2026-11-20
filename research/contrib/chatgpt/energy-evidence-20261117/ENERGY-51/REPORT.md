# ENERGY-51 — Higher-order causal relationship learning and cold retention

**Date:** November 18, 2026. **Classification: DEVELOPMENT_NO_GO**, with **4 of 9 preregistered gates PASS**. This is external, contributor-run synthetic evidence, **NOT native Yggdrasil model training, SCIENTIFIC_PASS, or deployment**.

## Custody and prespecification

This is an explicitly new, disjoint hypothesis following ENERGY-49's provisional acquisition win and ENERGY-50's out-of-grammar screening no-go. The frozen scorer and auditor were committed at **`9be7cfcbcdcc740abffa272220b2ba16a83cf371`**, then all nine thresholds and primary seeds were committed in `prereg.json` at **`b2b9743778f8cbd0bddf2ba03bfe1c8469bb631e`** **before** scoring primary seeds **9311, 9323, 9341**. An excluded implementation smoke on seed **99971** passed **38,811 audit checks** (three worlds). No primary-seed tuning was performed.

## Hypothesis and experiment

An explicitly sequential sparse structural-energy learner discovered up to six parity-factor supports from **72 old-context do-interventions**, froze those old predictions, then learned up to five corrective factors from **72 new-context witnessed consequences**. All 36 fresh worlds used five hidden signed mechanisms spanning parity-of-four/five, five-way majority, modulo-three and conditional gates, with three shared factors plus old/new stage-specific factors. Two nuisance cues switched correlations between contexts and were independently randomized on cold held-out interventions. Within every world, **360 underlying causal action assignments were unique**, with 72 each for train-old, train-new, held-old, held-new and held-cold.

The candidate could search a **provided finite 1–5-way Walsh/parity grammar** of 1,585 possible features on all twelve observed action bits. Thus, the planted factor supports were previously unknown to the learner, but **the operator basis was supplied**, not invented. Conventional OMP6 and ElasticNet received the exact same 1,585-feature grammar and 144 witnessed training labels; separate fully trained RBF and fifth-degree polynomial kernel-ridge models and 64-tree ExtraTrees received the same raw labeled interventions. Negatives were no new adaptation and shuffled new-stage labels. No held consequences, planted mechanism identities or weights were exposed to a fitting method.

## Frozen primary measurements

| Method | Old held MSE ↓ | New held MSE ↓ | Cold held MSE ↓ | Fit + held prediction seconds |
|---|---:|---:|---:|---:|
| **Structural-energy candidate** | 1.5953 | 2.1590 | 3.2548 | 0.0560 |
| **ElasticNet (strongest cold conventional)** | **1.3929** | **1.5727** | **2.4572** | 0.5076 |
| Fully trained OMP6 | 1.7751 | 1.9640 | 2.9777 | 0.0800 |
| RBF kernel ridge | 4.0977 | 3.8904 | 4.1037 | 0.0770 |
| Fifth-degree polynomial kernel ridge | 5.5003 | 5.1549 | 5.5780 | 0.0494 |
| ExtraTrees (64 trees) | 5.8535 | 5.4448 | 5.8434 | 2.1451 |
| **Frozen old / no adaptation** | 1.5953 | 3.5012 | 2.2244 | 0.0445 |
| Shuffled-new negative | 1.5953 | 6.4708 | 5.9399 | 0.0452 |

The candidate recovered **92.708%** of the exact planted four/five-way **parity** supports, but cold MSE was **32.5% worse than ElasticNet** and **46.3% worse than simply retaining the old model without new updates**. Recovering correct support identities did not ensure sufficiently accurate weights or cross-context generalization. Per-seed candidate-versus-strongest-conventional cold MSE margins were **+0.7824, +0.6671, +0.9434** (positive means candidate worse), so none of the three seed cohorts was a candidate win.

Per-family candidate MSE was **2.1949** (parity45), **3.1980** (threshold) and **4.3714** (conditional/modulo); ElasticNet was **1.8835**, **2.5377** and **2.9503** respectively. Conditional/modulo generalization was the largest gap.

## All nine preregistered gates

| Gate | Result |
|---|---|
| At least 10% better cold MSE than strongest fully trained conventional | **FAIL** |
| At least 60% exact planted order-4/5 parity support recovery | PASS (92.7%) |
| Preserve frozen old-context predictions exactly | PASS |
| Held-new MSE no worse than 5% above strongest fully trained conventional | **FAIL** |
| Cold MSE at least 20% better than shuffled-new-label negative | PASS |
| Win vs strongest conventional per seed in at least 2/3 seeds | **FAIL** (0/3) |
| Fitting and inference local cost at most 2x conventional OMP6 | PASS |
| Cold MSE at most 20% above held-new MSE | **FAIL** |
| No causal family worse by more than 10% versus its strongest conventional | **FAIL** (0/3 families) |

**Final class: DEVELOPMENT_NO_GO (4 PASS, 5 FAIL).** No primary gate or hyperparameter was changed based on observed outcomes. The frozen old retention check is mechanically met by design and does not establish *competitive* old-context accuracy.

## Engineering, reproducibility, limitations

Independent scorer/fit audit: **PASS, 465,468 checks**, source generator and hidden outcome reconstruction, 360 unique intervention states per world, Walsh factor values, independently refitted eight methods and every held prediction. This independent implementation still reuses the underlying generator and scikit-learn estimator libraries, so it is not a separate data-source qualification. Unchanged-source replay produced **identical non-timing canonical result bytes**, SHA-256 `093290b0f10b75aee7bd359d5e1ab35f61a1d65cc6d22af9b9673733a03b14af`. Primary was executed locally on Linux Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0, SciPy 1.17.0 with BLAS threads capped at one, CPU only, zero paid API calls. Local policy time excludes full process and evidence-review costs. **No native multi-platform regression, official scientific acceptance, learning/transfer benchmark or model deployment was executed.**

Complete original 2,512,977-byte result is archived as `scored.json.bz2`, including all 36 x eight models x three contexts predictions, supports, labels provenance and timings (SHA-256 raw `acac0a6e9813b7d01436314593edec949673059165a6683b61c6e2698b3af741`). The smaller `world_scores.json.bz2` contains the 36 case-level error and selected-factor receipts. `audit_result.json`, `result.json`, `provenance.json` and `verify_archive.py` are deposited alongside preregistered frozen code. To reproduce:

```bash
python verify_archive.py
python -c "import bz2; from pathlib import Path; [Path(n).write_bytes(bz2.decompress(Path(n+'.bz2').read_bytes())) for n in ('experiment.py','audit.py')]"
python -c "import bz2; from pathlib import Path; Path('scored.json').write_bytes(bz2.decompress(Path('scored.json.bz2').read_bytes()))"
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py scored.json --out audit_replayed.json
```

## Interpretation and next research choice

The frozen, simple high-order structure learner identifies many correctly planted parity motifs, but the contextual residual updates degrade cold predictions relative to both strong conventional ElasticNet and the candidate's own old checkpoint. **Do not fine-tune the consumed seeds.** The next falsifiable direction is to isolate *why* residual updates harm generalization: compare a validation-gated or formally constrained update against a fully trained conventional ElasticNet control on fresh worlds, with genuine within-world intervention benefit and retention. The result does not establish native tokenless Yggdrasil progress or autonomous training.
