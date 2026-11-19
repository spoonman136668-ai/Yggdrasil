# ENERGY-46 — Disjoint contradiction-gated repair falsification

**Date:** November 18, 2026. **Outcome: DEVELOPMENT_NO_GO (5/9 frozen gates).** Independent synthetic external research only; **not** native Yggdrasil training or accepted science.

## What changed from ENERGY-45

The previous ENERGY-45 gate achieved an aggregate cold improvement but failed old-context competitiveness and seed stability. ENERGY-46 holds the essential support-replacement mechanism and fixed 0.12 training-validation trigger while testing fresh seeds and a **new, separately authored causal-world generator** with three factor families: 2-bit XOR parity, 3-bit XOR parity and mixed parity/AND. This is **not** a new general learning architecture; it is an independent disjoint test of whether ENERGY-45's reported advantage is reliable. Pre-primary diagnostic smoke identified and repaired an uncompetitive old-context memory path; the final candidate protects the original OMP4 old head exactly. There was no post-primary adaptation.

## Frozen custody and experiment

- Prior archive HEAD: `2556ffca7dfefc0c026240b1694edbf34fdc2ec`. Source + independently written auditor committed **before protocol** at `78dffbfecfa7616822514cf1e5414a1ae467de67`. Protocol committed **before primary scoring** at `7a8e6e99f55cbc167317e4a750ea938fa6058776`.
- Source is `source.tar.bz2` (7,309 bytes), SHA-256 `2f3b1ac3e65340c6d3555ace51d6870f169dd72a01fa2917d2d7fd317855b8c9`; scorer original SHA-256 `fa38237a02f5fd76b66406ef6dccfe9b35bd406a24697ca81642d7c1ef1e1698`; independent auditor original SHA-256 `528509534942e2e18bb2880f411db2e1af2dc9b9128cfb8a024f6779d3858074`.
- Excluded pre-primary smoke: seed **99863**, six cases, **25,565 independent checks PASS**. Primary disjoint seeds **8909, 8923, 8933**, four source IDs × three factor families = **36 worlds**, including **27 changed mechanisms** and **9 no-change controls**.
- Per method per world: **96 witnessed old + 96 witnessed new interventions**; 128 disjoint held old, 128 new and 128 cold observations. Each arm sees the identical witness label stream, not hidden supports/weights or withheld labels.
- Exactly **11 distinct arms**, including fully trained ElasticNet, OMP, separate stagewise OMP, cumulative OMP structural memory, Ridge, random forest and validation-switched hybrid. Ablations: unconditional replacement, no repair, shuffled new labels. The author-specified feature grammar contains 364 binary parity/AND features; no open-world factor invention, active action selection or model transfer.
- Candidate holds the old-context support/coefficients completely frozen, ranks 24 replacement candidates by residual correlation, evaluates delete-one/add-one support edits on the last 24 of 96 **new training labels only**, triggers at validation MSE reduction ≥0.12, refits 4 selected new-context weights on all 96 new training labels. No held labels are used for structure search.

## All-arm primary results

| Fully fitted method | Old held MSE | New held MSE | Cold held MSE | Fit+predict seconds |
|---|---:|---:|---:|---:|
| replay_gated | 0.148153 | 0.163080 | 0.155899 | 0.43583 |
| unconditional_replay | 0.148153 | 0.375623 | 0.359777 | 0.41363 |
| hybrid_validation | 0.148153 | 0.144851 | 0.235008 | 0.35927 |
| stagewise_omp4 | 0.148153 | 0.153045 | 0.247324 | 0.28001 |
| omp_structural_memory | 0.632983 | 0.559002 | 0.633145 | 0.33296 |
| omp_full7 | 0.632983 | 0.559002 | 0.633145 | 0.27445 |
| elasticnet | 0.124873 | 0.135193 | 0.155626 | 0.36291 |
| ridge | 2.458617 | 2.519560 | 2.661642 | 0.30828 |
| forest | 2.594615 | 2.648098 | 2.663439 | 1.93298 |
| no_repair | 0.148153 | 1.684226 | 1.700360 | 0.26691 |
| shuffled_gate | 0.148153 | 4.441895 | 4.343238 | 0.42746 |

