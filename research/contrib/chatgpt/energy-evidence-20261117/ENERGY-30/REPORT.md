# ENERGY-30 — Bayesian novelty evidence vs noisy contradictions

**Date:** November 18, 2026. **Status:** `DEVELOPMENT_NO_GO`. Isolated source-free synthetic CPU development study; no original-source first-use, no native Yggdrasil checkpoint run, no merge, no deployment.

## Motivation and source

ENERGY-29 exposed a costly error: a fixed minimum-mismatch trigger can expand the hypothesis space during noisy observations of an already known causal relation. Instead of posthoc trigger tuning, this experiment prospectively freezes a second mechanism: **the posterior odds that an observed consequence stream comes from a novel causal-function family rather than the retained original family**. The method is exact finite Bayesian evidence and is *mathematically* expressible as a normalized classical energy; it does not establish a distinctive energy architecture or a native CKAD improvement.

The source uses the original 160 familiar signed XOR3±AND2 relations and the general 23,044-function ANF (degree≤3, up to three terms) family from ENERGY-29, with an unchanged byte-identical source dependency and **new disjoint action-split namespace/seeds**. The actual hidden relationship, family ID, label flip positions and withheld outcomes are evaluator-only. All methods receive the same 24 witnessed action→consequence pairs. Every case has a disjoint 24-action test, with 16 further intervention combinations unused. A SHA-256 source-side generator selects 0, 2 or 4 corrupted training labels without disclosing their positions to learners.

**Frozen source:** SHA-256 `baa15cbe0eded0506fc4e31e102a135790d15b408cb8e0b37a8037c781283dd9`. **Frozen protocol:** SHA-256 `94ddc584df77a648b5571b42d410e8c25cb72f3574c7f84fc8b05624c94cdd4a`. **Original ENERGY-29 dependency:** SHA-256 `9dde0d8dbc70262d35404957a29b0405861b88caeaea7001767dbe9021443001`. The protocol, source and smoke preflight were frozen before scoring. Primary cohorts: four new seeds `3041,3061,3083,3109`, 20 source laws per seed and family, three corruption levels, three families = **720 independently fitted cases**. Separate smoke seed `9091` with 18 tests never enters scoring.

## Mechanisms and controls

- **Original mismatch trigger:** after the first 12 observations, admit the broad ANF family if the best familiar rule mismatches ≥2 witnessed outcomes; or admit after 24 when mismatches ≥3. Otherwise use the old 160-rule exact Bayes posterior.
- **New posterior-evidence trigger:** fixed prior probability 7/8 retained family and 1/8 general family; fixed assumed independent label-error probability 1/4. At 12 or 24 observations, expand only if \(P(\mathrm{general}\mid\mathrm{witnesses})\geq0.5\). Both families use fully normalized evidence over **all** their hypotheses. Once admitted, predict using the broad ANF posterior.
- **Soft two-family Bayes mixture:** retain both familiar and general families with 7/8:1/8 prior, marginalize rather than hard-admitting either; this is a strong uncertainty control and also an exactly normalized energy reparameterization.
- **Strong controls:** original familiar exact Bayes; always-expanded 23,044-function exact Bayes; fully fitted identical-feature kernel ridge, a depth-six decision tree, and a 31-tree ExtraTrees ensemble on identical witnessed evidence.
- **Negative control:** a third source family requiring quartic interactions or five-bit majorities, outside the ANF≤3 candidate grammar. Any apparent held success in this family is interpolation, not inferred recovery of a missing representation.

## Frozen results

All counts below are out of **80 worlds** for births and **1,920 independent held predictions** per arm and stratum. Higher held correct is better.

| Source family | Corrupt labels /24 | Original false/true birth | Posterior-evidence birth | Retained Bayes | Mismatch trigger | Evidence trigger | Soft mixture | Complete ANF Bayes | Trained forest |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| old | 0 | 0/80 | 0/80 | 1920/1920 | 1920/1920 | 1920/1920 | 1920/1920 | 1101/1920 | 862/1920 |
| old | 2 | 11/80 | 0/80 | 1896/1920 | 1760/1920 | 1896/1920 | 1896/1920 | 950/1920 | 818/1920 |
| old | 4 | 79/80 | 0/80 | 1816/1920 | 913/1920 | 1816/1920 | 1816/1920 | 915/1920 | 861/1920 |
| novel_in_basis | 0 | 80/80 | 66/80 | 823/1920 | 1591/1920 | 1460/1920 | 1480/1920 | 1591/1920 | 1529/1920 |
| novel_in_basis | 2 | 80/80 | 44/80 | 850/1920 | 1508/1920 | 1233/1920 | 1308/1920 | 1508/1920 | 1344/1920 |
| novel_in_basis | 4 | 80/80 | 30/80 | 878/1920 | 1411/1920 | 1102/1920 | 1191/1920 | 1411/1920 | 1246/1920 |
| outside_basis | 0 | 80/80 | 48/80 | 1051/1920 | 1553/1920 | 1330/1920 | 1376/1920 | 1553/1920 | 1435/1920 |
| outside_basis | 2 | 80/80 | 24/80 | 910/1920 | 1398/1920 | 1029/1920 | 1144/1920 | 1398/1920 | 1314/1920 |
| outside_basis | 4 | 80/80 | 16/80 | 895/1920 | 1329/1920 | 972/1920 | 1049/1920 | 1329/1920 | 1203/1920 |

### Key result: protected familiar knowledge, but excessive conservatism

