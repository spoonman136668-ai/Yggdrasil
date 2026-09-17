TITLE: DG-1 Current Research Status
DATE: 2026-09-17
STATUS: ACTIVE — DG-1A P0 DYNAMIC SUPPORT / HOMEOSTASIS STABILIZATION
TRACK: DG-1
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; EXPLORATORY FOR SANDBOX RESULTS

PURPOSE
Maintain the durable operator-readable DG-1 research frontier.
This status is not an execution authority.

ACTIVE BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
fbc30b97a3812b8a2293bf0fbb2e6f877c4a592e

CURRENT OBJECTIVE
Establish a viable canonical DG-1A developmental substrate that:
- grows meaningful target morphology;
- maintains bounded support;
- reaches post-growth homeostasis;
- suffers meaningful damage;
- exhibits measurable stable repair;
before DG-1B functional computation is opened.

RESEARCH FOUNDATION
YG-R1 through YG-R8 research records exist.
YG-R8 Pass 1 remains reconciled into the DG-1 implementation gate.
Functional-regeneration, structural-plasticity, resource-pressure, and measurement contracts remain adopted for early DG-1 work.

P0 IMPLEMENTATION STATUS
The substrate, state-pool curricula, recovery/persistence telemetry, resource accounting, resumable deterministic training, evidence paths, and seven historical loss modes are implemented:

1. global_mse
2. balanced_fg_bg
3. global_plus_foreground
4. global_plus_foreground_bg_alpha
5. global_plus_foreground_bg_alive_margin
6. global_plus_foreground_farfield_bg_alpha
7. global_plus_foreground_graded_bg_alpha

Implemented target/support helpers now include:
- foreground morphology;
- all-background alpha energy;
- threshold-aligned alive margin;
- one-cell target support halo / far-field mask;
- immutable target Chebyshev-distance weights;
- graded background alpha energy.

LATEST RECONSTRUCTED TEST STATUS
100 passed
0 failed

All 100 tests were executed in bounded clean-return groups because the combined subprocess-heavy suite exceeded the outer tool-call window:
- 95 non-runner tests passed;
- five runner-evidence tests passed.

Python 3.13.5
PyTorch 2.10.0+cpu

STAB-08 scientific execution source:
5b67f6a6f2f748ee2da9a8208739173b8d4232cb

The source was semantically reconstructed from connected GitHub readbacks.
Native byte-identical checkout was not established.
Scientific classification remains MEASURED SANDBOX, not commit-bound confirmatory acceptance.

CURRENT FULL-GRID FINDINGS

STAB-01 — NEGATIVE
Maturity-threshold increase was not a valid monotonic stabilization mechanism.

STAB-02 — NEGATIVE
Longer development horizons converged to an all-dead sparse-target solution.

STAB-03 / STAB-04 — NEGATIVE
Foreground-emphasized objectives avoided death but drove severe overgrowth and invalid lesions.

STAB-05 — NEGATIVE WITH OCCUPANCY SIGNAL
Uniform continuous target-background alpha pressure reduced STAB-04 overgrowth but remained expansive.
Reference:
- pre-damage active: 1206;
- pre-lesion MSE: 0.0701904967;
- DamageEffect: -0.0144327730.

STAB-06 — NEGATIVE / NEAR-DEAD SIDE
Threshold-aligned alive-margin pressure over-suppressed support.
Reference:
- pre-damage active: 3;
- final recovery active: 0;
- RecoveryFraction: 0.0.

STAB-07 — NEGATIVE / BINARY SUPPORT GEOMETRY
One-cell immutable target-support halo exemption restored robust viability but did not bound support.
Reference:
- pre-damage active: 1094;
- pre-lesion MSE: 0.0625592172;
- final recovery active: 1232;
- persistence final active: 1276;
- lesion still improved morphology.

STAB-08 — NEGATIVE / GRADED STATIC SUPPORT GEOMETRY
DIST-1 used immutable target Chebyshev distance:

DistanceWeight(d) = d / (d + 1)

GradedBackgroundAlphaMSE =
mean(DistanceWeight(d) * alpha^2 over target-background cells)

Frozen geometry:
- foreground: 113;
- background: 1487;
- max distance: 16;
- mean background weight: 0.8635463277.

Exactly one fresh seed-0 candidate completed the frozen 200-iteration H96/M16 envelope.

