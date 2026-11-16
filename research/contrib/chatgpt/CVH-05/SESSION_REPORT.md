# CVH-05 — Real-source sixfold falsification: plain-English research report

**Date:** November 16, 2026  
**Research line:** Yggdrasil native tokenless earned-return memory  
**Candidate:** unchanged CVH01 `EarnedReturnMemory`; original source author CausalAILab/Causal-Gymnasium.  
**Status:** **ENGINEERING development source-safe PASS**, **RETROSPECTIVE ROBUSTNESS NO-GO**, **SCIENTIFIC PASS FALSE**, **DEPLOYMENT NONE**.

## What the real experiment found

CVH04 reported a 5.1% lower prediction error than the training-only global-return prior on its **one** split of actual independent Causal-Gymnasium observations. CVH05 tested **all six possible** two-episode training/two-episode held combinations from that same previously consumed original 124-action source evidence. This answers whether the earlier result was a stable feature of the available records or fragile to the training split.

**The gain failed to generalize.** In only **3/6** splits did the native return-memory estimator beat the weak prior. Across all **333** supported predictions (of **372** repeated/overlapping held evaluations), its pooled MSE was **0.271928164667**, compared with **0.258786728000** for the global prior. Native error was thus **0.013141436667 higher**, approximately **5.08% worse**. The worst split lost **0.073670551763 MSE**.

| Frozen pair used for 62 TRAIN source actions | 62 held predictions supported | Native MSE | Global prior MSE | Native gain (prior − native) |
|---|---:|---:|---:|---:|
| 996100 + 996101 (original CVH04) | 55 | 0.278320 | 0.293238 | **+0.014918** |
| 996100 + 996102 | 58 | 0.395355 | 0.321684 | **−0.073671** |
| 996100 + 996103 | 56 | 0.238295 | 0.240317 | **+0.002022** |
| 996101 + 996102 | 56 | 0.269816 | 0.267811 | **−0.002005** |
| 996101 + 996103 | 55 | 0.223275 | 0.186614 | **−0.036661** |
| 996102 + 996103 | 53 | 0.218482 | 0.239080 | **+0.020598** |

The learning mechanism kept its data intact: all six candidate checkpoints cold-restored, all original train address counts and return totals were retained after ingesting historical held rows in a **separate** development copy, and no unsupported CVH01 context was passed off as confident learned knowledge.

### Stronger conventional controls

The separately implemented **exact source-informed conventional batch estimator tied the native candidate on all 333/333 supported predictions**. That means the new algorithm does not yet outperform the simplest exact equivalent conventional computation.

A separately fitted **four-cell** table (just observed current binary state × binary action, learned from the same two source TRAIN episodes, with two training-only global-prior pseudo-counts) was better on this small sample: across six folds, mean all-row MSE **0.227323148283** versus **0.272760957614** for the native candidate with explicitly marked global-prior fallback. Training-only global-prior mean MSE was **0.260997252211**, and 36-slot Bayesian shrinkage mean MSE **0.261559093439**. These are **all-row** MSE metrics, not the earlier selective-coverage comparison. They are correlated retrospective evaluations of four worlds and cannot establish future performance, but they strengthen the NO-GO against premature model promotion.

### Off-policy limitation

The original FKP24 behavior policy deterministically selected action `(public_before + current_episode_step_index) % 2`. At **each of the 124 actually observed unique source histories**, the action *not* taken has **no measured reward**. Two hypothetical assignments setting all such unknown rewards to 0 or 1 both preserve every recorded observation, yet disagree about all 124 unmeasured rewards. These are mathematical **data completions**, not two verified underlying original MDP causal laws. Thus, the source log alone cannot prove that a different selected-action policy would earn more reward. Offline return prediction is not policy evaluation or causal intervention discovery.

## Source and scientific integrity

- True external original-source data were previously produced by FKP26 [PR #1158](https://github.com/spoonman136668-ai/Yggdrasil/pull/1158), GitHub [#43930489602](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43930489602), independent source `CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf`, exactly **124 physical `do` actions**, four fully consumed seeds.
- Frozen CVH05 preregistration **FIRST commit `75abed7e43f04d23cf54ae2ed34130c8a4c46a54`** before new code/evaluation/results. CVH04 exact qualified parent **`5836c5dcdb74a8a1a7c5c32097d02ee955a4b2c3`** and all original source hashes unchanged.
- `CVH-05/result.json` preserves sixfold scores, controls and negative. CVH05 independently recomputes and requires the original CVH04 result: native **55/62**, MSE **0.278320065227**, prior **0.293237912094**, fixed SHA receipt `44f3f62ad48369448d2126154a482b2d215d94a6c19f8c3ad8024339ec5123f7`. No post-outcome tuning of that or this frozen hypothesis.
- The Python result payload SHA-256 across Ubuntu/Windows after *report-only* 12-digit normalization is **`44363bc2b710e40118025dd9def024f1375862f041d9180710b264d168265d08`**, calculated after all frozen raw comparisons. All six controls/negative outcomes reproduce on both OS without new source first-use.
- **Zero new original CausalGym reset/do calls**, zero protected scientific DEV or TRANSFER, no prior consumed seeds replayed in the original source, no source-private future outcome or hidden confounder seen. No accepted-main, native model, FORGE, Wingless, Hybrid, KTRADE, owner loop, runner, controller, scheduler, or paid API modifications.
- Retrospective cross-split estimates are **not independent prospective trial replications**. The same four worlds appear across folds. A sixfold negative does not establish the general impossibility of this memory architecture, only lack of robustness on the supplied genuine source evidence.

**Next meaningful scientific operation:** design and qualify a *disjoint*, prospectively sealed external causal action environment; fit the native and strongest fully trained conventional/policy competitors on identical public information and per-arm actions/compute; test their **executed decisions, actual earned return, cold memory, unfamiliar causal family transfer and whole-process cost**. Owner permission is required before any genuinely new protected or external scientific first-use. Do not turn this failing four-world audit into a positive by rerunning/tuning its already consumed source.

## Qualification

Cross-platform source-safe development PASS at [run #43962205011](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43962205011), original native model unchanged. Final exact-SHA root regression and independent G29 recorded in the draft PR qualification receipt after completion; do not claim them as completed based on this report alone. This report is pre-final-G29 and intentionally retained unchanged during same-tree final qualification.
