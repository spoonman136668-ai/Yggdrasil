# ENERGY-43 — Unknown causal-factor support discovery and cold retention

**2026-11-18 · External synthetic contributor development · DEVELOPMENT_NO_GO**

**ENGINEERING:** Local frozen source primary, independent source/model reconstruction, 116,772 audit assertions and outcome-only semantic replay **PASS**. Yggdrasil native regression, independent scientific first-use and acceptance **NOT RUN**.  
**SCIENCE:** **DEVELOPMENT_NO_GO**, 3 of 7 preregistered gates.  
**DEPLOYMENT:** None. Evidence archived exclusively to existing draft PR #1210; no merge, accepted-ref, model, controller or runner changes.

## What was tested

ENERGY-41/42 learned weights over three supplied structural factor groups. ENERGY-43 asks a different question: can one sequential learner **find the unknown factor supports** using actual randomized interventions and noisy observed consequences, remember old relationships after new learning, and generalize under a distribution shift of noncausal cues?

Each of 36 independent source worlds has 12 binary action coordinates. An unknown signed causal law combines **five latent factors** from the first ten coordinates: three shared across contexts, one old-only and one new-only. The learner receives **no planted support indices, signs, weights or hidden labels**. The known but broad *grammar* contains unary/pair/triple parity and pairwise conjunction functions, 364 possible base supports, with context-gated copies. Thus this is **bounded structural discovery within a supplied grammar**, not unconstrained concept/operator invention, native Yggdrasil cognition or open-world general intelligence.

Each world supplies 96 old-stage and 96 new-stage **randomized do-interventions** with labeled real-valued consequences (Gaussian noise σ=0.3). Each model is trained on the same 192 outcome observations and tested on 128 independent interventions each in old, new and third **cold new-stage** domain. The two cue variables change correlations between old/new/cold domains but never causally affect the generating law. They are not identified to learners.

The proposed candidate uses sparse residual-contrast discovery, retains three first-stage factor structures, rehearses all old labels, anchors their coefficients during second-stage learning, and fits up to seven supports. Eight control arms include no-memory, conventional anchored OMP structural memory (equal support/replay budget, no special anchoring), full sparse OMP, ElasticNet, Ridge, a 60-tree forest and a shuffled-label sparse negative. The two dense models and forest have greater capacity than the sparse candidate; results are compared against **all** conventional fitted controls, not only weaker/same-capacity models.

## Frozen custody and cohort

- Prior evidence archive HEAD: `4fc4b038aa982046801530fac9276c97276eaf8c`.
- **Experiment and separately authored auditor first committed:** `8d828ce929f3c625141858df2a510ce810ab7eb8`. Decompressed source SHA-256: `48a798f75c1afc9701158edb4131d076dbe07f9dd3ad9374b9095ad2b47fe79f`. Auditor: `b838cf23568016d97c068c8ea0e1e818b9355ab3a28992d602d1cb4f4d775e61`.
- **Seven gates, seeds, data/cost budgets and interpretation committed before any primary score:** `288ee9322dfda7975ea40d687ca5cb6b37f92bd5`.
- Smoke-only seed `99811`: 3 excluded worlds and independent **9,753-check** source/refit audit PASS. No primary seeds evaluated in smoke.
- Primary: seeds **8617, 8629, 8651** × world IDs **0–3** × families **parity2/parity3/mixed** = **36 worlds**. A total of **6,912 labeled training interventions**, with **4,608 disjoint old, new and cold labels per domain**. A planted truth is used solely by the after-training evaluator and the independent postscore auditor.
- One frozen primary and one unchanged-source replay; no primary tuning or after-score change to weights, criteria, capacities, seeds or source.

## Primary results

**Held mean-squared error (MSE, lower is better)**

| Fully trained arm | Old after stage two | New | Cold unseen cue distribution | Local sum of fit+predict wall seconds |
|---|---:|---:|---:|---:|
| **Conventional OMP + structural memory** | **0.097645** | **0.104496** | **0.123558** | 0.3948 |
| **Proposed structured-energy + retention anchor** | 0.122600 | 0.108923 | 0.139290 | 0.4803 |
| Same energy without structural memory | 0.126870 | 0.116557 | 0.135193 | 0.3832 |
| ElasticNet full grammar | 0.142819 | 0.141226 | 0.188399 | 0.4939 |
| Standard OMP full grammar | 0.168621 | 0.179586 | 0.366623 | 0.4102 |
| Ridge full grammar | 2.121190 | 1.925957 | 2.292251 | 0.4265 |
| Random forest on raw interventions | 2.657509 | 2.662012 | 2.871544 | 1.8923 |
| Shuffled-label sparse energy (negative control) | 4.806120 | 5.976500 | 5.870804 | 0.3971 |

The candidate is **12.73% worse cold MSE** than its strongest comparator, anchored conventional OMP (0.139290 vs 0.123558), rather than at least 10% better. It **also loses to the no-memory energy ablation** on cold MSE (0.139290 vs 0.135193). It is 1.17× the standard full-OMP local fit+prediction component cost (0.4803/0.4102), passing the 2× ceiling but not demonstrating an energy efficiency gain.

**Exact learned structure:** the proposed learner recovered all **five hidden support identities in 35/36** worlds (mean factor recall **99.44%**); the conventional structural-memory OMP recovered **36/36** (mean recall **100%**), and no-memory energy 33/36 (97.78%). **This is a shared win for finite-grammar supervised factor discovery, not energy-specific structural superiority.**

