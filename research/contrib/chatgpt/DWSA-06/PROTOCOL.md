# DWSA-06 — direct weight-path prototype compilation, external trained donor

**Status: preregistered engineering DEVELOPMENT ONLY.** No confirmed scientific trial; no owner first-use, runtime teacher model, original model forward, new source actor, canonical model, integration, merge, or deployment.

## Exact immutable original source and admissible claim

- Existing model source: `MasanneckLab/neural-networks-explained@149a2838309efe6ee5ec9e8c9689e4a321158b7d`.
- `public/assets/digit-model.json` Git blob: `16ea8cf939bfa0f5f21e227d159b11d4ff578eca`; 32,743 decoded UTF-8 characters at inspected connector read. Check input raw Git blob (SHA-1 Git blob identity) before using. Do not fetch by floating `main`.
- `src/models.js` blob `6f95eea88422ceb01b3118e65cd45b9a4c065bd9`; `scripts/train.mjs` blob `1776478a312781e0866f16e1ef237fcbc1092d1a`.
- `LICENSE` blob `dfd27a6c6044c52de150f4a274483ab1e9583310`, MIT, copyright 2026 MasanneckLab; retain copyright/license notice when distributing source or substantial licensed material.
- Observed donor: 35→24→16→12→10 ReLU/softmax network; 1,598 float parameters; 80,000 stochastic gradient updates, seeded 20261022. Evaluated by its publisher on 2,000 newly corrupted draws (seed 571932), 1,986 correct per claimed metadata.
- This is not real handwriting. Only 10 authored original 5×7 bitmap templates, 7% independent bit-flip noise in both fitting and source training, **same world/law family**. The original model is not owner-authenticated Yggdrasil training state.
- Accepted Yggdrasil baseline: `main@5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; DWSA-01–04 archived in **closed, unmerged** PR #1335. Never resurrect/tune the failed 320-byte affine/tanh recipes.

## Fresh zero-teacher, architecture-distinct recipient

Aim: recover class-specific 35-bit feature prototypes from **static learned weight-route signs**. No input is passed through the donor, and no source model forward, weight gradients, teacher outputs or activations are read. Donor biases are intentionally unused.

1. Validate exact model shape, all finite numeric weights, exact metadata and fixed layer order.
2. Compute a fixed signed total path-influence matrix `S = W_last @ W_2 @ W_1 @ W_first` by plain matrix multiplication of stored weights (10×35). This is a **linear path statistic, NOT the donor Jacobian or a faithful nonlinear functional approximation**.
3. For class `c` and input bit `i`, define `margin = S[c,i] - mean_{j != c}(S[j,i])`; compile bit 1 iff `margin > 0`, otherwise 0. No template, label, extra data, or student evaluation may influence the threshold.
4. Serialize 10×35=350 bits row-major big-endian within each byte, zero-pad final 2 bits. Exactly **84 bytes**: `DWP6` magic 4; version 1 byte =1; reserved 1 byte =0; classes byte=10; feature count byte=35; 44 packed bytes; SHA-256 of 52-byte prefix. Reject size/checksum/padding/header/bit-count errors. Three cold restores and duplicate compilation must be identical.
5. Student is a fixed-footprint **tokenless native Hamming prototype table**, NOT the donor MLP: choose class whose 35-bit prototype has minimum Hamming distance to incoming observed 35-bit vector. Tie → numerically smallest class; no learning or trainable state in the recipient. No donor architecture is installed.

## Locked evaluation and controls

- Ground truth comes only from the publisher's *authored* bitmap templates in `src/models.js`. Do not use templates in the weight-only compilation path.
- 2,000 newly corrupted same-template observations: each class 0..9 repeated 200 times, exactly 35 independent bit-flip draws with probability 0.07 per example, deterministic Mulberry32 `seededRandom(637127)` from pinned `src/models.js`. **No original model, source actor or teacher forward**. This eval seed differs from publisher's training (20261022) and earlier evaluation (571932); true sample independence not verified beyond deterministic RNG streams, and **not unfamiliar law/world**.
- Strong supervised comparison: 10×35-bit prototype majority fitted from 20 newly generated labeled examples per class, using the same seed function with seed 492615, and the same 84-byte recipient. Per bit majority > 10 -> 1; tie -> 0. Fit only; do not look at eval outputs.
- Exact symbolic source-template Hamming baseline, same 84-byte capacity. This is an oracle given the original true 10 templates; strongest lawful control.
- Shuffled-label control: deterministic one-slot cyclic permutation of compiled class-prototype labels.
- Source-blind control: 350 independent Bernoulli(0.5) bits generated with seed 774113, same 84-byte codec.
- No-signal control: always class 0 (10% balanced accuracy).
- Evaluate exact 0/1 classification accuracy, per-class totals/errors, accuracy gap vs sham/source-blind/strong controls, confusion matrix, source bits and bytes, reproducibility and timing/resource. Every method receives the same 2000 labeled observations; all train/eval sets and thresholds frozen before execution.
- Predefined **development signal PASS** iff SHA/source/codec/restores/zero-donor controls pass, weight-derived student accuracy >= 70%, >=30 percentage points ahead of both shuffled and source-blind controls. Failure => `DWSA06_STRUCTURAL_SIGNAL_NO_GO`. Independently report whether it beats same-byte supervised and symbolic controls (expected unlikely). Even DEV_PASS is NOT scientific advantage.
- No codebook variants, alternate thresholds, fit on eval, seed switching, new model parameters, hidden original-world first-use, any local or remote teacher forward, or post-result tuning.

## Qualification and significance

ENG local/CI: focused tests, version/shape/custody/checkpoint tests; full candidate-SHA Linux and Windows final regression plus G29 atlas companion *separately required* before acceptance. Do not dispatch an unapproved workflow or reproduce unavailable runner custody.

SCIENCE: At most source-only cross-architecture *structural association* transfer within a tiny synthetic same-law label task. **No causal learning, new-world transfer, meaningful cumulative intelligence, teacher functional fidelity, or scientific gain claim.** Synthetic source generator and exact Hamming template are known; symbolic/control superiority must be disclosed; owner protected first-use remains NO-GO.

DEPLOYMENT: none. Only Unified Causal Intelligence Amalgam Work owns candidate integration and canonical checkpoint continuation; this contributor is research-only.
