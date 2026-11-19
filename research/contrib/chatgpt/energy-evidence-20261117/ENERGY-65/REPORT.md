# ENERGY-65 — Residual fourth-order causal-factor induction after OLD learning

**Date:** November 19, 2026. **Frozen prospective verdict: `SCREEN_NO_GO`; 7/9 screening gates PASS, two robustness gates FAIL.** External contributor synthetic development evidence only; **not native Yggdrasil training, learning-system acceptance, scientific pass, merge, deployment or autonomous-loop change.**

## Frozen chronology and custody

- Previous draft PR #1210 archive head: `b4cf5fb070601bd5957f3cac02daee20c5e0fb03`.
- Frozen exact scorer, independent auditor and README source committed as **`4c798eae7409baa1d99e08c5f4e1848a7a3468e2`**. Source tar SHA-256: `743c7198ed805e4f5330cca9b376eb26cf2b234f4de49ed51ff0e2a9f1bf9686`; scorer `5bdb167862ab6979ead7aa05ec04dfbd86958b560808e25cb5c4e19dd141d760`; auditor `d09a12db2ae81b44d9e8b5f4070f7f546e5e24b66d34127a58f0b86520ada371`. Source Git blob `9cb52c825ab7834e71045019862c11f8a51618c5`.
- **Separate preregistration commit `5ca2ee9152092441e8e2289bc89f89b97c43cca0`**, successfully read back and checked against source manifest BEFORE prospective scoring. Frozen screening seeds `[999563,999577]` × four IDs × three families = 24 worlds. Primary seeds `[107101,107119,107137]` **never consumed**, because frozen stop rules failed.
- Excluded pre-source-freeze dev smoke seed `999551` x one world ID x three families. Dev smoke ran before source/prereg freeze and was explicitly excluded (5,286 auditor checks PASS); do not treat it as confirmatory data.

## Hypothesis and methods

Does learning **one new fourth-order action-consequence relation** by residualizing the witnessed NEW consequences against three OLD learned pair factors provide transferable new function without altering the frozen OLD response, and beat strongest conventional learners trained on the SAME observations?

Every author-generated world contains eight controllable ±1 action variables, three hidden old pairwise parity factors, and independent stage-specific Gaussian noise sigma .18. Generator families: `single_new_quad` (one new fourth-order factor), `double_new_quad` (two new fourth-order factors, beyond candidate's one-correction capacity), `novel_fifth` (a fifth-order factor outside candidate's entire fourth-order grammar). Three OLD pair coefficients may shift in NEW. Exactly **208 disjoint underlying binary action assignments per world:** 60 OLD witnessed, 40 NEW witnessed, and OLD/NEW/COLD held sets of 36 each. COLD changes action identities within same NEW mechanism, **not new unknown context or natural-world domain**. All learners see identical OLD60 + NEW40 witnessed labels; planted mechanism truth and held consequences never enter any fit. The auditor can inspect disclosed truth only for verification.

The candidate learns three OLD pair supports by ordinary OMP on a known 28-term pair-parity bank and freezes the old prediction head exactly. It fits a NEW Ridge head using the old supports, identifies a novel fourth-order feature from residualized correlation among 70 author-supplied four-bit Walsh candidates, then jointly refits the three old supports and selected new factor. The primitive grammar and search are **pre-authored**, not unrestricted invention.

Decisive conventional controls with the same witnessed labels: **three-fold train-only cross-validated ElasticNet** on the **matched old supports + all 70 quad features** (same representation capacity up to sparse selection), and a separately cross-validated full 98-feature pair-plus-quad bank; fully fitted full-bank OMP4 and Ridge; conventional train-error softmax retrieval of OLD and NEW fitted OMP hypotheses. Other controls: no new quad, frozen old, shuffled new labels. A truth-informed fitted oracle is diagnostic only and **excluded** from strongest-realistic comparisons. Training labels are equal but fitted model capacity and computational cost are **not matched exactly across all conventional arms**.

## Prospective 24-world mean squared prediction errors (lower is better)

| Method | OLD held | NEW held | COLD held |
|---|---:|---:|---:|
| `factor_residual_quad` | 0.037438 | 1.827906 | 1.856831 |
| `softmax_old_fresh` | 0.037438 | 2.036566 | 1.994126 |
| `full_bank_elasticnet` | 0.037438 | 2.169542 | 2.199357 |
| `same_support_elasticnet` | 0.037438 | 2.190754 | 2.331107 |
| `full_bank_omp4` | 0.037438 | 2.309993 | 2.299309 |
| `full_bank_ridge` | 0.037438 | 6.558300 | 6.084708 |
| `old_support_no_quad` | 0.037438 | 3.140559 | 2.959792 |
| `old_frozen` | 0.037438 | 2.696335 | 2.705609 |
| `shuffled_new` | 0.037438 | 7.380065 | 7.654247 |
| `oracle_basis (truth-informed, diagnostic ONLY)` | 0.037438 | 0.038271 | 0.038172 |

