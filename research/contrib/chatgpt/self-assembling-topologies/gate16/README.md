# Gate 16 — Higher-order Walsh interaction construction from interventions

**Research-only.** New, separately preregistered scientific development study on a restricted 5-input binary causal world. **Result: REPRESENTATIONAL GAIN ONLY, NOT STRUCTURAL SELF-ASSEMBLY.** No accepted Yggdrasil model, central Amalgam checkpoint, training owner, or native scientific first-use was changed.

## Source custody

- [Frozen preregistration](./prereg.json), committed **before source and results** at `860487bed0498cc22dc26f93b4b7ed157c799163` (Git blob `f499143c9d4abfda480e84aa6f31618018403061`).
- [Executable JavaScript source](./run.cjs), committed before first primary run at `0ab9cb7740c7993555aea5b8190daad0f34463d3` (blob `5693c55b28fd281a111c08560286f34aadb4e5f7`).
- [Sealed result](./result.json), committed after first primary run and exact independent deterministic recomputation at `ae0525b54f619f9f1450f0f2c1c1db5978d06d6f` (blob `b1b347b887c8cae36d327969ddf246b297556a5a`).
- [Arithmetic and Boolean truth-table audit](./audit.cjs) independently checks mathematical nonrepresentability and receipt thresholds, not a wholly separate learner implementation.
- [Provenance](./provenance.json) pins resources, scope and qualification status.

To reproduce from the repository root, using Node.js only:

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate16/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate16/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate16/audit.cjs
```

## Novelty boundary and frozen experiment

Gate 13–15 failed to calibrate confidence under unfamiliar causal worlds. This experiment tests a **different mechanism**: bounded construction of **third-order XOR/Walsh interaction candidates** from the accumulated observed action–consequence correlation, rather than more posterior-surprise thresholds. The candidate operator library remains fully specified in advance; adding a triple is **not open-ended discovery of arbitrary nonlinear operators**, and "constructed" refers to selecting a predescribed basis composition, not creating a native causal circuit.

Five independently controlled input bits yield 32 intervention settings. Two context-labeled worlds per seed each supply **96 uniformly sampled intervention–consequence training events**, of which the first 64 select a candidate and the next 32 independently validate it. A final 32 held actions enumerate all settings, using independent source noise and **no held updates**. Cohorts are disjoint from all Gates 10–15:
- Genuine 3-parent XOR parity, 64 seeds `51000..51063` (128 worlds);
- 2-parent parity `52000..52031`, unary `53000..53031`, independent random `54000..54031`, and 3-parent majority `55000..55031`, each 32 seeds (64 worlds per cohort).

Every compact learner stores **exactly 388 serialized bytes**, including both contexts' last 96 training (action,label) pairs and two route bytes each. The expanded learner first scores the 15 unary/pair basis functions, *then* scores the ten explicitly constructed third-order XOR candidates only if no lower-order feature has an absolute correlation of 0.70. A candidate must clear the predeclared training-only validation Brier improvement >=0.10 and validation Brier <=0.15. It is then refitted on all 96 training events. Comparator arms use the **identical data and state capacity**: 25-feature preallocated fixed full classifier, truncated 15-feature 1/2-parent classifier, 32-setting Laplace table, and marginal null. An unmatched **816-byte** Bayesian 51-hypothesis reference uses the same specified parity family. This is not a fully trained conventional architecture comparison.

## Held Brier results (lower is better)

| World type | Constructed third-order | Matched fixed full | Truncated 1/2-order | Laplace action table | Unmatched Bayes |
|---|---:|---:|---:|---:|---:|
| True triple XOR | **0.0517363146** | **0.0517363146** | 0.2518414772 | 0.1041039279 | **0.0514990234** |
| True pair XOR | 0.0520824694 | 0.0520824694 | 0.0520824694 | 0.0994753265 | **0.0429296875** |
| True unary | 0.0491610379 | 0.0491610379 | 0.0491610379 | 0.1036838751 | **0.0490820312** |
| Independent fair labels | 0.2526463990 | 0.2526463990 | 0.2526463990 | 0.2770829309 | **0.2500000000** |
| Unfamiliar 3-way majority | 0.2533032704 | 0.2533032704 | 0.2533032704 | **0.1003597639** | 0.2422445193 |

**Bounded useful result:** The constructed three-parent learner identified the exact triple in **128/128 positive worlds** and achieved a held Brier advantage over the 1/2-order control of **+0.2001051626**, paired approximate 95% CI **[+0.1935065617,+0.2067037636]**, above the frozen +0.10 margin. The third-order effect is identifiable under randomized interventions and the *known* Walsh-parity grammar. No missed triple or spurious installed parity route was observed in the random/majority cohorts.

**Critical matched-control negative:** The 388-byte preallocated fixed full learner scored **identically on every seed and every cohort**. The measured gain of dynamic construction over fixed is **exactly zero**, 95% CI **[0,0]**, failing both prereg structural-superiority gates. The same-capacity fixed model is **no less predictive** than adaptive expansion. On true triple worlds both evaluated 212,992 candidate fit/validation operations; on pair/unary worlds adaptive sometimes avoided higher-order scans, reducing selected algorithmic comparisons but not demonstrating physical compute/energy efficiency.

**Unfamiliar operator limitation:** The 3-parent majority world is not a pure parity. The candidate learner safely abstained from asserting a parity relation on **64/64** majority worlds, but its Brier remained near chance (0.2533) while the ordinary action-conditioned Laplace table achieved **0.10036**. This is material evidence that knowing only XOR/Walsh structures does **not** generalize to a new nonlinear causal rule. Matching a frozen safety threshold of Brier <=0.27 must not be marketed as learning the new rule.

**Cold restore:** All **192/192 seed trials** restored the compact 388-byte record exactly and matched predictions; native checkpoint continuation, across-process cold durability, interference and cumulative skill growth were **not tested**. Full process memory excludes source dictionaries, scratch arrays and runtime. The first synthetic primary run took approximately 3.64s in a V8 isolate without hardware benchmarking; no whole-process speedup, energy saving or intelligence gain is established.

## Engineering / Scientific / Deployment separation

- **ENGINEERING:** Prereg and source committed before scored results, sealed exact deterministic outcome and constrained memory design. Final GitHub CI and complete repository regression must be read separately at the exact final head.
- **SCIENTIFIC:** **Representational development signal** (new, restricted third-order causal interaction is useful) with decisive **FAIL** against an equal-capacity fully specified fixed model. NO unique self-assembly superiority, transfer to majority, native scientific acceptance or general intelligence claim.
- **DEPLOYMENT:** **NONE.** The central Unified Causal Intelligence Amalgam Work chat alone coordinates native learning/checkpoint and accepted model integration. Keep the existing research PR #1340 **draft and unmerged**.

**Next experiment:** A frozen change that produces **genuinely unfamiliar nonlinear causal compositions** from action consequences with demonstrable retention and generalization beyond the given Walsh family, or independent exact-cost evidence that selective construction is cheaper than fixed full structure without losing prediction quality. Avoid retuning Gate16 on its evaluated seeds and preserve all negative controls.
