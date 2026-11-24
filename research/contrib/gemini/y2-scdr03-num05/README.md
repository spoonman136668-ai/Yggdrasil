# Y2-SCDR03-NUM05 — Continuous Gaussian Sub-Stochastic Sinkhorn on `NUM05`

**Status:** Isolated, external DEV exploratory contribution (`DEV_EXPLORATORY_ISOLATED`), targeting `research/num05-numeric-causal-memory-20261120` (PR #1357).  
**Authority:** Evidence only — zero edits to `NUM05` files, `main`, `.ice`, or `NUM05`'s reserved DEV/null/pilot/primary seeds (`520117`, `520131`, `520211`, `520311`, `520331`, `520411`, `520431`, `520451`).

## Key Finding (Sandbox DEV Seeds `[620101, 620103, 620107]`)

Testing `SCDRNumContinuous` directly against `NUM05`'s actual `NumericRegimeMemory` and strong controls uncovered a concrete blind spot in `NUM05`'s fixed `0.15` contradiction threshold: under an action permutation (`permuted_ABA`), Phase B MSE (~`0.074`, 40× above noise `0.0017`) failed to trigger `NUM05`'s `0.15` gate, silently corrupting Bank 0.

Adding a **self-calibrated relative surprise gate** (`min(0.15, max(0.025, 8.0 * ema_mse))`, updated only on non-contradictory events) + **Continuous Gaussian Sub-Stochastic Sinkhorn** yielded:

- **`permuted_ABA` (`A → Perm(A) → A`):** `early_B = 0.0119` (**6.2× lower MSE** than `NUM05_Native` `0.0737`), `pooled_num05 = 0.0029` (**10.1× lower** than `NUM05_Native` `0.0296` and **4.4× lower** than best conventional control `CellHist_80` `0.0129`), `bank0_byte_exact = 1.0`.
- **`partial_ABA` (`A → [3 Permuted A + 2 Disjoint B] → A`):** `early_B = 0.0681` (**2.06× lower** than `NUM05_Native` `0.1401`), `pooled_num05 = 0.0049` (beating `NUM05_Native` `0.0065` and `CellHist_40` `0.0249` by **5.1×**), with `0.0053` familiar abstain vs. `0.9792` novel abstain.
- **`disjoint_ABA`:** `pooled_num05 = 0.0074` (beating `CellHist_40` `0.0309` by **4.2×** and `CellHist_80` `0.0488` by **6.6×**; `+0.0025` behind `NUM05_Native` `0.0049`), `bank0_byte_exact = 1.0`.
- **`null_AAA`:** `0.001045` pooled (identical to `NUM05_Native`), **`0.0` false archives**.

## Run Unit Tests

```bash
python3 -m unittest discover -s research/contrib/gemini/y2-scdr03-num05 -p "test_*.py" -v
```

## Cycles 28-29 Upgrade (`scdr_num05_multibank.py` — Precision-Gated Multi-Bank & Continuous Control)

- **Precision-Gated Readout (`disjoint_ABA`):** Truncating sub-floor hazard weights (`< 0.03`) before mixing forecasts cut `disjoint_ABA` pooled MSE from `0.0074` to **`0.0059`** (within `0.001` of `NUM05_Native`'s `0.0049`) while pushing `permuted_ABA` to **`0.0027`** (**10.9x lower** than `NUM05_Native`'s `0.0296`).
- **6-Phase Multi-Regime Chain (`A -> B -> C -> Perm(A) -> B -> A`, 510 rows):** `MultiBankSCDRNumV2` achieved **`0.0276`** pooled MSE across the 3 return phases vs. `NUM05_Native` `0.0704` (**2.55x lower**) and `CellHist_40` `0.1744` (**6.3x lower**).
- **Continuous Reward-Maximizing Control (100 steps, zero-reward Phase A pre-training):** Earned **`+17.73`** on `perm_A` vs. `Fresh_UCB` `+14.19` (`+25.0%`), and **`+47.34`** on `partial_B` vs. `Fresh_UCB` `+31.64` (**`+49.6%`**) and `Random` `+16.63`.

## Cycles 30-32: Continuous D4 Spatial-Symmetry x Sinkhorn (`SpatialSymSCDRNumV3`)

Extends `MultiBankSCDRNumV2` from action-only permutation transfer to joint **2D Euclidean dihedral symmetry ($D_4$, 8 rotations/reflections)** acting equivariantly on both `(x, y)` and `(dx, dy)` alongside 5-action permutations and partial novelty isolation (`scdr_num05_spatial_d4.py`), with an exact Rao-Blackwellized mixture marginal likelihood and a **pre-archive contradiction quarantine buffer** (Cycle 32) that prevents pre-freeze bank contamination.

- **DEV Sandbox Seeds:** `[620101, 620103, 620107]` (`NUM05` reserved seeds untouched; `SCIENTIFIC: UNVERIFIED`).
- **Cycle 30 (honest partial miss):** Passed 4/5 criteria (`rot90_perm_ABA`, `reflect_partial_ABA`, `null_AAA`, `rot270_perm_control`), missed `disjoint_ABA` target by `+0.0036` (`0.0516` vs `0.0460`) due to pre-archive contradiction rows contaminating Bank 0 and starving `active_bank`.
- **Cycle 32 (5/5 PASS with quarantine buffer + mild `id` prior):**
  - `rot90_perm_ABA` Phase 2 MSE: **`0.009779`** vs `MultiBankSCDRNumV2` `0.038764` (**3.96x lower**) and `NUM05_Native` `0.111099` (**11.36x lower**); exact gauge `(0, "rot90")` on 3/3 seeds, Bank 0 byte-exact.
  - `reflect_partial_ABA` (`anti_diag` + 3 permuted / 2 novel) Phase 2 MSE: **`0.047124`** vs `V2` `0.063989` and `NUM05_Native` `0.097341` (**2.07x lower**); abstain `0.0709` (familiar) vs `0.9795` (novel).
  - `disjoint_ABA`: Phase 2 MSE **`0.078643` == `0.078643`** (exact parity with `NUM05_Native`); pooled **`0.047857`** vs `0.045997` (`+0.00186 <= +0.002`).
  - `null_AAA`: `0.0` false archives, exact MSE parity (`0.001271`).
  - `rot270_perm_control` (100-step on-policy reward): **`+17.7635`** vs `MultiBankSCDRNumV2` `+13.7467` (**`+29.22%`**) and `Fresh_UCB` `+13.6765` (**`+29.88%`**).
  - Cold checkpoint: **`7,526 bytes`**, 100% byte-exact replay (`12/12` unit tests PASS).
