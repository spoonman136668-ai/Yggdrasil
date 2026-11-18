# ENERGY-36 — Sparse-energy committee active causal witness selection

**2026-11-18; frozen prospective synthetic development; `DEVELOPMENT_NO_GO`.** No native Yggdrasil training, accepted-ref changes, scheduler changes, merge, scientific admission, or deployment.

## Why this exists
ENERGY-35 showed that acquiring 16 genuine cross-context consequences is beneficial, but the added pairwise loss did not outperform simpler energy learning or conventional methods. ENERGY-36 asks whether **choosing which 16 actions to witness** adds transferable causal information beyond fixed/random selection. A sparse max-margin energy committee (six independently bootstrapped models) selects candidate action patterns where its members disagree, plus a small source-label-blind diversity criterion. Control selectors: a matched six-model **conventional OMP committee**, single-energy uncertainty, fixed first 16 pairs, and independently hash-random 16.

Each selector's 16 witnessed new consequences are then used to **fully fit five separate downstream learners**: sparse energy (12 active coefficients), OMP12 (matched support), Ridge, Logistic Regression and depth-8 tree. This is **25 selector/learner arms**, with the same 80 old observations and 16 additional new observations per arm. The **actions and therefore the new observed outcomes can differ across selectors**, but each arm gets exactly 96 real witnessed outcomes. No selector uses hidden source-factor IDs, withheld action labels or evaluation truth.

## Prospective freeze and evaluator
- ENERGY-35 parent archive SHA: `70ae8db36ecb363a997bebeec5d35e1371d53b08`.
- Source, prerequisite and fully frozen seven-gate protocol committed **before primary** at `5671659318e7003104cbd96d6418fe3c29dd6673`. Source `experiment.py.bz2`: original SHA-256 `320ffbe34409b1f9eb49219f22e0f136a933e4604480e153f3a1afaf863d7b7e`; compressed Git blob `7335991ba27cfc7908ea435f61480d4a1996c8b5`.
- Primary seeds 7607, 7621, 7643; 8 independently generated worlds per seed × 3 causal families = **72 source worlds**. Smoke seed 99089 was excluded from primary.
- Fixed 8-bit intervention grammar, 190 predesigned parity and pairwise AND features, hidden 3-factor signed-majority causal response, independent Bernoulli 10% training-label corruption. No native model or protected dataset.
- Every source world gives 80 independently witnessed x0=0 old actions. The 80 possible x0=1 candidates are flips of those observed actions; each policy selects 16 without observing their consequences first. Evaluation uses the same 16 other disjoint x0=0 actions and 48 disjoint x0=1 actions **never selectable by any policy**.
- Active committee uses 6 source-only bootstrap fits and greedy maximum Bernoulli-vote disagreement plus 0.05 Hamming diversity. Frozen energy-uncertainty ablation uses a single model; fixed and random do no committee work. All source shuffles and bootstraps SHA256-seeded.
- Frozen gates: +3pp over **best other complete policy and fitted learner**, +2pp over energy uncertainty, +1pp over conventional OMP selector with same energy learner, no >1pp old-context regression, positive vs strongest complete control on ≥2/3 seeds, +5pp over shuffled-label negative, and selection+fit component time ≤1.5× random+OMP12.

## Scored primary: all 72 worlds, 3,456 x0=1 disjoint held outcomes per arm

| Selection policy | Sparse-energy final learner | Conventional OMP12 final learner |
|---|---:|---:|
| Energy disagreement committee | **2,985 (86.37%)** | 2,822 (81.66%) |
| Random 16 | 2,930 (84.78%) | 2,832 (81.94%) |
| Single energy uncertainty | 2,926 (84.66%) | 2,869 (83.02%) |
| Fixed first 16 pairs | 2,918 (84.43%) | 2,909 (84.17%) |
| Conventional OMP disagreement committee | 2,915 (84.35%) | 2,825 (81.74%) |

Across **all other 24 complete selector/learner combinations**, the best was random selection+energy at 2,930. Energy-committee+energy gained **55/3,456 = 1.59 percentage points**, failing the predeclared +3pp requirement. Compared to the single-energy uncertainty ablation: +59/3,456 = **+1.71pp**, failing the +2pp requirement. Compared to OMP committee selection feeding the exact same energy learner: +70/3,456 = **+2.03pp**, passing the frozen +1pp comparator.

Old-context retained held accuracy: energy committee+energy **1,096/1,152**, fixed first16+energy 1,098/1,152; within the prespecified 1pp tolerance. Shuffled-label negative on energy-committee-selected interventions scored **1,849/3,456** versus 2,985/3,456 using true witnessed labels, passing the negative-control gate.

