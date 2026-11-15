# FKP-15 — Learned action choice, not privileged branchability

**Research-only stacked on FKP-14 [draft #1105](https://github.com/spoonman136668-ai/Yggdrasil/pull/1105).** This is the first prospective attempt to convert FKP-14's real 16-step branch headroom into a **one-action decision rule on unseen public worlds**. It does NOT train or alter accepted Yggdrasil, its autonomous controller, or production runtime.

The FKP-14 source audit physically replayed nine possible actions from the exact same public history. It achieved **128/128 return contrasts** and an unattainable hindsight best-of-nine advantage of **+0.23125 native reward** over fixed random, but **only one observed terminal goal** across 128 16-step anchors. A learner cannot inspect the unchosen eight outcomes. FKP-13's earlier myopic online numeric controller was beaten by a shuffled negative; FKP-15 attempts to learn *delayed* 16-step public action values, not an immediate reward estimate.

## Frozen before any original source first-use

`prereg.json` is committed BEFORE this implementation. Exact original MIT source `MarcoMeter/endless-memory-gym@a94f2b60d1769ea44df3226561488768e1dff9f4`, unchanged physics. Original public task is `MysteryPath-v0` with declared native `reward_fall_off=-0.05, max_steps=512`; **not the benchmark's official default reward**. No private layout/goal, `env.unwrapped`, `info`, debug render, oracle hints, or hidden position.

Fresh source worlds: **TRAIN** 975100–975163 (64), **VAL** 975200–975215 (16), **original public DEV** 975500–975531 (32). Four physical source-blind public action prefixes 0,16,32,64 and nine real native macro action pairs repeated up to 16 steps. The prefix is reset/replayed and byte-compared across alternatives. Budget **≤358,400 true env.step actions**; report actual cost. Former FKP10/11/12/13/14 consumed worlds, FKP14 transfer reserved 974500–974563, FKP15 transfer reserved 975600–975663 and protected science are all EXCLUDED.

Every model sees exactly the same fully paid real TRAIN nine-branch consequences. This includes the model input: RGB source observation sequence, the model's public previous action and true previous reward, pooled into fixed 8×8 RGB (192 values), nine prior-action symbols, and three signed-outcome indicators (204 floats per frame). A deterministic public visual/context summary averages at most the last eight historical frames. Fully trained GRU additionally uses the *whole* public prefix sequence; do not assert exact representation/compute equality to a vector model.

**Direct candidate:** fixed **4,096×9** numerical action-value memory, learned int32 counts + 1,000×return accumulated int32 weights, **294,912 raw bytes**, two independently seeded visual-context projection hashes, additive smoothing toward source TRAIN action means. Exactly one non-gradient numeric write per observed real TRAIN branch/action. No DEV adaptation, no additional capacity, no private source. Full bit-exact cold restore and tamper rejection.

**Matched-source strong comparators:** one-hash conventional count action values, 64-hidden trained GRU over temporal source observations, trained MLP 64×64, ridge trained on TRAIN with validation-only regularization selection, TRAIN-only kNN (1/5/15 validation choice), global per-action prior, deterministic random legal choice, and shuffled-TRAIN-outcome negative. GRU and MLP each train **all 24 epochs × two independently frozen seeds**; choose best checkpoint on VAL nine-action return MSE only. All train and selection complete before the original DEV `env.reset`.

**Blinded actual DEV action evaluation:** First read only the real public history at each fresh unseen DEV anchor. Have all models choose and seal ONE of the nine real 16-step actions. Only THEN, as a distinct evaluator action, physically replay nine source branches to determine each method's real chosen-action outcome and retrospective privileged ceiling. The learner **never sees unchosen future outcomes**. Valid source comparisons are paired by 32 independent worlds, not 128 independent anchors. No model is retrained from DEV.

**Frozen criterion:** Candidate must earn ≥0.05 more mean actual 16-step return than strongest trained noncandidate (reselect comparator in each world-bootstrap), with 10k world-cluster bootstrap 95% lower CI strictly>0, ≥0.10 less oracle regret, no positive-return choice rate drop, valid contexts in ≥24 worlds, raw source best-vs-random gap >0.05, and cold/tamper PASS. Record actual rare goals but do not demand a statistically implausible goal success gate. No metric/feature/seed/threshold retuning after first-use.

A passing public DEV may establish only `DEV_ACTION_VALUE_SIGNAL_ONLY` — **never `SCIENTIFIC_PASS`**, native promotion, cross-family unfamiliar causal transfer, action-consequence intelligence, or whole-process compute superiority. Unfamiliar source family, new transfer conditions, true multi-step adaptive choices, fully compute-matched strong baselines and separately authorized owner scientific evaluation are subsequent gates.

### Qualification sequence

Prereg commit FIRST → frozen original model/control/test SHA → G29 source atlas generated-only child → Linux and Windows source-safe fixture + mandatory full inherited regression **BEFORE original DEV** → one Linux public original DEV + source receipts → Windows replay ONLY consumed public source → archive actual positive/null result (never tune) → mandatory exact-tree full final regression on both platforms.

The shell entry point below is **source-executing** and must not be rerun as virgin after original development has been consumed:

```text
python -B research/contrib/chatgpt/FKP-15/run_dev.py --public-dev --upstream-root PINNED_MEMORY_GYM_CLONE
```

Everything is scoped to `research/contrib/chatgpt/FKP-15/` plus three generated `.ice/code-atlas.*` files. No native main ref, runner, scheduler, autonomous loop, paid API or owner-protected source is touched.
