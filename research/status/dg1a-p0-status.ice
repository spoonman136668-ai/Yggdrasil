TITLE: DG-1A-P0 Current Status
DATE: 2026-09-17
STATUS: ACTIVE — STAB-07 CLOSED NEGATIVE / STAB-08 DESIGN NOT YET PREREGISTERED
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; EXPLORATORY FOR SANDBOX RESULTS

BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
cbaefe561c191ebff59cef65b71d55939c3ba426

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
- explicit global_plus_foreground_farfield_bg_alpha training mode;
- target-foreground morphology helper;
- target-background alpha-energy helper;
- threshold-aligned alive-margin helper;
- target-derived one-cell support-halo / far-field alpha helper;
- fail-closed foreground/background/far-field/margin validation;
- fail-closed config validation.

LATEST TEST STATUS
STAB-07 reconstructed sandbox regression:
89 passed
0 failed
pytest return code: 0
Environment: Python 3.13.5 / PyTorch 2.10.0+cpu

The sandbox source was semantically reconstructed from connected GitHub readbacks of implementation/test revision:
5635413653888f36e85305877be95b587c017d70

This was not a native byte-identical checkout. Treat the tests and scientific result as sandbox evidence, not commit-bound confirmatory acceptance.

SCIENTIFIC / EXPERIMENTAL FRONTIER
Full-grid 40 x 40 canonical stabilization remains unresolved.

STAB-01 — CLOSED NEGATIVE
Fixed maturity-threshold increases did not provide a valid monotonic stabilization mechanism.

STAB-02 — CLOSED NEGATIVE
Longer 64..128 development horizons converged to an all-dead phenotype, exposing sparse-target degeneracy in global morphology MSE.

STAB-03 / STAB-04 — CLOSED NEGATIVE
Foreground-emphasized objectives avoided death but produced severe overgrowth and invalid lesions.
STAB-04 seed-0 reference:
- pre-damage active cells: 1578 / 1600;
- pre-lesion global MSE: 0.1845480204;
- DamageEffect: -0.0661034361.

STAB-05 — CLOSED NEGATIVE WITH DIRECTIONAL OCCUPANCY SIGNAL
OCC-A1 added continuous alpha-energy pressure on all target-background cells.
Measured seed-0 result:
- pre-damage active cells: 1206 / 1600;
- pre-lesion global MSE: 0.0701904967;
- DamageEffect: -0.0144327730;
- final recovery active cells: 1329 / 1600;
- persistence active cells: 1140 -> 1378.

STAB-06 — CLOSED NEGATIVE / NEAR-DEAD SIDE
AM-05 used threshold-aligned target-background alive-margin pressure.
Measured seed-0 result:
- pre-damage active cells: 3 / 1600;
- pre-lesion global MSE: 0.0283585768;
- RelativeDamageEffect: 0.0062380726;
- final recovery active cells: 0;
- RecoveryFraction: 0.0.

STAB-07 — CLOSED NEGATIVE
Candidate: HALO-1

ForegroundMask = target alpha > 0.1
SupportHaloMask = one 3 x 3 max-pool dilation of target foreground
FarFieldBackgroundAlphaMSE = alpha^2 mean only outside the target support halo

TrainingMorphologyLoss = GlobalVisibleMSE + ForegroundVisibleMSE + FarFieldBackgroundAlphaMSE

Frozen target/support geometry:
- foreground cells: 113;
- support halo including foreground: 169;
- support ring only: 56;
- far-field cells: 1431.

A target-derived viability floor of 113 hard-active cells was frozen before execution.

Exactly one fresh seed-0 HALO-1 candidate completed 200 / 200 iterations through a single-writer resumable checkpoint path.

Measured sandbox result:
- minimum recorded loss: 0.1897521913;
- final recorded loss: 0.2067640871;
- pre-damage active cells: 1094 / 1600;
- pre-lesion global MSE: 0.0625592172;
- post-lesion global MSE: 0.0531895496;
- DamageEffect: -0.0093696676;
- RelativeDamageEffect: -0.1497727759;
- active-cell removal: 47.90%;
- final recovery active cells: 1232 / 1600;
- bounded RecoveryFraction: undefined;
- stable T50/T90: not attained / undefined;
- persistence active cells: 1005 -> 1276;
- persistence global MSE: 0.0572690740 -> 0.0921664238;
- candidate worth widening: NO.

