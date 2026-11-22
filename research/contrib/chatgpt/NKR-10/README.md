# NKR-10 — Real historical TRAIN masked-relationship transfer

**Purpose:** Move beyond synthetic-only rule adaptation in NKR-09 without claiming to access a new independent scientific test set or automatically promote Yggdrasil's accepted model. Test **source-visible, historical Wikidata numerical knowledge** in a strict source mask so training cannot look up the target label.

## Original source and scope

NKR-05 compiled the complete **21,343,681-row historical Wikidata5M-variant TRAIN** image, **828** predicate IDs, **256,124,172** bytes. NKR-09 induced composition rules from synthetic observation bundles and scored **9/12 vs 3/12** after synthetic feedback, tying a strong equally informed symbolic control, then proved interface compatibility on the full real image. Its full-size proof used an **invented synthetic target rule**; it did **not** evaluate unknown real historical relationships.

NKR-10 does a different, falsifiable test: freeze a semantically meaningful numerical relation composition `P31 + P279 => P31` (historically *instance of* plus *subclass of*). Mine source-supported motifs from the genuine existing historical image; hide selected actual original P31 facts from the learner, and measure whether it can retrieve their object IDs through the remaining visible P31/P279 relationships. This is **historical TRAIN replay**; it is **not** freshly held-out Wikidata valid/test and does not prove new world facts or a novel relation family.

**Frozen prereg FIRST** `2874e4e048ec95bc14a68c9eb8621d97f5d9e6df` before code/first NKR-10 source access. Parent NKR-09 draft [PR #1137](https://github.com/spoonman136668-ai/Yggdrasil/pull/1137) exact `5c9c9c93c63d3705383f9bd3d5d088f983030b3d`. Accepted main remains `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.

The existing immutable [NKR-05 historical image artifact #14220169461](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43856374741/artifacts/14220169461) is **not regenerated**. Original archive source and TRAIN SHA remain frozen; **never read original valid/test data**. Original image SHA `6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1`, manifest SHA `aa2d56e72284a042aee72587028642110327307b483de667586f105f018ebe8f`, source artifact ZIP SHA `c7265cabac91b8762fb5d65209eef44fa79a8fbf3d9a6f61300ef60ded0a5275`. Artifact expires **December 16, 2026**.

## Source-mask design

`yggdrasil/native_historical_transfer.py` never accepts a free-form success flag, owner source claim, oracle or model output as a real fact. The original native factual bytes are streamed read-only **twice**. First select subjects with a fixed `mix64(subject) % 32 == 7` into the cohort. Split each source `(subject, P31, object)` by `mix64(subject XOR (object << 1) XOR salt) % 4 == 0` into *sealed target labels*, with all other cohort P31 edges visible to the training view. The identical triple always hashes to the same side, so duplicate TRAIN rows cannot leak a withheld target to training.

Second pass obtains only P279 edges where the subject is a retained visible P31 class ID. The model receives **only** `MaskedTrainingView` (visible P31/P279), with neither original source-handle nor held-out targets; the sealed labels are supplied only to an independent scoring function after rule inference. The presumed `(31,279)=>31` relation is **preselected from known Wikidata predicate types**. Source-visible direct witness motifs on at least four distinct training subjects are required to activate the rule. No missing link is a negative label, and inferred links are NEVER stored as observed or ground-truth facts.

Evaluate the first 4,096 lexicographically eligible unique hidden `(subject, object)` positive labels for subjects retaining at least one P31 fact. Do **not** select examples because candidate paths succeed. On each source-hidden query, rank by number of training-visible P31/P279 paths (top 4, numeric ID ties). The same complete visible training evidence goes to an **independently coded exact symbolic composition/count control** (parity required) and a simple global top-4 P31 frequency prior. Report masked positive recall@4, rule training support, inference coverage, lift, read passes, resource cost and nulls.

Frozen *development* result threshold: at least 64 eligible masked positives, >=10% recall@4, >=5 percentage points over the fixed top4 prior. **Even if met, science remains UNVERIFIED** because this is historically consumed TRAIN replay, the relation template is specified in advance, missing KB facts are not labeled false, the strong exact symbolic control ties by design, and neither general intelligence nor new real relationship-family invention has been demonstrated.

The prereg also mandates truthful null/negative outcome when P31/P279 is absent or unsupported, 0 eligible labels, low lift, or too few sampled positive source facts; **never change the split or post-tune it to produce a positive**.

## Engineering and owner fences

Source-safe Linux+Windows tests check deterministic masked partition, no duplicate leakage, exact matched symbolic parity, no-signal nulls, unknown relation abstention, retained original source and native YPC1 checkpoint. Run full original root regression on identical final SHA/tree, independent G29 code atlas on both OS, then only once reuse the original **already built** full image artifact to run `research/contrib/chatgpt/NKR-10/run_historical_mask.py`. This is limited to the existing GitHub-hosted Ubuntu temporary file, with **no new 256MB artifact upload** and a small source-bound result receipt. No external source download, no protected first-use, no owner-accepted model mutation or scheduler.

The native model remains independent, non-transformer and non-token; this new module is an **isolated research diagnostic**, not a permanent installed knowledge path or live agent. P31/P279 source labels are historically archived and may be incomplete or stale. If only symbolic-equivalent association retrieval is supported, retain that result as useful engineering and do not claim autonomous scientific insight or new categories of knowledge.

**Pending deployment remains unchanged:** accepted Yggdrasil main and owner-controlled native DG1 are not modified. Permanent owner-controlled knowledge installation still requires an independently verified location, qualified authority and cold receipt; this PR stays draft/unmerged.
