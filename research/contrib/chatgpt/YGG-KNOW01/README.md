# YGG-KNOW01 — existing cumulative learner knowledge-capacity audit

**Date:** 2026-11-19  
**Purpose:** establish exactly what learned/stored knowledge and capacity already exist in the recovered experimental Amalgam checkpoint before proposing new factual or causal knowledge ingestion. This is a **read-only reviewer contribution**, not a new model, data source, owner, or training line.

## Provenance and exact starting state

- Accepted `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` (still not a verified canonical continuously trained owner checkpoint).
- Amalgam research implementation: [draft PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), source SHA `86264b41a08d49f558418c0fba367f3a2636befa`.
- Original saved Linux/Windows historical research states: [run #44499793023](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44499793023); Linux artifact ID `14517860401`, Windows artifact ID `14516669671`.
- Linux ZIP SHA-256 `b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d`, nested joint-state SHA-256 `576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8`.
- Windows ZIP SHA-256 `bb2b689f84caf939b76bea669eff7efb26506b602eed81ac79a81b42efb0a5a6`, nested joint-state SHA-256 `65b22e284b94fe022fb6345757e364e1a44f8156edf7f081e1b7420e5561f454`.
- The **actual** native and property state SHA-256 match across both systems: native `5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d`; property `dadbb9bb762a24377e50a037eac3e79b0bebe96475ac94a885f7ca409d466377`. Joint bytes differ due to floating-point specialist values; no equivalence is claimed beyond the verified native/property bytes and the pre-existing archival tolerance audit.

`knowledge_capacity_audit.py` parses only explicitly supplied, checksum-pinned historical artifacts and reports limited metadata. It does **not** automatically search the owner machine, upload or publish model weights, invoke any model, execute a data source, alter weights, create a checkpoint, or claim source truth. `knowledge_capacity_result.json` contains **aggregate counts/hashes only**. The two ZIPs and their raw checkpoint contents are intentionally **not committed**.

## Findings (direct readback, not a hypothetical capacity calculation)

Both Linux and Windows snapshot records have:

| Field | Value |
|---|---:|
| Entity capacity | 10,000 |
| Property bits per entity | 10 |
| Explicit known property positions | 100,000 |
| Unoccupied known/value bit positions | **0** |
| Fully known entities | 10,000 |
| Property source bundles | 1 |
| Nondefault relation-source slots | 2 of 16 |
| Existing causal witnessed episodes | 1,025 |
| Persistent trained specialist heads | 4; 2,109 gradient steps each |

**The properties are synthetic, not real factual understanding.** The exact property namespace is `ckad01-synthetic:101` and its source mode is `engineering_fixture_only`. The learned native relationship hypotheses and causal action ledger are distinct states. Saturation is **specific to the 10,000×10 property known/value planes**; it does not mean all model memory, relation slots, or episode headroom are exhausted.

The separate historical Wikidata numerical image in [NKR-08 #1135](https://github.com/spoonman136668-ai/Yggdrasil/pull/1135) has 21,343,681 train historical fact triples and 828 relation IDs. That data is stored in a different research subsystem and is **not part of these Amalgam property planes**, and the existing NKR-08 incremental candidate overlay allows only `engineering_fixture_only` synthetic staging. An arbitrary `(subject, predicate, object)` triple is **not** an observed action/consequence witness; source checksum is not a real-world custody attestation.

The already frozen Amalgam `curriculum-start-dev-01` tested 32+32 staged synthetic episodes against shuffled exposure and fully fitted controls. Result **DEV_NO_GO** (gradual order underperformed the shuffle by 0.01411 mean changed Brier and missed retention on 2/3 seeds). Do **not** rerun consumed cohorts as new science merely to try smaller increments.

## Engineering implication and safe next work

**Do not append a second corpus into the existing occupied property-bit addresses.** Do not overwrite or relabel the synthetic values as real concepts, and do not rewrite an archived, unaccepted checkpoint as the canonical owner state.

The smallest coherent next *implementation proposal* is a bounded, source-qualified **typed factual knowledge interface** to the existing Amalgam: retain the current native and four specialist checkpoints byte-identically; reuse the NKR-08 historical numerical image and its source-provenance ledger rather than rebuilding 21 million triples; separate witnessed direct facts from inferred paths and causal action evidence; use namespaced/typed queries and abstain when a real-world entity/predicate has no authenticated grounding into the Amalgam's numerical public view. Only directly witnessed and independently owner-qualified interventions may change causal weights. A later checkpoint version must preserve previous native witnesses, property source identities, specialist weights and verify cold restoration and idempotency.

The next experiment should be **small and falsifiable**: a disjoint licensed/sourced batch with a source-to-native feature mapping admitted by its owner, then matched factual retrieval/composition controls, source-independent action/consequence tests and retained old-task readout on the *same* verified model, with frozen thresholds and budgets. A known-fact lookup tie against exact symbolic retrieval is not a scientific gain. Owner custody and original-world first-use restrictions ([issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426)) remain in force.

## Reproduction

Download the exact historical Linux and Windows artifacts identified above using the existing authorized repository access. Do **not** commit the ZIPs to the repository. Run locally:

```sh
python -B research/contrib/chatgpt/YGG-KNOW01/knowledge_capacity_audit.py \
  --linux LINUX_ARTIFACT.zip \
  --linux-archive-sha256 b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d \
  --linux-joint-sha256 576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8 \
  --windows WINDOWS_ARTIFACT.zip \
  --windows-archive-sha256 bb2b689f84caf939b76bea669eff7efb26506b602eed81ac79a81b42efb0a5a6 \
  --windows-joint-sha256 65b22e284b94fe022fb6345757e364e1a44f8156edf7f081e1b7420e5561f454
python -B -m unittest discover -s research/contrib/chatgpt/YGG-KNOW01 -p 'test_*.py' -v
```

Local code-only unit qualification **9/9 PASS** (negative controls include false owner-source laundering, tampered hash, invalid property masks, duplicate JSON keys, malformed specialists, cross-platform state drift and archive mismatch). Main repo dual-platform final regression is a separate gate; do not call it PASS before CI completes.

**ENGINEERING:** archived facts directly inspected + bounded reproducible audit PASS locally; final cross-platform qualification tracked separately.  
**SCIENTIFIC:** no new run, no new knowledge learned, original Amalgam DEV_NO_GO remains, `SCIENTIFIC_PASS=false`.  
**DEPLOYMENT:** none; no merge, accepted or active owner mutation, paid API, new scheduler, or source-first-use.