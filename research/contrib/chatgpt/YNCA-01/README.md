# YNCA-01 — native causal arbitration, synthetic falsification

**Verdict: DEVELOPMENT_NO_GO.** This is a source-free standalone *development* experiment inspired by [CEA (2026)](https://arxiv.org/abs/2606.10607), **not** a replication of CEA, a native Yggdrasil model, or a scientific first-use qualification.

## Mechanism

Three deterministic experts receive exactly the same sampled data for a binary X-to-Y causal-edge question: observational contrast, do-interventional contrast, and noisy-proxy-adjusted observational contrast. A native referee is trained on 256 separate labeled synthetic worlds to assign context-conditioned expert weights using disagreement and sample-budget metadata. It only changes weights when equal-weight pooled probability is within 0.20 of the decision boundary. Global learned weighting, equal weighting, individual experts, shuffled-label weights, random weights, and a privileged per-case oracle are controls. No LLM, paid API, controller, native model, or external dataset is used.

## Chronology

- Accepted `main` used only as branch parent: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- First explored 128 development and 128 shifted-simulation worlds (not confirmatory). Do not count these as prospective science.
- Frozen prospective holdout protocol **before inspection** at commit `ce61b7851d6d93f376e2eb209c027b0d5235290b`.
- Frozen exact executable source before heldout at commit `2de0321f8fbe4416d6a25e1d59b549ee5f01e8eb`; source SHA-256 `a5a3d489c1f5732728fc5809e44c9b4b7234eb24e281975926cdc97ad128a0d0`.
- Executed new 256-world shifted holdout (seeds 61001–61256), then reproduced identical result bytes. Result SHA-256 `4817c743867d45630979ca363f5ff8c527e1bd3ce1a3f5775720e6e989bd63de`.

## Heldout scores (lower Brier is better)

| Nonprivileged arm | Brier | Edge accuracy |
| --- | ---: | ---: |
| Shuffled-training-label gate | **0.12798857** | 0.796875 |
| Global learned gate | 0.12879428 | 0.824219 |
| Contextual native learned gate | 0.13916724 | 0.824219 |
| Interventional expert | 0.14561272 | 0.796875 |
| Equal weights | 0.17818170 | 0.679688 |
| Random-weight gate | 0.18258227 | 0.695313 |

Privileged per-world best-expert oracle (diagnostic only) Brier: 0.03841589. The learned referee triggered on 64 of 256 worlds (25%).

Paired bootstrap Brier gain of contextual gate versus global learned gate was **-0.01037296** (95% interval [-0.01715287, -0.00416525]); versus the strongest single interventional expert it was **+0.00644549** (95% interval [-0.02158934, 0.03392741]). Thus context-dependent arbitration failed the prospective superiority threshold. The shuffled-label control beating the learned gate further weakens any causal-learning claim. No retuning is allowed for this candidate.

## Reproduce

From repository root with Python 3.12+ and standard library:

```bash
python -B -m unittest discover -s research/contrib/chatgpt/YNCA-01 -p 'test_*.py' -v
python -B research/contrib/chatgpt/YNCA-01/experiment.py --heldout > result-reproduced.json
sha256sum result-reproduced.json
```

Expected result SHA-256: `4817c743867d45630979ca363f5ff8c527e1bd3ce1a3f5775720e6e989bd63de` when run with the frozen source on the tested Linux/Python 3.13.5 environment. Seven focused tests passed locally. Exact byte reproducibility on Windows/Python 3.12 is **unverified**.

## Limitations and next useful work

This proves neither autonomous discovery nor a transferable causal world model. The hidden-U simulator and three expert types are intentionally small, and an independently strong exact Bayesian causal-graph comparator has not been implemented. The current source's simple internal label-separation assertion is not an independent leakage audit.

The next *separately preregistered* development should test whether arbitration has value after adding genuinely complementary experts, calibrated abstention when all experts fail, explicit intervention value, and a trained global-gating baseline. Do not retune this consumed holdout or alter the negative verdict.

**Engineering:** local focused 7/7 PASS; full Linux/Windows regression UNVERIFIED. **Science:** synthetic DEVELOPMENT_NO_GO; no independently qualified SCIENTIFIC_PASS. **Deployment:** none. Do not merge to accepted model based on this evidence alone.
