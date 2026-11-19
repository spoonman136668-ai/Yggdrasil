# ENERGY-59 — Context-blind persistent causal-memory functional retention

**2026-11-19. Classification: DEVELOPMENT_NO_GO (6/10 frozen gates PASS).** External synthetic research only. No native Yggdrasil model training, SCIENTIFIC_PASS, merge, accepted-ref or autonomous loop changes.

## Exact custody and temporal ordering

Previous archive HEAD: `99756a3550f7cdcc0f34e982bfc7750b2d15d178`. Frozen scorer and separately authored refit auditor **committed before primary** at [`7563eb7471f97a0da2bbff4d1302905c8985fa8b`](https://github.com/spoonman136668-ai/Yggdrasil/commit/7563eb7471f97a0da2bbff4d1302905c8985fa8b). A different commit [`fa6fb59fc796a6bc3a151165f5338e5b0dc2e019`](https://github.com/spoonman136668-ai/Yggdrasil/commit/fa6fb59fc796a6bc3a151165f5338e5b0dc2e019) froze 10 gates and primary seeds **101101, 101119, 101141** before the first primary result. Documentation note: the pre-primary README described “nine” gates in one sentence, but the actual authoritative GitHub preregistration froze **ten** gates before scoring; no outcome or threshold changed. The source tar SHA-256 is `999fc5bc1bfcc892af3bf9d16e0dca990fb1da6b535e48d452336f7f054b5205`, scorer `7bc7bbb204a058a424313a3562a48fda824e3cdebbea00e671f7fa5f5bb8138c`, audit `faf60818fe29b3a2cdfcec0583a31e819cfe22ca58f3d33fb8af909589dd2c62`. Excluded development smoke seeds **998911 and 998921** were tested before freeze (each 3 worlds and audited). Candidate vs matched best snapshot was mixed across these two excluded cohorts (0.031196 vs 0.032461, and 0.029770 vs 0.028906), so primary gates were not adjusted to favor the candidate.

## Mechanism and matched controls

**36 worlds** = three fresh seeds, four source IDs, three distinct families (`return_old`, `return_middle`, `novel_composition`). Each world has **nine underlying causal action bits** and three observed nuisance cues; every causal action assignment is unique across chronological stream, calibration and all held probes. Three hidden regimes have randomized **64–88** witnessed interventions each. Learners see a chronological raw `(action, consequence)` stream **without episode IDs, regime boundaries, planted factor labels or true weights**. Each query provides **12 labeled calibration interventions** to all arms, without identifying the true regime, then scores 64 withheld action consequences per target regime (A/B/C). **This is calibrated context recognition, not pure zero-shot unlabelled identification.** At held evaluation the nuisance cues are independent; training/calibration cues were correlated or anticorrelated.

The candidate maintains one serialized checkpoint of overlapping historical **OMP4 hypothesis snapshots** learned from windows of 64 stream observations at stride 16. Its fixed structural-consensus rule averages the two lowest calibration-error snapshots only if >=3 supports agree and their calibration errors differ by less than .04; otherwise it selects best. **These are multiple statistical snapshots in one memory store, not a native monolithic causal learner.** The operator dictionary (all 286 pairwise and triple Walsh/parity terms over 12 inputs) was authored and supplied. No unrestricted operator invention occurred.

Fully fitted, same-stream and same-calibration controls: strongest **matched best historical snapshot without consensus**, conventional softmax model averaging over *the same* snapshots, latest snapshot with no retrieval, pooled full-dictionary ElasticNet, recent-window ElasticNet, pooled RBF kernel ridge, random historical snapshot and reversed-label calibration negative. The calibrations and observation budget match; the methods have different representational biases and model capacities.

## Original frozen primary outcome

| Method | A historical held MSE | B historical held MSE | C cold held MSE | A/B/C pooled MSE |
|---|---:|---:|---:|---:|
| softmax_memory | 0.043951 | 0.166991 | 0.134594 | 0.115179 |
| best_snapshot | 0.039357 | 0.267818 | 0.104160 | 0.137112 |
| energy_consensus | 0.039395 | 0.267939 | 0.113846 | 0.140393 |
| pooled_elasticnet | 2.122215 | 2.062858 | 1.821634 | 2.002235 |
| recent_elasticnet | 3.052304 | 2.815814 | 0.301299 | 2.056472 |
| pooled_krr | 2.134976 | 3.460620 | 2.917887 | 2.837828 |
| last_snapshot | 4.142196 | 4.294791 | 0.588045 | 3.008344 |
| random_snapshot | 2.871693 | 2.682085 | 2.865489 | 2.806422 |
| shuffled_probes | 2.647387 | 3.098139 | 2.719830 | 2.821785 |

**Falsification:** Candidate pooled MSE **0.140393** versus strongest conventionally weighted memory **0.115179** (candidate **21.89% MORE error**) and directly matched best snapshot **0.137112** (candidate **2.39% MORE error**). Candidate cold C error **0.113846** versus matched best snapshot **0.104160** (+9.30%). Improved A historical retention over latest-only model is real in this bounded setting, but ordinary memory retrieval explains it; structure-specific consensus does not add value. Across seeds, the candidate beats the strongest conventional pooled control on only **1/3**. Structural consensus triggered **79/108** queries, so this is not a no-op negative.

## Ten frozen gates

| Frozen gate | Result |
|---|---|
| `cold_C_vs_matched_best_5pct` | **FAIL** |
| `overall_vs_matched_best_5pct` | **FAIL** |
| `overall_vs_strongest_other_5pct` | **FAIL** |
| `seed_stability_2of3` | **FAIL** |
| `family_non_degradation_10pct` | **PASS** |
| `old_query_retention_vs_last_20pct` | **PASS** |
| `old_query_noninferiority_5pct` | **PASS** |
| `shuffle_query_negative_20pct` | **PASS** |
| `serializer_refit_audit` | **PASS** |
| `consensus_exercised_10pct` | **PASS** |

**Decision: 6 PASS, 4 FAIL => DEVELOPMENT_NO_GO**. No source, score, gates, thresholds, or primary seeds were retuned. A hypothesis-bank representation can retrieve previously fitted causal response regimes using labeled probes, but this candidate's extra structure-sharing is not justified compared with conventional calibration-based retrieval.

## Engineering, audit, replay and fresh-process restoration

- Original complete scorer receipt `primary.json`, **2,798,682 bytes**, SHA-256 `49787e56866180ae38bf924e6c455fe21d977fb5887739a1116bad8e9cec4f82`. Every 36 world x nine methods x three queries retains every 64-held prediction vector, selected snapshot, gate decision, scores, hidden source for independent checking, and checkpoint. `case_receipts.csv` has 108 context-query rows; all raw originals are included in evidence tar.
- Independent auditor `audit.py` **does not import scorer** and refits every historical OMP and all conventional nonlinear controls. It checked unique causal assignments, label consistency with disclosed hidden mechanism, feature IDs, each query's decisions and held predictions and metric aggregation. **369,674 checks PASS**. Limit: auditor shares third-party NumPy and sklearn numerical solvers, and validates supplied source truth rather than independently regenerating all noise. Not an independent scientific replication.
- Exact-source replay on identical seeds and source: **PASS**; canonical timing-free SHA-256 `99d91e7aa0ae77d0deefaece48fec604a855fde85456e09b24f09ca972dc4dfc`, 2,796,859 bytes. Only elapsed seconds omitted; all scientific predictions, checkpoints and scores byte-identical. The replay is determinism verification, not disjoint scientific replication.
- **Fresh Python-process checkpoint restore PASS**, **6,912 historical held predictions exactly equal** (maximum difference 0.0). Every candidate prediction was recomputed using only the stored JSON memory hypothesis bank plus 12 labeled query outcomes in a new process, without importing scorer. This verifies functional readout restoration, not native Yggdrasil cumulative weights.
- Local fit/run primary elapsed 7.4087s on single-thread CPU (does not include audit, replay, packaging, GitHub CI, or full infrastructure; no electricity measurement). Native Windows/Linux regression and official acceptance are separate and NOT attempted.

## Conclusion

Preserve this prospective **negative mechanism-specific result**. Context-free historical snapshot memory and conventional posterior-weighted retrieval are viable **synthetic baselines**, but neither proves native causal intelligence, unknown-grammar generalization, permanent functional retention in Yggdrasil, or autonomous context discovery without labeled calibration. Future work should test a stronger learned latent-state representation against this best softmax-memory comparator on genuinely unfamiliar mechanisms and match all compute and observation costs. Do not reuse consumed seeds for tuned promotion.
