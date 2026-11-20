# ENERGY-42 — Corrected cross-world energy contrastive transfer

This is a **new preregistered experiment**, not a retroactive repair of ENERGY-41. ENERGY-41's mathematical contrastive delta was inverted and its frozen primary classified INVALID; that immutable result remains at the predecessor commit. The **only mechanistic fix** here changes d_g from `-ΔV_group` to mathematically correct `V_group(one vertex flipped)−V_group(truth)`. The auditor now independently enumerates every signed edge violation before/after each training vertex intervention and checks the contrastive delta before validating the trained learner.

The graph generator version and all primary/smoke seeds are new and disjoint. All other learner hyperparameters, data budgets, traditional controls, train/holdout criteria, eight gates and classification policy remain exactly as originally specified for ENERGY-41. We keep the contributor lane strictly outside native Yggdrasil, official CI acceptance, scientific first-use, runner, controller, merger, and deployment authority.

Compressed sources `experiment.py.bz2` and `audit.py.bz2` are byte exact (see frozen SHA in prereg.json). To reproduce:

```bash
python - <<'PY'
from pathlib import Path
import bz2,hashlib
for name in ('experiment.py','audit.py'):
    payload=bz2.decompress(Path(name+'.bz2').read_bytes())
    Path(name).write_bytes(payload)
    print(name,hashlib.sha256(payload).hexdigest())
PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out replay.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py replay.json --out replay_audit.json
```

No native learning or general intelligence claims are warranted from synthetic graph-reliability weights alone.
