# PCER-02 — Conditional-outcome-stratified witness replay

**Status:** Frozen research-only successor to the [PCER-01 DEV_NO_GO](https://github.com/spoonman136668-ai/Yggdrasil/pull/1360). Engineering-only selection of 10 of 50 archived FIT witness IDs, not fresh science and not a native learner improvement. Coordinator remains [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278). G41 [PR #1329](https://github.com/spoonman136668-ai/Yggdrasil/pull/1329) and all original owner checkpoint refs are untouched.

## Method and authority

[Preregistration](prereg.json) was independently frozen in commit `ede3c45e3de75eda6efeca05a299aa3f622b26d2` before the selector implementation or any PCER-02 source-data evaluation. Existing Amalgam archived source `selection-dev-01/trace.json` is 96 **already-consumed synthetic** native prequential witnesses (sha256 `36f535c451c813dd56afd58c4f1833ac8e5fca98627d898a571e40c8bc8a0114`). This candidate reads **only indices [0,50)** for outcome selection and training-fidelity diagnostics. The 14 previous VALID and 32 previous familiar-return HELD observations are **not re-scored**. There are **zero fresh original-world actions**.

The deterministic selector exhaustively searches the allocation of 10 references across four public (context, first-action) cells and binary outcomes. It minimizes (1) worst absolute deviation from the full FIT Beta(1,1) conditional posterior, then (2) cell-frequency-weighted squared deviation, then (3) negative prequential residual utility, then (4) chosen IDs. It chooses individual within-cell/outcome references by the already archived native residual. Original 96 witness rows remain losslessly in their source file. Returned IDs are only a bounded **active index**; full archived bytes, actual model RAM and persistent checkpoint size do **not** shrink.

**The required conventional comparator matters:** for this exact tabular Beta estimator, four positive counts and four total counts reproduce full-history conditional probabilities exactly, using no retained individual witnesses. A replay index cannot claim superiority over this sufficient-statistics control without measuring a distinct native capability that requires individual witnesses. Uniform 10, pure-error 10, predecessor 70/20/10, full 50, and sufficient statistics are all declared in the frozen protocol.

## Execution

From an isolated exact branch checkout (Python standard library; do not run protected original source):

```bash
python -B -m unittest discover -s tests -p 'test_pcer02.py' -v
python -B research/contrib/chatgpt/PCER-02/selector.py \
  --source research/contrib/chatgpt/CAUSAL-AMALGAM/selection-dev-01/trace.json \
  --prereg research/contrib/chatgpt/PCER-02/prereg.json \
  --index /tmp/pcer02-new-index.json
```

The index output path must not already exist. `selector.py` verifies source SHA, validates FIT identities/public shapes, chooses a bounded index, cold-recomputes, and verifies source bytes unchanged. It does not write any native checkpoint or invoke an original environment. `test_pcer02.py` contains only source-free engineering fixtures and negative/tamper controls.

## Classification and stopping rules

A successful FIT-only max probability gap <=0.10 and 80% fewer active references is **ENGINEERING_FEASIBILITY_ONLY**. It is *not* evidence of held predictive gain, native retention, unfamiliar-family transfer or actual reduced RAM. Any failed integrity/capacity/fidelity check gives engineering NO_GO. A scientific decision requires a separately owner-admitted fresh unseen source cohort under [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426), matched fully trained controls, cold native restore, unchanged source budgets and a new independent qualification. **Do not re-score the consumed PCER-01 held windows or tune this policy after reading them.**

**No merge, production integration, owner-controller/runner dispatch, original-world first-use or G41 edits are authorized by this proposal.**
