# ENERGY-45 — Contradiction-gated replacement of obsolete causal supports

Independent **synthetic external** Yggdrasil research, not native model training, autonomous controller activity, first-use scientific acceptance or deployment.

One persistent learner first discovers four factor supports from 96 old-context witnessed action–consequence interventions. It then receives 96 new-context witnessed interventions. A learned contradiction gate selects a single old factor to remove and a new candidate factor to install in its context-specific new model; the old context predictor remains immutable. Selection uses 72 new-context labels and a separate 24-label validation subset, with frozen MSE-improvement trigger >=0.12, followed by refitting selected new-context coefficients on all 96 observed new labels.

**Critical no-change negative control:** One quarter of worlds retain exactly the old causal law but shift nuisance-cue correlations. The gate must avoid changing these. Changed worlds have one true old-only and one true new-only hidden factor.

The fixed finite grammar has 364 unary, pair/triple parity and pairwise AND features over 12 binary intervention bits. This does NOT discover arbitrary previously unknown operators or demonstrate general intelligence.

11 arms: gated replacement, unconditional replacement, conventional 2-factor OMP delta, independent new-context OMP4, conventional cumulative OMP structural memory, full OMP7, ElasticNet, Ridge, 60-tree forest, unchanged old model, and shuffled-label negative. All use exactly 96 old and 96 new labeled actions; disjoint old/new/cold held samples are evaluator-only. Three disjoint primary seeds 8803,8819,8831; 4 world IDs × 3 families × 3 seeds = 36 worlds. Excluded smoke seed 99847 checked 6 worlds and 25,713 independent comparisons PASS before freeze.

## Source custody and reproduction

`source.tar.br` stores **exactly two pre-primary Python source files**, scorer `experiment.py` and independent auditor `audit.py`. Brotli-compressed deterministic tar SHA-256 `0951c0cb804c3f4bdd1ecf910926bb0b59d59007c9615e35c5aefd0cbb7f13e7`; uncompressed tar SHA-256 `7cfaa53341b6a29708133c10492e0a8bc06fcc4db795537eb0887c0e7f7484e3`. Original Python SHA-256 values: experiment `0f57e0ef01f69cfc94e6b31b355d628e27813bcbaf454d6c88f1eac643d77718`; audit `947a47d93085c7478687d183edc8da7dc63a4ae56b8e6ac4bbc3b66e58c28213`.

The unchanged, SHA256-verified source oracle from ENERGY-43 is loaded read-only: `../ENERGY-43/experiment.py.bz2` and `../ENERGY-43/audit.py.bz2`. These must be present for reproducibility.

```bash
python - <<'PY'
import brotli,tarfile,io,hashlib
from pathlib import Path
b=Path('source.tar.br').read_bytes()
assert hashlib.sha256(b).hexdigest()=='0951c0cb804c3f4bdd1ecf910926bb0b59d59007c9615e35c5aefd0cbb7f13e7'
with tarfile.open(fileobj=io.BytesIO(brotli.decompress(b)),mode='r:') as t:
    for member in t:
        assert member.name in ('experiment.py','audit.py') and member.isfile()
        Path(member.name).write_bytes(t.extractfile(member).read())
PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --smoke --out excluded_smoke.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py excluded_smoke.json --out excluded_smoke_audit.json
```

**Primary must not run before a separate GitHub preregistration commit.** Its frozen gates, seeds and stop criteria appear in `prereg.json` after source custody. Repository CI, scientific acceptance and native runtime full regression remain independent qualifications.
