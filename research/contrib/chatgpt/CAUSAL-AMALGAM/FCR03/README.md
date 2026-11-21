# FCR03 — change-gated mechanism recall (source-free DEV negative)

**Outcome:** `DEV_NO_GO`. This is an isolated contributor screening result, not an accepted Yggdrasil learner, scientific experiment, true retained-memory gain, source-use authority, deployment, or merge instruction.

## Immutable provenance / commit ordering

- **Accepted Yggdrasil main:** `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` (untouched).
- **Parent Amalgam coordinator [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278):** `86264b41a08d49f558418c0fba367f3a2636befa` (untouched).
- **FCR03 preregistered before any primary outcome:** commit `95dac750ef5c9ccf9503543e553454cb137288e2`.
- **Exact tested code committed before the primary run:** commit `3bfa0cd51e02c16bc8124cd9d0b2f220377b245a` (four Python files). Source byte parity with local Python 3.13.5 test checkout was verified by Git blob hashes.
- **Primary trial:** executed ONCE after the code commit: new deterministic public fixture seeds `317101..317108`, eight cohorts × (80 familiar A +80 changed B +80 return A +80 recombined C +48 unfamiliar nonlinear D) = **2,944 consumed public fixture episodes**; no original-world actor or protected source.
- Original complete JSON result: `primary_result.json.xz`, 7,040 bytes XZ (Git blob `f9ca478fe6ff6d3fd7b694d70ec279c22bebfe34`; XZ SHA256 `ac986ca1f95db18997440e319f47103d415a2359fb9533924f8782b35dc7b5a8`). Decompressed 60,680-byte JSON SHA256 `a81297f6a0f0bf7c982f7c8656af85be92c432e321b5e49dfbea9b5beee92cee`. The original record includes per-seed per-arm evidence, cold-restored sidecar summaries and platform-dependent CPU observations.
- `result-summary.json` holds human-readable aggregate and per-seed outcome metrics. No source or metric was revised after the primary trial.

## Distinct experiment

Unlike the prior negatives (FCR01-S exhausted resource budget at **5.462×** native CPU; FCR02 cumulative mask selector failed reward recombination with **0.2810 vs 0.0385 Brier**), FCR03 uses bounded *stage-specific* snapshots of affine XOR laws learned from previously witnessed public input/output pairs. A precommitted mismatch-window alarm compares archived candidates against a newly fit law, then retrieves the lowest-error explanation without phase IDs or hidden data. The archive is capped at three per head and each active mechanism requires twelve public witnesses before archiving. This represents a **frozen hypothesis class**, not the discovery of arbitrary causal structure.

Matched information and actions are fed to six **fully trained** controls: exact public-input conditional Jeffreys Beta (full, trailing-32, trailing-16), a full-history Bayes mixture over the **same 8 transition/32 reward affine laws**, and hazard-weighted Bayes mixtures with hazard 1/32 and 1/8 in the **identical hypothesis class**. Both stage forecasts occur prequentially, before any episode's outcomes are admitted. The experiment's phase labels are evaluator-only. The D phase is a deliberately unfamiliar nonlinear negative control that is outside the candidate's hypothesis class.

## Frozen outcome — lower Brier is better

| Preset phase / prediction | FCR03 | Strongest matched control | Verdict |
|---|---:|---:|---|
| C recombination / transition | 0.00390625 | 0.00390625 (full affine Bayes) | TIE |
| C recombination / reward | **0.07773438** | **0.03097034** (hazard-1/32 affine Bayes) | **FAIL (+0.04676404)** |
| A return / transition | **0.05722656** | **0.02239503** (full affine Bayes) | **FAIL (+0.03483153; cap +0.020)** |
| A return / reward | 0.00390625 | 0.00082999 (full Jeffreys Beta) | Within +0.020 |

On the eight cohorts, **transition archive recall happened in all 8**, but reward archive recall happened in **2 of 8**. Cold sidecar replay and exact checkpoint parity PASS in all eight; checkpoint 751–757 bytes. The nonlinear D reward Brier was **0.22037760**, a negative diagnostic, not a learned generalization. **Both frozen development acceptance gates failed; do not rerun/re-tune these seeds and call it a new test.**

13/13 local stdlib focused tests PASS before primary execution, including cold replay; corrupted source/checkpoint rejection; phase-leakage API guards; source-free nonlinear non-identifiability; native-source admission is NOT implemented in this sidecar. The source-free CPU timings are **not** a matched native CPU gate. Exact Linux/Windows full repo regression, native runner SHA custody, authentic checkpoint restore from owner P0, independent science replication, and source first-use were **NOT RUN**.

## Reproduction (development fixture only)

```bash
cd research/contrib/chatgpt/CAUSAL-AMALGAM/FCR03
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_mechanism_recall.py test_dev_trial.py
# For deterministic score reproduction only; NOT an independent new scientific trial:
PYTHONDONTWRITEBYTECODE=1 python dev_trial.py > /tmp/fcr03-replay.json
# Recover the original one-time observation, including original CPU timings:
python -c "import lzma,sys;sys.stdout.buffer.write(lzma.decompress(open('primary_result.json.xz','rb').read()))"
```

Rerunning deterministic code can verify arithmetic, but the original consumed trial is **not new evidence**, CPU timing will differ, and first-use/reviewer approval remains separate. The current submission is a **falsified architecture variant**, retained as negative evidence. No promotion, no new controller, no paid APIs, no GitHub workflow dispatch, no original-source lease, no canonical learner changes.

**Next research criterion, not authorized here:** a distinct preregistered approach must address hidden-variable aliasing between old-stage mechanisms and observable cross-stage interventions, distinguish novelty from return-within-evidence, and outperform fully trained hazard Bayes + trailing controls under exact matched resource and cold retention boundaries. Preserve [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) protected source custody.
