# ENERGY-11 — Evidence-efficient learning over competing causal hypotheses

**Outcome: DEVELOPMENT NO-GO for faster reasoning.** Completed November 17, 2026, on an isolated Linux CPU sandbox. This is **not native Yggdrasil**, **not a CRAM reproduction**, and **not a scientific first-use or deployment**. Negative results are retained. Research sources, owners, runners, existing PRs and accepted models were not mutated.

## Verified repository custody

- `spoonman136668-ai/Yggdrasil` `main` `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- ENERGY-01 draft PR #1201 head `69123bc92cad8bc14fe6596f42d9b2f4e71a2542`, unmerged; CKAD draft #1182 separate head `5df8dbf506027b914f66e19441376d1347a3e09d` at the preflight read.
- Mind-Palace bootstrap and catalog were pinned at `4f0ef7cda0441116b253fc53ac11cedd47ce24dc`; schemas and matching `source.records_sha256` verified. Project-index material was advisory, not execution authority.
- A new ENERGY-11 GitHub PR was not created. No local-native Yggdrasil tests, repository full regression, GPU, or protected original environments were run.

## Pre-registered question and scope

Can a *classical numerical energy over 36 causal explanations* learn from a bounded sequence of interventions and reason with comparable accuracy, less cost and better action selection than exact Bayesian reasoning? A distinct trained recurrent network acts as an iterative comparison, **not a capacity-/compute-matched scientific claim about looped-model families**.

Each world contains a hidden Boolean causal law over an unknown unordered pair of four intervenable binary inputs. Candidate operations are AND, OR, XOR, XNOR, A-AND-NOT-B, B-AND-NOT-A. Thus the *operator vocabulary and parent-selection grammar are known*, while the realized relationship is unknown. Outcomes are flipped independently with a 10% chance. Each policy observes only **7** sequentially selected interventions out of 16 possible input assignments, including one common initial random observation, and predicts the noiseless consequences of the remaining **9** unobserved assignments.

The energy hypothesis score is the cumulative **negative log-likelihood of observed outcomes**, with online updates. Its approximate prediction and active selection retain the top six explanations. The exact Bayesian baseline uses all 36 explanations and the same calibrated observation-noise probability. Because its energy is a log probability, this is a compact **discrete posterior approximation**, not learned new physics, general causal discovery or a neural associative memory.

- Meta-training: 3,600 independent synthetic worlds and 720 validation worlds, excluding XNOR as a realized law. The energy and Bayesian baselines know the full fixed grammar; they fit observation-noise reliability from training. The GRU sees the same type of seven-event evidence sequences, supervised by the 16 true outcomes per training world.
- Test: 72 in-distribution worlds and 48 test worlds using XNOR, excluded as a **realized law** during recurrent meta-training but still present in the classical candidates. This is **held-out operator transfer within a specified grammar**, not discovery of an unknown operator type.
- Test labels, unseen potential outcomes, and world mechanism IDs are evaluation-only. Scored source files/thresholds/seeds were frozen and hashed before test generation. Source-free original synthetic data only; no reserved first-use worlds touched.
- Exact-on-energy is the most informative apples-to-apples inference comparison: it uses precisely the energy learner's chosen interventions and observations. Exact-active is a separate policy comparison. Random-active controls experimental design. Outcome-shuffled controls evidence dependence.

## Results: all 1,080 unseen predictions

| Method | ID 648 | OOD 432 | Total 1,080 | Brier lower better |
|---|---:|---:|---:|---:|
| Energy top-6 active | 539 (83.18%) | 333 (77.08%) | **872 (80.74%)** | 0.13187 |
| Exact Bayesian active | 544 (83.95%) | 343 (79.40%) | **887 (82.13%)** | 0.12155 |
| Exact Bayesian with energy's own evidence | 543 (83.80%) | 331 (76.62%) | **874 (80.93%)** | 0.12938 |
| Random intervention + exact Bayesian | 518 (79.94%) | 342 (79.17%) | **860 (79.63%)** | 0.13800 |
| Meta-trained recurrent GRU on energy's evidence | 533 (82.25%) | 187 (43.29%) | **720 (66.67%)** | 0.25526 |
| Reversed-evidence negative | 395 (60.96%) | 232 (53.70%) | **627 (58.06%)** | 0.29080 |

The energy model came within **2 of 1,080** exact-Bayesian answers on identical observations, passing its within-one-percentage-point **inference accuracy** subcriterion on both cohorts. However, exact-active selected better observations and answered **15 more** overall. The energy policy improved over random in the ID cohort by only **3.24 percentage points**, short of the required 5 points. On XNOR OOD it was 2.08 points **worse** than random. The baseline was stronger in Brier score.

The trained GRU reached its frozen validation-patience stopping rule at **epoch 62**, with the best checkpoint from epoch 50 and validation BCE 0.37024. This is a completed trained comparator, but training excluded XNOR, while the energy/exact hypothesis grammar included it. They also differ greatly in capacity, supervision and compute; the OOD comparison **does not establish architectural superiority**. The outcome-shuffled negative dropped overall accuracy by ~22.7 points, passing the evidence-dependence check.

## Timing and qualification

| Stage over the scored 120 worlds | Measured local wall time |
|---|---:|
| Energy active inference + online evidence updates | 0.03793 s |
| Exact Bayesian active inference + online updates | 0.03087 s |
| Uniform-random active exact inference | 0.01684 s |
| Common metadata/noise calibration | 0.10695 s |
| GRU training (separate meta-training) | 4.28210 s |
| GRU inference on the energy-acquired transcripts | 0.04181 s |
| Entire shared scored process (including source setup, generating meta-examples, other arms, I/O and audit-excluded steps) | 9.91 s |

Energy-active was **~23% slower** than exact-active in instrumented inference/updates, and still slower with the shared calibration cost included (0.14487 versus 0.13782 seconds). It failed the preregistered 2x whole-method cost threshold. Timing is Python/numpy/torch CPU implementation-dependent. A joint scored process cannot be used to infer precise separate full-process costs; data generation, framework initialization, and training-world generation were not apportioned by method. No FLOP or GPU equivalence is claimed.

**Local engineering PASS:** source-freeze `freeze.json` precedes scored execution; exact frozen SHA-256 hashes matched after. Independent stdlib/NumPy/Torch-primitives audit `audit.py`, without importing any primary scoring code, reproduced the generated test mechanisms/noisy potential outcomes, selected observations, energy scores, top-six and exact posterior outputs, intervention selection rules, metrics, state hashes, and exact GRU checkpoint replay. **10,400 audit checks PASS**; 120/120 cold energy restorations internally checked bit-exact. Smoke used other seeds and passed 596 independent checks.

**Scientific faster-reasoning NO-GO:** exact-active is more accurate and faster; the energy policy missed its advantage over random, despite near-exact same-evidence posterior accuracy. World-bootstrap intervals (postscore descriptive only) for ID energy-minus-random accuracy were **[-2.62, +8.95] points** around +3.24; they are not predeclared significance criteria. Unknown operator classes beyond the supplied grammar, persistent native knowledge, unfamiliar natural environments, and matched compute are untested.

**Deployment NONE:** no merge, controller/scheduler/runner mutation, FORGE integration, native model promotion, original data consumption, new paid API or new GitHub PR. Native full final regression and independent science acceptance **UNVERIFIED**.

## Reproduction

The original evidence is in `scored.json` and `gru-checkpoint.pt`; their integrity is listed in `MANIFEST.json`. To reproduce without overwriting the original evidence, first extract the archive into a **new scratch copy**, then run:

```bash
python experiment.py --smoke --out new-smoke.json  # regenerates smoke checkpoint in scratch
python experiment.py --out new-scored.json          # regenerates scored checkpoint in scratch
python audit.py --file new-scored.json --out new-audit.json
```

Requires Python, NumPy and PyTorch; no network API. Predictions and count-based metrics are reproducible; CPU wall times and training floating-point numerics are environment-dependent. Independent audit of *original* evidence in a copied folder: `python audit.py --file scored.json --out second-audit.json`.

## Next scientific decision

Do not tune the scored top-K threshold or re-run the heldout worlds to turn a negative into a positive. If continuing, the next distinct test should study **representation learning for genuinely unseen causal operator forms**, or assess an **energy-based amortized value-of-information policy** against strong Bayesian action-selection over larger, partially identifiable causal systems. The existing 36-hypothesis discrete posterior is too small for classical energy approximation to offer an inference-cost advantage. Freeze new controls and holdout origins before a new scored experiment.