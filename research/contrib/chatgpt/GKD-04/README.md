# GKD-04 — generic structured GPT donor → type-checked numeric program

**Research contributor only.** The user's goal is to determine whether GPT can serve as a useful donor for a separate tokenless native Yggdrasil learner. This pilot improves the **source interface**, not Yggdrasil's accepted model, and not independent causal intelligence.

## Immutable chronology

1. Existing qualified GKD-01/02/03 source parent: `f6adb8eec0c78ad3e51b438aad4c035399359d4d`, [final dual-platform CI #44820553865](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44820553865).
2. **Preregistration FIRST:** `71a85055096d7d4fa4c92e0ae2afb3522b519848` — question, four domains, frozen 1024 synthetic test cases, controls, success/failure conditions, no first-use. Precedes any new source or test.
3. **Assistant-generated structured donor, frozen before testing:** `d20e77fcec0b64fa9f1e093d127881bdb8eb08e5`, [donor.json](donor.json). These statements were **generated using GPT inference**, with manually provided numerical expression trees, input ranges and SI dimensions; no teacher model inference occurs after this frozen source is prepared.
4. Generic compiler is [run.mjs](run.mjs). No per-claim opcodes or model-specific operators are hard-coded. The *separate independent symbolic evaluator* explicitly implements each well-known ideal equation to test correctness; this is a strong same-information control, not proof of knowledge discovery.

## Engineering boundary

Donor supplies a JSON arithmetic expression tree with `input`, `const`, or binary `add/sub/mul/div`, plus each input's five SI base-unit exponents, lower/upper valid domain, and target result dimensions. A single compiler checks grammar, depth, register limit, array shape, formula units and arithmetic dimensions. It emits small tokenless numerical bytecode, input domain limits, a SHA256 of the source claim and a separate SHA256 integrity footer. Recipient computation uses only numbers, ranges and arithmetic instructions. Bytecode has **no text tokens**, no gradient training and no runtime language-model inference.

**This is not automatic English-to-weights compilation.** The AST and units were already supplied by the assistant; conventional compilers can process them. The source-hash footer only detects accidental changes; there is **no independent source issuer authentication** or physical-world truth validation.

## Frozen tests and strongest controls

Four ideal physics law families; 256 fixed-seed synthetic numerical cases per rule (1024 total), with comparison to separately hand-written textbook exact symbolic computations. Exact same knowledge/control scores should tie. Cold decode checks are 3/rule (12 total). A physically wrong spring formula `force=2*k*x` has the **same units** as the correct donor claim and MUST pass the type checker; independent ideal-law numerical evidence must reject all 256 predictions. This negative is central: **unit consistency is NOT factual truth, causal grounding or knowledge admission**.

Source-free negative tests cover malformed input, missing source field, unsupported operations, invalid dimensions, deep graphs, nonfinite constants, bad domain bounds, tampered and re-signed invalid programs, out-of-bounds runtime evidence and division by zero.

Run from any directory with Node 22: `node research/contrib/chatgpt/GKD-04/run.mjs`. In the existing PR's dual-OS G29 workflow it is tested on GitHub-hosted Ubuntu and Windows alongside the **entire original 54-test Python regression** and inherited GKD-01 through GKD-03 studies.

## What this DOES NOT show

- No GPT weight access, zero-inference teacher distillation, automatic natural-language interpretation or live GPT model API.
- No independently verified physics experiment, novel causal-law discovery, unknown-world transfer, action-consequence learning, functional long-term retention, or trained neural superiority.
- No claim of savings compared with a general-purpose symbolic interpreter at equal information. Four already known ideal laws can be represented exactly by ordinary algebra and are therefore expected to **tie**.
- No protected Yggdrasil #426 original-world first use, native cumulative learner integration, acceptance, merge, deployment or controller/runner authority.

**If engineering passes, the next eligible scientific question** is whether a source-admitted, independently observed real intervention can verify/refute GPT's suggested constraints and improve an unfamiliar task **beyond equally informed robust symbolic and conventionally trained controls**. Existing WSP physical-chamber studies have already tested several real intervention predictors and produced strong negative results; do not replay their consumed cohorts as new science.
