# CKAD-01 — wide-first, knowledge-before-discovery development report

**Date:** 2026-11-16
**Classification:** Isolated synthetic exploratory development only. **Not** Yggdrasil native training or external scientific first-use.

## Plain-English verdict

Knowing more validated *synthetic* entity properties allowed a bounded rule learner to make many more safe predictions for previously unseen entities, without being given their outcome labels. At full 100,000-property exposure, it identified both two-property effect laws on all heldout entities. It was unable to learn a three-property majority relation outside its allowed pairwise grammar, while a conventional trained decision tree learned it. An independently implemented exhaustive symbolic rule learner made exactly the same predictions as the bounded learner. The result therefore establishes an information-exposure and representation-capacity boundary, **not a native intelligence breakthrough**.

## Grounded source and training qualification

- 10,000 simulated entities × 10 simulator-verified binary properties = **100,000 public factual relationships per seed**. The source is deterministic *synthetic simulation*, not real-world factual or causal grounding.
- Three independent development seeds: `101`, `202`, `303`; four nested knowledge exposures: 10,000 / 25,000 / 50,000 / 100,000 relationships.
- Same **512 selected public action consequences per mechanism per seed** at every knowledge exposure; action=1 effects observed on unique training entities.
- Heldout entity IDs 6,144–8,191; 2,048 never-outcome-trained entities per seed per mechanism, 6,144 cold questions per relationship family aggregated.
- Three causal mechanism families: A two-bit XOR, B two-bit conditional AND-NOT, C three-bit majority (outside the fitted two-property rule grammar).
- Comparison arms: isolated rule generator, separately written complete symbolic fitting control, fully trained depth-4 CART, and retrieval-only (which cannot answer any heldout entity).
- Rules were formed from observed public properties and selected action outcomes; no hidden mechanism class or evaluator action outcome passed into fitting.
- Learning interface was a separate standalone Python prototype, not accepted Yggdrasil `main`, Wingless, TTT-Hybrid, or any original model checkpoint.

## Measured heldout results

Correct answers out of **6,144** previously untrained entity consequences per family (three seeds combined):

| Exposed properties | Two-property XOR | Conditional AND-NOT | Three-property majority |
|---:|---:|---:|---:|
| 10,000 | 0 | 0 | 0 |
| 25,000 | 0 | 0 | 0 |
| 50,000 | 1,506 | 1,498 | 0 |
| 100,000 | 6,144 | 6,144 | 0 |

- All supported native-style predictions were **correct** in this generated source, with zero confidently incorrect predictions; unsupported queries were explicitly rejected.
- At full exposure, the depth-4 CART conventional control scored **5,900/6,144** on A, **6,144/6,144** on B and **6,144/6,144** on C.
- The independently fitted exact symbolic control **tied** every bounded learner prediction in every arm. This rules out a demonstrated learning advantage over the strongest equally informed control.
- The three-property family C yielded **0/6,144** predicted by the bounded pairwise learner even with all 100,000 facts, versus **6,144/6,144** correct from CART. This is the decisive representation-capacity failure.
- The jump from 50k to 100k reflects newly available feature evidence/coverage and a fixed minimum-support threshold. It does **not** establish continuous emergent understanding or generalized human-like causal reasoning.

## Verification and negative controls

- 36 frozen seed × exposure × mechanism arms executed.
- Fresh independent Python process reproduced exactly the full semantic result (timing excluded).
- 9/9 shuffled-feedback negative cases and 9/9 zero-feedback negative cases produced **no supported new rule**.
- Public synthetic source was fully regenerated and hashed per seed; exactly 100,000 facts were present at maximum exposure.
- Entity ID splits were disjoint; unobserved entity consequences did not enter rule fitting.
- All 36 learned predictions matched the independently implemented symbolic control.
- Initial facts were not overwritten by later rule fitting. Earlier rule outputs could be recalculated identically in-process; **real cold-process native-model retention is NOT demonstrated**.

## Reproducible identities

- Preregistration file SHA-256: `3455cac180efcd33aa9f3e56925b041bc67bfbb8c48c318e4a1ea844b4fafca4`
- Experiment source SHA-256: `768922dc0500e94454cc4d6cb16b5556978551214acd3186b47fb326a3f9441d`
- Source-independent semantic result SHA-256: `03ae99affdc6167a89992d29da4b0f197e642c120b5845c9632cb6b092165d4f`
- Environment: {"numpy": "2.3.5", "platform": "Linux 6.18.57", "python": "3.13.5", "scikit_learn": "1.8.0"}
- Qualification time: 2.320 s; original experiment runtime from receipt: 0.711 s.

## ENGINEERING / SCIENTIFIC / DEPLOYMENT

**ENGINEERING — PASS (local exploratory only):** generator correctness, 100k knowledge scale, strong symbolic parity, negative controls, fresh-process result reproducibility and explicit unknown abstention. **NOT QUALIFIED:** Yggdrasil repository regression, dual operating systems, GPU execution, source-owner custody, native-model training or persistent checkpoint installation.

**SCIENTIFIC — UNVERIFIED / no advantage established:** real-world grounding and independently unconsumed causal family transfer were not tested; the pairwise rule generator matches the strongest symbolic controller and fails outside its grammar. There is no credible claim of AGI, novel unrestricted causal relationship invention or a 10-point gain over the strongest control.

**DEPLOYMENT — NOT DONE:** no GitHub PR/merge, accepted model mutation, controller, queue, scheduled task, external source first-use or real intervention was executed.

## Current repository constraints (read-only check)

- `spoonman136668-ai/Yggdrasil` accepted `main` was `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` during the check; wider historical knowledge image is a **read-only** source resource, not proven integrated native cognition.
- Latest NKR-25–27 evidence on draft PR #1172: **21,343,681 historical fact rows** and bounded injected-fault repair, but no native understanding or scientific superiority.
- Latest CVH-09/10 draft PRs #1176/#1177: operator-approved ceiling **13,312 real interventions** exists, but actual original source first-use remains blocked by owner-signed virgin cohort/actor custody; do not misread approval as source execution.
- `TTT-Hybrid-Lab` R105 draft PR #301: native factual role-aligned unfamiliar-rule accuracy **70.313%**, below frozen **75%** requirement and below independently engineered 256-rule posterior **91.667%**, despite beating trained GRU/MLP in unit-only development. Original science still unverified.
- Wingless and Hybrid own independent architectures and cannot be silently integrated.

## Next Work task: do not repeat this synthetic benchmark

1. Select the user-approved CKAD owner and verify a **typed, source-grounded join** between factual knowledge and public causal transitions. Do **not** infer that historical Wikidata Q/P/Q facts establish causal action effects.
2. Verify independently owned source-first-use authority and never-consumed causal families. Until seed custody is valid, use only prior consumed source records and explicitly classify all work development-only.
3. Measure knowledge **acquisition into native Yggdrasil state**, not external record retrieval. Compare full source exposure and matched strong conventional learners under identical action/data/compute budgets.
4. Freeze unfamiliar entire causal families and a bounded repair protocol before original use. Test whether adding correct knowledge improves unfamiliar prediction, retention under subsequent training, and information-gain per action.
5. Only if source and owner conditions permit, execute independent authentic original-action learning; otherwise finish safe code/controls and record exact blocking predicate.
6. Require independently qualified benefit over the strongest equally informed trained control before promotion to accepted model.

**The key next problem is learned representation capacity and grounding, not bulk storage alone.**
