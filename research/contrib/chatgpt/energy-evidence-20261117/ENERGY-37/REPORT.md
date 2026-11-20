# ENERGY-37 — One-pass causal-energy witness selection

**Date:** 2026-11-18. **Result:** DEVELOPMENT_NO_GO (3 of 7 frozen gates pass). **Engineering:** local primary, independent refit and semantic replay PASS; native cross-platform regression NOT RUN. **Scientific qualification:** NO-GO. **Deployment:** NONE.

## Objective
ENERGY-36 showed that a costly six-model energy disagreement committee could select somewhat more useful interventions but was far slower than conventional methods. ENERGY-37 tests a different bounded mechanism: **one single contrastive-energy gradient for choosing interventions**, with no bootstrap or iterative fitting in the selection stage. After the selected intervention consequences are actually witnessed, the final downstream energy learner is still fully fitted over 48 epochs; it is not a one-pass end-to-end learner.

All policies start with 80 identical observed familiar-context x0=0 action consequences. They choose exactly 16 actions from the same 80 x0=1 intervention candidates before observing those actions' consequences, then train on 96 acquired outcomes per policy. They predict 16 disjoint old-context and 48 disjoint unfamiliar-context actions per world. The source is an explicit finite 190-feature parity/AND2 grammar with 10% corruption on observed labels; it is not open-world concept invention or original/native Yggdrasil training. The source and seven gates were preregistered before any primary scoring.

## Frozen custody
- Prior ENERGY-36 archive baseline: 966456fd95fbdafa77f2192e49ab565238134597.
- Frozen source + independent auditor commit: aebfc1a36074c2591c6569c455edf79f775aa93c.
- Preregistration committed before primary: 62efe126e65110917838e332b3e6b20a29a6e90d.
- Experiment original source SHA-256: e84d68cb79aa0cf5f58d72813a9eb5a400ec767384a4807cf411e69bb7773173 (decompress experiment.py.bz2).
- Auditor original source SHA-256: bf982045b4acef4a4730d39866dc5b11ebeab2379eca5329be5aefc36bf348b6 (decompress audit.py.bz2).
- Smoke-only seed 99107 excluded from primary: 3 worlds, 339 source-independent audit checks PASS.
- Primary seeds 7703, 7723, 7753; 8 worlds per seed; 3 causal families: 72 distinct source worlds; 7 selectors × 5 fully retrained downstream learners = 35 selector/learner pairs.
- All seven selector policies and their random/bootstrap draw rules are fixed in the committed source; no primary-score threshold, seed, capacity or model tuning.

## Primary results

| Intervention selector | Final energy shifted held correct / 3,456 | Old held correct / 1,152 | Local selector + final energy component time across worlds |
|---|---:|---:|---:|
| Six-model energy committee | **2,899 (83.88%)** | 1,090 | 1.7487 s |
| **One-pass energy** | **2,887 (83.54%)** | 1,082 | 0.9144 s |
| Fixed first sixteen | 2,863 (82.84%) | 1,095 | 0.1591 s |
| Random sixteen | 2,857 (82.67%) | 1,090 | 0.1602 s |
| Conventional OMP fitted uncertainty | 2,856 (82.64%) | 1,071 | 0.9543 s |
| Six-model conventional OMP committee | 2,846 (82.35%) | 1,093 | 1.2587 s |
| Single-model iterative energy uncertainty | 2,769 (80.12%) | 1,079 | 1.0329 s |

The strongest alternative among all 34 other fully fitted selection+learner combinations is six-model energy committee+energy, 2,899/3,456. One-pass gets **12 fewer correct** (−0.35 percentage points), failing the frozen requirement of at least +3 percentage points versus the strongest.

One-pass beats iterative single-energy uncertainty by 118/3,456 (+3.41 percentage points), passing the +1pp ablation gate. Versus conventional fitted OMP uncertainty feeding the same final energy learner, it gains 31/3,456 (+0.90pp), failing the frozen +1pp comparator.

Old-context retention loses 13/1,152 against fixed first16+energy (1082 vs 1095; −1.13pp), failing the maximum one-point retention regression. Per-seed margins versus the strongest alternative complete arm are **−81, +11, +8**, meeting the weak positive-in-2-of-3 gate but showing a pronounced negative seed. A matched label-shuffled energy negative gives 1,850/3,456 correct, much less than 2,887/3,456 for real witnessed labels.

