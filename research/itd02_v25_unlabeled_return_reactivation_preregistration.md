# ITD-02 V25 — preregistration: unlabeled return-to-source memory reactivation

**Status:** PREREGISTRATION ONLY, before V25 executable mechanism, audit, tests, or result. Source-only development experiment, not independent scientific first-use or an original-world test. This file is the entire V25 delta at this gate.

## Frozen immutable starting point

- Exact parent is unmerged Yggdrasil V24 PR #609 head `671d8c3def0ef6cbe60e52eaf66d28ead8475e66` on V23 PR #607 head `e5bf689f213a72d9f572320fc14ab2eeb05cc0ff`.
- V24 exact-source Linux/Windows 2/2 PASS run #40667473910; canonical 48-case SHA `563cbaf71049bff0607aabf808b5261c33819830748fca69962cd13f686348ab`. V24's frozen slow bank was bitwise preserved but active predictions matched fresh scratch: T1 17.770323, T2 28.966420; source reactivation was **not** demonstrated. Its preregistered result remains `V24_SOURCE_MEMORY_PRESERVED_TARGET_PARITY_ONLY__NO_SCIENCE`.
- V23 failed sparse-target transfer/retention; original unfamiliar-world V12 NO-GO remains binding. Existing native bridge, ring, V22 learner, V23 harness and V24 evidence are immutable foundations. No G29/proxy exemption.

## Research question and hypothesis

Can a source-trained eight-cell ring be **reactivated automatically when a previously learned source reward regime returns**, based exclusively on accumulating legal public selected-action feedback, without a source/target identity label, task switch command, hidden reward law, evaluator signal, or source-memory API call?

Hypothesis: a predeclared bounded sequential evidence controller can recognize **a return**, switch from independently target-adapted fast memory back to physically protected slow source memory, and reduce post-return prediction error and action regret compared with always-fast continual learning and strong conventional public-error change detection, without damaging target adaptation. Preserving source parameters alone is **not** success.

## Candidate boundary, inputs, and exclusions

- Retain V24's existing V22 eight-cell neighbor-ring as each learner. Use one frozen, source-trained slow bank (163 learned scalars) and one independent fresh/trainable fast bank (163 learned scalars). No added neural capacity, copied weights, global model-gradient or target reward oracle.
- All feedback is from actual selected legal terminal actions; never update from withheld counterfactual rewards. The frozen bank cannot train, even when active. Each readout receives the same legal public event.
- The V25 candidate may maintain only bounded publicly observed pre-update per-bank loss evidence and an explicit deterministic change-detection state; the learned banks remain independent. A centralized scalar selector is permitted but **must be disclosed as an external controller**, not misdescribed as emergent local cognition.
- Training starts in the SOURCE environment as in V24; after this initialization there is **one uninterrupted stream**. No call to source/target stage constructor, no bank reset, no trigger, no regime label, no environment name, no evaluator hints or scripted switch when a new regime begins or source returns. Ground-truth stage boundaries may appear only in the *offline evaluator* after predictions and actions have been frozen.
- No hard-coded stage length or public cue-order marker may be used to infer a transition. Include non-transition control streams and variable-length epochs to expose count-based switches. Freeze all event-generation seeds, orders, labels, model settings and decision thresholds in the later pre-executable audit specification; never select them after observing V25 outcomes.
- A frozen-source score callable by the evaluator is a **control**, not evidence that the candidate itself retrieved memory.

## Frozen development experiment design

Reuse exactly V23/V24's known synthetic nonlinear source law and two previously seen public input families T1 (cue × second action) and T2 (triple parity). These are familiar **toy reward mappings on the same 36 public feature tuples**, not independently novel worlds.

Run independent cold starts of one source-pretrained bank and one fresh fast bank for each of these four prospective environment sequences, without revealing sequence identity to the learner:

1. S → T1 → S
2. S → T2 → S
3. S → T1 → T2 → S
4. S → T2 → T1 → S

Preserve source pretraining at 576 legal public terminal observations. On each changed or return segment use **at most 12** legal selected terminal feedback observations, with interleaved pre-update predictions and audit-only withheld second-action outcomes. Change segments must have varied legal feedback counts (8, 10 and 12 across predetermined arms), rather than always switching on the same step count. Include matched unchanged-S streams with the same lengths and public cue frequencies to measure false alarms. Use a disjoint fixed public evaluation subset within each segment for prediction and 12-context action regret, retaining V23/V24's definition of unobserved second-action feedback isolation. The evaluator's knowledge of the true reward mapping is restricted to post-hoc scoring.

