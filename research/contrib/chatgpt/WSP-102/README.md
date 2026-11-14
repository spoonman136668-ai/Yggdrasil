# WSP-102 — largest-first real structured knowledge, source-custody gate

**Research status:** real-world archive metadata only, no training, no original scientific first-use, no evaluation labels read and no model promotion.

Wikidata5M is a historical, Wikidata-derived graph with **4,594,485 entities, 822 relation IDs and 20,614,279 transductive training triples** (publisher: https://deepgraphlearning.github.io/project/wikidata5m). These are genuine catalogued relationships, not the earlier generated four-function simulation. Statements may be outdated or disputed; this is not a live factual authority for November 2026.

The initial input will be an independently hashed third-party benchmark archive, not the roughly 40–100GB Wikimedia official dump. The first run **must only** download within a 256MiB compressed bound and enumerate TAR paths and sizes. It MUST NOT read graph rows, build models, score a heldout target, or use the WSP101 reserved cohorts. The source SHA256 must then be frozen before any further data access. The checked-in preregistration is `prereg.json` and was committed before any code at `94d7e527b2122722c998c0de627543ab6ec0270f`.

When licensed data provenance, transport and member names are verified, the next step is a separate preregistered 20M-triple memory/association experiment with full-graph first and fixed 5M/1M/250K fallback budgets. It must compare against **exact symbolic graph storage and fully trained neural graph learners**, preserve multivalued facts, and test heldout entities, multi-hop reasoning, contradictions, cold retention and total process cost. Simply storing or retrieving relations is not AGI.

Underlying Wikidata structured statements are CC0. **Do not** ingest aligned Wikipedia text/images as though they were CC0. This branch has no privileged controller, queue or scheduler interactions, no paid API, and does not touch main or the accepted Yggdrasil model.

## Frozen real archive obtained (metadata-only)
- Original one-shot source custody [run 43626313760](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43626313760) PASS; 174,515,774 compressed bytes, SHA256 `ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878`.
- Allowlisted members: `wikidata5m/train.txt` 436,189,882 bytes; `valid.txt` 109,498; `test.txt` 108,932. Source compressed archive and exact member paths pinned in `source_seal.json` at `8773288fe8152d23686eb216e5a22e83b875de7c`, BEFORE any graph row read.
- Next one-shot read is **training member ONLY**, checks all 20,614,279 claimed training rows, 822 relation types, exact SHA256 of training content, entities and source distribution. It NEVER reads official validation/test contents, fits learner weights, or evaluates science. All raw data ephemeral on CI runner, no repository/LIBRARY storage.

## Wide real-world TRAIN-memory engineering result (not AGI proof)

Frozen source variant: `HISTORICAL_VARIANT_SEAL.json` (real archive training rows **21,343,681**, relations **828**, not the original published 20,614,279 /822 Wikidata5M benchmark; heldout sets untouched). Published-count mismatch preserved in `SOURCE_COUNT_NEGATIVE.json` and [original failed count run](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43626765368); actual row and relation counts verified independently in [reconciliation run](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43627376935). All source archives are read-only and separately SHA-pinned.

- Before any numeric weight write, frozen `weight_capacity_prereg.json` in `e5e4a38ea0997e7fba0a4bef735b33518e7bc490`.
- [Original real full-width numeric write run 43627988006](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43627988006) **ENGINEERING PASS**: **21,343,681 source facts** ×3 little-endian uint32 weights = **64,031,043 numeric slots / 256,124,172 bytes**. Exact cold-restored first half **128,062,080 bytes**; original half, final packed memory and raw training input independently hashed.
- Source-to-weight encoding **50.14 seconds CPU / 50.14 seconds wall**; complete download, parse, encoding and cold verification **62.98 seconds wall** in original CI run.
- No validation/test triple truth read, real unknown fact prediction, semantic language understanding, learned knowledge transfer, genuine interference test or conventional/symbolic full-cost comparisons occurred. This is **known-fact numeric storage**, not a scientific claim of increased intelligence or a gradient-free learning speedup. A comparably packed symbolic triple store could take 12 bytes per relation as well.

**Next scientific work (not executed):** Independently preregister fact-query indexing and multi-hop association, heldout entity/property generalization, contradiction repair and old-skill retention, plus equally informed exact symbolic graph lookup and fully trained conventional graph learners. Avoid using benchmark published test scores with this 828-property historical source variant.