**Seed-wise margin vs strongest other complete arm:** +3, 0, −22 held correct on the three primary seeds; only one strictly positive, failing the 2/3-seed stability gate. This is not a replicated improvement.

## Efficiency: the main obstacle
The complete energy committee acquisition plus final sparse-energy fitting/inference summed to **1.9797 seconds** over all 72 cases, while random selection plus fully trained OMP12 took **0.08874 seconds**, roughly **22.3× less** on this exact local implementation. Comparing with random+energy: 0.18701 seconds (~10.6× less). The committee expends six bootstrap fits per case to select actions. This is an information-matched comparison (96 observed consequences each), **not a compute-matched comparison**; the frozen ≤1.5× cost gate fails dramatically. Whole experimental Python process wall 8.891 seconds for all 25 arms and source generation. No controlled end-to-end runtime advantage, native speed improvement, or inference engine proof is established.

## Frozen classification
**PASS (3/7):** advantage over OMP committee selector when both use energy, old held retention, shuffled-label negative. **FAIL (4/7):** ≥3pp absolute shifted gain over strongest, ≥2pp uncertainty-ablation gain, ≥2/3 seed stability, policy cost budget. **Overall `DEVELOPMENT_NO_GO`.** The signal is suggestive on this finite synthetic source grammar but does not justify tuning against consumed seeds or promotion.

## Engineering provenance
- Original primary 539,531-byte `scored.json` SHA-256 `8f7d9bdfd31974522c9b4807106d61a10819ecd6e8fdf3e8a51e2176670f505b`. **This exact timing-bearing original is not uploaded.**
- The repository **does** preserve the full **126,072-byte deterministic semantic score record** in `semantic_scored.json.bz2` (11,545 bytes, SHA-256 `3ae450399f6af280ab9ce3133d7117ddde7698caa6080db35f187cbff0638d1d`, Git blob `eb32fa0f2dfa894e00fe165c80b9fe3bdaefd6cd`). All 72 case IDs, all chosen action receipts, witnessed consequences, all 25 fitted arm scores, negative controls and gates are included. Only aggregate and per-case timing measurements are removed; exact semantic replay hash `ff591f3f9d00c5de1b9c7323de53341c1fe17ff0506ba167d3f43219f0bd5dd2`.
- **Independent local refit audit PASS: 5,700 checks.** A separately implemented source grammar, action partitions, noise, all five selectors and all 25 fitted learner combinations matched source scores and selection receipts without importing the scorer. It uses the same independent scikit-learn conventional estimator implementations, so do not call this an independent library implementation. Source `audit.py.bz2` original SHA-256 `3afa76e1ff1065ac7c5db41d616c1acf674dc2376777c13f640b5fb2db5964d9`.
- Unmodified scorer replay on the identical seeds produced **byte-identical semantic JSON** after dropping only timing keys. Original whole runtime 8.891s; replay whole runtime 8.471s, local Linux Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0, CPU only, single-threaded BLAS.
- Mandatory full Yggdrasil Linux/Windows final regression, external scientific qualification and original native first-use **not executed**. The archive draft PR historically has a G29 code-atlas generated-index CI failure; keep CI separate from synthetic science outcome. No main branch, model source, controller, runner, research-loop, scheduler, merge, promotion or deployment changes.

## Reproduction
From the exact evidence-branch checkout, `cd research/contrib/chatgpt/energy-evidence-20261117/ENERGY-36` and run:

```bash
python - <<'PY'
import bz2,hashlib,pathlib
for file,digest in [('experiment.py','320ffbe34409b1f9eb49219f22e0f136a933e4604480e153f3a1afaf863d7b7e'),('audit.py','3afa76e1ff1065ac7c5db41d616c1acf674dc2376777c13f640b5fb2db5964d9')]:
    data=bz2.decompress(pathlib.Path(file+'.bz2').read_bytes())
    assert hashlib.sha256(data).hexdigest()==digest
    pathlib.Path(file).write_bytes(data)
print('frozen sources verified')
PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out replay.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py replay.json --out new_audit.json
```

Do not compare timing-bearing replay bytes against original. Use `verify_archive.py` to confirm frozen source and committed semantic score digests and scores.

## Research decision
**Stop this expensive six-bootstrap disagreement committee on consumed seeds.** The selection signal does not clear the predeclared margin or generalization-stability requirements, and is far slower than low-cost control policies. Any new candidate should test whether a **single-pass low-cost causal witness selector** can approach the committee's accuracy without bootstrap-model overhead, on completely fresh source worlds and independently frozen thresholds. It must not silently retune or reuse this cohort.

**ENGINEERING:** isolated local scorer/replay/independent full refit PASS, native CI/acceptance UNVERIFIED. **SCIENCE:** DEVELOPMENT_NO_GO. **DEPLOYMENT:** NONE.