For the familiar source with two corruptions, the original mismatch rule triggered **11/80 false hypothesis expansions**, whereas Bayesian evidence triggered **0/80**. With four corruptions the original falsely expanded **79/80** while Bayesian evidence again expanded **0/80**. The new method consequently retained the original Bayes model's held performance **1,896/1,920** and **1,816/1,920** respectively. The mismatch-triggered model fell to **1,760** and **913** correct. This was the desired *retention and false-alarm* effect.

In genuinely novel in-grammar worlds, the same 0.5 prior-odds threshold is too conservative. With clean evidence it admitted **66/80** new families and scored **1,460/1,920 (76.04%)**, below the original mismatch policy at **1,591/1,920 (82.86%)**. With two corruptions it admitted **44/80** and scored **1,233/1,920 (64.22%)**, while the mismatch policy scored **1,508/1,920 (78.54%)**. With four corruptions it admitted only **30/80** and scored **1,102/1,920 (57.40%)** versus mismatch **1,411/1,920 (73.49%)**. The fully expanded exact Bayes control remained stronger across all novel strata, though it catastrophically misclassified the familiar prior when it ignored that prior.

The soft posterior mixture also avoids familiar-world false expansion and improves over the hard 0.5 evidence gate on novel worlds, but does **not** overtake the strongest exact full-grammar control in novelty. These methods use the *same finite hypothesis candidates* and no extra learned causal representation: improvements or losses follow prior odds and admission decisions, not independent scientific learning.

## Frozen development gate

Frozen criteria were (1) cut familiar false-birth rate by ≥half at 2/4 corruptions, (2) lose ≤2 percentage points of familiar prediction against its original bank, (3) ≥80% clean novel births **and** ≥90% clean novel held accuracy, (4) ≥80% novel held accuracy with two corruptions, (5) at most 1 percentage point below the mismatch policy in *every* novel corruption stratum and strict improvement in at least one, (6) beat strong full Bayes and conventional trained controls for any energy-specific performance claim.

**Results:**
- `PASS` — `noise2_false_birth_at_most_half`
- `PASS` — `noise4_false_birth_at_most_half`
- `PASS` — `familiar_retention_within_2pp`
- `PASS` — `novel_clean_birth_at_least_80pct`
- `FAIL` — `novel_clean_accuracy_at_least_90pct`
- `FAIL` — `novel_noise2_accuracy_at_least_80pct`
- `FAIL` — `novel_minus_mismatch_at_least_minus1pp_each`
- `FAIL` — `strict_improvement_over_mismatch_one_novel_stratum`
- `FAIL` — `beats_full_grammar_and_conventional`

**Overall: `DEVELOPMENT_NO_GO`.** The false-alarm and familiar-retention gains are substantial, but are insufficient to offset the large novel-classification losses. **Do not tune the existing 0.5 threshold on these consumed scored worlds.** This is a useful falsification of *a threshold proposal*, not a negative verdict on all Bayesian or energy-based novelty detection.

## Independent qualification and limitations

An independently implemented auditor, with no import from the scorer or generator, rebuilt all 720 source-law truth tables and 24/24 SHA-selected action splits, verified every corruption index and withheld causal truth, and independently refitted all 720 conventional decision trees and 31-tree ensembles, plus an augmented least-squares variant of the regression. It rederived the old/general evidence and all four principal posterior prediction arms on all cases, using **exact integer posterior arithmetic on a prospectively fixed nine-case stratum sample** (one per family/corruption combination). **125,326 source and inference assertions PASS; 138,240 held prediction comparisons validated; 9 exact posterior certificates PASS.** 257 original ridge held predictions have very small numeric margins under this source design; independent augmented fitting produced zero differing classifications, so no numerical scoring repair was needed.

Independent full 720-case source replay (same frozen code, fresh process) matched byte-for-byte once only run-specific elapsed timing was excluded. Semantic SHA-256 `32fb6bf60aab65ae3d1ede0bc8032f6aba8cfad64ab1f0e03269a6d33e5d5ac7` in both runs. Original primary source `scored.json` SHA-256 `772d220db99dcc731191e37422c1aad7a6f0534f821142bc8c3f3af4826a038f`. No scored outcomes, model weights, thresholds, seeds, priors or admitted evidence were modified following primary scoring.

The test requires *named synthetic causal families* that are known to the experimenter but hidden from the learner. It does not establish open-ended concept invention, native Yggdrasil retention in an unsignaled stream, statistically independent generality beyond the four training seeds, GPU efficiency, native deployment, or original-source scientific first-use. It did not execute the native CKAD checkpoint; its observation interface is standalone five/six-bit synthetic causal truth tables, not the complete CKAD two-stage episode structure. The full 18.42-second local CPU test wall is combined overhead across all arms, **not** an individual-model end-to-end speed comparison.

## Engineering, science and deployment

- **ENGINEERING:** Frozen score, replay and independently reconstructed local audit **PASS**. Full final native dual-OS Yggdrasil regression and G29 atlas acceptance for this isolated archive branch remain separately unverified until CI status is checked on the exact candidate SHA; do not describe these synthetic audit results as native acceptance.
- **SCIENCE:** `DEVELOPMENT_NO_GO`, `scientific_pass=false`; familiar-noise robustness improved, true novelty admission/prediction **failed**. No energy-specific superiority to a correctly normalized Bayesian control demonstrated.
- **DEPLOYMENT:** NONE. Existing CKAD hypothesis tournament and action planner, research owner/controller/scheduler and unmerged native PR are untouched.

**Next falsifiable question:** Can a *single learned novelty belief* accumulate evidence over successive action–consequence episodes and transition smoothly from retained hypotheses to newly generated causal explanations, with calibrated false alarms and minimal retention loss, without a hand-picked family threshold? This requires a **new** frozen temporal protocol and native controls, not tuning this consumed 720-case grid.
