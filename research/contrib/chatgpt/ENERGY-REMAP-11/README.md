# ENERGY-REMAP-11 — Causal topology under hidden sensor relabeling

**Post-primary analytic correction (ENERGY-REMAP-GATE-12):** The [exact mathematical certificate](../ENERGY-REMAP-GATE-12/README.md) proves that the frozen 6-OLD/2-NEW, Dirichlet(0.5), prior-reset=0.25 setup has maximum possible P(reset)=**5/7=0.7143**, below its hard **0.80** gate. Exhaustive 9,702 unordered count cases and a separately derived 16,632 ordered-case audit both found **zero reachable activations**. Thus the experiment's 0/36 repairs were **inevitable by design**, not stochastic misses; the candidate's apparent benefit is **ordinary MAP sensor alignment**, not functioning causal-edge repair. Original 36-world primary scores, frozen prereg, consumed seeds and MIXED_NO_GO classification remain unchanged. No source was retuned or primary trial rerun.


**20 November 2026 · Independent source-free Yggdrasil research · SCIENCE: MIXED_NO_GO · DEPLOYMENT: NONE**

## Question

Can a bounded directed-edge learner transfer causal action relationships to unfamiliar sensor labels while repairing changed action-conditioned edges, rather than relying on a conventional Bayesian posterior over possible sensor mappings and edge changes?

This is a contributor-only study in [draft PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346). The only central cumulative learner remains [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278). The contributor did not change accepted Yggdrasil source, owner-runner execution, checkpoints or main.

## Frozen experimental design

Each source-free world has six hidden physical states, two interventional actions and a directed ring. Action 0 follows the ring; action 1 follows the reverse ring. The correct next state has probability 0.88, with the other five outcomes sharing 0.12. The NEW observation labels are an independently drawn hidden permutation of the OLD state labels. All models receive **only two public OLD→NEW landmarks**, for OLD states 0 and 3; the remaining four states admit 24 possible anchor-consistent mappings. The true mapping is recorded only for postscore auditing.

Each world supplies **72 OLD training transitions** (six per state and action), then **24 NEW training transitions** (two per state and action), then **1,152 disjoint held NEW consequences** (96 per state and action). Three scenario families, 12 primary seeds each: SENSOR_REMAP (same graph under new labels), LOCAL_REWIRE (two action-1 targets swapped), and OUT_FAMILY (action-1 targets separately sampled with replacement, violating the ring/local-swap family). Total **36 worlds, 2,592 OLD training + 864 NEW training + 41,472 held-out outcomes**.

The proposed candidate chooses maximum-evidence mapping using source-free mapped OLD row Dirichlet(0.5) predictions, pools the OLD/NEW rows, and resets a row to NEW-only after integrated change-posterior >=0.80. The old prediction readout is snapshotted before new learning. All models see the same public transitions and anchors. Baselines include a fully fitted NEW-only tabular learner, full Bayesian mixture over 24 possible mappings without changes, conventional MAP alignment, and a **fully fitted joint permutation-plus-row-change Bayesian mixture** that marginalizes mapping and reset uncertainty. A privileged true-target law is recorded only as a theoretical reference, not an intended Brier competitor.

## Source and evidence custody

1. Frozen [preregistration](prereg.json) committed `d793d4b1ecfd940199eb9e51315f02b0b61b5d0c` before implementation.
2. Frozen source [experiment.mjs](experiment.mjs) committed `ab203a45bd1e42a11a043055e4541d26e1676ced`; Git blob `8a5fbfa908edad48bb23804517c06bb645b5fda8`. Source was serialized from the exact invoked JavaScript function, fetched back and compared byte-for-byte to the committed source **before smoke or primary execution**.
3. Distinct smoke seed `95701` used only for data quota and probability validity.
4. One frozen primary using seeds `95711,95717,95729,95731,95747,95753,95767,95773,95783,95789,95801,95813` and three scenario families.
5. Full **36-world per-arm metrics, mapping and reset decisions** committed in [result.json](result.json) at `43947609fc4ef7c8a7aff668d71704854a89d1b4`, Git blob `e31e7eb4b1b9d41295fcbfebc4ebe73a7284b2ed`.
6. Readback-verified [postscore arithmetic audit](audit.mjs) at `e6187d6302ade4d0bda795cda18ba9e98fb10d22`, Git blob `15ef03535435209b2c9b7d9334a10cfe51a166a1`, re-aggregated all 36 world scores, checked source/seed/data quotas, mapping/set validity and classifications. **PASS without primary replay.** See [provenance.json](provenance.json).

