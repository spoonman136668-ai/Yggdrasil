# Gate 19 — Causal mechanism reuse across hidden parent remapping

**Contributor-only synthetic research. SCIENTIFIC MIXED / NO-GO on frozen joint thresholds. No native Yggdrasil training, checkpoint promotion or accepted cumulative intelligence gain.**

## Verified frozen custody

- [Preregistration](./prereg.json): committed **before experiment source and any Gate19 outcomes** at `73e3e3ab872fe3a91f6d999ecbd3bb0146f77ba6`.
- [Executable source](./run.cjs): frozen at `45c6339798292cfffc1b2f7127f336fd0a3061c6`, Git blob `06adf15e1cb4ac43b7c8897d4395f4cd3368d4d7`.
- [Primary sealed result](./result.json): committed at `d42ddc56e3da3f8caf1db8aca7dea8f2e214048d`, blob `10d06a579fc3e73491f7acd22808d4790cd0bed6`. The original source was reexecuted to check exact numeric parity before sealing. No seed, threshold, hypothesis or algorithm tuning after results.
- [Independent arithmetic/Boolean audit](./audit.cjs): committed after result at `cd70312cab02374e86fd37cefc21d0dda678842c`, checks exact gate arithmetic, source family symmetry and capacity; **not** an independent full learner reimplementation.
- [Provenance](./provenance.json): source and custody chain, negative controls, compute and first-use limitations.

