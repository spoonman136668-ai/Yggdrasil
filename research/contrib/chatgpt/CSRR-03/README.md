# CSRR-03 — generic causal rule induction with reversible hypothesis archive

**Disposition: NEGATIVE_DEV_ONLY.** Three-seed, source-free synthetic experiment under the existing Yggdrasil contributor lane. It does NOT train the native Yggdrasil learner, access protected source worlds, use pretrained donor weights, or qualify scientific causal transfer.

## Question and method

Unlike CSRR-01/02, the candidate receives no source-law identity or hard-coded XOR/exception law as its predictor. It enumerates all **256** Boolean output functions of three binary public inputs (action and two context bits), maintains a rolling 32-witness Bayesian score, and stores up to four previously selected hypotheses. The simulator (but not the candidate) switches A → B → A → C → A → B. A known-family symbolic upper bound receives the three true source laws as additional prior knowledge; equally informed controls are an uncached exact same-class tournament, rolling Beta-Binomial per-input counts, and cumulative counts.

The **representation class is still preprogrammed** (all 256 three-bit truth tables). This is not an independent unfamiliar causal family or proof of new causal law invention. Shared action/outcome stream: 3 seeds × 6 phases × 192 = 3,456 public witnesses per method, source-only. No held evaluator labels or phase identities enter candidate updates.

## Frozen source / evidence

- Source and protocol committed *before* primary evaluation: [`13c9cb39`](https://github.com/spoonman136668-ai/Yggdrasil/commit/13c9cb39b821fe017498b0dbbf1f0f2fb58d33b7).
- Run from this directory: `node study.mjs --self-test`, then `node study.mjs` (Node 22, no dependencies). A second fresh Node process reproduced byte-identical output.
- Full primary stdout SHA-256: `35c4686fb5861b670c444a32a568362ebe20c10c60498edc6676d5777d254977`. Metrics and per-phase summaries are in `result.json`; custody and runtime in `provenance.json`.

## Frozen outcome

| Model | Mean prequential Brier (lower better) |
| --- | ---: |
| Raw constant | 0.25000 |
| Archived 256-mask tournament | 0.16932 |
| Identical tournament without archive | 0.17055 |
| Rolling counts | 0.16730 |
| Global counts | 0.21670 |
| Informed symbolic control | **0.14732** |

The archive was **0.00298 Brier worse than uncached** in the first 32 steps of returning A-regimes; it was **0.02263 worse than rolling counts** in the same early-return slices. Its mean returned-old-regime error exceeded the Bayes floor by **+0.043999**, above frozen +0.020. All three seeds produced **32–33 archive promotions**, suggesting instability rather than reliable consolidated rule retrieval. Cold clone produced zero prediction mismatches.

Engineering focused source-free PASS; scientific candidate retention **FAIL**; independent causal transfer and true Yggdrasil intelligence improvement **UNVERIFIED**. Full-platform regression/G29/CI/native acceptance **UNVERIFIED**; deployment NONE.

**Stop this candidate without post-result retuning.** Preserve the negative alongside CSRR-01/02 and refer future unfamiliar mechanism testing to the existing authorized source owner [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426), preserving central coordinator [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278). No new runner/controller/actor may be inferred from this research.
