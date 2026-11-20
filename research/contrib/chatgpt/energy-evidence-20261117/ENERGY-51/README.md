# ENERGY-51 — Higher-order causal factor learning outside the old grammar

External contributor-run synthetic study for Yggdrasil, **not native model training**. This is the next, explicitly disjoint test after the negative out-of-grammar intervention-selection ENERGY-50 screen. No Forge/Yggdrasil owner, runner, scheduler, queue, accepted ref, main, or deployment changes.

A sparse structural-energy learner sequentially models 72 old-context witnessed consequences and 72 new-context consequences. The OLD predictive checkpoint is frozen, while up to five corrective high-order Fourier supports are discovered for NEW and COLD contexts using new factual outcomes. The factor dictionary is all 1–5-way parity terms over **12 observed action bits** (1585 candidates): this is **a provided finite grammar**, not free-form causal operator invention. Hidden causal factors include 4/5-way parity, 5-way majority, modulo-3, and conditional gates; some are representable as combinations but not individually named by the model. Two nuisance action cues switch correlations, and COLD cues are independently randomized. Every world has 360 disjoint 10-bit randomized intervention assignments (72 old train, 72 new train, 72 old/new/cold each held).

Strong controls get the *same factual labels*: fully trained separate-context OMP6 and ElasticNet on the identical 1585-feature basis, two fully trained kernel-ridge variants, and 64-tree ExtraTrees; negatives are frozen-old no-adaptation and shuffled new labels. The source-free independent audit reconstructs all held hidden consequences, checks assignment disjointness and factor columns, and refits every arm to verify all predictions and metrics. Scorer and auditor share the original generator and sklearn estimator library; this limits true independence.

**Frozen source identities** (decompress before running):
- `experiment.py.bz2`: SHA256 `25499ac492c10bacc9392eb97588cb862e1493f1d36293440184fd2c032a51d5`; raw Python `76427457e5452585d07fc23b05e5a0812717d1e3d6a4ee2848cf982cde6b9c20`.
- `audit.py.bz2`: SHA256 `1871246adadcfc4d2410adecdd132b12922c1a604a76929f721fb900b57c91ae`; raw Python `73e27052ac44025dbf6deb509df623008c0c3dc055ec99756d640196e2f97483`.

Run on CPU with Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0. Set `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`.

```bash
python -c "import bz2; from pathlib import Path; [Path(n).write_bytes(bz2.decompress(Path(n+'.bz2').read_bytes())) for n in ('experiment.py','audit.py')]"
python -B experiment.py --primary --out scored.json
python -B audit.py scored.json --out audit_result.json
```

Exactly **one frozen primary** on seeds 9311/9323/9341 is allowed after the separate preregistration commit. The excluded smoke seed was 99971 (3 worlds; independent audit PASS 38,811 checks). The old 364-term ≤3-way grammar is not used in the candidate's predictors; this tests the higher-order representation capacity, not model-agnostic intelligence. Research is read-only with respect to native Yggdrasil.
