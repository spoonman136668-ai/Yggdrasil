# ENERGY-60 — Learned latent-state causal-memory retrieval

**External synthetic evidence only.** This experiment tests whether a persistent **learned latent-state codebook and transition filter** improves functional recall of changing causal response regimes compared with conventional calibrated softmax retrieval of the exact same historical models. It is not native Yggdrasil training, scientific first-use, operator invention, a self-improving AI, or an accepted checkpoint.

## Mechanism

Each world has nine hidden causal intervention bits, three nuisance cues, three chronological regimes, and a novel parity4 or threshold5 factor that is **not represented by the supplied pair/triple Walsh grammar**. The generator keeps all 9-bit causal intervention assignments disjoint across training, calibration and held contexts. Learners see only actions, outcomes and chronology, not regime names or changepoints. Each A/B/C query provides 12 factual action-consequence calibration pairs; consequently this is *few-shot latent-state identification*, not zero-label zero-shot retrieval.

All methods learn identical OMP4 historical snapshots from windows of 64 witness events, stride 16. The proposed method uses 40 fixed unlabeled action signatures to cluster those snapshot predictions into three latent prototypes with KMeans; transition frequencies among consecutive cluster assignments become an internally learned, smoothed state Markov matrix. The next query posterior uses **80% learned previous-state transition prior + 20% uniform prior**, times calibrated prototype likelihood exp(−probe MSE / 0.10), to form its prediction. No hidden labels or held truth are used for the state representation. The matched conventional controls are exactly **ENERGY-59 softmax retrieval (temperature 0.10) over the same snapshots**, independent prototype softmax without temporal filtering, calibrated best snapshot, last snapshot, pooled and recent ElasticNet and RBF KRR, plus shuffled-probe and random-snapshot controls.

Every arm receives the same chronological training consequences, 12 labeled calibration probes per query and 52 completely held query actions per hidden context. This is a finite hand-authored feature grammar and small statistical clustering substrate, not unrestricted learned causal mechanisms. Model capacities and compute differ across controls, and CPU time does not measure physical energy.

## Reproduction

Frozen source archive `source.tar.bz2` includes `experiment.py` and separately written `audit.py`; SHA-256 values are in `source_manifest.json`. The audit **does not import the scorer**, independently refits all historical snapshots, KMeans prototypes, all sklearn comparisons and held predictions, verifies assignment uniqueness, disclosed latent-factor truth and aggregate scores. It shares NumPy/sklearn and the scorer-disclosed noise realization; this is not an independent external replication.

Linux CPU, Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0, SciPy 1.17.0; all BLAS threads 1:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
tar -xjf source.tar.bz2
python -B experiment.py --seeds 997601 997619 --out screen_scored.json
python -B audit.py screen_scored.json --out screen_audit.json
```

Excluded code-validation seed 999701, world ID 0 x 3 families, passed 35,102 independent audit checks; it is **development smoke, not the prospective screen**. The two prospective screen seeds are not to be evaluated before the distinct preregistration commit. Primary seeds 102101/102119/102137 remain reserved unless the frozen screening stop rule allows primary. No code, seed, threshold or control is to be changed in response to scored primary screen outcomes.

Research location: existing draft Yggdrasil PR #1210, `research/contrib/chatgpt/energy-evidence-20261117/ENERGY-60/`. No merge or native runtime mutation.
