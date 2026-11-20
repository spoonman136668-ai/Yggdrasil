# JEPA2 view-disagreement reset-trigger diagnostic (posthoc, whitebox)

Independent research contributor, **not** the Unified Causal Intelligence Amalgam training/integration coordinator.

This adds **no new source event or training data**. It cold-restores two *already consumed* original and continued JEPA2-05 native models from the existing Git-pinned archives and replays the *authentic* 16-event continuation in source order. At each next event, it clones the exact pre-update native state and toggles **only** the second public view's projected bit in a disposable one-event negative control, holding the first view, action, state, reward, and old trained model fixed. It compares pre-update `_accept` likelihood, detector score, reset decision and detection receipt; then discards the altered branch and continues **only** the original source-observed event. Both old and final authentic native checkpoints and original published Brier scores must reproduce to the existing diagnostic tolerance.

The altered public view violates the genuine `YGG-JEPA2-05/source.py` overlapping latent-state construction and may violate state continuity. Therefore this is **a mechanism-level white-box diagnostic only**, not a legal external causal intervention, not evidence about a new source law, and not an Amalgam admission. Even if the immediate reset is invariant to current-event `views[1]`, earlier historical paired-view differences can still modify trained weights and future reset likelihoods. A different synthetic current-event second view creates a different disposable model state; there is no claim all downstream predictions are invariant.

The original consumed development remains `DEV_NO_GO`; this test claims `science_pass=false` regardless of outcome. Do not promote/checkpoint/import into Amalgam. Avoid duplicating CAP04/LR-92AP original first-use research.

Original model source pin: `7b0d9fd8c16b8e0433a632666cec88d8d008c19f`. Existing original archived replay `research/contrib/chatgpt/YGG-JEPA2-05-RESET-POSTHOC/diagnose.py` already verified across Linux/Windows. This standalone diagnostic is **new exploratory posthoc implementation**, not a prospective preregistered scientific experiment.

Run from the existing research branch:

```
python -B research/contrib/chatgpt/YGG-JEPA2-05-EVIDENCE-REENTRY-POSTHOC/paired_view_reset.py --platform linux --output result.json
```
