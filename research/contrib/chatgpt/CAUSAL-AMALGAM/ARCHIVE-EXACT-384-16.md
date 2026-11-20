# ARCHIVE-EXACT-384-16 — original CKAD22 intermediate checkpoint byte recovery

**2026-11-20. Engineering custody PASS, scientific gain UNVERIFIED.** This is read-only recovery of original **already-consumed synthetic** historical source evidence, not model training, original-world source actor first-use, new actions, deployment, or a checkpoint promoted to the canonical learner. Integration authority remains solely with the Amalgam coordinator PR #1278. Contributor PR #1326 is draft.

## Source custody

- Original CKAD21 Linux parent ZIP: SHA256 `2addc338ebaba21115d5700f6a64b1612a4be7099267b7ec1df7d84d1530c293`; saved per-seed original 320-witness parent checkpoint and final_sha256.
- Original CKAD22 Linux run [#44266448951](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44266448951), artifact #14410228167 ZIP SHA256 `90362c075154ab936fc2e0a82716fbe5bd875585cd89aeed0b08b32831560fc4`; three full original 448-event final native checkpoints and `campaign-result.json`, with the exact intermediate original checkpoint SHA, byte count and derived-state SHA for 4 sessions/seed.
- CKAD22 original Windows same-run artifact #14411380648 ZIP SHA256 `e4fea224001f0b850a10cd1954e85262a41364b0f09734caf07175c9e3caa6f7`; original stable report digest in both OS `4b20ef3b9229eddfd509e5897e6aa8f8d5226288ab331c4a98f8a7bc46fbccc2`. Original saved state receipts **12/12 seed-session matches** Windows vs Linux.
- Original source commit `e9aa921c57dca836c06c7125e52229cce728620a`; CKAD22 producer `research/contrib/chatgpt/CKAD-22/campaign.py` Git blob `84ca680476b8bb6e1be8791d2eb6bf01b819b83c`; native exact-ASCII canonical serialization `sort_keys=True,separators=(',', ':'),ensure_ascii=True`.
- Original full 320-witness parent experience ledger is byte-equal to first 320 events of CKAD22 final 448-event ledger in **3/3** seeds. All root native checkpoint fields **except `experience_ascii`** are byte-equivalent to the original 320-witness parent across **3/3** seeds. Original CKAD22 parent checkpoint hash matches exact CKAD21 parent hash in **3/3** seeds.

## Method (no native model inference)

The original final 448-event checkpoint contains the immutable ordered native experience ledger. The original CKAD22 per-session result includes the authentic original episode-state SHA256 and original full native checkpoint SHA256, as well as full byte length. For session i in {0,1,2,3}, take the final root native JSON, replace **only** `experience_ascii` with canonical ASCII JSON of the same episode checkpoint containing the first `320+32*(i+1)` original events, original saved `context_start=320+32*i`, and **original separately recorded `experience.state_sha256`**. Hash the complete canonical ASCII native checkpoint bytes. Reject on SHA mismatch, byte-count mismatch, context/seed/event-source drift or noncanonical source. **No invented digest, event, reward or model value** is admitted.

**Important limit:** The recovered derived state SHA was **taken from the original signed-by-archive campaign receipt**, not independently recalculated by executing the native model. Matching the original full checkpoint cryptographic SHA256 and byte length nevertheless establishes byte-identical serialized source custody, assuming original Actions artifact integrity. The recovered **384-event checkpoint is the saved end-of-session1 (B) state, with `context_start=352`**. The *newly initialized* session2 return-world **zero-probe** context (same 384 events but `context_start=384`, reset 12×7/96 + 1/8 weights) is a **different state** and was not recreated/restored or executed here. Do not conflate these.

## Actual exact historical SHA and length

| Seed | Recovered end-of-session1 384-event native full-checkpoint SHA256 | Bytes | Status |
|---|---|---:|---|
| 101 | `c98c3aca9388b8f1fa96f057955aceb1a460410641c3b87892501ce563bfb3c4` | 2,747,485 | PASS |
| 202 | `6a91dfed5eaebaf5766e400ff05c9c323f95b66cf77f0d2dab683668d60af42e` | 2,778,879 | PASS |
| 303 | `708334d15e385fb02513c5b9b701b400681a04086037d8209725637f38c066fb` | 2,775,831 | PASS |

Full original session0–3 352/384/416/448 saved checkpoint bytes and hashes **12/12 exact PASS**; 384 specifically **3/3 PASS**. No original checkpoint bytes or raw experience IDs published in this repo. A read-only local copy was created under the auditor's temporary working directory only, not integrated or promoted.

## Auditable implementation

- Source-only pinned reproducer: [`ckad22_exact_intermediate.py`](./ckad22_exact_intermediate.py), Git blob `f5868744ec6c59e874d0cd480eb1582740d6ac4f`. CLI `python research/contrib/chatgpt/CAUSAL-AMALGAM/ckad22_exact_intermediate.py ckad21-original.zip ckad22-original.zip ckad22-original-windows-proof.zip`. Emits ONLY sanitized metadata (SHA, byte length, seed, checkpoint session, qualification flags).
- [Archive-gated regression and tamper negatives](../../../tests/test_ckad22_exact_intermediate_recovery.py), Git blob `8b86e99bd19e3f13bca982e7868133db0f858e2a`. CI without the original ZIPs MUST skip the original-byte custody tests; source-only negative checks are CI safe. Explicit original artifact inclusion is required before asserting original archive CI proof.
- Local source-only proof script SHA256 `c61812bfeb72f8b440242a608ff57731366859d8fbac831a6bb5f718038fa9d8`, local original-source tamper tests SHA256 `5ca784792f293a4e53013ae455080564c8479a783c49d42ca478f4c1e24fc74e`; original local 14/14 PASS (these local files are a slightly different formatting revision from the subsequently Git-committed reproducer). Sanitized source result JSON SHA256 `6611bfb48714ab8e31e12c08d59c279b1dff1f6d7ca29adf868da42ac76bdce4`. Do not misstate the local tests as exact Git-blob Linux/Windows qualified without final CI receipts.

**Engineering:** archival 12/12 exact byte-source custody PASS, original Windows semantic custody PASS, local focused 14/14 PASS, current candidate G29/full regression must be qualified independently; inherited Gate25 4 frozen failures cannot be waived. **Scientific:** actual native zero-probe-context selection, independently held cold return, unfamiliar causal discovery and gain beyond strong Bayesian control UNVERIFIED; original historical CKAD22 strongest control reward 257/288 versus native 246/288 on return (NO-GO for superiority). **Deployment:** NONE. Source-owner protected new first-use [#426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) remains DENIED.

**Next distinct engineering target:** given these byte-identical original end-B native checkpoints, call `NativeCumulativeLearner.restore(raw, original_sha)` and then `begin_experience_context(novel=True)` read-only, compare source-exact newly initialized cold readout against historical independent Bayesian mixture, without any `observe` or new original source episodes. This is a test design, not an executed claim.


## Read-only actual-native zero-probe follow-up (pre-execution note)

The separate [frozen protocol](ckad22_native_zero_probe_freeze.md) and [candidate script](ckad22_native_zero_probe.py) use ONLY the hash-authenticated original CKAD22 pre-return 384-event native checkpoint reconstructed here, on an isolated clone. The actual class is restored; `begin_experience_context(novel=True)` creates a new in-memory context with 12 old hypotheses and one empty candidate; the code reads predictions and two-stage native choices without receiving a new outcome or touching accepted model lineage. This is **not** the already scored historical result, a new owner first-use, source action, or scientific gain. The existing scoped [qualification workflow](../../../.github/workflows/amalgam-relation-shadow-qualify.yml) (path relative to repository root) now uses the exact original GitHub Actions artifact ZIP ID 14410228167 with source/ZIP/checkpoint pins before running full inherited tests. Existing frozen Gate25 failures remain expected regression failures. CI and actual-native comparison are **UNVERIFIED** until independently checked against final candidate SHA and logs; scientific gain remains **UNVERIFIED/NO-GO**, deployment NONE.
