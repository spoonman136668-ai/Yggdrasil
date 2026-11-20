# ENERGY-37 — One-pass causal energy witness selection

Isolated synthetic development successor to ENERGY-36. All candidate policies see 80 witnessed old context actions and may choose 16 new actions from a common pool **before** seeing their outcomes. Each fully retrained model then sees exactly 96 acquired labels, and held consequences are disjoint. No native Yggdrasil weights, runner, controller, accepted refs, or autonomous loop are changed.

Primary source and independent auditor are immutable bzip2-compressed files `experiment.py.bz2` and `audit.py.bz2`. Their original SHA-256 identities and preregistered outcomes are in `prereg.json`. Decompress them to run; use Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0. This archive PR is evidence only.

```bash
python - <<'PY'
from pathlib import Path
import bz2
for n in ['experiment.py','audit.py']:
    Path(n).write_bytes(bz2.decompress(Path(n+'.bz2').read_bytes()))
PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out scored.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py scored.json --out audit_result.json
```
