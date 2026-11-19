# ENERGY-50 — Out-of-grammar causal-intervention acquisition screen

**Date:** 2026-11-18. **Decision: DEVELOPMENT_SCREEN_NO_GO.** Exploratory excluded-seed evaluation; **36-world primary seeds 9209, 9221, 9241 NOT CONSUMED**. The exact-source smoke and source-free independent audit are preserved, not interpreted as prospective SCIENTIFIC_PASS.

## Research question

ENERGY-49 showed a provisional benefit for Hamming-distance diversity on an authored 364-term parity-through-order-three and pairwise-AND grammar. Is diversity still valuable when **hidden causal mechanisms cannot be represented exactly by that grammar**?

## Independent synthetic novelty

A new source stream `E50:v1` selects 5 hidden signed factors from three unfamiliar families: 4- or 5-bit parity; nonlinear four/five-bit majority/threshold and modulo-three functions; and conditional five-bit gated mechanisms. Three shared factors coexist with one old-only and one new-only factor (for the 3/4 changed source cases). A separate independent auditor proved each planted factor has at least one **nonzero Fourier-Walsh term of order >=4**, hence not representable as a *linear combination* of the old <=3 parity and AND2 factors. A richer nonlinear model may still approximate or represent them; this result is a narrowly specified grammar counterexample, not arbitrary new operator invention.

All action contexts are disjoint in their **underlying 10-bit causal action assignment**: exactly 720 different assignments per world (96 witnessed old +48 initial witnessed new +192 candidate pool +128 old-held +128 new-held +128 cold-held). The two extra observed bits are nuisance cues whose correlations change; cold nuisance bits are independent. Outcomes contain hidden shared/stage-specific nonlinear factors plus independent N(0,0.3) observation noise. Ground-truth factor identifiers and all held outcomes are excluded from selector and learner inputs.

All seven intervention selectors (Hamming diversity, uninformed random, fixed order, four-member kernel-ridge committee, old/new kernel-ridge disagreement, pair-value coverage and shuffled-outcome committee) see exactly the same 192 unlabeled candidate actions and the 96 old +48 new witnessed labels. Each selects 24 *before* its outcomes become available. Each of three downstream models (RBF KernelRidge, ExtraTrees 64 trees, and legacy ElasticNet over the known grammar) trains on the same **168** witnessed outcomes. All 21 policy × model combinations are fully fitted and held predictions include 128 old/new/cold actions per world.

## Two independently excluded six-world screens

| Screen seed | Hamming diversity + RBF kernel-ridge cold MSE (lower better) | Random + same kernel-ridge cold MSE | Relative improvement | Fixed nine Boolean checks true | Independently audited items |
|---|---:|---:|---:|---:|---:|
| 99941 | 3.712661 | 3.709348 | -0.09% | 4/9 | 943 |
| 99947 | 3.521150 | 3.530811 | +0.27% | 3/9 | 943 |

**Important:** One of the nine Boolean checks is the prespecified **two-of-three seed stability** rule. Each smoke cohort contains only one seed; that check was automatically false because it is **not evaluable**, so the appropriate screen interpretation is 4/8 and 3/8 *evaluable* checks satisfied, **not** a scientific nine-gate primary failure. The full scorer outputs, including the not-evaluable false gate, remain preserved.

The primary candidate did not approach the 10% gain over random required for advancement: differences were -0.09% and +0.27% respectively. Both kernels and trees struggled to recover the new nonlinear causal functions under 168 observations, so an intervention-coverage improvement cannot compensate for model-class and sample limitations. Previous ENERGY-49 errors of ~0.15 are **not directly comparable** to these new OOD errors of ~3.5 because the generators, label functions and variance differ.

## Engineering custody and qualification

- Independent auditor imports no candidate scorer or source code; regenerates all 12 hidden worlds and their unique intervention/cold-outcome streams, checks all **7 × 12 =84** acquisition choices, refits **21 ×12 = 252** models, checks **3 ×128** held predictions per model using SHA-256 digests and reaggregates each model MSE. **1,886 checks PASS** across two screens. Scikit-learn and NumPy implementation libraries are shared (not separate ML engine qualification).
- Exact-source replay on screen seed 99941: semantic byte identity excluding observed elapsed seconds, SHA-256 `8317e054b1faabdd7748a10547e6ce2a3ae81365e5188311f49f6c9e525d3b14` PASS.
- Frozen scorer original SHA-256 `49c8b13643c725ba48a91300c1e18225f1a30b3a168fcfe248208263cd9d6f5d`; independent audit original SHA-256 `14b812aa2e1c1274c9f5c4408edbbf35d71e02b9974d12455d23a4d204c5c80b`.
- These are exploratory *pre-primary* screens, **not prospectively preregistered confirmatory trials**; the code and results are being archived **after the exploratory screens**, clearly labeled rather than falsifying preregistration timestamps. Primary seeds remain wholly unscored.

## Classification and research decision

**DEVELOPMENT_SCREEN_NO_GO.** Do not tune against these screen seeds, do not consume the 36 reserve worlds for this candidate. The ENERGY-49 in-grammar provisional GO is **not independently replicated outside the original factor class**. Candidate acquisition is not a native Yggdrasil mechanism, no SCIENTIFIC_PASS, no native tokenless model learning, no authorized first-use, accepted checkpoint, controller/runner/queue/scheduler action, merge, or deployment.

**Next falsifiable problem:** first qualify an expressive learner capable of learning new higher-order interactions from interventions, against suitably trained kernel/tree/neural conventional baselines, *then* test whether selective intervention policies have additional value. The intervention-selecting heuristic cannot be fairly credited with repairing a representation bottleneck.

## Reproduce read-only

The self-contained `ENERGY-50-EVIDENCE.tar.bz2` contains frozen Python source, both complete original smoke records, two independent audits, exact-source replay, frozen summary, manifest and verifier. With Python 3.13.5, NumPy 2.3.5 and sklearn 1.8.0 and single-threaded BLAS, unpack into a clean directory and run:

```bash
python verify_archive.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python experiment.py --mode smoke --out replay_smoke.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python audit.py replay_smoke.json --out replay_audit.json
```

**ENGINEERING:** independent local audit/replay PASS; GitHub CI must be evaluated separately. **SCIENTIFIC:** SCREEN_NO_GO, primary untouched. **DEPLOYMENT:** NONE. No accepted Yggdrasil repo state modified.
