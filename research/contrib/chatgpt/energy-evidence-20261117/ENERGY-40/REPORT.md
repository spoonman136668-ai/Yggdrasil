# ENERGY-40 — Classical energy minimization at larger graph sizes

**Date:** 2026-11-18. **External synthetic falsification.** **Outcome: `DEVELOPMENT_NO_GO` — 5 of 8 prospective gates PASS.** No native Yggdrasil training, tokenization/transformer integration, official research-loop action, scientific acceptance, merge, or deployment.

## Scientific question

ENERGY-39 found that a fixed classical Metropolis annealer hit the mathematically certified global optimum in 36/36 *small* n=14/18 constrained XOR2 graphs, but vectorized exhaustive enumeration was faster and the annealer did not beat good greedy control by its frozen +10 percentage-point margin. ENERGY-40 moves beyond tractable enumeration to three new graph topologies at **32, 64, and 96 binary variables**, and compares solution quality against multistart greedy descent, iterated local search, random sampling, and a time-limited HiGHS integer-programming optimizer.

These are graph **optimization** experiments. No weights were trained. The algorithm has no persistent memory, no causal intervention learner, no unfamiliar semantic transfer, and no proof of native/Yggdrasil intelligence. The planted graph assignment is withheld from every solver and is **not necessarily optimal** after edge frustration.

## Prospective freeze and custody

- Archive baseline: `3624e7ee850d6abde7430d35f110a832dafefd73` on research archive PR #1210.
- Original scorer and independent auditor were deposited as compressed byte-exact sources first in commit **`6bf5845dab5d338936dda66da4290438eaf44a0c`**, source SHA-256 `0b0f432189d0bd41008bfe3bc90a97ccc5f3a4931d512bdbd600f53c071b4f49`, audit SHA-256 `9c2d2bb0e779d2b3e70e1e6cd8aca5413b8027a1c203d93a62589c081c1ae780`.
- Full eight-gate preregistration was committed **before any primary scoring** in commit **`0187800e53f5ca08d570f42774c90d875fb83222`**. Source SHA, seeds, graph identity, controls, CPU budgets, evaluation and stop policy were fixed.
- Only the excluded smoke seed `99703` was run before freeze (three graphs, **1,617 independent checks PASS**). New primary seeds **8303, 8311, 8329** each contributed one world for each graph family (`erdos`, `modular`, `lattice`) and size (32, 64, 96): **27 primary worlds**.
- Each world has a ring connectivity backbone and two additional ranked edges per variable, hence `3n` weighted XOR2 constraints. Hidden signed targets are produced from synthetic SHA256 bits with an independent 22% frustration condition and weights 1–4. All five solvers receive the identical public constraint list, never the planted bits.

## Frozen solvers and computational budgets

Metropolis annealing uses **12 seeded random starting assignments and 48 sweeps**, testing each variable once per sweep per start (12 × 48 × n bit-flip proposals). Temperature decreases geometrically from 3.0 to 0.04; best encountered feasible state is recorded. Conventional multistart **greedy** uses 12 identical initial states, 48 greedy sweeps and only improving flips. Stronger **iterated local search (ILS)** uses the same initial states and sweeps with 10% state perturbations every eight sweeps. Random baseline samples 588 complete independent states per graph, with its measured runtime but a **different computational workload**. The exact reference is HiGHS mixed-integer linear programming with parity constraints, a **0.35-second time limit per graph** and zero MIP gap when certified.

This is **not** a strict equal-wall-clock or equal-CPU-cycle comparison against HiGHS or random search. Per-policy time is graph-generation elapsed plus that solver's elapsed, summed over the same 27 graphs; importing Python, external CI, host provisioning, scientific acceptance and physical Joules are excluded.

For n ≥32 no exhaustive oracle was run. A **best observed** result means the minimum verified *feasible* objective across all methods, *not a globally proven optimum* unless the HiGHS solver returned an exact certificate and matching primal/dual values. HiGHS certification metadata and every emitted candidate's integer violation cost were independently verified in the external auditor.

## Frozen primary result

| Solver | Cases reaching lowest observed feasible cost / 27 | Total excess integer violated weight | Cumulative generation + solver elapsed |
|---|---:|---:|---:|
| **Energy Metropolis annealer** | **20 (74.1%)** | **20** | **1.0351 s** |
| Strong conventional ILS | 13 (48.1%) | 87 | 0.7702 s |
| Multistart greedy | 5 (18.5%) | 247 | 0.6569 s |
| Random state sampling | 0 (0%) | 2,670 | 0.1534 s |
| HiGHS exact MILP with time cutoff | 17 (63.0%) | 1,717* | 6.9697 s |

*The HiGHS excess includes only cases where the time-limited solver produced a feasible incumbent; a noncertified incumbent is not an exact optimum. There were **17 certified exact optima**, 10 uncertified cases, and the annealer matched only **10 of those 17 mathematically certified optima**.*

Annealer vs multistart greedy: **22 strict wins, 0 strict losses**, 5 ties. Annealer vs stronger ILS: **13 strict wins, 2 strict losses**, 12 ties. Therefore its locally measured optimization advantage over these methods is real on this frozen source cohort, but **not** evidence that it finds globally optimal configurations reliably.

