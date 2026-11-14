# WSP-107 — independent projected TransE conventional baseline (historical TRAIN-only DEV)

**Source of truth:** `prereg.json` first committed at `64247687d2abc4ff9413ce7e1122af9d019109c3`. The protocol was frozen before WSP107 code or this source-run. This is **exploratory DEV on an already exposed historical TRAIN-derived split**, not independent original scientific first use.

## Parent, negative and rationale
- Stacked on qualified [WSP106 draft PR #1058](https://github.com/spoonman136668-ai/Yggdrasil/pull/1058), exact parent `89ebc7ea7424e8908e08ebb8ad0522d04139c274` and tree `2724860922db51b504d475060be983d7acf1810a`.
- The WSP106 fully sourced conventional DistMult logistic-SGD model failed with `FloatingPointError: unbounded training logits` in [run 43641588196, job 132591972913](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43641588196), before any valid full-epoch-score result. **Preserve this negative and do not tune, repair or rerun its original frozen source/learning rate/seed/hyperparameters after that result.**
- WSP107 is an **independent standard conventional model family**, translational `TransE`: squared-distance margin ranking and unit-ball projected sparse SGD, not merely a changed DistMult learning rate. This still does not create a fair scientific heldout-first-use result, because WSP103/WSP104/WSP105 TRAIN-derived test queries have already been examined.

## Full retained training source and fixed comparisons
- Independently sealed **noncanonical historical Wikidata-derived mirror**, original archive SHA256 `ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878`; source train SHA256 `2ef1a279f6393a8edfbb2b44114a2c97944272e5fe2a1bd2a7cbe48f94742f1a`, **21,343,681** facts. Do not claim this is official canonical Wikidata5M.
- Reuse the entire (subject,predicate) 1/32 group mask from WSP103: **20,677,636** retained training edges; **666,045** masked; **4,096** source-derived DEV query groups. Original valid/test members and protected WSP101 scientific cohorts remain unopened.
- All Q entity and P relation IDs use exact unique retained mappings, not hashed buckets or leaked heldout features. Score the **identical WSP104 64-candidate-per-relation universe**, first verifying its original ranking SHA256 `4a4364b6c4a806d2b69e9bb329e70f6c1f7d3f39fbafb68bb536d22fb9e2259a`.
- Frozen conventional TransE parameters: dimension **16**, exact **4 epochs** over every retained fact, batch **4096**, seed **1076107**, one uniformly sampled negative object per positive, squared-distance hinge margin **1**, sparse SGD rate **0.02**, unit L2-ball projection after every minibatch. Fixed-budget training is **not** evidence of convergence; no post-result early stopping or tuning.
- Compare pretrained zero-epoch seed vs trained TransE Hits@1, Hits@10, MRR against WSP104 frequency (921/4096 Hits@1; 1853/4096 Hits@10) and WSP105 relational-symbolic path first (1190/4096 Hits@1; 2038/4096 Hits@10). Record epoch losses and full-process CPU/wall/memory, identical query provenance and in-memory cold-copy output.

## Qualification and scope
- Focused Linux/Windows synthetic unit tests cover active-margin descent, zero/NaN projection rejection, no masked leakage, exact retained candidate receipts, deterministic cold replay, out-of-vocabulary and budget negatives.
- The first focused run failed one **fake fixture**: its two synthetic vectors already had zero hinge loss, so a further decrease was impossible. The fixture was corrected in `c6009b9e05f6a2709dc0c70757939cebfd3457c4` before any original real source fit. No optimizer, data, labels, split, parameter or metric changed.
- Full original WSP80–WSP107 + Yggdrasil root regression must PASS **Linux and Windows at candidate SHA**, independent G29 atlas acceptance PASS both OS and code tree clean before the **bounded one-shot public Ubuntu runner** original TRAIN-only model fit.
- No official valid/test, protected original first-use, private runners, new controller/scheduler, paid APIs, artifacts, main/ref merges, accepted model weights, production, or external deployment.

**Decision:** Positive, negative and training-failure outcomes are all preserved without refitting on the same DEV scores. No `SCIENTIFIC_PASS`, AGI, direct-weight programming advantage, cold retention across worlds or unfamiliar transfer can be claimed from this already known TRAIN-based cohort.
