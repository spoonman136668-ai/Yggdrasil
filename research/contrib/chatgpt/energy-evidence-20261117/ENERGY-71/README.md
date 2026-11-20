# ENERGY-71 — Causal composition without preauthored higher-order supports

**2026-11-19 · Frozen development result: SCREEN_NO_GO (3/7 gates PASS).**

This is a bounded *external, source-free synthetic* experiment, not native Yggdrasil learning or a scientific result eligible for integration. The hypothesis and all screen gates were frozen **before** the primary 80-world run in [prereg commit `f0e00f07`](https://github.com/spoonman136668-ai/Yggdrasil/commit/f0e00f07a1069485e03b1a85f2f9cc1d1aff9855). The exact original 13,328-byte Python source was pinned at SHA-256 `130d8b63461bddbee14ea28eb4dce91814b52ac6b48cd14996e4732ab5dd9ef7`; its compiled and excluded smoke test preceded freezing, seed 271099 not included below. The source never changed during scoring.

## Actual question and controls

Can a native-style compositional relationship builder **learn OLD causal factors from intervention receipts, then invent a previously unavailable higher-order factor by composing those learned supports with additional action variables**, and outperform strong conventional learners on held NEW action-consequence predictions?

- **80 independent generated causal worlds:** four new seeds × four mechanism families × five worlds. Each has nine controllable action bits, with **128 OLD fit + 96 NEW fit + 32 NEW validation + 64 returning OLD held + 64 NEW cold held** = 384 distinct action assignments per world; continuous noisy action consequences σ=0.22. Planting logic is not visible to trained models.
- OLD: learn two unknown 2-/3-way parity effects from 128 witnessed actions with OMP-like sparse fitting. NEW: unchanged old law, a fifth-order composition of an old pair with three extra bits, a sixth-order composition with four extra bits, or an unrelated fifth-order effect that has no old factor in common.
- **Candidate `composed`**: generate fifth-/sixth-order supports by multiplying *actually learned* OLD support atoms with unshared action bits, choose a one-factor residual correction using NEW training/validation only, refit on NEW witness data. This is **finite algebraic construction**, not open-ended concept invention.
- Strong eligible controls receive the same OLD readout and exactly the same NEW intervention/outcome receipts: `full_sparse` (all preauthored 4-/5-/6-way supports, one-factor validation selection), fully fitted validation-selected `elasticnet`, 96-tree validation-selected `extra_trees`, and analytic Gaussian one-new-factor `uniform_bayes` mixture with an explicit no-change hypothesis. `old_only` and `shuffled` are negative/safety controls. **Controls do not have access to planted source identities or cold outcomes.**
- COLD means **unseen action identities within each world after learning that world's NEW law**, not generalization to an independently unfamiliar world without training. OLD return is a JSON-serialized *immutable old model* readout and does not demonstrate shared-weight resistance to interference.

## Full frozen screen — held NEW MSE (lower is better)

| Arm | Mean cold MSE |
|---|---:|
| Conventional analytic Gaussian one-feature mixture | **0.049224927** |
| Conventional full-dictionary sparse fit | **0.049225408** |
| Conventional fully fitted ElasticNet | 0.053539259 |
| **Candidate constructive composition** | **0.159780717** |
| Old-only no-adaptation | 0.413610762 |
| Shuffled NEW outcomes | 0.422701498 |
| ExtraTrees (raw bits + OLD readout) | 0.558307574 |

**Candidate prediction error was 3.246× that of the strongest conventional control (+224.6% MSE), not 5% better.**

| Causal family | Candidate | Strongest conventional |
|---|---:|---:|
| Unchanged OLD mechanism | 0.048837 | 0.047926 |
| Compose fifth order from learned OLD factor | 0.048645 | 0.048645 |
| Compose sixth order from learned OLD factor | 0.054163 | 0.054163 |
| Unrelated fifth-order NEW relationship | **0.487478** | **0.046167** |

The candidate **matches, but does not beat** the full search and Bayesian control on the two supported compositional families. It fails almost completely on the unrelated mechanism because its candidate grammar is restricted to factors sharing OLD support. This is the decisive representational failure, and there is no claim that tuning its threshold would remedy it.

All four independent seeds fail the prespecified 5% advantage check. **Frozen gates:** global ≥5% stronger-control win FAIL, ≥3/4 seeds FAIL, ≥2/3 novel families FAIL, every-family ≤5% degradation FAIL; OLD return ≤0.02 absolute MSE drift PASS (immutable checkpoint, trivial), shuffled negative ≥20% separation PASS, cumulative fit+prediction time ≤2× fastest conventional PASS. **3/7 PASS → SCREEN_NO_GO**, no confirmatory promotion.

The isolated single-core Python process completed in **15.35 seconds** at peak **169,028 KiB RSS**. Per-arm fit+inference timing in `result.json` shares OLD fitting cost; it excludes generation/auditing overhead and is **not** complete research-wall process, FLOPs, or measured electrical energy.

## Engineering evidence / reproducibility

The complete unmodified original source, full 80-case JSON receipts, result JSON, independent case aggregation audit and audit result are present as exact-byte XZ/Base64 text objects to avoid binary file limitations in this connector. Their original byte lengths and SHA-256 identities plus committed Git blob IDs are frozen in `archive_manifest.json`.

From an exact checked-out commit, run `python -B verify_bundle.py --out /tmp/energy71-reconstructed` to verify **all** byte counts, Git object IDs, reconstructed SHA-256 and save the original six files. Use Windows-safe output paths as desired. Then `python -B audit.py <original-output-dir> --out reproduced-audit.json` to reaggregate case receipts (does not retrain). **Local post-score independent implementation audited 970 receipt/gate/identity assertions PASS**; it does **not** reconstruct learned predictions from source without importing the scorer. Replaying training with consumed seeds would be an engineering check only, not independent scientific replication, and is not needed for this archival qualification.

## Decision / stopping

**SUSPEND this specific external classical-energy / compositional-threshold exploration.** No further ENERGY-xx gate after this failed independent structural test is justified without a genuinely new source-grounded hypothesis capable of constructing relationships that do not share prior factors, real source licenses, disjoint first-use authorization from the native owner, and a new fully trained strongest-control comparison. Retain this negative alongside ENERGY-67/69 and the positive *mathematical* bounds ENERGY-68/70. Continued Yggdrasil cumulative training remains a distinct program with its own owner and permissions; no native integration, weights, first-use, accepted `main`, runner/controller, deployment, or merge was touched.

**Separate engineering limitation:** Existing archive PR #1210 G29 Atlas Acceptance fails on both Linux and Windows because pinned Atlas indexed source set is stale after the additive evidence files; this must be repaired on a clean authorized checkout without weakening tests. A scientific NO_GO is not converted into infrastructure failure by this CI issue.
