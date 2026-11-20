# ENERGY-62 — Unprovided high-order Boolean templates from learned primitive compositions

**Date:** November 19, 2026. **Frozen verdict: `SCREEN_NO_GO`; 5 of 10 gates PASS.** External contributor synthetic development evidence; **NOT native Yggdrasil training, operator invention without a primitive algebra, SCIENTIFIC_PASS, official acceptance, merge or deployment**.

## Frozen custody before the first new seed

- Prior PR #1210 head: `b86d4b98ac933f3ae8411663c731c83dc3d08bd3`. Source freeze: `c46d94f3d7c07a578adfdf65c08995c34fa00661`. **Separate GitHub preregistration: `ce349b9281db82794c0d1bb90af334cb118d504c`**, verified by GitHub readback BEFORE scoring seed `997711` or `997733`.
- Original source tar SHA-256 `f50f0ae406c5e272fc2602fa30c568232a838b0a79c9221c21361e93ba89f4ef`; scorer `42e2bd671589e9f33ba766ba5f97c1f1a077bd2a9773f546351ccde1935d3771`; audit `27a6bc44b31254e79589697ae8bd8376537b14c477ab8508a9f9b7e343936124`.
- Development seed `889811`/world ID 0 (3 families) scored before freeze for code smoke. Source subsequently added a conventional softmax memory control, then new source+audit were frozen. The dev pilot is excluded, cannot be confirmatory.
- **Prospective** screen seeds `997711`, `997733` × four worlds × three families = **24** worlds. Unconsumed primary seeds **`104101,104117,104129`** stayed unused under the frozen stop rule.

## Intervention and model design

Each world has 8 underlying causal binary action variables and two context-dependent nuisance inputs. There are 224 distinct 8-bit causal do-assignments per world: 64 old witnessed, 64 new witnessed, 32 old-held, 32 new-held, 32 cold-held. Nuisance cues change correlation old/new and are independent cold. Source plants a shared two-bit parity and one old-versus-new higher-order mechanism across `conditional5`, `nested_xor5`, `threshold5`, with iid Gaussian consequence noise σ=.18. The held consequence labels, planted operators, factor identities and true parameters are withheld from all fits; synthetic generator code is author-known.

The candidate learns source lower-order unary/pair AND/XOR primitives from factual training examples, retains selected old primitives, composes a bounded new feature dictionary by AND/XOR over disjoint primitive pairs, then sparsely selects five features with an explicit 1.12x old-structure score bias. The *generator-specific high-order conditional/threshold templates are not supplied as named features*, but basic operations, search depth and candidate-construction rules **are provided**. This is finite designed program search, not unbounded self-invented operators.

All arms see exactly the same 128 old/new witnessed examples. Controls include **fully trained same generated-bank ElasticNet, Ridge and fresh OMP5**, conventional old/new OMP softmax memory, raw-input KRR and ExtraTrees, primitive-only OMP, frozen-old and shuffled-outcome negative. Same data budget is NOT identical compute/capacity. Scores are mean per-world MSE on 32 withheld consequences per context, lower better.

## Original prospective screening results

| Learner | Old MSE | New MSE | Cold MSE |
|---|---:|---:|---:|
| `softmax_memory` | 0.248470 | 0.676047 | 0.698598 |
| `fresh_omp` | 0.248470 | 0.678498 | 0.703707 |
| `reused_composition` | 0.248470 | 0.651958 | 0.724034 |
| `matched_elasticnet` | 0.248470 | 0.780279 | 0.923157 |
| `atom_only_omp` | 0.248470 | 0.908653 | 0.914960 |
| `matched_ridge` | 0.248470 | 1.226164 | 1.377427 |
| `rbf_kernel` | 0.248470 | 1.317949 | 1.443969 |
| `extra_trees` | 0.248470 | 1.693580 | 1.751108 |
| `old_no_update` | 0.248470 | 1.705012 | 1.767250 |
| `shuffled_new` | 0.248470 | 2.801658 | 2.734940 |

