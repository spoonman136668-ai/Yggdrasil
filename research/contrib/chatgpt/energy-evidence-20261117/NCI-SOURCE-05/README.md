# NCI-SOURCE-05 — Historical native-admission guard compatibility

**2026-11-19 · Independent Yggdrasil research contributor · ENGINEERING_READ_ONLY_PASS / SCIENTIFIC_UNVERIFIED.**

## Core finding

Read-only GitHub-connector retrieval and deterministic field inspection of **17 unchanged SHA-pinned historical Amalgam development JSON traces** at [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), source commit `86264b41a08d49f558418c0fba367f3a2636befa`, found **2,456/2,456** structured public episode rows satisfy both the binary format and proposed NCI-SOURCE-03 consistency guard: `row["s1"] == views[0][0] == views[1][0]`. **0 contradictions**. Every one of the 17 GitHub-returned source-file Git blob identities matched its manifest identity.

| Archived group | Files | Records matching |
|---|---:|---:|
| Causal templates | 3 | 288 / 288 |
| Curriculum start | 3 | 576 / 576 |
| Open set | 3 | 288 / 288 |
| Selection | 1 | 96 / 96 |
| Staged retention | 3 | 216 / 216 |
| Transfer curve | 4 | 992 / 992 |
| **Total** | **17** | **2,456 / 2,456** |

These are *historical archived development* traces, **not** 2,456 independent scientific trials and **not necessarily 2,456 accepted model writes**. The curriculum and transfer traces also include held and test entries. Counts are input-schema compatibility evidence only; there were **zero new source actions or retraining steps** in this gate.

The Amalgam `NativeCausalAmalgam.observe_experience` entrypoint Git blob `287e6fbb9d1f9612f88f9d5ed5dda88be4bb7952` currently checks paired-view initial-state consistency **after** native append and duplicate early-return; it does **not** verify `row["s1"]` agrees with the two views. In `NativeEpisodeExperience.observe` Git blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`, the admitted event omits the validated `s1` field and derives its initial state from the first view. This previous NCI-SOURCE-02/03 failure remains real as an *input contract gap*.

The proposed minimal entry guard preserves the record values in all these historical traces. **It has NOT been installed or executed through the actual full multi-MB model/checkpoint restore.** No accepted model code or weight/owner/ledger is modified. The earlier NCI-SOURCE-03 and NCI-SOURCE-04 isolated source/fixture tests are separate; their cases are not included in today's counts.

## Deterministic reproduction

`manifest.json` pins all 17 historical Git blob SHA-1 values, exact row counts, research commit and the two native source identities. The pure standard-library **read-only** `verify_historical_input.py` reconstructs the same check from a clean, exact detached checkout:

```sh
python -B verify_historical_input.py --source-tree /path/to/clean/Amalgam-86264b41
```

It rejects dirty/wrong-SHA checkouts, mismatched file blobs, unknown trace schema, invalid event IDs/bit fields, inconsistent `s1` versus public views and unexpected row counts. The script itself was authored for this gate; GitHub static readback and the prior direct connector audit are the measured evidence here. Do not imply that running this script against a clean external checkout, full native code, or native cold restoration has already been demonstrated.

## Precise integration handoff / owner boundary

- **Native research integration seam:** `NativeCausalAmalgam.observe_experience` first-statement guard, before `NativeCumulativeLearner.observe_experience` and before duplicate return. `StagedPublicReadout.observe_reward` already produces `s1` from views; other existing historical trace producers also conform on the inspected cohorts. Do not rewrite `NativeEpisodeExperience.observe` globally; other legitimate callers and projections may differ.
- **Central coordinator:** the *Unified Causal Intelligence Amalgam Work chat* alone can decide installation after owner-host checkpoint authentication, complete old/new/return cold restoration with source-packet/duplicate/tamper controls, full final Linux+Windows regression, and independent source-first-use authority. [LINEAGE01 #1322](https://github.com/spoonman136668-ai/Yggdrasil/pull/1322) owns checkpoint custody and [source-owner issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) remains PROTECTED FIRST_USE_BLOCKED.
- **Research disposition:** ENGINEERING archived-input compatibility PASS; full native runtime and checkpoint restore UNVERIFIED; SCIENTIFIC causal learning/retention/transfer improvement UNVERIFIED; DEPLOYMENT NONE. This is a contribution to the existing Yggdrasil repo, **not** another learner or model integration. Preserve older ENERGY NO_GO results.

**Do not** claim a score improvement from deleting malformed inputs. Valid input preservation is a safety condition, not a learning result.
