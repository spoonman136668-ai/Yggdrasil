# ENERGY-14 — CRAM reference-method verification and disjoint CPU smoke

**Date:** 2026-11-17. **Final development cohort:** ENERGY-14B. **Status:** engineering PASS locally with scope limitations; scientific faster-reasoning hypothesis NOT DEMONSTRATED / NO-GO on this task; no native qualification or deployment.

## 1. Paper, upstream source, and exact scope

Paper: Hoover, Blayney, Whittington, *Classical Energies Learn to Reason 1,000× Faster than Looped Models*, arXiv:2611.17309v1 (2026-11-12). Upstream repository `Prefrontal-AI/CRAM`, pinned commit `62bbe830c7d6f87f2ba18f30a28039258b986454`.

This work **does not run the upstream source code, dataset, checkpoints, GPU kernels, or original neural baselines**. It is an independent PyTorch/NumPy CPU **math-port** of the published Maze-Unique algorithm: 4 symmetric 2×2 local pair-cost tables and 2 open-cell biases (18 trained numbers), zero initialization, 20 SGD/momentum/cosine pseudolikelihood updates directly on solved boards, followed by random focused Gibbs updates at temperature zero from the all-open board. Training does not differentiate through inference. The source's full test suite (`91 tests`), official EqR 30×30 puzzle split, H200 timings, exact GPU/CPU parity, and official HRM/TRM/GRU comparisons are **not** reproduced here.

This method was examined for its potential relevance to independently native, tokenless Yggdrasil. It does not establish the learning of unknown causal mechanisms or persistent memory.

## 2. Custody: invalid first cohort preserved, independent replacement

Original ENERGY-14 (A): After scoring its 192 generated test mazes, the independent audit detected **one repeated test maze across two seeds**. A subsequent pre-declared provenance investigation detected train/test overlaps on two seeds, invalidating the train/test disjointness criterion. The first scored 192/192 is **INVALID evidence** and is not used as scientific support. Its frozen protocol, source, result, and original audit failure remain in the evidence package.

ENERGY-14B is a **separately preregistered, freshly seeded** cohort with seeds 67/79/101, with no changes to the 18-parameter model or its 20-update training/search hyperparameters. The revised generator rejects duplicate full input boards across **all new training, validation and test splits**, all three scored seeds and the separate smoke seed; it also rejects all previously observed ENERGY-14(A) train/validation/test and smoke boards. The new audit verifies collision exclusion in a fresh process. The model, protocol, and audit source hashes were frozen before scoring and verified unchanged after a deterministic repeat.

## 3. Results on corrected 14B cohort

Training: 256 independently generated solved 11×11 perfect random mazes per seed; validation 32 per seed; scored test 64 per seed (192 total). Perfect mazes have exactly one simple path between S and G, which a standard breadth-first search can find directly. All arms use the same input maze, and the true path is only provided to the energy model at train time (not at inference).

| Seed | CRAM math-port full-board exact | Same-energy synchronous updates | Exact graph BFS | Fixed points reached |
| --- | ---: | ---: | ---: | ---: |
| 67 | 64/64 | 64/64 | 64/64 | 64/64 |
| 79 | 64/64 | 64/64 | 64/64 | 64/64 |
| 101 | 64/64 | 64/64 | 64/64 | 64/64 |
| **Total** | **192/192** | **192/192** | **192/192** | **192/192** |

A zero-energy untrained ablation solved 0/192. The learned model exactly predicts these *small procedural-maze* paths after learning only the spatial pair energy, but the result is not a reproduction of 30×30 Maze-Unique, an unfamiliar causal relationship, or a heldout original benchmark. The same-energy synchronous update also solves all test cases; CRAM's focused search does not uniquely account for these successes.

**Local CPU whole-process times, summed over all three seeds:**

| Method / stage | Wall elapsed |
| --- | ---: |
| CRAM math-port fit (3×20 SGD steps) | 0.08670 s |
| CRAM focused-Gibbs inference (192 cases) | 3.85723 s |
| **CRAM fit + inference** | **3.94393 s** |
| Same-energy synchronous inference (192 cases, fitted weights reused) | 2.60861 s |
| Exact BFS inference (192 cases, no fit) | **0.01600 s** |

This is **~246.5× slower than exact BFS whole-process**, not faster, and the Gibbs inference is about **1.48× slower** than synchronous updates on the same learned energy (excluding common fitting). These numbers are direct, non-amortized local Python/NumPy CPU measurements; do not extrapolate to Triton, optimized libraries, GPU or HRM/TRM. Training/validation heldout and scoring cannot be compared with the original H200 42/132ms headline.

## 4. Audits and repeatability

- 18-parameter count/zero initialization; tests of independent explicit pair energy versus PyTorch convolution energy, local flip-energy deltas, and local currents passed before scoring.
- Corrected 14B smoke: 8/8 exact; **2,922 audit assertions PASS**.
- Scored cohort: **5,148 audit assertions PASS**. Independent tensor-vs-explicit pair energy, different BFS route reconstruction and label scoring; deterministic replay of the stored weights and predictions through the same generator and Gibbs code (not an independent complete solver).
- All new train/validation/test boards are bytewise distinct from one another and from earlier ENERGY-14(A) boards; repeated test-case SHA256s are checked.
- A second complete scored run reproduced all 192 prediction hashes, all 3 fitted tensor sets and the per-case objectives/moves exactly; elapsed wall times differed normally.
- Frozen SHA-256 checks passed after both runs. Original source hashes pinned in `prereg.json`. Local runtime: Python 3.13.5, torch 2.10.0+cpu, NumPy 2.3.5, one CPU thread, CUDA unavailable.

**Auditing limitation:** the auditor independently checks the energy and BFS target but intentionally reuses the frozen data generator and Gibbs search to reproduce decisions. Thus, numerical and scoring consistency is validated, not external upstream behavior equivalence or a scientific acceptance test.

## 5. Qualification

- **ENGINEERING: LOCAL PASS** for 18-param energy math-port, masked pseudolikelihood fit, zero-temperature focused search, disjoint dataset, numerical audit and deterministic replay. The invalid first cohort remains preserved.
- **SCIENTIFIC: NO-GO on the measured faster-reasoning claim.** Exact BFS is far faster at equal 100% accuracy, and fully converged original looped-model comparisons are absent. This synthetic maze workload is too easy for a decisive intelligence claim.
- **DEPLOYMENT: NONE.** No modifications to accepted Yggdrasil main, CKAD PR #1182, ENERGY-01 PR #1201, Forge, any runner/scheduler, original-source first-use, or promoted model. No CI/full native regression was run.

## 6. Reproduce without external services

From this `ENERGY-14B` folder using Python 3.13+ with CPU torch and NumPy:

```bash
sha256sum -c FROZEN-SHA256.txt
python experiment.py --smoke --output another-smoke.json
python audit.py --input another-smoke.json --output another-smoke-audit.json
python experiment.py --output another-scored.json
python audit.py --input another-scored.json --output another-audit.json
```

Wall-clock timing is environment dependent; model tensors and per-case prediction hashes are the stable repeatability targets. Input generation remains synthetic and source-safe.

**Decision:** End the local toy-maze escalation. A *genuine paper reproduction* requires checking out the pinned original CRAM repository, setting up CUDA/Triton and pinned datasets on the permitted project GPU, running its 91-test suite and checkpoint evaluator, and then matching published baselines with original recipes and full train+inference accounting. Nothing in this 14B local result authorizes that separate GPU or scientific first-use action. Yggdrasil integration remains unqualified.