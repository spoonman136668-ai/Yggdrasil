# DWSA-BR01 — fixed-budget donor-weight prototype correction (DEV preregistration)

**Frozen before any BR01 candidate evaluation.** Independent, synthetic same-template development screen only; no native Yggdrasil checkpoint, training owner, protected first use, runner dispatch, merge, accepted baseline or production integration.

## Provenance and question
- Accepted Yggdrasil main: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; DWSA-06 original negative: [PR #1347](https://github.com/spoonman136668-ai/Yggdrasil/pull/1347).
- Public pretrained donor: `MasanneckLab/neural-networks-explained@149a2838309efe6ee5ec9e8c9689e4a321158b7d`.
- Weights `public/assets/digit-model.json`: Git blob `16ea8cf939bfa0f5f21e227d159b11d4ff578eca`. Generator `src/models.js`: Git blob `6f95eea88422ceb01b3118e65cd45b9a4c065bd9`.
- Train source is publicly MIT-licensed, original third-party copyright/notice remains upstream. No donor runtime, teacher forward calls, donor activations, prompts, env actions or source modifications.
- Hypothesis: a budgeted, calibration-gated correction of the DWSA-06 weight-derived 350-bit recipient recovers >=5.0 percentage points on new same-law observations without losing >2.0 points under stronger corruption. This is NOT a hypothesis of superiority over a fully fitted control, general-world transfer, or autonomous intelligence.
- Preserve DWSA-06 exact prototype compilation: weight matrices `S=W4@W3@W2@W1` without biases, bit `S[c,i]-mean(S[j!=c,i])>0`, 10 35-bit class prototypes, min-Hamming / lowest-class tie break.

## Frozen deterministic screen
- Only training observations can select edits. 20 labeled examples per class at independent 7% bit-flip noise; Mulberry32 seed **504827**, class-major generation, bit-major within sample; 200 total labels. NO held-out evaluation input or output can affect edits.
- Determine each row/bit majority on its own class's 20 training samples. Propose an edit only when majority is `>=16` votes for 1 or `<=4` for 0, and differs from compiled donor bit. Sort all proposals by descending majority confidence `abs(ones-10)`, then ascending class index and ascending bit index.
- Bounded repair: process proposals once in that order, at most **48** accepted bit flips in total and **12** per class. Accept only if whole training-set classification count improves strictly and classification correct count does not fall for ANY individual class (compared to state immediately before proposed edit). No retries or threshold/seed changes.
- Same capacity and no extra runtime memory: compiled, corrected and supervised baselines all store 350 bits, plus common identical container overhead excluded from comparative model size. Selection uses source labels as teacher-free observed calibration; 200 calibration labels are charged.
- Controls: (1) original DWSA-06 weight-only (zero corrections); (2) bounded repair starting from 350 all-zero bits with identical algorithm/data/budget; (3) majority-fitted same-350-bit bank on the identical 200 observations with tie ->0; (4) exact authored-template Hamming upper bound; (5) donor bank with all 350 bits replaced by fitted bank (explicitly UNBOUNDED, not a matched repair-control).
- Outcomes are exact correct / 2000, per class and percentage point gap to strongest fitted control on two fresh **unseen-by-BR01** deterministic streams: seed **781223** at 7% flips, and seed **781229** at 12% flips. 200 samples per class, class-major and bit-major. Report train-set correct counts, attempted/accepted/rejected proposals, acceptance by class, and full-state 350-bit pack/unpack parity across three cold copies. Retention proxy is performance under 12% corrupted observations; NOT historical multiworld retention.
- Screen condition: donor+bounded >= donor-only +5.0 percentage points on 7% test; and donor+bounded >= donor-only -2.0 percentage points on 12% shift; 3 exact restores. Separately call out whether stronger fitted control still wins; any outcome remains same-family DEV ONLY.
- No changes after examining BR01 scores. No claim of independent native transfer, functional causal memory, lower cost than an already trained supervised baseline, or SCIENTIFIC_PASS.

## Follow-through
Use the same exact pinned donor bytes and original generator; refuse source SHA mismatch. Save implementation, computed scores (including negative), and verification receipts on this research branch only. Focused tests may run in an isolated local evaluation process. Full exact-candidate G29 atlas and Linux/Windows root regressions must complete before engineering qualification of integration; protected original source use needs separate owner authority. Do not create an additional training owner or competing persistent learner.
