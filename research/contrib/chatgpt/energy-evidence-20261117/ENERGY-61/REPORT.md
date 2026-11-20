# ENERGY-61 — Compositional causal operator induction and functional historical retention

**Classification: SCREEN_NO_GO (6/10 frozen gates PASS).** Date 2026-11-19. External synthetic evidence only. No native Yggdrasil training, SCIENTIFIC_PASS, accepted-ref change, merge or deployment.

## Prospective custody

Prior draft PR #1210 archive HEAD: `327d44d0038ac9600fb600ff7e92101b61ddb841`. Frozen scorer and independently authored auditor committed **before scoring** at `378a5445b59fbc46290c91f12c930ea2b1858555`; a separate GitHub preregistration froze all ten gates and prospective seeds at `83111478f22479062b1758a763e59885d567cc7c`. GitHub readback verified the original source blob, hash and prereg at HEAD before scoring any 103301/103319 data. Original source tar SHA256 `e6bf6e1e52aaf654fc5fb477431c094ac3c9da87317e944fa2f2fb801a0a0afa`. Original independent auditor SHA256 `a91e63928f3662539bde664b0c9a27a5d475818f37454d357d21cd972e123151`.

Excluded development smoke `999001` (3 worlds; 21,603 independently audited checks) was evaluated before freeze. A matching-bank ElasticNet control was added and old-readout preservation fixed **before freezing source**, with the smoke disclosed. Excluded smoke is exploratory only. The prospective 12 worlds are two new, previously untouched seeds `103301` and `103319` × two source IDs × three causal families. Reserved 36-world primary seeds **103401, 103419, 103433 NOT CONSUMED** because this screen failed the frozen stop criteria.

## Mechanism and information/capacity comparisons

Each world has **352 different randomized 10-bit causal intervention assignments** split 80 OLD training, 80 NEW training, and 64 OLD/NEW/COLD held interventions. Two observed nuisance bits change correlation OLD/NEW and become independent in COLD. The hidden generator plants one shared high-order Boolean relationship and a changed second relationship, across `xor_and`, `and_xor`, and 5-variable `conditional` families; Gaussian noise σ=.18. Learners do not get planted supports, named high-order factor labels or hidden held consequences.

Candidate: search generic binary AND/XOR primitives of observed inputs and AND/XOR composition of two disjoint pairs, **12,012 researcher-authored expressions**. Fit four OLD sparse terms, preserve OLD predictions, reuse two OLD selected expressions and induce two new expressions using NEW consequences. **The generic primitive operations, maximum depth and search strategy are supplied; this is not unrestricted autonomous invention of causal operators.** The conditional five-variable mechanisms are outside the depth-two expressivity limit.

Strong controls receive exactly the same 80 OLD +80 NEW witnessed intervention outcomes, and include same-library four-term fresh OMP and pooled OMP, **fully fitted same-library ElasticNet on the identical 12,012 expressions**, conventional fourth-degree polynomial ElasticNet, ExtraTrees, HistGradientBoosting, RBF KernelRidge, conventional training-loss-weighted softmax memory of same OLD/FRESH OMP snapshots, frozen old no-update and shuffled NEW labels. Some fully fitted controls use NEW-only observations by design. Capacities/computational costs differ, so observation parity is not equal-compute parity.

## Frozen prospective scores (MSE; lower better)

| Method | OLD held MSE | NEW held MSE | COLD held MSE |
|---|---:|---:|---:|
| program_memory | 1.587137 | 0.731302 | 0.663030 |
| fresh_full_bank_omp | 0.846002 | 0.745675 | 0.752324 |
| pooled_full_bank_omp | 1.135194 | 0.800839 | 1.054848 |
| fresh_poly_elasticnet | 1.483442 | 1.082831 | 1.413696 |
| fresh_composition_elasticnet | 0.762953 | 0.540792 | 0.593623 |
| fresh_extra_trees | 3.183300 | 2.849805 | 3.094638 |
| fresh_hgb | 1.904079 | 1.561286 | 1.788330 |
| fresh_rbf_krr | 2.328490 | 2.215975 | 2.322269 |
| softmax_old_fresh | 0.845293 | 0.745479 | 0.751624 |
| old_no_update | 1.587137 | 1.842000 | 1.722692 |
| shuffled_new | 5.249412 | 4.991907 | 4.977893 |

