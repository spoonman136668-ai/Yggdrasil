# NCI-04 R18 — Additional original-source log recovery (review only)

**Disposition:** `HISTORICAL_LOG_RECOVERY_PASS / GLOBAL_ORIGINAL_RESET_CUSTODY_INCOMPLETE / SCIENTIFIC_FIRST_USE_NO_GO`

## Source-bound addition

Parent R17 exact commit: `3c21441f491f003451a9c592b8d898c4887c892e`. Source-only supplemental record `R18_EXTENDED_ORIGINAL_LOG_RECEIPTS.json` was derived from the previously completed, real original-engine GitHub Actions jobs below, not from a simulator or an intended future execution:

| Historical experiment | GitHub Actions run | Independently compared native jobs | Episode records | Original source actions |
| --- | --- | ---: | ---: | ---: |
| MR34G | [39704703315](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/39704703315) | Ubuntu + Windows, 2/2 agree | 40 | 2,098 |
| MR34H | [39743368976](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/39743368976) | Ubuntu + Windows, 2/2 agree | 64 | 3,353 |
| MR34I0 | [39744526158](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/39744526158) | Ubuntu ×2 + Windows ×2, 4/4 agree | 16 | 740 |
| **This R18 addition** | | **8/8 agree** | **120** | **6,191** |

The exact frozen protocol Git blob identities were checked before extraction: MR34G `d64d1fd1d50bfb8c021b7a254d91fea92931d2ad`, MR34H `9131e3c459cff0f93b1c7950c38f19fbc23229a7`, MR34I0 `f458b50b713d91383f9b8cc5c05fc1205d431353`. Source-engine commits are declared in the new JSON and pinned to the original source protocols. All 120 rows include engine, role, reset, policy stream, authentic action count and the original source-public action/consequence SHA256. Each experiment's own 2/4 original jobs agree per episode.

## Independent cumulative reconciliation with R17

Original R17 sources: S4A 16, MR34E 32, MR34F 60, S4C1 held-development 16 = **124** log-derived original episode rows from 14 original native jobs. With R18: **244** row observations from **22** historic native job logs. Deduplicate ONLY by original source family + reset ID + policy stream (not by numeric seed alone): **228 distinct episodes**, accounting for **11,158 authentic native original actions** (one canonical exposure per distinct episode, never multiplied by replica count). **16** identical episode identities overlap between MR34H held-development and S4C1 held-development; every overlapping exact source-public trace digest and action count is identical, **0 contradictions**.

The original P0F-C2 frozen design Git blob `42db4b7e285a1ee0423c219febc6892f76d9e875` contains 40 proposed development reset IDs; their intersection with the 228 recovered episode identities is empty. This evidence only documents visible historical use. It does NOT prove global original-engine seed non-use.

## Missing coverage and mandatory stop

These 228 reconstructed rows are **not** an append-only history from the original time of engine execution. Known omissions include other historical original-source runs, failed/ephemeral attempts, S4C0 per-original-episode detail not available in this record, S4C1 training individual episode receipts (only aggregate available from that job) and original-source histories outside the recorded Actions jobs. Original source-birth authority and completeness of previously consumed resets are **not attested**.

CKB Q11's [qualified fixture-only hash-chain prototype](https://github.com/spoonman136668-ai/ckb-plane/actions/runs/39791559183) demonstrates create-new synthetic mechanics; it is **not a live issuer, global ledger, accepted signed source-birth certificate, or permission to reset any actual engine**. This R18 audit does not retroactively transform historic logs into authorized first-use records.

**Guardrails:** No authentic source engines instantiated or reset during R18; no new actor actions/learner training/evaluation, protocol mutation, scientific thresholds, protected heldout, paid API, main/accepted-ref merge, controller dispatch, workflow trigger, or CKB/FORGE live operations. Prior MR34H Farama generalization NO-GO and S4C1 trained-checkpoint nondeterminism NO-GO remain unchanged.

**Next science gate:** Sole CKB authority to independently establish a **prospective signed source-birth/one-shot reservation** regime and adjudicate missing historical coverage explicitly. If globally exhaustive prior use cannot be proven, `CUSTODY_INCOMPLETE` applies to the previous 40 seed line; use only a separately frozen and approved genuinely prospective lineage. Require original source Git identity, actor/policy identity, seed/role, valid signed authority, pre-reset irreversible consume event, durable third-party head witness, and post-execution source-public digest. No real source reset before that admission.
