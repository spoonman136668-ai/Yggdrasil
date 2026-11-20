# ENERGY-39 — Classical Ising energy on compositional constraint graphs

**Date:** November 18, 2026. **Prospectively frozen synthetic research; DEVELOPMENT_NO_GO.** No native Yggdrasil training, scientific first-use, accepted-ref mutation, autonomous-loop change, merge or deployment.

## Objective and scientific distinction

ENERGY-33–38 failed to establish energy-specific causal-witness learning gains against strong conventional controls. This gate **changes the computational objective**: solve constrained, frustrated binary graph systems rather than predicting causal outcomes. The system is a classical Ising-compatible *optimizer*, not a trained cognitive agent; it does **not** demonstrate native Yggdrasil intelligence, reasoning, cumulative memory, or model learning.

Each graph consists of 14 or 18 binary variables and 3n weighted signed XOR2 constraints. A hidden planted binary assignment generates edge targets, then approximately 22% of parity targets are independently flipped to create frustrated cycles. The planted assignment is **never provided** to any solver. Each solver gets the **same entire public constraint list** and minimizes the exact sum of violated positive integer edge weights. The three graph families are Erdős–Rényi-style ranked pairs, modular clusters and short-range lattice/ring graphs; every graph also contains a cycle backbone for connectivity.

## Source, protocol and custody before primary

- Previous external evidence head: `623926aa14aa615dbfbe56ac9e5d4c28a0fcdc63`.
- Frozen scorer and independent verifier committed **first**, at `f6c7e217e4039a5ed961f5424f1e37d5d7f17657`. Source SHA-256 `7e95b250d63911d4b47c55ab62d67ed2acd06509fd2571095e9c91568e0bf1d8`; committed bzip2 source Git blob `3b3520d641ebd66e6b8fcef1f5e2b96f853a1bcf`. Independent auditor source SHA-256 `61e66de9e444af7c991cb3800b20657e732b064aef35038e58689fc224cd03ec`.
- The full **eight-gate preregistration** was committed **before scoring any primary seed** at `748c7090c02c2905c2854d307cfb60f33f45062e`, with seed identities, graph families/sizes, budgets and negative-stop rule fixed.
- Pre-primary isolated smoke used excluded seed `99563`: three graphs and **62 independent audit checks PASS**. Its results never contributed to primary scores.
- Primary seeds **8209, 8221, 8231** × graph families **erdos, modular, lattice** × sizes **14, 18** × world IDs **0,1** = **36 source graphs**.
- Energy annealer: 12 fixed random initial states, 60 sweeps in seeded variable order; Metropolis updates with temperature 3.0 decreasing geometrically to 0.04. Strong controls: greedy coordinate descent with the **same start and sweep budgets**, 732 uniformly random trial assignments, **HiGHS exact MILP** with a two-second instance budget and zero MIP gap, and symmetry-reduced vectorized NumPy exhaustive enumeration. All solvers use exact graph constraints, **not a learned or transformer/tokenized model**.

## Frozen primary outcome

| Method | Globally optimal / 36 | Total integer excess violated weight | Graph generation + solver cumulative wall |
|---|---:|---:|---:|
| **Classical energy annealing** | **36** | **0** | **0.747 s** |
| **Exact HiGHS MILP** | **36 (all certified)** | **0** | **1.318 s** |
| **Vectorized exact exhaustive enumeration** | **36** | **0** | **0.364 s** |
| Zero-temperature greedy descent | **34** | 2 | 0.571 s |
| Random assignment sampling | **2** | 322 | 0.031 s |

Energy annealing reached the **mathematically verified global optimum on all 36 graphs**, all **12/12** in each family, and **18/18** for 18-variable cases. This is a real small-graph optimization-quality observation, not evidence of learned causal abstraction.

But greedy already solved **34/36**, so annealing improved global-optimum hits by **2/36 = 5.56 percentage points**, below the frozen **+10pp** requirement. Annealing was approximately **1.76× faster** than exact MILP in this particular single-run local implementation (1.318/0.747), falling short of required **2×**. More decisively, the vectorized exhaustive exact solver **ran ~2.05× faster than the annealer**, so the energy solver has no established efficiency advantage even at these small instance sizes.

The random control only found 2/36 exact optima; this passes the preregistered basic nonrandom optimization advantage but does not establish an advantage over competent deterministic or exact solvers. All HiGHS results were independently checked equal to the exhaustive optimum and carried exact solver certifications.

## Frozen gate decision — five PASS, three FAIL

