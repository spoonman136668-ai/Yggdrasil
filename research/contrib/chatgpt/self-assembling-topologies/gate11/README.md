# Gate 11 — Calibrated causal abstention (scientific development NO-GO)

This is an **independent, synthetic contributor study**, not a native Yggdrasil learner run. We did not update accepted `main`, the cumulative Amalgam checkpoint, training ownership, scientific first-use data, or any production model.

## Hypothesis and preregistration

**Question:** When a candidate two-parent causal relationship is unsupported, can a small learner reject the structure without sacrificing prediction accuracy?

The frozen intervention-only test was committed at [original preregistration](./prereg.json), commit `824dac2b2a78f823e15765b7783c489d567f177d`. A wording clarification about the **training-only last-64-observation buffer** was committed at `3941a97c557f078f45993b38395e6496e43a3328`, **before the first primary run**, with no change to seeds, thresholds, metric or capacity. The [executable source](./run.cjs) was then committed `2aafc98f708236e8f39e4f951f4cf4cba72e9a1d` before scoring. The [primary result](./result.json) was sealed at `021ffb6f67063fcb54825972fd6acfff312e5f09`. Later [arithmetic and model-order audit](./audit.cjs) was committed separately.

**Fresh, disjoint synthetic seeds:** 64 in-family seeds `10000..10063`, plus 32 each of 3-way parity `11000..11031`, random labels `12000..12031`, and unary functions `13000..13031`. Every seed contains two labeled worlds A and B, each with 128 interventions for training and 32 immutable held-out interventions. Source parent IDs and unknown operator truth tables stay hidden from all learners. All models see the same interventions and consequences.

The learner selects a pair based **only on the first 48** of the last 64 training observations. It tests predicted Brier reduction relative to a fitted marginal null on the **other 16** training observations, and independently requires a conditional-effect contrast for each proposed parent. It then refits on all 64 observed training examples. This avoids choosing among all 15 pair candidates on the same 16 examples used to validate confidence.

## Frozen metrics and controls

| Learner | In-family held Brier ↓ | Unary held Brier ↓ |
|---|---:|---:|
| Calibrated dynamic, 260 packed bytes | 0.0711203534 | 0.2535735552 |
| **Matched calibrated fixed**, 260 packed bytes | **0.0711203534** | **0.2535735552** |
| Gate 10-style legacy pair, 260 packed bytes | **0.0607651136** | **0.0494270039** |
| Marginal null, smaller state | 0.2084884714 | 0.2535735552 |
| Larger Bayesian model with explicit null, nominal 3856 bytes | **0.0504003906** | **0.0416113281** |

**Predeclared tests:**
- Two-parent route accepted: **115/128**, just below **116/128** requirement (**FAIL**). All 115 accepted parent sets were correct on these synthetic worlds.
- Unsupported two-parent relationship rejected: **64/64** parity3, **63/64** random-label, **64/64** unary (**PASS**; gate required >=58/64 each).
- Macro mean OOD Brier improvement vs legacy: **−0.0609495979**, required **+0.005** (**FAIL**). Negative number means worse performance.
- In-family Brier degradation vs legacy: **+0.0103552398**, permitted up to +0.025 (**PASS**).
- Byte-exact trained-state packing and prediction-only cold restore: **64/64** in-family seed runs and **32/32** per negative family. Continued training after cold restore **not tested**.
- Matched calibrated fixed and dynamic predictions **tied exactly** on all three negative families and the positive family. Dynamic had **630,784** in-family candidate comparisons vs fixed **188,416**, approximately 3.35× as many candidate operations, not whole-process speed.
- Out-of-family Brier: parity3 **0.2525714352** calibrated vs **0.2618693138** legacy; random **0.25724457** calibrated vs **0.269244449** legacy; **unary 0.2535735552 calibrated vs 0.0494270039 legacy**.

### Main falsification

The calibrated gate avoids claiming two causal parents for a single-parent relationship, **but its fallback then loses the highly predictive single-parent relationship**. This distinguishes *structural uncertainty* from *prediction uncertainty*: rejection of a two-parent explanation should redirect the model to a one-parent explanation, rather than discarding the useful prediction.

The larger Bayesian comparator includes single-variable truth tables within its 240 two-input candidates and therefore retains accurate unary predictions. Its 3856-byte state is **not** memory matched to the 260-byte learners. No self-assembly advantage is demonstrated by this experiment.

The preregistered overall outcome is **SCIENTIFIC_NEGATIVE_DEV**. Do not change this gate's thresholds or promote its result as model intelligence gain. Future new-seed research may preregister a hierarchical 0/1/2-parent learner (and explicit null) with fair matched capacity and compute.

## Reproduce, without downloading chat artifacts

From the repository root, with Node.js:

```bash
node research/contrib/chatgpt/self-assembling-topologies/gate11/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate11/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate11/audit.cjs
```

The first command reruns the **entire frozen numerical comparison** and checks exact JSON equivalence. The second independently checks model-order Boolean counterexamples, seed ranges, gate arithmetic, resource claims, and negative findings. It is **not** a fully independent second numerical implementation.

CI dual-platform replay, native scientific first-use, build and deployment have separate status: inspect the PR's pinned action run. The accepted learner remains untouched; **do not merge/promote this evidence without central owner qualification**.
