# ENERGY-69 — frozen joint-block admission screen: DEVELOPMENT_NO_GO

**Date:** November 19, 2026. **Scope:** isolated *external synthetic* energy-related causal-representation screen. Not Yggdrasil native training, original scientific first-use, or a production model improvement.

## Exact chronology and source custody

1. An implementation smoke used seed `210899` on only two cases; excluded from screening. Frozen Python source SHA-256: `fea1b3ea38c190aed31ba91f9a824db1f484219d475179d2beedbba002713393` (7,654 bytes), Git blob SHA `29a6ef68f42b9cd38129a453db2af69ad9defc24`.
2. Prospective protocol `prereg.json` was **committed before the screened run** at `66632412fd1f70ff815a2ba71bd95e687f410995`, locking the source hash, methods, controls, held setup, seeds `210901,210917,210929`, stopping rules and 5 gates.
3. The original exact SHA-pinned Python source was executed once for the 72-case screen with NumPy 2.3.5 and scikit-learn 1.8.0, single-threaded BLAS/OMP/MKL. The source SHA was unchanged before/after. A source-identical replay matched all 72 non-timing case fields exactly; it is **not independent scientific replication**.
4. A separately written post-score audit independently re-aggregated original CSV case receipts without importing experiment code; **1,206 assertions PASS**. This audits arithmetic/identity/gate reporting, **not** independent source/world reconstruction, learning/transfer, or scientific efficacy.

## Frozen screen (72 unique worlds)

Four families (`null`, `two`, `four`, and `four_plus_fifth`), three distinct screened seeds, six worlds per seed/family. For each world: 48 observed fit interventions, 16 disjoint validation interventions, and 48 disjoint cold held action identities; Gaussian observation noise σ 0.30. Both block4 and validation-selected path share the **same** five-step feature-search path, corresponding train/validation fits and final observed labels. Full 126-feature ridge and fully fitted validation-selected ElasticNet are separate conventional controls. Cold held means **new action identities under the same mechanism**, not unfamiliar-world transfer. No planted support labels enter fitting.

| Arm | Mean held cold MSE (lower better) |
|---|---:|
| Same-path conventional validation-selected `cv_path` | **0.1620345424** |
| Conventional `fixed4` | 0.1831939999 |
| Candidate `block4` | **0.1880505691** |
| Validation-selected ElasticNet | 0.2207117881 |
| Conventional full 126-feature Ridge | 0.7497886735 |
| Shuffled-label negative | 1.4616632589 |

Candidate `block4` has **16.06% more mean cold MSE** than the best eligible conventional control `cv_path`, hence the 5% required superiority gate fails. The candidate is also worse than same-path validation selection on seeds `210917` (0.227474 vs 0.170344) and `210929` (0.177952 vs 0.157054). On out-of-grammar `four_plus_fifth`, candidate MSE **0.457627** vs conventional `cv_path` **0.355928**.

| Prespecified gate | Status |
|---|---|
| Best-control improvement >=5% | **FAIL** |
| Strict win on every seed | **FAIL** |
| Every-family non-degradation within 10% | **FAIL** |
| No-signal null protection within 10% | PASS |
| Shuffled-label negative separation >=20% | PASS |

**Overall: 2/5 PASS → DEVELOPMENT_NO_GO.** Do not tune against these consumed seeds or use ENERGY-67 reserved primary seeds. The mathematical ENERGY-68 counterexample still stands; it did not imply this new block strategy would win against proper conventional validation.

### Retained evidence / scope note

- Original raw `cases.csv`: **24,080 bytes**, SHA-256 `6fe5fb7ed986952bac82581fd5f0ef028acd102e956f183a70f33eda1b5feaf6`.
- Original result JSON: **2,812 bytes**, SHA-256 `3b0afb5df107a3da71a6ccea2dcc65caa86037e6d5bf4418633007bff3aaa0ed`.
- Post-score audit JSON: **416 bytes**, SHA-256 `944a0d028839c087942abeb5913e6e06d04f1b92afec075cd28d66e35ee6fa49`; post-score audit Python: **2,859 bytes**, SHA-256 `9f0f1be824c7036e1f5d83b7230c74c8a827aa6857598fd58c9e4b7c9257afc3`.
- Source-identical semantic replay SHA-256 `f04a3be8d7ba2c370e777bff28f45d8a7143dfffa0f8957c46c61366f109bede`.
- Original original-evidence archive `ENERGY-69-original-evidence.tar.xz`: **14,684 bytes**, SHA-256 `2de9e13da3924b6ebc244a54f9907525685c897487e0718f9fbb060717058238`; original unencoded Git object identity `4c4f1dd925834485d463fe1031669c0ad7d70245`. **Complete remote evidence custody:** the original byte-exact archive is stored as three verified base64 text parts in this directory, with `archive_manifest.json` and `verify_archive.py`. Run `python -B verify_archive.py` on a checked-out candidate to verify all part SHA-256 hashes, reconstruct the archive SHA-256, validate six tar members and exact original source/case/result/audit content digests. Both the independent post-score audit source and all 72 original case-level CSV receipts are present inside the archived tar. Source, result JSON and audit JSON are separately reviewable. GitHub blob SHA-1 checks for every part matched the original local part bytes before linking this tree; CI/engineering and native scientific acceptance are separate.
- Isolated CPU process wall time **2.32 seconds**, peak resident memory **160,296 KiB** for this run. Per-arm component timings are descriptive; no measured 2× end-to-end advantage, physical energy reduction, native retention gain, new-family invention, or scientific validation.

## Engineering and deployment separation

G29 Atlas Acceptance remains failing for this archive PR on both Linux and Windows because the pinned indexed-file set changed; this is **engineering CI FAIL**, not a failure of the 72-case screen or a qualified native regression. Repair requires exact-SHA atlas regeneration of all three generated files on a compatible clean checkout and full mandatory final regression. `main`, weights, model architecture, research owner, runner, scheduler, scientific first-use, deployment and accepted refs remain unchanged.

**Disposition:** retain the negative in the existing archival PR; stop joint-block threshold tuning. For the next independent mechanism, focus on causal-state adaptation/structural transfer with real action-consequence receipts and fully trained matched controls, not another per-step admissions threshold.
