# WSP93 — explicit source-evidence binding for human question answering

**Research isolation:** draft branch only, no accepted Yggdrasil model / FORGE owner loop / promotion / merge / deployment / protected science or scheduled tasks.

WSP92 (draft PR #1010, original result 0/24 exact public SQuAD questions) showed that direct numerical editing of hashed character contexts did **not** yield useful cross-article question answering. That original negative remains immutable. WSP92's 50 reserved SQuAD *dev* questions were left unconsumed and are not used here.

## Different mechanism

WSP93 tests a **small interpretable relation-binding program**, not an expanded high-dimensional hash context readout. A candidate answer is connected to evidence through a raw-character substring shared between the human question and a source paragraph. The program calculates the anchor's direction and character distance relative to the answer candidate, source-local connectors, answer character shape and question-intent prefix, then **edits numerical operator weights directly** from supervised outcomes. Query and source bindings are explicit and inspectable; the model has no pretrained semantic embeddings, no word-token vocabulary, no autoregressive next-token objective, no transformer and no gradient updates. Actual answer spans are copied from source character offsets with associated source identifiers.

This is not free document retrieval. It is a *span ranker given the relevant source paragraph*, with intentionally small, interpretable program operators. There is still explicit supervised answer feedback, and a hand-coded question-intent/shape prior. The experiment cannot establish general reading, causal intelligence or AGI.

## Source / prospective custody

The WSP93 preregistration was frozen FIRST at `3eb12021dc6954410b91becd785375ce60119887`, before any WSP93 code, source collection or scoring. It fixes official original SQuAD 1.1 **TRAIN** archive SHA256, one read-only download, article and question deterministic hash ordering, sample counts, thresholds, comparisons, negative controls and first-use admission.

The title selection explicitly skips the first sixteen SQuAD TRAIN article titles used in WSP92. It then freezes **72 labeled training QAs across 12 disjoint articles**, **24 public fixture QAs across six other articles**, and **32 reserved DEV questions across eight additional articles**, none of which belong to WSP92's original 50 reserved SQuAD dev QAs. The source snapshot contains question/context and per-article Wikipedia/SQuAD attribution under **CC BY-SA 4.0**; exact answer labels and offsets are a separate frozen, hashed file. This is the *same publisher* and known SQuAD benchmark family, not independent publisher generalization or secret held-out science. No full raw archive or Library copies are retained.

The collector requires exactly the pinned official source bytes, no substitution or missing article/offset, and exactly two derived files in its source-only commit.

## Falsifiable comparisons

- **DirectBinding:** explicit learned operator table, source anchor direction/distance, answer shape and question intent, updated with fixed balanced source-positive/source-negative feedback. First 48 QAs then 24 more, no old replay.
- **Question-ablated DirectBinding:** same exact trained numerical weights and source candidate list, but inference removes ALL question-derived anchor/intent features. Critical negative control.
- **Fully trained conventional logistic:** fixed 120 epochs over exactly the same interpretable source features and original supervised feedback, no hidden pretrained reading model. Train fit and end-to-end cost always reported; any conventional win stays recorded.
- **Independent lexical anchor retrieval:** closest source span to literal shared raw-character evidence, no learning.
- **Independent symbolic type matcher:** question prefix vs candidate character shape plus evidence proximity.
- **Random source span:** fixed SHA256 seed and same candidate generator.

All methods emit exact source substrings with original context offsets or abstain. Public scores, original retention and CPU times must be recorded even when scientifically negative. A **public positive** requires ALL frozen criteria, especially at least 5/24 exact, at least three above random, **at least two above question-ablation**, at least 30/72 source training fit, 45/72 ordinary training fit, 80% raw gold-span candidate coverage, source citations, cold restore and tamper rejection. A negative is `PUBLIC_BINDING_NEGATIVE` and disallows reserved first-use. A positive is only `PUBLIC_BINDING_FEASIBLE`, not `SCIENTIFIC_PASS`.

## Qualification

Source-only one-shot capture on isolated branch → public source/negative qualification both Windows and Ubuntu → if public science positive, exact tree G29 atlas three-file reanchor and mandatory **full WSP80–WSP93 focused + complete Yggdrasil root** regression on both OS → only then one-shot reserved original DEV, conditional on source custody and separate first-use admission. If public negative, seal classification, stop the existing mechanism, retain 32 reserved WSP93 and 50 reserved WSP92 questions unconsumed. No threshold retuning or covert reserved reuse.

No paid API, new runner, scheduled task, user Library upload, controller, accepted ref or production modification. The user does not need to run workstation commands.
