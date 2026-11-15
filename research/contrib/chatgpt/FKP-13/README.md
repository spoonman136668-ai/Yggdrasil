# FKP-13 — High-budget true closed-loop intervention learning

**Research-only, separate from Yggdrasil's accepted native model.** Parent: [FKP-12 draft PR #1103](https://github.com/spoonman136668-ai/Yggdrasil/pull/1103), frozen source/learned reward-prediction DEV NO-GO, full dual-OS qualified. Distinct experimental ID, source seeds, model-control question and scientific objective.

## Falsifiable question

FKP-12 showed that directly programmed tokenless weights can improve numerical probabilities when forecasting actual environmental consequences, but its **0.0061 Brier gain** over conventional counts missed the preregistered **0.020** gain threshold and every model tied in raw top-class accuracy. **Predicting a reward is not choosing a better action.** FKP-13 instead makes models **choose actual public interventions**, observe actual consequences, update persistent bounded memory without gradients, and measure whether they genuinely earn more reward than strong trained/online conventional controllers on independent worlds.

**Preregistration is committed FIRST** in `research/contrib/chatgpt/FKP-13/prereg.json`. Never change source-policy parameters, action budgets, splits or thresholds after public original DEV. Keep failures.

## Exact source and capacity

Original MIT `MarcoMeter/endless-memory-gym@a94f2b60d1769ea44df3226561488768e1dff9f4`, `MysteryPath-v0`. No hidden environment path, coordinates, debug renderer, `info`, private state, oracle/held labels or owner-protected source. Public configured native `reward_fall_off=-0.05` and original `max_steps=512`; this is **NOT** the official task default reward benchmark. Original environment code and physics unchanged.

TRAIN worlds 973100–973147 (48×2 source-blind policies ×512 = **49,152 max** native action consequences), VALIDATION worlds 973200–973215 (16×2 ×512 = **16,384 max**), fresh original DEV worlds 973500–973523 (**24 worlds ×9 action-deciding controllers ×512 = 110,592 max**), total **176,128 genuine-source-action cap**. All FKP10/11/12 DEV and training seeds excluded; FKP13 TRANSFER 973600–973631 and owner-protected scientific sources **untouched**.

All learned controllers use unchanged 204-float tokenless visible 8×8 RGB pooled image plus chosen 3×3 action one-hot plus previous *actual* signed reward. They score all nine hypothetical public actions by `0.1 P(positive outcome) − 0.05 P(negative outcome)`, use frozen epsilon=0.2 legal exploration and uniform tie breaks, and choose exactly one action before reading its true reward. The four source-hidden action coordinates are never accessed.

The proposed model directly writes **observed consequence counts to existing 4,096×3 int32 weights (49,152 bytes)** with no gradient. The memory persists across all 24 new worlds. Every world probes cold bit-exact restore, tamper rejection and previously acquired validation-performance retention without reading future source labels.

Nine policies, each with the same original source TRAIN+VAL and legal action opportunities: direct online, strong conventional one-key Dirichlet counts online, fully trained GRU online, direct fixed/no new learning, fully trained GRU frozen, fully trained MLP frozen, uniform random, eight-step random macro, and reward-shuffled fixed direct negative. Conventional GRU and MLP get two initial seeds and **24 full epochs each**, best VALIDATION Brier only. GRU_ONLINE receives only its own actual source outcomes, with one bounded Adam step per 16 native interactions on up to 64 recent public transitions; model parameters persist across worlds. It has a separate compute budget—not falsely presented as equal FLOPs to direct.

**On-policy comparisons necessarily produce different actions and histories.** Every arm starts each world at the same source seed, same public starting distribution and cap. Do not describe source histories as identical across controllers after their first choice. Compare paired returns by world and count actual interventions, rewards, failures, positive progress, terminal goal rewards and whole-process costs.

## Frozen decision and promotion boundary

DIRECT_ONLINE must improve **mean actual public return ≥0.10 per world** over the strongest fully fitted/online/frozen/random arm, with a 10,000-resample world-cluster 95% bootstrap lower bound **strictly above zero**, ≥1.25× strongest positive-progress events, ≥1 real goal reward and no >1 goal deficit versus the strongest. Also require 100% bit-exact cold restoration and no >0.01 previous-validation Brier regression. All requirements are frozen *before* original DEV; no post-result best-of retuning.

Even a winning public DEV signals only `DEV_ACTION_SIGNAL_ONLY`, not `SCIENTIFIC_PASS`. Independent cross-mechanism/world transfer, owner-protected first-use, fully matched compute and native-owner scientific qualification remain unperformed. **Do not merge into accepted `main`**, alter controllers/runners/schedulers, dispatch protected science, or integrate into the Yggdrasil autonomous model.

## Source and regression qualification

Before the one original DEV use, freeze the exact source/GRU/controller/test SHA, source atlas G29 and run source-safe tests plus **full inherited regression on BOTH Ubuntu 24.04 and Windows 2022**. This is a precondition of original first use. The one Linux original DEV performs source-native closed-loop evaluation; Windows only replays already-consumed source-blind TRAIN/VAL and random/macro action traces to certify mechanical source parity—no second independent first use. Preserve negative results in `result.json`/`provenance.json` and regenerate only approved G29 derived files.

Reproduction (once DEV has been consumed; not a claim of fresh science):

```console
python -B -m unittest discover -s research/contrib/chatgpt/FKP-13 -p test_fkp13.py -v
python -B research/contrib/chatgpt/FKP-13/run_dev.py --replay-consumed --upstream-root UPSTREAM_EXACT_CHECKOUT
python -B scripts/build_code_atlas.py --check-if-present
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

Results must report source intervention counts, all nine policy returns, progress, goals, failure incidence, trained-control provenance, protected/transfer exclusion, original CI source SHA, and external contributor evidence class. **Strongest-control ties and negative outcomes remain primary evidence.**
