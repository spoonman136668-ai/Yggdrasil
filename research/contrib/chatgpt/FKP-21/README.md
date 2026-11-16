# FKP-21 — Can a tokenless learner invent a genuinely new causal rule without enough feedback?

**ISOLATED RESEARCH ONLY. No protected scientific first-use, no native Yggdrasil integration, no accepted-main change.**

## Why this gate exists

FKP-20 [draft PR #1116](https://github.com/spoonman136668-ai/Yggdrasil/pull/1116) learned which two older actions jointly caused delayed physical outcomes and earned perfect known-family rewards. But independent exact symbolic and fully trained logistic controls also earned perfect returns. Its three possible two-parent XOR relationships were *preprovided*. This does not prove the model invents operators outside its grammar.

FKP-21 isolates a harder and more fundamental distinction: **constructing a composite rule from physical observations** versus **identifying a completely unobserved rule extension that the same evidence cannot distinguish**. It does not copy or modify WSP120's [draft PR #1113](https://github.com/spoonman136668-ai/Yggdrasil/pull/1113) graph programs. Its raw data are binary public action effects, not graph-derived associations.

## Frozen before implementation

- Preregistration **FIRST and sole original commit** `ef9ee3fa690a77250829424070ec4a8fc87b2197`, parent exact qualified FKP20 candidate `a3f560435f8d23043b81438ec0e5d6b149ff0bec`. The prior FKP-20 experiment is frozen and unchanged.
- Exactly **16 inspectable synthetic TRAIN worlds** `993100..993115`, in **8 matched low-complexity/adversarial pairs**. Protected FKP21 DEV `993500..993531` and TRANSFER `993600..993663`, and all predecessor protected/consumed cohorts, are inaccessible.
- Each world has an unknown-to-policy four-bit input of **public context + three physically selected earlier actions**. A fourth distractor action must be applied before terminal ±1 feedback. The frozen training input set contains **12 patterns: 3,4,5,6,8,9,10,11,12,13,14,15**. The **four unobserved first-probe patterns** are **0,1,2,7**. Predict first, physically apply the four action steps, then receive only the actually earned reward.
- The fixed 12×11 matrix of constant, four unary and six pairwise Boolean monomials has full rank **11 over GF(2)**. Low-complexity worlds use **eight frozen degree≤2 coefficient masks**. Each adversarial partner returns **identical physical responses to all 12 training actions**, yet *flips exactly one* of the four previously unseen effects. That makes the two corresponding laws observationally identical at training time, no matter how powerful the model.
- The learner may use only source-public observations, not seed identity, source coefficient masks, source-private hidden functions or counterfactual future feedback. The source is *reviewer-inspectable*, not an external hidden evaluator, so this is development-only work.

## Architecture and fair comparators

`rule_learning.py` implements a compact incremental **GF(2) elimination** over the physically observed feature/outcome equations. It constructs a composite algebraic normal form by allocating numeric coefficients, not by selecting a named operator from a library of XOR/AND/OR relations. Its degree≤2 monomial basis **is still an explicit inductive bias**; this is *not* unrestricted spontaneous invention of arbitrary logic.

The independent strongest control enumerates all **2,048 possible degree≤2 coefficient vectors**, fits the same 12 source-public actions, and must agree with the candidate when the evidence is identifiable. A direct **public exact-lookup** baseline abstains on previously unseen inputs rather than guessing; a **NO_UPDATE** baseline ignores action rewards; **SHUFFLED_OBSERVATION_TO_INPUT** deliberately attaches feedback to incorrect public inputs. These arms see exactly the same actions and observations.

After each initial prediction and physical held probe, a small explicit feedback cache records the newly witnessed effect. A SHA-covered, canonical JSON cold checkpoint must restore that evidence exactly. A later repeat lookup on an already witnessed input is **retention/repair from actual feedback**, not transfer to another unobserved relationship. The exact lookup and independent symbolic control can also retain direct feedback, so do not claim uniqueness.

`run_public_feedback.py` compares **16 worlds ×5 independent arms ×(12 train +4 first physical probes)×4 actual actions = 5,120 source actions**. It separately reports correct predictions, wrong predictions, honest abstentions, paired world-law observational identity, direct feedback-cold recall, fit/scoring wall time, bounded learned bytes and 10,000 *paired-world* resamples (seed 2121). It must report the expected **32/32 low-degree first-probe correctness** and **24/32 adversarial first-probe correctness** for each fully fitted GF2 learner (56/64 overall). The **eight unavoidable paired contradictions** are not a model-training failure; they prove a fundamental identifiability boundary under insufficient feedback.

## Engineering, science and authority

Engineering requires original prereg blob and source SHA pinned, source independence and negative tests, generated-G29-only child, and full mandatory root regression on **Ubuntu 24.04 and Windows 2022**. It may be run on the already-existing isolated source-safe GitHub-hosted CI helper; no additional workflow file, scheduler, owner, controller or paid API is authorized.

The source’s first-probe worlds are still known **TRAIN**, and some public TRAIN observations are exercised in unit tests. There is **no independent unfamiliar operator first-use**, native admission, zero-shot arbitrary operator discovery, transfer, proven non-gradient intelligence advantage or model RSI. If this exact-source comparison succeeds, its correct interpretation is **bounded compositional rule learning plus a proven need for additional consequential feedback**. If it fails, retain the measured negative and stop; do not tune the frozen source or model after primary data.

All FKP17/FKP18/FKP19/FKP20 drafts remain unmerged. Accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` was the verified baseline at preregistration; no accepted native Yggdrasil code is modified.
