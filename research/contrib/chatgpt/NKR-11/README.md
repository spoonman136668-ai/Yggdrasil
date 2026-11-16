# NKR-11 — Contradiction-triggered native action/context relation repair

## Why this experiment

NKR-10 [draft PR #1141](https://github.com/spoonman136668-ai/Yggdrasil/pull/1141) qualified a complete **21,343,681-record historical TRAIN** fact-store bridge but failed its preregistered real historical reconstruction requirement: **106/1,270** (8.35%) source-mask recall@4 vs **33/1,270** (2.60%) frequency baseline, and tied an exact equally informed symbolic control. This result is immutable/NO-GO for scientific promotion. Repeating variations on the same consumed masked source will not prove actual causal learning.

NKR-11 tests a **different thing**: can Yggdrasil's isolated non-transformer, non-token, numerical native research substrate recognize that a previously learned action mechanism no longer explains public consequences, learn a previously unseen context-conditioned intervention relation from *actual selected actions in a deterministic computational environment*, and preserve its old knowledge across cold restoration?

**This is a self-generated, synthetic development environment. It is NOT externally authentic public causal data, a new scientific test set, or permission to mutate accepted DG1 or original NKR03 causal cells.**

## Frozen source and cohort

- **Prereg FIRST SHA** `4838b45371cc9b59ae53235e4cfdc044f3074498` — frozen before implementation/data outcomes.
- Parent exact [NKR-10 draft](https://github.com/spoonman136668-ai/Yggdrasil/pull/1141) `c420bd7ecd5655bc529ec1d781e458b62ce4a768`, tree `a19e10ca0436e7fc8e422cd118f3f7271097758a`. Accepted main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` unchanged.
- **12 deterministic worlds**, 4-bit contexts, 2 real selected intervention actions, binary public outcomes. The computational simulator is in `research/contrib/chatgpt/NKR-11/experiment.py` and is never imported by the learner module.
- Old mechanism `outcome=parity(context & (1 << (world mod 4))) XOR action`. **32** previously revealed outcomes (16 contexts × two actions) fix the prior knowledge checkpoint per world.
- New mechanism `outcome=parity(context & new_base_mask) XOR (action AND parity(context & new_action_interaction_mask))`. Its intervention effect changes with *two or more* context bits; this is **outside the old unary-only operator catalog**, though it stays inside a PRESELECTED 10-feature parity hypothesis family. New masked relationships are not free-form intelligence/operator invention.
- A real public intervention at `context=0, action=1` always returns 0 after the shift, contradicting the old model's predicted 1. This is due to the frozen world construction, not a learner looking at a hidden phase label. **No world mechanism/shifting flag** is supplied to the learner.
- Freeze eight training contexts `[0,1,2,4,8,3,5,10]`. Act on **both** arms once at each: 16 observed consequences per world, with the contradiction first. Freeze the other eight `[6,7,9,11,12,13,14,15]` for cold evaluation, both actions, **16 cold probes per world** or **192** total. Learner never consumes their labels.
- Retest old mechanism after repair on all 16 contexts × both actions per world, **384** cold retention probes; the original old checkpoint must be byte-identical.

## Mechanism, controls and budget

`yggdrasil/native_intervention_repair.py` introduces a separate opt-in **integer-exact GF(2) causal signature**, with 10 binary coefficients: intercept, four context main effects, global action effect and four action–context interaction effects. Warmup outcome records and new intervention outcome records have canonical SHA-pinned bundles and source IDs; the checkpoint is read-only until the first publicly observed **contradiction** gates a separate new immutable repair state. If no contradiction is observed, do not activate a new model. Without enough evidence to identify an action consequence, return **UNKNOWN_ABSTAIN**, not an invented counterfactual.

No outcome values are predicted from hidden simulator masks; only `observed_intervention` fixture source rows with refs and exact SHA may update the research state. SHA checks are a **byte-integrity mechanism, NOT real-world authenticity**. Any original DG1/NKR03 causal owner state, NKR08 factual knowledge/21M historical source, and legacy YPC1 checkpoint remain unchanged. This test does not need to reread or rebuild the full historical image: NKR09 and NKR10 already established its typed read-only compatibility, while this cohort evaluates distinct causal-action observations rather than historical Q/P/Q triples.

Strong controls all get the same *16 observed outcome budget* and target training contexts:
- **Fully fitted independent exact symbolic**: exhaustive enumeration of every 1,024 possible 10-coefficient signatures from **exactly the same 16 selected action outcomes** as native. A TIE is expected.
- **Explicit phase-change reset**: instantly replaces the old model with an identical fully trained signature given exactly those 16 outcomes. It is a stronger known-boundary control and expected to TIE.
- **Passive confounded observation**: same 16 outcomes (two repeats per training context) but each action is chosen by `action=context.bit0`; never observe the opposite intervention. Unknown predictions must abstain.
- **Unconstrained fixed-seed action sampler**: same 16 outcomes and contexts with a reproducible binary arm selection for each observation, but no guarantee of both arms.
- **Frozen old model**: zero new observations, an explicit static negative control.

Metrics: total *correctly identified* cold action outcomes out of 192 (abstention counts incorrect), non-abstention coverage, old retention out of 384, mechanism-change detections out of 12, full 16-outcome budgets, source-hash/identity, checkpoint sizes, exact symbolic parity and wall time. No network, paid LLM API or new controller.

**Preset development threshold:** native >=173/192 cold correct, at least +38/192 absolute correct over passive, 384/384 original retention, 12/12 contradiction detections and same predictions as the independent fully fitted symbolic baseline. Preserve all nulls/negative deviations; do not tune worlds/splits/thresholds after results. **SCIENTIFIC_PASS remains false** even when this criterion is satisfied because a deterministic self-generated environment cannot certify real-world causal discovery, and the exact strong conventional theory may tie. Subsequent actual unfamiliar-domain trials need separately frozen owner-authorized source/first-use and fair conventional trained controls.

## Source-safe qualification and isolation

The new tests `tests/test_native_intervention_repair.py` protect integrity/persistent cold replay, case-specific unknown abstention, wrong source kind, malformed public action, source-ID rebound/replay, SHA tamper, duplicate evidence and contradiction-gated repairs. All other qualified research code remains on the same stacked draft branch, unmerged.

Development uses GitHub-hosted Ubuntu and Windows, **full root regression** and independent **G29 atlas** source pinning on the exact candidate tree. Do not rerun any 256MB original fact artifact, owner-accepted model, real original scientific test, extra runner, private local execution, scheduled loop, new controller or paid API. The source-safe deterministic outcome receipt is printed by the experiment and retained within the PR's CI logs. No duplicate result files in a Library or unapproved release.

### Reproduce the source-free experiment

```bash
python -B -m unittest discover -s tests -p test_native_intervention_repair.py -v
python -B research/contrib/chatgpt/NKR-11/experiment.py
python -B -m unittest discover -s research/contrib/chatgpt/NKR-05 -p 'test_*.py' -v
python -B -m unittest discover -s tests -p 'test_*.py' -v
python -B scripts/build_code_atlas.py --check-if-present
```

**Engineering PASS != SCIENTIFIC PASS != DEPLOYMENT.** A successful experiment earns no automatic integration, promotion, source-first-use or mutation of accepted Yggdrasil `main`. The standing owner-activation blocker remains verified permanent destination and owner authority.
