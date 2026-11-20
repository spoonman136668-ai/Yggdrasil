# ENERGY-57 — Stable relations between learned causal factors

**2026-11-19. Classification: SCREEN_NO_GO, 10/11 preregistered gates PASS; one critical FAIL.**

This is external synthetic causal-learning research, not native Yggdrasil cumulative training or SCIENTIFIC_PASS.

## Frozen scientific custody

- Prior archive branch: `d656a6b64066d37c919ffa3f1e9ac84223801987`; exact source+auditor freeze commit `2d835e55131748a0cfcee28b27ad52e84dc39a8f`. Separate preregistration commit `d24f2293322d72a0213e7216dafe37e2b5cbe1e4` was confirmed on GitHub **before** either prospective seed was scored.
- Source tar SHA-256: `9a854558df61ff23f48befe229747e49e208f7c55ee7b91c38280f2253dada41`. Scorer SHA-256: `d6584ea41afaaf2f86bdf5ab5d6b26f6872223ff16c7d0481a385a51b21d2b40`; independently written audit SHA-256: `2650ee998ffb7938c2ab9b91aaeac319cf58458e835c08e909418925f9dbd1b5`.
- Two excluded pilots 99557 and 99563, three cases each, were evaluated *before source freeze*, independently audited (7,280 checks each) and excluded from confirmation. Candidate beat some conventional models on the first pilot and lost to OMP on the second; no post-prospective tuning.
- Prospective screen: seeds **99619 and 99637**, four world IDs × three families each = **24 independent generated worlds**. Reserved 36-world primary seeds **100019, 100043, 100057 NOT consumed** under frozen stop rule.

## Data and architecture

Every world has 408 unique 10-bit randomized underlying causal interventions, split 96 old training, 96 new training, and 72 held old/new/cold each; two additional observed nuisance cues follow context-specific correlations and become independent at cold. Four unknown hidden pair-parity primitive factors on causal bits connect via two stable shared relations, an old-only and a new-only edge. A flipped-relation family reverses one shared edge; an unseen-triple family adds a new three-factor interaction that the candidate relational grammar cannot represent.

The candidate recovers four pair-parity supports using only old witnessed outcomes, fits four primitive coefficients and six possible pairwise relational products, independently evaluates old/new coefficient stability and shares only stable signed edges. **The old checkpoint is frozen exactly**; a new constrained Ridge head predicts new and cold contexts. The selection is a fixed heuristic over an authored finite graph grammar, not unrestricted causal-rule invention. Neither planted module identity nor held labels are available at fit time.

Fully trained controls on identical observed labels: a strong **matched separate-relations Ridge using the same learned primitives and relational graph**; an unconditional-sharing Ridge ablation; full order-4 Walsh OMP8 and ElasticNet; RBF KernelRidge; 48-tree ExtraTrees; frozen no-adaptation; shuffled-new-label negative. Stronger and weaker controls have different inductive biases; same information budget does not imply identical capacity or compute.

## Prospective aggregate held errors

| Fitted method | Old held MSE ↓ | New held MSE ↓ | Cold held MSE ↓ |
|---|---:|---:|---:|
| stable_relations | 0.045934 | 0.344705 | 0.412945 |
| separate_relations | 0.045934 | 0.351145 | 0.418607 |
| unconditional_shared | 0.045934 | 0.895293 | 0.930654 |
| full_elasticnet | 0.196569 | 0.817802 | 1.956340 |
| full_omp | 0.120854 | 0.905622 | 3.363938 |
| rbf_krr | 4.662746 | 5.026965 | 5.892671 |
| extra_trees | 9.272981 | 9.314161 | 10.532380 |
| no_adapt | 0.045934 | 2.515724 | 2.432468 |
| shuffled_new | 0.045934 | 7.735840 | 8.213373 |

**Candidate cold vs strongest full-basis conventional (ElasticNet): 78.89% lower error.** Candidate vs directly matched separate-relations: **1.35% lower error**, less than the frozen **3.00%** minimum. The latter is the decisive scientific comparison; comparisons to much weaker full-basis models do not override it.

## Learned support and relational identity

- Planted base pair support recall: **98.96%**; chosen factors come from OLD observations only.
- Stage-invariant relation edge recall: **97.50%**; precision among shared edges **100.00%**. Shared edges selected: 39; false shared: 0. Ground-truth relation identity is used for audit/scoring only.
- These numbers are conditional on the generator’s simple planted causal graph and finite pair-parity primitive grammar, not discovery of a general symbolic mechanism.

