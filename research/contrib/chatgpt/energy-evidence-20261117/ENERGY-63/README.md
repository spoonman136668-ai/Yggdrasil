# ENERGY-63 — Reusable causal-factor memory under interference

External contributor **synthetic** falsification study. This archive is **not** native Yggdrasil cumulative training or scientific acceptance. It does not change runtime, accepted refs, owner, controller, queue, deployment, or trading.

## Hypothesis

After three interfering episodes, can a learner reuse persistent previously fitted causal factors by selecting each factor's previously learned coefficient independently, using only six witnessed `do` outcomes in a returning context, and generalize to cold nuisance shifts? The decisive strong control is **exact Bayesian averaging over the identical finite factor-combination codebook**. Additional fully trained controls include conventional softmax snapshot retrieval, best snapshot, empirical prior Ridge with the identical learned factor support, per-episode and pooled full-pair-feature ElasticNet, and RBF kernel ridge. This is a bounded finite experiment, not invention of unrestricted causal operators.

A contributor-authored generator plants four pair-parity primitives among ten causal action bits, with two extra nuisance bits. Every world has 502 disjoint 10-bit causal intervention assignments. Three consecutive training episodes A/B/C each witness 80 labeled actions; all learners get six identical returning-context labeled calibration actions. Return/cold evaluation each withholds 64 causal actions and distinct underlying assignments, and 64 held A/B historical actions test retained readouts. Three causal families: factorwise **recombination**, **return to old**, and **novel four-way factor outside the supplied pair dictionary**. COLD nuisance observations are randomized independently, so generalization includes cue shift. The source specifies all primitive families and the bound of four factors; the learner receives no planted supports, coefficients, true regime ID, or held outcomes.

The candidate searches only 81 possible assignments of four learned factor coefficients from A/B/C, minimizing six-probe squared error plus a pre-fixed factor-change penalty. Its historical A/B readout heads remain immutable. Exact Bayesian codebook averaging is given the same 81 choices, stage coefficients, six outcomes, and full posterior; its probabilistic likelihood/prior are **fixed rather than tuned on the prospective data**. Candidate MAP and conventional Bayes use identical capacity and observation budget. A wins-over-softmax result alone is *not* sufficient.

The one prefreeze excluded pilot seed `998203`, one world ID per family, was evaluated to check program and independent audit. It is not prospective confirmation. Fresh screen seeds `998269, 998281` and reserved primary seeds `105101, 105119, 105137` must be frozen separately in `prereg.json` on GitHub **before** fresh scoring. Any critical screen failure stops the primary. Source+auditor and hashes are committed to the existing draft PR #1210 before preregistration. No post-result tuning allowed.

## Reproduce

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir source && tar -xjf source.tar.bz2 -C source
cd source
python -B experiment.py --seeds 998269 998281 --out screen.json
python -B audit.py screen.json --out audit.json
```

Requires Python 3.13, NumPy 2.3, SciPy 1.17, and scikit-learn 1.8. Independent audit reconstructs every intervention and source outcome and refits all ten arms **without importing scorer**; uses shared NumPy/sklearn mathematical backends, so it is not an independently developed new-world replication. Check `provenance.json`, `REPORT.md` and evidence tar for the original unmodified experiment output, independent audit, semantic replay and per-case predictions after scoring. Training/selection CPU seconds are not measured energy or whole-system cost.
