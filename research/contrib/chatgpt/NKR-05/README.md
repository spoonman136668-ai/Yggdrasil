# NKR-05 — Populate the entire historical training knowledge foundation

## Objective

Stage **every one of the 21,343,681 historical Wikidata5M-variant training triples** (not a sample, not 16 causal slots) into a cold-restorable, typed native numeric factual memory. Provide direct evidence lookup and bounded two-hop compositional *hypotheses* for Yggdrasil's future developmental cognition.

**Research branch and model image only. No acceptance into current `main`, owner/controller changes, scientific first-use or deployment.**

### Reuse, not reinvention

- Original historical CC0 structured TRAIN source, archive and train SHA from WSP-102, WSP-103 and WSP-116. It is a noncanonical **historical variant**, not newly/currently verified facts. Prior WSP-103/104/105 masks and WSP-116 query evidence have already been consumed. NKR-05 uses the **complete TRAIN source**, including those previously consumed training groups; thus it cannot reuse prior heldout/DEV results as fresh science.
- WSP-110 programmed 1m synthetic fact parameters; WSP-116 demonstrated native-*external* integer storage of 20,677,636 *masked* historical TRAIN triples. Neither populated a permanent/accepted Yggdrasil native model.
- NKR-04 is a distinct **actual-action-consequence** native intake with 16 slots; arbitrary Wikidata `Q/P/Q` predicates do not map into those four-bit action fields. This new module adds a separate **typed factual memory** rather than flooding NKR-04 with fake evidence.

## Implemented factual representation

- `yggdrasil/native_factual_weights.py::NativeFactualWeights` memory maps a sorted little-endian `(uint32 Q-subject, uint32 P-relation, uint32 Q-object)` stream, **12 bytes per original TRAIN triple**. Full planned output is **256,124,172 bytes / 64,031,043 numeric slots** and 828 real historical relation IDs.
- The source is externally sorted in bounded 500,000-record chunks by `research/contrib/chatgpt/NKR-05/build_full_image.py`, preserving duplicate source rows and every original TRAIN row. Binary search gives exact `has_fact` and bounded paginated `objects(Q,P)` retrieval without loading the entire dataset into heap RAM. Two-hop paths return clearly marked **UNVERIFIED_PATH_HYPOTHESES**, never automatically learned facts.
- `manifest.json` pins the original train SHA, archive SHA, 21.3m source count, all sorted content bytes, duplicate count, numeric slots and image checksum; `receipt.json` records exact full cold restoration. `NativeFactualWeights` requires an independent exact manifest SHA pin and checks all image bytes before querying.
- No ontology/English labels are synthesized; Wikidata `Q` and `P` integers are opaque typed identifiers. Literal fact memory is **not** a trained neural model and cannot claim causal understanding, relationship-category invention or general intelligence.

## Source and first-use fence

Source archive URL: `https://web.informatik.uni-mannheim.de/pi1/kge-datasets/wikidata5m.tar.gz`; exact archive SHA-256 `ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878` (174,515,774 bytes). **Only** archived `wikidata5m/train.txt` content may be read. Exact train SHA-256 `2ef1a279f6393a8edfbb2b44114a2c97944272e5fe2a1bd2a7cbe48f94742f1a`; train bytes 436,189,882, rows 21,343,681, predicates 828. `valid.txt` and `test.txt` may be checked for sealed member *names/sizes*, **never their data**. This source has previously been used; this is a nonindependent engineering materialization, not novel first-use.

Source custody helpers and parsers are reused from WSP-102/WSP-103 byte-for-byte. Mismatched source counts, SHA, format, duplicate tar members, external redirects, file types, archive size or output integrity fail closed. The source is downloaded once per approved single-run materialization; no paid APIs.

## Engineering qualification

1. Preregistration-first SHA `90be3e856b72b5ac1ac43e3bcffce0eb3d9432e4`, from NKR-04 qualified source parent `e0ed191cc8dc2b4dd62dd1d6836fa7fb0309500c`; original `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
2. Synthetic fixture only: full chunked sort, cold mmap and exact membership vs independent Python tuple set, duplicate preservation, grouped sorted query, source provenance, two-hop candidates marked hypothetical, source inventory mismatch, bad Q/P identifiers, noncanonical manifest, unapproved accepted-state claim, corrupted binary and refused overwrite.
3. New+inherited root suite and G29 source index preflight Ubuntu/Windows at exact source candidate, then one-shot original historical TRAIN **already consumed source** materialization on existing GitHub-hosted Ubuntu, **only after mandatory preflight success**. Run root regression again on same exact source SHA after materialization.
4. Full binary image is too large for Git source. The source-safe job uploads the exact `facts.uint32le`, `manifest.json`, and `receipt.json` as a bounded **GitHub Actions build artifact**, with 30-day expiration. Artifacts are not automatically installed, accepted or durable model checkpoints; before expiry an owner-approved persistent artifact store/native activation is needed.
5. No NKR-04 native causal store edits, DG1 developmental model updates, accepted-ref mutation, autonomous controller/runner/scheduler changes, merge, real-time knowledge downloads or scientific first-use.

### Reproduce from source

```bash
python -B -m unittest discover -s research/contrib/chatgpt/NKR-05 -p 'test_*.py' -v
python -B research/contrib/chatgpt/NKR-05/build_full_image.py --historical-train-only-full-image --output /tmp/nkr05-full-train
python -B -m unittest discover -s tests -p 'test_*.py' -v
python -B scripts/build_code_atlas.py --check-if-present
```

**Scientific interpretation:** Source-grade engineering storage and retrieval, not a new intelligence proof. Native cognitive admission must still test interpretable semantic grounding, interference/retention, independent unknown-relationship discovery, provenance-verified action consequences, conventional neural/optimized symbolic equal-information controls, matched whole-process cost and separately authorized accepted native integration.
