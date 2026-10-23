# ELG-01 — Efficient Native Language Generation: Independent Verification Charter

**Status:** ADDITIVE / exploratory / PUBLIC DEVELOPMENT DESIGN ONLY; no evaluation run, candidate approval, access to held-out unfamiliar source, protected first use, merge, or qualified scientific result. Frozen development charter prospective to all ELG evaluations.

**Governance:** Finish and preserve active NCI-04, ITD-01, BIO, Mass Research CS13, Optimizer, FORGE, source-custody and transfer investigations first. Neither this document nor subsequent language work may replace them, change their source/checkpoint hashes, mutate original evaluation refs, create a controller or consume protected source data. CS07–CS09 information-cost negatives, CS10 real source-native rewarded learning positive, CS11/12 transfer negatives, original R10 #422 and G29/R7Q/proxy execution blockers remain distinct and unwaived. Scientific first-use requires independent witness and established CKB-plane admission; FORGE only under qualified delegation. No paid API.

## Verification target, not architectural mandate

**Hypothesis:** A proposed nontraditional realization mechanism might reduce **complete** training-plus-inference compute/latency/memory/energy without a meaningful regression in semantic and task capabilities compared with equally informed, properly trained conventional language generation. Competing mechanisms include state→language, hierarchical concept→text, adaptive characters/words/chunks, parallel drafts with selective verification, and reusable learned linguistic structures. Do not favor any mechanism by name. Choose a single **bounded small candidate** only after the current Optimizer and Research Charter work provides actual model source/checkpoint plus the exact behavior boundary; do not invent one or commission a full LM rebuild.

## Exact candidate identity and isolation preregistration

Before the first experiment, independently freeze a content-addressed *candidate checkpoint and training transcript*, tokenizer/output representation, training/data provenance, decoder, parameter count, software/compiler/hardware, generation policy, decoding temperature, random seeds, stopping criteria, resource budget, maximum number of refinement/retry steps, and any external verifier/retrieval/cache. Distinguish:
- reasoning/cognitive-state construction from language realization;
- bytes/chars/tokens/phrases, noting output granularity changes do NOT alone imply capability or cost improvements;
- full training source data from model development tasks, frozen public validation and independently born *unfamiliar* source test families;
- model-only compute versus actual full-loop cost: candidate state construction, retrieval, verification, repair, retries, re-decoding, tool calls, I/O, checkpoint/storage, training amortization and evaluation overhead.

Freeze **all** held-out source family hashes and evaluator implementation identities before running a particular candidate. Have a separate source custodian perform later independent birth/selection when qualified and never recycle publicly inspected prompts as unfamiliar scientific first use. No adaptive prompt/baseline change after result exposure. If inaccessible, label `HELDOUT_UNFAMILIAR_SOURCE_NOT_ADMITTED`.

## Independent task and capability coverage

Require independent, source-owned tasks whose answers are **judged by task outcome, not fluency or surface similarity**:
1. **Meaning/semantic compression:** long factual/source-backed documents with intentional negations, role swapping, numerals and omitted facts. Exact semantic propositions, information recall, bidirectional entailment, contradicting/unsupported statements and loss of rare but decisive details. Latent-to-text only counts as preserving meaning if all causal/logic constraints survive compression, not if text sounds plausible.
2. **Instruction/format adherence:** nested requirements, exceptions, refusal/abstention cases, structured output, tool abstention, JSON/schema correctness and exact constraints. Measure any hard violation.
3. **Mathematical reasoning:** source-unfamiliar multi-step discrete/continuous problems, generated separately from model training with executable/verifiable exact answers and symbolic consistency where possible. Measure numerically precise answers, intermediate causal dependencies and failure.
4. **Coding:** unfamiliar tested repositories/patch tasks from independent source owners, executable offline tests, compilation/runtime, security regressions and full task success; do not use lexical similarity or plausible-looking code as success.
5. **Multilingual semantics:** bidirectional unfamiliar cross-lingual instructions, lower-resource languages and long contexts, named entities/numbers, faithful detail retention, no English-only leakage.
6. **Long-range memory/consistency:** delayed constraints, revisions, facts introduced far apart, changed requirements and contradictions; score complete multi-part outputs.
7. **Novel composition/generalization:** tasks independently born across new compositional rules, unfamiliar environments and source-held-out forms; probes specifically distinguish retrieval/memorization, benchmark/template contamination and true first-use transfer.

