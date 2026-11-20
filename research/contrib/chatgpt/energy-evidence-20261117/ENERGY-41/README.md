# ENERGY-41 — Cross-world reusable constraint-reliability transfer

This experiment is independent, source-free synthetic **external evidence only**. It does not use or change a native Yggdrasil model, research controller, scheduler, queue, runner, main, or accepted research state.

The learned sparse structured-energy model fits **three global edge-reliability coefficients** from labeled small graph demonstrations. Those three coefficients are frozen within a seed cohort and transferred, without updating, to held-out graphs with new node counts (36,52) and one previously unseen topology (lattice). The hidden test assignments and held relational queries are available only to the scoring function. Matched supervised controls: empirical Bayes group frequencies, regularized logistic regression, uniform weights and shuffled group-label negative; known true group reliabilities as a **non-information-matched diagnostic ceiling**, excluded from the strongest-control gate. Every arm shares an identical, fixed multi-start local search solver and equivalent supervised training data.

To reproduce with Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0:
```bash
python - <<'PY'
from pathlib import Path
import bz2,hashlib
for fn in ('experiment.py','audit.py'):
    data=bz2.decompress(Path(fn+'.bz2').read_bytes())
    Path(fn).write_bytes(data)
    print(fn,hashlib.sha256(data).hexdigest())
PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out replay.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py replay.json --out audit_replay.json
```
Verify SHA256 against frozen preregistration. Evaluation outcome, provenance, reaggregation, and deterministic semantic receipts will be deposited under this directory after the preregistered primary run. No branch merge or scientific first-use is implied.
