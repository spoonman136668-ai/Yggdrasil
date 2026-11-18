# CKAD25-T — Evidence-certified selective native repair (frozen prospective development)

**Goal:** Test whether the existing tokenless `NativeCumulativeLearner` can avoid confidently wrong sparse repairs on genuinely **new synthetic causal families** without losing useful, justified answers.

## Why this study

Previous CKAD25-S PR #1241 produced a real cumulative native development experiment across four law families. The original degree readout achieved Brier 0.1875, while automatically accepting eligible conventional GF(2) sparse repair worsened it to 0.229166667 (24/48 answered; only 19/48 correct). A separate old-CKAD25 synthetic fixture had been repaired retrospectively in CKAD25-R PR #1240 (4/4), but that fixture was consumed and does not prove prospective transfer.

**Distinct frozen new evaluation:** `xor4` (four-way parity), `nand2`, `cross_mux`, and `threshold4` from three independent predeclared shuffle seeds 4409, 5519, 6637. For each seed-law family, 12 training do-action/outcomes (8+4 stages) and four hidden held outcomes; total 144 NEW synthetic train and 48 new held actions. Different seeds of the same four fixed laws **are not independent causal families**, and separate native slots supply an explicit episode/law boundary.

## Candidate and strong controls

The same CKAD25 native checkpoint is cold-restored, trained in existing slots 1–4 and left unchanged in slot 0. Candidate **does not modify the native algorithm or weights on accepted main**. For a query, preserve the native degree model's confident answer when eligible. If degree abstains and the pre-existing minimum-support sparse repair predicts a bit, issue that bit **only when every conventional ANF hypothesis with ≤3 terms that fits all 12 training observations also agrees**. If the sparse hypothesis space is empty, disagrees, or lacks consensus, abstain at 0.5. The user-facing candidate is an external source-free research readout; any future native integration is a separate owner-qualified change.

Controls consume identical revealed rows: no-memory 0.5, fitted frequency, fully fitted CART, fully fitted RF64, fully fitted logistic ANF, exact uniform posterior over all 697 ≤3-term ANF combinations, conventional exact agreement-certificate readout, unmodified native degree, and ungated native sparse repair. The certificate is itself **conventional inference**, not native invention, and cannot establish intelligence or outperform its own exact hypothesis class by assumption.

All seven usefulness/retention admission predicates (including the per-family wrong-prediction constraint) are frozen in `prereg.json`. No tuning of consumed CKAD25-S family outcomes or current held outcomes, no threshold revisions, no extra data or paid model.

## Custody and scientific boundary

- Parent = sealed CKAD25-S PR #1241 head `01ffab6d6493004ff3cd28bdf4e9c36cd4fa1170`. Main still `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- First prereg before source = `b48c6f56e1883979461962932e75ea362d374a1b`.
- Frozen new executable source before scoring = `812a49ff80256766ecc7e08c01f09eda0af1d243`, Git blob `650a84097ba06aa0373f988ef8acb5d11619929c`.
- Previous unchanged CKAD25-S shared helper Git blob `31e06746dd2fa83cf4bfedf28da43cacbc68c99f`. **Only helper functions are imported; prior consumed source score is never replayed as new evidence.**
- Original native CKAD25 source checkpoint SHA256 `c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f`.
- Source is repository-local synthetic procedural code only. No protected original causal-environment action/seed/data, source-owner first-use, model controller, scheduler, FORGE authority, accepted ref, paid API, merge, promotion or deployment.
- `SCIENTIFIC_PASS=false` by construction. Focused cross-platform tests, even if green, are not full native regression or accepted first-use. Keep failed gates and science negatives unaltered.

Example (uses the native developer dependencies already pinned by CKAD25):

```bash
python -B research/contrib/chatgpt/CKAD25-T/run.py --output "$RUNNER_TEMP/ckad25t-result.json"
```

One primary source-frozen cohort plus a byte-identical replay on both GitHub-hosted platforms. Independent original-source scientific transfer remains a separate authorization and experiment.
