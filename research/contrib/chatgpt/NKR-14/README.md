# NKR-14 — Unseen operator-family falsification and identifiability lower bound

NKR-13 [draft PR #1149](https://github.com/spoonman136668-ai/Yggdrasil/pull/1149) qualified at [exact source SHA `429135fa95aad733a3ef84b167f13431db552a58`](https://github.com/spoonman136668-ai/Yggdrasil/commit/429135fa95aad733a3ef84b167f13431db552a58) with 131/131 full regression on Ubuntu and Windows. On the same synthetic conjunction worlds that exposed NKR-11's parity limitations, NKR-13 achieved 129/192 correct and **zero** confident errors, with 63 abstentions, 384/384 retention and 4/4 single-corruption refusal. The equally informed independent exact conjunction symbolic learner **tied on every query**. This was bounded engineering, **not proof of novel cognitive relation-family invention**.

## Research question

How does that *unchanged* bounded learner behave when the hidden action effect is **not a conjunction at all**? Is there enough information in the eight paired action contexts to identify any unrestricted relation on the other eight unseen contexts? Can overconfidence or unavailable grammar be exposed without changing the learner after inspecting results?

**NKR-14 prereg FIRST** `78d2b994af8a3df829dc3b6c53aa02a9f8eb36f3`, before implementation or fresh world outcomes. New task-specific code is only a new independent procedural environment and a separate mathematical identifiability comparator, not changes to `yggdrasil/native_operator_discovery.py`, native causal owner or the accepted Yggdrasil model.

## Unseen causal operator families

Twelve fixed 4-bit context worlds, each with an old warm mechanism and an unfamiliar new action-effect function:

1. XOR(x0,x1)
2. OR(x0,x1)
3. NAND(x0,x1)
4. XNOR(x0,x2)
5. EXACTLY_ONE(x0,x1,x2)
6. AT_LEAST_TWO(x0,x1,x2)
7. x0 AND NOT(x1)
8. IF x0 THEN x1 ELSE x2
9. (x0 OR x1) AND x2
10. x0 XOR (x1 AND x2)
11. AT_LEAST_TWO(x0,x1,x2,x3)
12. (x0 XOR x1) OR (x2 XOR x3)

All are outside the NKR-13 family of *single nonempty positive conjunctions* when evaluated across all 16 contexts. The experimental environment's hidden operator ID and implementation are **not passed to the learner**; its source IDs use hashes of actual public observation rows rather than operator/world labels. These functions are **experimenter-designed synthetic examples**, not authentic independent world evidence, and their existence in the evaluator does not prove that the model discovers their algebra.

The old mechanism is revealed by all 16 contexts × both actions, **32 observed outcomes/world**. On the new mechanism, only the fixed eight paired intervention contexts `[0,1,2,4,8,3,5,10]` are presented to the learner, both actions (16 source-visible public outcomes). The eight different contexts `[6,7,9,11,12,13,14,15]` are never learned; test both actions on each (192 heldout action outcomes across 12 worlds). Original warm memory must retain **384/384**, with exact immutable checkpoint receipts, source-pinned events and no writes into accepted YPC1/DG1 or any 21.3M factual dataset.

## Strong safety and identifiability comparator

There are `2^16 = 65,536` possible *arbitrary binary action-effect truth tables* on four context bits. After measuring eight independent action-effect outputs, precisely `2^(16-8) = 256` such functions remain consistent with **the same visible intervention data** in each world. For each unseen action-effect query, both 0 and 1 remain possible among those 256 tables. This is an **information-theoretic impossibility without some structural prior or another intervention**—not an implementation defect.

A separately implemented **unrestricted Boolean effect version-space control** receives the exact same 16 public action outcomes and learns the independent action-zero parity baseline from the visible contexts. It returns the known baseline for new contexts with action=0, and **abstains** from predicting the action=1 effect on every unobserved context. Expected source-free result: **96 correct, 96 abstentions, zero confident mistakes** out of 192. This is a *conservative bound*, **not** a fully trained predictive neural competitor; NKR13 may make additional correct predictions by using its prespecified conjunction inductive bias but risks overconfidence outside that bias. Do not compare scores as architecture dominance.

For the unmodified NKR13 learner, score its **qualified post-feedback** predictions and abstentions; if its new-family feedback cannot qualify a candidate, do NOT silently count stale old-memory predictions as knowledge of the changed environment. The frozen falsification criterion is **at least one confident wrong prediction OR at least one new-family evidence bundle with no supported conjunction**. Preserve separate counts. Do not change the worlds, action budget, splits, score or hypothesis family after results.

## Acceptance and limits

- New source-free test suite validates all 12 operators differ from each of the 15 conjunction templates, identical independent evidence for model and conservative comparator, 256 consistent completions, cold context protection, old-retention 384/384, exact provenance, fail-closed unsupported operator family and no accepted-model write.
- Existing qualified GitHub-hosted Ubuntu and Windows only. Mandatory full original root regression and NKR05 six focused tests, plus independent G29 on each OS at exact final SHA/tree. G29 source index is generated-only after source-safe development. No paid API, new runner or task scheduler, no model owner, no current 21.3M artifact download, no original science first-use.
- No scientific `PASS` is possible here: all outcome mechanisms were authored inside a deterministic synthetic test harness, and 8 independent unseen effect bits remain mathematically undetermined without structural assumptions. The correct lesson is to seek **authentic interventions**, learn useful compositional priors independently, and explicitly plan how to acquire information rather than repeatedly claiming operator invention from a finite grammar.
- Accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` remains unchanged; this remains a stacked draft research PR and does not install the full historical knowledge image or activate Yggdrasil cognition.

The large-scale operator capacity question is answered by the exhaustive 65,536-function ceiling for 4-bit contexts, not a narrow benchmark with 8 handselected relation slots. For general intelligence, a finite family and synthetic replay do not establish transfer; **a source-independent information-acquisition and representation-learning experiment is the next independent science objective**, with owner-qualified data/first-use and matched strongest baselines.