**Primary candidate vs strongest conventional (ElasticNet):** cold 0.155899 vs 0.155626, **+0.18% relative error**, so **the aggregate improvement DID NOT REPLICATE**. Old 0.148153 vs 0.124873, **+18.64% higher error**. Candidate nevertheless beats a validation-switched hybrid (0.235008) and unconditional replacement (0.359777); these weaker comparisons do not override the frozen strongest-control requirement.

**Mechanism fidelity:** correct obsolete/new factor replacement in **24/27 changed** cases; no-change correctly declined in **8/9** cases. The one false edit misses the strict ≤10% false-positive threshold on just nine no-change cases.

### Independent seed stability

| Primary seed | Candidate cold MSE | Strongest conventional cold MSE | Candidate strictly better? |
|---|---:|---:|---|
| 8909 | 0.156944 | 0.131582 | No |
| 8923 | 0.222314 | 0.148442 | No |
| 8933 | 0.088439 | 0.186855 | Yes |

### Family breakdown (descriptive, not post-hoc acceptance)

| World family | Candidate cold MSE | ElasticNet cold MSE |
|---|---:|---:|
| parity2 | 0.157838 | 0.188611 |
| parity3 | 0.089112 | 0.143871 |
| mixed | 0.220747 | 0.134397 |

### Frozen nine gates

| Gate | Outcome |
|---|---|
| `changed_correct_support_70pct` | **PASS** |
| `cold_vs_best_10pct` | **FAIL** |
| `cold_vs_matched_hybrid_5pct` | **PASS** |
| `nochange_false_edit_at_most_10pct` | **FAIL** |
| `old_replay_retention_1pct` | **PASS** |
| `old_vs_best_1pct` | **FAIL** |
| `seed_wins_2of3` | **FAIL** |
| `sham_new_20pct` | **PASS** |
| `time_at_most_3x_memory` | **PASS** |


**Classification:** **5/9 PASS; 4/9 FAIL ⇒ DEVELOPMENT_NO_GO**. Do **not** tune model thresholds, seed list, family rules or base controls against these consumed primary seeds. Old predictions were mathematically protected relative to the old checkpoint, but that protection **did not** equal competitive old learning. The third seed gains were not representative of the other two.

## Independent technical receipts and audit

- **Full byte-exact original primary** stored at `scored.json.bz2`, original 163,402 bytes, SHA-256 `f540d34519a8ae10de86d77dad8d04024d678855fbdaa39089b06702882d4961`; packed 25,194 bytes, packed SHA-256 `38be7ed6b49c9e0d26e367c39b5069173ea8fbf018d6dae2aa2865b0bd6d8837`. Includes all original factors, weights, per-arm cases, MSE and measured run timings.
- Full **36-world** case CSV, SHA-256 `9ed01d6c025060e7106302af710b09286c8b774dd0bf9e2ad750f5ca55279759`; independently verifies all arms and primary record hashes in `verify_archive.py`.
- **Independently authored** generator/refit audit reconstructed all 36 worlds and all **11 fitted/specified methods** without importing the scorer, checking source truths, selected supports/weights and every old/new/cold held prediction: **153,215 checks PASS**. NumPy RNG and scikit-learn solvers are common backends, not independent implementations of their internals.
- One exact-source semantic replay **PASS**, canonical timing-free payload 77,689 bytes, SHA-256 `37d1ce78db2955431b0ef2c90dfe8c6b99cc0c11a51a9fe12d1521aa7df29262`. Timing excluded from semantic equality and stored separately.
- Linux CPU Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0, one BLAS thread. Local fit+predict elapsed is **not** an end-to-end physical energy measure or a multi-platform acceptance qualification.

## Decision and next falsification

**Stop this variant at DEVELOPMENT_NO_GO.** The absence of reliable improvement across genuinely different seeds and independently created factor families falsifies a broad claim that ENERGY-45's cold advantage generalizes. The successful factor-replacement detection is mechanistic evidence on a finite authored grammar, not proof of autonomous general reasoning or Yggdrasil model learning.

A worthwhile future test should improve the existing *old-context model itself* (not merely freeze it), benchmark against the conventional **ElasticNet** baseline and include larger, unfamiliar action-dependent worlds under frozen matched budgets. Do not merge, integrate into FORGE, promote native scientific first-use, or modify accepted Yggdrasil refs based on these results. Native full Linux/Windows regression and repository atlas CI are separately unqualified.
