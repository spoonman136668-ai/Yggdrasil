# YGG-RET01 — evidence-bound readout retention in cumulative native Yggdrasil

**FROZEN BEFORE SOURCE/IMPLEMENTATION:** prereg commit `91100fa70086e5c1b2bc604da07c98dbe70af9e4`. Exact qualified prior native+six-head source: `65a69d2733c18910178e1b7443332fddfd6bab89` (JEPA2-04 PR #1280, dual-platform engineering PASS, development NO-GO). This draft does not merge or promote either source.

**Hypothesis:** a native causal learner can keep learning across domains **without forgetting the reliable original readout** if it retains an immutable cold-pinned readout archive and uses only witnessed public action-consequence likelihoods to arbitrate between archived and current contextual predictions.

The actual previously trained native state (942/917 causal episodes across two independent original cohorts) **continues** with 64 additional *new* public observed action-consequence episodes per cohort in two new disjoint synthetic development worlds. Its original native memory and four earlier trainable causal-predictive heads continue updating. Both separately trained 3-step future-head weights persist in the state unchanged, because this specific readout experiment does not furnish prospective 3-step target sequences. Original native source epochs and inherited learned weights remain intact.

A pinned original native readout archive (702/677 episodes, prior JEPA2-03) receives **no** learning updates; the Bayesian reader begins with archive weight 1/8 and updates after each revealed observed transition+reward using only public evidence, without hidden A/B/A regime tags or evaluator labels. Old-source direct readout and live-context predictions are compared with fixed-half mixture, intentionally mispaired update, online full/window24/window32/discount95 Beta count controls, chance and gated readout.

**Separate evaluation dimensions:** the new-source A/B/A prequential late/return-Brier measures actual development adaptation against the strongest fitted baseline. A separate 32-event **already-consumed** historical old-source diagnostic tests archival readout preservation and post-evidence model arbitration without retraining either learner on those examples. This second diagnostic **is not held science**. Pre-set Brier/margin/retention guards on BOTH original seed replicas make acceptance falsifiable. Failure is preserved without tuning or rerunning scored data.

Source hash and original trained-model Git blobs are pinned in `prereg.json`. Frozen source: `source.py`. Candidate: `yggdrasil/native_readout_retention.py`. Protocol: `campaign.py`, independent `audit.py` and `seal.py`. Results and full model checkpoints will be recorded under this folder, not as chat attachments.

**Status:** source, model, tests and protocol committed to an isolated branch. Engineering preflight is the active gate; **neither source training nor science has been claimed**. No accepted `main`, Forge controller, paid API, scheduled task, owner's protected first-use, other model, or deployment is modified.

## Frozen two-platform preflight proof

[Run #44435011018](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44435011018) **COMPLETED SUCCESS, Linux and Windows original prior-source pins and all focused readout/JEPA compatibility and cold tamper tests passed**. No model code, original native state, source generation, training controls, frozen metrics, thresholds, seed identity or preregistration changed after this preflight. The next commit is a README-only trigger for the single original frozen development training comparison.
