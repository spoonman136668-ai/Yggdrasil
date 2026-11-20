# ENERGY-63 — Factorwise causal knowledge reuse after interference

**Scientific decision: SCREEN_NO_GO (5 of 8 frozen screening gates PASS).** External synthetic evidence only. **No primary, native Yggdrasil training, new runtime, accepted-ref update, merge, autonomous loop change, scientific pass or deployment.**

## Frozen GitHub custody

- Previous evidence head: `f8c5d137ff2d049213de2b4161b28b0e1301c412`.
- Exact source/auditor GitHub freeze commit **`b91e56278afdbd5005c25702933f001ade37d252`**, Git blob `8b2972f91ecf50e1546f97c9d2f7ce94fd34e1c0`; source tar SHA256 `1b300aa3caac9aa83196415811a10bfdc4be498fffecfda493edd4dd367dbeb5`.
- Separate prospective preregistration commit **`aa4d525ab6ba2e1931a4e658bc9c54fb4ddd7c6a`**, read back with source blob before any new seed result.
- Excluded development smoke `998203`, one world ID per family = 3 worlds, independently audited (14,639 checks PASS); not prospective.
- **Prospective 24-world screen:** untouched seeds `998269`, `998281` x four world IDs x three families. **Reserved primary seeds `105101`, `105119`, `105137` NOT USED** because decisive direct comparator gates failed.
- Frozen scorer SHA256 `5acf19cb7d54cfc10c7cb537fbf5ea70ac7d1eb5e21802be3fcb19bf4b8571d8`; independent auditor SHA256 `83ae13d1ac7426dcdb76690fc02bd254fc5b1987ad567d074a9853c53125a678`.

## Question, causal mechanism, and equal information

Can a bounded causal-factor memory retrieve independent pieces of previously learned mechanism knowledge after intervening training contexts, using only **six labeled recovery interventions**, and generalize through nuisance-distribution shift? Each world contains ten binary causal intervention variables, two nuisance cues, and four unknown pairwise signed parity factors. A/B/C contexts each provide **80 witnessed actions** and have changed factor coefficients. Returning context D uses (a) factorwise recombination; (b) intact return to A; or (c) factorwise recombination with a novel four-variable effect **outside the learner's pair dictionary**. The contributor-generated worlds have exactly **502 disjoint causal intervention identities each**: 240 witnessed history, six witnessed return probes, and 4 x 64 withheld A/B/D/COLD actions. Noise sigma=.16. Cue correlations shift with context; COLD cues are randomized independently.

Every arm gets the same historical data and the **same six labeled D probes**, but no hidden regime identifier, planted support identities, held labels or planted coefficients. The candidate selects **four learned pair supports from OLD only**, then stores three fitted stage coefficient vectors and selects one observed coefficient per support from A/B/C. The 81 possible factor combinations are a **researcher-defined finite codebook**; candidate MAP selection minimizes squared six-probe error plus .16 for each factor changed from A. A/B historical readout heads are immutable and can be restored from stored numeric state. This is not unrestricted operator invention or native continual learning.

**Decisive matched control:** conventional exact Bayesian posterior averaging over the same 81 factor choices, identical learned supports and snapshot coefficients, with fixed prior [.50,.25,.25] and Gaussian calibration likelihood sd=.36. Other controls: conventional three-snapshot softmax, best snapshot, matched support-prior Ridge, fully trained pooled/recent 66-feature ElasticNet, recent fully fitted RBF KRR, frozen no-update and shuffled-probe negative. Identical witnessed data do **not** imply equal compute or equal expressivity across all methods. We make no physical energy-efficiency claim.

## Prospective 24-world prediction error

| Policy | Cold MSE ↓ | Return MSE ↓ |
|---|---:|---:|
| `factor_bayes` | 0.877572 | 0.823287 |
| `factor_map` | 0.930849 | 0.868688 |
| `factor_ridge` | 1.280635 | 1.293345 |
| `softmax_memory` | 3.201628 | 3.233292 |
| `best_snapshot` | 3.206381 | 3.237333 |
| `recent_elasticnet` | 10.910361 | 10.964959 |
| `pooled_elasticnet` | 5.183238 | 4.386040 |
| `recent_krr` | 6.952653 | 6.929424 |
| `old_no_update` | 3.307906 | 3.379030 |
| `shuffled_probe` | 8.061962 | 8.153507 |

