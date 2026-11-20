# DWSA-06 — independent Node codec qualification (local engineering-only)

**Qualification scope: PARTIAL PASS.** Original DWSA-06 weight-extraction and layer-intervention scores are unchanged; the external donor model was not downloaded, restored, trained, or forward-run in this gate.

## What was actually tested

- Standalone `codec.mjs`: strict 10-class × 35-bit Hamming prototype checkpoint, fixed **84-byte** layout (`DWP6` header 8 bytes, 44 packed bytes, 32 SHA-256 bytes); serialise, cold restore, strict decoded inputs, Hamming argmin/tie rule.
- `test_codec.mjs`: six Node built-in test-runner scenarios: deterministic byte parity and reserved pad, three cold restores, header/payload/digest/length corruption, recomputed valid SHA over invalid padding, malformed model/input rejection, deterministic Hamming classification/tie.
- Local Linux execution command: `node --test test_codec.mjs` (run with both files in the same temporary directory). **Node.js v22.16.0**. TAP output **6 tests, 6 passed, 0 failed, 0 skipped**, test process duration approximately **129 ms**. This timing is diagnostic and **not** model runtime speed or whole-process cost.
- Exact tested Git blob identities were verified against GitHub on this PR after upload: `codec.mjs` **`b8d8f2e46d346d55e9a4c4efa116e796a663881e`**, `test_codec.mjs` **`b34dc59b5b9845acb573a7fb8b5095ab2880b7b2`**. No source code drift between local tested bytes and committed blobs.
- New independent codec uses Node's built-in `crypto`, `node:test`, and `Buffer`, no package install, network request, paid API, or runner dispatch.

## Important boundaries

1. **This verifies the standalone codec module, not the existing `run.mjs`, `untrained_ablation.mjs`, or `layer_intervention.mjs` end-to-end.** The latter scripts retain their original local codec implementations and frozen score receipts. Their actual Node runs on exact pinned third-party model/template files remain UNVERIFIED.
2. Original scientific evidence is still the pre-scored ten-template synthetic development campaign: trained weight-path 80.75%, best untrained 21.35%, best mixed 66.65%; strongest equal-capacity conventionally fitted and exact symbolic 99.25%. There is **no scientific performance claim** from this codec test.
3. Linux-only Node v22 focused tests do not prove Python 3.12/Windows correctness, the mandatory full Yggdrasil final regression, regenerated code atlas or independent model acceptance. The latest previous G29 check failed at stale `.ice` atlas before research tests.
4. Accepted `main` remains `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. PR remains draft and unmerged. No native learner or source-first-use action, checkpoint promotion, controller or deployment change.

**Status:** ENGINEERING: independent native-format codec LOCAL PASS (6/6), end-to-end original program/full regression UNVERIFIED. SCIENCE: no new trial, all DWSA-06 evidence remains development-only. DEPLOYMENT: NONE.

**Next executable qualification:** exact pinned third-party `model.json`, `src/models.js`, `scripts/train.mjs` readback into a qualified Node runtime, run original scripts with their Git blob SHA checks; preserve exact data and output receipts. Then resolve generated source atlas and run required final dual-platform qualification before any integration discussion. No protected first use is implied.