**Candidate COLD MSE 1.856831 versus strongest legitimate conventional `softmax_old_fresh` 1.994126: 6.88% lower pooled error**. This aggregate win is not adequate: the frozen per-cohort superiority and per-family nondegradation gates both fail. Against full-bank ElasticNet the improvement is 15.57%; against matched-support ElasticNet 20.35%. Old readout is copied unchanged for all arms by construction, so exact retention demonstrates the specified checkpoint arrangement, **not resistance to parameter interference in a single mutable learner**.

### Two independent prospective seed cohorts (COLD MSE)

| Seed | Candidate | Full-bank ElasticNet | Softmax memory | Strongest conventional |
|---|---:|---:|---:|---:|
| 999563 | 1.871248 | 2.136887 | 2.238020 | 2.136887 |
| 999577 | 1.842414 | 2.261827 | 1.750232 | 1.750232 |

### Three mechanism families (COLD MSE)

| Family | Candidate | Matched-support ElasticNet | Full-bank ElasticNet | Softmax memory |
|---|---:|---:|---:|---:|
| `double_new_quad` | 1.517194 | 0.081248 | 0.100873 | 1.731267 |
| `novel_fifth` | 4.016024 | 6.797532 | 6.336417 | 4.213909 |
| `single_new_quad` | 0.037275 | 0.114542 | 0.160781 | 0.037203 |

The candidate recovered the exact newly planted quadruple in **8/8 single-new-quad worlds** but its single-correction capacity failed strongly when TWO new quadruples were present: candidate COLD 1.517194 against matched conventional ElasticNet 0.081248. On `novel_fifth` the candidate cannot represent the planted five-way relation, so accuracy is limited; the truth-informed oracle's near-noise-floor results are NOT a valid learned-method comparison.

## All nine frozen screening gates

| Pre-registered gate | Decision |
|---|---|
| `cold_gain5_vs_best_strong_control` | **PASS** |
| `cold_gain5_vs_full_elasticnet` | **PASS** |
| `cold_gain5_vs_matched_elasticnet` | **PASS** |
| `each_family_nondegradation10pct` | **FAIL** |
| `each_seed_better_than_best_other` | **FAIL** |
| `novel_quad_recovered_60pct` | **PASS** |
| `old_retention_exact` | **PASS** |
| `over_old_frozen20pct` | **PASS** |
| `shuffled_negative20pct` | **PASS** |

**Screen decision: `SCREEN_NO_GO` (7 PASS / 2 FAIL)**. Four prereg critical gates required both pooled >5% gains and **strict per-seed superiority**. The latter failed (seed `999577`). Family nondegradation also failed on the double-quadruple family. Frozen rule required all four critical gates and at least 8/9 gates; therefore **do not execute the 36-world primary**, revise thresholds, consume reserved seeds or elevate the result to a scientific pass. Preserve the positive pooled effect as a bounded lead for *future disjoint* experiments only.

## Independent audit and replay

- Locally executed prospective scorer: **PASS, 24 worlds**; separately authored auditor `audit.py` **does not import `experiment.py`**, reconstructs action-bit identities, independently reconstructs every old/new/cold source outcome from disclosed noise and planted operators, refits all ten arms, validates trained CV configurations, candidate quadruple selection, all old/new/cold prediction vectors, all MSE aggregates and exact OLD readout: **42,078 checks PASS**.
- Auditor shares the disclosed generator semantics and NumPy/scikit-learn solvers. This is code-level independently implemented **refit verification, not independent scientific replication**.
- Exact frozen-source replay passed; only `elapsed_seconds` was ignored. SHA-256 of canonical non-timing scores: `641132d94466e051dc98a6870beb5ca3a55bb3928c0a9776299afa7702a3a9b5`. The replay auditor passed the same 42,078 checks; this proves deterministic execution, not new-science replication.
- The first prospective invocation attempted to write results from a process without directory write permission and exited `PermissionError`; **no result file was created and no outcomes were inspected**. The unchanged frozen source was rerun through a directory-authorized process. This was an infrastructure/file-permission defect, **not** a scientific failure or justification to change protocol.
- Original `screen_scored.json`, both original independent audit receipts, unchanged-source `screen_replay.json`, original 3-world excluded development smoke and its audit are stored in the integrity-verified evidence tar. `case_receipts.csv` provides compact per-world metadata; original full records preserve every prediction and source sample. Python 3.13.5 / NumPy 2.3.5 / scikit-learn 1.8.0 / SciPy 1.17.0 on Linux single-thread CPU. No physical energy or whole-process cost measurement; no native Yggdrasil runtime execution. Native Windows/Linux regression and official scientific acceptance must be assessed separately.

## Research conclusion

A **single** newly induced fourth-order factor can be recovered accurately on authored synthetic cases, and aggregate cold error can improve over trained conventional controls. But **two** new factors violate the one-correction assumption, and results are not stable across the independent seeds. This is a valid falsification of promotion readiness, not evidence of general causal operator invention. Strong future tests should explore multiple independent residual causal factors under held-out action mappings with exactly matched train-only CV and capacity, while retaining all negative cases and old functional readouts.
