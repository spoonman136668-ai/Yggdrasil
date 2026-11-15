# WSP-115 — Fresh 1,024-intervention high-first, 64-node quadratic causal worlds

## Why this branch exists

Original WSP-114 [PR #1085](https://github.com/spoonman136668-ai/Yggdrasil/pull/1085) completed **engineering qualification successfully**, but [first-use job 132768156237 / run #43699116882](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43699116882) was cancelled when its one-job 75-minute execution limit was reached on 2026-11-15 10:48Z. It emitted **no** completed scientific result. That original first use is consumed/censored; never rerun or call its hidden data pristine.

## Frozen BEFORE v2 generator, test or evaluator

WSP-115 first commit `3ab8b239d0e92646e4eb895cc8828f06bdec1a3a` freezes v2 at 64 interacting state bits, 12-previous-node quadratic and linear causal features, **1,024 observed interventions per unfamiliar transfer world**, **16 novel worlds**, **512 never-seen exact 64-bit state queries per world** and **8 budget prefixes 1024/512/256/128/64/32/16/8**, without any reduction in benchmark scale or strongest independent GF2 symbolic controls. New world generation uses separate WSP115/v2 SHA256 domains from consumed WSP114/v1.

To prevent another wall-time timeout, evaluation is split into **eight immutable-source independent two-world jobs**, each with all five learning/control arms and an independently fitted matched-feedback exact symbolic control. Each of eight jobs SHA256-seals its own two-world, all-arm, all-prefix intervention transcripts and predictions **before opening that shard's hidden heldout labels**. The Python output in each shard carries exact world IDs, 1024 intervention budget, per-world and per-prefix exact counts, seed and protocol hash, native cold restoration, tamper test and CPU/wall receipt. No cross-shard tuning, post-result source changes or replay.

The aggregate conclusion only exists when all **16 unique** worlds across **eight exactly qualified** shards finish on the same source SHA/tree. The primary measure is full-state exact on 8192 never-seen queries; exact symbolic and same-direct-feedback symbolic remain eligible strongest controls. The 95% high-capacity criterion and >=2pp stronger-control superiority criterion are frozen, but **SCIENTIFIC_PASS=false** until independent reproduction plus complete process-cost/retention/rollout and source controls. The inherited WSP114 evaluator does **not** quantify every preregistered secondary scientific metric, so this v2 development followup does not claim those absent measures.

If the 64-node aggregated cohort misses 95% after a **complete** v2 evaluation, independently preregistered 48-then-32-node fallback can be considered. No lower-capacity experiment has been authorized or started as a substitute for this 1024-first 64-node test.

## Engineering and isolation

The sole numerical writer/learner implementation and its independent symbolic/ridge controls are still WSP114 `native.py` and `controls.py` pinned at parent `5ad70cf8dd2fb32d47afc5df53a8776b53763950`. WSP115 only adds the new independent oracle namespace, world-ID-bound evaluator and fabricated data test. No accepted Yggdrasil, Wingless, Hybrid, FORGE, main, controllers or scheduled tasks changed.

The exact frozen candidate must pass fabricated WSP115 fixture + complete inherited WSP80–115 and root regression Linux/Windows, generated pinned G29 atlas and independent G29 both OS. One-shot v2 shards start **only** when all gates PASS. No original v1 source changes or v1 heldout reuse.

### Fabricated-only fixture

`python -m unittest discover -s research/contrib/chatgpt/WSP-115 -p 'test_*.py' -v`

### Original protected first-use (CI only, after qualification)

`python research/contrib/chatgpt/WSP-115/experiment_v2.py --frozen-v2-shard 0` — each shard index 0..7 runs exactly once via the qualified GitHub workflow and prints its unique first-use receipt.
