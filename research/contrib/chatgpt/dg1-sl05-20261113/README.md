# DG1-SL05 — cold-retained three-context causal memory (isolated DEV)

**Preregistered:** 10fa5ec7c983b871482b772ec54d7522ec3e3ac5, before implementation or outcomes.
**Parent:** SL04 draft PR #986, f440698b0d1e32bb029a43c204eb6fa3d189b236, source qualified but scientific NO-GO.
**Scope:** non-token, non-gradient synthetic external research; **no native model, main, autonomous owner loop, accepted state or weight-editing change.**

This tests whether three independent retained causal-rule memories survive return to old physical dynamics after ABCA and ABCB interference. Two further prospective cohorts detect stationary forgetting and inappropriate confidence when a fourth context is outside the 40-rule hypothesis family. Real physical action traces are shared across all seven arms; the learner never receives hidden phase identities, world oracle, paid-bit-flip transitions, seed or evaluator audits.

A three-bank native candidate (three sets of 4x40-rule masks) preserves banks and requires two independent causal witnesses after switching before predicting. The confidence-gate ablation and FIFO forgetful-bank control test mechanism necessity. Strong conventional comparators include independently implemented three-bank HMM-style version-space tracking and a matched-observation bounded eight-event replay variant. Frozen SL04 two-bank/selective and recent-window controls remain. **The HMM is not a fully trained neural baseline or exact Bayesian online change-point detector.** All agents receive the same physical evidence; capacity metadata and whole-process compute are measured separately and are **not identical**.

Eight seeds per cohort × 4 cohorts × 80 paid physical actions = 2,560 paid actions total, of which 320 are charged exogenous flips. Only the other 2,240 events provide causal learning. Model state is **cold-serialized and restored at physical step 60** then used without reset through step 80. Evaluator-only 64-pair audits are conducted at 20/40/60/80, including unseen physical state/action queries. Frozen thresholds are in prereg.json and cannot be tuned to observed results.

Run from repository root:
```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-sl05-20261113 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-sl05-20261113/sl05.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

The prospective outcomes remain **UNVERIFIED** until executed. All source, results, trace digests, negative outcomes, formal classification and cross-platform qualification receipts will be stored directly in this GitHub repository, not ChatGPT file attachments. A synthetically positive outcome would remain DEV only; no training, AGI, autonomous self-improvement or scientific PASS may be inferred without independently qualified broader controls.

### Frozen-control checkpoint compatibility

The first SL05 focused run **failed before the prospective cohort executed**: SL04's frozen recent-window decoder limits the observation counter to 64 even though SL05 has 70 paid causal observations. The SL05-only `restore_frozen_recent_80` adapter retains the exact same SL04 predictor/training masks, validates its canonical SHA-256 checkpoint and reconstructs derived window masks for counters 65–80. It does not alter SL04 source, observations, training, or results. This is an engineering integration correction made *before* the first SL05 cohort results. The failing preflight is retained as a GitHub Actions receipt.
