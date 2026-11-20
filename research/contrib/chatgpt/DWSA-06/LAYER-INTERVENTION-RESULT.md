# DWSA-06-M — signed weight-path layer-intervention outcome

**Frozen gate: INTERLAYER_DEPENDENCE_DEV_SIGNAL = PASS.** This is a same-family static-weight **development** study only, not scientific acceptance, native causal learning, or model deployment.

## Source, preregistration, and zero-teacher constraints

- Prospective protocol committed **before any mask scoring**: `416429f6ea77d189876289b098718d5e44438775`, `LAYER-INTERVENTION-PROTOCOL.md`.
- Third-party MIT model `MasanneckLab/neural-networks-explained@149a2838309efe6ee5ec9e8c9689e4a321158b7d`; pinned donor checkpoint Git blob `16ea8cf939bfa0f5f21e227d159b11d4ff578eca`, source templates/RNG blob `6f95eea88422ceb01b3118e65cd45b9a4c065bd9`, actual training script blob `1776478a312781e0866f16e1ef237fcbc1092d1a`. Exact original source identities rechecked by connected GitHub read before scoring.
- Recreated source's exact initial seed-20261022 four weight matrices using original row-major Mulberry32 formula `(random-0.5)*sqrt(24/fan_in)`; 16 fixed combinations take each of the 4 weight matrices from trained donor or exact initial tensors. No source model forward, teacher-generated output, gradient step, donor activation, or original-world action.
- Each combination compiles into the same 350-bit structural Hamming prototypes. 16 predictions on *the identical* 2,000 previous same-template, 7%-bit-flip synthetic cases; classes 0..9 balanced, original evaluation seed 637127, source ten symbols unchanged. No novel symbol class, unfamiliar family or independently untouched scientific held-out. There is no 16× new source first use.
- Full-trained mask `15` reproduced **1615/2000 (80.75%)**; full-initial mask `0` reproduced **230/2000 (11.50%)**. All 16 mask scores were computed once under the frozen rule; code/repro script is `layer_intervention.mjs`.

## Exact mask outcomes

A set in the trained-layers column means **trained donor weights** used for that layer (indices are input-first 0 through output layer 3); all other layers are exact original untrained weight matrices.

| Mask | Trained layers (0–3) | Correct / 2,000 | Accuracy |
| ---: | --- | ---: | ---: |
| 0 | none | 230 | 11.50% |
| 1 | 0 | 924 | 46.20% |
| 2 | 1 | 580 | 29.00% |
| 3 | 0,1 | 714 | 35.70% |
| 4 | 2 | 588 | 29.40% |
| 5 | 0,2 | 808 | 40.40% |
| 6 | 1,2 | 687 | 34.35% |
| 7 | 0,1,2 | 943 | 47.15% |
| 8 | 3 | 273 | 13.65% |
| 9 | 0,3 | 772 | 38.60% |
| 10 | 1,3 | 800 | 40.00% |
| **11** | **0,1,3** | **1,333** | **66.65% (best mixed)** |
| 12 | 2,3 | 569 | 28.45% |
| 13 | 0,2,3 | 1,312 | 65.60% |
| 14 | 1,2,3 | 785 | 39.25% |
| **15** | **0,1,2,3** | **1,615** | **80.75% (all trained)** |

Frozen success required full-trained >=70% and greater than **every** partially initialized control by at least **10 percentage points**. Measured gap: **80.75%-66.65%=14.10 percentage points**. Gate **PASS**.

Leave-one-layer-at-initialization accuracy: layer 0→39.25%; layer 1→65.60%; layer 2→66.65%; layer 3→47.15%.

Descriptive **additive interaction contrast**:
`acc(15) - acc(0) - sum_{i in (0,1,2,3)} (acc(1<<i)-acc(0)) = -0.0300`, i.e. **−3.00 percentage points**. This does not support the stronger interpretation of super-additivity; the predefined result only shows full trained configuration beats every tested hybrid. It does **not** imply all trained layers are individually necessary or general intelligence is synergistic.

The strongest earlier same-capacity conventional supervised and exact-symbolic controls each achieved **99.25%**, beating this full-trained signed-path recipient by **18.50 percentage points**. The result therefore shows training-dependent cross-layer **task alignment**, not competitive advantage or transfer of novel causal knowledge.

## Evidence and qualification gaps

- Source-only numerical derivation executed in the connected V8 environment, with frozen masks, signatures checked by GitHub, all 16 measured counts and exact full-vs-initial reproduction. No teacher executed. Exact code committed at `research/contrib/chatgpt/DWSA-06/layer_intervention.mjs`; a second syntax parse of its module body in V8 passed.
- Committed Node script specifies per-mask 84-byte SHA-protected checkpoints, 3 cold restores per mask, 4 tamper-negative tests and exact input Git-blob checks. **These Node paths have NOT been executed with actual pinned source files on a qualified Node runtime.** Do not claim checkpoint integrity tests PASS merely from the source.
- The isolated V8 computation reports no measured total process cost. Local tooling, G29 generated atlas and **full final candidate-SHA Linux+Windows repo regression** remain unqualified; earlier branch G29 failed stale generated atlas, before DWSA tests.
- No accepted `main`, persistent learner, unified Amalgam coordinator, training/first-use custody, controller, environment, CI workflow or deployment changed. Keep PR draft; no independent scientific promotion.

**Verdict:** ENGINEERING: SOURCE-ONLY MECHANISTIC DEV PASS, full qualification UNVERIFIED. SCIENTIFIC: DEVELOPMENT SIGNAL PASS, independently reproducible unfamiliar-world gain **UNVERIFIED**, SCIENTIFIC_PASS=FALSE. DEPLOYMENT: NONE. Owner action: no model integration; preserve as contributor research for sole Amalgam coordinator.
