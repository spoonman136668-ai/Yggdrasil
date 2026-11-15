# FKP-12 — Direct causal memory learns from *real* Mystery Path action consequences

**Independent Yggdrasil research contribution; not the accepted native model.** The frozen preregistration was committed FIRST as `eb2ab3758c090f653c0245f6d546c842fc670669` before implementation and original DEV. Inherited pinned source admission FKP-10 [PR #1100](https://github.com/spoonman136668-ai/Yggdrasil/pull/1100) and FKP-11 reward headroom [PR #1102](https://github.com/spoonman136668-ai/Yggdrasil/pull/1102).

## What changes versus prior weight-programming experiments

This study tests a learner against **actual original upstream Memory Gym Mystery Path interactions**. It does not choose among an author-supplied finite set of Boolean rules. The model sees only rendered RGB observations, a chosen native two-symbol action, and the **previous** observed reward sign; its prediction target is the **next actual source-issued** reward sign. No environment private state, hidden path, direct target labels, source info fields, or debug renderer enter learning. This is prediction of action consequences, **not** evidence of improved control, planning or reward-return.

Original upstream is MIT `MarcoMeter/endless-memory-gym@a94f2b60d1769ea44df3226561488768e1dff9f4`; research task explicitly configures its built-in public `reward_fall_off=-0.05` feedback. This changes reward *semantics* relative to the benchmark default, not physics or public observations. Never present configured-reward outcomes as official Mystery Path score.

We freeze 8×8×3 mean-pool image numeric input, 9 action one-hots, 3 previous-reward one-hots. A fixed two-key numeric associative memory directly writes source-observed class counts into **4,096×3 signed integer weights =49,152 raw bytes**, without gradients or tokenization. It is an exploratory mechanism, not a proven new learning foundation. Conventional equal-data Dirichlet counts, fully trained GRU (64 units), MLP (64×64) and logistic controls, source prior, action-erased and label-shuffled negatives all receive exactly the same training action/reward history.

The GRU, MLP and logistic controls train 24 complete Adam epochs for EACH of two fixed seeds (1212/3434), selecting the lowest-validation-Brier checkpoint across epochs and seeds **before** accessing DEV worlds. The direct weights are fitted once on the full training history. Report full-process acquisition/training/cost, memory and parameter counts; this is **not a claim that per-algorithm training FLOPs are matched**, though source data/action budgets are equal.

## Custody and frozen cohorts

- **TRAIN** 16 new worlds seeds 971300–971315; **VALIDATION** four seeds 971400–971403; **original public DEV** eight seeds 971500–971507. Two source-blind policies, maximum 256 actual `env.step` interactions each episode; at most 14,336 authentic source events across 56 episodes.
- **TRANSFER** 971600–971607 and all owner-protected scientific world sources remain unopened. FKP-10 970100–970103 and FKP-11 971100–971103 are already consumed and not reused as new science.
- One-shot source-locked GitHub CI: before the first DEV call, pinned implementation exact SHA and G29 atlas, fixture-only tests, full inherited repo regression on **both Windows and Ubuntu**, dependencies and strong control import/training preflight must pass. Original DEV is Linux-only first-use; Windows repeats consumed source observations for deterministic *mechanical* reproducibility, not fresh science.
- Models train and select on TRAIN/VALIDATION, then emit a SHA-256 seal of every learned memory/control weight and model-selection receipt before DEV observations. They are not tuned on DEV results.
- Freeze per-world 3-class Brier, log loss, outcome counts, pair-by-world 10k-bootstrap CI, policy-stratified nonregression, cold exact memory restoration and tamper negative. Report the strongest *actually fitted* conventional comparator, not a weaker reference cherry-picked post hoc.

A developer signal requires **direct Brier at least 0.02 lower than the strongest** of GRU, MLP, logistic, count, a positive context-bootstrap CI lower bound, no >0.01 regression on either policy and genuine positive/negative DEV feedback. Even a public DEV signal is not independent `SCIENTIFIC_PASS`; future disjoint source families, true action-value learning, cold interference, whole-process resource parity and native-owner qualification remain mandatory.

## Reproduction

With the exact upstream Git checkout and Python3.11 + pinned numpy/gymnasium/pygame/PyTorch CPU:

```console
python -B -m unittest discover -s research/contrib/chatgpt/FKP-12 -p test_fkp12.py -v
python -B research/contrib/chatgpt/FKP-12/run_dev.py --public-dev --upstream-root UPSTREAM_EXACT_CHECKOUT
python -B scripts/build_code_atlas.py --check-if-present
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

**Do not rerun already-consumed public DEV as untouched first-use.** The explicit `--replay-consumed-public-source` switch supports reproducibility only. This code must not merge to accepted Yggdrasil `main` or be wired into an autonomous controller/runner on its external contributor receipts.