For each family, preregister failure strata, critical or hard false positives, and uncertainty intervals. Language-model-graded assessments may supplement but may never be the only metric for math, code, safety, exact semantics or instructions. Where scientific contract requires **zero hard false positives**, any critical false positive **fails closed** even if average quality is high.

## Strong learned alternatives and fair comparisons

At least a properly fitted transformer/reference decoder, a capacity/resource-matched recurrent or state-space learned model, and the cheapest credible **simpler conventional** reference at the corresponding output granularity, conditional on each receiving the same permitted source information, task supervision and training budget. If trained controls cannot be provided, classify `EQUAL_FIT_BASELINE_MISSING`, not a candidate positive. For a realization-only head comparison also hold the latent cognitive state fixed and compare realization decoders; separately test full end-to-end systems against conventional baselines. Explicitly separate unmatched model quality/capacity improvements from architecture efficiency.

Run causal ablations: no-concept compression, randomized or permuted state, restricted latent capacity, no phrase reuse, no parallelism, disabled verifier, disabled repairs, fixed/removed retrieval, varied chunk granularity and untouched conventional baseline; each planned before seeing independent held-out results. Add leakage canaries and exact source identities. Disallow hidden extra model calls in verification or candidate retries. Masking certain source features requires equal information for the relevant fair comparator—ablation deficits alone do not show unconventional superiority.

## Complete, reproducible resource accounting

Measure original hardware family and clock, CPU and GPU accelerator time (kernel and wall-clock), FLOPs or calibrated proxy if honest, tokenization/rendering work, training/optimizer steps, peak host RAM and accelerator VRAM, persistent checkpoint/cache/retrieval bytes, communication and disk, realized energy/power when reliable, training/fine-tune amortization assumptions, latency to first correct output, full completion latency, number of retries and verifier/repair calls. Report full distributions and tail latency (p50/p95), not advertised raw generation speed or token count. For repeated deployment, show break-even queries against all training costs and how quality changes with budget. Energy unavailable → `NOT_MEASURED`, never fabricated.

## Falsification and advancement

Small source-frozen PUBLIC mechanism screening precedes expensive tests. **PUBLIC eligibility:** no regression on any preregistered hard constraints, matched-info strong control included, a confidence-supported quality-vs-total-cost Pareto improvement (quality noninferior *and* total cost lower, or capability gain with nonworse total resources), bounded capacity variation permitted if declared prospectively. Report exact absolute quality differences, confidence intervals with source-family-level replication units, variance across seeds and full total cost. No aggregate fluency score can hide missing mathematics/coding/multilingual/instruction strata or hard semantic contradictions.

**SCIENTIFIC advancement:** independent previously unfamiliar original source-family first-use on frozen protocol with independent witness and genuine proper trained baselines, reproducible **end-to-end** Pareto gain including verification/repair overhead; source identities and scientific negatives preserved, zero hard false positives where mandated, one final source-accepted integration regression. If no candidate, no properly trained comparators, no independent source custody or no resource instrumentation, declare `ELG01_NOT_TESTABLE_YET` and retain current research frontier. At most one small candidate family and one exact matched comparison initially; only evidence justifies increased portfolio investment.

## Immediate non-disruptive deliverable

This **charter only** is the first artifact. No model was generated, trained, benchmarked or awarded efficiency claims. When the existing Research Charter and Optimizer Work present a concrete qualified candidate and matched conventional checkpoints, produce a **separate FIRST-only candidate-and-control prereg** and bounded PUBLIC development run on an already authorized hosted runner, with original-source receipts preserved. Until then, research execution and controller ownership are untouched.
