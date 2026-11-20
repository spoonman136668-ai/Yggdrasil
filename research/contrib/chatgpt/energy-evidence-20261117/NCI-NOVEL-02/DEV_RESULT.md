# NCI-NOVEL-02 — Original frozen source-free development result

**Primary classification: REPRESENTATION DEVELOPMENT PASS (4/4 family gates), SCIENTIFIC SUPERIORITY DEV NO-GO (0/4), NEGATIVE-CONTROL INCOMPLETE (6/8 safely unidentified).** Independently scoped Yggdrasil contributor. Not an authenticated native learner, accepted scientific improvement, or activation.

## Chronology and custody

1. New [prereg committed before source](https://github.com/spoonman136668-ai/Yggdrasil/commit/e16fbf1b6c320a581719f9f01c05a01d3652c352); source-free DEV seeds `[592113, 592127, 592139, 592157]` reserved. Prior NCI-NOVEL-01 primary seeds were **not reused**.
2. Implemented source-free Python and ran 13/13 focused unit tests + exposed engineering pilot seed **592101** only (2 families). Fixed a pilot-observed floating-point cold-checkpoint equality issue by lossless float.hex() encoding and a 65,536-byte checkpoint overflow by deterministic zlib-compressed canonical source-fixture state **before source commit**. No primary seeds consumed for these fixes. Pilot result preserved.
3. Frozen [complete original source, contracts, pilot, manifest](https://github.com/spoonman136668-ai/Yggdrasil/commit/4f259728b9e8a941697989dcd2297208e83de3e0) with 7/7 exact GitHub blob readback PASS, then executed the primary source-free development **once** on four untouched seeds: 592113/592127/592139/592157 × eight independent synthetic families = **32 worlds**.
4. After the primary completed, ran a separate **report-only** independent arithmetic/provenance audit (`audit.py`, `audit.json`); it did not import or execute the evaluator or generate any new actions, observed outcomes, or primary seeds.
5. Raw complete 32-world `primary_result.json` is archived with SHA256 `dc3fe45bf32237b44b889366a447a147d8c1452e127f04c8ec64de90ae5918a0` (93,157 bytes). Source SHA identities and runtime are in `source_manifest.json` and `provenance.json`. This publication adds result/provenance/audit files **without changing** any frozen source code.

## Experiment

All source observations are synthetic. Evaluator hides the actual laws and returns only public four-bit factors, two source-declared action-role identities, the chosen binary action, true witnessed transition, and reward. Both candidate and controls receive the same 64 old and 96 new training episodes, 32 VALID evaluation episodes (no fitting), 32 HELD_SHARED prequential common action/transition/reward episodes, 32 actual separate HELD_POLICY action episodes per policy, and 64 OLD_RETURN evaluation episodes. Two actions per episode; source-free budget 8 families × 320 episodes ×2 = **5,120 possible actions per arm per primary seed**, though VALID and OLD_RETURN are evaluation-only and not admitted into the model. Source-free online weights/ledger are isolated per world; **these are not one lifelong model**.

The `GATED_MAP` candidate obtains posterior factor support within a **prewritten finite grammar** of Boolean signatures (constants, literals, parity ≤4 variables, pairwise AND/OR, and two-input gates XOR third input). When source evidence supports the fourth variable and two or more actual contrast contexts exist, it gates from Bayesian averaging to a MAP readout; otherwise it preserves the posterior average. Its explicit closed-program grammar already includes the four novel demonstration families. Fully fitted **same-grammar exact Bayesian BMA** uses the same evidence, grammar and posterior; no oracle correct equation is supplied. Also fit a three-factor restricted BMA ablation, full tabular Beta, all-subset backoff Beta, recurrent context Beta and frozen-old source-only benchmark. VALID alone selects the strongest comparison before HELD. There is **no matched trained neural RNN**; the 'RECURRENT' comparator is a fitted finite-context Beta table, not a recurrent neural network.

## Original held results — lower Brier is better

| New causal family | Both stages identified (seeds) | Candidate held Brier | No-fourth ablation | VALID-selected fitted control | Candidate policy reward | Fitted-control policy reward | Representation gate | Fitted superiority gate |
|---|---:|---:|---:|---:|---:|---:|---|---|
| novel_cross | 3/4 | 0.058600 | 0.204368 | 0.058600 | 0.93750 | 0.93750 | PASS | FAIL |
| novel_guard | 4/4 | 0.072350 | 0.236976 | 0.072350 | 0.97656 | 0.97656 | PASS | FAIL |
| novel_parity4 | 4/4 | 0.062037 | 0.424928 | 0.062037 | 0.93750 | 0.93750 | PASS | FAIL |
| novel_toggle | 4/4 | 0.058600 | 0.405755 | 0.058600 | 0.96094 | 0.96094 | PASS | FAIL |

Across the 16 genuinely new-family world cells: candidate held Brier **0.062896875**, compared with **0.318006976** for the deliberately feature-deprived baseline and **0.062896875** for full same-grammar exact BMA. Actual policy reward candidate **0.953125**, exact BMA **0.953125**. Thus a large gain over a weakened representation **does NOT mean an improvement over a complete conventional/exact Bayesian learner**. Candidate 4/4 representation families pass its limited prespecified gate, while **0/4** achieve the required 5% plus utility improvement over the VALID-selected strong control.

**Key negative:** for the out-of-class family, candidate false-identified the transition relation on seeds **592113** and **592127**, despite insufficient expressivity to represent its actual law. Out-of-class held Brier (mean) is approximately 0.212753 candidate vs 0.090885 strongest fitted control, a serious confidence/representation failure. All four unidentifiable-constant-fourth-factor worlds abstained; only **6/8** prespecified negative worlds abstained correctly overall.

OLD source bank digests stay byte-identical before and after NEW fitting and OLD_RETURN scoring; native-style research-fixture cold checkpoint identical after restore, max candidate serialized bytes **32,773** (<65,536). **Functional old performance is protected here by separate namespaces and readout isolation, not demonstrated generalized lifelong retention or automatic recall.**

## Qualification and unresolved limits

- **ENGINEERING — local contract and exact source freeze:** 13/13 unit tests PASS, pilot 2 worlds, source GitHub 7/7 PASS, report-only result audit PASS; 32-world primary one-shot. `primary_result.json` and source frozen in separate commits. Raw result audit proof pinned in `provenance.json`.
- **SCIENTIFIC — no superiority:** both candidate and exact BMA had identical mean new-family Brier and policy reward. Out-of-grammar false identification is a definite negative; no GI, unseen physical law, autonomous model growth or native causal intelligence claim. Fitted conventional baselines do not include an actual neural RNN. Program grammar is manually prespecified. Full matched compute is **NOT qualified**.
- **Performance cost:** locally instrumented candidate CPU 6.221064s vs BMA 3.536715s covers training and selected held phases, **not all validation/return/serialization costs**. RAM and true matched compute not qualified; no speed/efficiency claim. Program uses Python's `resource` import which is not portable to Windows without qualification. Full Linux/Windows final regression remains **UNVERIFIED**.
- **DEPLOYMENT — none:** no canonical Yggdrasil training, accepted main, actual native checkpoint, first-use, new controller or model owner, merge or installed integration. [Source owner #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) still blocks original-world first-use. Preserve original NCI-NOVEL-01 and ENERGY negatives.

## Proposed research pivot, not post-result retuning

**Do not install or retrain this candidate on consumed seeds.** A genuinely new preregistered successor would test **source-likelihood model criticism and explicit abstention for out-of-class mechanisms**, with fresh untouched cohorts, fully fitted non-symbolic conventional controls, and true novel action/factor identities, not reuse this scoring set. The sole central coordination/owner boundary remains **Unified Causal Intelligence Amalgam Work chat** PR #1278. This contribution is research evidence only.