Reproduce without extra packages, from repository root:

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate19/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate19/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate19/audit.cjs
```

## Experiment: actual environment change

This changes the question from Gate18's unseen **action vectors** to **retaining and reusing a causal function after physical inputs are remapped**.

A source environment A exposes 96 observations (three shuffled 32-action rounds) from a hidden three-parent Boolean relationship. Environment B uses the same underlying truth table for related families, but selects a *different* unordered triple of the five possible physical input variables and randomly permutes their correspondence to A's causal inputs. B reveals only **24 distinct interventions and labels**, split into 16 for matching and eight independent B-training validation examples. A further **eight unseen B action vectors** are held out from all learner selection and updates. The learner sees no true parents, operator identity or cross-environment mapping.

Families use **48 fresh seeds each**: same majority (`81000..81047`), MUX (`82000..82047`), sampled essential-three-parent Boolean truth table (`83000..83047`), XOR parity (`84000..84047`), and *unrelated* essential three-parent truth tables (`85000..85047`). The unrelated family rejects function equivalence to A under any three-input permutation and output complement. Total **240 A/B environment pairs**, **23,040 A source training observations**, **5,760 B fit/validation observations**, and **1,920 B held responses**. Per-context source noise is deterministic and domain-separated; no external model, teacher, paid API or hidden source-label access.

The **transfer arm** fits A's generic (1/2/3-parent) Boolean conditional table using A only. It considers all ordered physical B input mappings to A's selected parents (up to 60 permutations), using the first 16 B actions to choose the map. Eight B validation events must show ≥0.015 Brier benefit over a B-only learner or it falls back to B-only. Conditional probabilities for accepted transfer come from A, not held B outcomes. B-only learns a parent subset from at most 24 B actions.

Controls: (1) B-only conditional subset learning, (2) same-persisted-size fixed mapping computation producing the exact same forecasts, (3) deterministically shuffled A labels to break reusable source relations, (4) an explicitly stronger soft Bayesian mixture of all candidate B mappings and B-only subset hypotheses, (5) Bayesian B-only, (6) direct unobserved five-bit B action memorization and p=.5 null, and (7) an **informationally advantaged oracle mapping** for an illustrative ceiling only. The oracle is invalid as a competitive control in unrelated worlds (no true shared mapping). The Bayesian controls use unmatched transient memory/computation. No whole-process compute, energy or deployment gain is inferred.

## Held-out B Brier (lower is better)

| Environment B | Transfer | B-only scratch | Shuffled-A negative | Strong Bayesian shared |
|---|---:|---:|---:|---:|
| Shared majority | **0.0787031139** | 0.1147530781 | 0.1178853698 | **0.0573906068** |
| Shared MUX | **0.0771900499** | 0.1079771419 | 0.1157276627 | **0.0577670497** |
| Shared essential random Boolean | 0.0975536272 | 0.1103363725 | 0.1103363725 | **0.0738963617** |
| Shared XOR parity | **0.0604966518** | 0.0978949653 | 0.0978949653 | **0.0558494124** |
| Unrelated essential Boolean negative | 0.1150317538 | **0.1126049185** | 0.1133303099 | 0.1339954102 |

Matched persistent-size fixed transfer: **identical Brier to transfer on all 240 seeds**. Direct B action table and null each score 0.25 on these eight never-trained five-bit action vectors.

**Measured positive but limited:** Shared majority transfer saves **0.0360499642** Brier vs B-only scratch (paired approximate 95% CI **[0.0167518487, 0.0553480797]**); MUX saves **0.0307870920** ([0.0102424217,0.0513317623]); parity saves **0.0373983135** ([0.0257848307,0.0490117963]). Across four related families mean of their per-seed gains = **0.0292545287**, and compared with shuffled-A source gains mean **0.0319752319**. The related-world transfer validator accepts 41/48 majority, 40/48 MUX, 39/48 essential Boolean, and 45/48 parity trials.

**Four frozen failures:**

1. **Arbitrary Boolean transfer vs scratch:** Essential random relation transfer improvement is only **0.0127827452** Brier (95% CI **[-0.0169202340,0.0424857245]**), below prereg ≥0.025. The interval includes no gain.
2. **Strong Bayesian advantage:** Bayesian shared posterior beats the tested transfer mechanism on essential random relations by **0.0236572655 Brier**, greater than the prereg allowed 0.020. A majority gain vs Bayesian is also negative (transfer 0.07870 vs Bayesian 0.05739). Failing the strongest available control precludes declaring a preferred reusable mechanism.
3. **No unique structural advantage:** Fixed transfer and adaptive transfer tie exactly in all 240 seeds. Advantage 0 and paired CI [0,0]; both structural-superiority requirements FAIL.
4. **Limited negative specificity:** In unrelated-world controls transfer is mistakenly accepted **4/48** times (8.33%), though the prereg max false acceptance of 20% PASSES. Its mean held Brier worsens modestly vs B-only scratch by **0.0024268353**. This is not evidence of perfect unrelated-task discrimination.

**Mathematical identifiability limitation:** Majority and XOR parity are invariant to the six permutations of their three inputs. Even with infinite noiseless samples, the exact ordered B-to-A input matching is not always identifiable for these operator families. [Independent audit](./audit.cjs) proves this exhaustive Boolean invariance. Recovery of predictive behavior does not establish unique physical correspondence, much less discovery of all general causal mechanisms.

## State continuity and limits

Each arm's common persisted-evidence envelope is **388 bytes**, with 192 bytes of A96 action/response pairs and 48 bytes of B24 pairs, with 148 padding bytes; no truth table, map or source parent IDs are persisted directly. Both independently reconstructed records reproduce all eight B-held transfer forecasts. All **240/240** trials preserve A's 32 action forecasts and A's raw learned state after learning B. This is *same-process deterministic state reconstruction from saved examples*, not externally durable native model memory, a demonstration of interference repair, nor evidence of cumulative learning after hardware restart. It is also **not** a fully matched computation benchmark: transfer scans mapping candidates, Bayes recomputes many hypotheses, and scratch has different algorithmic cost.

**ENGINEERING:** Protocol/source committed in order; sealed primary data, independent arithmetic/Boolean audit; exact Linux/Windows source-first repo regression is a separate qualification to read back.

**SCIENTIFIC:** **MIXED / NO-GO** on prereg joint targets, despite partial benefit on three familiar operator families. Never rebrand the passing A-retention checksum as true native causal-memory retention or new intelligence.

**DEPLOYMENT:** NONE. Accepted Yggdrasil main, central Unified Causal Intelligence Amalgam model/checkpoint, owner-controlled first-use, controller and runners unchanged. PR #1340 remains draft/unmerged.

**Next experiment:** Test a *real cumulative native* learner via owner-controlled interfaces only, with cold process recovery, controlled interference, new independently composed environments, matched Bayesian computation, and prereg positive/negative targets. This contributor may only provide evidence and a qualified integration proposal, not independently merge or promote a checkpoint.
