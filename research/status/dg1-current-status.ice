TITLE: DG-1 Current Research Status
DATE: 2026-09-17
STATUS: ACTIVE — DG-1A P0 OBJECTIVE / OCCUPANCY STABILIZATION
TRACK: DG-1
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; EXPLORATORY FOR SANDBOX RESULTS

PURPOSE
Maintain an operator-readable durable research status ledger. This record summarizes the live DG-1 frontier and points to experiment-specific evidence. It is not an execution authority.

CURRENT OBJECTIVE
Establish a viable canonical DG-1A developmental substrate that can grow a target morphology, remain stable, suffer meaningful damage, and exhibit measurable stable repair before opening DG-1B functional computation.

RESEARCH FOUNDATION
YG-R1 through YG-R8 research records exist.
YG-R8 Pass 1 is closed and reconciled into the DG-1 implementation gate.
Functional-regeneration, structural-plasticity, resource-pressure, and measurement contracts remain adopted for early DG-1 work.

ACTIVE BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
8f9dedecb76c334264232c22c7e459f78055c92e

P0 IMPLEMENTATION STATUS
The bounded P0 substrate, training curricula, recovery/persistence telemetry, resource accounting, resumable training, explicit evidence, and four explicit training-loss modes are implemented:
- global_mse;
- balanced_fg_bg;
- global_plus_foreground;
- global_plus_foreground_bg_alpha.

Latest reconstructed sandbox regression:
69 passed
0 failed
Python 3.13.5 / PyTorch 2.10.0+cpu

The STAB-05 execution source was semantically reconstructed from connected GitHub readbacks of implementation/test revision 8c1acff13ec5d6e43b7520793555dbc9ac849f34. Byte identity with a native checkout was not established. Treat STAB-05 as measured sandbox evidence, not commit-bound confirmatory scientific acceptance.

CURRENT FULL-GRID FINDINGS
STAB-01: NEGATIVE
Fixed maturity-threshold increases did not provide a valid monotonic stabilization mechanism.

STAB-02: NEGATIVE
Longer 64..128 developmental training horizons converged to an all-dead phenotype, exposing sparse-target degeneracy in global unweighted morphology MSE.

STAB-03: NEGATIVE
Equal foreground/background regional weighting avoided death but overcorrected into severe overgrowth and an invalid lesion.

STAB-04: NEGATIVE
GlobalVisibleMSE + ForegroundVisibleMSE also avoided death but produced 1578 / 1600 pre-damage active cells, pre-lesion global MSE 0.1845480204, negative DamageEffect, and invalid regeneration inference.

STAB-05: NEGATIVE WITH DIRECTIONAL MECHANISTIC SIGNAL
Candidate OCC-A1 added a fixed target-background alpha-energy term:

TrainingMorphologyLoss = GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAlphaMSE

Exactly one fresh seed-0 candidate completed the frozen 200-iteration H96/M16 envelope with single-writer resumable checkpoints.

Measured sandbox result:
- minimum recorded training loss: 0.1833379418;
- final recorded training loss: 0.1999244839;
- pre-damage active cells: 1206 / 1600;
- pre-lesion global MSE: 0.0701904967;
- post-lesion global MSE: 0.0557577237;
- DamageEffect: -0.0144327730;
- RelativeDamageEffect: -0.2056228929;
- lesion removed 45.77% of active cells;
- final recovery active cells: 1329 / 1600;
- stable T50/T90 and bounded RecoveryFraction: undefined/not attained;
- persistence active cells: 1140 -> 1378;
- persistence global MSE: 0.0642844662 -> 0.1067116261;
- candidate worth widening: NO.

STAB-05 DIRECTIONAL EFFECT
Relative to STAB-04:
- pre-damage activity reduced 1578 -> 1206, approximately 23.57%;
- pre-lesion global MSE reduced 0.1845480204 -> 0.0701904967, approximately 61.97%.

Therefore explicit occupancy pressure demonstrably changes the learned phenotype in the intended direction, but the tested alpha-energy term is insufficient for canonical P0 stabilization.

CURRENT INTERPRETATION
The immediate P0 failure is now more specifically characterized:
- pure global occupancy-weighted MSE can make sparse-target death competitive;
- strong foreground protection can make excessive structure competitive;
- explicit target-background alpha-energy suppression partially reduces that excess, but continuous alpha energy does not directly enforce thresholded active-cell cardinality or stable support geometry.

The STAB-05 lesion still improved the common global morphology metric, proving substantial harmful/excess structure remained before damage. Persistence also expanded rather than stabilized.

This narrows the next research question to bounded occupancy/support structure rather than generic foreground/background loss balancing.

DURABLE STAB-05 RECORDS
research/experiments/dg1a/dg1a-p0-stab05-spec.ice
research/experiments/dg1a/dg1a-p0-stab05-result.ice
evidence/dg1a/p0_stab05_sandbox.json
research/status/dg1a-p0-status.ice

Full local sandbox evidence SHA-256:
32108c4908e3328188dfe2223b032881bcd8944c73c22f1b41e96e6a7fb79f3c

CURRENT DECISIONS
- STAB-05 is closed negative;
- OCC-A1 is not widened to additional seeds;
- its coefficient is not tuned retroactively;
- the global evaluation metric remains unchanged;
- implemented historical loss modes remain preserved for reproducibility;
- the directional occupancy reduction is retained as mechanistic evidence;
- canonical full-grid P0 remains unresolved;
- DG-1B remains unopened.

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-06 — DESIGN / PREREGISTRATION ONLY.

The next experiment should discriminate the mismatch between continuous alpha-energy pressure and actual bounded active/support structure. Candidate mechanism classes for design review include a differentiable occupancy/cardinality surrogate or target-support geometry control.

No STAB-06 mechanism is selected by this status ledger.
No STAB-06 scientific execution is authorized until one mechanism, one fixed parameterization, the common evaluation metric, frozen envelope, and complete gates are preregistered in .ice.

FIBONACCI TRACK
DG-1A-FIB1 remains preserved and separate.
Do not introduce Fibonacci repair budgets, capacity ceilings, topology priors, or module-size schedules into canonical P0 while basic viability/stability remains unresolved.

LARGER DG-1 TRAJECTORY
stable local development
-> functional computation
-> specialization
-> functional regeneration
-> continual development
-> developmental neural modules
-> frozen intelligent seed
-> developmental adapters
-> ancestor inheritance
-> resource-constrained organism
-> regenerable capability

ANCESTOR INHERITANCE
Remains a first-class future direction. It is not opened by STAB-05.

BOUNDARIES
Do not modify Wingless, ckb-plane, or Mind-Palace without explicit authorization.
Do not activate CKB runtime, Coinbase/live broker systems, TradeGuard, deployment/promotion, or external execution authority.
P0 remains morphology/developmental-substrate research and does not establish cognition or general intelligence.

NEXT ACTION
Design and preregister STAB-06. Do not execute it until its exact single factor and gates exist in .ice. Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling until canonical P0 viability/stability is adequately characterized.
