# DG1 Sleep01 — Tokenless offline consolidation (synthetic DEV)

**Frozen before implementation:** `bf6ba379b03f3caee5b4b13c7f60c3d7d6d2e94e`, based on HC11 `d36e4010709be8aa7907561e8312a3e9ddaf56f2` (draft PR #980). HC12 separately preregistered at `26deb869f89d905fc504ea86e754cc299f9e1be5`; no HC12 results are used or changed.

## Design

Inspired by Google Research's sleep/consolidation idea ([arXiv:2606.03979](https://arxiv.org/abs/2606.03979)), retain Yggdrasil's **non-transformer, no-token, no-gradient causal-program basis**, not the Google LLM implementation.

Wake learns only from actual charged physical observations. At fixed steps 8/16/24/32/40/48, sleep replays a bounded 64-event stream into at most two retained latent 40-rule-per-action causal contexts with a fixed-width deterministic search. It then audits *pre-update physical witness predictions* to calibrate confidence, requiring two distinct verified states per queried action and minimum current-context evidence. Dreams are no more than eight **unverified** counterfactual proposals; they are never used as synthetic labels. This work does not replicate Google's RL, neural distillation, MoE, parameter growth, or real dreaming.

Independent/ablated comparisons use exactly the **same charged physical trajectory**: unchanged HC09 awake-only version-space, one-context sleep ablation, conventional independently coded causal rule evaluator with the same sleep algorithm, empirical Bayesian run-length control, and a no-dream sleep ablation. This gives no claim of equal total CPU, memory or separate learning trajectories.

## Frozen new-world DEV (seeds 93001–93024, shared 1,088 physically charged actions)

| Cohort, total 512 evaluator-only pairs | Native sleep correct / wrong / abstain | Awake HC09 | Conventional sleep |
|---|---|---|---|
| Return-to-A after A→B→A | 64 / 16 / 432 | 273 / 177 / 62 | 64 / 16 / 432 |
| Stable majority | 48 / 0 / 464 | 512 / 0 / 0 | 48 / 0 / 464 |
| Unfamiliar cubic | 45 / 3 / 464 | 450 / 62 / 0 | 45 / 3 / 464 |

**Result: NEGATIVE_DEV, frozen primary NO-GO**. The model misses the safety limit (16 > 8 ABA wrong) and stationary coverage floor (48 < 128). Conventional sleep ties. These numbers were reproduced locally using a faithful *temporary* HC09/HC10 interface stand-in; the uploaded repository source must be independently qualified on the actual code and on Ubuntu/Windows. Keep any source/CI/atlas failure separate from the scientific negative. No native model promotion.

## Reproduce

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-sleep01-20261113 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-sleep01-20261113/eval_dev.py > sleep01-result.json
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

Check receipts: charged action counts, cold checkpoints, physical trace SHA256, no oracle calls, no training on forced flips, and no effect from unverified dream proposals.

## Scope and interpretation

This is source-only external synthetic DEV. Neither whole-world general intelligence, unfamiliar-world transfer, native recurrent sleep learning, neural representation development, autonomous RSI, nor useful dreaming has been shown. The old replay-heavy mechanism is rejected; a separate prospective **selective sleep-time causal repair with real charged verification** experiment is the defensible next hypothesis.

No protected first-use, main, native Yggdrasil model, FORGE controller/owner loop, Wingless, CKB-plane, independent WSP weight editing, external scheduling or paid APIs are touched.
