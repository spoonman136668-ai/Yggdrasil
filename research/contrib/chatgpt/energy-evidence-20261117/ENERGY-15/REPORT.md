# ENERGY-15 — Upstream CRAM fidelity and GPU-readiness gate

**Scope:** Read-only provenance and protocol audit; no new science run or source modification. 2026-11-17.

## Outcome

- **ENGINEERING — PASS (read-only preflight):** 31 deterministic checks; all 15 prior evidence members match the original ENERGY-14B manifest; the archived ENERGY-14B primary outcome remains 192/192 on synthetic 11×11 mazes, unchanged.
- **SOURCE FIDELITY — FAIL for ENERGY-14B as a literal upstream training reproduction:** The archived math-port draws mini-batches with replacement; pinned upstream CRAM `experiments/maze_unique.py` uses a fresh random permutation per epoch, consecutively yields full batches and discards the tail. With an otherwise fixed 256-example dataset, 20 batches of 64 produce five exposures per example upstream; the local port gives uneven exposures and omits two examples on seeds 67 and 79. The 14B work already disclaimed being an upstream execution, and this finding further explains why its learned weights and timings cannot be used as a reference reproduction. **Do not retroactively repair, retune or rescore 14B.**
- **SCIENTIFIC — UNVERIFIED for the paper:** Not a run of the authors' checkpoint evaluator, EqR mazes, H200 training pipeline, or HRM/TRM/EqR baseline models. No measured training or inference speedup over qualified neural baselines.
- **DEPLOYMENT — NONE:** No modifications to Yggdrasil, Wingless, TTT-Hybrid, FORGE, workflows, runners, branches or accepted state; no original test dataset or first-use was consumed.

## Authoritative sources pinned

- Authors' original code repository: `Prefrontal-AI/CRAM` commit `62bbe830c7d6f87f2ba18f30a28039258b986454`.
- Its `experiments/maze_unique.py` Git blob `ea320ae6a00275d2069628cb944a29abc3baa08b`, specifically `batches` lines 84–90 and `train` lines 104–154.
- Its `REPRODUCING.md` Git blob `13d6e03e52b14f92e197886e22a00a6b66d3395f` and `baselines/README.md` blob `6c0c47b7ae7ac9f33723c9d4dafd6b3bea82f954`.
- Original checkpoint manifest blob `a83c1e42c6f4fc93a4c48cdeeac24a10f531535e`.
- Prior evidence `/mnt/data/ENERGY-14-evidence.zip` SHA-256 `fd3169eb2d14f3d5b96c4fe81e572352d4d97b9a5588b37c88647c3fb3740f45` and prior model source SHA-256 `f874b62345d77bffba7b5e3989bd2eb2e93e1dfa7c3f6e1259d605a0961579fc`.

## Verified sampling discrepancy

| Seed | Local 14B unique training examples sampled (of 256) | Local 14B repetitions per example | Upstream sampler at 256 examples |
|---|---:|---:|---:|
| 67 | 254 | 0–11 | All 256 seen exactly 5 times |
| 79 | 254 | 0–13 | All 256 seen exactly 5 times |
| 101 | 256 | 1–13 | All 256 seen exactly 5 times |

The local audit constructed only sample index vectors from the published algorithms. It did not train, score, consume held-out examples, or use any additional dataset. This test of batch sampling is not proof of what would happen if the original training code were run on the reference benchmark.

## Execution environment / custody

- Available working container: Linux, Python with `torch 2.10.0+cpu`, `torch.cuda.is_available() == False`; `triton` absent. Original source requires Python >=3.12, pinned `torch==2.11.0`, CUDA 12.8 on Linux for its GPU workflows, and an NVIDIA GPU.
- Live state checked from GitHub: Yggdrasil `main` `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; ENERGY-01 PR #1201 `69123bc92cad8bc14fe6596f42d9b2f4e71a2542` draft/unmerged; CKAD PR #1182 `5df8dbf506027b914f66e19441376d1347a3e09d` draft/unmerged. Recheck heads before any future mutation.
- The existing Yggdrasil GitHub workflows include `self-hosted, Windows, X64, yggdrasil, research-only` selectors with tightly prescribed packages; they do **not** prove availability of a CUDA GPU or authorize an unrelated upstream CRAM execution. The source-backed direct runner provisions a fixed Python runtime and isolated requests, not this CRAM package.
- GitHub connection exposes read-only workflow inspection but no authorized, supported native GPU dispatch action for this experiment. The present host cannot run original GPU reproduction. Do not redirect it to TTT-Hybrid's independent GPU runner by assumption.

## Next executable owner-side qualification, when its own authority/custody is verified

1. On the **authorized Yggdrasil-scoped GPU host**, resolve and lock the original repo commit `62bbe830c7d6f87f2ba18f30a28039258b986454`; verify branch cleanliness and upstream file and checkpoint hashes. Record host GPU model, driver, VRAM, `uv.lock`, Python, torch/CUDA and Triton versions, exact input dataset revisions and hashes. A laptop GPU is not an NVIDIA H200; compare methods on the same actual hardware instead of asserting published milliseconds.
2. Qualification before scored experiments: use upstream `uv sync --frozen` and its `uv run pytest` (the original suite advertises 91 tests). A separate checkpoint loader hash check does not consume a test score. Diagnose failures as toolchain, infrastructure or source faults rather than science.
3. Once original-source/test-first-use custody is explicitly certified, prepare the pinned `locuslab/EqR-data` Maze-Unique 30×30 split (`bcb7d45c`) and run `uv run python checkpoints/evaluate.py --seeds 0 1 2 --tasks maze-unique` once. Save exact stdout, output hashes and result files. The repo reports 1000/1000 per seed; this is a claim to verify, not a result of ENERGY-15.
4. If required to test training speed and quality rather than only checkpoint fidelity, run the exact upstream recipe from `REPRODUCING.md` and its three seeds; record all fit stages, warm/cold timing, inference latency, peak memory, energy/FLOPs when measured, data and source custody.
5. Qualify looped comparators separately on the same host, splits, information, objective and compute/time budgets. Upstream `baselines/README.md` specifically discloses that the baseline scripts were moved and syntactically checked but **not re-trained from the published layout**. Do not claim they have been reproduced until they actually pass.
6. Yggdrasil native acceptance and an energy-to-causal-reasoning transfer trial are **separate future qualifications**. No token-based or transformer architecture is imported into its foundation.

**Stop criterion:** Do not promote CRAM, merge ENERGY-01, or alter Yggdrasil/CKAD until original code and source custody, GPU qualification, trained comparators, and separate native-science evidence actually pass. The read-only preflight is complete; original CRAM reproduction remains blocked by an unavailable authorized GPU execution route and protected first-use requirements.