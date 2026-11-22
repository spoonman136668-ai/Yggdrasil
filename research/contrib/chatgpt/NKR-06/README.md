# NKR-06 — Offline activation of the real 21.3M historical-fact image

**SOURCE-SAFE DEVELOPMENT. ISOLATED READ-ONLY RESEARCH SESSION. NO ACCEPTED MODEL ADMISSION OR AUTONOMOUS CONTROLLER CHANGE.**

The complete numerical factual image **already exists**, sourced from NKR-05 PR #1129, exact final SHA `c4b4e97726f6541197913ad405a47d4c4019a3cf`. Do **not** run the historical source generator again to qualify this gate.

## Why

NKR-05 built and cold-verified **21,343,681** full historical Wikidata TRAIN facts, **828** predicates, **64,031,043** numeric `uint32` slots, **256,124,172 bytes**, but supplied an *expiring GitHub Actions artifact*, not an owner-persistent local installation or an activated Yggdrasil knowledge interface.

This successor addresses the next engineering issue: load exactly those already-qualified bytes into an **explicit offline read-only Yggdrasil knowledge session** with a safe, no-overwrite local installation. It does not convert Q/P/Q triples into 16-slot NKR-04 causal action records or claim original scientific transfer.

## Pinned immutable source

- NKR-05 source SHA `c4b4e97726f6541197913ad405a47d4c4019a3cf`, tree `69d0999c64175a10178539ab0099239b4590ac20`. Accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Original artifact: [GitHub run #43856374741, artifact ID 14220169461](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43856374741/artifacts/14220169461), expires **2026-12-16**. Artifact ZIP SHA-256 `c7265cabac91b8762fb5d65209eef44fa79a8fbf3d9a6f61300ef60ded0a5275`.
- Canonical manifest SHA-256 `aa2d56e72284a042aee72587028642110327307b483de667586f105f018ebe8f`.
- Full packed image SHA-256 `6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1`.
- Frozen historic source TRAIN SHA-256 `2ef1a279f6393a8edfbb2b44114a2c97944272e5fe2a1bd2a7cbe48f94742f1a`; archive SHA-256 `ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878`.
- Preimplementation prereg FIRST `d9ccbc8b22bb4b3e6ff502532af093ae7b753a8a`.

## Native offline access

`yggdrasil.native_knowledge_activation.install_offline_image(source_directory, destination_parent, name)`

Consumes **only an existing local artifact image** (`facts.uint32le` + `manifest.json`) against the **hard-coded exact trusted NKR-05 bytes/rows/predicates/source identity**. Creates a fresh, non-overwriting directory with image+manifest+activation receipt and rejects any missing, malformed, forged, tampered or unrecognized image. The caller owns the storage location. No accepted model mutation, background download, network access, API calls, tokenization, native intervention, credential, new scheduler or hidden data read occurs.

`open_installed_session(path)` independently validates receipt and cold full-image SHA-256. Session offers `fact(Q,P,Q)`, `objects(Q,P)`, and source-supported two-hop `hypothesize(Q,P,P)`. It distinguishes verified **historical source records** from `UNKNOWN_ABSTAIN` and `UNVERIFIED_PATH_HYPOTHESES`; none are qualified as new causal evidence, current fact, model learning, or accepted intelligence.

Native code continues to preserve the existing NKR-03/04 `PublicCausalCells` behavior and the legacy 164-byte YPC1 checkpoint, and never writes graph propositions as observed environment consequences.

## Full artifact rehydration gate

1. Run source-free test suite with small fabricated pin fixture and tamper/no-overwrite/rollback negatives on Ubuntu and Windows; retain the original 21.3m frozen image untouched.
2. Generate exactly the three source atlas files using the repository G29 builder (single pinned-source job), then full **mandatory root+focused** regression and independent G29 on the exact final SHA/tree on Ubuntu and Windows.
3. Once those pass, GitHub-hosted Ubuntu retrieves **artifact ID 14220169461** from immutable original run **43856374741** using read-only GitHub Actions permissions and checks origin-run SHA, expired state, file count, manifest and full binary hash. It executes the *same offline installer* on a new local temp folder, cold-opens the entire 21.3m fact image, tests real first/last recorded source triples, unknown query abstention and source provenance, then reruns the final root regression.
4. Store a small exact-source activation receipt only; do **not** upload a duplicate 256 MB binary or redownload the historical external original. Avoid duplicating expensive previous WSP112/116 science experiments.

The GitHub-hosted runner's temp directory is **ephemeral**, so a successful proof is not a permanent installation into the actual Yggdrasil owner/workstation. Owner-approved real persistent storage and accepted native activation are separate. No scientific first-use or promotion has been authorized, and the original artifact expiry is not extended.

## Practical interface

After a human or separately authorized owner workflow supplies the original pinned artifact bytes in an approved local directory, the already-tested installer runs:

```console
python -B -m yggdrasil.native_knowledge_activation --source /owned/staged-NKR05 --destination-parent /owned/persistent-Yggdrasil --name historical-train-facts
```

This command is **not executed on your workstation by this PR**. Existing native knowledge session code can open `/owned/persistent-Yggdrasil/historical-train-facts` directly in read-only mode. No persistent location can be inferred, and no controller should auto-consume it.

**Scientific interpretation:** Demonstrates offline knowledge availability and provenance fences, not autonomous discovery, language understanding, transfer, or superior cost/performance. Research remains isolated until a real source-qualified independent acceptance decision.
