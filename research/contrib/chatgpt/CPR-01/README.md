# CPR-01 — Conformal Prediction-Set Routing (research-only)

This **readout-only source-free candidate** is downstream of the single Amalgam
coordinator [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).
It is not a replacement learner, accepted checkpoint, deployment, first-use
authorization, or G41/R15-V2 original-world replication.

## Custody / scope

- Accepted `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Research parent: G41 R13 branch at `40774e820b0c0e6cabb4d6b2766d38f15b63d387`.
- Preregistration preceded the new Python source at commit
  `c3cf82c4d8d9c1f50f93e70e0da81b06bc76aedc`. Its status is
  **DESIGN_ONLY_INPUT_CUSTODY_AND_OWNER_FIRST_USE_PENDING**.
- Exact committed module Git blob `8b6109b6199c9cf161e7d65f33c69ea30c18bccd`.
- Exact committed test Git blob `29e7e24b017f1f073914c5163b2f19cfbf812b15`.
- No native learner or checkpoint format was edited. No G41 original artifact
  was loaded, no real specialist was frozen, and no protected source was used.
- Existing G41 and R15 development outcomes are already consumed; they cannot
  become new held-out evidence merely by selecting a new router.

## Implemented mechanism

For binary outcomes, the exact split-conformal order statistic is
`k = ceil((n+1)*(1-alpha))` among `n` held-out nonconformity residuals,
with an infinity sentinel at rank `n+1`. Probability scores use integer
millionths, so each specialist's prediction-set cardinality takes two
constant-time comparisons. An expert is gated using **prior** observed
coverage only; the revealed outcome is appended after the route was chosen.
For the eight-step test, at least 6/8 previous labels must fall within that
expert's prediction sets. Among eligible experts, choose the smallest binary
set and then stable model name. Abstaining experts continue passive readout,
so no frozen model update is needed to requalify a familiar expert.

Calibration and routing live in a separate SHA-pinned sidecar. Restore
requires each original model pin. The sidecar never edits the original model
checkpoint. A run of universal abstention emits **one bounded signal**, never
spawns a specialist or freezes the current learner automatically.

Conformal **marginal** coverage relies on exchangeable calibration/test data.
It cannot promise empty out-of-distribution sets, valid coverage under a
regime shift, accurate regime classification, or A-to-B-to-A revival.
Calibration sample identity and disjointness from FIT must be independently
certified by the source owner; this code accepts pins but cannot prove dataset
custody.

## Source-free engineering results

Exact Git-blob-matched module and test files were tested in an isolated
Linux Python 3.13.5 container, **not on MIND-PALACE-WIN**:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p test_cpr01_routing.py -v
```

All **7/7 source-free focused tests passed**, including exact quantiles, routing
before outcomes, reject-on-replay, cold sidecar restore, model-pin tampering,
single-step gating, A/B/A revival and 10% noisy-counterexample detection.
Synthetic A(16) -> B(16) -> A(16) revived expert A on **return step 7**.

**Critical negative:** with two frozen experts calibrated on clean outcome
1, an 80-observation stream containing **eight consecutive flipped labels**
(exactly 10% overall corruption) produced **one false universal-abstention /
speciation signal**. The synthetic test intentionally asserts the negative
event is detected; its green test is **not** a scientific robustness pass.
Under unconstrained clustered label noise, CPR W8 fails the asserted
'no false-positive speciation' property. No specialist was spawned.

Exploratory same-host medians for five repeats, without inference cost:
R15 verified-source two-target two-expert `step()` **1,792.2 ns**;
CPR single-target two-expert route+observe **1,650.4 ns**;
CPR single-target 33-expert route+observe **18,387.4 ns**.
These are **different amounts of work**; do not subtract them and call the
difference end-to-end overhead. Repeated microtiming also exceeded the
preregistration's 100,000-operation budget, so these timings are diagnostic,
not a qualified prospective performance result.

## Scientific and deployment status

| Requirement | Status |
| --- | --- |
| Familiar-task Brier delta <= +0.02 | UNVERIFIED |
| New-task prediction error <= 0.1958 on a comparable cohort | UNVERIFIED |
| Real G41 33-expert original checkpoint | NOT RESTORED |
| R15 original 9 stage comparisons and strongest matched controls | NOT RE-SCORED; historical 0/9 remains |
| Actual A/B/A return <= 12 without oracle labels | UNVERIFIED; synthetic 7-step result only |
| No false-speciation at 10% noise | **FALSIFIED** for clustered synthetic noise |
| Frozen FIT/CAL/HELD input identities | NOT QUALIFIED |
| Full final exact-SHA Linux + Windows regressions | NOT RUN |
| G29 atlas / `.ice` manifest and accepted deployment | NOT UPDATED / NOT AUTHORIZED |

**Decision:** Research-only source-free screen is useful for architecture
falsification, but the noise robustness gate is **NO-GO as worded**.
Keep automatic speciation disabled. Before any new original-world
CPR qualification, establish certified disjoint 128-row calibration sets per
frozen expert, pin new disjoint held cohorts, equal-information fully fitted
controls and source-owner authority, then run the whole frozen regression on
the exact candidate. Do not tune thresholds on the consumed R15/G41 evidence.

## Original-control identity correction (no post-result tuning)

The **actual frozen G41 R13 protocol**, Git blob
`438e147f243fbe51cc33819a9d777ba6c97b1760`, names
`static_novel_cap_1/2` and `coverage_cap_3/4`. The handoff's 12.5% and
25% caps are **not those two documented original R13 arms**; the initial
CPR-01 design-only preregistration lists 12.5% and 25% proposed controls,
so it cannot be represented as an exact replay of R13. No original-world
scoring was attempted. A fresh source-pinned and owner-qualified prospective
protocol must explicitly include the **original 1/2 and 3/4 arms** if those
are the comparator intended, before any new held-out outcomes are inspected.

A separately qualified **R15-V2** source or original cohort was not
identified in the verified R15 branch, issue and PR discovery used here.
The available frozen R15 protocol and report are two-expert, three-stage,
three-seed, already-consumed **R15** records, not evidence that R15-V2 ran.
