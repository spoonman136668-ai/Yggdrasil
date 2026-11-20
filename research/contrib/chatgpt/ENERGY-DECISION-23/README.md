# ENERGY-DECISION-23 — archive-only causal-change alarm risk analysis

**2026-11-20 | Yggdrasil Energy Research contributor | ENGINEERING 15/15 saved-result checks PASS plus four mutation controls | SCIENTIFIC no new experiment / NO native gain | DEPLOYMENT NONE**

## Why this was the next useful gate

Earlier Energy Gates 15–22 explored distinct synthetic binary causal-change learners and then **identified a source-contract mismatch** between freely intervening on 32 five-bit contexts and the existing `NativeCausalAmalgam` two-stage witnessed episode semantics. A fresh synthetic detector test would not close that native-learning gap. The Amalgam owner is the sole integration coordinator ([PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278)); no second native learner, runner or controller is authorized by this contributor.

The decision-worthy unresolved question in **already collected and consumed** Gate 21 evidence was: *When does a 95th-percentile high-sensitivity alarm policy justify more false repairs than a 98th-percentile conservative one?* This report addresses that question **without generating, replaying or retuning any primary world**. Its policy-cost scenarios are illustrative hypotheses, not learned estimates of real change prevalence or error cost.

## Exact evidence and custody

