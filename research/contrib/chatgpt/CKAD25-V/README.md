# CKAD25-V — Persistent causal relations inside one native Yggdrasil learner

This is an **opt-in research candidate** for the existing tokenless `NativeCumulativeLearner`, not a separate learning architecture, accepted model, owner actor, controller, or unrestricted-world claim.

## What changed

The previous CKAD25-S/T/U and CKAD30–32 studies repeatedly found that source observations could be sufficient for an exact symbolic/Bayesian comparator while the native model abstained or made a brittle minimum-support repair. Continued tuning of action order or gates did not close the representation gap.

This gate changes the actual native research candidate: `compile_causal_relations(slot)` derives a **bounded, source-pinned set of binary causal weight vectors** from revealed do-action/outcome observations in the learner's own existing source ledger. It stores those vectors **in the same native cumulative checkpoint** (new opt-in v6 schema), and `causal_relation_probability(slot,context,action)` returns exact rational prediction counts. No text tokens or autoregressive language model are introduced, and the old numeric `predict()` remains unchanged.

The candidate is deliberately explicit about its limitation: it supplies a **conventional fixed GF(2) ANF grammar** of all ≤3-term expressions over sixteen monomials of three context bits plus one action bit. The maximum is 697 candidate weight vectors. This is learned posterior conditioning, NOT independent discovery of those primitives or novel general intelligence. When that grammar cannot explain observed consequences the committee is empty and the readout abstains at 0.5; a confident wrong answer is not excused.

The original 12-observation CKAD25 source-owned checkpoint is restored unchanged. Per seed the same cumulative learner learns six genuinely **new synthetic law formulas** in existing slots 1–6 (8+4 new public witnesses each), compiles each source to retained numeric hypotheses, cold-restores the entire learner, and scores 4 genuinely withheld action outcomes per law. This includes a deliberately **out-of-grammar** threshold rule to retain negative evidence. Three frozen split seeds: 41017, 42017 and 43017; 216 public source-free synthetic training observations and 72 new held outputs total. All source fixture labels and hidden outcomes are evaluator-only. Six fixed formulas and three permutations are not eighteen independent causal families.

## Strict matched controls and gates

The strongest independent baseline is a fully enumerated, equally informed 697-rule Bayesian posterior over the **exact same supplied grammar**. Per-held-case posterior probability parity is a mandatory exact numeric check; matching this baseline can show persistent native compilation works, but never superiority over its conventional source. Independently trained CART/RF/logistic, fitted frequency, uniform 0.5, and the original native degree and opt-in sparse readouts are separate controls with identical observed source.

The preregistered development signal requires source/cold continuation and old-property retention, mean Brier improvement ≥0.025 over original native degree, compiled Brier ≤0.23, ≤4 fully confident held errors, exact parity with conventional ANF Bayes at ≤1e-12 on **all 72 withheld probabilities**, and within 0.03 of the strongest non-symbolic trained baseline. Any failure remains a DEVELOPMENT_MIXED_NO_GO or INVALID, not post-hoc tuning. `SCIENTIFIC_PASS=false` regardless of engineering/development classification. No native promotion solely for a synthetic control parity.

## Identity and limits

- Accepted main unchanged: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Research parent qualified CKAD25-U PR #1247 head: `6e355e9470c8daaf918434d70e5256eb06903e7c`.
- Original source-owned CKAD25 checkpoint SHA256 `c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f`.
- Preregistration FIRST (before implementation/evaluation): `c3c5a051f4fb68ef1088d16e1770d0c42b806bf5`.
- New native committee module `56eb28c7e07cd5e4abd63b3833b86bcbe7ffda78`; cumulative integration `0eda1191f35937fe403b5f65c836697999358a9a`.
- Prospective executable source committed BEFORE scoring: `b60ea5b63bee23e562664ee875e382789e0bfe30`, Git blob `959b5dccb64408016277a9add461d91997fba25a`.
- The previously qualified CKAD25-S helper `run.py` stays Git blob `31e06746dd2fa83cf4bfedf28da43cacbc68c99f`, imported for **controls only**. No prior CKAD25-S/T/U held outcomes are reused as new scientific labels.

### Source-grounded authenticity and isolation

All new experiments use public synthetic procedural outcomes and the repository's explicit **`engineering_fixture_only`** source mode. The original trusted source owner, protected CausalGym environments, accepted main/weights, FORGE, scheduled tasks, deployment and autonomous research controller are **not** accessed or modified. The proposed new v6 checkpoint is experimental; prior v1–v5 checkpoint bytes must restore unchanged. No merge or model promotion is authorized, even if the development signal passes. Original-first-use scientific qualification requires its own authorized source owner, virgin held-out transfer family and independent matched controls.

### Reproduction

```bash
python -B -m unittest discover -s tests -p 'test_native_causal_relation_posterior.py' -v
python -B research/contrib/chatgpt/CKAD25-V/run.py --output /tmp/ckad25v.json
```

CI runs the one frozen synthetic cohort on two GitHub-hosted operating systems, verifies source Git blobs and exact-result cross-platform identity, and audits the retained native checkpoint without reclassifying negative results. Full final Linux/Windows inherited regression and G29 remain independently required.
