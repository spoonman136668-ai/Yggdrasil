# NKR-07 — Owner-explicit persistent installation of the existing full knowledge image

**Objective:** Provide the missing end-to-end **installation mechanism** for a caller-owned durable filesystem without guessing where Yggdrasil's actual owner keeps model state or crossing its acceptance boundary. The real 21,343,681-record knowledge image is **already built** in NKR-05 and was successfully read and installed on a temporary test machine in NKR-06. Do not download/rebuild the historical dataset again.

## Pinned source, not a new dataset

Existing historical source Q/P/Q snapshot, **21,343,681 records, 828 predicates**, original archive and TRAIN hashes were qualified at [NKR-05 run #43856374741](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43856374741). The exact image (256,124,172 bytes) is in [GitHub artifact 14220169461](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43856374741/artifacts/14220169461), ZIP SHA256 `c7265cabac91b8762fb5d65209eef44fa79a8fbf3d9a6f61300ef60ded0a5275`. **The original artifact expires 2026-12-16.** SHA-pinned manifest `aa2d56e72284a042aee72587028642110327307b483de667586f105f018ebe8f`; exact image SHA `6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1`.

The qualified offline native read-only research session is NKR-06 [PR #1131](https://github.com/spoonman136668-ai/Yggdrasil/pull/1131), source `3510870b9cde9870f055a49c9eb72ccb1a9ef671`. That research module never alters native DG-1/causal owner state, and the existing main accepted model remains `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.

Preimplementation prereg NKR-07 FIRST SHA `7e82dea6e53d430c4fb878853f192a20ac792914`.

## Owner-side installer (only when independently authorized)

`scripts/install_owned_historical_knowledge.py` adds a single **explicit** command, no defaults for storage location and no background execution. It uses preexisting `gh` CLI authentication to fetch and verify GitHub metadata for **the original artifact ID only**, insists on its original run, original source SHA, fixed ZIP digest metadata, exact name/byte size and nonexpired status, and downloads that previously built artifact into a temporary staging directory.

After requiring exactly `facts.uint32le`, `manifest.json` and `receipt.json`, the installer calls the existing NKR-06 `install_offline_image`. That validates the **complete** 256.1 MB binary against the immutable full-image SHA, verifies original historical 21.3m source rows and 828 predicates, creates a **new non-overwriting** directory within the caller-specified owned parent, copies and cold-verifies the knowledge, and publishes the validated installation receipt. It then cold-opens and checks first/last real historical facts and unknown abstention. Any failure closes without installing a model, rewriting prior weights, changing main or launching a controller. The human/owner decides whether and where the image persists; source code and GitHub CI do not.

Example for a separately approved owner-controlled environment (NOT RUN IN THIS PR):

```powershell
python -B scripts/install_owned_historical_knowledge.py --owner-persistent-parent "C:\\Approved\\YggdrasilKnowledge" --name yggdrasil-historical-facts
```

This example path is illustrative, **not** a discovered or authorized real owner directory; never execute it as an instruction without verifying the actual owner-selected path and permission. The parent must exist, be owned and be free of an existing target directory. Requires GitHub CLI `gh` logged in with read access to this private repo; never prints credentials.

## Scientific and operational boundaries

The materialized knowledge is **factual historical Q/P/Q numeric memory**, not a transformer or token core, current-world ground truth, a causal observation stream, a fully trained neural embedding or proof of autonomous relation invention. The read-only research API can retrieve historical facts and generate clearly marked unverified path hypotheses. No direct acceptance into production native DG-1 and no bridge of Wikidata facts into 16-slot action/consequence memory.

This gate does **not** copy the artifact into ChatGPT Library, make a GitHub release, fork a new repository or allocate an additional scheduler or controller. It does not configure an unidentified private runner or modify the owner's live workstation. No automatic artifact replication or expired replay. No hidden scientific first-use.

## Acceptance plan

- Source-only development tests for pinning, GitHub metadata authorization boundary, expired artifact, staged source full manifest and packed SHA, fail-closed source invalidity, atomic no-overwrite, unknown abstention and no model mutation — Ubuntu and Windows.
- Only if dev PASS: regenerate exactly three G29 `.ice/code-atlas.{json,ice,html}` derived files, then **full final existing root regression**, NKR-05 source-safe suite and independent G29 both OS at exact candidate SHA/tree.
- **Do not rerun the 256 MB artifact experiment:** NKR-06 already proved full-source rehydration on an isolated GitHub runner with original artifact. NKR-07 is a source-safe owner-side installer enhancement and no owner path has been supplied.
- The deployment and durable storage gate remains **UNVERIFIED** until an authorized native owner picks its persistent directory, executes this installer on that owner path, verifies its readback and explicitly authorizes the accepted model integration. CI engineering green is not deployment authority.

No user action is needed for source-safe engineering qualification. A genuine owner-approved permanent installation cannot be inferred or declared from GitHub-hosted fixture tests.
