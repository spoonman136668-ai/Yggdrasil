# ENERGY-29 — Constructive Boolean causal hypotheses beyond fixed rule templates

**Date:** 2026-11-18. **Frozen outcome: DEVELOPMENT_NO_GO.** **Scientific pass: false.** **Deployment: NONE.**

## Research question and relevance

ENERGY-28 showed that a finite hypothesis-birth rule can outperform a prior 40-template family, but its new causal relationships were still selected from the experimenter's XOR3+AND2 grammar. ENERGY-29 instead constructs Boolean causal rule hypotheses as sparse algebraic-normal-form (ANF) expressions from a generic 41-feature basis (all monomials of degrees 1, 2 and 3 over six public intervention bits). It can combine up to three distinct monomials, with an optional output complement, producing **23,044 signed Boolean programs**. No source target is presented as an identity/label to the learner.

This is a **bounded general-purpose compositional hypothesis space**, not unconstrained causal concept invention or native Yggdrasil code. It is mathematically a version-space Bayes/energy-equivalent estimator, **not a distinctive performance benefit of energy inference**. Native CKAD's existing retained context learner, exactly marginalized planner and controlled scientific first-use were not modified or executed.

## Prospective frozen protocol

- Six binary public intervention variables, **64 possible interventions** per world. Exactly **24 witnessed action-consequence observations** used for learning, **24 disjoint held-out interventions** for scoring and **16 unused**. For each primary seed, the split is independently SHA-ordered and **the same across all laws**, preventing hidden-rule-dependent intervention selection.
- Source families: **old** signed three-bit parity optionally corrected by an AND of two remaining bits (160 known templates); **novel_in_basis** new three-term generic polynomial expressions including cubic and quadratic factors, deliberately excluded from those 160 templates; **outside_basis** degree-four interactions or majority-of-five, absent from the 23,044-rule hypothesis bank.
- **Four new primary seeds 2399, 2411, 2423, 2441**, 20 independently generated laws per source family and seed, training corruption of zero or exactly two observed labels, **480 independently fitted cases** and **11,520 held binary outcomes per learning arm**. Separate non-scored smoke seed 7001.
- **Same public evidence for every learner arm**. Structural-birth arm initially uses the old exact Bayesian bank; it admits all 23,044 compositional candidates if the old bank's minimum mismatch reaches at least 2 in the first 12 observations or at least 3 in all 24. Model receives no source law labels, hidden values or held outcomes; only the 24 intervention/outcome pairs.
- **Strong controls:** fully fitted exact Bayesian complete ANF version space, fully fitted old-template Bayesian bank, conventional degree-three polynomial kernel ridge, trained depth-six CART and trained 31-tree ExtraTrees forest, plus hard single-hypothesis MAP ablation. No arm gets more observed data or action capacity. Bayesian rule posterior and normalized classical energy are mathematically equivalent.
- Prespecified development GO requires clean novel >=90%, noisy novel >=80%, >=20 percentage-point novel gain over old and >=3 points over strongest conventional control in **each** noise group, within 2 points of full exact ANF control, and familiar knowledge degradation <=0pp without corruption and <=2pp with corruption. **All conditions mandatory.** Outside-basis scores describe representational limits only.

**Freeze seals:** `experiment.py` SHA-256 `9dde0d8dbc70262d35404957a29b0405861b88caeaea7001767dbe9021443001`; `protocol.json` SHA-256 `df7d308c71a9a2bcfa17c271b7caf63e52df4eefb64f105b56ad021d5863c75b`; smoke SHA-256 `a04de66a8e8276fae2a5a0fc7ca642ca5ebb154eb82e4f223b5cd8bc6f30a861`. Frozen **before** any primary scoring; code, cohort, priors and development thresholds unchanged after the score. Scoring may be rerun semantically with timing excluded. The auditor had only serialization corrections after scoring (retained failure record).

## Primary held-out results

Each row contains **80 fitted worlds ×24 disjoint held interventions =1,920 predictions per arm**.

| World family | Training flips | Old fixed Bayes | Constructed ANF birth | Complete exact ANF Bayes | Strongest conventional (forest) | Novel births |
|---|---:|---:|---:|---:|---:|---:|
| Familiar old | 0/24 | 1920/1920 | 1920/1920 | 1107/1920 | 790/1920 | 0/80 |
| Familiar old | 2/24 | 1898/1920 | 1764/1920 | 964/1920 | 813/1920 | 12/80 |
| New function within expanded basis | 0/24 | 843/1920 | **1643/1920 (85.57%)** | 1651/1920 | 1498/1920 | 79/80 |
| New function within expanded basis | 2/24 | 850/1920 | **1507/1920 (78.49%)** | 1507/1920 | 1336/1920 | 80/80 |
| Outside even expanded basis | 0/24 | 1057/1920 | 1566/1920 | 1566/1920 | 1403/1920 | 80/80 |
| Outside even expanded basis | 2/24 | 1016/1920 | 1426/1920 | 1431/1920 | 1295/1920 | 79/80 |

