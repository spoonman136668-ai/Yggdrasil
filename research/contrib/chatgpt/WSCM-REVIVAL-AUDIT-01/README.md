# WSCM-REVIVAL-AUDIT-01 — Actual native forecast history, retrospective selector

## Disposition: RETROSPECTIVE_SELECTOR_NO_GO

This gate checks a *stored causal function revival decision* using **prequential forecasts already produced by Yggdrasil's real integrated native learner**, rather than fabricated candidate predictions. It does not train new weights, interact with a source world or authorize promotion. The original 216 episodes (3 seeds × 72) were already consumed and inspected; these results are **UNPREREGISTERED**, not fresh independent science.

### Exact source identity and owners

- Parent research coordinator: [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), head `86264b41a08d49f558418c0fba367f3a2636befa`. WSCM is a research contributor only: [PR #1364](https://github.com/spoonman136668-ai/Yggdrasil/pull/1364).
- Source traces: `research/contrib/chatgpt/CAUSAL-AMALGAM/staged-retention-dev-01/seed-818621/trace.json` (Git blob `7b3f2ff0b120d6557d4630de3461276d892b503f`), seed 818653 (blob `bac19fb71d2a9918bd4ede1d3f2e6bae7b81dc48`), seed 818687 (blob `449a186109b0b30ec98352b5b4565e2e96435b14`). Auditor verifies exact Git blobs, not just file names.
- Source policy: `selection_protocol_dev.json` (blob `ff2615f4923ad9da9b0a13de14470044f280e1c4`) specified window 16, minimum count 4, selection gain 1/100 **before this retrospective assessment**. These are reused unchanged, rather than tuned to this result. Source staged protocol blob `1bbc1672ccd80f248c86c5ec7482f6ade8a0d76a` defines stages.
- Existing forecasts per row: `pinned`, `unguarded`, `fit_full`, `fit_trailing`, `fit_change_point`, `guarded`, all produced **before that row's outcome**. No regime identity, stage label or next outcome enters selector choice. Stage label is used only for after-the-fact score grouping.

### Read-only decision rule

Before a row, compare the **mean equal-weight transition/reward Brier** over the previous maximum 16 **already revealed** episodes. With at least 4 such episodes and an average gain of ≥0.01, choose the continuously updated `unguarded` native forecast. Otherwise retain the frozen `pinned` forecast. The forecast bank and actions are fixed and shared; this code does not modify or recompute native weights.

The fitted full-history/trailing/change-point controls are reported side by side. The **best per stage** fitted number is selected post hoc for descriptive context only, and must not be presented as a deployable online comparator or a prospective matched win.

### Result (lower Brier is better)

| Stage | Frozen native | Continuing native | Revival selector | Best per-seed fitted control (post hoc) |
|---|---:|---:|---:|---:|
| First changed law | 0.301633 | 0.172604 | 0.180111 | 0.170896 |
| Second changed law | 0.169413 | 0.194227 | **0.199188** | 0.225300 |
| Familiar return | 0.129036 | 0.143066 | **0.132622** | 0.122883 |

These are means of three source-identified seed scores, each stage 24 historical episodes per seed. The revival selector chose the updated model on **60/72** first-stage episodes, **36/72** second-stage episodes, and **3/72** return episodes. During the second change it was worse than the frozen model on *all three seeds*. On familiar return it was worse than frozen on two seeds and tied on the third. Those negatives demonstrate a functional selection failure despite retention of the original 1,025 witnesses; they do not establish that the underlying true causal structure was forgotten.

### Engineering and science status

- Source/readout analysis executed read-only using the GitHub-connected trace files and exact-integer squared-loss comparisons.
- Python reproduction script: `audit.py`, Git blob identity pinned against parent forecast traces. **Nine unit tests PASS** locally in CPython 3.13.5/Linux using deterministic synthetic negative inputs. The complete Amalgam parent checkout was not mounted in the local container; hence the Python script was **not run end-to-end against the full original file set** here. The GitHub trace analysis is a separate read-only execution and the numeric receipts are recorded in `result-summary.json`.
- All scored outcomes were already exposed in the historical development cohort. **No preregistered prospective validation, independent cross-platform requalification, new learning, held-out transfer, charged new-world action, cold native checkpoint scoring, or accepted-ref mutation**. ENGINEERING focused PASS / full regression UNVERIFIED. SCIENTIFIC retrospective selector not qualified and failed the all-stage improvement goal; genuine retained capability improvement UNVERIFIED. DEPLOYMENT UNVERIFIED.
- **Stop condition:** Do not tune this gate on the reused traces, and do not promote another 16-event historical-loss router to Yggdrasil. The next evidence-producing mechanism must independently identify informative interventions or latent regime evidence, preserve separate native learned structures and beat a fully fitted **equal-information/action-cost** diagnosis control on prospectively frozen and cold-restarted data.

### Reproduction

From a checkout including the pinned parent source plus this contributor branch:

```sh
python -m unittest discover -s tests -p test_wscm_revival_audit01.py -v
python research/contrib/chatgpt/WSCM-REVIVAL-AUDIT-01/audit.py --repo . --out /tmp/revival-audit.json
```

The script independently reads/verifies original Git blobs and outputs full per-stage source-accounted metrics. It has no network, training or world interfaces.
