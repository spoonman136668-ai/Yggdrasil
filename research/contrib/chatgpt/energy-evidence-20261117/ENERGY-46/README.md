# ENERGY-46 — Disjoint falsification of contradiction-gated repair

**External synthetic evidence only.** No native Yggdrasil model, accepted research state, first-use, controller, runner, merge or deployment changes.

ENERGY-45 was promising on aggregate cold transfer but failed old-context competitiveness and seed stability. ENERGY-46 changes the **world generator** to newly sourced, fully randomized binary interventions, three independently generated causal-operator families (two-bit parity, three-bit parity, mixed signed parity/AND), and disjoint seeds. It deliberately does **not** tune ENERGY-45's contradiction gate on its consumed results. The candidate retains its original old-context OMP4 model without overwriting it; on new training observations it tests support replacement using a 72/24 training-only split and a fixed 0.12 MSE improvement gate.

This study uses an authored **known finite grammar** (364 parity/AND functions over 12 observed binary action bits). The learner does not have access to planted factor identities but is given that hypothesis grammar. It is not a token model, not general intelligence, and not unrestricted causal-operator invention.

The single primary uses three *new* seeds 8909, 8923, 8933, each with four case IDs and three disjoint grammar families = 36 worlds; nine worlds have no causal change. Each arm receives exactly 96 old and 96 new action-consequence labels and is evaluated on separate 128 old, 128 new and 128 cold outcomes per world. Strong controls include full conventional OMP, conventional cumulative structural memory, 96/96 stagewise OMP, an equal-information validation-selected hybrid, ElasticNet, Ridge, random forest, unconditional replacement, frozen old model and shuffled-label negative. One redundant duplicate candidate arm was removed before preregistration.

The scorer and independent auditor source are byte-exact in `source.tar.bz2` (SHA256 `2f3b1ac3e65340c6d3555ace51d6870f169dd72a01fa2917d2d7fd317855b8c9`). Original scorer `fa38237a02f5fd76b66406ef6dccfe9b35bd406a24697ca81642d7c1ef1e1698`; auditor `528509534942e2e18bb2880f411db2e1af2dc9b9128cfb8a024f6779d3858074`. Excluded smoke seed **99863**: six cases, source-free all-arm refit audit **25,565 checks PASS**. Primary seeds have **not** been touched before prospective prereg.

Reproduce with Linux CPU Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0, single-threaded BLAS:

```bash
tar -xjf source.tar.bz2
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --primary --out scored.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py scored.json --out audited.json
```

Full results and integrity receipts are archived after primary; `prereg.json` freezes the exact gates first. Native Yggdrasil full regression, acceptance and science remain separate and not performed here.
