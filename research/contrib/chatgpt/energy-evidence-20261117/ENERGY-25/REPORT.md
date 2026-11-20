# ENERGY-25 — Structural causal constraint discovery on disjoint interventions

**Date:** 2026-11-18. **Classification:** isolated synthetic CPU development study. Native Yggdrasil checkpoints were **not executed or modified**. No protected original-source first-use; no model promotion or deployment.

## Hypothesis, frozen before held scoring

Can a learned 3-body conditional energy factor recover an unknown three-parent causal parity relation from 16 actual action-consequence observations and predict the 16 distinct unseen intervention combinations? Compare to a pairwise energy learner, a **fully fitted capacity-matched conventional cubic ridge learner**, and an **exact fully fitted Bayesian rule-hypothesis learner** with the same evidence. Frozen development threshold: >=90% held accuracy and >=20 percentage-point improvement over pairwise. No synthetic result can establish SCIENTIFIC_PASS.

Each environment chooses a hidden parent triple from the ten unordered 3-of-5 subsets plus one sign (20 structures). The public interventions select all 5 binary action bits and observe the sign of the parity of the three hidden causal parents. Other action bits are nuisance factors. Exactly 16 unique actions and corresponding true consequences are shown to all models; the other 16 never enter training. A SHA-256 permutation fixes the split per structure and seed. Four preregistered primary seeds (103,211,307,401), **80 independently fitted world-specific models**, each evaluated on **16 disjoint held actions =1,280 held outcome predictions per arm**. The single separate smoke seed is 809. All model fit budgets and input data matched; no protected data or original Yggdrasil CKAD stimuli used.

## Primary frozen results

| Model/arm | Held correct | Held accuracy | CPU fit+predict wall, 80 worlds |
|---|---:|---:|---:|
| Pairwise conditional energy (intercept + five first-order factors) | 452/1280 | 35.3125% | 5.693 ms |
| 3-body learned conditional energy (10 triple factors + same first-order) | **1,055/1,280** | **82.421875%** | 8.823 ms |
| Fully trained conventional cubic regression, identical features/loss/penalty | **1,055/1,280** | **82.421875%** | 6.583 ms |
| Fully fitted Bayesian 20-rule hypothesis control, 5% label-noise likelihood | **1,280/1,280** | **100%** | 21.821 ms |

All 80 hidden parent triples and signs were correctly recovered by the largest-magnitude learned 3-body coefficient; **yet 225/1,280 held outcomes were classified incorrectly** by this ridge energy model. This exposes the critical distinction between identifying a dominant parent relation and reliably predicting the complete outcome for unseen action configurations: correlations/aliased secondary features in the underdetermined regularized fit can still corrupt individual decisions.

**Frozen feasibility threshold FAIL:** 82.42% is below the >=90% requirement despite exceeding pairwise by 47.11 percentage points. **Scientific advantage FAIL:** the identical-capacity conventional model ties exactly and the well-specified Bayesian symbolic rule model is 17.58 percentage points more accurate. Total CPU time is for this optimized small NumPy/SciPy implementation on a local CPU and cannot be generalized to native GPU or CKAD inference.

## Independent audit and numerical caveat

A separately implemented auditor re-generated all 80 source truth tables and SHA-ordered splits, checked 1,280 held causal consequences, re-fitted the linear regression with a different augmented least-squares solver, independently recomputed Bayesian likelihoods using exact integer weights (19^correct at 5% noise), and reconciled every score. **Audit PASS:** 5,120 independently refitted held predictions assessed (80 worlds x16 held x4 arms); 80/80 parent relations confirmed; semantic replay PASS after excluding measured timing fields; immutable frozen source/protocol hashes match.

**First audit failure retained.** The initial auditor assumed numerical solver bitwise parity for all predictions. It failed: 15 individual cubic predictions across four worlds had different signs under two valid numerical solvers despite minuscule margins. A *post-score exact-rational normal-equation calculation* proved **32 held cubic model margins were mathematically exactly zero across six worlds**. Of those original 32 numerically unstable predictions, only seven matched the true held labels. Amended auditor explicitly accounts for two copies of the 15 near-zero differences (cubic energy and equivalent conventional model), rejects material-margin divergence, and verifies the exact certificate. No scored output, model parameters, seeds, or thresholds were changed; the primary 1,055 count remains as actually recorded, not claimed bit-for-bit portable. Zero-margin tie conventions affect exact score, but cannot reverse the no-go against a 1,280/1,280 exact Bayesian control.

## Reproduction and provenance

- Run `python -B experiment.py --smoke`, then `python -B experiment.py --out scored-replay.json` to regenerate the deterministic semantic result, ignoring performance timing differences.
- Run `python -B numerical_diagnostic.py` for a **post-score** rational zero-margin certificate (requires SymPy).
- Run `python -B audit.py` for the independent method/data audit (requires NumPy/SciPy/SymPy).
- Frozen source SHA-256 `bca7c75d8b0a5a7309fc387ed8cdde324538ac2b77b40ceb719c891cbe004c19`; frozen protocol SHA-256 `b0cb331d15aff549d84e247c8f76e9a6e4f69e3f21a251d16c144c6d879c168b`.
- Original scored file SHA-256 `6b7b90999096c56aba0590a8ce79a4d4584d7bbb8ee72d4877271171f2b78e11`.

## Decision

**ENGINEERING:** Local experiment/independent audit PASS with correctly disclosed numerical degeneracy; native Linux/Windows full regression UNVERIFIED. **SCIENCE:** DEVELOPMENT NO-GO on prereg 90% threshold and exact strong control; no CKAD improvement claim. **DEPLOYMENT:** NONE.

Research implication: The hypothesis bank used by CKAD is structurally appropriate for these few-shot causal-intervention tasks. A small unconstrained higher-order energy parameterization can recover a parent factor but still create spurious held conclusions; identifiability, posterior uncertainty, and explicit hypothesis consistency matter. An energy mechanism should not replace CKAD hypothesis selection without a newly frozen native test against exact controls. All prior ENERGY negative outcomes remain preserved.