**Candidate cold 0.663030 versus strongest matched same-library ElasticNet 0.593623: 11.69% MORE error.** Candidate improved over fresh OMP and conventional softmax retrieval, but those wins do not override the strongest same-bank conventional learner. Old-checkpoint predictions were retained exactly; conditional operator transfer was the failure point.

### Per fresh seed

| Seed | Candidate cold | Same-bank ElasticNet cold | Fresh OMP cold |
|---|---:|---:|---:|
| 103301 | 0.650439 | 0.583604 | 0.801002 |
| 103319 | 0.675620 | 0.603643 | 0.703647 |

### Per mechanism family

| Family | Candidate cold | Same-bank ElasticNet cold |
|---|---:|---:|
| xor_and | 0.034252 | 0.080100 |
| and_xor | 0.031054 | 0.089757 |
| conditional | 1.923784 | 1.611013 |

## Ten frozen gates

| Gate | Result |
|---|---|
| `cold_best` | FAIL |
| `cold_same_bank_elasticnet` | FAIL |
| `cold_same_bank_omp` | PASS |
| `cold_softmax` | PASS |
| `seed_both` | FAIL |
| `family_at_most_10pct_worse` | FAIL |
| `cold_new_ratio` | PASS |
| `old_exact` | PASS |
| `shuffled_negative` | PASS |
| `pooled_omp_gain` | PASS |

**Verdict: SCREEN_NO_GO.** Critical direct conventional superiority fails and both seed cohorts lose to the strongest conventional baseline. No threshold, source, architecture or primary seeds were changed after seeing prospective outcomes; do not tune these consumed cohorts for confirmation.

## Engineering audit and limitations

- Independent generator reconstruction and independent model refitting without importing scorer: **PASS, 86,313 checks** across all 12 worlds, 11 complete model fits and every OLD/NEW/COLD predicted outcome, observed/held source labels and unique intervention ID; code shares third-party NumPy/sklearn solvers and generic interpretation, not independent scientific authorship.
- Unchanged frozen-source deterministic replay: **PASS**, original and replay semantic SHA256 `2b3e72ea85f69432581b0cfbb70a0a8ddfb93726462eac1fcbaa845a796fa1ce` across 772,295 bytes, excluding only CPU timing fields. Replay independently audited **86,313 checks**; replay is not a new dataset.
- Original scorer result SHA256 `1525e94f76329aa95e0571c48a994bf2350d15325812ae778cb2a089f0a89c74`; original full prediction-by-world receipts and all strong/sham controls preserved in `EVIDENCE.tar.bz2` with independent audit and excluded dev smoke. `case_receipts.csv` preserves every world, source key and selected expression ID.
- Local screen scorer elapsed 3.010 seconds single-thread CPU, excluding audit/replay/custody and physical energy measurement. See `provenance.json` and exact `source_manifest.json`.
- Causal operator classes and primitive AST algebra are researcher-generated; no native Yggdrasil weight learning, unknown-world unrestricted generalization, action autonomy, cold checkpoint restore, production readiness or physical low-energy claim follows.

## Decision

Reject this **OLD-anchor compositional sparse-program update mechanism** for promotion. The matching-bank ElasticNet is the new strongest conventional comparator on these synthetic families. The failure on 5-variable conditional composition suggests future tests need a more expressive, independently qualified representation *and* fair same-library conventional controls, not more acquisition tricks. Keep the negative result in existing draft PR #1210, do not merge or modify Yggdrasil's owned runtime, and leave the 36 reserved primary worlds untouched.
