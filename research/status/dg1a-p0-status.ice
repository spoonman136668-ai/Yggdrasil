TITLE: DG-1A-P0 Current Status
DATE: 2026-09-17
STATUS: ACTIVE — STAB-05 CLOSED NEGATIVE / STAB-06 DESIGN NOT YET PREREGISTERED
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; EXPLORATORY FOR SANDBOX RESULTS

BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
7900839162a59d79bd68db323ddb55691194d5ea

CURRENT PURPOSE
Establish a trustworthy canonical developmental NCA control with bounded growth, persistence, meaningful damage, and stable regeneration before DG-1B functional computation or later Yggdrasil mechanisms are opened.

IMPLEMENTED SURFACE
- fixed-grid shared-rule NCA substrate;
- deterministic seed and repository-native target generation;
- state-pool persistence/regeneration curricula;
- maturity-gated training damage;
- independent training/evaluation lesion geometry;
- global and stable recovery metrics;
- persistence telemetry;
- resource accounting;
- resumable deterministic training sessions;
- machine-readable evidence writer and runner;
- explicit global_mse, balanced_fg_bg, global_plus_foreground, and global_plus_foreground_bg_alpha training loss modes;
- foreground/background balanced morphology helper;
- target-foreground morphology helper;
- target-background alpha occupancy helper;
- fail-closed empty-foreground/background behavior;
- fail-closed config validation.

LATEST TEST STATUS
STAB-05 reconstructed sandbox regression:
69 passed
0 failed
Environment: Python 3.13.5 / PyTorch 2.10.0+cpu

The sandbox source was semantically reconstructed from connected GitHub readbacks of implementation/test revision:
8c1acff13ec5d6e43b7520793555dbc9ac849f34

This was not a native byte-identical checkout. Treat the tests and scientific result as sandbox evidence, not commit-bound confirmatory acceptance.

SCIENTIFIC / EXPERIMENTAL FRONTIER
Small-grid P0 work previously established exploratory regeneration signals, but confirmatory support remains blocked by commit-bound provenance requirements.

Full-grid 40 x 40 canonical stabilization remains unresolved.

STAB-01 — CLOSED NEGATIVE
Fixed maturity-threshold increases did not provide a valid monotonic stabilization mechanism.

STAB-02 — CLOSED NEGATIVE
Longer 64..128 developmental training horizons converged to an all-dead phenotype, exposing sparse-target degeneracy in global unweighted morphology MSE.

STAB-03 — CLOSED NEGATIVE
Balanced foreground/background pressure avoided death but produced an overgrown poor-morphology phenotype with an invalid lesion.

STAB-04 — CLOSED NEGATIVE
GlobalVisibleMSE + ForegroundVisibleMSE also avoided death but produced severe overgrowth:
- pre-damage active cells: 1578 / 1600;
- pre-lesion global MSE: 0.1845480204;
- DamageEffect: -0.0661034361;
- final active cells: 1073 / 1600;
- candidate worth widening: NO.

STAB-05 — CLOSED NEGATIVE
Candidate: OCC-A1
TrainingMorphologyLoss = GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAlphaMSE

BackgroundAlphaMSE penalized state alpha squared only on target-background pixels, with fixed coefficient 1.0.

Exactly one fresh seed-0 candidate completed 200 / 200 iterations through a single-writer resumable checkpoint path.

Measured sandbox result:
- initial recorded loss: 0.4459555447;
- minimum recorded loss: 0.1833379418;
- final recorded loss: 0.1999244839;
- pre-damage active cells: 1206 / 1600;
- pre-lesion global MSE: 0.0701904967;
- post-lesion global MSE: 0.0557577237;
- DamageEffect: -0.0144327730;
- RelativeDamageEffect: -0.2056228929;
- active-cell removal: 45.77%;
- final active cells: 1329 / 1600;
- stable T50/T90: not attained / undefined;
- bounded RecoveryFraction: undefined;
- improvement rule: FAIL;
- candidate worth widening: NO.

STAB-05 PERSISTENCE
- initial active cells: 1140;
- final active cells: 1378;
- active-cell drift: +238;
- initial global MSE: 0.0642844662;
- final global MSE: 0.1067116261.

STAB-05 FAILURE MODE
PARTIALLY SUPPRESSED BUT STILL OVERGROWN / POOR-MORPHOLOGY PHENOTYPE WITH INVALID LESION.

The occupancy intervention had a real directional effect relative to STAB-04:
- pre-damage activity fell 1578 -> 1206, approximately 23.57%;
- pre-lesion global MSE fell 0.1845480204 -> 0.0701904967, approximately 61.97%.

However, the absolute preregistered gates still failed:
- pre-damage active cells remained above 800;
- pre-lesion global MSE remained above 0.0361635;
- lesioning improved morphology rather than degrading it;
- final recovery activity expanded to 1329;
- persistence activity expanded to 1378 while error worsened.

CURRENT OBJECTIVE DIAGNOSIS
The P0 objective problem is no longer an undifferentiated foreground/background weighting problem.

Evidence now supports three narrower observations:
1. global occupancy-weighted MSE can make sparse-target death competitive;
2. strong foreground protection can make excessive active structure competitive;
3. explicit target-background alpha-energy suppression partially counteracts overgrowth, but continuous alpha energy alone does not enforce bounded thresholded active-cell cardinality or stable support geometry.

This makes occupancy/support structure a live mechanism class for the next discriminating experiment without establishing which specific mechanism should be used.

DURABLE STAB-05 RECORDS
research/experiments/dg1a/dg1a-p0-stab05-spec.ice
research/experiments/dg1a/dg1a-p0-stab05-result.ice
evidence/dg1a/p0_stab05_sandbox.json

Full local sandbox evidence SHA-256:
32108c4908e3328188dfe2223b032881bcd8944c73c22f1b41e96e6a7fb79f3c

CURRENT DECISIONS
- close STAB-05 as negative;
- do not widen OCC-A1 to additional seeds;
- do not tune its background-alpha coefficient inside STAB-05;
- do not change its foreground coefficient inside STAB-05;
- preserve global morphology MSE as the common evaluation metric;
- preserve all four implemented historical loss modes for reproducibility;
- do not reopen STAB-01 through STAB-05 with post-result parameter/threshold inserts;
- retain the STAB-05 directional occupancy improvement as first-class mechanistic knowledge;
- do not begin DG-1B yet;
- do not introduce Fibonacci scheduling into canonical P0 yet;
- retain Fibonacci as the separate DG-1A-FIB1 follow-on ablation.

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-06, DESIGN / PREREGISTRATION ONLY.

STAB-06 should discriminate the remaining mismatch between continuous alpha-energy pressure and bounded active/support structure.

Plausible mechanism classes for consideration include:
- a differentiable occupancy/cardinality surrogate;
- a target-support geometry penalty.

NO STAB-06 mechanism is selected by this status record.

Before execution, STAB-06 must preregister one explicit mechanism, one fixed parameterization, unchanged global evaluation metric, a frozen experimental envelope, and explicit viability, occupancy, lesion-validity, morphology, recovery, persistence, and finite-state gates.

Do not convert STAB-06 into a coefficient sweep of STAB-05.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
No claim of cognition, functional specialization, continual learning, ancestor inheritance, structural growth, or general intelligence is authorized.

NEXT ACTION
Design and preregister STAB-06. Do not execute it until its exact single factor and gates exist in .ice. Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling.
