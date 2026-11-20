# ENERGY-SELECT-14 — Active intervention selection against Bayesian information gain

**2026-11-20 · Yggdrasil independent Energy Research contributor · ENGINEERING partial PASS · SCIENCE NEGATIVE_NO_GO · DEPLOYMENT NONE**

## Research question

ENERGY-REPAIR-POWER-13 showed that a *uniform* source-specific hard reset needs seven new public observations per row (84 total for 12 rows) to meet its mathematical power/false-reset specification. Does selecting *which* action-conditioned relationship to investigate allow a 24-intervention budget to learn unfamiliar changed causal consequences better than strong conventional selection policies? This is a genuinely new intervention-allocation mechanism, not a retroactive threshold change to ENERGY-REMAP-11.

### Frozen protocol and source custody

- Existing draft contributor [PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346), based on accepted main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Sole native cumulative integration owner remains [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).
- [Preregistration](prereg.json) frozen **first**, commit `ea20ddda4c7d1f2b84f1cd7945213f297eaa41b4`.
- [Executable Python source](experiment.py) frozen **second**, commit `e3a4b628a8ed0e8192d581dc210a8c2e959908b0`, Git blob `91bc10d77689ce4827d1c96ce9a499c559a58ba8`. The exact local executed source hash-object matched the GitHub readback blob **before** smoke or primary execution. No third-party packages, paid APIs, runners, protected datasets or model weights.
- One disjoint smoke seed `97801`: 3 worlds, outcome **NO_GO**; 3/3 independent-process toy OLD snapshot readouts passed. Then **one** frozen primary using the 12 seeds in `prereg.json`, across NULL, SINGLE_REWIRE, OUT_FAMILY_DOUBLE, **36 worlds total**. Primary never rerun or post-tuned.
- Per world: 12 state-action rows, 6 OLD categorical observations/row, 24 NEW online interventional consequences **per action-selection policy**, and 96 held consequences/row. Across worlds: 2,592 OLD, 864 NEW per policy (3,456 across four policies), and **41,472 held consequences** scored against all four policies. Outcomes are counter-based and paired by row/observation ordinal.
- All policies use **the exact same fitted Dirichlet(0.5) reset/stay posterior mixture readout**. Only action selection changes. Four arms: bounded contradiction tournament (candidate), fully computed conventional myopic Bayesian information gain, round robin and deterministic random. The true categorical law is a *privileged oracle reference*, not a learning baseline to exceed.

## Frozen primary results

Multiclass held Brier, lower is better, averaged over 36 worlds:

| Online intervention selector | Overall | NULL | SINGLE_REWIRE | OUT_FAMILY_DOUBLE | Changed-row detection |
|---|---:|---:|---:|---:|---:|
| **Bayesian information gain** | **0.309508** | **0.290684** | **0.308569** | **0.329271** | **86.11%** |
| Contradiction tournament (candidate) | 0.329328 | 0.291595 | 0.324380 | 0.372010 | 52.78% |
| Round robin | 0.332445 | 0.297436 | 0.332409 | 0.367489 | 0.00% |
| Random | 0.342420 | 0.304624 | 0.343616 | 0.379019 | 22.22% |

Every policy had **0/12 NULL worlds** with a posterior >=0.8 false alarm. The tournament is **0.019820 Brier worse** than strongest matched control, and fails the frozen >=0.010 superiority and >=80% changed-row-detection thresholds. It also loses to Bayesian information gain in every scenario. The source-free experiment therefore **falsifies the proposed causal-contradiction tournament benefit**.

A postscore descriptive 95% *normal-approximation* paired interval for (Bayesian information-gain Brier minus tournament Brier) is [-0.02857,-0.01107]. This is exploratory, because within-seed worlds are not independent and the interval was not a separate preregistered acceptance test; do not treat it as independent scientific qualification.

### Evidence, independent arithmetic and custody limit

- [36-world original score table](world-metrics.csv): source Git blob `c902c09bec05cb3fd58db30e7f38d81cfcd71650`, file SHA-256 `1a52288089fb5602540d55841deba1fb4548fba6aa0680ceb780d5053cf3ab1b`. Exact 36 scenario/seed rows and per-arm Brier, true-positive and false-positive counts.
- [Separate postscore arithmetic auditor](audit.py), Git blob `8af4ac405dccef4e1d4194b3a56fcbda73d46e9c`, reaggregated the CSV independently, checked cohort membership, score bounds and event counts, and compared all aggregates with the original local primary. [Receipt](audit-result.json): **PASS**. This is **not** an independent rerun of the experimental source or original consequence generator.
- The larger original `primary.json` contains intervention traces/CPU times and was retained **locally only**, 309,400 bytes, SHA-256 `9b4f5a8d169f6eb2d9b74b55fdf1ebc7936a561c657245779287fc6a70e10205`. The original raw file **was not uploaded** to GitHub; do not describe the bounded CSV as full original trace custody.
- A separate Python subprocess cold-reloaded the toy OLD snapshots for all 36 worlds with exact readouts **36/36**. This does not prove native learned-state retention or interruption recovery: the synthetic OLD readout is intentionally immutable.
- Source CPU times and wall time were recorded locally but have no matched environmental controls, repeat-run qualification or native end-to-end resource accounting. **No 2x efficiency gain claimed**.
- The branch's G29 Linux/Windows atlas source-set check was previously failing at the generated index; *no final source-set atlas or full dual-OS regression success* is claimed for this new head.

## Decision

**ENGINEERING:** Frozen prereg/source custody verified; single source-free primary execution and separate score aggregation PASS. Full raw source receipt transfer, full final regression and independent experimental replica **UNVERIFIED**. G29 atlas CI on the earlier branch head **FAIL**, latest head CI unverified.

**SCIENCE:** **NEGATIVE_NO_GO**: simple contradiction concentration is inferior to a fully computed conventional information-gain action policy at equal interventional budget and identical Bayesian readout. This is not a learned topology/energy advantage, native Yggdrasil cumulative gain or autonomous research proof.

**DEPLOYMENT:** **NONE**. Do not merge this draft contribution or promote any checkpoint. Accepted main, central Amalgam weights and owner, protected first-use, local or GitHub runners, controller/scheduler, and operational systems unchanged.

**New research direction:** If a distinct mechanism is attempted, it must *construct and revise explicit unfamiliar causal hypotheses*, with discriminating interventions evaluated against a **fully fitted Bayesian active planner**, control for intervention cost, unfamiliar/out-of-family effects and independently restored historical functional memory. Do not retry this tournament on the consumed primary or merely increase observation budget to rescue it.
