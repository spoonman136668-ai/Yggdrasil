# ENERGY-53 — Hypothesis-specific intervention acquisition

**Frozen classification: SCREEN_NO_GO (mixed positive aggregate, negative per-seed stability)**

- Source frozen commit: `4fdadd0b4de9bd6ac79537ccc76356793e898b3d`
- Prereg before any prospective score: `f5eb3730d8233d7592d2a762044ca3389e8f9d8f`
- Prospective screening: 24 worlds across independent source seeds **99721, 99733**. Excluded prefreeze development seed **99709**. Primary seeds **9511, 9523, 9547 were NOT consumed**.
- Every policy used **80 common OLD consequences, four identical NEW anchors and 12 additional NEW interventions** from a 96-action pool. The causal hypotheses all come from one **preauthored finite 24-signature grammar**. Neither hypothesis identity nor held-out outcomes was available when selecting actions.
- **Five acquisition policies × three independently trained downstream learners (OMP3, ElasticNet, Ridge)**; primary method specified before outcome as **tournament + OMP3**. Full matched observation budgets and actual selected action IDs in evidence bundle.

## Primary screening comparison (cold-context held MSE; lower is better)

| Acquisition policy | OMP3 | ElasticNet | Ridge |
|---|---:|---:|---:|
| tournament | 0.278002 | 0.329427 | 0.638369 |
| hamming | 0.566689 | 0.372219 | 0.810048 |
| d_optimal | 0.375740 | 0.339299 | 0.762665 |
| uncertainty | 0.340311 | 0.355509 | 0.759413 |
| random | 0.493852 | 0.525980 | 0.929407 |

**Pooled tournament OMP3:** 0.278002. **Best conventional other policy+learner:** d_optimal + elasticnet, 0.339299; tournament's pooled advantage **18.07%**. Best alternate OMP3 policy MSE 0.340311, tournament gain **18.31%**. Random OMP3 MSE 0.493852; tournament gain **43.71%**.

### Frozen screening gates

- **PASS** `gain8_omp_best_alternative`
- **PASS** `gain5_all_other_arms`
- **PASS** `gain10_random_omp`
- **PASS** `gain5_hamming_omp`
- **FAIL** `per_seed_positive_both`
- **PASS** `old_retention_exact`
- **PASS** `family_no_more_than_10pct_worse`
- **PASS** `selection_cost_below_20x_random`

**7 of 8 PASS**, but the **explicitly critical** per-seed strict-advantage gate failed. Under frozen preregistration, **SCREEN_NO_GO**, and the reserved 36-world primary is NOT authorized. Reclassifying this as a development pass based on pooled results would be outcome-dependent.

### Replication by prospective source seed

| Seed | Tournament OMP3 MSE | Strongest other OMP3 MSE | Advantage (+) / disadvantage (−) |
|---|---:|---:|---:|
| 99721 | 0.354541 | 0.472511 (uncertainty) | +24.97% |
| 99733 | 0.201463 | 0.133116 (d_optimal) | -51.34% |

**Scientific interpretation:** Adaptively discriminating competing, explicitly enumerated causal hypotheses was promising in one cohort and pooled over both, but was **51.34% worse** than standard D-optimal acquisition on seed 99733 (OMP3). No claims about reliable unfamiliar-world transfer, energy use or native tokenless intelligence are supported. Preserve this outcome; do not tune consumed seeds.

## Audit, reproducibility and limitations

- Source-freeze byte hashes and numerical source identity in `source_manifest.json` and `provenance.json`.
- `EVIDENCE.tar.bz2` contains the **original unmodified** `screen_scored.json`, exact-source `screen_replay.json`, `screen_audit.json`, semantic replay receipt and all **120 policy/world receipts**, including acquisition indices and per-arm prediction hashes.
- Independent selector reconstruction and all 15 downstream refits pass **2,399 checks**. Exact-source deterministic replay is byte-equivalent after excluding timing metadata. Audit still **shares the synthetic generator and sklearn/NumPy**, not wholly independent science.
- Source runtime on Linux single-core CPU: primary screen ~5.40 s and auditor ~4.57 s, excluding independent re-scoring and GitHub custody. Policy selection CPU wall time is not whole-process training or physical energy consumption.
- **ENGINEERING:** Local source and audit PASS. GitHub-hosted code-atlas/CI and native Yggdrasil regression must be reported separately.
- **SCIENCE:** `SCREEN_NO_GO`; no accepted scientific first-use, no primary result.
- **DEPLOYMENT:** None. Main, accepted refs, autonomous controller/loop and native weights unchanged.

See `verify_archive.py` for exact hashes/recomputation, then run from extracted source archive:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -B experiment.py --seeds 99721 99733 --out replay_scored.json
python -B audit.py replay_scored.json --out replay_audit.json
```