| Frozen gate | Result |
|---|---|
| Energy optimum ≥90% of all graphs | **PASS — 36/36** |
| Energy exact-optimum rate ≥10pp better than greedy | **FAIL — +5.56pp** |
| Energy optimum rate ≥30pp better than random sampling | **PASS** |
| Energy ≥80% optimum separately in all three families | **PASS** |
| Energy ≥80% optimum on 18-variable graphs | **PASS** |
| Energy whole graph-generation+solver wall ≤half of exact enumeration | **FAIL — slower** |
| Energy whole graph-generation+solver wall ≤half of HiGHS | **FAIL — 0.747 vs 1.318 s** |
| All 36 HiGHS instances exactly certified and equal oracle | **PASS** |

**Valid synthetic experiment: DEVELOPMENT_NO_GO.** Do not change annealing temperatures, restart counts, seeds, graph cohorts, or timing rules using these consumed results. The single-run timing figures have no formal confidence intervals; both speed gates fail on observed values even without considering variance.

## Complete independent evidence

- The **byte-exact original primary `scored.json` (151,913 bytes)**, including every graph's full edge list, exact optimum, all solver scores, certification metadata, source-generation timings, solver timings and all eight gates, is in GitHub as `scored.json.bz2` (5,801 compressed bytes). **Original SHA-256:** `a49f7a7b5d2fa2a25336b2e8a02c66080d34e260ef2b7e9fffcda72dceec4aa5`. **Compressed SHA-256:** `b3a1429f63ef8a10ffd78d6fe537693f5b904aeab037d2832e953255cf65d704`; Git blob `2bab37007f136ba0f256adb2f11e4de055c1603d`.
- Complete **36 per-world CSV receipts** in `case_receipts.csv`, 7,033 bytes, SHA-256 `9b377d86b833311687495a1850379fd46e64d691896209813c888e8cadc83653`, Git blob `968c8834a5bbe14c1b708f8e813ea0e8fed1aaa6`.
- Independent, source-free `audit.py` reconstructed all 36 graphs with a separately written generator, reimplemented symmetry-reduced exact optimization, replayed all seeded annealing/greedy/random results, verified all 36 HiGHS reported optima and dual bounds, and recomputed frozen decision gates: **623 checks PASS**. The third-party NumPy RNG and SciPy HiGHS remain shared libraries; this does not claim an independent reimplementation of their internals. Original audit JSON SHA-256 `46e348ec9cb5ed221618869608754c608bbe3021973fe456dd6828a7534baf3a`.
- Exact-source primary semantic replay **PASS**: all non-timing fields byte-identical after the one permitted replay; canonical compact JSON **27,630 bytes**, SHA-256 `ec43d048a193e4611efcaa527c5ba7aa97c3f8fc800f3ba0d479a431db6def13`.
- Local Linux, Python **3.13.5**, NumPy **2.3.5**, SciPy **1.17.0**, CPU-only, single-threaded BLAS. No native Yggdrasil model trained, no native scientific first-use, and no final native Linux/Windows regression performed. G29 repository code-atlas CI is separate and has historically failed on the archive branch; no claim of CI PASS or accepted science follows.

## Reproduction

From the exact archive commit, inside the ENERGY-39 directory:

```bash
python - <<'PY'
from pathlib import Path
import hashlib,bz2
for fn,sha in [('experiment.py','7e95b250d63911d4b47c55ab62d67ed2acd06509fd2571095e9c91568e0bf1d8'),('audit.py','61e66de9e444af7c991cb3800b20657e732b064aef35038e58689fc224cd03ec')]:
    decoded=bz2.decompress(Path(fn+'.bz2').read_bytes())
    assert hashlib.sha256(decoded).hexdigest()==sha
    Path(fn).write_bytes(decoded)
print('frozen source custody PASS')
PY
python -B verify_archive.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out scored_replay.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py scored_replay.json audit_replay.json
```

Use `verify_archive.py` for the deposited **original** primary's byte hashes and 36 receipt equality; replay timing fields naturally vary, so compare the non-timing semantic fields, not raw entire JSON SHA.

## Research conclusion

Classical nonconvex energy minimization is **valid and effective on this small constraint-solving cohort**. But the experiment **does not establish an improvement over optimized exact conventional computation**. The results are limited to at most 18 variables; larger unfamiliar graph structures or genuinely learned causal operators were not tested.

**Stop this frozen candidate at DEVELOPMENT_NO_GO.** An appropriate new, separately preregistered test would examine graph-scaling beyond exact-enumeration's practical regime, with **equal hard CPU budgets** against best available exact and heuristic solvers, and separately measure transfer of reusable constraints if claiming cognitive learning. No operator/controller, accepted-ref, science, model, or deployment state changes are justified by this archive.
