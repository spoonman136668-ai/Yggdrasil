TITLE: DG-1A-P0 Current Status
DATE: 2026-09-17
STATUS: ACTIVE — STAB-08 CLOSED NEGATIVE / STAB-09 DESIGN NOT YET PREREGISTERED
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; EXPLORATORY FOR SANDBOX RESULTS

BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
a82decbd24d3145b7d302b7c35e9b311b853b8ac

CURRENT PURPOSE
Establish a trustworthy canonical developmental NCA control with meaningful viable growth, bounded support, persistence/homeostasis, meaningful damage, and stable regeneration before DG-1B functional computation or later Yggdrasil mechanisms are opened.

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
- target foreground morphology helper;
- all-background alpha-energy helper;
- threshold-aligned alive-margin helper;
- one-cell support-halo/far-field helper;
- immutable target Chebyshev-distance weight helper;
- graded background alpha helper;
- fail-closed config/target-region validation;
- seven explicit historical training-loss modes:
  1. global_mse
  2. balanced_fg_bg
  3. global_plus_foreground
  4. global_plus_foreground_bg_alpha
  5. global_plus_foreground_bg_alive_margin
  6. global_plus_foreground_farfield_bg_alpha
  7. global_plus_foreground_graded_bg_alpha

LATEST TEST STATUS
STAB-08 reconstructed sandbox regression:
100 passed
0 failed

Execution was split only to stay within bounded tool-call windows:
- 95 non-runner tests: PASS, return code 0;
- STAB-04 + STAB-05 runner-evidence tests: 2 PASS, return code 0;
- STAB-06 + STAB-07 runner-evidence tests: 2 PASS, return code 0;
- STAB-08 runner-evidence test: PASS, return code 0.

Environment:
Python 3.13.5
PyTorch 2.10.0+cpu

STAB-08 execution source was semantically reconstructed from connected GitHub readbacks of:
5b67f6a6f2f748ee2da9a8208739173b8d4232cb

This was not a native byte-identical checkout.
Treat STAB-08 as MEASURED SANDBOX evidence, not commit-bound confirmatory acceptance.

SCIENTIFIC / EXPERIMENTAL FRONTIER
Full-grid 40 x 40 canonical stabilization remains unresolved.

STAB-01 — CLOSED NEGATIVE
Fixed maturity-threshold increases did not provide a valid monotonic stabilization mechanism.

STAB-02 — CLOSED NEGATIVE
Longer 64..128 developmental horizons converged to an all-dead phenotype, exposing sparse-target degeneracy in global morphology MSE.

STAB-03 / STAB-04 — CLOSED NEGATIVE
Foreground-emphasized objectives avoided death but produced severe overgrowth and invalid lesions.
STAB-04 reference:
- pre-damage active: 1578 / 1600;
- pre-lesion MSE: 0.1845480204;
- DamageEffect: -0.0661034361.

STAB-05 — CLOSED NEGATIVE WITH DIRECTIONAL OCCUPANCY SIGNAL
OCC-A1 added continuous alpha-energy pressure on all target-background cells.
Seed-0:
- pre-damage active: 1206 / 1600;
- pre-lesion MSE: 0.0701904967;
- DamageEffect: -0.0144327730;
- final recovery active: 1329;
- persistence final active: 1378.
This reduced overgrowth relative to STAB-04 but remained expansive and lesion-invalid.

STAB-06 — CLOSED NEGATIVE / NEAR-DEAD SIDE
AM-05 used threshold-aligned background alive-margin pressure.
Seed-0:
- pre-damage active: 3 / 1600;
- pre-lesion MSE: 0.0283585768;
- RelativeDamageEffect: 0.0062380726;
- final recovery active: 0;
- RecoveryFraction: 0.0.
This crossed the viability bracket into near-death.

STAB-07 — CLOSED NEGATIVE / BINARY SUPPORT GEOMETRY
HALO-1 fully exempted one immutable target-derived 3 x 3 support halo from dedicated continuous alpha pressure.
Frozen geometry:
- foreground: 113 cells;
- one-cell support halo including foreground: 169;
- support ring only: 56;
- far field: 1431.

Seed-0:
- pre-damage active: 1094;
- pre-lesion MSE: 0.0625592172;
- DamageEffect: -0.0093696676;
- RelativeDamageEffect: -0.1497727759;
- final recovery active: 1232;
- persistence active: 1005 -> 1276.

HALO-1 restored robust viability relative to STAB-06 and modestly improved STAB-05, but remained far above occupancy/morphology gates.

STAB-08 — CLOSED NEGATIVE / GRADED STATIC SUPPORT GEOMETRY
Candidate: DIST-1

For each target-background cell:
d = immutable Chebyshev distance to nearest target-foreground cell
DistanceWeight(d) = d / (d + 1)

GradedBackgroundAlphaMSE =
mean(DistanceWeight(d) * state_alpha^2 over target-background cells)

TrainingMorphologyLoss =
GlobalVisibleMSE + ForegroundVisibleMSE + GradedBackgroundAlphaMSE

Frozen target-distance facts:
- foreground cells: 113;
- background cells: 1487;
- max distance: 16;
- mean background weight: 0.8635463277;
- no support-radius parameter;
- no distance cap;
- no coefficient schedule.

