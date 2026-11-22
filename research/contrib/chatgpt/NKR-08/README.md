# NKR-08 — Cumulative native factual memory, without rewriting the base

**Engineering successor proposal — isolated research only. Not independent scientific gain, native acceptance or owner deployment.**

## Why

NKR-05 produced the already verified **21,343,681-row** historical Wikidata5M-variant Q/P/Q factual image (828 predicate types, 256,124,172 immutable bytes). NKR-06 proved the exact image is queryable through a read-only native research session; NKR-07 provided an owner-side installer for an expressly authorized persistent destination. None of those stages modified accepted DG-1/Yggdrasil main or demonstrated cumulative fact acquisition.

**NKR-08 addresses cumulative retention.** It adds an isolated, **append-only developmental observation ledger** beside the complete historical image. No historical knowledge is re-encoded, compressed away or rewritten. New source observations may extend queries; historical facts remain the source of truth for exactly matching triples. Source-based duplicates are recognized and not duplicated in the delta, while distinct evidence references remain auditable.

The source of the new facts is **public SYNTHETIC engineering fixture data only**. A user-provided SHA verifies exact bytes, not that observations actually occurred. No generic `verified=True` parameter, no owner-certified or unverified public data ingestion route, no permission to invent actual facts from two-hop paths, and no interface for writing Wikidata triples into NKR-04's native action-consequence bank.

## Architecture

`yggdrasil/native_cumulative_facts.py::CumulativeNativeFacts` accepts a **fully verified NKR-06 NativeKnowledgeSession** with exact pinned source manifest `aa2d56e72284a042aee72587028642110327307b483de667586f105f018ebe8f`. No path guessing, model mutation, installer launch or background activity.

`stage(canonical_bundle_bytes, caller_pinned_bundle_sha256)` returns a **new** candidate and a deterministic receipt: original session and prior candidates remain unchanged. Each typed `[Q,P,Q,source_ref]` is bound to a unique evidence identity. An existing source_ref cannot refer to a conflicting fact; identical retransmission is idempotent. The new candidate's canonical versioned checkpoint includes the immutable base SHA, bundle digests, all direct observations and flags `scientific_pass=false` and `native_admission=false`. Restoration **requires the independent external checkpoint SHA** and exact canonical replay. SHA tamper checks do not establish source authenticity; this is a development-only evidence boundary.

Calls are read-only:
- `fact(Q,P,Q)` returns historical known fact, separately labeled developmental direct observation, or unknown abstention.
- `objects(Q,P)` performs bounded combined lookup against historical base plus candidate facts without changing the original 21.3-million-fact image. Historical triples are preferred and deduplicated.
- `hypothesize(Q,P,P)` composes two explicitly supplied relation IDs and labels results `UNVERIFIED_COMPOSED_PATH_HYPOTHESES`; such path outputs are **not** admitted as facts or native causal observations.

### Frozen development experiment

NKR-08 prereg **FIRST** `d5a6cecb7dc4f37fbb05e081810ce18d3ac33c75`, parent NKR-07 final `efd0059f93b30072757c796eb905ec4d6e7609b3`; native main remains `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.

Fixture input consists of a protected **128-fact historical-like base** and two sequential phases of **128 novel typed direct observations each** (256 new). Phase two additionally contains 32 repeat facts from phase one and 32 already present in the original base, all with unique source_ref provenance. Expected candidate report: 128 new after phase 1; **256 nonduplicated new facts retained after phase 2**, 64 source-backed duplicates counted but not reprogrammed. Original 128 remain unchanged, totaling **384 unique supported source facts**. No heldout real Wikidata/benchmark or first-use science is touched. With source-equal information an independent optimized Python exact symbolic set is expected to tie exactly on membership and all supported two-hop compositions; a tie is **not** proof of superiority or learned generalization.

The negative cases freeze source-ID rebinding, conflicting evidence references, unsupported model-inferred or graph-composed input, self-attested real/owner-qualified data, source SHA mismatch, tampered checkpoint, duplicate JSON fields, invalid Q/P/Q types, oversize, source order, bad base manifest, unchanged YPC1 counters, and unknown abstention. Checkpoint retention and deterministic restoration are qualified across Ubuntu and Windows.

## Qualification and limits

Use the existing GitHub-hosted source-safe workflow; only if focused and inherited NKR-05/06/07 tests pass, regenerate exactly three `.ice/code-atlas.*` files once, then execute the mandatory full **root regression on the exact final SHA/tree on both Windows and Ubuntu**, separately run independent G29 checks. No original image re-download, no new runner or scheduler, paid inference, live source first-use or accepted ref change.

**Interpretation:** NKR-08 is developmental **cumulative memory plumbing and a reproducible retrieval experiment** over a fixed source format, not genuine autonomous novel-relation discovery, semantic language understanding, trusted external factual updating, a new neuronal trained state or permanent accepted owner installation. The base architecture remains independent, native, non-transformer and non-token. A separate independently frozen authentic-source learning evaluation must measure how a model uses this memory for causal reasoning, cold retention, interference, transfer and total cost against fully trained and symbolic controls before any scientific promotion.

The original [full historical source artifact #14220169461](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43856374741/artifacts/14220169461) expires **2026-12-16**. A later owner deployment still requires verified permanent storage and Yggdrasil owner acceptance; this PR cannot supply those permissions.

## Additional full-image engineering corroboration (not new science)

The focused development fixture checks 128 historical-like base facts plus 256 two-phase synthetic additions. Before final qualification, use the **previously published original NKR-05 artifact once** to run `qualify_real_image.py` after both OS full-root and G29 tests pass. This source is **already consumed**, so such an extra proof is only an engineering cross-check, not a newly preregistered independent scientific result.

The GitHub-hosted Ubuntu job must verify immutable GitHub artifact identity/digest/run SHA and use `gh run download` to retrieve the existing 256 MB binary **without downloading/rebuilding its historical training source**. It may install to *temporary runner storage only* using the already-qualified NKR-06 installer and cold-open the complete 21,343,681-row image. It then source-free stages 128 + 128 entirely **synthetic** new observations into a separate NKR-08 overlay, detects 32 repeated phase-one facts and 2 duplicated real historical records without writing to the base, retains the original first/last facts, preserves 256 exact-match fixture records, independently checks 128 compositional paths and cold-restores the cumulative candidate. Afterward rerun full tests on the same exact source SHA, and upload **only a small receipt**, not another 256 MB artifact.

This extra evidence is explicitly **not an independent real-world knowledge-learning or original-science outcome**. It does not install anything on the owner workstation or validate first-use, source truth, learned semantics, discovery or accepted native state.
