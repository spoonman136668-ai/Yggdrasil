# WSCM-PROBE-01 — Evidence-driven historical causal-function revival

**Status: SOURCE-FREE DEVELOPMENT ENGINEERING PASS; SCIENTIFIC GAIN UNVERIFIED.**

This is one completed bounded contributor trial inside existing draft [Yggdrasil PR #1364](https://github.com/spoonman136668-ai/Yggdrasil/pull/1364), whose stable research base is the unified [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) head `86264b41a08d49f558418c0fba367f3a2636befa`. Neither accepted `main` nor production native learner is changed.

## Custody: frozen before scored outcomes

1. Development preregistration committed **first** at `83661c0c8bcf6a3cc48dcf9d691b38050ebb9dd2` (Git blob `613c4d37f4ca76934658ee3d40ea13f4d8126706`).
2. Locally tested source, scorer and negative tests were cryptographically frozen *before the one scored execution* in Git commit `4563a44a5de9850e26ef9082790ac5eeedc36a48`, `candidate-freeze.json` blob `ea5be911343f6160124e62708d3966a89738bc55`. At that moment **only cryptographic hashes**, not the full source files, were already in GitHub. All later source file Git blobs must exactly match those prior SHA commitments. No scoring seed had been used.
3. The **first and only** scored development run used the frozen sources, was given no hidden regime labels and completed all original 4 seeds / 288 source-free public outcomes. It wrote one immutable STARTED marker and one COMPLETED receipt per seed, plus a final result. No rerun, tuning, added budget or rescue.
4. Exact frozen source files, tests, receipt archive and machine summary are subsequently attached to this same research PR for owner reproduction. Original parent native episode Git blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`, original typed version sidecar blob `de9fe9a25a575379286425d81e9a490da7b913fa`; execution imported original native episode code using **limited source-equivalent native_context_basis/PublicCausalCells shims**, not the full parent dependency tree.

## Actual experiment

On an **already-investigated synthetic repair fixture** (48 native source-free witnesses plus the original three-event contradictory repair), the original native history contains a real repair receipt preserving the old transition `P(s2=1)=1/26` and the replacement `P(s2=1)=4/5` at public context 0/action 0. `probe.py` retrieves both exactly, without an oracle label. It proposes the public action with maximum frozen difference, updates an exact rational posterior with a preregistered symmetric `1/16` switching hazard, and preserves the mixture with the original source-bound native checkpoint after every stage. For the other context, both versions are observationally indistinguishable; the agent **abstains** rather than guessing its regime.

Fresh development seeds `96211,96221,96229,96253` each receive 24 observations under B (4/5), 24 under familiar return A (1/26), and 24 under unrelated public context C (9/10). One action and outcome per step; all readouts use identical witnessed actions/outcomes, and scenario labels are only in the **harness**, never the retrieval model. Equal-information controls include continuing original native, full-history Beta, trailing-32 Beta, fixed old/reset, and an **independently coded conventional exact two-state Bayesian HMM** using identical model likelihoods and hazard.

## Measured result — mean prequential transition Brier (lower is better)

| Development phase (96 public outcomes each) | Causal version diagnostic | Exact two-state Bayes | Continuing native | Fully fitted cumulative Beta | Fixed-old / fixed-reset |
| --- | ---: | ---: | ---: | ---: | ---: |
| B confirmation | 0.233049 | **0.233049 identical** | **0.223262 better** | 0.392788 | 0.664941 / **0.208750** |
| A familiar return | **0.115419** | **0.115419 identical** | 0.192581 | 0.140364 | **0.059172** / 0.602500 |
| C unrelated, unidentifiable | 0.096094 | 0.096094 | 0.096094 | 0.096094 | 0.096094 / 0.096094 |

- After 8 B observations, old-posterior <=20% on **3/4** seeds (the fourth was 25.18%). After 8 A-return observations, old-posterior >=80% on **4/4** seeds (**97.8–98.3%**).
- The retrieval candidate is **exactly identical** to the independently coded conventional Bayesian HMM on **288/288 prequential predictions and posterior updates**. Thus it has **no demonstrated superiority to Bayesian inference**, no novel intelligence gain, and no basis for scientific promotion.
- **192** observations of the informative public transition; **96/96** different-context observations abstained from causal version diagnosis. The context-C forecasts were shared with original native rather than presented as generalized structural transfer.
- All **12/12** scheduled stage-boundary cold checkpoint restores reproduced the exact original native+version+posterior bytes and forecasts. No original native production file was modified.
- The candidate's A-return Brier was lower than continually trained native (0.115419 vs 0.192581), but higher than the fixed old predictor (0.059172). The fixed old predictor's stage-specific advantage is a descriptive bound, **not** an online label-free policy. In the B confirmation stage the candidate also lagged continuing native and reset fixed control. This is a positive *functional revival* engineering check only, not a broad memory-quality win.

## Exact outputs and reproducibility

`sealed-results.tar.gz`: nine original immutable write-once records (four STARTED, four COMPLETED, one final `result.json`). Git blob `5180f69dffdda4009db5ab037aa045324249dee4`, SHA256 `fd2eda4ded51785bb9d9b71c98f578a60624d5e99bcf31e2131c413eeb59b285`. The final original `result.json` SHA256 is `d9cf1345c4e436456fea641e0dbadc92217ca84653ee60a0d6142c2cd957e438`. Machine-readable aggregate and per-seed metrics are in `result-summary.json`. All generated observations are source-free synthetic, not protected first-use.

`tests/test_wscm_probe01.py`: **12/12** isolated focused tests PASS (Linux CPython 3.13.5). Existing compatible suites: archived cold 8/8, structural readback 9/9, versioned copy-on-write 14/14. **43/43 local focused regression tests PASS** with authentic archived 1,025-witness fixture, no skips. This is **not** the mandatory complete exact candidate Linux/Windows regression, no CI run was invoked, and neither original full source dependency tree nor independent owner/runner acceptance was qualified.

Example **only for inspecting the already consumed results, not replaying seeds**:

```sh
mkdir -p /tmp/wscm-probe01-receipts
tar -xzf sealed-results.tar.gz -C /tmp/wscm-probe01-receipts
sha256sum /tmp/wscm-probe01-receipts/result.json
python -B -m unittest discover -s tests -p test_wscm_probe01.py -v
```

## Decision

**ENGINEERING:** prereg/source custody and single completed four-seed run PASS; 43 focused local tests PASS; true cross-platform final regression UNVERIFIED. **SCIENTIFIC:** conditional source-free old-function revival demonstrated, but mathematically identical to strongest exact Bayesian HMM and not better than all matched readouts; independent unfamiliar transfer and intelligence gain **UNVERIFIED**. **DEPLOYMENT:** UNVERIFIED; draft/unmerged; original native overwrite remains intact in production.

The highest-value next problem is **representation and causal-memory generalization beyond a single known repaired cell**, with an informative-action budget, unfamiliar structures, independent original native full dependencies and fully trained matched baselines. Avoid repeating consumed W16/epoch historical-loss studies and do not promote this single-cell Bayesian behavior as a novel memory breakthrough.
