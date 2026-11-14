# WSP91 — free-answer span reading from real source prose

**Isolated research only. No accepted Yggdrasil model, controller, autonomous loop, deployment or merge.**

WSP90 (PR #1005, `2d0eb824ae539bdd39a26358ec0e38a686f97cb0`) provided two city article choices per question, with 10/12 country-disjoint DEV answers correctly selected. It tied a fully trained ordinary classifier and a hand-written parser. **WSP91 removes answer choices**: the candidate must return an *actual in-article character span* to answer source-grounded factual questions.

## Frozen prospective hypothesis and custody

`prereg.json` was independently committed before other WSP91 files and source capture at `698c3ba125b94880271d68713d20326ffeab95fe`. It predeclares all 36 English Wikipedia chemical-element article titles, element symbols, atomic numbers, three disjoint article cohorts, all numerical thresholds, baselines, negative controls, licensing and stop criteria. **Reserved DEV** is 16 new chemical elements ×2 questions =32 first-use questions. Public structural and fixture workflows must never run DEV evaluation.

The one-shot source collector reads at most 2 MediaWiki API requests for the 36 specified element pages; it fails closed on missing, malformed, too-short, bad revision or ambiguous redirects. It stores exact captured prose, text SHA256, reported page revision metadata and URL, contributor-history URL and a separate CC BY-SA 4.0 notice. The source file contains **no extracted symbols, atomic numbers, answer roles or verdicts**. Wikipedia's TextExtracts API reported latest revision ID is not a claim the excerpt is a reconstructed historic revision. Article/corpus exact captured bytes are pinned in GitHub; no live API during evaluation.

## Candidate and baselines

- **Direct writer:** For each question relation (chemical symbol, atomic number) enumerate 1–2 letter or 1–3 digit spans from raw characters only (no supplied answers), form hashed 3–5 Unicode character n-gram contexts around every span, and perform direct additive numerical edits from separately supervised training answer strings. No word-token representation, LLM, pretrained text embedding, autoregressive prediction or candidate gradient training. Every returned string is sliced directly from the source with start/end offsets and source identification.
- **Ordinary fully trained logistic SGD:** Independent multi-epoch span scorer trained to rank the *same* raw candidate spans using identical labeled source documents/context features, with 160 frozen epochs, loss/fit checks and CPU accounting. A model underfitting its own training answers is disclosed as a control failure.
- **Symbolic regex:** Explicit national source-style pattern, e.g. "symbol X" and "atomic number Y"; allowed to outperform or tie the candidate.
- **Lexical cue:** First valid character span after literal source cue, independent of training.
- **Random source span:** Fixed-seed selection among all actual in-text candidate spans. Without any candidate options from the evaluator.
- **Negatives:** unsupported question IDs, no eligible source span, altered numerical snapshot and zero/empty state; collect all failures, do not mask them.

The reader has a *hardcoded type prior* for short alphabetic/digit answers and receives a document + relation ID. This is a tightly scoped **extractive reading mechanism**, not open-domain fact discovery, unconstrained natural-language question interpretation, long-document comprehension, scientific reasoning or language generation.

## Stage protocol

1. Train on 8 source articles ×2 labeled factual fields; freeze initial source-context numerical weights and training predictions.
2. Append 4 new article ×2 labels without replay to the direct writer. Train ordinary comparator on all 12 ×2 examples with all candidate-span negatives. Verify cold restoration and retention of earlier learned answers.
3. Qualify on 8 separate **public fixture** element articles, 16 unanswered fields; may repair errors here before first DEV, without modifying frozen thresholds, title lists, core question interface or reserved source.
4. Source-only three-file G29 atlas reanchor, then **mandatory full final regression** on the exact source SHA on Ubuntu and Windows: WSP80–WSP91 focused/negatives, entire Yggdrasil root regression, G29 and source/checkout cleanliness.
5. Only after both qualify, run **once** on 16 reserved first-use Wikipedia element articles (32 questions); candidate, SGD, regex, lexical cue and random predictions are hashed before scorer reads reserved answer labels. Record individual wrong answers, source offsets, whole CPU and control metrics in GitHub.
6. `DEV_FREE_SPAN_READING_FEASIBLE` requires at least 24/32 exact answers, ≤4 behind fully trained SGD, ≤8 behind symbolic parser, ≥12 ahead of random, ≥15/16 initial answer retention, ≥23/24 SGD training answers, exact source proof and attribution, cold restore, unknown abstention, tamper resistance, and all other preregistered checks. Any failed criterion is `DEV_FREE_SPAN_READING_NEGATIVE`. No post-result retuning on consumed DEV.

## Execution boundaries

```sh
python research/contrib/chatgpt/WSP-91/source.py --verify
python -m unittest discover -s research/contrib/chatgpt/WSP-91 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-91/experiment.py --public-fixtures-only
```

Reserved evaluation uses `--reserved-dev-first-use` **only in a gated one-shot CI job** after both final full regressions pass. All results/data are in GitHub, not the user's ChatGPT Library. No paid APIs, new runner, schedules, main ref edits, accepted science, official Yggdrasil/FORGE loop changes or deployments.

**Research interpretation:** Even perfect performance could simply learn to identify recurrent Wikipedia phrasing. The hand-coded regex baseline may do as well. This does *not* establish Claude/GPT comparable knowledge or a general reader. Next hard tests need free-answer questions whose relation types are not predeclared, multiple-document evidence, temporal contradiction, cold retention, genuinely different publishers and domains, and trained neural retrieval/reader controls.
