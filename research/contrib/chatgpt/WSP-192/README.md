# WSP-192 — Real historical gene-pair fitness: direct-weight composition vs trained controls

**Result:** `PUBLIC_DEV_NO_GO`. Original-author historical experimental data; no synthetic science, no live actions, no native Yggdrasil integration, no scientific acceptance or deployment.

## Frozen question and custody

Does directly programming local residual interaction weights enable transfer to previously excluded gene-pair combinations better than a fully fitted conventional model with the same observed FIT values?

- Original source: Norman et al., *Exploring genetic interaction manifolds constructed from rich single-cell phenotypes*, *Science* (2019), DOI 10.1126/science.aax4438.
- Original investigator repository: [`thomasmaxwellnorman/Perturbseq_GI@3b25109aeb9c0c2026bd70abd50304a0ad4e5395`](https://github.com/thomasmaxwellnorman/Perturbseq_GI/tree/3b25109aeb9c0c2026bd70abd50304a0ad4e5395).
- Author's processed source: `final_emaps/processed_fitnesses.csv`, **exact Git blob `c3609fe77b10e8b18d61bde816743528e42a0533`, 235,998 bytes**. This is guide-averaged historical growth/fitness interaction evidence, **not raw transcriptomics or a virgin new-world source**. Original source bytes are *not* republished here.
- Preregistration FIRST: [`86f45714b623ac1f755497432aadf3bd7e63daa3`](https://github.com/spoonman136668-ai/Yggdrasil/commit/86f45714b623ac1f755497432aadf3bd7e63daa3), prior to opening any fitness values.
- Frozen algorithm: [`evaluate.mjs`](./evaluate.mjs), code Git blob `5f8a4ba2289b21da19f3bd33c710779f5a4da01a`, initial commit `ede5d473d4b50f192fca9267caae4dea9e0536e5`.
- Pre-score [capacity caveat](./pre-score-qualification.json) committed before primary scoring. Direct residual memory 4,338 observed FIT scalar edges can exceed the strongest baseline's 1,792 rank-factor coordinates, so do not claim capacity/efficiency parity.
- First and **only** scored public DEV result commit: [`caef27604605491cc459eb4a99165963ac383078`](https://github.com/spoonman136668-ai/Yggdrasil/commit/caef27604605491cc459eb4a99165963ac383078). Sealed [`result.json`](./result.json) and [`provenance.json`](./provenance.json).

## One frozen public-development evaluation

The author matrix contained **112 intersecting genes** and **6,216 unordered distinct gene pairs**; orientations agreed to floating precision. Fixed SHA256 pair-level split from preregistration: **FIT 4,338**, **VALID 936**, **DEV 942**. Only FIT normalizes outcomes and fits parameters; VALID chooses hyperparameters and conventional control; DEV scored once.

| Method | Held DEV normalized RMSE (lower better) |
| --- | ---: |
| Fully fitted conventional rank-8 bilinear ALS (lambda=1; converged) | **0.177549179487** |
| Directly programmed two-hop residual composition (beta=2) | 0.270020629165 |
| Additive ridge diagnostic (lambda=1; *not converged* in frozen 300 epochs) | 0.300044554859 |
| Shuffled pair mapping negative (beta=0) | 0.300044554859 |

Compared with the VALID-selected converged bilinear control, direct program is **52.08% higher error** (ratio 1.52082). Pair-resampled 2,000-bootstrap uncertainty puts the candidate's relative *improvement* at **-61.23% to -42.81%** (95% interval): unequivocal negative. The direct program improves over a simple additive diagnostic but fails the preregistered stronger conventional comparator. All six bilinear ALS variants met the declared optimizer convergence check. The additive solver did *not*; it cannot be described as fully converged.

No retuning or primary DEV replay occurred. The public author matrix has known historical analysis and the pair-split experiment is a public-development screen, **not independent SCIENTIFIC_PASS**. This program neither trains the native Yggdrasil architecture nor validates genuine cold memory retention, unknown-family transfer or action-policy causal learning.

## Reproduction and validation

On a read-only local copy of the *exact original-author* `processed_fitnesses.csv` with the pinned Git blob, from this folder:

```sh
node --test test_evaluate.mjs
node reproduce.mjs /path/to/processed_fitnesses.csv
```

`reproduce.mjs` hashes the original input using Git's content-blob SHA1 rule, refuses source drift, recomputes the fixed evaluation, and asserts candidate/control RMSE, bootstrap bounds and classification against the sealed [`result.json`](./result.json). No network, data download, file mutation or science owner execution.

Source-free engineering test executed in a sandboxed V8 isolate against the exact GitHub `evaluate.mjs` blob and associated test blob **PASS**; 80-gene generated engineering fixture, not a research dataset. Full Windows/Linux candidate regression, exact-source independent scientific replication and native owner acceptance **NOT RUN**.

### Engineering / science / deployment

- **ENGINEERING:** comparator and source-free focused test executed; source, code and result bound to Git blobs; full candidate regression/independent qualification **UNVERIFIED**.
- **SCIENTIFIC:** `PUBLIC_DEV_NO_GO`, not `SCIENTIFIC_PASS`; retain this falsification and stop further score-directed changes on this cohort.
- **DEPLOYMENT:** NONE; accepted Yggdrasil main and original owner [#426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) unchanged.
- **Next experiment:** independent source with actually new target/family and matched information/capacity/cost; abandon rather than tune this specific two-hop residual program on consumed public DEV. Real native Yggdrasil weight integration would require its own qualified owner acceptance.