Candidate cold MSE **0.724034** vs strongest conventional `softmax_memory` **0.698598**, so candidate is **3.64% MORE error**, not a superiority result. Compared with fresh same-bank OMP5, candidate 2.89% worse. Matched same-bank ElasticNet is weaker on this screen but cannot rescue the failure against the strongest conventional model.

### Per-seed cold

| Seed | Candidate | Best other pooled control for seed | Control |
|---|---:|---:|---|
| 997711 | 0.761939 | 0.803664 | `softmax_memory` |
| 997733 | 0.686128 | 0.593531 | `softmax_memory` |

### Per-family cold

| Family | Candidate | Same-bank OMP | Same-bank ElasticNet | Softmax memory |
|---|---:|---:|---:|---:|
| `conditional5` | 0.318944 | 0.318944 | 0.244370 | 0.318943 |
| `nested_xor5` | 0.985135 | 1.052122 | 1.527457 | 1.052102 |
| `threshold5` | 0.868023 | 0.740057 | 0.997645 | 0.724748 |

The composition mechanism was active in **22/24 worlds**, selecting **53** composed expression terms across them. Source-built operator search was exercised, but not reliably advantageous.

## Ten preregistered gates

| Frozen gate | Result |
|---|---|
| `cold_vs_same_bank_elasticnet_5pct` | PASS |
| `cold_vs_same_bank_omp_5pct` | **FAIL** |
| `cold_vs_softmax_memory_5pct` | **FAIL** |
| `cold_vs_strongest_conventional_5pct` | **FAIL** |
| `composition_exercised_20pct` | PASS |
| `family_noninferiority_10pct` | **FAIL** |
| `new_cold_vs_old_no_update_20pct` | PASS |
| `old_readout_frozen_exact` | PASS |
| `shuffled_negative_20pct` | PASS |
| `win_each_screen_seed` | **FAIL** |

**5 PASS / 5 FAIL -> `SCREEN_NO_GO`.** Critical strongest-model, softmax-memory, same-bank OMP and per-seed gates fail. The entire 36-world primary was stopped without any runs. Do not retune the consumed screen or reinterpret wins over weaker conventional methods as positive confirmation.

## Source-free audit and reproducibility

- Independently implemented generator / model refits: **PASS 50,059 checks**; 24 worlds; ten methods; each 32-held old/new/cold prediction compared, plus disjoint action assignments, all hidden consequence labels, all feature indices/fit coefficients and every metric. Auditor does **not** import `experiment.py`; nevertheless shares generator specification and NumPy/scikit-learn solvers, so no wholly independent scientific replication is claimed.
- Exact unchanged-source semantic replay PASS; timing field `elapsed_s` alone excluded. Canonical SHA-256 `95e04f9659f89c3899de92690ce6be4182e5705db602a0b3588acab0c784b05f`; re-audit PASS same 50,059 checks. Not a fresh dataset.
- Scorer single-thread local elapsed `1.080839` seconds, not end-to-end compute cost or physical energy. See source manifest/provenance. Linux and Windows GitHub CI to be reported separately; there is no native Yggdrasil qualification.
- Original `scored.json`, `replay.json`, two auditor receipts and pre-freeze `dev.json`/audit are compressed without alteration in `EVIDENCE.tar.bz2`; per-world receipts are also in `case_receipts.csv`. `verify_archive.py` verifies byte hashes and replay scores. Reproduce `tar -xjf source.tar.bz2` then `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --seeds 997711 997733 --out replay.json` and `python -B audit.py replay.json --out audit.json`.

## Decision and isolation

Reject this particular persistence-biased compositional feature learner. On the source-authored unfamiliar mechanisms, conventional calibrated memory or fresh OMP is at least as good. Further work should isolate whether the information in persistent prior causal structure becomes useful under recurrence or sparse labels, rather than retuning this consumed cohort. No change to native Yggdrasil weights, main, owner loops, official scientific state, first-use datasets or deployment.
