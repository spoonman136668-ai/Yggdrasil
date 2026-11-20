# ENERGY-55 — Matched-intervention causal-variable representation

**External synthetic research evidence, exploratory UNPREREGISTERED.** The two excluded development cohorts were evaluated **before** the code and protocol were committed. Do **not** treat these screens as prospective replication, accepted Yggdrasil science, actual native Yggdrasil training, discovery of an unprovided operator, or measured physical energy efficiency. The reserved primary seeds `9811`, `9827`, `9839` have never been scored.

## Question

When hidden high-order causal mechanisms and nuisance correlations change, do controlled, one-variable-at-a-time `do` contrasts help a small nonlinear learner identify causal input variables and generalize to cold nuisance shifts? Does the proposed **squared** intervention-effect ranking beat a standard **absolute-difference** ranking with exactly the same paired observations?

## Design

For each world, six causal variables are hidden among twelve binary observed variables, with two observationally correlated nuisance cue variables. Six latent causal roles influence nonlinear parity, threshold or conditional response operators. The **true operator grammar and true causal variables are withheld from all learners**, but the generator is written by the contributor and known to the auditor. The learner selects six input variables, then uses standard RBF kernel ridge to predict new-context consequences. It is not an autonomous symbolic world model.

Every arm receives the same **72 matched old-context intervention outcomes** (three one-bit-flip pairs for each of twelve observable bits), 24 additional old observations, and 48 new observations. Every method is trained with only observed interventions and consequences. Independently generated 96-action old/new/cold held sets have withheld outcomes; assignment duplication across streams is not ruled out, so this is nuisance-shift generalization rather than genuinely unseen causal assignments. Cold nuisance bits are independent. All fitted nonlinear prediction heads are ordinary scikit-learn regressors.

Arms: squared matched-effect ranking (candidate); standard absolute-difference ranking (strongest matched contrast control); conventional mutual-information/ExtraTrees/ElasticNet variable selection with the same six-variable downstream capacity; random 6-variable negative; 12-variable fixed and cross-validated RBF kernel ridge; raw 12-variable ExtraTrees; and shuffled-pair-effect negative. Conventional controls see the same 144 labeled examples. Test old/new/cold MSE on 96 held actions per world. All arms train separate old and new heads; new head is used for cold. The matched-effects rankings use the 72 old controlled observations, while supervised selector controls are allowed both old and new labels.

## Execution and custody

`source.tar.bz2` contains the scorer `experiment.py` and separate `audit.py` with exact SHA256 hashes recorded in `provenance.json`; `EVIDENCE.tar.bz2` retains both unmodified original scored JSONs, independent audit receipts, original unchanged-source replay and semantic replay receipt. See `verify_archive.py` for byte-hash and count verification.

Run from extracted source with Python 3.13, NumPy 2.3, SciPy 1.17, scikit-learn 1.8 on single-thread CPU:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
tar -xjf source.tar.bz2
python -B experiment.py --seeds 99983 --out out_smoke1.json
python -B experiment.py --seeds 99989 --out out_smoke2.json
python -B audit.py out_smoke1.json --out audit1.json
python -B audit.py out_smoke2.json --out audit2.json
```

These are **exploratory evidence** seeds, not scientific holdout confirmation. Three fresh primary seeds remain unconsumed. No scientific primary was run because the simplest strong conventional paired-contrast control matched or outperformed the proposed ranking. **Do not tune these consumed screens to claim a new mechanism.**

There were **72,568 independent refit checks PASS** (36,284 each), but the independent auditor imports the identical synthetic world generator and uses the same NumPy/sklearn numerical libraries; therefore this is not complete independent evaluation of the scientific hypothesis.

Native Yggdrasil main, accepted refs, owned runtime, controller, scheduler, queue, training checkpoints, and deployment are unmodified. The external draft PR remains evidence-only.