**Fair baselines using identical public observations, action opportunities, starting source pretraining and compute accounting:**
- V24 protected source bank only; V24 always-fast scratch and V23 destructive single-bank continuous adaptation.
- V24 supervised/oracle-boundary selector as a clearly **privileged upper bound**, not an admissible unlabeled-world comparator.
- Unlabeled conventional residual CUSUM/Page–Hinkley detector with matched 80-feature online ridge predictor, plus a conventional two-expert source/ridge loss-selection arm. Both get the same legal feedback and capacity/cost ledger.
- Zero and observed-mean predictors, and an ablation with source bank intact but no return detector.
- Source score must be reported separately for the protected bank and the actually ACTIVE prediction policy; never replace active performance with retrospective source lookup.

## Frozen metrics and classification

Report for every sequence and host: (a) source SHA before/after; (b) active and source-only absolute error on withheld source-return predictions; (c) first 4/8/12 return-event errors and action regret, (d) post-return reactivation latency in **observed terminal rewards**; (e) false switches in unchanged-source and target segments; (f) target adaptation prediction error and regret; (g) selector decision trace with observed public feedback provenance; (h) bank counts, checkpoint bytes, scalar edge-message counts, CPU/wall time and traced peak Python memory. Normalize comparisons to identical observation windows and report negative cases individually, not only pooled results.

**Engineering qualification** requires exact pinned source and dirty-tree rejection; prereg-before-code chronology; no identity/label/counterfactual leakage; identical canonical case SHA across Linux/Windows; source bank SHA unchanged; exact cold-restore and corruption rejection; fast-bank public-feedback-only updates; no original V22/native code mutation; bounded checkpoint <=12,288 bytes; affected-interface focused controls plus **one final V24→V12 inherited regression**. Any breach: `V25_ENGINEERING_BLOCKED__NO_SCIENCE`.

**Ordered development-outcome gates**, evaluated separately in BOTH S→T1→S and S→T2→S (longer sequences and controls cannot rescue a short-sequence failure):
1. Fail to reactivate the protected source bank within **4 observed return rewards** on either basic return or make any false source reactivation in matched unchanged-target arms: `V25_RETURN_REACTIVATION_NOT_ESTABLISHED__NO_SCIENCE`.
2. Reactivate, but fail to reduce total **ACTIVE** source-return prediction error by >=10% versus always-fast and by >=10% versus matched conventional detector in **both** basic return sequences; or fail to reduce return action regret versus both: `V25_REACTIVATION_WITHOUT_STRONG_CONTROL_GAIN__NO_SCIENCE`.
3. Pass those comparisons but make target prediction error >10% worse than the equal-observation V24 scratch/fast comparator on either T1 or T2, or exceed the checkpoint budget: `V25_RETURN_GAIN_WITH_TARGET_OR_RESOURCE_REGRESSION__NO_SCIENCE`.
4. Only if all cases and the longer-sequence/unchanged controls also pass, classify `V25_BOUNDED_SYNTHETIC_RETURN_REACTIVATION_ENGINEERING_POSITIVE__NO_SCIENCE`.

No outcome establishes native continual intelligence, independent unfamiliar-world transfer, learned semantic task identity, non-transformer general cognition, or scientific first-use. These toy problems were already observed; the V25 experiment is **developmental** regardless of apparent positive performance. Do not revise these gates after looking at results.

## Resource and authority boundaries

Keep candidate banks at exactly 326 learned scalars total (163 target-trainable), the original 8-cell seven-public-channel topology in each bank, and no paid model/API calls. Do not infer retail desktop compute/energy suitability from GitHub runner measurements; a separate consumer-PC qualification is required. Do not merge draft ancestors, change FORGE/CKB-plane/controller, promote any accepted source/checkpoint, enable auto research, waive G29 or write-proxy, submit a queue item, start original-world experimentation, or create a competing scheduler. The next gate is a separate bounded implementation and exact-source deterministic verification, only after this preregistration is committed and source-pinned.
