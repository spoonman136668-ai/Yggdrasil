# ENERGY-53 — Hypothesis-discriminating causal interventions

This is **external synthetic evidence**, not native Yggdrasil model training, scientific qualification, merger, controller work, or deployment.

**Question:** Can a causal-hypothesis tournament use the consequences of already observed interventions to select more informative next actions than Hamming diversity, conventional D-optimal design, single-hypothesis uncertainty, and random acquisition?

The generator independently creates 9 true causal binary action variables and 2 nuisance observation bits. All methods observe the same 80 OLD outcomes, the same 4 anchor NEW outcomes, then choose exactly 12 more NEW interventions out of 96 candidates. Mechanism families are parity of four bits, threshold on four bits, and four-bit conditional gates. The 24 possible mechanism signatures are **preauthored and shared with every learner/policy**; planted family/support and coefficients are hidden from them. This does not invent unrestricted operators and does not test a native tokenless model. Old and new share four background 1–3-way motifs, but new includes an additional signed mechanism. The total 320 causal assignments per world are unique across OLD training, NEW pool, held OLD/NEW/COLD sets.

The candidate assigns probabilistic weights to 24 competing hypotheses using only *revealed* new consequences, then chooses the next action maximizing posterior predictive variance. Standard D-optimal design and Hamming diversity are strong acquisition controls, with identical action budgets. Each acquired dataset trains three independently fully fitted downstream learner variants: OMP3, ElasticNet and Ridge on the exact same bank, with an OMP4 learned OLD base. OMP is the **prespecified primary downstream learner**; no post-result best-learner promotion.

**Source package:** `source.tar.bz2`, Git blob `3d202e61e45f6a723c550e923a40c7bc59735c89`; SHA-256 `bd1df60e730c72928e1b0aa1c7831f995eb1b84e43bc8bdda6269219ec941661`. Unpacked original `experiment.py` SHA-256 `c1566f297a01c774d5b50b787f297cd7df31be6a4b51eb3876b603c4626f4851`; `audit.py` SHA-256 `24f59a552448ae9a67810a7d8fdd8d181a429a40e64516fe98e0eddb70e8fb48`.

**Reproduce** using Linux CPU Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0 and `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`:

```bash
tar xjf source.tar.bz2
python -B experiment.py --seeds 99721 99733 --out screen_scored.json
python -B audit.py screen_scored.json --out screen_audit.json
```

The independent auditor reconstructs all world source identities, checks duplicate-free interventions and unchanged old prediction, independently reconstructs acquisition choices, refits all 15 policy × downstream combinations, verifies exact prediction hashes, and recomputes aggregate errors. **It still reuses the generator and NumPy/sklearn libraries**, so this is not an independently authored simulator.

**Pre-freeze development seed `99709` was evaluated solely to debug an initially numerically unstable tie-break in D-optimal selection and restrict planted background factors to causal bits.** It is excluded from screening and primary. Two prospective screen seeds `99721`, `99733` and the reserved primary `9511`, `9523`, `9547` must not be scored before the separate preregistration commit. Primary runs only if BOTH independent screen cohorts satisfy the frozen screening gate.

No other Yggdrasil, FORGE, Wingless, TTT-Hybrid, accepted-state, controller, scheduler, queue, or runner modification.
