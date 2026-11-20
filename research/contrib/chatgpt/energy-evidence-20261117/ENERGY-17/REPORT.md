# ENERGY-17 — Pretrained CRAM Maze-Unique weights: out-of-distribution maze transfer

**Classification:** isolated synthetic development qualification; not the original CRAM official evaluation, not native Yggdrasil scientific first-use, and not an authorized GPU benchmark.

## Plain-English outcome

Three *actually trained* CRAM Maze-Unique checkpoints, downloaded via the connected GitHub repository and represented as their 18 exact float32 parameters, each recovered the correct path through 72 newly generated, unfamiliar, perfect mazes. All 216 checkpoint × maze cases were correct; both negative controls scored zero. However, the unoptimized Python/NumPy energy-search implementation took roughly 105 times as long as ordinary breadth-first search on the same simple mazes. This is limited evidence of structural transfer, **not** faster reasoning or general causal intelligence.

## Source and custody

- Original repository: `Prefrontal-AI/CRAM` at pinned commit `62bbe830c7d6f87f2ba18f30a28039258b986454` (Apache-2.0 per upstream README).
- Source checkpoint files: `checkpoints/maze-unique/seed{0,1,2}/model.pt`.
- The GitHub connector returned base64-encoded original PyTorch ZIP archives. The raw 16 floats in `model/data/0` (four 2×2 neighbor-pair tables) and two floats in `model/data/1` (open-cell bias) were read as little-endian float32, without executing untrusted pickle. Original source blob SHA-1 values and the manifest's declared SHA-256 are recorded in `checkpoints.json`. The entire source archive bytes are not included; manifest SHA-256 is **upstream-asserted**, not independently recalculated here.
- The source-free CPU implementation explicitly reproduces the published local pair cost `sum_{i,d} T_d[state_i,state_{i+d}] - sum_{free i} b[state_i]` and focused zero-temperature Gibbs moves that flip a nonminimum-energy open cell. This is **not** a byte-for-byte execution of upstream CUDA/Triton code or its exact random-number generator.
- ENERGY-15's sampler discrepancy is not involved here: **no training was performed**. The original pretrained weights are used unchanged.

## Frozen cohort and controls

- Frozen scripts / original checkpoint floats / preregistration and smoke outcomes are SHA-256 pinned by `freeze.json` before `scored.json` was created.
- New generated trees: 24 mazes each at 15×15, 21×21, 31×31, using seeds `173101 + case`, `173211 + case`, `173311 + case`, respectively (72 different mazes; 216 model evaluations).
- Every maze is a DFS-generated spanning tree of corridors with a unique S–G path. Ground truth and the exact baseline derive from BFS; the generator is unrelated to the authors' EqR benchmark distribution.
- Initial predicted board: every passable cell on, wall off, S/G on. Energy search: one uniformly chosen dissatisfied cell per move, zero temperature, cap 20,000 moves. Same fixed search budget for all models.
- Negative controls: invert every trained energy coefficient, and predict all open cells as on. Controls are diagnostic only; neither is a capacity-matched neural learner.
- Pre-registered OOD accuracy objective: >=95% exact board overall and >=90% at each size. Pre-registered efficiency objective: at matched exact-board accuracy, CPU energy-search time <=2× same-process exact BFS time. Accuracy passes; efficiency fails.

## Scored results

| Size | Cases | Exact board correct | Mean Gibbs moves | Energy search CPU (s) | BFS CPU (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 15×15 | 72 | 72 | 48.0 | 0.349 | 0.0057 |
| 21×21 | 72 | 72 | 120.5 | 0.806 | 0.0083 |
| 31×31 | 72 | 72 | 264.3 | 2.383 | 0.0197 |
| **Total** | **216** | **216** | — | **3.538** | **0.0336** |

- Exact board accuracy: original checkpoints **216/216**, inverted-weight diagnostic **0/216**, all-open diagnostic **0/216**, exact BFS **216/216**.
- Every reported search stopped at a local minimum within the move budget; no reported uphill moves. Direct independent numerical audits confirm local stability and final energies.
- Measured energy-search / BFS inference cost ratio **105.16×**, at equal exact-board accuracy. Both sides are single-process Python/NumPy wall clock; no GPU optimized implementation, no model-loading or training cost, and no original official dataset. This is **not** a comparison to HRM/TRM or to upstream optimized CRAM timings.
- Evaluations of three checkpoints on identical mazes are correlated; there are 72 independently generated maze inputs, not 216 independent problem draws.

## Engineering verification and audit amendments

- Pre-score, separate-disjoint-smoke arithmetic checks: **201 PASS**, proving that flipping a free cell changes explicit energy by exactly its local-field difference. Development smoke on six small mazes × three checkpoints: **18/18**.
- **Independent post-score audit PASS — 56,685 assertions**: verifies the frozen file hashes, independently recreates all 72 mazes, independently proves each maze is a tree with a unique BFS path, independently verifies all 216 ground-truth and prediction bitmaps and energies, checks all local fields at predicted boards, and completely replays nine trajectories using a slow independent search.
- The first two independent-audit invocations failed only due to auditor defects (bitwise operator on token integers and incorrect `np.unpackbits` input type). Both were repaired in `audit.py` **after scoring** without changing any frozen file; `AUDIT-FIRST-FAILURE.md` preserves the precise corrections. Do not misclassify those as experimental failures or conceal the correction.

## Qualification and next direction

| Layer | Status | Interpretation |
| --- | --- | --- |
| Engineering — source-ported mathematics and independent score audit | **PASS** | Original learned weights and reproducible inference are demonstrated locally. |
| Scientific — transfer across new maze sizes in a familiar structural family | **PASS, bounded** | 72/72 distinct synthetic mazes solved by all three original checkpoints. |
| Scientific — reduced compute at matched accuracy | **FAIL** | CPU energy search ~105× slower than BFS. |
| Scientific — new causal laws / persistent native reasoning | **UNVERIFIED** | Maze path inference is not causal discovery, and weights were pretrained. |
| Official upstream benchmark on pinned datasets, CUDA/Triton | **NOT EXECUTED** | Requires a separately authorized GPU runner and original code. |
| Native Yggdrasil regression, scientific first-use, merge, deployment | **NONE / UNVERIFIED** | No Yggdrasil source, controller, runner, CI, first-use data, or research loop was modified. |

The next decisive comparison remains official source-pinned upstream CRAM + fully qualified looped controls on an authorized GPU, followed by a separate native Yggdrasil causal-learning test. Do not interpret these maze results as justification to integrate CRAM into the native architecture.

**Last verified repo checkpoint:** `spoonman136668-ai/Yggdrasil main = 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; ENERGY-01 draft PR #1201 head `69123bc92cad8bc14fe6596f42d9b2f4e71a2542` still unmerged; CKAD draft PR #1182 head `5df8dbf506027b914f66e19441376d1347a3e09d` still unmerged.