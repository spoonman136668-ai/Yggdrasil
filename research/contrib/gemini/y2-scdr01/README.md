# Y2-SCDR01 — `SCDR-RoleCell-v4` (DEV Exploratory Contribution)

**Status:** Isolated, external DEV exploratory contribution (`DEV_EXPLORATORY_ISOLATED`).  
**Authority:** Evidence only — does not mutate `main`, accepted research state, `.ice` files, or locked `y2-cce06` calibration seeds (`[13, 29, 53, 71, 97]`).

## Question & Method

Can an unconventional, stdlib-only, strictly public-only causal contract learner (`SCDR-RoleCell-v4`) simultaneously handle:
1. **Hidden-state discovery with negative-control restraint** via calibrated $H_1$ Sheaf-Cycle Defect Splitting (out-of-sample prequential hurdle on `multichannel_brier`).
2. **Long-horizon functional retention without replay buffers** via an immutable **Anchor-to-Genesis Quine Ledger** + **Gauge-Deduplicated Sheet Compression**.
3. **Unfamiliar-world transfer & out-of-family safety** via **Charged-Probe EVGI** on-policy exploration (`decay=1.0`) paired with a **Bayesian Epistemic Abstention Guard**.

## Key DEV Results (Fresh DEV Seeds `[101, 103, 107]`, Locked CAL Seeds Untouched)

- **In-Family $H_1$ Splitting vs. `ActionHMM (h=6)`:** Closed `gated_nonlocal` to within `+0.0004` Brier (`0.1104` vs `0.1100`, `1.0` split/seed), beat `ActionHMM` on `local_reversible` (`0.1249` vs `0.1250`) and `action_null` (`0.1352` vs `0.1362`, **`0.0` false splits**).
- **10-World Cumulative Chain (All 4 Families + Permutations + Bit-Inverted Exotic Law):** Allocated **`2.33` unique sheets** + `4.0` lightweight gauge pointers, holding mean cold-return drift to **`+0.0054`** and worst-world max drift to **`+0.0164`** (strictly under `+0.02`, vs. `+0.0274` without Genesis Ledger, `+0.0852` naive speciation, and `+0.0973` pooling).
- **On-Policy Priced-Intervention Frontier (40 steps, `COST=[0,1,1]`, 300-step frozen audit):** Dominated `y2-cce06`'s `ActiveBayesianPolicy` and `DecisionFocusedBayesianPolicy` across `local_reversible`, `gated_nonlocal`, and `aliased_probe` (`-0.050` to `-0.084` lower Brier at **3.8×–12× lower paid-probe cost**), and cleanly abstained on an out-of-family bit-inverted world (`abstain=0.996` at `B=6`, beating both Bayes controls at `B=12`).

## Run Engineering Unit Tests

```bash
python3 -m unittest discover -s research/contrib/gemini/y2-scdr01 -p "test_*.py" -v
```

## Limitations

- DEV exploratory seeds (`[101, 103, 107]`) only; locked `y2-cce06` calibration seeds (`[13, 29, 53, 71, 97]`) were never touched.
- Does not yet handle non-bijective partial action spaces (e.g., 2 familiar actions + 1 brand-new unknown action) or simultaneous observation-bit permutations.
