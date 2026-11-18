# ENERGY-38 — Verified causal-effect learning per CPU second

This is **isolated, source-free synthetic external development**; no native Yggdrasil checkpoint, accepted ref, controller, runner or merge is authorized.

The two pinned Python sources are uploaded as bzip2 binaries to retain byte exact provenance. Decompress `experiment.py.bz2` to `experiment.py` and `audit.py.bz2` to `audit.py`; verify decompressed SHA-256 against prereg.json before running. No old ENERGY-33–37 seeds may be reused for ENERGY-38 primary scoring.

The experiment compares learned sparse-energy intervention selection and training against fully fitted OMP12, Ridge, decision-tree, classical OMP uncertainty, ridge leverage, diversity and random selection on fresh 8-bit causal systems. Primary held scoring is **exact signed intervention effect** on disjoint action pairs, not merely classification. Policy cost includes source generation, action selection and final model training/prediction; whole experiment time is recorded separately.

```bash
python - <<'PY'
from pathlib import Path
import bz2,hashlib
for name in ('experiment','audit'):
    b=bz2.decompress(Path(name+'.py.bz2').read_bytes())
    Path(name+'.py').write_bytes(b)
    print(name,hashlib.sha256(b).hexdigest())
PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out scored.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py scored.json audit_result.json
```

The experiment is not proof of general causal intelligence, transferable native Yggdrasil learning, or energy superiority. Even a development pass cannot promote code or research-loop state.
