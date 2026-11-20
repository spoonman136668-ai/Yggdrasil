# NCI-SOURCE-03 — Exact Amalgam admission-boundary replay guard audit

**2026-11-19 | Independent Yggdrasil research contributor.** The only central integration coordinator is **Unified Causal Intelligence Amalgam Work**. This is a *non-installed* compatibility/negative-control study of the existing research Amalgam admission method, not a new model, training, authorized first-use, model integration, or promotion.

## Pinning / scope

- Repository: `spoonman136668-ai/Yggdrasil`. Amalgam research candidate: [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), HEAD `86264b41a08d49f558418c0fba367f3a2636befa`.
- Exactly pinned original source: `yggdrasil/native_causal_amalgam.py`, Git blob **`287e6fbb9d1f9612f88f9d5ed5dda88be4bb7952`** (6,102 bytes), independently retrieved from GitHub and verified again in the local read-only reconstructed copy. The test compares the original `NativeCausalAmalgam.observe_experience` **full AST** against its committed verbatim method excerpt before scoring. It runs that *actual original method body* and an AST-instrumented **proposed** method in an isolated, in-memory, simplified native/JEPA fixture. It does not execute the imported full Amalgam object, its actual specialist GPU/CPU training, native checkpoint parser, or real environment.
- Related unchanged native episode interface: `yggdrasil/native_episode_experience.py`, blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`, 
  `ROW_FIELDS=("s1","x1","s2","x2","y")`. It encodes `event=(identifier,views,*bits[1:])`, omitting the validated `s1` from stored event. The existing Amalgam restore reconstructs `s1` from `views[0][0]`. The source-specific original/adapter mapping was audited independently in NCI-SOURCE-02.
- Accepted `main` and the actual owner-held persistent checkpoint are not modified or used. Source-owner [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) still denies new original-world protected first use.

## Precise failure and smallest proposed change

Current research `NativeCausalAmalgam.observe_experience()` calls `self.native.observe_experience` **before** validating whether public paired views agree; if it was a duplicate, the native reader returns the identical object, and Amalgam exits without that check. Also, no check in the method requires the original `row["s1"]` to equal either view's first component. Since native event projection excludes that row field, a duplicate with changed `s1` can be accepted as idempotent even when a separately calculated source packet digest matches the changed row. This is a consistency/audit finding within an unmerged research implementation, not evidence of a real malicious source or prediction failure.

**Proposed guard placement — FIRST statement before `self.native.observe_experience`, before any idempotent return:**

```python
require(
    type(views) is tuple and len(views) == 2
    and all(type(v) is tuple and len(v) == 2 for v in views)
    and type(row) is dict
    and type(row.get("s1")) is int and row["s1"] in (0, 1)
    and all(type(v[0]) is int and v[0] in (0, 1) for v in views)
    and row["s1"] == views[0][0] == views[1][0],
    "AMALGAM_PUBLIC_INITIAL_STATE_MISMATCH")
```

The local test script supplies the same check as its `guard()` helper and inserts it only at the beginning of a copied AST, without changing any original native source, policy, specialist, owner, or checkpoint. **The precise guard error semantics and compatibility for invalid *other* input shapes still need full original-source negative regression**. Do not auto-apply it to `NativeEpisodeExperience`: that class has other paired-view caller contracts and no owner-qualified evidence yet warrants changing their meaning.

## Exact isolated result

Running `audit_boundary.py --full-native-source <exact checked-out native_causal_amalgam.py>` first verifies the complete original source Git blob SHA-1 and the original method AST; it then scores **128** fully enumerated *consistent* binary event configurations: 2 initial states × 2 auxiliary bits in each view × 2 each for `x1`, `s2`, `x2`, and `y`.

| Original pinned method and proposed entry guard | Count / result |
|---|---:|
| Valid first admissions preserve identical serialized fixture state / native parent / four specialist updates | **128/128 PASS** |
| Valid duplicate admissions remain idempotent | **128/128 PASS** |
| Valid cold *fixture* serialization and re-admission of the row reconstructed from views | **128/128 PASS** |
| Original pinned method accepts contradictory initial-state field on first admission | **128/128 observed** |
| Original pinned method silently replays changed `s1` duplicates | **128/128 observed** |
| Original pinned method silently replays contradictory paired views on duplicate | **128/128 observed** |
| Proposed guard rejects contradictory first admissions before native update | **128/128 PASS** |
| Proposed guard rejects changed-`s1` duplicates before native update | **128/128 PASS** |
| Proposed guard rejects inconsistent-view duplicates before native update | **128/128 PASS** |

There are **11 × 128 = 1,408** explicitly counted cases across the result's independent categories. Counts measure fixture protocol cases, **not** independent statistical trials, full-model regression cases, original source actions, or learned scientific gains. The existing method excerpt and full original source **match by AST** and blob. The fixture native-memory implementation reproduces the pinned event projection but does not prove full-source `NativeCumulativeLearner.restore` or `NativeCausalAmalgam.restore` would succeed with a real multi-MB checkpoint after installation. Historical trained checkpoint/ledger and public source first-use were **not touched**.

## Reproduction

Use standard Python 3.13 (no packages). For strict, exact-source qualification, obtain the same pinned Amalgam commit on a clean read-only checkout and run:

```bash
python -B audit_boundary.py \
  --full-native-source /path/to/pinned/yggdrasil/native_causal_amalgam.py
```

The script fails closed if full-source blob or AST differs; if `--full-native-source` is omitted it reports `METHOD_EXCERPT_ONLY_STRICT_FULL_SOURCE_NOT_RUN` and should **not** be represented as exact whole-file qualification. The JSON at `result-strict.json` was produced with strict full-source verification in an isolated local copy, which was reconstructed byte-exactly from the GitHub commit; source file itself is **not vendored** into this contributor archive.

## Integration interface and next owner gate

**Exact target:** existing `NativeCausalAmalgam.observe_experience` (source blob above), ahead of the call to `NativeCumulativeLearner.observe_experience` / `NativeEpisodeExperience.observe`, and before returning early for duplicate ledger event. The narrow intake guard requires no checkpoint-schema change. The central coordinator should separately evaluate it against the same **verified owner-held checkpoint**, with authentic old/new/old-return predictions, native source packet validation, valid staged view disagreement if allowed by caller, conflict/idempotence negatives, full cold restore and Linux/Windows full final regression. This contributor does **not** implement the guard in the canonical model or consume protected first-use.

**ENGINEERING:** exact Git blob/method AST PASS; isolated 128-case fixture negative and compatibility proof PASS; full installed native cold restore and final dual-platform CI **UNVERIFIED**. **SCIENTIFIC:** no new-law learn/retention/transfer improvement established. **DEPLOYMENT:** NONE. Preserve ENERGY-67/69/71 NO_GO and all independent research tracks. The existing large archival PR may still fail G29 for stale generated atlas; do not weaken that check.