**Positive bounded signal:** constructed ANF rules gained **800/1920 (+41.67 percentage points)** over fixed old templates for clean novel laws and **657/1920 (+34.22 points)** for corrupted novel laws. Compared to the strongest conventional forest, improvements were **+7.55** and **+8.91** points. Birth occurred in 79/80 clean and 80/80 noisy novel cases, but perfect rule identification is not established.

**Disqualifying weaknesses:** novel clean accuracy **85.57%** misses the >=90% frozen target; novel noisy accuracy **78.49%** misses >=80%. Familiar clean retention of the original bank was exact; familiar **noisy** cases triggered erroneous expansion in **12/80** worlds and lost **134/1920 = 6.98 percentage points** versus the unchanged old-Bayes control, breaching the <=2pp degradation limit. It is a genuine contradiction-triggering false alarm on the familiar structural family.

**Out-of-basis control:** constructing generic ANF helps on higher-degree truths even though their exact functions are **not in the 23,044-model bank**. These are extrapolations, not recovered exact laws. No claim of open-ended conceptual discovery, causal retention after session transitions, or general intelligence. The negative is that even a broad version space has a formal representation boundary.

## Audited evidence and numerical caveats

Independent source/reconstruction audit **PASS**; it does **not import the scorer**. It independently regenerates truth masks, SHA-ordered interventions, corruption positions, old/constructed Bayes predictions, all three conventional fits, and every 480-case held result, including 7 arms ×24 held outputs. In **48 stratified cases ×24 held** it additionally checks the complete ANF posterior prediction using exact unbounded Python integers rather than floating-point likelihood sums. Summary:

- **80,640** individual arm predictions independently recalculated; **11,520** held causal truths reconstructed; **1,152** exact-integer votes; **10,560** designated source/structure invariants. The aggregate is **103,872 checked values/invariants**, not 103,872 distinct unit-test functions. The conventional tree/forest auditor retrains the **same third-party sklearn implementations**, so this is an independent evidence rebuild but not an independent forest algorithm implementation.
- The independent augmented least-squares polynomial regression reproduced the scorer's kernel solution classifications on all held examples. **240** held ridge margins were numerically near zero (<1e-8); their exact sign may depend on environment and tie conventions. The audit matched this specific environment and thus cannot claim cross-platform bitwise reproducibility for those ties.
- The **first auditor execution failed only when serializing NumPy `int64` counters**; a second console-summary serialization issue was corrected in the auditor alone. `AUDIT-FIRST-FAILURE.md` preserves both. No frozen source, primary score, cohort or threshold changed.
- Fresh complete scoring-process semantic replay reproduced **all 480 case records and summary aggregates** byte-for-byte when wall timings are excluded; canonical SHA-256 **`07dedbe8eaf72bec08c39036af32be3269d92cdee128269f837bf09e8d6cdfa8`**. Original scoring wall **9.812s**, replay wall **9.964s** on local CPU. Those times include **all arms** and do not measure a relative learned-model speedup. Full native H200/Windows qualification was not executed.

## Frozen decisions and implications

| Gate | Result |
|---|---|
| familiar_loss_noise0 | PASS |
| familiar_loss_noise2 | FAIL |
| gain_vs_old_noise0 | PASS |
| gain_vs_old_noise2 | PASS |
| gain_vs_strong_conventional_noise0 | PASS |
| gain_vs_strong_conventional_noise2 | PASS |
| gap_to_full_exact_noise0 | PASS |
| gap_to_full_exact_noise2 | PASS |
| novel_accuracy_noise0 | FAIL |
| novel_accuracy_noise2 | FAIL |

**ENGINEERING:** frozen source and primary scoring, independent local audit, and semantic replay PASS. No accepted-source Yggdrasil full regression, Linux/Windows parity or original first-use was performed. GitHub archive must be verified separately before claiming remote evidence custody.

**SCIENTIFIC:** **DEVELOPMENT_NO_GO**, strong in-family construction improvement but missed absolute thresholds and familiar-noisy retention. Full exact ANF Bayes reaches virtually the same novel accuracy; the normalized energy viewpoint is equivalent, not a new model or special intelligence gain. Avoid retuning this scored cohort. Future work would need genuinely new modalities/actions and native CKAD competing-hypothesis integration only after independently qualified prospective science.

**DEPLOYMENT:** NONE. Existing Yggdrasil native learner / CKAD PR #1207, Wingless, Hybrid, FORGE owner and their respective research loops remain untouched. No controller, scheduler, new PR, protected scientific first-use, or merge.
