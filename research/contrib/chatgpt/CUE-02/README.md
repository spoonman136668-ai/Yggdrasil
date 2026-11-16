# CUE-02 — finite-public-evidence novelty auditing, high-first probe sweep

**Result: `ENGINEERING_DEV_PASS_SCIENCE_UNVERIFIED_AND_UNBOUNDED_IDENTITY_UNPROVABLE`.** Native source-blind read-only audit works on reused engineering fixtures; **no accepted world identity, independent scientific source, native accepted weight or automatic deployment**.

## Why CUE-02 exists

[CUE-01 draft PR #1150](https://github.com/spoonman136668-ai/Yggdrasil/pull/1150) identifies 12 of 12 previously saved NKR-11 causal relationships from public intervention feedback and exactly ties an independently implemented symbolic selector. However, two of four out-of-family nonlinear engineering worlds produce **false provisional memory slot matches** after eight CUE-01 active probes.

CUE-02 tests a different mechanism: **finite-domain public evidence auditing**, prospectively sweeping the largest budget (all **32** possible `(4-bit context, binary action)` intervention pairs) down through **24, 16, 12 and 8**, with three source-blind probe orders, a fully fitted independently coded exact symbolic control, and intentionally adversarial indistinguishable unknown laws. This does not rerun NKR-13's separate operator-induction experiment or invent a new causal learner.

A known stored memory agreeing on all observed outputs is *compatible*, not source-authenticated. For any algorithm observing fewer than 32 unique actions, another law can return the same results on all queried actions and differ on one unqueried action. We construct **12 exact counterexamples** in the development evaluator: one per stored law, matching its first 31 public responses and flipping its last. Therefore no partial-observation policy can **guarantee** rejection of every out-of-family source. Even agreement on all 32 outcomes proves at most equivalence on this finite interface, not that the new external world's identity and dynamics are the historical source. This is a general identifiability limit, not a training failure.

## Source, tested software and pre-registration

- Exact parent: CUE-01 source-pinned generated-only SHA `600c5dc828adccf86f1411cddef153401658bdcd`, unmerged draft; accepted main unchanged `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Preregistration committed **first** at `7900c9f548577a689bc9b2e68ea62d3215a37611`, before implementation, source screen or outcomes.
- All new code plus **19 focused tests** committed before the first source evaluation at `d86c76b24f784cad69592be0e89c07858a64d35a`.
- `yggdrasil/native_finite_cue_audit.py` (Git blob `089fe536650404c645dc07cf2ec9ffb86758153e`) accepts only the unchanged NKR-12 native bank and actual public `(context,action,consequence)` observations. It never sees the true world identity, source mask, oracle, accepted source provenance or protected score. Read-only: there are **zero** bank writes.
- `research/contrib/chatgpt/CUE-02/dev.py` (blob `9919facd671cde30c6bdddd6c78920c8780ff0dc`) is the **separate** evaluator that owns actual deterministic public action responses, target identities and the independent symbolic control. It consumes **only previously exposed NKR-11/CUE-01 synthetic engineering worlds**, no fresh real/original science.
- Original CUE-01 router, NKR-11 solver, NKR-12 native bank and existing model/weights unchanged. Returned statuses never set `source_identity_authenticated`, `native_accepted`, `scientific_pass`, `safe_to_activate_accepted_model` or `write_to_accepted_model` true.

## Exact frozen screen

Three deterministic action orders, independent of a world ID or hidden nonlinear masks:

- **Dense**: descending population count of public context bits, then descending context and action; tests interactions generically.
- **Lex**: ascending context/action.
- **Hash**: ascending SHA256 of the string `CUE02|public-probe|context|action`, then tuple.

For each policy, the evaluator calls the public action oracle for all 32 unique interventions, then scores the *same action trace prefixes* of lengths 32, 24, 16, 12, and 8. Each budget gets the **same number of public observations across policies**. Twelve existing known models and four already-used out-of-family AND worlds are evaluated, all without retraining. The independently implemented strongest conventional exact symbolic selector checks identical public evidence and existing stored models; **every model decision agrees exactly**.

### Actual source-only results (identical on Ubuntu 24.04 and Windows 2022)

| Probe order | Budget | Known retrieved | Unknown nonlinear rejected | False provisional matches |
|---|---:|---:|---:|---:|
| **Dense** | **8** | **12/12** | **4/4** | **0/4** |
| Hash | 8 | 8/12 | 3/4 | 1/4 |
| Lex | 8 | 6/12 | 4/4 | 0/4 |
| Dense | 12, 16, 24, 32 | 12/12 at each | 4/4 at each | 0/4 |
| Hash | 12, 16, 24, 32 | 12/12 at each | 4/4 at each | 0/4 |
| Lex | 12 and 16 | 8/12 | 4/4 | 0/4 |
| Lex | 24 and 32 | 12/12 | 4/4 | 0/4 |

All known-world incorrect matches **zero**, all budget and source-custody gates **PASS**. The independent exact symbolic control makes the **same decisions on every policy/world/budget**: the positive is better cue ordering for these known test families, **not** an independent intelligence advantage.

**High-first result:** Complete 32-probe evidence correctly distinguishes all four preexposed nonlinear laws from all retained GF(2) memories. We then worked backwards and found that the frozen complexity-first order also achieves 12/12 known recognition and 4/4 unfamiliar rejection at the original eight-probe budget. This is a **mechanical development signal only**, because those nonlinear families are already known to this research track and the policy's success is distribution-specific. The twelve 31-of-32 adversarial witnesses show that a different, genuinely unknown law can still evade the same incomplete observation strategy. Even full 32-probe equality never authenticates source identity.

- Exact public training source SHA256: `caf7ae6b1b3af283ca9af2a1d852f95d25cdd8638281fb37b77d6b72b7990acc`.
- Exact result trace SHA256: `ef40cc064e7a24be74cf8fe13b1ab4cf780e5e32f2e0d0169db2ef426e8d9303`.
- Original persistent native bank checkpoint SHA256: `a03b6e5fc63d3b69d088bd4b45aca3ed5df7d169e4c9820dcc8f9b3dd25b67bb`, **24,773 bytes, unchanged**.

## Engineering qualification and original negative

First isolated [Windows/Linux screen #43920235795](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43920235795) had an **engineering test failure, 18/19 tests on both platforms**: the source-blindness test incorrectly matched the literal substring `source_id` inside the *allowed safe result field* `source_identity_authenticated`. This did **not** reveal a model/learner failure. The only correction changed the test to match a complete identifier with regex word boundaries, at commits `1437be0c91f5595f3502be964a6be8feac1a2cad` and `c95eed2f50011e4a9ab1a3a12d29f872e3459688`. The native auditor, source/evaluator, intervention order, truth tables, fixed thresholds and preregistered gates were unchanged after first score.

The corrected **[source-only run #43920501441](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43920501441) completed SUCCESS** on Ubuntu and Windows: **19/19 focused tests PASS** each; identical predicted decisions, trace and source IDs, 12/12 deterministic impossibility witnesses PASS, and no protected scientific first-use. See `result.json` and `provenance.json`.

A separate exact-source generated G29 atlas and **complete inherited Windows/Linux Python regression** are required before declaring this draft engineering-qualified. An additional native application build, original scientific source admission, source authenticity attestation, and owner runtime integration remain **NOT RUN**.

## Reproduce and interpret

From repository root, Python 3.12 standard library:

```sh
python -B -m unittest discover -s tests -p test_native_finite_cue_audit.py -v
python -B research/contrib/chatgpt/CUE-02/dev.py --source-dev
python -B research/contrib/chatgpt/CUE-02/dev.py --primary # must reject
```

**ENGINEERING:** adds a safe, read-only finite-evidence matching interface on native retained causal memory, without changing accepted state. It exposes evidence coverage, never authenticates a source.

**SCIENTIFIC:** unverified. The rule family remains fixed, all environments are reused public synthetic worlds, the independent fully informed symbolic model ties, and **unrestricted out-of-family identity detection is mathematically impossible without additional assumptions/source authentication**. Cold return and storage were inherited from NKR-12, not newly learned here.

**DEPLOYMENT:** none; draft stacked on the unmerged NKR-11/12/CUE-01 line, no main merge, native owner activation, scheduler, controller or protected science first-use. A future substantive direction is actual operator learning from independently sourced environments with provenance-qualified confirmation, not raising confidence in these matching outputs.
