# ENERGY-28 — Generating previously absent causal interaction hypotheses

**Date:** 2026-11-18. **Outcome:** `DEVELOPMENT_NO_GO` on prospectively frozen, isolated synthetic evidence. **Scientific:** UNVERIFIED, no native Yggdrasil learning or first-use. **Deployment:** NONE.

## Question

Can a causal learner that initially knows only **40 signed three-input parity relations** generate causal hypotheses that it did not originally contain when *witnessed interventions* contradict that bank? Would generating an interaction rather than merely reweighting old hypotheses improve prediction on unseen interventions, without sacrificing previously known relationships? The new interaction is a two-input conjunction added as a parity correction: `XOR(three parents) XOR AND(two other action bits) XOR sign`. Its **120 possible signed instances** are absent from the initial bank.

**Scope limitation:** This is finite-grammar composition, not unrestricted conceptual invention or native causal representation growth. The causal template grammar was designed by the experimenter and the candidate expansion rule was frozen beforehand. The method is mathematically a finite Bayesian mixture / classical energy over rule consistency, **not a demonstrated advantage of energy models**. It is not CKAD's existing context-candidate implementation.

## Freeze and evidence provenance

The primary scoring executable and protocol were frozen *before* evaluating primary seeds. Only separate smoke seed `8009` was used for implementation preflight. SHA-256 identities:

| Artifact | SHA-256 |
|---|---|
| `experiment.py` | `e707c20e67692f9e229f23a2daf3de4f8ad4243dd5ec900fc4bc175b4839d7e4` |
| `protocol.json` | `08f168d9d28969be54ad3764dbcbfa8f394be270e8c0cbe2beae77c20db28021` |
| `scored.json` | `6f3cc544726db4fd7bdb06a73e3eae1e6f6ae60cb181be094ee2f8b583260656` |
| Replay semantic record | `5267aab234442a7c745ca18809b8ca6a44030beeaf455c668a1f8144cb36142b` |

Original source laws: six binary intervention variables. Forty initial signed XORs of three parents, plus 120 two-nonparent-bit conjunction corrections. Every training world has 16 witnessed action/outcome pairs, 16 distinct unobserved test interventions, and 32 unused intervention combinations. Source truth, law ID and withheld outcomes are not passed into the inference methods. Three primary seeds `1811, 1823, 1831`; all 160 source laws; training corruption strata of 0 or exactly 2 flipped outcomes per world. **960 independently fitted world/regime cases**, **15,360 distinct held causal predictions per arm**. No protected original scientific data used.

**Comparison arms** all see the identical revealed data: (1) fixed old 40-rule exact Bayesian posterior, (2) evidence-triggered 120-rule birth and exact posterior, (3) fully fitted **strong exact Bayesian all-160-rule control**, (4) fully fitted 160-feature conventional kernel ridge, and (5) hard MAP ablation after birth. The rule models use fixed 1/8 assumed observation-error probability and prior mass 7/8 on the initial family, 1/8 on the new family (uniform within families). The source action-split permutation uses a source-side hash keyed by rule ID; only chosen intervention vectors and revealed outcomes are given to the learner, and none of the fitted models uses the rule ID, seed or split algorithm. This is a finite synthetic design, not randomized independently of structural family.

A new candidate is generated only when the smallest mismatch among the original rules is at least two after eight witnessed outcomes, or at least three after sixteen. Once generated, all previously observed evidence is re-evaluated under the expanded grammar. No new hidden rules are directly supplied to the predictor, no held-out label is used during fitting, and the original bank is not overwritten.

## Frozen primary results

| Source worlds | Old 40 rules | Hypothesis birth | Exact full grammar | Fully fitted ridge | Hard MAP birth | Births |
|---|---:|---:|---:|---:|---:|---:|
| Familiar, clean (120 worlds) | **1920/1920** | **1920/1920** | **1920/1920** | 1191/1920 | 1920/1920 | 0/120 |
| Familiar, 2 corruptions (120) | **1911/1920** | 1905/1920 | 1905/1920 | 1119/1920 | 1906/1920 | 10/120 |
| Novel interaction, clean (360) | 3350/5760 | **5356/5760 (92.99%)** | **5615/5760 (97.48%)** | 4732/5760 | 5361/5760 | 293/360 |
| Novel interaction, 2 corruptions (360) | 3115/5760 | **4589/5760 (79.67%)** | **4590/5760 (79.69%)** | 4058/5760 | 4529/5760 | 324/360 |

### What succeeded

The newly generated hypothesis family improved held causal prediction by **2,006/5,760 (+34.83 percentage points)** in clean novel worlds and **1,474/5,760 (+25.59 percentage points)** in corrupted novel worlds compared with the original bank. The learner generated new rules in **81.39%** of clean novel worlds and **90.00%** of noisy novel worlds, surpassing its frozen >=80% birth gate. A top-posterior newly generated hypothesis was selected in 293/360 clean and 225/360 noisy novel worlds. Thus, an initially absent causal *rule template instance* can be constructed from contradictions and fitted on witnessed consequences. This is a real synthetic mechanism result, not proof of general intelligence.

