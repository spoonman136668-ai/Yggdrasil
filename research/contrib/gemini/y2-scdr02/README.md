# Y2-SCDR02 — `SCDR-RoleCell-v6` (Sub-Stochastic Sinkhorn Soft-Exclusion & 5–7 Action Scaling)

**Status:** Isolated, external DEV exploratory contribution (`DEV_EXPLORATORY_ISOLATED`), follow-up to Draft PR #1370 (`y2-scdr01`).  
**Authority:** Evidence only — does not mutate `main`, accepted research state, `.ice` files, or locked `y2-cce06` calibration seeds (`[13, 29, 53, 71, 97]`).

## Core Advance over `y2-scdr01`

Replaces $O(|A|!)$ whole-world action-permutation enumeration with **$O(|A|^2)$ Factorized Per-Action Role Binding + 3-Iteration Sub-Stochastic Sinkhorn Soft-Exclusion** (column cap `max(1.0, col_sum)` over known roles, leaving the `Fresh_a` novelty column un-competed) + **Joint 2-Bit Sensory Symmetry Gauge** (8 bit-swap/XOR symmetries).

## Consolidated DEV Results (Cycles 5–7, DEV Seeds `[101, 103, 107]`, Locked CAL Seeds Untouched)

- **5-Action Full Permutation + Sensory Bit-Swap:** `SCDR-v6` achieved `0.0980` Brier at 60 steps (`30.7 ms`), beating independent `SCDR-v5.1` (`0.1050`) and `Fresh5A` (`0.1709`) while running **6.3× faster** than exhaustive `WholePerm-120` (`194.3 ms`).
- **5-Action Partial Space (3 Familiar + 2 Brand-New Actions):** `SCDR-v6` achieved `0.1570` / `0.1094` (60 / 120 steps), beating both `WholePerm-120` (`0.1776` / `0.1339`) and `Fresh5A` (`0.1650` / `0.1276`), with `0.0097` familiar abstain vs. `1.000` novel abstain.
- **7-Action, 3-Bit Observation Scaling ($7! = 5,040$):**
  - Full 7-action perm: **`0.0794`** @60 steps (`7.7 ms` / 150 steps) vs. `Fresh7A` **`0.2240`** (`-0.1446` Brier).
  - Partial 5 familiar + 2 brand-new actions: **`0.1507`** @60 / **`0.1078`** @150 vs. `Fresh7A` `0.2088` / `0.1708`, with **`0.000003`** familiar abstain vs. **`0.9998`** novel abstain.
- **Cross-Family Compositional Transfer (Cycle 5):** On `local_reversible → aliased_probe` (bit-swap + XOR + perm), factorized binding beat `FreshOnline` by `-0.0298` Brier at 60 steps (`0.0879` vs `0.1177`).

## Run Engineering Unit Tests

```bash
python3 -m unittest discover -s research/contrib/gemini/y2-scdr02 -p "test_*.py" -v
```

## Cycles 8–9 Upgrade (`scdr_hazard_v7.py`)

- **Mid-Episode Silent Gauge Shift (`HazardSinkhornRoleCellV7`, `h=0.015`):** On a 300-step 7-action episode with a silent permutation swap at step 150, `SCDR-v7` matched stationary pre-shift accuracy (`0.0601` vs `0.0593`) and beat log-decay `SCDR-v6` by **`-0.2399` Brier** over post-shift steps `150..210` (`0.1496` vs `0.3895`) and `Fresh7A` by **`-0.1370`** over steps `150..300`.
- **Bonferroni Multi-Lag $H_1$ + Event-Triggered Latch (`LatchAndBonferroniH1Sheet`):** Held `action_null` at **`0.00` false splits / `0.00` false latches**, beating `ActionHMM (h=6)` by **`-0.0150`** on `gated_nonlocal` (`0.1249` vs `0.1400`) and **`-0.0067`** on `local_reversible` (`0.1269` vs `0.1336`).

## Cycles 10-14 Upgrade (`scdr_cce06_adapter.py`)

- **Plug-Compatible `y2-cce06` Policy Frontier Adapter (`SCDRCCE06PolicyAdapter`):** Implements `fit`, `start`, `choose`, `update`, `posterior`, `spent`, `actions_taken`, `pending` and runs directly inside `y2-cce06` `calibration_policy_frontier._episode(..., paired_noise_required=True)` with zero edits to `y2-cce06`.
- **Coupled Broadcast Changepoint Hazard:** When any action flips its MAP role after step 10, it broadcasts a `0.35` hazard pulse to all other actions, waking up paid probing after silent mid-episode shifts. On `local_reversible` (silent shift at step 40), post-shift Brier dropped from `0.2087` to **`0.1262`** vs. `StaticNoHazard` (`0.2226`), `ActiveBayes` (`0.2319`), and `DecisionBayes` (`0.2405`).
- **240-Step Triple-Shift Campaign:** Beat both `ActiveBayes` and `DecisionBayes` across all three consecutive silent shifts (`0.1216` / `0.1448` / `0.1614` vs. `0.1518` / `0.2232` / `0.1750`).
