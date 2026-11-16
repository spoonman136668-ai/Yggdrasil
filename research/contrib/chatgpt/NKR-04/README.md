# NKR-04 — Source-pinned native evidence-to-weight compiler

**ISOLATED ENGINEERING RESEARCH / NOT ACCEPTED WEIGHTS / SCIENTIFIC UNVERIFIED / NO MAIN OR RUNTIME MUTATION**

## Why this is needed

Yggdrasil already has distinct, unmerged research lines with complementary but **noninterchangeable** evidence:

- WSP-110 PR #1075 programmed one million synthetic sparse relational *fact parameters* and two derived relation layers, tied strong symbolic and trained controls. It is not a language model or accepted native Yggdrasil weights.
- WSP-116 PR #1108 numerically encoded approximately 21.3 million historical real Wikidata **TRAIN triples**, with exact symbolic controls. Those triples are knowledge-graph statements, **not** public native action/consequence outcomes and must not be fabricated into them.
- NKR-01 PR #1092 implemented an actual 16-slot opt-in native contextual weight path. NKR-02 PR #1094 revealed 128/352 **confident wrong** unfamiliar quadratic predictions. NKR-03 PR #1096 added conservative `choose_verified_contextual`, which only changes a decision when **both real action outcomes at that exact context are evidenced**; symbolic/MLP controls were stronger on some public synthetic cases.
- WSP-122 PR #1126 demonstrated dynamic 16-coefficient polynomial growth only on fixture data and tied an independent symbolic ANF control.

**NKR-04 reuses existing NKR-03 native weights** rather than developing yet another weight store, semantic encoder or causal learner. Its contribution is a deterministic, transactional batch intake seam for source records. It cannot turn arbitrary Wikidata triples into causal intervention outcomes.

## Frozen boundary

- Accepted original main: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Parent NKR-03 qualified draft SHA: `9710917f7edb87ed7caebfd01759b50418fdb89c`.
- Preregistration-first SHA: `f3909fc81c6a6b361755798bad8c1bf33cb3c81f`, committed **before** implementation/tests.
- No edits to `yggdrasil/native_relation_memory.py`, `yggdrasil/public_causal_cells.py`, accepted DG-1 architecture or 164-byte YPC1 native checkpoint.
- No original/restricted WSP120–122 source cohorts, historical consumed queries, paid providers, external inference or native owner state touched.

## Interface

`yggdrasil/native_evidence_compiler.py::stage_native_bundle(raw, expected_source_sha256, prior_checkpoint=None)`

Input is an **exact-byte-pinned, canonical ASCII JSON** bundle containing only an `engineering_fixture_only` / `observed_public_intervention` demonstration source, sorted `[slot,context,action,outcome,source_ref]` rows, and at most 512 records. No arbitrary text, knowledge graph triples, inferred counterfactuals, hidden heldout labels or claimed source qualifications are admitted. The license indicator is `synthetic-fixture`—not a claim of licensed real-world causal data.

The compiler restores the optional prior NKR-03 native checkpoint **in a private temporary object**, validates all inputs, programs matching or exceptional consequences through `observe_public_verified`, ignores identical source aliases, rejects conflicting outcomes, then returns a candidate checkpoint and integrity receipt. No global or accepted model mutation occurs; if any row fails, no staged candidate is returned. Cold replay re-verifies the resulting native bytes. The existing `choose_verified_contextual` remains the only conservative native selection path for this candidate.

**SHA-256 matching verifies identity of the bytes against a separately supplied digest—not source truth, intervention reality or approval.** A forged bundle can carry its own matching hash. Therefore this interface deliberately rejects `owner_qualified` input and cannot perform real-world source admission. True external source ownership, timestamp/action provenance, authorization and independent qualification must precede accepting any candidate.

## Development gate

Synthetic PUBLIC fixture fills every existing native relation slot: **16 addresses ×16 visible contexts ×2 actions = 512 unique observations**. The source law includes a pairwise conjunction term so the original NKR-01 affine grammar is insufficient. NKR-03's witnessed exception mechanism preserves those discordant observations. With both outcomes witnessed per context, the existing guarded native chooser must agree with independently coded exact symbolic lookup on all **256 available decisions**.

Additional controls check partial evidence fallback, staged split-vs-single-load byte parity, second-load idempotence, alias duplicates, contradictory updates, tampered prior checkpoints, invalid numeric and Boolean fields, noncanonical or duplicate-key JSON, invented outcomes, graph triple misrouting and capacity overruns.

These tests would demonstrate bounded, non-gradient **native capacity and evidence loading**—not fully populated general knowledge, unseen causal discovery, neural intelligence, source authenticity or a faster method than exact lookup. The 16-slot native capacity remains separate from WSP116's millions of historical facts.

## Engineering qualification

1. Run new and inherited native NKR-01/03 plus entire root suite on the exact source SHA and **Ubuntu + Windows**. Use existing GitHub-hosted runners only.
2. Pin the repository G29 source atlas with the existing builder, changing **only** `.ice/code-atlas.json`, `.ice/code-atlas.ice`, `.ice/code-atlas.html`.
3. Complete mandatory full final regression on the source-identical final commit/tree, and independent G29 check.
4. Do not interpret unrelated proxy automation failures as source or scientific failures. Do not merge/promote on engineering alone.

## Beyond 512 native consequences

A fully equipped knowledge system requires a **typed, provenance-qualified path** from historical structured facts (WSP116), relationships (WSP110/122) and independently witnessed action consequences (NKR03/04) into compatible developmental native modules, with scale, interference, regeneration and unfamiliar-transfer evidence. This is research still to implement. Broad Wikidata facts are *not* interchangeable with 4-bit action contexts; do not silently hash millions of facts into 16 addresses.

Scientific pass requires independently held out and disjoint real new-source families, fully trained conventional models, optimized graph/symbolic controls, matched actions/compute, cold retention/interference, whole-process cost and separately qualified Yggdrasil-native admission. Preserve null results and negative safety findings.
