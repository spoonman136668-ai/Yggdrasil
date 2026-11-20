# GKD-06 — corrected Sachs ZIP manifest, frozen public-data experiment

**Purpose:** Test one already-published original-intervention-condition dataset with the *unchanged* GPT-supplied parent-mask candidate and unchanged strongest conventional controls, after GKD-05 correctly rejected two wrong ZIP member names. No claims of new virgin data, original scientific first-use, native model adoption or causal-effect estimation.

## Source and preregistration

- Published dataset: [Zenodo Sachs v2](https://zenodo.org/records/7681811), DOI `10.5281/zenodo.7681811`, direct ZIP `https://zenodo.org/records/7681811/files/sachs.zip?download=1`, user-provided and publisher-advertised `md5:d50ccd7f88bb3705bcf6eda3978bcc41`.
- Source preview inventory: [sachs.zip ZIP member preview](https://zenodo.org/records/7681811/preview/sachs.zip?include_deleted=0). The actual inventory lists `cd3cd28_icam2.csv` rather than the `cd3cd28icam2.csv` spelling used by the curator description, and `GroundTruth.csv` rather than `Ground_Truth.csv`. All other GKD-05 preregistered experiment and simulation names are unchanged.
- **GKD-05 original attempt remains FAILED / SOURCE_PACKAGING_NO_GO**, no original numeric values were parsed, no model trained, no predictive performance score; [failed original source run #44825472870](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44825472870) and [archived receipt](https://github.com/spoonman136668-ai/Yggdrasil/pull/1348#issuecomment-7051749909). Its preregistration and source are not edited.
- **NEW GKD-06 preregistration FIRST:** `35cc14449fc1acd28ebb7bc16f8638cb9b7477d3`, committed before any original numeric reading. This is the single first numeric public DEV under the corrected file list. Baseline accepted main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` remains unchanged.

## Scientific task and strong controls

Everything except the frozen ZIP member spellings remains identical to GKD-05. Five genuine experimental-condition datasets FIT, two VALID and two previously unseen published conditions DEV. Five curator-described **simulated** conditions and `GroundTruth.csv` are strictly excluded from training and scoring. The assistant's four proposed protein-target parent masks are only hypotheses, not ground truth; the assistant had prior public documentation exposure.

A pooled five-group, FIT-only standardized regression predicts each held-out condition's target using **the other ten simultaneously observed proteins from that cell**. Conventional full-ridge, 65-feature quadratic ridge, FIT-only top-two-correlation ridge, exact same-mask fitted ridge, sham-parent and constant-target baselines all consume the same FIT examples and VALID selection. Six frozen alphas; no DEV-based selection or postresult tuning. The original fixed threshold is donor >=5% better than the VALID-selected strongest conventional arm and >=5% better than sham, with no >5% group-target losses and at least 6/8 nonregressions. See [prereg.json](prereg.json) for exact identities, scores and failure conditions.

**Important:** This is group-shift *conditional prediction*, not intervention-effect identification, causal discovery, action-consequence learning, or a native Yggdrasil model test. Even if the donor passes this historical public DEV, it cannot establish scientific superiority or general intelligence without genuinely held-out independent source and matched trained replication.

## Code custody and tests

[GKD-06/run.py](run.py) is a narrow provenance-checked adapter around the **unchanged** GKD-05 `admit.py` and `score.py` code (Git blob SHA-1 `7f95b1ad1244b43884cdfa5b473d979456843016` and `b5cae9715859b9406b65d889e640686378581573`). It changes *only in-memory frozen source-member names* and the resulting experiment ID. It fails closed if upstream bytes, candidate mask, splits, alphas or MD5 drift. No duplicate model implementation or scoring logic.

`python -B research/contrib/chatgpt/GKD-06/run.py --selftest` runs source-free on GitHub-hosted Linux and Windows with the mandatory full native Python regression, existing GKD01–05 checks and G29 pinned atlas. A **single exact-commit-subject gate** on GitHub-hosted Linux runs `--score-public` once, after offline qualification and without owner runner or paid API. It first validates ZIP MD5, archive content inventory, headers and numeric row counts; if any differ, fails closed *before fitting or scoring*. If valid, runs once and records all conditions/target scores regardless of whether the donor loses. No source rerun after results, no protected Yggdrasil #426 first-use.

**Completion criterion:** a source-identified historical-public DEV result **or** a source-admission NO-GO, followed by exact-final regression and full immutable evidence/provenance in this PR. SCIENTIFIC_PASS remains false.