**Proposed factorwise MAP cold MSE = 0.930849; exact Bayesian factor memory = 0.877572 (candidate 6.07% MORE error).** Candidate improves 70.93% relative to conventional whole-snapshot softmax, but **that is an insufficient comparison** because the stronger conventional exact Bayes uses the same compositional codebook and labels. In other words, factor-level reuse helps on authored synthetic mixes; this specific hard-selection mechanism is not supported against conventional posterior integration.

### Independent prospective seeds

| Cohort / family | Candidate | Exact Bayes | Softmax memory |
|---|---:|---:|---:|
| `998269` | 1.282114 | 1.177393 | 3.725419 |
| `998281` | 0.579584 | 0.577751 | 2.677837 |

### Distinct mechanism families

| Cohort / family | Candidate | Exact Bayes | Softmax memory |
|---|---:|---:|---:|
| `novel_quad` | 2.741370 | 2.582067 | 5.107274 |
| `recombine` | 0.026601 | 0.026638 | 4.473035 |
| `return_old` | 0.024576 | 0.024011 | 0.024576 |

The proposed learner's nearly perfect performance on recombination/old-return is largely **because the generator and candidate both use the supplied finite primitive-factor algebra**. On `novel_quad`, both candidate and Bayesian control suffer because the new four-way factor is absent from that algebra. The synthetic worlds therefore do not demonstrate unlimited unfamiliar-operator generalization, true native learning, or human-like cognition.

## Frozen gates and stop decision

| Preregistered gate | Result |
|---|---|
| `both_seeds_win_strongest` | **FAIL** |
| `cold_gain3_vs_exact_factor_bayes` | **FAIL** |
| `cold_gain3_vs_softmax_memory` | PASS |
| `cold_gain5_vs_best_other` | **FAIL** |
| `factor_switches_exercised_20pct` | PASS |
| `family_non_degradation_10pct` | PASS |
| `old_exact_frozen` | PASS |
| `shuffled_negative_20pct` | PASS |

**5 PASS, 3 FAIL ⇒ `SCREEN_NO_GO`.** The critical `cold_gain5_vs_best_other`, `cold_gain3_vs_exact_factor_bayes`, and `both_seeds_win_strongest` requirements failed. No change to the source, threshold, model, intervention count or seeds after scoring. No reserved primary scored.

## Audit, reproducibility, limitations

- Independently authored auditor `audit.py` reconstructs all planted interventions and source outcomes **without importing scorer**, then refits each conventional/candidate model, verifies each prediction vector/hash, 502 disjoint causal assignments per world, and all published aggregates. **PASS: 116,562 checks across 24 worlds** and ten modeled arms. It shares NumPy/scikit-learn numerical solvers and the disclosed generator rules; therefore **not an independent scientific replication**.
- The original `screen_scored.json` is 2,029,975 bytes, SHA256 `774fe2fa26926c79ec1200d1c1069fe62c322d7a914ea7a11acf31902924eae6`; all 24 worlds have raw observed and held outcomes, selected factor IDs, candidate coefficients and all model prediction vectors. Original independent audit and both excluded pilot records retained.
- Unchanged frozen-source replay **PASS**, semantic SHA256 `9440692f986a2d002e2936343b0c5ab8c8f6471e22f088ece6c5862d8f22b4f8` across 2,029,936 bytes. Excludes only `runtime_seconds`. Independent audit repeated on replay PASS 116,562 checks; replay is deterministic verification, not a fresh scientific dataset.
- The local scorer runtime was 0.1791 s in a single-thread process; this does **not** include audit, replay, GitHub transfer, CI, native regression or physical energy cost. Original source and all original evidence files are preserved in the split `EVIDENCE.tar.bz2` archive with manifest and verifier.
- Native Yggdrasil checkpoint state, accepted branch, controller, queues, official research-loop training and deployment remain unchanged. GitHub CI and full native qualification are separately reported in the final status rather than represented by local audit PASS.

## Decision

**Keep exact Bayesian factor-memory retrieval as the strongest conventional comparator on these constructed recombination worlds.** Factor representations are useful in this *bounded* setting, but hard MAP selection was not better than Bayesian marginalization. A genuinely disjoint successor should test transfer of factor semantics to **previously unseen input mappings and operators**, using unconsumed seeds, a frozen strongest matching control and native-owner qualification separately. Do not promote/tune this failed screen or consume the reserved primary.
