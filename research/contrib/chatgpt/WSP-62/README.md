# WSP-62 — Adaptive numerical causal representations with no training resets

## Source custody and hypothesis
- Frozen before creating WSP62 source, learner, or results: `09a8b8e10bed6c21b85180cb4b0d15ffb719c619` (`prereg.json`).
- Parent [WSP61 draft PR #952](https://github.com/spoonman136668-ai/Yggdrasil/pull/952), source `58f323dd65b9bd02854f5a8fd16b1cf0c4fb0c9b`. WSP61's **210/384 (54.6875%)** versus 91/384, zero confidently wrong, criterion-missed result is preserved unchanged.
- WSP61's largest issue was a fixed <=3-causal-parent representation: triple-XOR worlds require four-variable next-state expressions. This successor tests representation change against **exactly the same sequential training action history**, not just changes in exploration.

## Three unseen simulated rule families
- Four new seeds each of conditional chain, triple XOR, and **XOR with binary conjunction interaction** (`2801..2812`), 4 shuffled sensor-role channels, four binary sensors, 80 sequential charged actions from the only initial zero state. The mixed interaction family is evaluator-generated only.
- `source.py` holds private dynamics and oracle-selected 2–6-step goal tasks. Neither numerical learner imports the evaluator or reads hidden action maps, task shortest paths, or uncharged consequences.
- Actions are selected by the **frozen WSP61 original active policy**, and every charged transition is fed to both the original WSP61 <=3-parent learner and the WSP62 expanded learner. A separate random-trajectory arm receives its own 80 sequential actions with the **same WSP62 model**.
- The model infers Boolean **algebraic normal form** (GF(2) numerical coefficients) directly from action consequences. Its degree-one representation is contradicted by quadratic observations in the mixed worlds; the mechanism then recognizes an expansion to degree two. Public predictions are conservatively guarded by every degree-two solution consistent with evidence, including before a contradiction is first observed.
- This **degree <=2 ANF prior matches all source mechanics by construction** and is therefore a designed inductive bias, not learned general-purpose representation grammar. Unknown coefficient combinations produce abstentions, never arbitrary imputation.

## Frozen qualification
- **384** held-out tasks (12 worlds ×32), every one with an evaluator-proven shortest path of 2–6 actions, scored under original source physics from an otherwise withheld test start.
- **768** state-action transitions audited after training, including specifically those state-action pairs *never observed* during training; exact observation lookup cannot predict the latter.
- Success requires (A) expanded learner >=300/384 goals, (B) >=50 more goals than fixed WSP61 under **identical active evidence**, (C) >=25 correct confident predictions on **previously unobserved** state/action pairs, (D) zero confidently wrong transitions, (E) >=4 observed linear-model contradiction-triggered expansions across mixed worlds, and (F) all cold restores/80-action continuous ledgers valid.
- Separate diagnostic controls: fixed-degree-one GF(2), original WSP61 <=3-parent learner, exact state/action memory lookup, and equal-action random trajectory with the same expanded learner.
- Seed/world/task/charge SHA256 receipts, per-action rank/witnesses, explicit identifiable coefficient dimensions, memory bits including raw evidence, end-to-end wall/CPU and policy time are recorded in test output.

## What this cannot demonstrate
Even if the frozen SELFTEST criterion passes, this is only **a source-family-aligned finite Boolean rule-learning result**, not unrestricted invention of a new representational language, natural language learning, a conventional neural network's dense-weight training replacement, open-world intelligence, or superiority against fully trained strong conventional neural and independent symbolic compute-matched baselines. The test is not a scientific first-use, independent acceptance, deployment, or merge.

## Reproduction
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-62 -p 'test_*.py' -v
```

The focused Ubuntu and Windows CI, generated-only source-pinned G29 atlas and complete inherited final regression are distinct qualifications. No DEV/PRIMARY first-use, scheduled task, paid API, new controller, runner changes, merge, promotion, official loop integration or deployment.