**Retention failure:** candidate old-context MSE before second learning stage **0.092913**, after stage two **0.122600** — **31.95% more error**, exceeding the maximum 10% regression; the conventional structural-memory control after stage two is also better (0.097645). A model can identify latent supports while still damaging predictive weights during further training.

### Frozen gate accounting

| Gate | Result |
|---|---|
| ≥10% cold MSE improvement over strongest trained control | **FAIL** |
| ≥60% exact support recall across all five hidden motifs | **PASS — 99.44%** |
| ≤10% old-context prediction MSE inflation after new learning | **FAIL — +31.95%** |
| ≤5% old MSE disadvantage vs strongest conventional control | **FAIL** |
| ≥20% cold MSE improvement over shuffled-label negative | **PASS** |
| Strict positive cold improvement over strongest trained control in ≥2 of 3 seeds | **FAIL — 1/3** |
| Fit+prediction local component time ≤2× full-grammar OMP | **PASS — 1.17×** |

**3 PASS / 4 FAIL → DEVELOPMENT_NO_GO**. The true-support recall gate's source key contains the word `shared` for legacy reasons; its frozen mathematical denominator includes **all five** shared and stage-specific planted supports.

### Postscore diagnostics (not extra acceptance gates)

| Primary seed | Candidate cold MSE | Anchored conventional OMP cold MSE |
|---|---:|---:|
| 8617 | 0.09452 | 0.09552 |
| 8629 | 0.18826 | 0.14583 |
| 8651 | 0.13509 | 0.12933 |

| Mechanism family | Candidate cold MSE | Anchored OMP cold MSE |
|---|---:|---:|
| Parity pairs | 0.09595 | 0.09584 |
| Parity triples | 0.18550 | 0.17651 |
| Mixed parity/conjunctions | 0.13642 | 0.09833 |

These are **postscore** analyses to diagnose failure, not license to select a better-looking primary subset or retune on consumed seeds.

## Independent technical evidence and limitations

- Scorer and auditor are **different source files**, and the auditor does **not import** the scorer. It reconstructs independent seeded actions, hidden factors, noisy labels, all eight fitted control/candidate methods, support IDs, coefficients and old/new/cold predictions. The auditor returned **PASS, 116,772 checked items, zero errors**. Both codepaths use common third-party NumPy/scikit-learn implementations, so this is **not** independently implemented linear algebra or random-forest infrastructure.
- Exact unchanged-source replay: **PASS on all non-timing semantic data**, SHA-256 `ae3e3f64b103eabe45b4cad9b3ef3d49159897170746a7d3ce3e76488e5ae3c4` over 74,516 canonical bytes. The first raw canonical comparison differed **only because the primary decision object included numeric timing-derived CPU totals**; excluding those two totals as well as ordinary wall/fit/predict timings produced byte-identical outcomes and frozen gate decisions. Do not claim timing fields reproducible byte-for-byte.
- Complete original timing-bearing primary `scored.json`: **164,277 bytes**, SHA-256 `853b6fdeb4a38fa77b7dcd49afeffd7d678f34000a74e368fbb9777b7d7210fa`, remains in the local research workspace **and was not uploaded**. The repository has compressed **36-world detailed case receipts** with per-arm old/new/cold MSE and learned structure indices, plus source to regenerate the full result. The original full raw timing fields are not in GitHub.
- The observable result comes from supervised additive Boolean factor functions under randomized interventions, with a **known finite grammar**, synthetic Gaussian noise and no agentic choice of informative interventions. There are no real-world data, independent unfamiliar mechanism families outside grammar, neural weight-based native Yggdrasil learner, or measured autonomous cognition. This external experiment cannot be construed as real native continuous training or scientific first-use.
- Local OS Linux, Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, CPU-only; single-threaded BLAS, no paid APIs. All timing figures are one-run Python fit/predict wall measurements, **not full system runtime, energy consumption or physical compute efficiency proof**. GitHub code-atlas CI and native cross-platform acceptance are separate engineering gates and do not change the scientific classification.

## Reproduction

Use this archive's immutable sources and preregistered protocol; SHA-256 verification must precede execution. In the ENERGY-43 directory:

```bash
python - <<'PY'
import bz2,hashlib
from pathlib import Path
for fn,sha in [('experiment.py','48a798f75c1afc9701158edb4131d076dbe07f9dd3ad9374b9095ad2b47fe79f'),('audit.py','b838cf23568016d97c068c8ea0e1e818b9355ab3a28992d602d1cb4f4d775e61')]:
 b=bz2.decompress(Path(fn+'.bz2').read_bytes())
 assert hashlib.sha256(b).hexdigest()==sha
 Path(fn).write_bytes(b)
PY
python verify_archive.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --primary --out fresh_scored.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py fresh_scored.json --out fresh_audit.json
```

A fresh run must reproduce all non-timing case observations, fitted supports/coefficient values, MSEs and seven gates. Timing-derived totals naturally vary. Do not use a rerun to retune against primary seeds.

## Decision

**Freeze and stop this particular anchored structured-energy proposal.** Structural factor learning works well **within the supplied grammar**, but its additional coefficient anchoring **hurts** cold transfer and memory retention against a simpler conventional structural-memory baseline. A justified successor, if any, must independently test preservation/repair of learned weights and longer cumulative sequences **without consuming these primary seeds again**. Do not promote to native Yggdrasil, FORGE, research controllers or accepted science.
