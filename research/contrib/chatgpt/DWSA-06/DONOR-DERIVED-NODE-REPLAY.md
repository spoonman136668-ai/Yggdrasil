# DWSA-06 — actual donor-derived 84-byte checkpoint cross-runtime replay

**Verdict: ENGINEERING LOCAL PARTIAL PASS.** This result independently qualifies the real trained-weight-derived compact checkpoint bytes, restores and Hamming classifications under Linux Node.js. It is **not** end-to-end Node execution of the original upstream weight-to-checkpoint compiler, a dual-OS CI PASS, a new scientific task, nor Yggdrasil integration.

## Exact custody before replay

- Accepted Yggdrasil `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; DWSA-06 draft research PR #1347.
- Original licensed donor repo: `MasanneckLab/neural-networks-explained@149a2838309efe6ee5ec9e8c9689e4a321158b7d`.
- Pretrained model weights file `public/assets/digit-model.json` Git blob `16ea8cf939bfa0f5f21e227d159b11d4ff578eca`.
- Public template/RNG source `src/models.js` Git blob `6f95eea88422ceb01b3118e65cd45b9a4c065bd9`.
- Source training code `scripts/train.mjs` Git blob `1776478a312781e0866f16e1ef237fcbc1092d1a`.
- Committed original weight-only core `run.mjs` Git blob `eee673dd0e8af3089bc5d1b686e4e00627940ead`.
- Reverified all pinned source Git blob identities using connected GitHub; **no source model forward calls**.
- Third-party original templates: Copyright (c) 2026 MasanneckLab, MIT license. Attribution and source license link retained inside `test_real_checkpoint.mjs`. Only 350 public template bits and the derived 350-bit checkpoint are included as research test fixtures, not the original trained weight checkpoint or teacher outputs.

## Method

1. Execute the **exact committed pure `analyze(model,source)` function body** in an isolated V8 environment with the existing pinned pretrained model JSON and source template text. No Node import or donor code import. The original weight-only path-statistic computation re-produced `1615/2000` same-template 7%-noise correct and the conventional control `1985/2000`. The independent exact committed `untrained_ablation.mjs` core was also executed and reproduced original exact-init `230/2000` and best untrained `21.35%`.
2. Extract only the computed 52-byte canonical checkpoint body `DWP6` + 350 bit-packs, *before* its SHA-256 seal. Exact body hex:
   `4457503601000a2354765cc4b573a0676eef2888eeec21784343b9d0f787d453e12f91087a7137dceab9d85462a8c4ea8e5e1090`.
   Source-trained per-class prototype ones counts: `[17,19,19,14,20,19,14,22,15,14]`.
3. Independently load that derived body into **local Node v22.16.0**, compute its SHA-256 seal to 84 bytes, and pass the result through the original exact-`blob` `codec.mjs` module. Re-encode parity, three cold restores, seven independent corruption rejection checks, and full Hamming scoring were performed.
4. Node regenerated exactly **1615/2000 (80.75%)** correct at fixed seed `637127`, with per-class counts `[198,106,124,195,196,176,194,65,180,181]`. No teacher-generated labels, source model activations, source inference or training.
5. Final 84-byte donor-derived checkpoint SHA-256:
   `a32ff3ae95dbe040b87b9763a1586fdb4a2e459b5375de99fe9c7a8a8e444135`.
   The local Node script output was captured as a standalone diagnostic receipt; **no private original checkpoint** was committed to this repo.

## Exact executable source evidence

- `codec.mjs` Git blob **`b8d8f2e46d346d55e9a4c4efa116e796a663881e`**, identical to local Node-loaded bytes.
- `test_real_checkpoint.mjs` Git blob **`7ac69288cfd8994895cf58b435f60b7f5f8c9ecf`**, identical to local Node-executed bytes, even after adding upstream MIT attribution.
- Local command: `node research/contrib/chatgpt/DWSA-06/test_real_checkpoint.mjs` with `codec.mjs` in same directory, using Node v22.16.0 on Linux. The script has only Node built-in imports; it does not require the external donor or network to replay the frozen representation.
- Previously independent `node --test test_codec.mjs`: 6/6 local unit tests PASS on the same exact codec Git blob. These tests were **not repeated** in this gate; the seven *real-checkpoint* corruption cases and three cold restores are a new, nonduplicated test.
- The original donor-facing `run.mjs` / `untrained_ablation.mjs` / `layer_intervention.mjs` full Node CLI execution on pinned raw source files remains **UNVERIFIED**. The V8 pure-core replay and Node compact-recipient replay test different interfaces; do not collapse them into a claim of original-script end-to-end PASS.

## Scientific and engineering boundaries

The 80.75% result remains a same-law template recognition development signal. A same-84-byte directly fitted supervised prototype and the exact symbolic-template control already score **99.25%**. No unfamiliar causal-world transfer, action-consequence learning, cold **cognitive** retention, interference repair, autonomy, first-use or scientific gain was tested.

Current mandatory GitHub G29 generated-atlas source check failed on both OS at [run #44726558108](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44726558108), before DWSA tests. A new source-only research file may trigger the same pre-existing atlas fail; this is NOT a scientific failure. Full candidate-SHA Linux and Windows regression and accepted owner handoff remain **UNVERIFIED**. Do not merge/promote without separate authority and qualification.

**Disposition:** ENGINEERING donor-derived checkpoint cross-runtime Node local PASS; original full Node compiler & CI acceptance UNVERIFIED/atlas-blocked. SCIENTIFIC cross-world gain UNVERIFIED. DEPLOYMENT NONE. Accepted Yggdrasil and its sole Amalgam coordinator remain unchanged.