Measured sandbox result:
- minimum recorded loss: 0.2007718384;
- final recorded loss: 0.2026043236;
- pre-damage active cells: 1440 / 1600;
- pre-lesion global MSE: 0.1016835570;
- post-lesion global MSE: 0.0743995309;
- DamageEffect: -0.0272840261;
- RelativeDamageEffect: -0.2683228925;
- active-cell removal: 40.00%;
- final recovery active cells: 1095;
- stable T50/T90 and RecoveryFraction: undefined;
- persistence active cells: 1348 -> 1102;
- persistence MSE: 0.0879649892 -> 0.0973186269;
- candidate worth widening: NO.

STAB-08 INTERPRETATION
DIST-1 did not interpolate into a bounded viable phenotype.

It worsened the mature pre-lesion state:
- versus STAB-05, pre-damage activity increased approximately 19.40% and MSE worsened approximately 44.87%;
- versus STAB-07, pre-damage activity increased approximately 31.63% and MSE worsened approximately 62.54%.

Although activity later contracted after damage and during persistence, the phenotype remained above the occupancy ceiling and morphologically poor.

The lesion removed 40% of active cells and improved global morphology.
Therefore substantial harmful/excess support remained in the nominal mature phenotype, invalidating regeneration inference.

CURRENT SCIENTIFIC BRACKET
Canonical P0 now rejects several simple static objective classes:

- global sparse-target loss can make death competitive;
- foreground protection can make severe overgrowth competitive;
- uniform alpha pressure partially suppresses overgrowth but does not bound it;
- threshold-aligned pressure can cross into near-death;
- binary support-halo exemption restores viability but remains overgrown;
- smooth static target-distance weighting can worsen mature overgrowth.

The emerging failure is DYNAMIC:
- support is created and maintained incorrectly over developmental time;
- endpoint spatial penalties do not reliably enforce a bounded homeostatic attractor;
- lesions can remove structure that was actively harming morphology;
- support can later contract without converging to a good morphology.

This shifts the next research question from STATIC SUPPORT GEOMETRY to DYNAMIC SUPPORT / HOMEOSTASIS CONTROL.

DURABLE STAB-08 RECORDS
research/experiments/dg1a/dg1a-p0-stab08-spec.ice
research/experiments/dg1a/dg1a-p0-stab08-result.ice
evidence/dg1a/p0_stab08_sandbox.json
research/status/dg1a-p0-status.ice

Full local sandbox evidence SHA-256:
8c4a0c21319cdb06dc2d806faec2d593cb9233d6320d29bbc77e14b651b6532e

CURRENT DECISIONS
- STAB-08 is closed negative;
- DIST-1 is not widened;
- no retroactive distance-function/coefficient/threshold/gate tuning;
- target-derived viability floor of 113 remains;
- occupancy ceiling of 800 remains;
- global visible morphology MSE remains the common evaluation metric and must be interpreted jointly with viability/occupancy/persistence/lesion-validity telemetry;
- all seven historical modes remain preserved;
- STAB-05/06/07/08 remain first-class mechanistic negative knowledge;
- canonical full-grid P0 remains unresolved;
- DG-1B remains unopened.

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-09 — DESIGN / PREREGISTRATION ONLY.

STAB-09 should test exactly one fixed dynamic support/homeostasis mechanism.

Design classes worth considering:
- excess-support creation penalty across consecutive developmental states;
- post-growth support-expansion/homeostasis penalty;
- coupled morphology + support-change loss with target-derived viability protection.

No STAB-09 mechanism is selected by this ledger.
No STAB-09 scientific execution is authorized until its exact mechanism, fixed parameterization, common evaluation metric, frozen envelope, and complete gates are preregistered in .ice.

Do not convert STAB-09 into:
- a coefficient sweep;
- a margin sweep;
- a halo-radius sweep;
- another static distance-weight sweep.

FIBONACCI TRACK
DG-1A-FIB1 remains preserved and separate.
Do not introduce Fibonacci repair budgets, capacity ceilings, topology priors, or module-size schedules into canonical P0 while basic viability/homeostasis remains unresolved.

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
Remains a first-class future direction.
It is not opened by STAB-08.

BOUNDARIES
Do not modify Wingless, ckb-plane, or Mind-Palace without explicit authorization.
Do not activate CKB runtime, Coinbase/live broker systems, TradeGuard, deployment/promotion, or external execution authority.
P0 remains morphology/developmental-substrate research and does not establish cognition or general intelligence.

NEXT ACTION
Design and preregister STAB-09.
Do not execute it until its exact dynamic mechanism and gates exist in .ice.
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling until canonical P0 viability/homeostasis is adequately characterized.
