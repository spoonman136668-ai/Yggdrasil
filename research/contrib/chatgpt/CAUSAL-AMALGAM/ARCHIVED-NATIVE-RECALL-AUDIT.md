# P0 native readout evidence — retrospective checkpoint-only gate (2026-11-21)

**Disposition: RETROSPECTIVE_DEV_NEGATIVE / no scientific gain / no native change.** This extends the original source-level context-routing observation in this isolated research branch, not the sole Amalgam coordinator or accepted native state.

## Pinned identity and custody

- Accepted `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Original Amalgam draft [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) HEAD `86264b41a08d49f558418c0fba367f3a2636befa`. Stacked draft [#1329](https://github.com/spoonman136668-ai/Yggdrasil/pull/1329) HEAD `bbcca1d06d394a7bcfdc514f4e04bb269cb023cb`. They share native episode-memory source Git blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`.
- Downloaded existing [Actions run #44499793023](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44499793023) archives: Linux artifact `14517860401`, ZIP SHA256 `b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d`; Windows `14516669671`, ZIP SHA256 `bb2b689f84caf939b76bea669eff7efb26506b602eed81ac79a81b42efb0a5a6`. The *entire* joint checkpoint differs cross-platform because of specialist state; **inner native checkpoint** SHA256 `5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d` and **episode checkpoint** SHA256 `9158254b80f147d7eb7516d630f6003441df4b8373375b994d864ee1d55568f4` match exactly.
- Linux joint checkpoint SHA256 `576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8` contains **1,025 consumed engineering-fixture episodes**. Status is `accepted_native=false`, `scientific_pass=false`. Protected source-first-use remains forbidden by [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426).
- This is the original 1025-witness joint anchor, **not** the separate earlier 1024-witness CKAD26 parent state. Do not confuse their native SHA256s.

## Read-only method and reproducibility

`archived_native_recall_audit.py` independently mirrors only the published source's existing `NativeEpisodeExperience` Beta(1,1) banks, 8-witness projection choice, optional three-contradiction local repair, 32-episode frozen expert blocks, 1/8 novel prior, 1/32 post-transition refresh, and pre-action first-stage mixture arithmetic. It does **not** import/run the actual native Python class, cold-restore through the official API, change original weights, generate an outcome, or claim owner acceptance.

It reconstructs **28 frozen historical block experts + one continually learned novel expert** using the 891-witness prefix, then scores **134 already-consumed public episodes** in chronological order. Each forecast precedes its witnessed outcome and all proposed routes use only previously revealed data. The exploratory `contextual_prior_select` arm chooses the lowest previously accumulated Brier expert per public `(context, action)` after 8 such observations; beforehand it selects the highest global-posterior historical expert. There is **no oracle regime label and no current-outcome leakage**. All arms receive equal recorded witness information. No source actions are taken.

The mirror's final four anchor forecasts match the four already-published `recall-evidence-bound.json` native anchor values **to 1e-14**: `[0.1443993732160158,0.7864317781394096,0.1530560248052734,0.6696158228675264]`. This is a strong parity cross-check for these readouts but **not** whole-checkpoint hash parity or full native execution.

Reproduce with Python 3.13 (standard library only), after downloading the **named preexisting ZIPs**:

```sh
python research/contrib/chatgpt/CAUSAL-AMALGAM/archived_native_recall_audit.py \
  amalgam-original-1025-14517860401.zip \
  amalgam-original-windows-1025-14516669671.zip \
  > result.json
```

Two independently launched processes gave byte-identical results, output SHA256 `921d90b41a4c892b3cce5033e226fad1fa8bc4beac16544184ed3eb8373a3e48`; source SHA256 `defdb6e8e0610bcc2a384e1a79cbf95e0f32e3d32472437cc5699b5af7656129`. Tampered-ZIP and swapped-platform negatives were rejected, and Python syntax compiled. This local sandbox is **not** the owner's original Windows runner or repository-native full Python checkout.

## Measured outcome (read-only, exploratory; Brier lower is better)

| Pre-action readout | First 8 witnessed suffix episodes | All 134 suffix episodes |
| --- | ---: | ---: |
| Existing global native-mixture mirror | 0.158884 | **0.183963** |
| Highest global-weight historical expert | **0.082982** | 0.187698 |
| New context-specific past-loss selector | **0.082982** | **0.228491** |
| All old experts equally weighted | 0.210519 | 0.237910 |
| Continually adapting new expert only | 0.202292 | 0.234340 |
| Constant 0.5 control | 0.250000 | 0.250000 |

The proposed context-specific selector is **+0.044528 absolute Brier worse** than the existing global mixture on the whole previously-consumed suffix. Its apparent early 8-step advantage **did not persist**, making it unsafe to promote from this evidence. All four prepublished original-anchor predictions are reproduced. This does **not** prove the global router is generally best, prove that individual memories were erased, or prove improved causal intelligence.

## Explicit gates

- **ENGINEERING/PREEXISTING SOURCE:** two original archives and inner native/episode custody hashes PASS. Focused mirror executed and twice reproduced PASS. Native Python source module itself and full checkpoint restore **NOT EXECUTED** in this sandbox.
- **SCIENTIFIC:** evidence is already consumed, heuristic not preregistered for independent science; comparator is a *diagnostic* with prior evidence and no strongest trained independent-control suite. `SCIENTIFIC_GAIN_VERIFIED=false`; proposed naive context router **REJECT** for now.
- **DEPLOYMENT:** none. No accepted state, model, PR #1278 or #1329, owner controller, scheduler, actor, source manifest or protected first-use changed.

**Next qualified research gate:** When original-owner custody of the later 2,048-witness trained continuation is independently verified, use the **existing exact native module**, freeze old-world windows and pre-action selector from FIT evidence, and separate (a) whether a historical expert still predicts old behavior from (b) whether selection ever improves over global mixture, full-history fitted Beta, recent-window Beta and hazard/HMM controls. The existing original-world source-owner NO-GO is separate; do not request new protected actions to interpret this retrospective negative.
