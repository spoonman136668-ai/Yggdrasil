# ENERGY-39 — Compositional classical-energy constraint solving

External **synthetic development evidence**, not native Yggdrasil training. Frozen SHA256-keyed connected XOR2 frustration graphs in three previously untested graph topologies, n=14/18; compare vectorized classical annealing against exact enumerative reference, scipy HiGHS MILP, same-budget zero-temperature greedy descent, and random sampling. All solvers get exactly the same public weighted constraints and no planted assignment. Measure optimum-hit rate, energy excess, actual measured component wall time (graph generation + solve). No distinct causal learning or weight training is claimed.

Sources stored bzip2-compressed for byte-exact Git custody. Check SHA256 identities in prereg.json, decompress `experiment.py.bz2` and `audit.py.bz2`, then:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out result_full.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py result_full.json audit_replay.json
```

The eight frozen gates (quality, stronger controls, family/size generality, runtime, exact MILP certification) determine DEVELOPMENT_GO or DEVELOPMENT_NO_GO. Scientific acceptance and any model integration require separate native qualification. No accepted-ref, controller, scheduler, runner, or production changes.
