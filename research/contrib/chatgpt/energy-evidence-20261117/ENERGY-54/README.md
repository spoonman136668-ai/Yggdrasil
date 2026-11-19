# ENERGY-54 — Out-of-grammar expected-information acquisition

**External source-free synthetic research only**, archived in the existing draft Yggdrasil PR #1210. The source does not train native Yggdrasil, alter accepted refs or modify Forge/runner/controller/scheduler state.

ENERGY-53's posterior-variance tournament had a pooled advantage, but failed the critical independent-seed stability condition. ENERGY-54 tests a distinct hypothesis: expected reduction in uncertainty about 24 known causal candidates, with a **frozen model-mismatch fallback to conventional D-optimal design**, might acquire more robust causal evidence.

The candidate `robust_eig` calculates expected posterior KL information gain by 5-point Gauss-Hermite quadrature, with frozen observation model sigma=0.45. If its best single-hypothesis residual-fit error exceeds **0.55** of the empirical squared residual energy, it selects by conventional D-optimal instead. It receives only already witnessed consequences, never hidden or held outcomes. The controls are unmodified expected-information acquisition, posterior-variance tournament, D-optimal, Hamming diversity and seeded random. All use **80 old observations, 4 shared anchor labels and 12 other selected NEW outcomes** from an identical 96-action pool, then fit OMP3 (predeclared candidate), ElasticNet and Ridge. OLD predictors are frozen identically.

Three generator families: one known-bank 4-bit parity factor, one previously unlisted 5-bit parity factor, and one conditional 5-bit factor not represented by an individual bank member. All have previously unknown signed weights and separate old/new/cold nuisance distributions. The same 24-term candidate grammar is available to every acquisition policy. **This is not unrestricted causal language/operator discovery**, and the source generator/NumPy/sklearn are shared by the auditor.

The **only pre-freeze diagnostic** was 3 worlds on excluded seed `99839`: its independent selector-and-refit audit passed 414 checks, while accuracy and computational cost were unpromising. They are not prospective data and are not used to retune source. Source is frozen before the separate preregistration. Screening seeds `99851` and `99863` may be scored only afterward; primary seeds `9719`, `9733`, `9749` remain reserved unless the prespecified screen qualifies.

Exact source and auditor are in `source.tar.bz2`. SHA-256: `e9bbeb9dd4fa1517b47a1f7dbf5b0b5605e02a22094cfc1a5c22163f2c86918e`. Unpacked `experiment.py`, `audit.py`, `benchmark53.py` SHA-256 are in `source_manifest.json`.

To reproduce on Linux CPU with Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0, BLAS threads 1:

```bash
tar -xjf source.tar.bz2
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -B experiment.py --seeds 99851 99863 --out screen.json
python -B audit.py screen.json --out audit.json
```

A valid `SCREEN_NO_GO` is a negative *external synthetic* result, not CI failure or native scientific acceptance. More costly computation is reported, not hidden.
