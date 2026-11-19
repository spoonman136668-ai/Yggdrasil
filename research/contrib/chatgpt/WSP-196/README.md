# WSP-196 — Original GB1 four-site transfer: direct weight programming vs converged regression

**Completed verdict: `PUBLIC_DEV_NO_GO`.** No scientific acceptance, native Yggdrasil model training, original-world first-use or deployment.

## Why a versioned source repair was needed

[WSP-195](../WSP-195/README.md) was frozen before authentic numeric outcomes, but its first original-source admission refused records containing underscore genotype placeholders. Its **INVALID** result is immutable. The original investigators' source has **191,157 rows**, including **32,587 incomplete four-site identifier rows** and **158,570 valid 20-amino-acid sequences**. Of the latter, **149,361 have an original, nonmissing unadjusted fitness score**.

WSP-196 was preregistered **after inspecting only genotype structure and missingness flags**, not fitness outcomes. It permits **only** those 32,587 underscore-placeholder rows to be excluded, requires their exact count, and otherwise uses the **same** science algorithm, frozen split, thresholds and controls as WSP-195. Changes to the previously failed code/result are prohibited.

## Source and immutable custody

- Original author: `wchnicholas/ProteinGFourMutants@dbdd7639187e0b8f22359f404ce4d1d950fcc8a9`, [`result/Mutfit`](https://github.com/wchnicholas/ProteinGFourMutants/blob/dbdd7639187e0b8f22359f404ce4d1d950fcc8a9/result/Mutfit), Git blob **`3bf094f1b5c8bd84a35e04ae9c23bcf97c2bfa89`** (13,837,211 bytes). Both original author code and Git blob SHA1 were checked independently. Original source values were never redistributed.
- Underlying experiment: Wu et al., *Adaptation in protein fitness landscapes is facilitated by indirect paths*, eLife (2016), DOI 10.7554/eLife.16965, four GB1 mutation sites V39/D40/G41/V54. This is a **public historical biochemical selection experiment**, not a new physical experiment or virgin source.
- [`prereg.json`](./prereg.json) committed FIRST at **`8141819243b3dfe0f26ae701d49737164d16aecf`** for this version. Original predecessor WSP195 prereg `3af4c3e0bcbedd0416d8c3d2955eec0ca89df8f7`. Original WSP195 invalid result commit `88fed22f6f3476bc3745f7d27ada9a742d601105` preserved.
- Exact frozen [`evaluate.mjs`](./evaluate.mjs) blob **`f7ad4a2db4d4226217d490ca69ef4c4d89b63b3c`**, committed `3ddb2171be10e1f35d976cc0dfcad86323b56b40`. Negative [`test_evaluate.mjs`](./test_evaluate.mjs) blob `fb2cb8426eea8e811ca4305f3a62020fa4d5ff48`, **6/6 PASS** against exact code. [Pre-score qualification](./pre_score_qualification.json) committed `478d715d210b714884083dec58f8673a689cc976`.
- **ONE** authentic primary experimental score sealed at [`result.json`](./result.json) in commit **`4839b12d6bbcd90d01fd21c468639ef74989cc33`**, Git blob `2ab22fd2e7efd7243446ea2360235932ba6852dd`. No scores were used to change the model, class rule, source or training split afterward.

## Frozen experiment

- Train **20,228 genotypes**: all measured WT/singles/doubles and 18,060 hash-selected measured triple mutants.
- Select on **7,959** disjoint measured triple mutants (VALID). Never use fourth-order fitness labels for any model training, preprocessing, feature selection or hyperparameter decision.
- Score **121,174** measured *four-site* variants (DEV), once.
- FIT-only `log1p(I20fitRaw)` normalization. The published adjusted `I20fit` and cross-experiment `AOfit` were explicitly excluded to prevent control contamination.
- Candidate: native categorical weights from measured singles; directly programmed pair residuals compressed to 2/4/8-rank or full tables; one-pass shared pair-context marginal program of third-order residuals. VALID chose **rank 2, pair multiplier 1, triple multiplier 1**. These are local programmed weights, **not gradients, transformers, or actual native Yggdrasil substrate changes**.
- Strong conventional baseline: 9 deterministic ridge candidates of additive, categorical pairwise and categorical third-order input features, lambdas 0.1,1,10; each trained on the **same source FIT records**, at most 250 coordinate descent passes, convergence threshold <=1e-4. Only converged variants were eligible for final selection, exactly as preregistered.

## Held-out result — lower normalized RMSE is better

| Predictor | VALID triple RMSE | HELD four-site RMSE |
|---|---:|---:|
| **Converged conventional categorical pairwise ridge**, lambda=10, 2,237 coefficients | **0.514139** | **0.608311** |
| **Directly programmed factorized pair + triple motif learner** (rank=2, alpha=1, beta=1) | 0.837439 | 1.129267 |

**Direct programming was 85.64% worse** on independently excluded fourth-order genotype targets. Pair-genotype resampled 1,000-bootstrap relative improvement 95% interval: **[-86.88%, -84.38%]**. Candidate does not win on VALID or held DEV.

Convergence honesty: baseline lambda 10 converged for all degrees 1,2,3; lambdas 0.1 and 1 **did not** reach the frozen tolerance by 250 passes, and their scores are diagnostic only. No claimed fully trained control includes those unconverged variants. Strongest selected converged was degree 2/lambda 10. The candidate retains 76 single-state weights, 2,091 observed full double residuals and 4,292 shared triple marginal buckets; capacity, training cost and memory are **not demonstrated better** than the 2,237-coefficient conventional control.

Serialization preserved historical HD1/HD2 readout values with maximum drift **8.88e-16** after the third-order stage. This is a same-process JSON restoration check, **not** qualified independent cold-state restoration or durable learning over days.

## Reproduce without modifying the repository

Install Node 22 or compatible locally and obtain an authorized read-only copy of the original `Mutfit` file. Verify its exact Git blob SHA1 against the pinned source before evaluation. Then, from this folder:

```sh
node test_evaluate.mjs
node reproduce.mjs /authorized/read-only/original/Mutfit
```

An optional *engineering-only* full-size synthetic fixture is under [WSP-195's tests](../WSP-195/test_evaluate.mjs) and took 112,071ms on the V8 host. Neither fixture is scientific source evidence. [`reproduce.mjs`](./reproduce.mjs) refuses source hash drift and compares numeric results against sealed [`result.json`](./result.json). It is provided for independent qualification; **a second original-source run has not been executed**.

## Engineering / scientific / deployment

- **ENGINEERING:** exact source byte SHA1 PASS; source-free negative 6/6 PASS; first authentic source and frozen model comparison completed. WSP196 model-and-score observed **106,496ms**, excluding source acquisition and independent CPU/RSS accounting. Exact-source full Windows/Linux repository regression, independent reproduction and GitHub G29 remain **UNVERIFIED** until assessed.
- **SCIENTIFIC:** frozen historical public `PUBLIC_DEV_NO_GO`; no superior trained representation, causal discovery, unseen physical world transfer, independently qualified cold memory or SCIENTIFIC_PASS. Retain negative; no post-DEV retuning on these 121,174 consumed variants.
- **DEPLOYMENT:** NONE. Main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` unchanged; [protected source owner #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) still disallows protected first-use. No scheduled work, runner dispatch, merge, autonomous controller, paid API or native architecture promotion.

**Research implication:** A low-rank pair plus directly programmed shared triple-motif memory does not capture this landscape's unseen higher-order behavior well enough. In this experiment the conventional pairwise ridge wins by a large margin; model-class innovation must be qualified on a *new* independent source without optimizing against this consumed DEV result.