STAB-07 FAILURE MODE
VIABLE BUT OVERGROWN / EXPANSIVE PHENOTYPE WITH INVALID LESION.

HALO-1 clearly avoided STAB-06's near-dead collapse and passed the 113-cell viability floor. However, it remained far above the 800-cell occupancy ceiling at growth, recovery, and persistence.

The 0.60 lesion removed 524 active cells, approximately 47.90% of the active phenotype, yet improved the unchanged global morphology MSE. Therefore substantial harmful/excess structure remained and regeneration inference was invalid.

Relative to STAB-05, HALO-1 was directionally favorable but insufficient:
- pre-damage active cells: 1206 -> 1094, approximately 9.29% lower;
- pre-lesion global MSE: 0.0701904967 -> 0.0625592172, approximately 10.87% lower;
- final recovery active cells: 1329 -> 1232;
- persistence final active cells: 1378 -> 1276.

CURRENT OBJECTIVE DIAGNOSIS
Canonical P0 is now experimentally bracketed across both strength and spatial-support behavior:

1. sparse global morphology pressure can make death competitive;
2. foreground protection can preserve viability while allowing severe overgrowth;
3. continuous all-background alpha pressure partially suppresses overgrowth but does not bound support;
4. strong threshold-aligned background pressure crosses into near-death;
5. exempting exactly one local target-support halo restores robust viability and modestly improves the overgrowth result, but does not bound global support or prevent expansion.

The next research problem is not a simple scalar interpolation or halo-radius sweep. A successful mechanism must preserve meaningful target support while more directly controlling excess support geometry/cardinality and dynamic expansion.

DURABLE STAB-07 RECORDS
research/experiments/dg1a/dg1a-p0-stab07-spec.ice
research/experiments/dg1a/dg1a-p0-stab07-result.ice
evidence/dg1a/p0_stab07_sandbox.json

Full local sandbox evidence SHA-256:
7c239b160e65c5bbf42e85657262c551853f6b42d98946cd47b5a10c0a5823b4

CURRENT DECISIONS
- close STAB-07 as negative;
- do not widen HALO-1 to additional seeds;
- do not tune its halo radius, far-field coefficient, foreground coefficient, or thresholds inside STAB-07;
- do not weaken the 113-cell target-derived viability floor or other preregistered gates;
- preserve global morphology MSE as the common evaluation metric alongside viability telemetry;
- preserve all six implemented historical loss modes for reproducibility;
- retain the STAB-05/06/07 occupancy/viability/support bracket as first-class mechanistic evidence;
- do not reopen STAB-01 through STAB-07 with post-result parameter or threshold inserts;
- do not begin DG-1B yet;
- do not introduce Fibonacci scheduling into canonical P0 yet;
- retain Fibonacci as the separate DG-1A-FIB1 follow-on ablation.

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-08, DESIGN / PREREGISTRATION ONLY.

STAB-08 should test one fixed mechanism that explicitly preserves target viability while constraining excess support geometry/cardinality or dynamic expansion.

Plausible mechanism classes for design review include:
- graded target-support geometry rather than binary halo exemption;
- a coupled target-support / excess-occupancy objective;
- a bounded support-expansion term tied to immutable target geometry.

NO STAB-08 mechanism is selected by this status record.

Before execution, STAB-08 must preregister one explicit mechanism, one fixed parameterization, the unchanged common evaluation metric, a frozen experimental envelope, and explicit viability, occupancy, lesion-validity, morphology, recovery, persistence, and finite-state gates.

Do not convert STAB-08 into a coefficient or halo-radius sweep of STAB-07.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
No claim of cognition, functional specialization, continual learning, ancestor inheritance, structural growth, or general intelligence is authorized.

NEXT ACTION
Design and preregister STAB-08. Do not execute it until its exact single factor and gates exist in .ice. Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling.
