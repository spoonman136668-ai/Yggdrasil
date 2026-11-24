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
