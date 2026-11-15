# FKP-17 — Structured foundational relationships for unfamiliar causal laws

**Research-only preregistration. No scientific result. No native Yggdrasil change.**

This is a distinct experiment from [FKP-16 #1107](https://github.com/spoonman136668-ai/Yggdrasil/pull/1107). FKP-16's 193,525 real source actions showed zero terminal goals and a direct-memory tie with conventional counts, prior and shuffled controls. Its original development cohort is consumed and must not be retuned or reused as virgin science. FKP-17 does **not** copy FKP-16's action-value algorithm, run its test cohort again, or infer a successful learner from the oracle's privileged hindsight.

## Question

Can a **native/tokenless, non-gradient, persistent relationship structure** built from real public intervention facts help an agent discover unfamiliar causal laws, repair contradictory associations, retain prior skills, and choose beneficial actions beyond what the **same facts** permit for fully trained conventional and unstructured controls?

The primary comparison holds the **32,768 source facts**, 24 exploration actions, 16 subsequent scored actions, public histories and memory ceilings fixed across candidate and fully informed baselines. Strong controls include flat memory, shuffled topology, no-update ablation, independent symbolic/Bayesian learning, fully trained recurrent learning and count/retrieval. A small-foundation arm isolates factual information quantity from structure.

The protocol in `prereg.json` fixes splits, controls, information budgets, 32-world DEV gain and clustered-bootstrap thresholds, disjoint held transfer, no-leakage rules, retention, error and stopping criteria **before implementing or opening any new source outcomes**. FKP-17 aims at genuinely disjoint causal-law families; synthetic achievement must not be called general intelligence.

## Current disposition

- **PREREG-FIRST:** `fe5e259d24100c03b5de8184090e3d6f56fcb7e3` (this branch's initial protocol commit).
- **SOURCE:** Research-only foundation/TRAIN/VALIDATION public synthetic fixture committed in `source_fixture.py`; evaluator-owned DEV/TRANSFER law source is **NOT implemented** and first-use remains blocked.
- **ENGINEERING:** Protocol static checks plus committed source-safe fixture and eight negative/public-history tests. These new Python tests, inherited full regression, G29, build and dual-OS source qualification are **NOT RUN/NOT VERIFIED** on the exact current branch SHA.
- **SCIENCE:** **NOT RUN**. No FKP-17 training, validation, development, transfer, or protected first-use performed.
- **AUTHORITY:** No dispatch or first-use grant inferred from a GitHub PR, a passing contract check, or the operator's conditional integration objective.
- **ACCEPTANCE:** Remains at Yggdrasil `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Do not merge or promote this research draft.

Source-safe contract tests, once checked out, use:

```bash
python -m unittest discover -s research/contrib/chatgpt/FKP-17 -p 'test_*.py' -v
```

## Reuse and nonduplication audit (read-only, 2026-11-15)

- **NKR-03** [draft #1096](https://github.com/spoonman136668-ai/Yggdrasil/pull/1096) already has bounded verified-source exception intake, evidence deduplication, conservative abstention, and cold checkpointing in the **existing 16-slot native relationship memory**. Treat this as a prior baseline/interface candidate, not a license to copy it into a parallel native component. Its quadratic/cubic DEV tied exact evidence lookup and was beaten by stronger symbolic/recurrent controls on some cases; no SCIENTIFIC_PASS or accepted-native integration.
- **FKP-01** [draft #1089](https://github.com/spoonman136668-ai/Yggdrasil/pull/1089) already preregistered a different protected primitive-composition source with 65,536 public edges. Its protected evaluator identity/worlds are **not** FKP-17 input and must remain untouched.
- **WSP-111** [draft #1078](https://github.com/spoonman136668-ai/Yggdrasil/pull/1078) already implements a million direct-programmed numerical facts and two rounds of inferred categories; symbolic/conventional controls tied its original synthetic task. Reuse only compatible publicly verified representations and cost/accounting patterns, never imply its source families are novel independent FKP-17 laws.
- **Implementation decision:** before adding any new memory engine, compare native NKR-03's evidence semantics with FKP-17's 8-register, 8-action, delayed-observation public interface and document exact incompatibilities. Prefer a minimal adapter or independent **research-only comparator**, not a rival accepted model, controller or scheduler.

## Source-safe implementation checkpoint (fixture only)

The separate `source_fixture.py` is a deterministic **synthetic** environment for 128 foundation worlds, 64 TRAIN worlds and 16 VAL worlds. `foundation_facts()` emits **128 × 256 = 32,768** source-observed public records. Each record exposes only 8 four-bit public registers before/after one action, the earned reward, the done flag and up to 16 already-observed public transitions; no law coefficients, alternate action returns or future observation leaks into a returned record. `public_actions(seed,count)` creates an independent seeded common-action tape for control parity. Public digest receipts can identify source facts separately from learned representations.

Its two known families are simple directed affine-mod16 and bounded pairwise monotone-mixing dynamics. This **does not implement the new held law families**, prove identifiability, or make synthetic reward comparable to a real external benchmark. Every original FKP17 DEV seed `978500..978531`, TRANSFER seed `978600..978663`, and all unknown or predecessor seeds raise `PermissionError` through the only public source-acquisition APIs. There is no `allow_dev` switch, no protected key or evaluator in this research branch.

`test_source_fixture.py` adds tests for denied held cohorts and invalid caller inputs, public-only fields, no future history, repeatability/digest changes, action consequences, complete 32,768 foundation record enumeration and a source-import boundary. **The tests are authored, not executed**; they are not evidence of simulator qualification. The published training fixture code is inspectable and does not create cryptographic isolation. A truly private, independently sourced DEV/TRANSFER evaluator remains a separate owner-controlled requirement. Candidate models must only see a sanitized public transition stream and may not import this evaluator module.

This source-only gate changes **no** Yggdrasil native implementation, accepted memory, scored FKP-16 world, first-use or external runner.

## Qualification before a first-use decision

The next engineering work is to independently author the source-private causal-world generator, learner and equally informed baselines; freeze their blobs and source provenance, implement public-only, leak-negative and contradiction/cold tests, and run mandatory exact-source full regression across Ubuntu and Windows. Any original DEV or TRANSFER run additionally needs **independently verified scientific-owner exclusive first-use approval**. Never use held outcomes to repair a pre-result harness defect; quarantine consumed worlds if that happens.

Nothing here authorizes new schedulers, controllers, runner ownership changes, paid models, source ref promotion, deployment, or modifications to Wingless/Hybrid.
