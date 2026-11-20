# DWSA-06-M — frozen four-layer train/init intervention matrix

**Preregistration: development-only, before calculating any layer-mask outcomes.** Research contribution to draft Yggdrasil PR #1347; not an experiment on the accepted model, not original-world first-use, not training, not donor forward inference, not a model promotion.

## Question

Does the previously observed DWSA-06 350-bit static signed-path signal (80.75% accuracy) require mutually coordinated changes across the donor's four trained layers, or can most of the information be attributed to only a subset of trained layers? This is a *weight-space mechanistic intervention*, not action-consequence or causal-world learning.

## Frozen source and derivation

- Third-party MIT donor `MasanneckLab/neural-networks-explained@149a2838309efe6ee5ec9e8c9689e4a321158b7d`.
- Donor `public/assets/digit-model.json` Git blob `16ea8cf939bfa0f5f21e227d159b11d4ff578eca`; `src/models.js` blob `6f95eea88422ceb01b3118e65cd45b9a4c065bd9`; `scripts/train.mjs` blob `1776478a312781e0866f16e1ef237fcbc1092d1a`; MIT `LICENSE` blob `dfd27a6c6044c52de150f4a274483ab1e9583310`. Reject source drift. Code/weights remain upstream, never committed to Yggdrasil.
- Four weight matrices, architecture 35→24→16→12→10; no biases enter the existing DWSA-06 compiler. Trained donor was recorded as 80,000 SGD updates from seed 20261022; **no teacher execution in this gate**.
- Reconstruct **exact initial** weights from the source's deterministic `seededRandom(20261022)`, using row-major sequential draws `(rand()-0.5)*sqrt(24/fan_in)` for every weight in source train order, with no training.
- For *each* of 16 bitmasks `m = 0..15`, take layer index `i = 0..3` from original trained donor weights iff bit `(m >> i)&1 == 1`, otherwise from its original seed-20261022 untrained initialization. No retraining or rescaling. Produce the same signed path statistic `S = W4 @ W3 @ W2 @ W1`, class-versus-other margin bit `>0` and 350-bit/84-byte Hamming nearest-prototype recipient as frozen DWSA-06. Do **not** execute the donor, its hidden activations or its nonlinear forward function. The interventions are in the *static weights being compiled*.
- Full mask `15` MUST reproduce original 1615/2000 (80.75%); zero mask `0` MUST reproduce 230/2000 (11.50%). Otherwise report INVALID / STOP; never adjust calculation until outcome matches.
- Evaluate each of 16 compiled students on the exact same 2,000 historical DWSA-06 same-template newly corrupted fixtures, 200/class, 7% bit flips, `seededRandom(637127)`. The source's 10 known true symbol templates may be used for evaluation only; no original model inference, no new protected source actions and no adaptation from scored labels. These are **not** genuine unfamiliar worlds or independently fresh scientific heldout data. All 16 masks have the same topology, statistical encoder and 350-bit student footprint.
- Report per-mask source layer identities, exact correct count, accuracy, per-class correct counts, all four leave-one-trained-layer-out masks (i.e. 14,13,11,7), best mixed 1..14, and full-vs-best mixed percentage-point margin.
- **Frozen mechanistic criterion:** `INTERLAYER_DEPENDENCE_DEV_SIGNAL` only if full 15 has >=70% accuracy **and** exceeds *every* mixed mask (1..14) by at least **10.00 percentage points**. Otherwise `INTERLAYER_DEPENDENCE_DEV_NO_GO`. Also report a descriptive additive interaction contrast `score(15)-score(0) - sum_i(score(1<<i)-score(0))`; its sign is exploratory and must not be a second success criterion.
- Maintain prior strongest matched 84B supervised/symbolic reference at 99.25%. Even a passing result demonstrates only that multi-layer trained weight-space route structure cooperates on familiar synthetic labels. It does not prove general cognitive knowledge, novel-world transfer, teacher equivalence, retention or science superiority.
- Verify hashes, zero donor inference, zero original environment actions, no trained weight writes; no trials beyond 16 masks, seed changes, threshold changes, extra model selection or retrospective relabeling.

ENGINEERING: independent portable static extraction with exact pinned source; full Node execution on exact original files, candidate Linux+Windows full regression and G29 atlas remain separate requirements. SCIENCE: development mechanism check only, SCIENTIFIC_PASS prohibited. DEPLOYMENT: NONE. Accepted main, existing Amalgam native training checkpoint/owner and source-first-use authority remain unchanged.