## Per-seed reproducibility

| Seed | Candidate cold | Matched separate cold | Best full-basis conventional cold |
|---|---:|---:|---:|
| 99619 | 0.318984 | 0.326753 | 2.354650 |
| 99637 | 0.506905 | 0.510461 | 1.558030 |

## Per-family cold transfer

| Family | Candidate cold | Matched separate cold | Best conventional cold |
|---|---:|---:|---:|
| stable_edges | 0.047631 | 0.048557 | 1.859225 |
| flipped_relation | 0.045952 | 0.046475 | 0.759623 |
| unseen_triple | 1.145252 | 1.160790 | 2.925693 |

## Eleven frozen qualification gates

| Preregistered gate | Result |
|---|---|
| `cold_vs_best_conventional_5pct` | **PASS** |
| `cold_vs_separate_relations_3pct` | **FAIL** |
| `both_seed_wins_best_conventional` | **PASS** |
| `both_seed_no_relational_damage` | **PASS** |
| `primitive_support_recall_80pct` | **PASS** |
| `invariant_relation_precision_70pct` | **PASS** |
| `invariant_relation_recall_65pct` | **PASS** |
| `old_frozen_retention_exact` | **PASS** |
| `all_families_no_degrade_10pct` | **PASS** |
| `shuffled_new_negative_20pct` | **PASS** |
| `cold_vs_new_robust_150pct` | **PASS** |

**10 PASS / 1 FAIL = SCREEN_NO_GO** because `cold_vs_separate_relations_3pct` was frozen as a *critical* gate. Do not reinterpret the large advantage over weaker full-basis controls as an invariant-sharing pass. No retuning or scoring the reserved primary seeds.

## Engineering, independent audit and replay

- Independent source reconstruction and refit audit PASS: **57,779 enumerated checks**, 24 worlds, nine fully fitted arms, all model predictions/held errors, old/new/cold context source labels, action disjointness, primitive selection, invariant relation edge IDs and aggregation. Auditors **do not import scorer**, but use the same NumPy/scikit-learn backends and matching synthetic generator rules.
- Exact-source replay all semantic fields PASS: timing-free canonical SHA256 `4865a75f490c9c4b83b0821d7133bc618d47aadc7c48f6d8a78ef67b983f1627` (1,422,662 bytes); excludes `elapsed_total_seconds` and per-arm `timings_control` only. Independent audit of replay also PASS 57,779 checks; not a second scientific dataset.
- First prospective source run took 1.839 local CPU seconds for all 24 worlds, excluding independent audit and full infrastructure. **No physical energy consumption or whole-process cost measured.**
- Complete byte-identical original score `7bb53016a6c3dc34e55e89d0245b0f0244ddc22742884fb592b5a30474c500c3`, replay `e9d67f038b50fa5219ba55daa2a2498811845dbe144cb75701d7e7540a19a38c`, audits, both excluded pilots and 24 per-world receipts will be stored in the evidence archive, with standalone SHA verifier.
- GitHub Actions CI/code-atlas result and native dual-platform regression are **separate** engineering gates; do not conflate them with local science checks. No deployment, PR merge, accepted-ref mutation, runtime controller change, or native Yggdrasil training.

## Decision and scientific implication

The **relational representation** improves cold prediction relative to poorly matched full-basis conventional learners in this synthetic setting, including an unmodeled triple interaction; crucially **ordinary separate-context Ridge on exactly the same learned primitives and relations explains virtually all the benefit**. The specific invariant-sharing rule therefore lacks independently qualified incremental benefit. The next falsification should test cross-episode function retention and learned causal relationships on new source grammars against the matched primitive+relation Ridge baseline; not another threshold adjustment on these consumed worlds.

## Reproduction

Extract `source.tar.bz2` from the pinned source commit. On CPU with Python3.13.5, NumPy2.3.5, SciPy1.17.0, sklearn1.8.0 and single-thread BLAS:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -B experiment.py --seeds 99619 99637 --out reproduced.json
python -B audit.py reproduced.json --out audit_reproduced.json
```

The original results and independent evidence are stored under `EVIDENCE.tar.bz2.part*` and verified by `verify_archive.py`.
