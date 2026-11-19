# ENERGY-59 — Context-blind persistent causal memory

**External synthetic research only.** This does not run or modify native Yggdrasil model weights, accepted refs, controller, Forge, queues, schedulers or deployment. This is NOT independent scientific qualification.

Research question: Can a *single serialized memory state*, developed from a continuous stream of do-interventions and observed consequences **without episode IDs or true regime boundaries**, retrieve and retain previously learned causal responses after interference? Is a structural-support-gated consensus of historical hypotheses reliably better than the directly matched conventional best-snapshot retrieval, or standard softmax Bayesian-like model averaging?

Scorer: `experiment.py` and independent refit auditor: `audit.py` in `source.tar.bz2`. Self-authored synthetic generator (E59:v1). Three families `return_old`, `return_middle`, and `novel_composition`; **9 underlying causal action bits plus 3 nuisance cue bits** observed, first 9 causal assignments disjoint within each world. Hidden parity2 and parity3 terms chosen from a *provided* 286-term dictionary; no new operator grammar invention. Three chronological regimes A, B, C have **randomized lengths** (64–88 each), unavailable to the learner. A/B/C are labels internal to generator/evaluator ONLY and not inputs to `learn_stream` or `select`. After training, the evaluator provides 12 labelled diagnostic interventions per requested hidden regime, without regime ID, and 64 separate held actions per requested regime with labels hidden during learning and query-time selection. The three query sessions are presented separately because their response distributions differ; this is a **limited labeled calibration / hidden-regime recognition task**, not zero-shot unlabelled state recognition.

Candidate uses a fixed history of overlapping 64-sample OMP4 snapshots every 16 observations as a persistent JSON checkpoint. A 12-observation query retrieves snapshots by their prediction residuals, using an authored structural-support overlap rule to average the best two only when they are nearly tied. This is a **bank of statistical snapshots within one persisted memory object**, not a demonstrated native monolithic causal substrate. The conventional matched control chooses the single best historical snapshot under the same calibration evidence and same stored capacity. Other fully trained same-information controls: softmax snapshot averaging, latest OMP4 snapshot, pooled ElasticNet, recency-window ElasticNet, full-history RBF kernel ridge. Negatives: random historical snapshot and shuffled calibration labels.

Development-only seeds 998911 and 998921 (three worlds each) were scored and audited **before source freeze**. Candidate pooled MSE respectively 0.031196 vs matched best-snapshot 0.032461 and 0.029770 vs matched 0.028906. Mixed, no consistent benefit. All 60,422 independent refit comparisons PASSED. These pilots are exploratory and excluded from scientific confirmation; no changes to thresholds were made after observing the two screens. Source readout code changed only to remove an unused no-op loop after the first pilot, with no behavior change; all further behavior must be frozen before any primary score.

**Reproduction:** Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0; BLAS threads=1. Extract source, then:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -B experiment.py --seeds 101101 101119 101141 --out primary.json
python -B audit.py primary.json --out audit.json
```

The proposed 36-world prospective primary is run **only after separately committing `prereg.json`** with the exact SHA of this source and nine frozen quantitative gates. No native implementation or scientific acceptance is authorized. Results, positive or negative, must be committed to existing draft PR #1210; main remains untouched.
