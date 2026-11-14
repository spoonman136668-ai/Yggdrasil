# WSP92 — human-written cross-article question answering through direct weight editing

**Isolated development only. No accepted Yggdrasil intelligence, no controller, no main, no FORGE official loop, no deployment.**

### Why WSP92 is different

WSP91, draft PR #1008 (qualified SHA `c60d705b06926154b8c4a1c5b59cd79c479f7ab2`), achieved 31/32 free-answer extraction on one narrow kind of Wikipedia element article, and **tied the fully trained conventional reader**. WSP92 switches to **real crowdsourced questions about many different Wikipedia topics** from the [Stanford Question Answering Dataset (SQuAD) 1.1](https://rajpurkar.github.io/SQuAD-explorer/). Unlike WSP91, relation type, question wording and answer string class are **not provided as two predefined answer kinds**. A relevant paragraph is still provided to all models; source/document retrieval is not tested. It is an incremental attempt at general reading, **not** a general knowledge model comparable to GPT or Claude.

### Frozen protocol and source

The full prospective experimental contract was committed at `a6f2824e9241f29034c19f058c59d205d5b6c4fb` **before source capture, WSP92 model implementation, source use or any reserved-first-use**. Training / public / reserved SHA256 article selection, all source/answer conditions, controls, counts, thresholds, budgets and negative interpretation are frozen in `prereg.json`.

One bounded source capture reads exactly two **official** SQuAD v1.1 public archives. Raw archive byte SHA256 is validated against the fixed hashes from the [maintained SQuAD dataset metadata](https://huggingface.co/datasets/rajpurkar/squad), not inferred from HTTP status or a moving webpage. A fixed, hashed article-title and question-ID ordering selects exactly **128 train questions from 16 articles, 24 public fixture questions from 6 different articles, and 50 reserved DEV questions from 10 additional articles**, with no post-result substitutions. The derived snapshot stores **202** question/context/source records in `data/squad-contexts-frozen.json`, with **no answer labels**; exact answer offsets and text are in separately hashed `data/squad-labels-frozen.json`. Relevant paragraphs are directly supplied to every model. The capture is a one-time action by dedicated isolated GitHub CI; full raw 35 MB input files are not committed or uploaded to the user's Library.

The derived SQuAD/Wikipedia question and passage data is published under **CC BY-SA 4.0**. Preserve Rajpurkar et al. and Wikipedia contributor attribution, source URLs and separate share-alike notices. These are original SQuAD source passages, **not a claim of current Wikipedia article revision status**. Exact raw context SHA256 and source/label-record digests enforce custody.

### Experimental arms

- **Direct writer:** train only from 96 labeled question/source-answer examples first, then append 32 labeled examples without replay. Enumerate answer candidates using raw document whitespace/punctuation boundaries (at most four consecutive segments, 55 source characters), score with stable Blake2s numerical hashes of Unicode raw-character 3–5grams of question and candidate context and cross-question cues. Direct sparse numerical edits only. No pretrained text model, learned word tokens, transformers, next-token training or candidate gradients. Output one exact article substring with offsets and source/citation identifiers, or abstain.
- **Fully trained conventional SGD:** independent 60-epoch sparse logistic comparator over the **identical** source candidate features and same original supervised answer annotations/negatives; report source-question training fit, exact answer generalization and CPU. This is *not* a modern pretrained neural reader; to establish superior broad knowledge, a much stronger modern reader would be necessary.
- **Non-gradient retrieval:** question and local passage raw-character trigram overlap, independent of writer weights.
- **Symbolic:** unsupervised nearest simple cue to the last question fragment.
- **Random span:** SHA256 deterministic choice from same source candidates.
- **Shuffled-label writer:** equal-action direct updates but deliberately wrong source answer spans for a negative-control test.
- **Integrity:** unknown source, altered source/context hash, empty questions, cold numerical restore, checksum corruption and full per-method resource accounting.

### Reserved scientific gate

Only **after** all public fixtures, mandatory full regression on **Ubuntu and Windows**, source custody and G29 exact source-pinned atlas, a single original DEV run may score 50 first-use SQuAD development questions across 10 unseen articles. It freezes every model's predictions and output hash **before** consulting public/DEV labels; it then reports strict/normalized exact matches, full per-question errors, source span evidence, candidate reachability, trained-control fit, incremental retention, 64-bit process CPU, weights/observations and all negative controls. No reruns of consumed DEV as fresh novelty, no post-score retuning, no protected-science acceptance.

Frozen success threshold is deliberately modest: >=8/50 strict correct, >=5 ahead of deterministic random, <=20 below trained logistic, >=32/128 source training answers correct, >=75/128 conventional training answers correct, >=12/96 original answers retained, >=85% test answers representable by the fixed span enumerator, 0 unsupported confident answers, clean source proof, all control and custody checks. All criteria must pass for `DEV_CROSS_ARTICLE_QA_MECHANISM_FEASIBLE`; failure is `DEV_CROSS_ARTICLE_QA_MECHANISM_NEGATIVE`. **Even passing is not SCIENTIFIC_PASS or AGI progress without a stronger independently validated control.**

### External limits and next decisive research

SQuAD is real human-written language and diverse subject matter, but **its paragraphs are supplied**, and the answer text and answer starting offset were crowdsourced. Its official development questions are not a hidden scientific test. This experiment does not measure retrieval across an unfamiliar corpus, open-world unanswerable questions, source conflict, causal reasoning, broad factual knowledge persistence or general intelligence. Any negative should motivate a mechanistic pivot in relation conditioning, not further infrastructure or retrospective threshold changes. Independent publisher/domain evaluation with a fully trained modern reader and cost parity is a later *separately authorized* scientific first-use.

No new runner, schedules, controller, paid APIs, accepted science, deployment, source/main merge or user Library upload. All code and evidence remain only in the isolated draft GitHub research branch.
