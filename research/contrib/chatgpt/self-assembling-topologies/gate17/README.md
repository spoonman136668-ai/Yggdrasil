# Gate 17 — Fitting unfamiliar nonlinear causal functions

**SCIENCE: BOUNDED NONLINEAR REPRESENTATIONAL DEVELOPMENT SIGNAL. STRUCTURAL SUPERIORITY FAIL. Native model integration and first-use NOT DONE.**

## Frozen source chain and replay

- Protocol [prereg.json](./prereg.json): committed before source/results at `47b2597c81ca990cf5947c59be145fbb972d0af4` (blob `7d03014e65d7fa5b0c87d6c68a2a5ff431b06250`).
- Executable [run.cjs](./run.cjs): committed before first primary outcome at `842f0a144885a03f92befebb801f04b741c894b9` (blob `d58693faa6e7df3427dad09eb004d98fb2186063`).
- [result.json](./result.json): exact synthetic results sealed at `ea230a995b3aa0162fdc9d2e5a09e19a3569dfc1` (blob `d5e4552cf92b494c19abaaed9ffa523dd044999f`) after first source execution and independent exact recomputation, no source/threshold edits.
- [audit.cjs](./audit.cjs): independent Boolean truth-table/model-order and numeric receipt audit, *not* a second independent learner.
- [provenance.json](./provenance.json): source and seed custody, resource and scientific limitations.

Run from the repository root (Node.js, no external packages):

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate17/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate17/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate17/audit.cjs
```

## Experiment

Unlike Gate 16's known XOR/Walsh representation, the learner may fit **any binary truth table on an inferred subset of one, two or three input variables**. True operator names and parent identities are hidden. Source families, used only by the evaluator, are: majority-of-three (61000–61031), 3-input multiplexer (62000–62031), randomly sampled Boolean tables that depend on all three inputs (63000–63031), 3-input XOR (64000–64031), pair XOR (65000–65031), unary copy/invert (66000–66031), and independent fair labels (67000–67031).

Each of 224 fresh seed trials creates two contexts, with **three shuffled full-factorial rounds of 32 interventions** per context. The first 64 actions select the minimal useful input subset using **leave-one-out Brier plus an explicit parameter-count penalty**. The next 32 *training* actions independently validate the selected subset; 32 additional interventions have separate deterministic noise and form the untouched evaluation. Total **448 worlds, 43,008 training and 14,336 held action/outcome records**. Every comparator sees the *same* interventions and labels.

The adaptive arm considers five unary and ten pair subsets first. It constructs/evaluates ten three-parent subsets from disjoint unary-plus-pair combinations only when the strongest lower-order model's training LOO Brier is at least **0.09**. Higher-order hypotheses must exceed the best lower-order training-validation Brier by at least **0.025**, and achieve validation Brier <=0.18. The final chosen subset is refit on 96 training events. This is a fully specified small Boolean lookup family, **not open-ended operator invention**, autonomous feature discovery in arbitrary modalities, or general causal intelligence.

Controls are a **fixed-full model of identical capacity and identical prediction rule** (always computes higher-order candidates, even when not needed), a truncated unary/pair model, the frozen Gate16 parity-only representation, the complete 32-action Laplace lookup table, and an **equal-saved-state** exact Beta-binomial Bayesian model over all 26 null/unary/pair/triple subsets. All six arms can serialize **388 bytes of context training records and route metadata**. The Bayesian model also uses more transient posterior/sufficient-statistics memory and computational work, so 388 bytes is **persisted state**, not equal process-level RAM or cost. Feature-scoring and Bayesian-fit work counts exclude some prediction-time operations; they are diagnostic operation counts, not full wall time, energy or end-to-end efficiency.

## Frozen held Brier (lower is better)

| Source world | Adaptive generic | Same-state fixed | Parity-only | Full 32-action table | Bayesian subset mixture |
|---|---:|---:|---:|---:|---:|
| Three-parent majority | **0.0536960** | 0.0536960 | 0.2502752 | 0.0829492 | **0.0508823** |
| Three-parent MUX | **0.0534319** | 0.0534319 | 0.2506489 | 0.0844922 | 0.0534448 |
| Random essential three-parent truth table | **0.0635930** | 0.0635930 | 0.2170531 | 0.0839453 | **0.0535853** |
| Three-parent XOR | 0.0522062 | 0.0522062 | **0.0465862** | 0.0823242 | 0.0522062 |
| Pair XOR | 0.0528201 | 0.0528201 | **0.0514301** | 0.0854688 | 0.0529267 |
| Unary | 0.0588652 | 0.0588652 | **0.0587421** | 0.0903320 | 0.0589417 |
| Independent random labels | 0.2515391 | 0.2515391 | 0.2515391 | 0.2808789 | 0.2537454 |

Exact three-parent mask identification: **62/64 majority**, **64/64 MUX**, **49/64 random essential functions**, and **64/64 XOR parity**. No three-parent route was falsely installed on 64/64 independent worlds. All prespecified nonlinear recovery/error/control thresholds pass. Compared with parity-only, held Brier improvements are **+0.1965792** on majority (paired normal 95% CI [0.1891921,0.2039662]), **+0.1972170** on MUX ([0.1886948,0.2057392]), **+0.1534601** on random essential functions ([0.1419003,0.1650199]).

**Critical controls and negative findings:** The fixed-full 388-byte baseline matches **every held forecast** of the adaptive learner, across **all 224 seeds**. It shows **no predictive self-assembly advantage**, paired mean and confidence interval [0,0]. The Bayesian reference performs better on random essential functions by 0.0100077 Brier with paired CI [0.0052858,0.0147297], inside the prespecified <=0.015 deficit but a real limitation. On known XOR parity, the older specialized parity-only learner is better (0.0465862 vs 0.0522062 Brier). The adaptive learner reduced deterministic candidate-fit comparison work by **35.67%** compared with the fixed-full control on simple pair/unary cohorts, but this **does not prove end-to-end speed or efficiency superiority**, especially against practical low-compute baselines.

**Held-out limitation:** All 32 possible intervention settings occur in each of the three training rounds, so the held-out round tests new stochastic outcomes on **previously seen interventions**, not response to entirely novel action vectors or real unseen environments. The unknown operator labels and new seeds are controlled synthetic variation, not independent real-world transfer.

**Cold-state limitation:** All **224/224 seed trials** exactly reproduced predictions after restoring 388-byte persisted records. Native Yggdrasil cold checkpoint retention, model training after restore, multi-world interference, cumulative reasoning and generalization to larger input alphabets were **not tested**.

## Disposition

**ENGINEERING:** Frozen protocol → exact-source commit → first primary outcome → sealed result. Source-level verification complete; exact-head dual-platform full repository regression and audit results require separate CI readback.

**SCIENTIFIC:** Restricted nonlinear relation acquisition is now demonstrated in a synthetic finite Boolean setting. **Structural-superiority FAIL**, no real-world transfer or independently qualified native intelligence improvement. Do not merge into Yggdrasil's accepted learner.

**DEPLOYMENT:** None. Accepted main and central Unified Causal Intelligence Amalgam checkpoint owner untouched. Keep PR #1340 draft and unmerged. Next decisive study should test **compositional transfer to genuinely unobserved interventions or environments**, while comparing against fully fitted Bayesian/flat and matched compute baselines, rather than inventing another gate around a cosmetic threshold.
