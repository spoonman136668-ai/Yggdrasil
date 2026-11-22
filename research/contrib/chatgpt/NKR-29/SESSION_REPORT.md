# NKR29: bounded feedback repair of actual recorded native forecasts

Result:DEV_SELECTIVE_REPAIR_NO_GO

The initial native bank learned96 actual public events from four previously
consumed external CausalGym worlds. Its164-byte checkpoint is preserved.
The remaining28 recorded events were forecast BEFORE being used as feedback.
All original labels were historically consumed; this is a retrospective
development experiment, not pristine heldout confirmation or new first-use.

## Wide first, then work backward

| Maximum new events | Feedback method | Actually learned events | Pooled Brier (lower better) | Confident misses |
|---:|---|---:|---:|---:|
| 28 | all_feedback | 28 | 0.181150747 | 6 |
| 28 | error_only | 4 | 0.188826071 | 6 |
| 28 | frozen | 0 | 0.185159824 | 6 |
| 28 | random_matched_701 | 4 | 0.189539300 | 6 |
| 28 | random_matched_702 | 4 | 0.186580720 | 6 |
| 28 | random_matched_703 | 4 | 0.185563136 | 6 |
| 14 | all_feedback | 14 | 0.180596225 | 6 |
| 14 | error_only | 4 | 0.188826071 | 6 |
| 14 | frozen | 0 | 0.185159824 | 6 |
| 14 | random_matched_701 | 4 | 0.185212656 | 6 |
| 14 | random_matched_702 | 4 | 0.189539300 | 6 |
| 14 | random_matched_703 | 4 | 0.188826071 | 6 |
| 7 | all_feedback | 7 | 0.179354876 | 6 |
| 7 | error_only | 4 | 0.188826071 | 6 |
| 7 | frozen | 0 | 0.185159824 | 6 |
| 7 | random_matched_701 | 4 | 0.185867491 | 6 |
| 7 | random_matched_702 | 4 | 0.185867491 | 6 |
| 7 | random_matched_703 | 4 | 0.186217971 | 6 |

Each matched-random arm updates at EXACTLY the same times/in the same
world and uses the same actual number of events as error-only repair.
It selects from previously witnessed, as-yet-unassimilated feedback, never
future events. Random controls are conditional on error-only's gate, not
independent deployed policies. Ordinary all-feedback learning shares the same
maximum budget/public stream but may consume more observations; actual costs
are disclosed above. A stochastic surprise is not proof of an incorrect law.

Every native forecast matches the independently fitted exact Beta control.
The native learned bank retains all192 original observed-counter increments
(96 physical events), and newly learned events add2 increments each. Counts
agree with independent per-arm event ledgers; other worlds' posterior values
remain unchanged after every update. Every final bank cold-restores exactly.
Checkpoint hex, hashes and actually learned event IDs are in result.json.

## Interpretation

Error-only support requires at the largest28-event cap BOTH a0.005 Brier
gain over frozen memory AND0.005 over matched-random mean. No thresholds or
caps are retuned after outcomes. Original NKR19 frozen score is reproduced
exactly. Old failures and the original native checkpoint stay frozen; these
separate exploratory repaired checkpoints do not rewrite previous evidence.

Learning here means changed native public consequence counts. This does not
train the21.3M factual image into understanding, learn a new operator, prove
unfamiliar-world transfer, beat an exact equally informed control or authorize
accepted-model installation. All source events were previously consumed.

Source SHA:eed9d1b5e3c5dcffce9ac1741ef47d6ce486516f
Prereg SHA:060eb2c00e11c447857bc23dad489fa8fa3248c7
Stable SHA256:eb743edfc6eec877e0f8fc357a6e1b912b2d1be0038a503902726ae54a1dff48
Ubuntu audit:0.019522s. Windows audit:0.031000s.
No source environments imported/reset/intervened; no original source scan,
protected seed, runner/controller/scheduler, paid API or deployment.
Full final exact-source root/NKR05/independent G29 both OS are qualified after
these receipts are committed; final PR records those terminal receipts.
