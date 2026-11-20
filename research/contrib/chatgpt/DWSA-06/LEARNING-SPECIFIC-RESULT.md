# DWSA-06-L result — trained vs precisely matched untrained weight-route controls

## Verdict

**LEARNING_SPECIFIC_DEV_SIGNAL = PASS** on the *same previously used* synthetic ten-template digit task, with source-only trained weight path + **no teacher inference**.

- ENGINEERING: connected source read, SHA-verified donor files and deterministic V8 evaluation **PASS**; exact Node command, wrapper checks, mandatory candidate-SHA full repository Linux/Windows regression and source atlas companion **UNVERIFIED/FAILING** (check latest CI). No recipient integrated.
- SCIENCE: narrow evidence of **training-dependent task alignment** in the static weight paths, not independent test of generalization or causal learning; **SCIENTIFIC_PASS=FALSE**. The stronger fitted and exact-symbolic controls still win.
- DEPLOYMENT: **NONE**; no native cumulative learner, checkpoint, owner, source first use, training, controller or accepted main changes.

## Preregistered source and frozen variables

Frozen prereg **before scoring**: `56341888b193d98e8aa168ed61fe8f23dc030d98` (`LEARNING-SPECIFIC-ABLATION.md`).
Pinned original third-party repository: `MasanneckLab/neural-networks-explained@149a2838309efe6ee5ec9e8c9689e4a321158b7d`.
Donor `public/assets/digit-model.json` Git blob `16ea8cf939bfa0f5f21e227d159b11d4ff578eca`; `src/models.js` blob `6f95eea88422ceb01b3118e65cd45b9a4c065bd9`; `scripts/train.mjs` blob `1776478a312781e0866f16e1ef237fcbc1092d1a`, MIT license blob `dfd27a6c6044c52de150f4a274483ab1e9583310`.

- Exact original architecture: 35→24→16→12→10, 1,598 stored parameters, 80,000 recorded SGD updates, publisher training seed 20261022.
- For each random initialization, reproduce the publisher's row-major `(Mulberry32(seed)-0.5)*sqrt(24/fan_in)` weight formula, before any training update. Biases equal source init but remain unused in all weight-path calculations. Thus **identical architecture, distribution, representational capacity and 350-bit student** for all 16 controls.
- Reuse original `S=W4@W3@W2@W1`, class-minus-other score positive bit threshold, 10×35 binary prototypes, Hamming student. No logits or teacher outputs from source model.
- Exact frozen seeds: `20261022,101,202,303,404,505,606,707,808,909,1001,2002,3003,4004,5005,6006`.
- Evaluation: 2,000 synthetic corruption draws (200/class) from **the same ten templates as donor training**, original DWSA-06 evaluation seed 637127 with 7% bit flips. NO unseen symbol family, unfamiliar world or source-owner first use. The previously observed 80.75% trained statistic is not a blind predeclared scientific endpoint.

## Result — source-blind INIT versus trained WEIGHTS

| Source | Seed | Correct / 2000 | Accuracy |
| --- | ---: | ---: | ---: |
| **Trained source weights** | 20261022 (after 80,000 updates) | **1615** | **80.75%** |
| Exact original initialization | 20261022 (before update 1) | 230 | 11.50% |
| Untrained | 101 | 323 | 16.15% |
| Untrained | 202 | 310 | 15.50% |
| Untrained | 303 | 147 | 7.35% |
| Untrained | 404 | 135 | 6.75% |
| Untrained | 505 | 105 | 5.25% |
| Untrained | 606 | 166 | 8.30% |
| Untrained | 707 | 117 | 5.85% |
| Untrained | 808 | 108 | 5.40% |
| Untrained | 909 | 427 | **21.35% (best random)** |
| Untrained | 1001 | 160 | 8.00% |
| Untrained | 2002 | 186 | 9.30% |
| Untrained | 3003 | 308 | 15.40% |
| Untrained | 4004 | 391 | 19.55% |
| Untrained | 5005 | 254 | 12.70% |
| Untrained | 6006 | 125 | 6.25% |

16 untrained controls: **mean 10.9125%; min 5.25%; max 21.35%**. Trained-minus-strongest = **+59.40 percentage points**; trained-minus-exact source initialization = **+69.25 pp**. Both clear frozen **+15 pp** margins; trained 80.75% exceeds frozen 70% minimum. No seed/threshold change or control selection after scoring.

Previously recorded fixed-footprint controls still matter: shuffled trained-label mapping 2.95%, blind random prototype 12.30%, **conventional fitted 84-byte supervised prototype 99.25%** (20 labeled training examples/class), symbolic exact-template 99.25%. The weight-route extraction remains **18.50 pp below** the strongest same-capacity trained/symbolic control. Thus **no conventional advantage**, science gain, transfer or intelligence claim.

## Precision limits

This gate differentiates *trained from untrained weights* in one model and one synthetic source family. It does not prove teacher-free assimilation independent of label/task identity: the original model's output channels represent known digit classes, and the recipient uses that mapping. Neither the native 84-byte seal (unverified exact Node execution), source-trained model functional equivalence, non-template transfer, robustness across different trained donors, cold cognitive retention, multiworld causality, nor whole-process cost is established.

Original model inference calls: **0**. Original environment/source actions: **0**. Trained new models in this gate: **0**. The only compiled model evaluations are compact Hamming students built from stored weights or generated untrained weights.

Code: `untrained_ablation.mjs` in this branch, run using exactly 3 pinned source files in declared CLI order. It was committed **after** prereg and after evaluation; local full Node exact-file execution is not independently verified and must be tested on a qualified local checkout before reporting engineering PASS at candidate SHA.

**Follow-up science:** independently trained, licensed donor(s), genuinely unfamiliar held causal worlds, matched fully trained controls, strict custody and owner-authorized actions only. Preserve source-first-use restrictions documented in Yggdrasil issue #426. Do not promote into Unified Amalgam or merge solely on this DEV signal.
