TITLE: DG-1A-P0 Current Status
DATE: 2026-09-17
STATUS: ACTIVE — STAB-06 CLOSED NEGATIVE / STAB-07 DESIGN NOT YET PREREGISTERED
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; EXPLORATORY FOR SANDBOX RESULTS

BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
a573e71d81c93794fa90a2f83f5303ea33d90d36

CURRENT PURPOSE
Establish a trustworthy canonical developmental NCA control with meaningful viable growth, bounded support, persistence, meaningful damage, and stable regeneration before DG-1B functional computation or later Yggdrasil mechanisms are opened.

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
- explicit global_mse training mode;
- explicit balanced_fg_bg training mode;
- explicit global_plus_foreground training mode;
- explicit global_plus_foreground_bg_alpha training mode;
- explicit global_plus_foreground_bg_alive_margin training mode;
- target-foreground morphology helper;
- target-background alpha-energy helper;
- target-background threshold-aligned alive-margin helper;
- fail-closed foreground/background and margin validation;
- fail-closed config validation.

LATEST TEST STATUS
STAB-06 reconstructed sandbox regression:
79 passed
0 failed
Environment: Python 3.13.5 / PyTorch 2.10.0+cpu

The sandbox source was semantically reconstructed from connected GitHub readbacks of implementation/test revision:
6e8d79b0fd47b7031b05f03b395bf49c1649f00e

This was not a native byte-identical checkout. Treat the tests and scientific result as sandbox evidence, not commit-bound confirmatory acceptance.

SCIENTIFIC / EXPERIMENTAL FRONTIER
Full-grid 40 x 40 canonical stabilization remains unresolved.

STAB-01 — CLOSED NEGATIVE
Fixed maturity-threshold increases did not provide a valid monotonic stabilization mechanism.

STAB-02 — CLOSED NEGATIVE
Longer 64..128 developmental training horizons converged to an all-dead phenotype, exposing sparse-target degeneracy in global unweighted morphology MSE.

STAB-03 — CLOSED NEGATIVE
Balanced foreground/background pressure avoided death but produced an overgrown poor-morphology phenotype with an invalid lesion.

STAB-04 — CLOSED NEGATIVE
GlobalVisibleMSE + ForegroundVisibleMSE produced severe overgrowth:
- pre-damage active cells: 1578 / 1600;
- pre-lesion global MSE: 0.1845480204;
- DamageEffect: -0.0661034361;
- final active cells: 1073 / 1600.

STAB-05 — CLOSED NEGATIVE WITH DIRECTIONAL OCCUPANCY SIGNAL
OCC-A1 added BackgroundAlphaMSE on target-background pixels.
Measured seed-0 sandbox result:
- pre-damage active cells: 1206 / 1600;
- pre-lesion global MSE: 0.0701904967;
- DamageEffect: -0.0144327730;
- RelativeDamageEffect: -0.2056228929;
- final recovery active cells: 1329 / 1600;
- persistence active cells: 1140 -> 1378;
- candidate worth widening: NO.

Relative to STAB-04, STAB-05 reduced pre-damage activity by approximately 23.57% and pre-lesion global MSE by approximately 61.97%, demonstrating that occupancy-specific pressure was mechanistically relevant but insufficient.

STAB-06 — CLOSED NEGATIVE
Candidate: AM-05

BackgroundAliveMarginLoss = mean((ReLU(alpha - 0.05) / 0.05)^2 over target-background pixels)

TrainingMorphologyLoss = GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAliveMarginLoss

Exactly one fresh seed-0 candidate completed 200 / 200 iterations through a single-writer resumable checkpoint path.

Measured sandbox result:
- minimum recorded loss: 0.3612360060;
- final recorded loss: 0.3881474733;
- pre-damage active cells: 3 / 1600;
- pre-lesion global MSE: 0.0283585768;
- post-lesion global MSE: 0.0285354797;
- DamageEffect: 0.0001769029;
- RelativeDamageEffect: 0.0062380726;
- active-cell removal: 33.33%;
- final recovery active cells: 0 / 1600;
- bounded RecoveryFraction: 0.0;
- stable T50/T90: not attained;
- normalized recovery AUC: 0.0036180955;
- persistence active cells: 2 -> 5;
- persistence global MSE: 0.0283863526 -> 0.0271319859;
- candidate worth widening: NO.

STAB-06 FAILURE MODE
OVER-SUPPRESSED / NEAR-DEAD PHENOTYPE WITH INSUFFICIENT LESION EFFECT AND ZERO REGENERATION.

The apparently acceptable pre-lesion global MSE does not represent a viable morphology: only three cells were active. Recovery reached zero active cells and final error converged to approximately 0.0295742, the known near-all-zero sparse-target regime.

The lesion technically increased global error but RelativeDamageEffect was only approximately 0.00624, far below the preregistered 0.10 requirement. Therefore the damage event was not meaningful enough for regeneration inference.

Persistence numerical gates passed only on an almost-dead phenotype and are not evidence of viable morphology stability.

CURRENT OBJECTIVE DIAGNOSIS
The canonical P0 search is now experimentally bracketed between two opposite failure regimes:

1. global sparse-target morphology pressure can make death competitive;
2. strong foreground protection can preserve viability while permitting severe overgrowth;
3. continuous background alpha-energy pressure partially suppresses overgrowth but remains insufficient;
4. the tested threshold-aligned alive-margin pressure suppresses occupancy strongly enough to reopen near-death.

The immediate research problem is therefore not simply more or less occupancy regularization. The next mechanism must preserve meaningful foreground/support viability while bounding excess occupancy and maintaining a meaningful lesion/recovery signal.

DURABLE STAB-06 RECORDS
research/experiments/dg1a/dg1a-p0-stab06-spec.ice
research/experiments/dg1a/dg1a-p0-stab06-result.ice
evidence/dg1a/p0_stab06_sandbox.json

Full local sandbox evidence SHA-256:
ba29d40ae653d61a6bee97668e402158d4f42f235502b3925280a1136cf6bf59

CURRENT DECISIONS
- close STAB-06 as negative;
- do not widen AM-05 to additional seeds;
- do not tune its coefficient, margin floor, margin width, or alive threshold inside STAB-06;
- do not weaken the preregistered gates;
- preserve global morphology MSE as the common evaluation metric alongside viability telemetry;
- preserve all five implemented historical loss modes for reproducibility;
- retain STAB-05's partial occupancy suppression and STAB-06's near-dead collapse as first-class mechanistic evidence;
- do not reopen STAB-01 through STAB-06 with post-result parameter or threshold inserts;
- do not begin DG-1B yet;
- do not introduce Fibonacci scheduling into canonical P0 yet;
- retain Fibonacci as the separate DG-1A-FIB1 follow-on ablation.

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-07, DESIGN / PREREGISTRATION ONLY.

STAB-07 should target the demonstrated need to couple bounded support with meaningful foreground viability rather than becoming a coefficient/margin sweep of STAB-06.

Plausible mechanism classes for design review include:
- a coupled viability/occupancy constraint;
- a target-support geometry objective.

NO STAB-07 mechanism is selected by this status record.

Before execution, STAB-07 must preregister one explicit mechanism, one fixed parameterization, the unchanged common evaluation metric, a frozen experimental envelope, and explicit viability, occupancy, lesion-validity, morphology, recovery, persistence, and finite-state gates.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
No claim of cognition, functional specialization, continual learning, ancestor inheritance, structural growth, or general intelligence is authorized.

NEXT ACTION
Design and preregister STAB-07. Do not execute it until its exact single factor and gates exist in .ice. Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling.
