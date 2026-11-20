# ENERGY-64 — Transfer of learned causal factors across unfamiliar action-variable identities

**Prospective screening verdict: `SCREEN_NO_GO` (5/9 frozen gates PASS; all 3 critical gates FAIL).** Date: 2026-11-19. **External synthetic research, not native Yggdrasil cumulative learning, accepted science, or a deployment.**

## Exact custody / prospective time ordering

- Existing draft PR [#1210](https://github.com/spoonman136668-ai/Yggdrasil/pull/1210), archive branch `research/archive/energy-evidence-20261117` at parent `ff161736fee82485c41d70ef7b29f332816b9fa9`.
- **Frozen scorer and independent auditor GitHub source commit `3b940e60e02171b3f1edd73034e140ecab53e393`.** Source archive SHA-256 `c7928457ae875a8f353b70eff6012f2aea587621d8b6a3d513a8aa9a1f61df6a`; Git blob `f7b930bb49853592cdc85988763a71c9e873b68b`. Individual `experiment.py`/`audit.py` hashes in `source_manifest.json`.
- **Separate preregistration GitHub commit `48734b71a8edb54696f36dc6f6d30ad3d56554e9`** was read back and verified before either prospective seed was scored.
- Excluded prefreeze engineering-development smoke seed `998317`, world ID zero, 3 families; independent audit 13,618 checks PASS. It did not count toward prospective conclusions.
- Prospective seeds **`998331` and `998347`**, each with four distinct world IDs in three mechanism families (24 worlds). Reserved primary **`106101`, `106117`, `106137` NOT CONSUMED** under frozen stop rule.

## Research question and exact information boundary

Can old learned causal pair factors be reused when NEW action variables have unseen identities / positions, using paired intervention evidence to infer the mapping? The candidate learns 3 primitive factors on OLD-only observations, enumerates **720 possible permutations** of the first six observed causal variables, refits the old factors under each mapping, then averages predictions with posterior weights based on paired NEW intervention differences. **The 720-map set and pairwise factor grammar are supplied by the experimenter.** The learner does not invent an unrestricted grammar or discover unknown variable classes.

Each synthetic world contains **eight binary underlying do variables** and two context-dependent nuisance cues. The simulator plants 3 signed pair-parity factors, and in two families changes a coefficient or adds a new fourth-order factor. OLD has 72 witnessed intervention outcomes; NEW has 36 witnessed outcomes arranged as 18 paired one-bit interventions (3 per each of first six source variables); OLD/NEW/COLD held have 48 unseen outcomes each. **252 of 256 underlying causal action assignments are distinct between *all* training and held streams.** COLD uses the same NEW permutation but randomizes nuisance cues, so cold transfer evaluates nuisance shift and previously unseen action assignments, **not a second newly mapped world**. NEW and COLD outputs are never used for selection or training until the stipulated NEW witness outcomes, and held targets are wholly withheld. The source truth/hidden mapping are included in evidence for independent audit but never accessed by fitted predictors.

All ten arms receive the **same OLD72 plus NEW36 witnessed labels**, though some fully trained conventional controls only *use* NEW training labels. The decisive matched `full_bayes_refit` gets the exact same OLD supports, all 720 mappings, regularized per-map refits and labels as the candidate; it differs in the choice of posterior evidence (full new labels versus paired intervention differences). Conventional alternatives include fully trained ElasticNet on 15 NEW pair features, **fully trained degree-four ElasticNet on the 15 pair plus 15 fourth-order Walsh features**, OMP3, Ridge, ExtraTrees, a frozen OLD model and shuffled-NEW negative. Observation parity and pair-map refit compute are matched, not total system compute across all methods. No physical energy figures are claimed.

## Original 24-world held-out mean squared errors (lower is better)

| Method | OLD held MSE | NEW held MSE | COLD held MSE |
|---|---:|---:|---:|
| `new_degree4_elasticnet` | 0.033081 | 0.048585 | 0.048085 |
| `full_bayes_refit` | 0.033081 | 0.321927 | 0.321299 |
| `contrast_refit` | 0.033081 | 0.321930 | 0.321305 |
| `new_pair_omp` | 0.033081 | 0.322458 | 0.322127 |
| `fixed_bayes` | 0.033081 | 0.461647 | 0.457245 |
| `new_pair_elasticnet` | 0.033081 | 0.611081 | 0.530895 |
| `new_pair_ridge` | 0.033081 | 0.777740 | 0.694453 |
| `new_extra_trees` | 0.033081 | 3.572747 | 4.359065 |
| `shuffled_new` | 0.033081 | 4.744731 | 5.516945 |
| `naive_old` | 0.033081 | 5.683409 | 6.118727 |

Candidate cold MSE **0.321305** versus strongest fully trained conventional **`new_degree4_elasticnet` = 0.048085**. Candidate has **568.20% greater cold MSE** (i.e., conventional baseline **85.03% lower error**). The exact 720-map full Bayesian refit is **0.321299** versus candidate **0.321305**: practically identical accuracy, no measured gain. Candidate beats no remapping and fixed-coefficient Bayesian mapping, but not the critical same-map, same-new-label refit baseline or the more expressive nonlinear polynomial learner.

### Fresh seeds

| Seed | Candidate cold | Matched full-posterior refit cold | Degree-4 ElasticNet cold |
|---|---:|---:|---:|
| 998331 | 0.348379 | 0.348378 | 0.053447 |
| 998347 | 0.294231 | 0.294221 | 0.042724 |

### Mechanism families

| Family | Candidate cold | Matched full-posterior refit cold | Degree-4 ElasticNet cold |
|---|---:|---:|---:|
| novel_quad_permuted | 0.894475 | 0.894455 | 0.056557 |
| return_permuted | 0.036498 | 0.036506 | 0.041321 |
| reweight_permuted | 0.032942 | 0.032937 | 0.046378 |

The `novel_quad_permuted` family contributes most of the candidate error because its fourth-order causal term is absent from the candidate's three-pair factor representation, while the conventional degree-4 control is explicitly allowed to fit that term. This is an important **representational scope limit**, not evidence of generic intelligence or a surprising defeat of a model with the same feature class. Candidate performance on the two pair-only families is close to the noise floor; strong transfer is conditional on supplied pair grammar.

## Nine preregistered gates

| Frozen gate | Result |
|---|---|
| `cold_vs_fixed_bayes_5pct` | PASS |
| `cold_vs_full_posterior_3pct` | FAIL |
| `cold_vs_naive_old_20pct` | PASS |
| `cold_vs_strongest_other_5pct` | FAIL |
| `family_noninferiority_10pct` | FAIL |
| `old_exact_retained` | PASS |
| `posterior_spread_exercised` | PASS |
| `seed_positive_each` | FAIL |
| `shuffled_negative_20pct` | PASS |

**5/9 PASS ⇒ `SCREEN_NO_GO`**, because `cold_vs_strongest_other_5pct`, `cold_vs_full_posterior_3pct`, and `seed_positive_each` were preregistered as critical and all FAIL. No scoring or tuning of reserved primary. No post-outcome seed changes or source alterations.

## Independent audit, determinism, limitations

- **PASS 108,401 independent-source refit checks across 24 worlds.** `audit.py` does **not** import the scorer. Independently reproduces SHA-keyed action IDs, 252-way disjointness, source hidden mechanism and exact source outcomes, independently enumerates and fits each of 720 candidate/control maps, refits all conventional controls, verifies every OLD/NEW/COLD prediction, per-case MSE, pooled metrics, per-seed/per-family scores and frozen gates. It uses the published synthetic generator logic plus the same NumPy/sklearn solvers, so this is **not a wholly independent scientific replication**.
- **PASS exact-source deterministic semantic replay** on the same seeds, excluding only `elapsed_seconds`. Canonical SHA256 `e9e20d9652964d01bdab4b08364494d76e1853fe0b308556b3b4bc9b680b2c2e`; original original full-score SHA256 `90cf0991137398742c7a393a19c9638b33823067d33257c6cff600aee4b7ba9c`. Replay is a reproducibility check, **not an independent world set**.
- Frozen source single-thread screening process took 0.800657 s locally; excludes auditing, replay, GitHub custody, CI and entire training infrastructure. No electricity consumption, latency at scale or end-to-end energy savings measured.
- The original 24-world scored JSON, independently generated audit, identical-source replay, prefreeze excluded smoke and per-world/per-arm score receipts are packed in integrity-checked `EVIDENCE.tar.bz2.part*` archives. Run `python verify_archive.py` from this directory to reconstruct and validate every component, then the exact scorer/auditor reproduction described in `README.md`.
- Native Yggdrasil main, accepted refs, checkpoints, autonomous learner, controller, queue and scheduler are unchanged. Official Linux/Windows CI and native regression have separate statuses and cannot be inferred from local audit PASS.

## Decision

Preserve a **negative result for posterior contrast mapping**. Transfer across a known finite action permutation works on the authored pairwise cases, but the exact same-map standard Bayesian refit is at least as good and a fully trained four-way representation is significantly better on novel higher-order effects. Future work requires either learning the missing operator *from experience*, or fewer labeled new interventions with a fair same-operator, same-compute comparison. Do not reuse consumed screen seeds or reclassify these results post hoc.
