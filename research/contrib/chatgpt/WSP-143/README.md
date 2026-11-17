# WSP-143 — tokenless hierarchical causal-concept modeling (exploratory)

**Status at source implementation:** Only pre-source hypothesis frozen. New public effects UNCONSUMED. Do not claim SCIENTIFIC_PASS or native Yggdrasil implementation.

## What this tests

Borrow the *coarse-to-fine latent refinement principle* of [Next-Concept Modeling (NCM), Kumbong et al., 2026](https://arxiv.org/abs/2610.14162), but **NOT** its residual VQ-VAE, codebook tokenization, transformer, text decoding or language generation. Yggdrasil remains an independent **tokenless, non-transformer** architecture.

This isolated prototype models six binary state variables and predicts observable action consequences. Rather than choosing among pre-enumerated finished causal laws, it forms a bounded lattice of **causal concepts**:

1. Raw binary factors and pairwise conjunctions: fit coarse, sparse XOR rules of up to four distinct terms from 32 witnessed public action effects.
2. If no consistent coarse representation explains those effects, generate candidate 3-way conjunctions from smaller components and refit.
3. If still insufficient, expand sequentially to 4-way and then 5-way conjunctions. Prefer smallest possible depth, fewest active terms, and lowest summed degree.
4. Preserve **all** equal-rank candidate causal rules and answer on a withheld state only when every retained candidate agrees. If >10,000 minimum-rank rules exist, conservatively abstain (no truncated topK fabricated confidence).

This learns a choice of source-blind programs/weights from consequences. The generic **AND/XOR primitives and at most four terms are already supplied**: it cannot claim to invent Boolean logic, learn unrestricted higher-order mechanisms, or reproduce NCM's token-model results.

## Existing failures and controls

The fully qualified predecessor [WSP142 #1188](https://github.com/spoonman136668-ai/Yggdrasil/pull/1188) is a permanent **NO-GO** on previous seed families: odd-numbered three-way worlds genuinely require 4 ANF terms but its direct-weight learner permits at most 3. It also makes confidently wrong five-variable predictions. This new test must use **entirely new sources** and cannot retrospectively increase WSP142's term cap or change its scores.

The identical 32 actually observed effects per world are passed to:

- This hierarchical learner (levelwise composed feature lattice, 4-term XOR weights, abstain on ambiguity).
- An **independently implemented FLAT exact same-prior symbolic solver** with full ≤5-degree conjunction basis, same 4-term and tie constraints. An exact tie means no demonstrated unique hierarchy/direct-numeric advantage.
- The **unchanged** WSP142 3-term binary direct-weight implementation, **unchanged** WSP135 source-blind latent fitter, and **fully fitted** WSP135 conventional CART on the same source data; plus no-update and a degree≤2 coarse ablation.

## Prospectively frozen evidence

New public synthetic seed families, from separate `WSP143|SOURCE|...` SHA256 namespace: known 250000..250007 (8); three-way 251000..251015 (16); five-way 252000..252015 (16); cross composition 253000..253007 (8); structureless OFF negative 254000..254007 (8); zero-action re-ID of four known laws 255000..255003 (4). **1,792** total public synthetic interventions, **ZERO** original protected CausalGym/DTR/MDP first-use effects. Original seed namespaces and all historic scored sources remain untouched.

The original fixed WSP135 32-action schedule is unchanged. For each world all models produce **64 predictions before any withheld scoring**. The evaluator alone privately chooses 16 questions from 32 never queried via `SHA256(WSP143|FUTURE|seed|x)` and scores with source-owned outcomes; full 32 unseen scored separately. No learner sees hidden source law, true family, seed, held truth, or source-private graph.

The preregistered development SUPPORT gate requires +10pp correct gain vs strongest of WSP142/WSP135/fully fitted CART in EACH three-way, five-way and cross family, ≤1% confident error in each, coverage ≥85%/65%/75%, known degradation ≤5pp, OFF confident wrong ≤2%, exact flat symbolic parity, all earlier known outputs stable, exact 256/256 old-law zero-action relabel readouts. Else preserve **DEVELOPMENT_HIERARCHICAL_COMPOSITION_NO_GO**. Fourteen or more small tasks in one family do **not** provide that many independent causal environments beyond the independent source worlds. Original 100k factual associations do not by themselves validate causal intervention learning.

The whole trial captures CPU/wall/tracemalloc and per-arm fit CPU. It does **not** measure matched GPU/RSS/energy or original-source realism and does not independently establish learning superiority if the flat exact solver ties.

## Exact source custody / engineering qualification

Original prereg ONLY at `be5a193c5345704b0bf34570d7b8e79fba023c6a` on qualified WSP142 exact `7908d0cf18fa46c17aafa24d49c7480c21d8f814`, tree `d661bc5e7ae2842ccd0b164445fc8e0fd24e4089`. Accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` unchanged.

Execute source-safe Linux/Windows tests and archive the **immutable original results** before generated-only G29 source pin, exact-candidate full inherited/standard root regression Linux+Windows and independent G29 acceptance. Do not touch old WSP results, protected benchmarks, native weights, merge target, controller, private runner or scheduling. This is development architecture research only.
