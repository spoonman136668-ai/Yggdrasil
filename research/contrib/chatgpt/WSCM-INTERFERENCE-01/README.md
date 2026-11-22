# WSCM-INTERFERENCE-01 — Localize failed native retention to public causal cells

**Decision: research-only forensic finding; functional memory improvement UNVERIFIED.** The preceding WSCM-REVIVAL-AUDIT-01 found an A→B→A recent-loss gate failed in the second changed stage on all three development replicas. This gate asks **where the underlying native forecast changed harmfully**, rather than tuning that failed gate.

## Source and scoring custody

- Coordinator parent <https://github.com/spoonman136668-ai/Yggdrasil/pull/1278> at `86264b41a08d49f558418c0fba367f3a2636befa`, unchanged. Contributing research PR <https://github.com/spoonman136668-ai/Yggdrasil/pull/1364>.
- Reuses the same **216 previously consumed public development events**. Original staged-retention trace Git blobs: seed 818621 `7b3f2ff0b120d6557d4630de3461276d892b503f`; 818653 `bac19fb71d2a9918bd4ede1d3f2e6bae7b81dc48`; 818687 `449a186109b0b30ec98352b5b4565e2e96435b14`. The auditor checks each source blob before parsing; source files are not copied or changed.
- Prequential `pinned`, `unguarded`, `fit_full`, `fit_trailing` and `fit_change_point` forecasts are paired against the *same actual observed outcome*, split into **transition** `s2` and **reward** `y`. Public context is `views[0][0]`, action is `row.x1`. Hidden regime identifiers are not used as predictors; the original experiment's stage label is used only for retrospective reporting.
- Each cell's delta is `Brier(unguarded) - Brier(pinned)`; positive values mean continued native training made predictions **worse**. Values are exact integer squared-loss aggregates scaled by `1e12`, rounded at final reporting. Results are descriptive, not significance tests.

## Paired result: second changed stage

| Public cell | Source episodes | Pinned transition Brier | Continuing transition Brier | Delta |
|---|---:|---:|---:|---:|
| Context 0, action 0 | 18 | 0.060362 | 0.194358 | **+0.133996** |
| Context 0, action 1 | 15 | 0.121993 | 0.255956 | **+0.133963** |
| Context 1, action 0 | 18 | 0.177623 | 0.179088 | +0.001465 |
| Context 1, action 1 | 21 | 0.141461 | 0.128134 | −0.013328 |

Context 0 aggregate over 33 observations: **0.088376 → 0.222357, +0.133981**; context 1 over 39: **0.158152 → 0.151651, −0.006500**. Overall second-stage transition Brier **0.126171 → 0.184058**, change **+0.057887**. The context-0 harm is partially offset by context-1 improvement, rather than uniformly corrupting all cells. All three independent original development replicas exhibited positive context-0 transition deltas (+0.126340, +0.165524, +0.124864), though this is a previously consumed cohort and not an independent new result.

The same-stage reward Brier slightly **improved overall** (0.212655 → 0.204395); the observed failure is more specific to the transition target.

In those already consumed context-0 transition rows, the preserved native predictor is also numerically better than the recorded `fit_full`, `fit_trailing` and `fit_change_point` controls; those control comparisons are **descriptive only** and are not fresh prospective trained-control superiority.

## Mechanism interpretation and limitations

The source implementation `yggdrasil/native_episode_experience.py` already stores context-specific transition counts (slots 0–1) **and** a pooled transition bank (slot 2); `_append` updates both, and `forecast` selects using a shared cumulative transition loss. Whether pooled-count contamination, shared-loss switching, repair, finite-sample noise, or another path caused the measured regression **cannot be inferred from two prequential forecast columns**. No causal root cause or causal benefit of a new patch is asserted.

A meaningful successor is a *single-learned-state, context-and-target-scoped counterfactual readout* that independently scores `full=True` versus pooled forecasts on exact cold-replayed native descendants, then tests a bounded local update/restore against the preserved learner and fully fitted conditional Bayesian controls. Freeze this before any new prospective source draws. **Do not tune a third global loss router on these consumed rows**; preserve original held split, source authority, paired interventions, full regression and separate owner promotion gates.

## Reproduction

```sh
python -B -m unittest discover -s tests -p test_wscm_interference01.py -v
python -B research/contrib/chatgpt/WSCM-INTERFERENCE-01/audit.py \
  --repo . --out /tmp/wscm-interference-01.json
```

- Local CPython 3.13.5/Linux: **10/10 synthetic audit-unit tests PASS**; byte compilation PASS. The committed source and tests have exact Git blob parity with these tested files.
- Real historical trace aggregates were computed **read-only through the authenticated GitHub connector** with each source blob pinned; the Python implementation was not executed end-to-end on the complete original repository checkout in the local sandbox. `result-summary.json` contains the per-cell/per-arm metrics and all source pins.
- This diagnostic is **retrospective, unpreregistered and observational**. No first-use data, new training, protected source actions, inference pipeline changes, native weight/Genome writes, CI runner or accepted-branch edits.

**ENGINEERING:** source-free unit tests PASS; inherited exact-candidate full Linux/Windows regression UNVERIFIED. **SCIENTIFIC:** transition interference localized retrospectively; functional retention/transfer improvement UNVERIFIED. **DEPLOYMENT:** UNVERIFIED, draft research PR only.
