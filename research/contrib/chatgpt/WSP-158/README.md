# WSP-158 — Train two native calibration weights against real historical public DTR outcomes

**Scope: independent research-only draft, source-only development, no protected first use, accepted native modification, deployment or merge.**

## Reason for this particular experiment

Original [WSP-157 PR #1208](https://github.com/spoonman136668-ai/Yggdrasil/pull/1208), head `75e8b1da111319cbccf25e76e3153ccba508ce9f` / tree `bbc8deee2a422da39b72f87d24ec110ec88bd887`, passed 185/185 complete root tests per OS and independent G29. It proved 164-byte native NKR-19 `PublicCausalCells` successfully persists learned real historical public probabilities from original Causal-Gymnasium DTR-02 actions, but **lost to saturated empirical MLE** (pooled Brier native Beta 0.149352637353 vs MLE 0.138323934568). The smoothing prior helped its transition prediction while harming its near-deterministic terminal reward. A globally selected fixed source-independent Beta(1,1) readout is therefore an incomplete calibration policy.

Previously [ITD-02 V11](https://github.com/spoonman136668-ai/Yggdrasil/tree/research/itd02-v11-cell-local-calibration-20261027) already explored native local calibration **in a different public task-ring architecture**, not this 164-byte original-source two-stage counter memory; do not duplicate its residual learning tests, variants or source-free worlds.

## Pre-result frozen design

1. **Preregistration was committed first** as sole new file at exact `49282e892e5ba1cdd99008fd2f6f32e211f97ebc` before new code/tests/results.
2. Keep all WSP157 original source, native memories, original first-use fences, training/held historical data and controls **unchanged**. Reuse its exact-hash authenticated `consumed-original-public-fit.json` (768 earlier spent original public FIT episodes: three ×256), and read only public `S1,X1,S2,X2,Y`. The independent original environment library **must never be imported or reset/do invoked**. Original DTR02 VALID/DEV source reserved trace content remains untouched.
3. New `yggdrasil/native_stage_calibration.py` is a **standalone, opt-in two-parameter readout** atop the 164-byte original `PublicCausalCells`. No original existing native file edited, no new memory bank or learned rule store. Stage 0 predicts observed `S2` from `(S1,X1)`; stage 1 predicts observed terminal `Y` from `(S1,X1,S2,X2)`. The source and historical public transitions remain exactly the original observations.
4. Freeze alpha grid = `[0, 1/4, 1/2, 1, 2]`; per stage and observed native action cell count successes `s`, failures `f`, output `(s+alpha)/(s+f+2alpha)`; no-support output `1/2`. Fractions calculated exactly with rational arithmetic. `alpha=0` is MLE; `alpha=1` reproduces original Beta. No after-result grid changes.
5. **Each of three historic FIT replicas independently**: first indices `0..63` FIT for selecting parameters, `64..127` validation selects exactly one alpha/stage by lowest validation Brier with frozen tie break nearest to `1`, then lower index. Independent separately fitted raw count table must yield *exactly identical indices and probabilities* without accessing the native program. After freezing both alpha indices, refit the untouched 164-byte native counts on `0..191` and attach only the two indices in a versioned **202-byte integrity-bound composite** (164 original checkpoint bytes preserved unchanged) before historical test `192..255`. No test label is available for weight selection, but those historical test outcomes have been examined previously in WSP-157, so they cannot be called virgin science.
6. Three independent replica models ×64 original held historical FIT episodes ×two binary outcomes = **384 observed-source forecasts per arm**. Compare original Beta, full closed-form MLE, independently optimized equivalent stage prior (expected exact tie), trained WSP157 fixed-iteration logistic diagnostic (convergence must be shown, never guessed), and chance. Report transition and terminal Brier separately, pooled Brier, chosen stage weights, exact cold, raw native SHA, composite SHA and resource time excluding all historical source acquisition.
7. **Frozen development gain gate**: new native pooled Brier must beat strongest fully fitted MLE by **at least 0.005 absolute**, with transition Brier no worse than MLE by more than `0.002`. Otherwise `DEVELOPMENT_NATIVE_CALIBRATION_NO_GO`. Even if positive, independently calibrated control is required to tie exactly; no native *architectural* superiority can be inferred. **SCIENTIFIC_PASS ALWAYS FALSE**. Never tune after scoring or promote to accepted native main.

## Evidence limits and qualification

WSP-157's original FIT suffix was scored by previous researchers and already shaped this hypothesis. These three replicas are same independently authored **simulation mechanism**, not independent unknown-family transfer, no learned policy selection in actual simulator, no off-policy causal value proof. Native calibration sidecar correct/incorrect outputs are only forecasts of the actually chosen historical interventions. Some native source-only suites have valid synthetic/fabricated source tests; they are not elevated to original source scientific qualification.

Engineering requirements: pre-score focused Linux+Windows original source and negative tests; exact SHA-custodied one-time first developmental fit; preserve null outcomes; three derived G29 files once; final complete Linux+Windows root regression and independent G29 on exact final source tree, checkpoint and source field isolation. No source-owner first-use, other model edits, private/local runner, scheduler, paid API, accepted main, migration or merge. Keep DRAFT.


## Frozen first source-results — completed 2026-11-17

The first scoring run was [#44203651656](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44203651656) from exact source/test SHA `5f5aa1dba4ac4a778b85ac2666b64a5cc524cc81`; Linux and Windows both **COMPLETED SUCCESS**, independent semantic output SHA256 **`336f93c5629e9cb9e3ed75a2f2abcafe8b6e3a891671fcefa4e8f73624121d8e`**. Original source data is unchanged, and the original `WSP-157` historical source footprint and native 164-byte original code are untouched. Linux artifact `14382887032` ZIP SHA256 `260ba5d952a69187740d975db5508fe4025d9d138cdd818fa62704b48778cfc9`; Windows artifact `14381938471` ZIP SHA256 `99c3011e4d5958b598e61e9d773437c6c9dde001bf62fc3655df86d4d1028b12`.

**All three independent FIT-source replicas chose stage alpha `[2,0]`** based *only* on each one's 64 calibration FIT and 64 separate validation histories: transition `alpha=2`, terminal reward `alpha=0`. Both weights were frozen before fitting 192 original source FIT rows and historical score of 64 rows/replica.

| Original public DTR FIT historical source, 384 binary held outcomes | S2 transition Brier | Y terminal Brier | Pooled Brier |
|---|---:|---:|---:|
| Original native Beta(1,1) | 0.249212655546 | 0.005396013832 | 0.127304334689 |
| Two-weight programmed native readout | **0.249139183072** | **0.000000000000** | **0.124569591536** |
| Strong exact independently fitted *same stage* calibrator | 0.249139183072 | 0.000000000000 | **0.124569591536 (exact tie)** |
| Fully fitted saturated empirical MLE | 0.249302802605 | 0.000000000000 | **0.124651401303** |
| WSP157 fixed-3000-iteration conventional logistic diagnostic | 0.249016190600 | 0.002604278257 | 0.125810234429 |
| Chance 0.5 | 0.250000000000 | 0.250000000000 | 0.250000000000 |

Lower is better. The programmed sidecar fixes the original over-smoothing on observed terminal reward in these original-source historical worlds and improves the parent native 0.127304 by **0.002734743153** Brier absolute. It beats the fully fitted MLE by only **0.000081809767**, **~61× smaller than the preregistered minimum 0.005**. Two replicas beat MLE by ~0.00011 / 0.00025, one loses by ~0.00012. The independent same-data, same-parameter calibrator matches **exactly**, so no native-specific superiority. Logistic transition converged in only 1/3 fits, terminal in 0/3; do not call it a converged neural strongest control. Do not use a confidence interval from nested same-law historical observations to imply a virgin scientific gain.

**Frozen developmental disposition: `DEVELOPMENT_NATIVE_CALIBRATION_NO_GO`.** Formal scientific first-use absent and never performed, model-selected original do actions zero, no native main acceptance, unknown-family causal transfer or intelligence proved. This is engineering-compatible evidence that two directly programmed readout weights can modestly improve historical observed-probability prediction, **not** a win against properly matched independent calibration. No after-score model, split, source or threshold edits are allowed.

The full first-run exact result and archived artifact provenance are recorded in `result.json`. Separate final exact-source mandatory full root regression and independent G29 checks still required to call **ENGINEERING PASS**.
