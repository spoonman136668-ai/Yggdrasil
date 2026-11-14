# WSP88 — token-free raw-utterance consequence grounding (isolated DEV)

**Parent:** WSP87 draft PR #999, exact head `3a64e167fa33e846e999f907e42ec3e7461710e3`. WSP87 eight-world result is **DEV_SUBSTRATE_FEASIBLE** with independent symbolic graph parity; no superiority or general language claim.

**Frozen prospectively:** `prereg.json` was independently committed at `76e25e0fdc1a104d94c37592e9468c00d086ee41` **before** WSP88 implementation, tests and any DEV run. No reserved seed 13011–13018 is permitted in ordinary tests or workflow fixture jobs.

## Why this gate matters

WSP87's matrix assumes externally supplied grounded entity and relation names. WSP88 instead asks whether an agent can associate *raw previously ungrounded English-shaped utterances* with the consequences of its own actions. It must generalize to entirely unshown sentence templates/object combinations, then learn three additional aliases without rewriting its old associations. The input is raw Unicode with fixed-width character n-gram hashing; there is no word tokenizer, language model, autoregressive next-token prediction, pretrained representation, gradient descent in the proposed weight writer, or hardcoded verb-to-action mapping in the learner.

This remains **synthetic templated English**, not natural discourse comprehension, world knowledge, semantic induction, or a plausible Claude/GPT competitor. The independent evaluator defines a small grammar and three hidden action classes; that is a research limitation, not a claimed breakthrough.

## Paid causal feedback

Every Stage A utterance is tried once against each of three actuators (324 paid actions); each trial returns a binary outcome, not a language class label. Stage B gives nine distinct demonstrations of three new action verbs, tested across three actuators each (27 more paid actions); the candidate updates its numeric matrix without replaying Stage A. A regularized ordinary trained softmax comparator receives exactly the same observed feedback and uses the same raw features. Its training optimizes by gradients for a fixed 80 epochs per stage; this comparator is allowed to refit historical data. An independent exact-whole-utterance memory, class-shuffled-feedback learner and all-zero numeric weights test shortcut explanations.

## Frozen metrics and strict boundaries

All eight independently salted novel DEV worlds must meet the preregistration's thresholds: at least 90% held-out old-verb accuracy, 75% new-alias accuracy after fewshot updates, 95% retention of old answers; at least +30 percentage points over exact-string lookup; shuffled-feedback accuracy at most 45%; unsupported commands confidently answered at most 5%; no worse than 10 percentage points behind the **fully trained** conventional softmax control; cold restore and tamper rejection; measured actions, train/inference CPU and resource count. A check failed is **DEV_GROUNDING_NEGATIVE**. Passing qualifies **DEV_GROUNDING_FEASIBLE** only, not a valid protected science result. Preserve negatives.

## Execution

Only public fixture worlds:

```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-88 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-88/experiment.py --public-fixtures-only
```

**Reserved DEV first-use, after full dual-platform exact-source regression and owner source check only:**

```sh
python research/contrib/chatgpt/WSP-88/experiment.py --reserved-dev-first-use
```

The DEV command is deliberately **not present in CI**. No accepted ref, main, official Yggdrasil/FORGE loop, production inference, protected scientific source, paid API, scheduler, new runner or user Library material is touched. Progress toward genuine general knowledge still requires untemplated raw language, source-backed facts, contradictions and time, and disjoint-domain QA under fully trained strong baselines.
