# WSCM-COLD-READ-01 — Genuine archived native checkpoint, full/pooled readout audit

**Outcome: default forecast parity 216/216, fixed conditioning is not a demonstrated cumulative-memory fix.** This remains a read-only *retrospective* research contribution under the existing [WSCM PR #1364](https://github.com/spoonman136668-ai/Yggdrasil/pull/1364), stacked directly on [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) at `86264b41a08d49f558418c0fba367f3a2636befa`.

## Original state verified

Downloaded the original **unexpired GitHub Actions artifact 14492525071**, `Amalgam-shared-consequence-ubuntu-latest.zip`, from workflow run `44442089107`. The archive includes `amalgam-joint-state.json`, **2,921,047 bytes**, SHA256 `576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8`; this matches `selection_protocol_dev.json`'s pinned joint checkpoint. Its native state SHA256 is `5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d`, native parent `a00119c73a6431172c19b39ec67a1d94b470897a32c55c1c946071793f37dcc4`. Inside, the original `NativeEpisodeExperience` contains **1,025 authentic engineering-fixture witness receipts**, with recorded state digest `3c6433c9e60a0f7e6b750327ae7b705984fb20b25e8bd04fe16a3e9a31c9dde8`.

The previous CKAD26 original parent artifact `14470790752` was also retrieved read-only and its `seed-101-refresh-native.json` SHA256 `a00119c73a6431172c19b39ec67a1d94b470897a32c55c1c946071793f37dcc4` verified. **No new world action or source data generation**.

## Exact readout custody and meaningful result

The local diagnostic reconstructed native episode models from the source-equivalent, fixed parent code semantics (`native_episode_experience.py` Git blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`; `public_causal_cells.py` Git blob `de8722f38d987ef7bcb4b7a0c23466b8e6f25712`). Source model blocks, 1/8 novel prior, 1/32 refresh, exact Fraction Beta counts/likelihood weights, and transition-conditioned terminal weights were reconstructed in a local *independent implementation*. Its **default/pinned** native forecasts match **216/216** already saved prequential forecasts in three prior staged-retention source traces **exactly to the original 1e6 probability encoding** (seeds 818621/818653/818687, 72 witnessed rows each, no mismatches). Their immutable Git blob pins are recorded in `result-summary.json`.

The table `native-readout-lookup.json` is the **exact byte-identical** 16-row (public context × action1 × transition outcome × action2) local output; Git blob `4aecd1529179fd1ddd93d5ea9dd3a1bafc980352`, raw SHA256 `936cbb650e9eac6115d96fa5e3fb0c0700d0bfecf6a94c62785d1fa0381623a6`. Every row contains the original default prediction and the same archived native memory with each component forced to its fully conditioned readout or its pooled readout. The held checkpoint is never updated to create these alternatives.

| Historical stage (72 events each) | Default/pinned Brier | Forced full | Forced pooled | Continuing native |
| --- | ---: | ---: | ---: | ---: |
| First changed stage | 0.301633 | 0.317095 | 0.297493 | 0.172604 |
| Second changed stage | 0.169413 | 0.163807 | 0.167962 | 0.194227 |
| Familiar return | 0.129036 | 0.139565 | 0.126794 | 0.143066 |

**Lower Brier is better**. Each value averages transition and reward loss, with each of three original trace seeds weighted equally. All rows already consumed in the earlier development experiments.

The fixed full readout slightly improves the **second** changed stage but worsens **both** the first changed stage and familiar return; fixed pooling improves these frozen-state aggregate losses slightly but remains far worse than continued learning on the first changed regime (0.297493 vs 0.172604), and it degrades some public-context strata. **Neither is evidence of successful cumulative learning or a causal repair.** Fixed pooling may merit a separate *prospectively frozen* test, but it is not a standalone memory solution based on this posthoc cohort.

## Qualify with the original native implementation

`cold_ablation.py` is committed to run on a checkout of the original **real** native Python source. It explicitly restores the archived native checkpoint using `NativeEpisodeExperience.restore`, verifies exact checkpoint replay and 216/216 recorded default forecast parity, and constructs pooled or fully conditioned shadow forecasts directly from its context models without writing native state. `tests/test_wscm_cold_readout01.py` tests the interface on synthetic real-native episode fixtures, no original world first-use.

The **new original-native script and native fixture unit tests have not been executed inside this sandbox**: the original complete Yggdrasil checkout is not locally mounted, so the local run used the independently reconstructed source-equivalent native readout instead. The 216/216 parity plus original source/checkpoint pin establish strong engineering consistency, but this does **not** replace final code-level execution, exact-candidate full Linux/Windows regression, or independently authorized acceptance.

Example when the full parent repository is available and the already archived artifact has been unpacked:

```sh
python -m unittest discover -s tests -p test_wscm_cold_readout01.py -v
python research/contrib/chatgpt/WSCM-COLD-READ-01/cold_ablation.py \
  --joint /path/to/Amalgam-shared-consequence-ubuntu-latest/amalgam-joint-state.json \
  --repo . --out /tmp/wscm-cold-ablation.json
```

The script refuses checkpoint or original trace byte drift before reporting. It does not dispatch CI, perform online science first-use, train JEPA, change Genome, accept a new causal learner or mutate `.ice`.

**ENGINEERING:** local source-equivalent 216/216 default native parity PASS; exact original-code integration tests/full dual-OS regression UNVERIFIED. **SCIENTIFIC:** retrospective fixed-state readout diagnostic, memory/transfer gain UNVERIFIED. **DEPLOYMENT:** UNVERIFIED, draft/unmerged, no native writes.

**Next decision:** Before any new architectural patch, reproduce the exact original-code cold audit and compare its **context-specific full/pooled** vs *existing selected context-mixture readout* in a separately preregistered A→B→A run with independently fitted exact Bayesian controls and matched actions, compute, source authority and functional cold retention. Do not tune these variants further on the already scored cohort.
