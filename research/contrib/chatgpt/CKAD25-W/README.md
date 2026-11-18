# CKAD25-W — unlabelled causal memory recall under interference

**Status: prospectively frozen, original source-only score not yet observed as of this README. Research-only draft; no accepted-model admission.**

CKAD25-V showed that the **same** Yggdrasil `NativeCumulativeLearner` can store a source-pinned numeric GF(2) posterior that exactly matches a conventional 697-rule exact Bayesian control. CKAD34 PR #1250 has **already** studied class/degree selection from source only. This study avoids duplicating it: the distinct question is whether **learned native memories are recalled across world switches without revealing regime labels, and whether unknown relations are rejected**.

## Mechanism

One source-owned numeric native learner restores the original CKAD25 developmental checkpoint (SHA256 `c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f`), observes 12 do-action/outcome records for relationship A and 12 for B in different pre-existing slots, compiles both numeric causal relation memories, then learns 8 source observations each for unrelated pressure worlds P and Q in slots3–4. After cold restore, an unlabelled target presents four **input/outcome observations** from one of A, B, novel C or novel D.

The new **read-only method** `NativeCumulativeLearner.recall_causal_regime` evaluates the likelihood of those four records under the two stored native numeric hypotheses, together with an unknown-world alternative, using **supplied conventional equal priors and a fixed 0.90 admission gate**. The method returns either a remembered native causal prediction or an abstention at p=0.5. This is a proposed retrieval seam in the SAME native model, not six learners, a new controller, a source-bound trust proof, or primitive invention. It does not change v6 checkpoint bytes or the previously compiled native representation algorithm.

## Frozen 2-seed screen

- **Preregistration before source implementation:** `33919529d6ebbd014c1ce84e44c7f8bb1e0824da`.
- **Native read-only code commit before original source scoring:** `81c3f95f2d547346169876eeb8f995fd0d1eaac1`, Git blob `7b81c241c8eea19f669a826bb03c6232735c94c3`.
- **Prospective score source before any original held score:** `f4322491277f403a68b41308362019a11080bb65`, Git blob `b4bd546859ef038a34935b59988ebe1e124cf160`.
- **Independent original conventional helper unchanged:** Git blob `31e06746dd2fa83cf4bfedf28da43cacbc68c99f`.
- Two deterministic seeds `51041,51047`; fixed schedule **A → B → A → C (novel) → D (novel)**. The repeated A-held inputs are a cold retention measure, **not new independent test outcomes**.
- For each seed, source training is 12 A +12 B +8 P +8 Q outcomes (40 source-free native observations); each of five phases reveals four unlabelled target-world diagnostic outcomes (20 more public rows). **120 synthetic observed action consequences total**, **40 phase-scored held predictions**, **32 unique independent source/evaluator held labels** due to repeated A.
- Known A/B numeric source witnesses and query masks are isolated: twelve source-trained masks, four target diagnostics chosen from *the twelve existing source-known inputs*, and the four remaining masks reserved as held. Target diagnostics are newly observed world outcomes, not true class labels. Common held test masks cannot influence selection.
- Full independent exact conventional 697-rule posterior over each source, continuous mixture with unfamiliar-world prior (strongest), exact identical hard gate (parity control), fully fitted logistic/RandomForest source memories, fixed recency B, fixed A, no-memory p=0.5, and privileged label oracle (ceiling only, never trained or available to candidate).

**Frozen screen GO:** source/old-memory integrity, returning-A Brier improvement ≥0.08 versus recency-B, known A/B/A phase coverage ≥12 of 24 with at most 2 wrong, at least 3/6 known regimes recognized, novelty Brier ≤0.27 and no more than 1 confidently wrong C/D label, overall within +0.03 of strongest logistic/RF and +0.04 of full conventional mixture, and exact gate-equivalent conventional/native source prediction parity. Any miss is DEVELOPMENT_NO_GO; all pass is DEVELOPMENT_SIGNAL, **never SCIENTIFIC_PASS**. No post-score tuning on those evaluated source worlds.

## Limits and custody

These are deliberately hand-specified small Boolean worlds with common training-mask probes, a fixed known/unknown Bayesian prior, and only two previously learned regimes. A success may demonstrate **native memory retrieval and persistence**, but not model-free novelty detection, genuinely learned inference beyond supplied grammar, long-term continual learning, general reasoning, or superiority to exact symbolic Bayesian source equivalents. A failure must remain visible. No original protected-world action/first-use, accepted Yggdrasil/FORGE promotion, controller/scheduler, model merge, paid API or deployment is authorized. For source-scoped research contributions, external source-evidence cannot grant its own owner acceptance.

The previous original CKAD25-V score is **not rerun as new proof**. New CKAD25-W artifacts, including original result bytes, source fingerprints, complete per-world diagnostic and held metrics, and final regression custody, belong in this GitHub research directory, not chat attachments.
