# DWSA-BR01 frozen-source independent reconstruction — 2026-11-21

**Scope:** read-only numerical recheck of already-scored synthetic DEV data. This is NOT a second experiment, new source first-use, native Yggdrasil integration, CLI qualification, full regression, cold model restore, or scientific promotion.

## Custody
- Accepted main: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; original source result branch head **before this receipt**: `c54fb3a547b8971f896435223ce16fec30eb0403`.
- Frozen preregistration: `510f06ede757e33900fadc63735842c2e75fd87b`; [protocol](PROTOCOL.md), [implementation](run.mjs), [original computed result](result.json), [no-go disposition](DISPOSITION.md).
- Donor source: `MasanneckLab/neural-networks-explained@149a2838309efe6ee5ec9e8c9689e4a321158b7d`.
- Upstream `public/assets/digit-model.json`: Git blob `16ea8cf939bfa0f5f21e227d159b11d4ff578eca`, independently returned unchanged by original GitHub contents read.
- Upstream `src/models.js`: Git blob `6f95eea88422ceb01b3118e65cd45b9a4c065bd9`, independently returned unchanged by original GitHub contents read.
- Candidate `result.json` read back from exact `c54fb3a547b8971f896435223ce16fec30eb0403`. All source reads used the GitHub connector; no upstream source or model was executed.

## Independent calculation
A newly written evaluation implementation in a separate isolated JavaScript invocation parsed the original weight JSON and generator text. It reconstructed each 35-to-10 linear weight-path response by propagating **one-hot basis vectors through all four matrices**, rather than using `run.mjs`'s repeated matrix-matrix multiplications. It independently regenerated the frozen 200-example class-major calibration sequence and the two 2,000-example class-major evaluation streams with the preregistered Mulberry32 sampler, proposals, sorted majority confidence, per-class non-regression gate, and Hamming classifier. It compared **every class-level correct count** for all six arms, both held evaluation streams, and the repair proposal/acceptance/training counts against the committed JSON. No additional source episode or unseen cohort was accessed.

The first source-parser attempt failed before scoring because the original generator's authored template array has a legal JavaScript trailing comma, not valid JSON. That verification-script-only parse was corrected by removing trailing commas before JSON decoding; the second independent reconstruction completed without altering frozen data, source, method, seeds or results. This was an **infrastructure/parser failure** in the recheck, not a scientific negative or test-data retry.

| Frozen arm | 7% noise: exact correct / 2000 | 12% noise: exact correct / 2000 |
| --- | ---: | ---: |
| DWA original | 1,603 | 1,424 |
| DWA + bounded repair | 1,860 | 1,666 |
| Zero-initialized + same bounded repair | 664 | 582 |
| Same-label fully fitted 350-bit bank | 1,978 | 1,931 |
| Authored-source template upper bound | 1,978 | 1,931 |
| Donor fully replaced by fitted 350-bit bank | 1,978 | 1,931 |

**Exact match: PASS.** All 12 arm/stream total counts and all **120 per-class counts** matched the committed `result.json` exactly. Bounded donor correction: 74 proposals, 11 accepted, 63 rejected; per-class accepted bits and calibration counts matched. Zero-seeded repair: 145 proposals, 5 accepted, 140 rejected; training counts matched. **Mismatches: zero.**

## Meaning and remaining gates
- This independently corroborates the *numerical reproducibility of the familiar synthetic screen*, not novel-world transfer, long-term functional retention, or native training.
- The fitted conventional control remains stronger: 98.90% vs 93.00% in-family; 96.55% vs 83.30% under stronger noise. **SCIENTIFIC PASS: NOT VERIFIED; mechanism not competitive with matched fitted control; do not promote.**
- The committed Node `run.mjs` CLI was **not** independently executed against a local checkout containing the donor files. The current cloud agent cannot reach public GitHub directly from its isolated shell, and the GitHub connector does not mount source bytes into that shell. This reconstruction is a separate JS implementation, **not Node CLI verification**.
- Cross-process native cold restore, G29 atlas, mandatory exact-candidate full Linux/Windows regression, original-world action-consequence, unfamiliar-family retention/transfer, and owner-authorized protected first-use remain **UNVERIFIED/NOT AUTHORIZED**.
- The source-owner issue [#426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) still marks new protected original-world first use **NO-GO**. Stop rather than reusing consumed original episodes or treating synthetic template noise as unfamiliar worlds.
- Deployment and accepted model changes: **NONE**. Preserve original negative DWSA-64 evidence under [PR #1347](https://github.com/spoonman136668-ai/Yggdrasil/pull/1347).

**Disposition:** DEV numeric replay PASS, engineering execution qualification PARTIAL, scientific superiority NO-GO/UNVERIFIED, deployment NONE. No new PR, actor, scheduler, runner dispatch, queue, native checkpoint, or original-world trial was created.