## Efficiency and frozen gates

One-pass selector+final energy took **0.9144 s** cumulative fit-and-predict component time across all 72 worlds. The committee+energy took 1.7487 s (1.91× longer). However, random selection+fully fitted conventional OMP12 took only **0.07038 s**, approximately **13× less** than one-pass+energy. One-pass does **not** meet the frozen limit of <=1.5× conventional policy cost. A whole local experimental primary run, evaluating all seven policies and all five learner variants, was 10.8092 s. These Python component measurements are not evidence of end-to-end scientific or native-system speedup.

**PASS (3/7):** one-pass better than iterative energy uncertainty, positive margin on two of three source seeds, real labels outperform shuffled negative. **FAIL (4/7):** versus strongest complete arm, versus conventional OMP uncertainty by at least 1pp, old held retention, and component compute cost. The original DEVELOPMENT_NO_GO classification is retained without tuning.

## Engineering evidence and audit
- Original complete local primary scored.json: **752,383 bytes**, SHA-256 **c0df97bf0b697e0ffc04dc1d492c9007ab004289c7fa2ee6a7fa386e2c374e9f**.
- Deterministic semantic replay PASS on a separate exact-source run: canonical non-timing JSON **174,857 bytes**, SHA-256 **222e7680dadd6f9a76176664358cd81dbdbf08e0bfa6fac8967713e9112eac70**; replay matched all non-timing fields byte-for-byte.
- Independent audit PASS: **7,860 checks**. Separately implemented synthetic source generator, noise, selected interventions, all 35 independently refitted learner arms, held-old/new predictions, shuffled negatives, aggregates and frozen decisions. The conventional arms reuse the same third-party sklearn algorithms and this is not a separate implementation of sklearn. Original local audit-result JSON SHA-256: **28b74fe62e8bc8d1d3797cc6dc3ff42de2ec3251e3072b188ca8a0ad27d40bc2**.
- **All 504 source-world×selector primary case receipts are on GitHub** in case_receipts.csv (50,334 bytes; blob 0a6caaf890615274cfa68c968b05d3f9f0cbcb6b; SHA-256 583854c0182d8ebf49f8ef8438acdf6b9c9725a3d3fd02305f3f08418e38f925). Each receipt contains seed/world/family, exact 16 selected candidate actions (32-character hex), the sixteen observed outcome signs as a 16-bit hex word, five fitted learners' old/new held scores and shuffled-label negative. The committed independent auditor and frozen scorer can recompute these on the exact primary cohort.
- The original full timing-bearing scored JSON and full canonical semantic JSON were retained locally and their hashes recorded, but **the full original JSONs are not deposited** in this GitHub record. The published case receipts preserve all original per-policy selection and scoring outcomes but omit per-case timers.
- Runtime: local Linux CPU, Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0, single-threaded BLAS. Mandatory native Yggdrasil Linux/Windows regression, scientific first-use and independent acceptance NOT RUN. The archive PR has a pre-existing G29 generated-code-atlas CI index failure; CI engineering status must not be confused with science.

## Exact reproduction
Checkout the pinned evidence commit and enter the ENERGY-37 directory. First decompress experiment.py.bz2 and audit.py.bz2 to the corresponding .py files; verify their uncompressed SHA-256 values above. Then run the frozen scorer once and the independent auditor:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out scored_replay.json
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py scored_replay.json --out audit_replay.json

Check against the aggregate result.json and all 504 CSV receipts. Full timing-bearing JSON hashes vary between runs; canonical comparison must omit only total_wall_seconds, cost_seconds and per-case acquisition_seconds/final_fit_seconds.

## Decision
**Stop this one-pass selector on the consumed seeds.** It nearly matches a costlier committee on this known small synthetic grammar, but fails the strongest-control margin, stationary retention and cost gates. No demonstrated native Yggdrasil reasoning/learning or end-to-end efficiency benefit.

A distinct subsequent research hypothesis, if funded, should target minimizing **whole-process compute per independently verified causal relationship** rather than spending further seeds on energy-selector gradient tweaks. Fresh independent source mechanisms and a fully optimized conventional active-learning baseline are required. No accepted-ref, main, controller, research-loop, native model, runner, deployment or scientific state changed.
