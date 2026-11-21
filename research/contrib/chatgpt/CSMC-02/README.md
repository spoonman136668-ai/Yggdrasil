# CSMC-02 — exact two-stage state + eight-witness provenance cache

**Verdict:** focused readout engineering **PASS (8/8 local Linux Python 3.13.5)**. Predictive gain over the conventional compact control **ZERO**. Original native learner update, full Linux/Windows regression and scientific improvement **UNVERIFIED**. **No promotion or merge.**

## Why this successor

PCER-02 selected 10/50 experiences and changed four of ten native action choices. CSMC-01 covered 15/15 observed terminal cells with 20/50 experiences and preserved all ten choices, but missed both registered forecast-fidelity limits. Both are frozen development results, not accepted research.

CSMC-02 is a **readout-only mechanism snapshot**, not a replacement cumulative learner. It copies the original 50-FIT native two-stage causal counters, exact prequential losses, and projection, alongside exactly eight early original witness IDs/outcomes and the original source archive digest. It reuses original NativeEpisodeExperience.forecast/propose code for inference; it does not learn, silently replay, repair or mutate the accepted checkpoint.

## Results and comparable controls (50 *previously consumed synthetic* FIT only)

| Mode | Checkpoint bytes | Stage-1 forecast difference | Stage-2 difference | Action mismatches |
|---|---:|---:|---:|---:|
| Original native checkpoint, original JSON | 4,715 | 0 | 0 | 0 |
| Original native checkpoint, **same zlib-9** codec | **2,290** | 0 | 0 | 0 |
| **CSMC-02 exact snapshot + 8 cached originals**, zlib-9 | **702** | **0/4** | **0/16** | **0/10** |
| **Exact conventional compact-only** summary, same zlib-9 | **351** | **0/4** | **0/16** | **0/10** |

The dual-tier snapshot is 1,588 bytes / 69.3% smaller than the original native *when both use zlib-9*, yet **351 bytes larger (2x)** than the equal-information compact-only control. Causal/probability performance is therefore **not improved**: the eight cached original IDs enable a small set of cold local duplicate/conflict checks. For all other witness IDs the original immutable archive is required; corrupt/missing archive fails closed.

The original archive and full native learner may still need their full evidence ledgers; **we have not saved 69.3% of whole-system memory**. This is a stored readout representation and provenance affordance, not a working cumulative/consolidating learner. There is no support for original-native repair, multi-context, stream, growth, future updates, or source-owner first-use in this v1 snapshot.

## Controls and custody

- Exact parent coordinator [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) at `86264b41a08d49f558418c0fba367f3a2636befa`.
- Git preregistration **`b15de1c87ec1c7a1213909f45294838095ceff0c`**, committed before the source code and local CSMC-02 run; nevertheless **FIT already previously consumed**, so this is not prospective scientific replication.
- Input archive `research/contrib/chatgpt/CAUSAL-AMALGAM/selection-dev-01/trace.json`, SHA256 `36f535c451c813dd56afd58c4f1833ac8e5fca98627d898a571e40c8bc8a0114`. Only first 50 observed synthetic FIT rows used. The archived raw bytes were not mounted in the local environment; offline reconstructed public FIT bytes were independently cross-checked against original GitHub evidence and first/last IDs. **Full repo checkout test should read/archive-hash-check the raw file**; that path remains unexecuted.
- Exact original native files Git blobs `5a18b00a4c4131526e71f51d63dfd9eb9471c81e` and `de8722f38d987ef7bcb4b7a0c23466b8e6f25712`. Local tests checked both against source bytes; research source/tests are byte-identical to the committed Git blobs described in `provenance.json`.
- Focused negative controls: cached conflicts, missing archive, corrupted archive, checkpoint bit flip, wrong digest, decompression bomb limit, unsupported blank native mode, baseline compact-only readout.

## Reproduce from full repository checkout

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CSMC-02 -p 'test_*.py' -v
```

The test will hash-check the full archived source if it is present (as in the complete repository) and exercise authentic uncached archive read-through. Local isolation test could not execute that branch, so final qualified native/Linux+Windows regression is **NOT_DONE**.

## Science and next qualification

**SCIENCE: UNVERIFIED.** No evidence of unfamiliar causal transfer, retention under interference, prediction gain beyond a conventional compact learner, useful action intervention gain, or whole-system memory savings. Do not classify 8/8 deterministic FIT tests as intelligence or memory consolidation success. Original source protected first-use remains owned by [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426), not authorized by this branch.

**Next:** qualify the exact committed SHA on an owner-authorized complete Linux/Windows checkout, including original archive read-through and bounded tamper tests. If qualified, further work must test **incremental changes** under archived repair/interference, prespecify matched source/compute/cost and stronger compact controls, and obtain distinct source-first-use owner authority before novel science. Do not expand caches or tune thresholds on already consumed FIT or held sources.

No existing learner, main ref, controller, runner, source, checkpoint or accepted model is mutated by this research.

## P1: source-authenticated cached FIT witnesses — 2026-11-21

**Correction to the original eight-test readout result:** The former v1 `TwoTier.restore()` validated cache IDs and the caller-provided checkpoint SHA-256, but did **not** validate the eight cached public observations against the independent pinned archive. An attacker controlling both checkpoint bytes and its supplied expected hash could replace one cached observation, recompute the hash, and make the old `check_witness()` return `CACHE_EXACT_MATCH` on the fabricated byte. The SHA-256 was a consistency check, not an independently anchored signature. This is a **development-source provenance boundary failure**, not a scientific experiment.

**Research-only P1 fix:** The first eight original public FIT bytes `44e50907bd0e110c` were rederived from the exact repository trace blob `9db0d3742fc8bd009c61d0864e4aba739a19e4e1` (raw archive SHA-256 `36f535c451c813dd56afd58c4f1833ac8e5fca98627d898a571e40c8bc8a0114`). `two_tier.py` now anchors those bytes in trusted source code and rejects mismatches **both on checkpoint restore and on cached-witness lookup**. Two new native test methods were committed first, at `536c068642f66a8e074638399ea4542267725581`; then the code fix `31b531ae59f456c24216fdfb6f387686b07fcafa`.

**Qualification classification:** Local Linux Python 3.13.5 isolated *validation-rule equivalent* exercise **5/5 PASS** (original modeled rules accept the re-signed forgery; new anchor rules reject it; legitimate original eight bytes still accepted). Local harness SHA-256 `ad2862306fdd3fc4287d9eba22ce2baed6609a7b49d277db7f60c6412f44f238`. This is **NOT** the complete committed `TwoTier` class or original native test runtime. The prior revision's 8/8 focused native tests remain historical and **do not qualify this changed commit**; the new 10-method native test, raw archive read-through and mandatory inherited Linux+Windows regression are **UNVERIFIED**.

**Important scope:** Hardcoding eight exact observation bytes is only valid for this previously consumed fixed FIT cohort. It is **not** general source authentication for future experiments; attacker-controlled source code, a compromised external trusted archive root, and forged counter/loss state remain out of scope. The compact-only control still matches 20/20 forecasts and 10/10 proposed actions; the eight-witness cache has no verified prediction, cumulative learning, intervention, cold retention or unfamiliar transfer gain. Nothing is accepted, deployed, merged, or newly trained.