- Contributor [draft PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346), accepted-main baseline `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Reused immutable [Gate 21 original result](../ENERGY-FACTORS-21/result.json), Git blob **`fc4a3e86710c31d4043b2843ab9c39c6639b1ce8`**, original experimental executable commit `b4970df3854c76ea7ccbcbc4d08a343f15d7fc4e`, original prior protocol `a83bf272c3ce9ea3869feb78d33e8afc348c5e57`; unchanged scientific classification `SCIENTIFIC_NO_GO`.
- Committed [prereg.json](prereg.json) for **archive-only** analysis *before writing code*, commit **`d6356cf0ec6394a64a2c43e2502b8580f9b6d84a`**. Committed [analyze.js](analyze.js), commit **`64a507400d943035cf546864b40e8db83b359a11`**, Git blob **`f41d387fd889045b2a27cd1b848239581f8c9c54`**.
- Read back both exact source files and the original frozen result by Git blob before computing. Reconstructed model-specific thresholds from all 200 original *independent NULL-only calibration scores* at ranked positions 191/200 and 197/200. Evaluated original 384-world primary **once from saved rows**, not from regenerated outcomes: 96 NULL worlds, 96 SINGLE_EDGE, 96 DOUBLE_EDGE, 96 NONLINEAR_AND; each original world has 24 OLD observations, 16 NEW and 12 distinct first NEW inputs.
- [result.json](result.json) retains 384 per-world decisions, policy confusion matrices, family splits, paired contingency tables, Wilson score 95% intervals, scenario loss grid and break-even prevalences. Separately written [audit.js](audit.js) and [audit-result.json](audit-result.json): **15/15 PASS**, independently recalculate thresholds, decisions against original probabilities, sample uncertainty, exact paired-count arithmetic, four crossovers, and 20 policy-loss cells from the saved source. Four mutation controls PASS: original good; corrupted threshold, world label and false-alert count each rejected. **No new native test, first use, cold functional restoration or complete cross-platform regression.**

## Frozen observed performance at 20% synthetic label noise

| Already-fixed alarm policy | Familiar changed correctly flagged (192) | False changes on NULL (96) | 95% Wilson interval for false alarm proportion |
|---|---:|---:|---:|
| **Bounded OLD top8 + local NEW, 95th-percentile** | 124/192 = **64.58%** | 4/96 = **4.17%** | **1.63–10.23%** |
| Same bounded model, 98th-percentile | 62/192 = **32.29%** | 0/96 = **0%** | **0–3.85%** |
| Full fitted Bayesian OLD/NEW, 95th-percentile | 134/192 = **69.79%** | 4/96 = **4.17%** | **1.63–10.23%** |
| Full Bayesian, 98th-percentile | 96/192 = **50.00%** | 2/96 = **2.08%** | **0.57–7.28%** |
| Bounded OLD top8 + global NEW, 95th-percentile | 119/192 = 61.98% | 4/96 = 4.17% | 1.63–10.23% |

**Causal family detail:** Bounded 95th detection was 60/96 SINGLE_EDGE and 64/96 DOUBLE_EDGE; bounded 98th detection 35/96 SINGLE_EDGE and 27/96 DOUBLE_EDGE. NONLINEAR_AND out-of-model flags remained poor (bounded 95th 16/96, bounded 98th 4/96). Do not treat detection of a shifted XOR truth law as generalized causal relationship discovery.

**Paired decisions on identical worlds:** Bounded 95th versus bounded 98th agrees on 62 changed-world alarms; the 95th flags **62 additional** changed worlds, with zero additional unique detections from 98th, because the thresholds are nested. But among NULL worlds, the 95th introduces four false flags relative to zero. The paired sign p for changed-world discordance is mathematically small (two-sided 4.34×10⁻¹⁹), **as expected when thresholds are nested**—it is not evidence of a novel learning mechanism or independent scientific replication.

**Bounded 95th versus conventional full Bayes 95th**: both flag 4/96 unchanged worlds, but the four need not be the *same* cases (only 2 overlap); full Bayes flags 134/192 familiar changes vs bounded 124/192. Of the 192 changed worlds: 114 both detect, 10 bounded-only, 20 full-only, 48 neither. The exploratory exact paired sign p is about **0.099**, so this sample does not independently establish a robust superiority of full Bayesian change *decisions*; underlying continuous event-Brier also favored the bounded candidate on this single cohort. No claims of conventional domination on all metrics or known real deployment prevalence.

## Frozen illustrative expected-loss calculation

Let `p` be the frequency of true causal change and `r` the relative cost of a false repair compared with missing a true change. With missed-change loss normalized to 1, the expected loss is:

`p × (1 - change detection rate) + (1 - p) × r × false alarm rate`

This uses **held synthetic conditional error rates**, *not* a measured deployment distribution. For the same bounded detector, the 95th threshold has better modeled expected loss than the 98th only once the assumed genuine-change prevalence exceeds this **illustrative** break-even:

| False repair cost / missed change cost | Minimum assumed real-change prevalence for 95th to beat 98th |
|---|---:|
| 1× | **11.43%** |
| 5× | **39.22%** |
| 10× | **56.34%** |
| 25× | **76.34%** |

The complete preregistered 20-cell scenario grid (change prevalences 1%, 5%, 10%, 25%, 50% crossed with false-repair cost multipliers 1, 5, 10, 25) and all five fixed policies is in [result.json](result.json). Bounded 98th had the lowest *empirical modeled* loss in 17/20 illustrative scenarios and full Bayesian 95th in 3/20. Bounded 95th was never the minimum among **these five** when ignoring computation and memory because full Bayesian 95th had the same *aggregate* NULL error count and more changed-world detections. It did use fewer counted operations in Gate 21, however. These minima are not operational recommendations or an independent scientific pass; selecting the minimum *post hoc* and replaying with that selected policy would be invalid.

### Key uncertainty and qualification failure

- **Observed 4/96 is not proof of <=5% real-world false alarm rate.** Its Wilson 95% upper bound is **10.23%**. Even 0/96 observed for bounded 98th has an approximate 3.85% upper bound, and neither sample is representative of a real deployment distribution.
- The primary held proportion of true familiar changed versus unchanged worlds is **192:96 = 2:1**, generated by a synthetic challenge protocol, *not* an empirically measured base rate. Any decision rule that silently assumes this proportion risks overcalling change.
- Cost ratios and change prevalence are parameters to test and fix by the **native original-source owner** before evaluation, not thresholds learned from this dataset.
- **Scientific NO-GO remains.** No new training; no evidence of persistent native memory, source-faithful staged-episode learning, unfamiliar-world transfer, intervention gain, wall-clock speedup or true energy savings.
- The existing Amalgam PR #1278 has a valid staged-episode `observe_experience`, `checkpoint()/restore()` and historical `retention_guard.evaluate`. Energy-NATIVE-22 already proved that direct translation from freely intervened five-bit contexts remains UNVERIFIED. **Do not add a rival native learner, replay consumed Gate 21 worlds or apply the 95th alarm cutoff to protected native source.**

## Concrete final research disposition

**ENGINEERING:** retrospective readback/pin, reaggregation 15/15, mutation controls 4/4 PASS. This is *not* the end-to-end candidate regression; G29 source-atlas index remains stale and dual-platform Actions cannot qualify this contributor head without a fresh atlas artifact commit generated by an authorized checkout. The existing isolated G29 writer workflows are scoped to other exact branches and do not authorize an alternative controller or runner from this contributor chat.

**SCIENTIFIC:** archive-only retrospective analysis and uncertainty assessment. A defensible next **owner-only** native experiment must freeze two-stage witnessed action-consequence semantics, real/no-change frequency and predeclared false-repair loss, exact matched conventional fitted controls, no-leakage probe, held unfamiliar and retained familiar consequence Brier, independent cold restoration and full final regression. The explicit research recommendation is **do not promote** the Gate21/23 alarm rule from synthetic evidence.

**DEPLOYMENT:** NONE. Accepted main, cumulative Amalgam learner, model weights, checkpoints, host runner, trading or controller state unchanged. No new scheduler, API charge, merge or first-use.