Familiar knowledge was preserved exactly in all 120 clean familiar worlds. Under two training corruptions, **10/120** familiar worlds triggered erroneous birth; six additional held outcomes were lost relative to the original-family control. This is a detectable cost of allowing revision under ambiguous evidence.

### Why the frozen gate failed

The protocol required >=90% novel held accuracy with zero corruptions; >=80% with two corruptions; >=10 percentage-point gain over the original bank in each stratum; >=80% novel birth; <=1 percentage-point loss against the strong full-grammar Bayes in **each** stratum; and <=10%/20% false birth on familiar worlds at clean/two-corruption levels.

- Novel birth coverage: **PASS** both.
- Novel accuracy: clean **PASS**, noisy **FAIL (79.67% vs >=80%)**.
- Gain over original bank: **PASS**, both.
- Strong exact Bayesian control parity: noisy **PASS** (one prediction deficit); clean **FAIL** (259 predictions deficit; **4.50 percentage points**).
- Familiar false-birth: **PASS**, clean 0/120; noisy 10/120 (8.33%).

**Overall: `DEVELOPMENT_NO_GO`**. The missed candidate-births on 67/360 clean novel worlds explain the main gap against an always-available correctly specified grammar; do not change the trigger after seeing these outcomes. The fully trained conventional ridge model is weaker here, but the strongest exact Bayesian control remains better in clean worlds and essentially tied in noisy ones. The posterior/energy calculation itself is mathematically equivalent to Bayesian rule weighting; no energy-specific superiority is established.

**Resource/cost:** Primary wall time was about **0.307 CPU seconds** for **all** arms together in this optimized Python/NumPy process. The experiment computed the full-grammar control on every case, so this wall time is **not** a selective-generation versus full-search speed comparison. An analytical count of candidate train evaluations would be 40*960 + 120*627 = 113,640 versus 160*960 = 153,600, about 26% fewer, excluding trigger overhead; no claimed >=1.5x measured acceleration, native training, GPU timing, or whole-process advantage.

## Independent audit and reproducibility

An independently implemented source/truth generator and exact-integer Bayesian posterior audit (`independent_audit.py`, **does not import the scorer**) regenerated all 960 source cohorts, 16 observed outcomes per case, 16 withheld truths, exact candidate-birth decisions, 16 held decisions for four structural arms, hard-MAP tie-breaking, and separately refitted the conventional ridge system with SciPy. **37,456 independent assertions PASS; 76,800 held arm predictions verified.** There were **zero** numerically near-zero ridge margins and zero independent ridge disagreements. The original source and protocol hashes match the pre-score freeze. A fresh independent scoring-process replay matched **all 960 semantic case records** byte-for-byte after excluding only runtime timing fields. Source seed namespaces were new and the smoke seed never entered primary scoring.

Reproduce in a qualified Python 3.12/3.13 environment with NumPy and SciPy, with single-threaded BLAS for comparable timings:

```bash
OPENBLAS_NUM_THREADS=1 python -B experiment.py --smoke --output smoke-replay.json
OPENBLAS_NUM_THREADS=1 python -B experiment.py --output scored-replay.json
# compare scored-replay.json to scored.json after excluding aggregate.measured_full_process_wall_seconds
OPENBLAS_NUM_THREADS=1 python -B independent_audit.py
```

## Engineering / scientific / deployment classification

**ENGINEERING:** Local source freeze, full synthetic scoring, independent audit, semantic replay, and GitHub evidence custody **PASS** after upload verification. Mandatory final native-source dual-platform G29 regression on Yggdrasil candidate **NOT EXECUTED**; historical G29 atlas failures are engineering-only. Do not confuse isolated audit with CKAD acceptance.

**SCIENTIFIC:** **DEVELOPMENT NO-GO / SCIENTIFIC_PASS=false**. This test demonstrates a bounded compositional candidate-birth mechanism and its evidence-conditioned limitations, **not** unbounded causal structure invention, persistent native state, unfamiliar-world transfer, or independent generality over fully trained conventional controls. No new protected held first-use or CKAD preexisting dataset was consumed.

**DEPLOYMENT:** NONE. Existing CKAD developer research and independent Wingless/TTT-Hybrid tracks untouched. No accepted ref, native model, runner, controller, research scheduler, merge, or promotion.

**Research decision:** Preserve this limited positive mechanism, but stop trigger tuning on these scored worlds. Next useful falsification is *true causal functional novelty* beyond the handcrafted XOR+AND grammar and stronger open-grammar learned controls, ideally under the native CKAD action/observation interface with pre-registered retention and whole-process cost; first-use and native qualification must remain separately authorized.
