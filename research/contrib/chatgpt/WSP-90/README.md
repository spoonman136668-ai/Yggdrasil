# WSP90 — learning country-capital evidence from raw Wikipedia prose

**Status: isolated development only, no accepted model / main deployment.**

WSP89 (draft PR #1003, head `87852c2e5bac10dd57d99191da387b43dab9aec7`) demonstrated numerical structured fact-store recall with sourced corrections, but had not read natural-language evidence at all. This WSP90 pilot introduces genuinely authored human English prose from Wikipedia city-page excerpts. The primary hypothesis asks whether editing *raw character-pattern numerical weights directly* from 16 labeled demonstrations can distinguish national from regional capital evidence on 24 unseen source documents from 12 countries.

**Pre-frozen protocol:** `prereg.json`, committed alone before implementation or source-capture attempts at `996d4afba658b149a7f7b81efc7b7c78c9d8ebd4`.

## Scope and hard limits

- This is **two-choice fact retrieval**. Every question already supplies the correct country and two candidate city article titles. Learners must choose the national capital candidate using article prose, not discover candidate cities independently.
- All 40 titles and ground truths were predeclared before capture: 16 public-fixture city articles from eight countries and 24 disjoint reserved development articles from twelve different countries. The source snapshot deliberately contains neither labels nor capital/control roles.
- The direct writer sees **six training positive/negative pairs initially**, adds two more pairs with no old replay, then answers unseen country questions using only article text and country/title metadata. Raw Unicode 3–5 character n-grams are hashed to 16,384 numerical coordinates, no word/token vocabulary, pretrained model, gradient optimizer or autoregressive objective in the candidate. Country and title mentions are replaced by fixed Unicode placeholders to limit entity-name shortcut learning.
- Conventional fully trained SGD logistic control uses the *same raw character features* and all the same supervised examples; independent hand-written proximity parser, lexical retrieval, randomly chosen candidate, and inverted-label direct writer are included. The strongest control is permitted to win.
- All downstream outputs and control guesses are hashed *before* the withheld role labels are used to score. The code and preregistration are public in the PR, so this is **not** a cryptographic evaluator seal or independent blind scientific validation.
- The snapshot collector copies the first ~1,100 characters of the Wikipedia city lead; this is not long-document understanding, multi-hop reading, new ontology acquisition or open-domain QA. The source may contain "capital" in the context of a province or department. The pilot checks whether numerical evidence distinguishes that contextual difference.

## Source and license

Text is taken read-only from **English Wikipedia** through its publicly documented TextExtracts API. Wikipedia text is licensed under [CC BY-SA](https://en.wikipedia.org/wiki/Wikipedia:Copyrights), with attribution and share-alike obligations. The isolated `data/wikipedia-leads-frozen.json` corpus is separately labeled CC BY-SA 4.0 and records per-page title, article URL, contributors/history link, captured text hash and reported revision identifier. The snapshot itself is immutable and checksummed. The TextExtracts API returns contemporary extracts; reported revision metadata is *not* independent proof of revision-exact historic extract reconstruction. Use the stored bytes as the authoritative experiment input. No model or output response is licensed as a derivative of the unseen copyrighted passages by mere numeric association; copied text in the source is labeled and attributed.

## Falsification

For `DEV_PROSE_RELATION_GROUNDING_FEASIBLE`, all predeclared development checks must pass: at least 9 of 12 novel country questions correct, no more than two fewer than fully trained conventional classifier, >=3 correct answers ahead of inverted-label control, >=10/12 correct first-six training labels, >=14/16 correct after adding two training pairs, unchanged correct candidate selection on original six training pairs, exact source attribution on correct predictions, unknown abstention, bitwise cold restore and tamper detection, measured resource/CPU costs, all controls reported.

If any criterion fails: **`DEV_PROSE_RELATION_GROUNDING_NEGATIVE`**. Such a result is useful falsification; do not change a threshold, use a different city, rerun reserved source as "new", or claim a pass. This is one development source family and publisher, not independently sourced novelty or scientific acceptance. An independent external corpus/publisher and a truly free-answer open-ended QA experiment are required later.

## Execution and isolation

The collector makes **at most two public Wikipedia API calls** for 40 frozen articles; it refuses an existing output file and fails closed on missing/too-short pages or unsafe normalization/redirect ambiguity. The source's one-shot capture runs only on its isolated research branch. Public fixture calibration and the structural controls execute with no DEV evaluation and no network.

```sh
python research/contrib/chatgpt/WSP-90/source.py --verify
python -m unittest discover -s research/contrib/chatgpt/WSP-90 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-90/experiment.py --public-fixtures-only
```

The `--reserved-dev-first-use` command must not run before **WSP80–WSP90 focused + full Yggdrasil root + G29** source-pinned qualification on *both* Windows and Ubuntu at the exact candidate SHA. The reserved first use is a separate, single gated DEV CI job. No accepted ref, official Yggdrasil/FORGE owner loop, production model, controller, protected scientific first-use, new runner, paid API, scheduled job, live market, or user Library content is authorized or modified.

**Next intended direction:** Open-ended document-to-answer retrieval/extraction across genuinely disjoint articles, topics and publishers, with citation precision, cold retention, adversarial counterevidence and *fully trained* retrieval-augmented neural and symbolic baselines. Closed-set country-capital selection here is not comparable to GPT/Claude world knowledge.