Exactly one fresh seed-0 DIST-1 candidate completed 200 / 200 iterations through the single-writer resumable path.

Measured result:
- initial recorded loss: 0.4459555447;
- minimum recorded loss: 0.2007718384;
- final recorded loss: 0.2026043236;
- pre-damage active cells: 1440 / 1600;
- pre-lesion global MSE: 0.1016835570;
- post-lesion global MSE: 0.0743995309;
- DamageEffect: -0.0272840261;
- RelativeDamageEffect: -0.2683228925;
- lesion active-cell removal: 40.00%;
- final recovery active cells: 1095 / 1600;
- RecoveryFraction: undefined;
- stable T50/T90: not attained / undefined;
- persistence active cells: 1348 -> 1102;
- persistence MSE: 0.0879649892 -> 0.0973186269;
- candidate worth widening: NO.

STAB-08 FAILURE MODE
VIABLE BUT SEVERE OVERGROWTH WITH INVALID LESION.

DIST-1 worsened the mature pre-lesion phenotype relative to both STAB-05 and STAB-07.

Relative to STAB-05:
- pre-damage activity 1206 -> 1440, approximately 19.40% higher;
- pre-lesion MSE 0.0701904967 -> 0.1016835570, approximately 44.87% worse.

Relative to STAB-07:
- pre-damage activity 1094 -> 1440, approximately 31.63% higher;
- pre-lesion MSE 0.0625592172 -> 0.1016835570, approximately 62.54% worse.

Later activity contracted more strongly:
- final recovery active: 1095;
- persistence final active: 1102.

That contraction does not represent success because:
- both remain above the 800 occupancy ceiling;
- persistence morphology remains poor;
- the lesion improved global morphology;
- no valid morphology-damage event existed for regeneration inference.

CURRENT OBJECTIVE DIAGNOSIS
The canonical P0 search is now bracketed across objective strength, support geometry, and dynamic behavior:

1. sparse global morphology pressure can make death competitive;
2. foreground protection can preserve viability while allowing severe overgrowth;
3. uniform continuous background alpha pressure partially suppresses overgrowth but does not bound support;
4. threshold-aligned pressure can collapse support into near-death;
5. binary one-cell support exemption restores viability but remains overgrown;
6. smooth monotonic target-distance weighting d/(d+1) worsens mature overgrowth rather than locating bounded viable support;
7. active support can later contract while morphology remains poor, indicating that static spatial weighting is not adequately controlling the developmental/homeostatic dynamics.

The next discriminating question should therefore move away from another static scalar/halo/distance interpolation.

The live mechanism class is DYNAMIC SUPPORT CONTROL:
- penalize creation or maintenance of excess support over developmental transitions;
- encourage post-growth homeostasis rather than only endpoint resemblance;
- preserve the target-derived viability floor while preventing continued support expansion.

DURABLE STAB-08 RECORDS
research/experiments/dg1a/dg1a-p0-stab08-spec.ice
research/experiments/dg1a/dg1a-p0-stab08-result.ice
evidence/dg1a/p0_stab08_sandbox.json

Full local sandbox evidence SHA-256:
8c4a0c21319cdb06dc2d806faec2d593cb9233d6320d29bbc77e14b651b6532e

CURRENT DECISIONS
- close STAB-08 as negative;
- do not widen DIST-1 to additional seeds;
- do not tune d/(d+1), coefficients, thresholds, margins, halo radii, or gates retroactively;
- preserve the 113-cell target-derived viability floor;
- preserve the 800-cell occupancy ceiling;
- preserve global visible-channel MSE as the common evaluation metric alongside viability/occupancy/persistence/lesion-validity telemetry;
- preserve all seven historical training-loss modes for reproducibility;
- retain STAB-05/06/07/08 as first-class mechanistic negative knowledge;
- do not reopen STAB-01 through STAB-08 with post-result parameter inserts;
- do not begin DG-1B yet;
- do not introduce Fibonacci scheduling into canonical P0 yet;
- retain Fibonacci as separate DG-1A-FIB1 follow-on ablation.

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-09 — DESIGN / PREREGISTRATION ONLY.

STAB-09 should test one fixed DYNAMIC support/homeostasis mechanism rather than another static coefficient, margin, halo-radius, or target-distance sweep.

Plausible mechanism classes for design review:
- explicit excess-support creation penalty between developmental states;
- post-growth support-expansion/homeostasis penalty;
- coupled morphology + support-change objective anchored to immutable target viability.

NO STAB-09 mechanism is selected by this status record.

Before execution, STAB-09 must preregister:
- one explicit dynamic mechanism;
- one fixed parameterization;
- unchanged common evaluation metric;
- frozen experimental envelope;
- explicit viability, occupancy, lesion-validity, morphology, recovery, persistence/homeostasis, and finite-state gates.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
No claim of cognition, functional specialization, continual learning, ancestor inheritance, structural growth, or general intelligence is authorized.

NEXT ACTION
Design and preregister STAB-09.
Do not execute it until its exact single factor and gates exist in .ice.
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling.