Never repeat consumed primary seeds or tune the 0.80 change posterior based on the original outcome.

## Measured primary results

Multiclass held NEW transition Brier score; lower is better:

| Frozen comparator | Overall | Action 0 | Action 1 |
| --- | ---: | ---: | ---: |
| Privileged true-target oracle (reference only) | **0.223684** | **0.230042** | **0.217327** |
| **Fitted joint permutation + change Bayesian mixture** | **0.359991** | 0.307646 | **0.412337** |
| Fully fitted permutation Bayes, no change | 0.409855 | **0.291719** | 0.527991 |
| Candidate point-map and local hard repair | 0.412334 | 0.293540 | 0.531127 |
| Conventional MAP mapping without reset | 0.412334 | 0.293540 | 0.531127 |
| Independent NEW-only Dirichlet | 0.466865 | 0.467195 | 0.466535 |

The candidate's measured gain over the independent NEW-only learner is **0.054532 Brier**, but its deficit against the **strongest fitted conventional comparator is 0.052342 Brier**. That fails the frozen >=0.01 superiority threshold by a wide margin.

| Transfer family | Candidate Brier | Fitted joint Bayes Brier | NEW-only Brier | Correct point mappings |
| --- | ---: | ---: | ---: | ---: |
| SENSOR_REMAP | 0.286071 | 0.303532 | 0.468628 | 12/12 |
| LOCAL_REWIRE | 0.394188 | **0.345626** | 0.456424 | 12/12 |
| OUT_FAMILY | 0.556742 | **0.430815** | 0.475544 | 11/12 |

**Critical negative:** Candidate repair activated in **zero of the 36 worlds**. Its outputs matched the conventional MAP-pooling control exactly. The observed benefit on pure sensor-remapping worlds is therefore **ordinary graph alignment** under two supplied public anchors, **not learned repair or unfamiliar causal discovery**.

Out-of-family mechanisms caused substantial performance degradation, even below naive new-context tabular learning. Mapping identification alone is insufficient to demonstrate transferable action-consequence intelligence.

All **36 OLD prediction arrays survived NEW fitting and an in-process JSON roundtrip**. The public OLD/NEW boundary is labeled and OLD memory is held separately. This does not test unsignaled context recognition, independent-process cold restoration or continual learned reasoning.

## Classification and stop

**MIXED_NO_GO.** The candidate improves over an intentionally information-poor NEW-only baseline under SENSOR_REMAP and LOCAL_REWIRE. It does **not** outperform the strongest matching-and-change conventional model, and its purported local repair did not actually fire once. Do not characterize pure graph alignment as a new energy or native intelligence gain.

The correct scientific next question is not another threshold tweak. A genuinely different mechanism would need adaptive, evidence-calibrated transition-law change handling (not a hard-gated MAP rule), true out-of-family tests, matched conventional structure learning and actual held interventions, with independently restored cumulative learned state. None of that is qualified by this result.

- **ENGINEERING:** exact source/readback + frozen primary + independent postscore arithmetic **PASS**. Whole-process CPU/memory measurements, independent-process restoration and draft PR G29 Atlas dual-OS acceptance are **UNVERIFIED/FAIL**.
- **SCIENTIFIC:** source-free MIXED_NO_GO; best conventional comparison FAIL; no verified native gain, forgetting prevention or general intelligence.
- **DEPLOYMENT:** NONE. Accepted main, central Amalgam, original model checkpoints, runner/scheduler/controller and production were not modified.