Best-observed hits by topology (9 graphs per family): Erdős 9/9, lattice 6/9, **modular 5/9**. The n=96 size slice met best-observed cost on **6/9**. Total positive graph constraint weights sum to 12,998, so annealer's total excess of 20 corresponds to a **0.154% weighted gap** relative to best observed across this cohort. That aggregate masks seven missed optima or feasible bests and is not an exact optimality guarantee.

## Frozen eight-gate decision

| Prospective gate | Result |
|---|---|
| Annealer matches best feasible on ≥80% of 27 graphs | **FAIL — 20/27 = 74.1%** |
| Net strict wins over greedy ≥20% of worlds | **PASS — (22−0)/27** |
| Net strict wins over ILS ≥10% of worlds | **PASS — (13−2)/27** |
| Aggregate excess weight / total constraint weight ≤1% | **PASS — 20/12,998** |
| Annealer matches best observed on ≥2/3 of n=96 worlds | **PASS — 6/9** |
| Annealer matches best observed on ≥2/3 of every graph family | **FAIL — modular 5/9** |
| Measured generation+solve elapsed ≤1.5× ILS | **PASS — 1.0351/0.7702 = 1.344×** |
| At least three exact MILP certificates and annealer matches **every** certified optimum | **FAIL — 10/17** |

**5 PASS / 3 FAIL → DEVELOPMENT_NO_GO.** No post-result tuning of restarts, sweeps, temperature schedule, source topology, compute budget, primary seeds, thresholds or classification.

## Independent audit and replay qualifications

**ENGINEERING / local external scorer: PASS.** The independently authored auditor reconstructed all 27 SHA256-keyed graphs with a separately implemented generator, recalculated each solver's emitted feasible assignment's weighted constraint cost, reproduced every seeded local optimizer trajectory, recomputed every decision gate and cross-checked all available MILP exact certificates. **14,283 local audit checks PASS** on the primary result. Audit results and original full scored file are deposited compressed, with exact Git objects and SHA256s in `provenance.json`.

**Deterministic replay: MIXED.** One unchanged-source replay reproduced **all anneal, greedy, ILS and random costs and assignments byte-for-byte across all 27 cases**. Three **noncertified, time-limited HiGHS** results differed between runs: two dual bounds changed and one feasible incumbent changed. Both runs certified exactly 17 worlds; they retained the **same eight gate decisions and DEVELOPMENT_NO_GO classification**. Do **not** claim a fully deterministic primary record, or treat an uncertified HiGHS incumbent as exact. `replay_diagnostics.json` retains exact case IDs and differences. The original immutable primary result, rather than the second replay, is the scored scientific record.

**ARCHIVE INTEGRITY / local PASS.** `verify_archive.py` checks byte-exact compressed and original source hashes, Git object identity, the complete original timing-bearing primary result, all 27 CSV case records, the 14,283-check audit and the HiGHS certificate/primal equality. Every CSV receipt includes exact graph hash, every solver's feasible assignment and cost, exact status, certification, and policy-component times. `case_receipts.csv` has **27 rows** and SHA-256 `3984d09bcaffdff5c6c15df045a1ca4d613635643f28bca794f6e6b3456c5f6c`.

**Native engineering and science acceptance: UNVERIFIED.** This is external research in the isolated contributor lane, not Yggdrasil's full Linux/Windows native regression, protected-science first-use, measured causal learning, or owner acceptance. The existing draft PR has repeatedly failed the repository G29 code-atlas indexed-file check on both OSes before downstream regression tests; that infrastructure failure is separate from the valid synthetic scientific NO-GO. No approved main/model/accepted-ref/control-plane modification or deployment was undertaken.

## Reproduce (source SHA and exact archive)

From a pinned GitHub checkout containing this directory, with Python 3.13.5, NumPy 2.3.5 and SciPy 1.17.0, decompress `experiment.py.bz2` and `audit.py.bz2`, verifying SHA-256 values above. The read-only archive custody verifier does **not** rerun primary seeds:

```bash
python -B verify_archive.py
```

To reproduce scoring and independently recalculate all cases on an isolated research CPU, not an official Yggdrasil runner:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out new_scored.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py new_scored.json --out new_audit.json
```

Only local-search heuristics are expected to replay exactly. The time-limited MILP solver's noncertified results, wall timings, and therefore best-observed reference can vary; never silently substitute a replay into the frozen primary.

## Research conclusion and stop decision

Classical energy annealing improves over greedy and ILS on this small, known weighted XOR2 grammar **without training**, but misses too many certified optima and is inconsistent on modular graphs. This is **not** a scientific demonstration of transferable causal intelligence or an efficiency win over a fully qualified optimal exact solver.

**Stop this frozen candidate at NO-GO.** A meaningful future experiment would need a genuinely different independent causal/compositional task, an *explicitly compute-equalized* conventional control and verified retained learning across worlds, rather than more annealing-temperature tuning against consumed seeds. Archive evidence is first-class even when negative; neither the core model nor autonomous research loop is changed.
