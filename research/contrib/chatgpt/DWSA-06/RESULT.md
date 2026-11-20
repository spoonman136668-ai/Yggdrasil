# DWSA-06 — signed-path weight-only prototype DEV signal

**Disposition:** DEVELOPMENT_SIGNAL_PASS (not SCIENTIFIC_PASS); no accepted Yggdrasil change, integration, training, or deployment.

## Frozen custody and method

- **Preregistered before any score:** commit `d379477033cab1d9dd72c8cdb5e69bedf574f339` in this branch.
- **Previously trained third-party source:** `MasanneckLab/neural-networks-explained@149a2838309efe6ee5ec9e8c9689e4a321158b7d`.
- Committed donor weights file: `public/assets/digit-model.json`, exact Git blob `16ea8cf939bfa0f5f21e227d159b11d4ff578eca`. Authored templates and RNG in `src/models.js`, Git blob `6f95eea88422ceb01b3118e65cd45b9a4c065bd9`. Training program `scripts/train.mjs`, blob `1776478a312781e0866f16e1ef237fcbc1092d1a`.
- Original `LICENSE`, blob `dfd27a6c6044c52de150f4a274483ab1e9583310`, MIT. Copyright (c) 2026 MasanneckLab. Attribution/notice preserved; third-party code and model artifacts remain upstream.
- Source model: 1,598 weights/bias parameters, 35→24→16→12→10, recorded 80,000 gradient steps. This experiment **did not run it** and did not invoke any teacher inference.
- Method: compose ONLY weight matrices into signed path-statistic `S = W4 @ W3 @ W2 @ W1`, then for class c, bit i set a stored bit iff `S[c,i] - mean(S[other classes,i]) > 0`. This creates ten 35-bit prototypes (350 bits / 44 packed payload bytes); class prediction uses minimum Hamming distance, tie → lowest index. The **specified** SHA-protected checkpoint is **84 bytes** (8 header, 44 payload, 32 digest), not a compressed equivalent donor neural network.
- Source-model-output data, activations and teacher forward calls: **0**. Original-world interventions: **0**. Accepted Yggdrasil checkpoint touched: **none**.

## Frozen 2,000-case evaluation results

2,000 held-out *random draws*, seed 637127, generated from the **same ten author-written symbol templates and 7% bit-flip corruption law** as source training. These are newly sampled observations with a different seed from training 20261022 and publisher's previous evaluation 571932. They are **not** novel symbols, unfamiliar causal laws, independent-world transfer or a proof of source model prediction quality.

| Recipient/control | Correct / 2,000 | Accuracy |
| --- | ---: | ---: |
| **Weight-path inferred 350-bit prototypes** | **1,615** | **80.75%** |
| Shuffled-output-label prototypes | 59 | 2.95% |
| Source-blind random prototypes | 246 | 12.30% |
| Always class zero | 200 | 10.00% |
| **Directly supervised, same-84B prototype control** | **1,985** | **99.25%** |
| **Exact symbolic 10-template Hamming control** | **1,985** | **99.25%** |

- Preset development condition: >=70% accuracy and >=30 percentage points ahead of *both* shuffled and blind controls. **PASS**: 80.75% and gaps **77.80** and **68.45** percentage points, respectively.
- Per-class correct counts (each out of 200), class 0 through 9: `[198,106,124,195,196,176,194,65,180,181]`. Strong heterogeneous errors, notably classes 1 and 7.
- Direct fitted prototype learned from only 200 separately generated labeled examples (20/class, seed 492615) wins by **18.50 percentage points** with identical 350-bit classification capacity. The symbolic true-template control ties.
- The benchmark is *supervised synthetic symbol recognition*, NOT causal discovery, action-consequence reasoning, cold retention, non-template transfer, or a meaningful intelligence gain.

## Engineering evidence and limitations

- Read-only source ingestion and pure JavaScript weight-composition + deterministic test generation ran successfully inside the connected source evaluation environment. Exact original pinned Git blobs checked **before** score. The scorer's algorithmic function body was reused as the exported `analyze` source in `run.mjs`.
- The committed `run.mjs` additionally provides Git-blob custody verification, proposed 84-byte SHA256 checkpoint packing/restore, three cold restores and five tamper tests. **These Node wrapper / checksum / cold restore paths were not run end-to-end on the original source in this environment; treat as UNVERIFIED until a qualified reproducible invocation.**
- `run.mjs` source commit `4d7837460914c7e71baf91b390a51dba3f2cc6df` fixed its Git blob NUL byte delimiter after initial commit; no source scores changed and no post-result parameter, seed, threshold or method tuning occurred.
- Source-only math and observational score development PASS. Native checkpoint mechanics and exact-SHA Linux/Windows full regression/G29 atlas UNVERIFIED. No deployment, no native model import or mutation, no runner/workflow dispatch.
- Future qualified scientific check needs a separately frozen disjoint **world/mechanism** and stronger matched data/information/compute controls; the same-template result cannot satisfy that condition. Only Unified Causal Intelligence Amalgam Work may review proposed native integration.

**Plain interpretation:** A frozen map of learned weight *routes* contains statistically useful class associations. A much cheaper same-byte supervised template learner performs considerably better. This is feasibility evidence for teacher-free structure extraction, not proof of superior learning, causal understanding, autonomous training, or scientific gain.
