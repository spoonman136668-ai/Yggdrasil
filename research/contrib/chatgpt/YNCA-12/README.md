# YNCA-12 — unlabeled causal-context memory and open-world failure

**Final disposition: ENGINEERING source custody verified; DEVELOPMENT_NO_GO (two bounded passes consumed); SCIENTIFIC_PASS=false; NATIVE YGGDRASIL TRAINING=none; DEPLOYMENT=none.** Draft research only, no merge. This is not a new controller or an implementation of CKAD's integrated learner.

## Provenance

- Accepted `main` baseline: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, untouched.
- Predecessor: [YNCA-11 PR #1236](https://github.com/spoonman136668-ai/Yggdrasil/pull/1236), including its failed evidence gate; no consumed predecessor B worlds were reused.
- Original development prereg Git commit: `f59e67a327e64c4be8e86464a3be7e0b33541c0b`.
- A exact executed source Git blob: `f861ea09eb19bb8986491ce4f1ac89ceb234359d` (SHA256 `aa43ffe20dfa994a8a9bde98f4a66ab903ecd22a380517d5b5fe73f3d458c089`); checked against GitHub object at commit `acce69c21e801c379e0d4ebd88f1cd48854b4fff`.
- A local exploratory result Git blob: `330d6b79e3c98431844e7a120dfe7cf3675810f0`, SHA256 `355b13dbf38b6908c3696dce4e9864dbfd72770112c40a3ab516f4c14ff18d5e`; committed `14f9ecc5d5091fae6ff3de8f3c0d33c3beec2924`.
- Correction frozen BEFORE B score at prereg commit `9d1c4be1417450d1fed18306095803f3feb14747`.
- Corrected B exact executed source Git blob `f6cc0cef6c0a7ddb9ad53bcf7580579e2fb0a861` (SHA256 `7ea099aece2765e14f497b1376eadc34d9682b8d9efc16a9bee15ee320a3124a`), confirmed against GitHub source commit `a60ac10456ad4b561628b8b7457559e4f44f4b6d` BEFORE scoring.
- One disjoint B local development score SHA256 `343eb204144de419d81a8ca6c4abd97e67cee95bccc50da1f3e28e98957fa9aa`; Git blob `8a44869c0aae19806784e62dfd624453774786c9`, committed `1514ae29ed648dc8b9690e619f5558d1f8814d9e`.
- Main, any original-world first-use, qualified native learning state and FORGE system remain unchanged. Results are source-free synthetic local runs, NOT independent two-OS qualification or native model learning.

## Mechanism, budget and strongest controls

Unlabeled training streams contain 32 independently permuted/noisy worlds, arranged internally as 8A 8B 8A 8B but the fitted memory sees only actions and their outcomes, NOT A/B labels, operator IDs or permutations. Two causal operators come from YNCA-11's fixed 24-table grammar; an unordered 300-pair exact Bayesian posterior integrates unknown per-world roles and contexts. The candidate retains the six highest-weight pairs, with normalized probabilities. Both A and B expose 128 training intervention/outcome pairs, and test 64 fresh familiar plus 64 unseen-third-operator worlds with two revealed actions per world, scoring 384 held truth assignments per family. The test worlds never train the model.

Controls include fully fitted single-operator Bayes, fully trained action-frequency, no memory, last-world overwrite, and the **full 300-pair exact Bayes** given exactly the same evidence. There is no new operator grammar, autonomous hypothesis creation or language training.

## Pass A (exploratory, seed 171200)

| Arm | Familiar Brier lower better | Third-operator novel Brier |
|---|---:|---:|
| TOP6_PAIR | **0.167213268** | **0.420822797** |
| FULL_PAIR_BAYES | 0.167213255 | 0.420822709 |
| Fully trained frequency | 0.195660835 | 0.317776516 |
| Fully fitted single-operator Bayes | 0.228451578 | 0.462660766 |
| NO_MEMORY | 0.284151758 | **0.227565884** |

Five of six preregistered gates passed. **Novelty rejection failed:** the pair grammar falsely insists the third operator must be one of the two learned operators. Six-pair memory reproduced full-pair exact Bayes in-family to 1.3e-8 Brier, but both also failed outside the learned pair. The measured compact state was 198 serialized bytes; this is **not** a full-process or physical efficiency superiority claim.

## Pass B (one prespecified correction, disjoint seed 181200)

One Bayesian novelty/evidence gate combines the retained pair posterior and a broad uniform 24-operator no-memory predictive. Its trust weight is the likelihood under the old pair divided by old-pair plus broad likelihood, both computed using the same **two observed actions**. The full-pair comparator receives exactly the same gate. The evaluator never gives the learner novelty labels.

| Arm | Familiar Brier | Third-operator Brier | Combined Brier |
|---|---:|---:|---:|
| GATED_TOP6_PAIR | 0.194813710 | 0.254861899 | **0.224837805** |
| GATED_FULL_PAIR_BAYES | 0.194850088 | 0.254828567 | 0.224839328 |
| UNGATED_TOP6 | **0.163440794** | 0.373145634 | 0.268293214 |
| Fully fitted single-operator Bayes | 0.188667410 | 0.379149798 | 0.283908604 |
| Fully trained frequency | 0.218696592 | 0.271653938 | 0.245175265 |
| NO_MEMORY | 0.256274722 | **0.231209724** | 0.243742223 |

The correction reduces out-of-family damage compared with the ungated candidate but **still harms unfamiliar worlds relative to no memory** by 0.023652175 absolute Brier, exceeding the frozen 0.02 maximum. It also sacrifices familiar-world accuracy/calibration: familiar Brier increases versus ungated, and misses its required +0.02 gain over the strongest nonpair control; combined-gain gate fails too. **Only 3/6 Pass B gates pass**; DEVELOPMENT_NO_GO. No further source tuning on evaluated A or B.

## Local reproducibility, not a new independent score

```bash
python -B research/contrib/chatgpt/YNCA-12/experiment.py --split A
python -B research/contrib/chatgpt/YNCA-12/experiment_B.py --split B
```

The above replays already-consumed development worlds; it **does not** create a new independent result. Single-host wall/runtime of the scored Python functions was approximately 0.72s for A and 0.85s for B, excluding interpreter/setup/authoring/repository CI. Whole-process memory, hardware energy, and 2x efficiency are unverified. No independent Linux/Windows regression or native-owner qualification is asserted.

## What this closes and what remains

The supplied-label bottleneck of YNCA-11 is partially narrowed: a six-pair state can infer two hidden contexts from unlabeled causal observations and predict new *familiar-family* worlds approximately as well as the full 300-pair Bayesian control. But **the causal grammar is closed and assumed**, and it fails on a third operator. Calibrating a mixture of known/unknown operators under only two observed actions did not close the failure without harming familiar performance. There is no discovery of truly unenumerated causal primitives, no cumulative native integration, no scientific superiority, and no autonomous training.

**Next distinct hypothesis, not a retry:** let a native learner recognize an inadequate causal explanation and propose a genuinely new operator family from additional discriminating interventions, with strict budget matching and a fully trained/exact generative control. Freeze new cohort, sources, gates and stop criteria before any such test. Preserve all YNCA-12 negatives.
