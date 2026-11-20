# ENERGY-19 — Energy witness selection versus correct causal decision-making

**Date:** 2026-11-17 (US Eastern). **Classification:** mathematical integration-safety test; no model training, no original CRAM GPU reproduction, no Yggdrasil native first-use.

## Hypothesis and result

A single minimum-energy successful **trajectory** can select a different action from the highest expected-reward **policy** even when conditional probabilities are perfectly known. On the frozen primary binary-next-state, two-stage decision table:

- First action 0 reaches states 0/1 with probability 1/2 each. With the optimal second-stage action, success probabilities are 3/5 and 3/5. Expected reward is **3/5 = 60%**; the most probable successful trajectory has mass **3/10**.
- First action 1 reaches states 0/1 with probability 1/2 each. With the optimal second-stage action, success probabilities are 9/10 and 0. Expected reward is **9/20 = 45%**; its most probable successful trajectory has mass **9/20**.
- Optimistic energy-witness decision chooses first action **1** because 9/20 > 3/10; exact expected-return planner chooses first action **0** because 3/5 > 9/20. This produces **3/20 (15 percentage points) absolute regret**.
- An energy representation that correctly marginalizes both states (sums over possible outcomes) chooses action **0**, matching the exact dynamic program. The failure applies to one specific inference/decision rule, not all energy-based methods.

## Exact finite grid (not trained benchmark)

With independent reward probabilities on the exact predeclared grid {0, 1/5, 2/5, 3/5, 4/5, 1} for both next states of both actions, the independent enumeration evaluates **1,296** possible worlds. Excluding tied decisions leaves **930** strict action comparisons. The single-witness method chooses the lower-value first action in **60/930** strict worlds; normalized marginalization has **0/930** mismatches against exact expectation. Maximum loss **3/10**; sum of losses over the 60 failed worlds **42/5**.

## Exact-source reproducibility

- Frozen before scoring: `experiment.py` SHA-256 `568d7296d6b1561f541562c288c6e2e431de51e7bc97c1fa0786259247373bc4`; `prereg.json` SHA-256 `c0e8059325f4f3184657baf9b3f8caa11e907ff00a67340b0147ad411fd99d03`.
- `freeze.json` and `scored.json` retained. Second independent replay produced a byte-identical score.
- `independent_audit.py` was written **after** the score; it checks source hashes and independently enumerates all 1,296 worlds using integer numerators instead of importing the experiment. See `audit_result.json` for passed assertions.
- Reproduce locally with `python -B experiment.py --out scored_replay.json` and `python -B independent_audit.py`. Python standard library only.

## Relevance and limits

CKAD-20's active Yggdrasil research has an original two-stage decision readout combining transition and outcome forecasts. This counterexample supports **retaining expectation/marginalization for policy choice** if adding energy consistency terms; do not replace that readout with a single low-energy best-case future. Source reference: `spoonman136668-ai/Yggdrasil` draft PR #1207, code inspected read-only at `d8f27db46af889afdfeb104fc471a710fc6d5c06`.

**ENGINEERING:** exact-rational local audit and deterministic replay PASS. **SCIENCE:** no trained energy learner, no conventional trained baseline, no new transfer result, no speedup, no Yggdrasil scientific promotion (**UNVERIFIED**). **DEPLOYMENT:** none. This is a counterexample, not a performance benchmark or model integration.
