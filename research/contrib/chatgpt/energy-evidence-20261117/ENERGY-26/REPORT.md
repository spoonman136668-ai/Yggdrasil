# ENERGY-26 — Structural causal projection under contaminated action evidence

**Date:** 2026-11-18. **Classification:** isolated source-free synthetic CPU development study. **Outcome:** `DEVELOPMENT_NO_GO` against strongest trained controls. No native Yggdrasil checkpoint was executed, no protected first-use, no merge, no deployment.

## The causal question and frozen design

ENERGY-25 showed an underdetermined learned 3-body energy model often finds the correct causal parent triple but makes wrong held predictions because other fitted coefficients overrule it. This new **prospective** experiment tests a minimal intervention: take the largest-magnitude learned 3-way feature and project the complete energy prediction onto only that signed structural relationship, discarding misleading lower-order fitted terms. Its matched conventional arm uses **exactly the same capacity, features, ridge objective and projection**, so any equality prevents energy-specific advantage claims.

Each source world has five binary interventions and one hidden signed three-parent parity rule. The truth rule is one of 20 possible structures, never revealed to the learner. Models observe 16 distinct action-consequence pairs and must predict the other 16 disjoint interventions. The training label source flips exactly 0, 2, or 4 outcomes per world, using a hash-random selection hidden from the learner. Four new primary seeds (`509,601,701,811`), all 20 rules and three noise levels give **240 independently fitted worlds**, **3,840 held predictions per arm**. The smoke seed is 919, fully separate from scored seeds and from ENERGY-25's original cohorts. Every method uses the same revealed action-consequence observations.

Source and frozen preregistration are `experiment.py`, `protocol.json`, `freeze.json`. Source SHA-256 `11347c7f7ec1952f9a2768c02da7781c43df1331005efcc0d22907e29d4e5131`; protocol SHA-256 `55d9eacf86552b1ad7bd0702f2e5eef1c9bcee97ddb4b5f691aa0d87149327dc`. The frozen gate required (i) >=95% held at zero corrupted training observations; (ii) >=85% on **each** noisy stratum (2 and 4 flips); and (iii) >=2 percentage points over a strong fully fitted unknown-noise Bayesian control on **all** strata. Since the conventional projection must match exactly, a distinctive energy advantage is impossible under this specific parameterization. No retrospective tuning occurred.

## Frozen primary results

| Corrupted labels / 16 | Pairwise energy | Original cubic energy | Projected energy | Same-capacity conventional projection | Exact Bayes, fixed 5% error | Exact Bayes, unknown noise Beta(1,4) | Parent/sign recovered |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 439/1280 | 1078/1280 | **1280/1280** | 1280/1280 | 1280/1280 | 1280/1280 | 80/80 |
| 2 | 488/1280 | 950/1280 | **1267/1280** | 1267/1280 | 1280/1280 | 1280/1280 | 79/80 |
| 4 | 555/1280 | 827/1280 | **971/1280** | 971/1280 | 1065/1280 | **1064/1280** | 47/80 |
| **Total** | **1482/3840** | **2855/3840** | **3518/3840** | **3518/3840** | **3625/3840** | **3624/3840** | **206/240** |

Projected-energy accuracy is **91.61% overall**, the exact unknown-noise Bayesian model **94.38%**, a **2.76 percentage-point loss** against the strongest principled unknown-noise control. The model's 4-flip accuracy is **75.86%**, below its frozen >=85% floor. Strong Bayes reached 83.13% there; neither method should be marketed as highly reliable under 25% adversarially selected label corruption. Against the original unconstrained cubic energy, projection improves all three noise regimes (+202, +317, and +144 additional correct held outcomes respectively).

With no corruption, projecting a reliable discovered parent triple perfectly removes noncausal fitted feature spillover. The technique is **not** an energy-only mechanism: it is equivalent to hard structural feature selection after ridge estimation. Under heavy corruptions it selects an incorrect signed parent rule in **33 of 80** test worlds, despite 16 observed action consequences. An exact finite-hypothesis Bayes rule mixture is a substantially stronger predictor in this correctly specified small hypothesis class.

## Independent verification and numerical integrity

The independent `independent_audit.py` was authored **after the frozen primary score** and does **not** import the scorer. It reconstructs all split and corruption actions from SHA-256 source namespaces; independently regenerates true causal labels; refits ridge using an **augmented least-squares solver** rather than the scorer's normal-equation solver; independently recomputes Bayes model-posterior votes using exact integer `19^(correct)` fixed-error weights and exact factorial Beta(1,4) integrated noise weights; and validates each per-case prediction and all aggregate totals.

- **53,760** predictive/invariant checks PASS, including every 240-world source split, 3,840 held causal truths, all 6 arms and exact posterior choices.
- An independent **one-shot rerun** reproduced the primary *semantic* score exactly (240 cases); wall timing fields excluded because they vary. Semantic SHA-256 `76d08b0acae657c22e5c631c988b8438699de5f122bfad2606f3cf66472177e1`.
- The auditor marked **51 original cubic-energy and 5 pairwise-energy near-zero margins** (<=1e-8). This is a property of the underdetermined linear model and may make some raw sign classifications sensitive to numerical solver choices, as already seen in ENERGY-25. The **projected causal hypotheses and predictions**, the capacity-matched conventional arm and both exact Bayesian arms verified without such ambiguity. Both Bayesian exact integer votes had **zero** ties.
- Retain `scored.json`, `replay-verification.json`, `audit_result.json`, `smoke.txt`, `freeze.json`, and sources in the original evidence ZIP. The original frozen score and source were not revised after scoring.

## Work and resource cost

The measured local cumulative CPU wall (fit plus predict across 240 worlds) was approximately **35.0 ms projected energy**, **20.2 ms conventional projection**, **8.3 ms fixed-error Bayes**, and **7.5 ms unknown-noise Bayes**; Python/NumPy overhead dominates this tiny workload. No GPU reproduction, cross-platform timing qualification, cache control or native full regression was performed in this gate. The projected model did not yield a speedup against optimized strong baselines here.

## Engineering / science / deployment

- **ENGINEERING: PASS local only.** Frozen primary scoring, semantic replay and independent reconstructive numerical audit passed. GitHub binary source custody and ZIP integrity must be verified on uploaded blob. No native Yggdrasil regression qualification claimed.
- **SCIENTIFIC: DEVELOPMENT NO-GO.** Hard causal projection reliably prevents the ENERGY-25 spurious feature interference on noiseless evidence but is not distinctive versus an identical conventional procedure and loses materially to Bayes under contaminated evidence. No causal retention, unfamiliar-world transfer or efficiency improvement in a native learner is established.
- **DEPLOYMENT: NONE.** Keep the Yggdrasil CKAD hypothesis bank and expected-return policy intact; do not promote this synthetic mechanism to the active research loop.

**Research decision:** A useful structural constraint needs *well-calibrated uncertainty* over candidate causal rules and support for revising those rules after contradictions, rather than hard-selecting a single top-weight factor. This is consistent with CKAD's retained hypothesis mixtures; no native change is justified by ENERGY-26 alone.