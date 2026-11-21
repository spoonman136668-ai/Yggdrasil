# Gate 13 — Information-seeking interventions and cold continuation

**SCIENCE: MIXED DEVELOPMENT / NO-GO for full preregistered acceptance.** No native Yggdrasil model, checkpoint, first-use, accepted main, or central Amalgam integration was touched.

## Evidence and exact custody

- [Preregistered protocol](./prereg.json) committed at `756b97735c9042fcd2d1d3534c37ae240151d9e0` **before** experiment source or primary results.
- [Frozen executable experiment](./run.cjs) committed `ef87941f7350534fbc00566e6cf7b5fdd280218f`, Git blob `ade143052b9d36a3f7d2c94a96adebaec23c440f`. No source or protocol edits after primary evaluation.
- [Sealed synthetic results](./result.json) committed `850c638c66061b5c6732f2fba4be2052add0e174`, Git blob `f1ea631f143ef12dce416b0b68d38dc65eb9819f`.
- [Independent mathematical and receipt audit](./audit.cjs) committed `4288f055b380fff0c1da96dafc7ba377bdaa45a6`. This is a separate audit of model-family cardinality, counterexamples, Brier comparisons, thresholds, and checkpoint size. It is **not** a second independent Bayesian learner implementation.
- [Provenance](./provenance.json): frozen seeds, controlled feedback, resource accounting and scientific limitations.

Exact result reproduction, from repository root using Node.js without added dependencies:

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate13/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate13/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate13/audit.cjs
```

## Causal/action protocol

Each seed generates **two isolated context-labeled worlds** with 5 independently controlled binary inputs, 32 possible intervention actions, one binary output, and an unknown relationship. All arms use the **same predeclared 113-hypothesis Bayesian posterior** (3 zero-parent, 10 unary, and 100 genuinely two-parent Boolean candidate functions) with equal prior mass by order and assumed 5% sensor noise. This is **not arbitrary novel operator discovery**.

Each world provides 12 selected intervention-and-consequence training events, then is evaluated on all 32 intervention settings with independently generated held labels and no held updates. Four *fresh, disjoint* synthetic cohorts:

- Two-parent Boolean causal worlds: seeds `23000..23063` (**128 worlds**).
- Unary worlds: `24000..24031` (**64 worlds**).
- Three-parent parity not in the hypothesis class: `25000..25031` (**64 worlds**).
- Independent fair-random labels: `26000..26031` (**64 worlds**).

Action arms share the same posterior, noise functions and query budget: **active** chooses an action with maximum posterior-predictive entropy (tie-break by fewest visits), **balanced** chooses a fixed full-factorial permutation sequence, and **random** uses an independent deterministic random action sequence. All arms intentionally calculate 32 candidate probabilities on each query so counted hypothesis evaluations match; fixed/random arms **could run much cheaper without this artificial equalization**. The program uses deterministic action/visit noise keyed by seed, context and intervention. Held outcomes are identical across arms.

## Frozen held-out result — Brier score, lower is better

| World type | Active information seeking | Balanced schedule | Random schedule |
|---|---:|---:|---:|
| Two-parent causal | **0.0744958968** | 0.0933087723 | 0.1169667217 |
| Unary causal | **0.0614142311** | 0.0646689339 | 0.0739332893 |
| Three-parent parity | **0.3329457529** | 0.2970561383 | 0.2908041391 |
| Independent random | **0.3177706147** | 0.2888839375 | 0.2914905747 |

**Positive but bounded:** On two-parent worlds active querying improved Brier by **0.0188128755** versus balanced (paired approximate 95% CI **[0.0068056767, 0.0308200743]**) and **0.0424708249** versus random (CI **[0.0273304598, 0.0576111899]**). Both exceed the frozen 0.01 margin. On unary worlds, active did not violate the 0.01 degradation threshold.

**Decisive falsification:** On **unfamiliar three-parent parity** and **random independent labels**, active querying was significantly worse than the strongest matched-action comparator, exceeding frozen maximum degradation **0.020** in both. For parity, Brier was 0.33295 vs best-control 0.29080, degradation +0.04214. For random labels, 0.31777 vs best-control 0.28888, degradation +0.02889. The policy tends to seek uncertain responses inside its own **misspecified** model rather than discovering that the model's causal family is wrong.

**Exact synthetic cold learner continuation:** Per arm a fixed **1,874-byte** two-context checkpoint contains all 113 float64 posterior scores, 32 action-visit counters and one step counter per context. After A→B training, A posterior and counters remained unmodified on all seeds. Two independently restored A learners produced identical selected actions, observed consequences, updated serialized bytes and predictions during **four additional A training interventions**: 160/160 seed runs PASSED. This is evidence of exact continuation **within this synthetic JavaScript study**, not proof of native Yggdrasil checkpoint retention or cross-process durability.

The matched forced posterior-hypothesis evaluation count on 64 two-parent seeds was **6,190,592 per arm**, with no demonstrated physical inference speedup. The full V8 primary study measured 16.533 seconds in one execution environment; platform CPU/RAM details were unavailable, so it is not a controlled hardware efficiency benchmark.

## Disposition and next falsifier

- **ENGINEERING:** frozen protocol → committed source → committed result ordering PASS. Local synthetic deterministic evaluation PASS; Linux/Windows CI pending exact-head qualification.
- **SCIENCE:** **MIXED / NO-GO** under preregistered joint thresholds. Familiar-family information acquisition helps, but misspecification worsens unfamiliar worlds. No accepted intelligence gain.
- **DEPLOYMENT:** NONE. Keep [PR #1340](https://github.com/spoonman136668-ai/Yggdrasil/pull/1340) draft and unmerged. The central Unified Causal Intelligence Amalgam Work chat alone coordinates potential qualified integration.

The next separately preregistered question is a **predictive posterior check with an explicit out-of-model/null hypothesis and a safe action fallback**. It must retain the pair-world intervention benefit while avoiding worse outcomes than balanced or random controls on unfamiliar worlds; preserve the exact negative Gate 13 results without retuning on these evaluated seeds.
