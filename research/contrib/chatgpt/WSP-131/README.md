# WSP-131 — transfer a learned causal rule when variable meanings change

**Source-safe public DEVELOPMENT only. No independent scientific first-use, accepted native model mutation, new controller, or merge.**

## Why this is a new experiment

WSP-130 [draft PR #1162](https://github.com/spoonman136668-ai/Yggdrasil/pull/1162) at exact full-qualified `86f7afeeff4f0f93ddd4b73adcd92f73ad5f25a2` wrote 64 previously absent high-order causal conjunction supports directly from source-visible consequences. Its identical symbolic control tied it, and 16 adversarial hidden one-bit changes escaped observation; the released synthetic model never demonstrated relinking a known relationship to **new variable roles**. WSP-130's zero-source transfer merely renamed opaque action IDs, leaving public input feature semantics unchanged.

WSP-131 tests that missing cognitive step, without reopening already-consumed CausalGym episodes in NKR-19 or CVH-04.

## Frozen preregistration before code or results

First and only preregistration commit: `436866e837c6da6430cb3c90a081245c077d71ee`. Parent WSP-130 exact final above. Source, budgets, accept/reject thresholds, independently trained controls, seeds and negatives were frozen before implementation.

- **Warm knowledge:** re-train existing WSP-130 direct coefficients and its separate exhaustive symbolic control from **128 genuine source consequence observations per each of 64 already exposed synthetic quartic/quintic laws**, 8,192 paid effects per arm. Retain full old 256-effect truth functions and untouched original model snapshot.
- **Changed meanings:** 64 fresh synthetic 8-input worlds, each formed by unknown permutation of six input roles while retaining two anchor roles. Reindexed actions have new opaque public subjects and original semantics are hidden from the learner. There are **720** possible semantic maps, all initially eligible.
- **Out-of-class negative:** 32 additional worlds apply a genuine invertible binary linear shear after the permutation, selected source-only to be observationally different from every pure permutation of the old rule over the full domain. A learner assuming only permutations must detect the mismatch or abstain rather than invent valid confidence.
- Each changed/negative world gets exactly **32 actual paid consequences per arm**, 224 truly withheld effect predictions. Run **0/4/8/16/32** acquisition checkpoints with each checkpoint's predictions frozen before future outcomes. Evaluation for every checkpoint is made only once, on the final withheld set. All 96 worlds cost 3,072 target-source effects/arm; 16 zero-source new-ID replays score 4,096 more effects on learned mapping with zero feedback. This is still public synthetic source, **not independently sourced physical novel environments**.
- New **720-bit numeric weight bank** is initialized to all mappings. Source-visible causal contradiction eliminates inconsistent mapping weights. Adaptive intervention chooses the x that most evenly divides the remaining supported hypotheses; no true permutation/shear/future source data is imported.
- Strongest comparator: separately implemented **exact exhaustive symbolic learner over all 720 permutations**, receiving the IDENTICAL 32 source actions and outcomes as the numeric bank. A source-blind greedy **optimized fixed 32-probe symbolic comparator** receives a different set of 32 real outcomes at equal cost, with probes selected to separate as many candidate mappings as possible without feedback.
- Additional conventional control: **deterministic fully grown, fully fitted CART** (max eight binary decision levels, min leaf one), trained on exactly the same 32 acquired consequences. STALE_PRIOR assumes old roles never changed and predicts all cases; NO_UPDATE always abstains. Strong symbolic parity is **required**, and numeric-vs-symbolic ties cannot support numerical weight-space superiority.
- Frozen target gate at 32 probes: >=95% correct on 14,336 held, <=1% confidently wrong, >=58/64 worlds have an identifiable and actually correct full 256-effect function, >=20 percentage points correct coverage over stale prior, zero-source transfer **4096/4096** correct, and perfect cold preservation of original warm knowledge.
- Frozen negative: >=30/32 nonpermutation shears cause all 720 candidates to be eliminated and <=1% confidently wrong across 7,168 held; active fit coverage no more than 2pp worse than fixed symbolic. Positive/negative failure = DEVELOPMENT_NO_GO, even if other metrics look impressive.
- Fit and scoring are source-blind, evidence is authenticated by per-action chained receipts, and tampered learned masks with newly forged checksum must fail replay. All original scientific source/held first-use remains disarmed and unrelated Yggdrasil research owners unaffected.

## Run and qualify

```bash
python -B -m unittest discover -s research/contrib/chatgpt/WSP-131 -p 'test_*.py' -v
```

The focused suite scores one complete preregistered public development experiment and prints `WSP131_FINAL_ENGINEERING_JSON`. The branch-local workflow verifies the *first prereg-only commit*, no protected sources, two-OS original development, then pins only three derived G29 source-atlas outputs. Full exact-candidate mandatory regression of WSP117–131 and root tests runs on **Ubuntu and Windows**, plus independent G29 acceptance. A successful engineering gate **does not** permit actual scientific first-use, accepted main mutation or native integration.

**Interpretation boundary:** recovering a hidden permutation **within a supplied 720-permutation grammar** demonstrates a bounded variable-binding mechanism, not autonomous discovery of arbitrary semantic relationships. If a changed world's function is indistinguishable under paid observations, abstention is necessary. No claims of general intelligence, human language understanding, real causal science, energy efficiency, or superiority over the strongest exact symbolic control are warranted. Preserve negative results and do not retune exposed worlds.
