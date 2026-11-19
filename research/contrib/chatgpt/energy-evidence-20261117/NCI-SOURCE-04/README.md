# NCI-SOURCE-04 — Pinned staged-callsite compatibility for Amalgam input guard

**2026-11-19 • independent Yggdrasil research contributor • `ENGINEERING_ISOLATED_PASS` / `NATIVE_SCIENCE_UNVERIFIED`.** No native production patch, model update, checkpoint mutation, external source first-use, merge, controller, runner or scheduler. The **Unified Causal Intelligence Amalgam Work chat** remains the single integration coordinator.

## Source identity and non-duplication

- Existing **Amalgam research PR #1278**, pinned SHA `86264b41a08d49f558418c0fba367f3a2636befa`; accepted `main` remains `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- `yggdrasil/native_causal_amalgam.py`: exact Git blob `287e6fbb9d1f9612f88f9d5ed5dda88be4bb7952` (6,102 bytes). This report compiles the actual original `NativeCausalAmalgam.observe_experience` method AST and a copy instrumented **only in memory** with the proposed first-statement guard.
- `research/contrib/chatgpt/CAUSAL-AMALGAM/staged_public_readout.py`: exact Git blob `33b8513f3acaf87bda8e1f5a846d90a91c07dbc5` (2,758 bytes). This report executes the **actual pinned source AST for all six methods** of `StagedPublicReadout`, not an invented replacement for its staged state machine. Both byte identities were checked against GitHub.
- Follows NCI-SOURCE-03 (independent isolated negative/compatibility testing of original Amalgam admission) without rerunning its scientific experiments. The **new distinction** is a full native research **caller contract**: action readouts before transition/reward, staging and packet digest, duplicate idempotency and future guard effect. The non-installed `Native` and four specialist heads are still simplified fixtures; nothing here performs full native/JEPA training or a real checkpoint restore.

## Full staged-callsite test

The existing staged constructor calls `_views` (two binary 2-tuples) and requires both initial state bits to agree. The real `observe_reward` constructs `row['s1'] = self._views[0][0]` and calculates `packet_sha256` over that exact public row. It therefore already enforces the proposed input guard on its normal path. Existing other research callers/owner-world ingress remain separate audit targets.

The test cross-products **128 valid** binary tuples: `s`, each view's auxiliary coordinate, `x1`, `s2`, `x2`, `y`. For each tuple:

- Call the original staged `first_action`, `observe_transition`, `second_action`, and `observe_reward` in their actual order, with exact source signatures.
- Compare the serialized **fixture** ledger, four observed specialist heads and parent pins against a direct call to the original unchanged Amalgam admission method, byte-for-byte. **128/128 PASS.**
- Use the same original staged interface on the resulting state and prove duplicate admission remains idempotent. **128/128 PASS.**
- Verify a second `observe_reward` is rejected by the original staged ordering contract. **128/128 PASS.**
- Verify staged construction rejects first-view state disagreement before any input reaches native. **128/128 PASS.**
- Verify proposed in-memory first-statement guard rejects a changed `row['s1']` on first or duplicate direct native admission *before native is called*. **128/128 each PASS.**
- Verify staged source packet digest stays identical to the expected public canonical envelope. **128/128 PASS.**

**Seven counted 128-case categories = 896 assertion groups; additionally two exact original Git blob/AST identities PASS.** Positive tests do not include any protected original source actor, real model checkpoint or independent scientific trial. The previous source-specific NCI-SOURCE-03 1,408-case fixture findings remain separately archived; their counts are **not** counted again here.

Negative controls: tampering either pinned source file causes a fail-closed source-blob check; an existing output destination is refused. Repeated invocation from identical source returns identical JSON results. These are local engineering checks only.

## Reproduction

The same `audit_staged_caller.py` source (sha256 specified in `manifest.json`) is archived losslessly as `audit_staged_caller.py.xz.b64`. Use the included `verify_source.py` to verify and reconstruct into a fresh output directory. Obtain a **read-only, exact SHA checkout** of Amalgam #1278; this contributor bundle intentionally does not vendor original GitHub modules. The audit checks both originals at the byte level **before** execution.

```bash
python -B verify_source.py --out /tmp/nci04-src
python -B /tmp/nci04-src/audit_staged_caller.py \
  --amalgam-source /path/to/Amalgam/yggdrasil/native_causal_amalgam.py \
  --staged-source /path/to/Amalgam/research/contrib/chatgpt/CAUSAL-AMALGAM/staged_public_readout.py
```

The `result.json` is the frozen local test receipt; reproduction must produce the same parsed JSON. No numerical seed or model training is used.

## Native interface and stop condition

**Proposed (not installed):** place an initial-state agreement guard at the **first statement of `NativeCausalAmalgam.observe_experience`**, before `self.native.observe_experience` and before the duplicate early return. This requires no new weight owner and **no checkpoint schema change**. Existing `StagedPublicReadout` is compatible with the guard by source and isolated case study. **It is not yet safe to assert all callers are compatible:** the full legacy `NativeEpisodeExperience` accepts its own paired-view semantics, and other `BASE.public_views`/`LEGACY.fixed_rollout` paths have not been qualified against an authenticated owner checkpoint.

The central Amalgam coordinator must verify the real owner-held native checkpoint and its original ledger; existing valid and intentionally divergent view cases; source packet authentication and duplicate conflicts; full native/JEPA cold restore; all targeted source callers; and mandatory Linux/Windows full regressions and G29 at final SHA before considering a native patch. Original-world protected first use remains blocked by source-owner issue #426. This independent contributor does not activate model-side updates or use new protected cohorts.

**ENGINEERING:** exact-source caller compatibility PASS in isolated fixture, accepted CI/regression UNVERIFIED. **SCIENTIFIC:** source-native causal learning improvement UNVERIFIED; no claims of retention, reasoning or transfer. **DEPLOYMENT:** NONE. Prior ENERGY-67/69/71 scientific negatives remain intact.
