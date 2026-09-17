TITLE: DG-1 Current Research Status
DATE: 2026-09-17
STATUS: ACTIVE — DG-1A P0 VIABILITY / SUPPORT-GEOMETRY STABILIZATION
TRACK: DG-1
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; EXPLORATORY FOR SANDBOX RESULTS

PURPOSE
Maintain an operator-readable durable research status ledger. This record summarizes the live DG-1 frontier and points to experiment-specific evidence. It is not an execution authority.

CURRENT OBJECTIVE
Establish a viable canonical DG-1A developmental substrate that grows meaningful target morphology, maintains bounded support, remains stable, suffers meaningful damage, and exhibits measurable stable repair before opening DG-1B functional computation.

RESEARCH FOUNDATION
YG-R1 through YG-R8 research records exist.
YG-R8 Pass 1 is closed and reconciled into the DG-1 implementation gate.
Functional-regeneration, structural-plasticity, resource-pressure, and measurement contracts remain adopted for early DG-1 work.

ACTIVE BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
41a2410c70980f2d2617a1c36a854d3610511420

P0 IMPLEMENTATION STATUS
The bounded P0 substrate, training curricula, recovery/persistence telemetry, resource accounting, resumable training, evidence paths, and six explicit historical training-loss modes are implemented:
- global_mse;
- balanced_fg_bg;
- global_plus_foreground;
- global_plus_foreground_bg_alpha;
- global_plus_foreground_bg_alive_margin;
- global_plus_foreground_farfield_bg_alpha.

The current implementation also contains target-derived one-cell support-halo / far-field occupancy telemetry used by STAB-07.

Latest reconstructed sandbox regression:
89 passed
0 failed
pytest return code: 0
Python 3.13.5 / PyTorch 2.10.0+cpu

The STAB-07 execution source was semantically reconstructed from connected GitHub readbacks of implementation/test revision:
5635413653888f36e85305877be95b587c017d70

Byte identity with a native checkout was not established. Treat STAB-07 as measured sandbox evidence, not commit-bound confirmatory scientific acceptance.

CURRENT FULL-GRID FINDINGS
STAB-01: NEGATIVE
Fixed maturity-threshold increases did not provide a valid monotonic stabilization mechanism.

STAB-02: NEGATIVE
Longer 64..128 development horizons converged to an all-dead phenotype, exposing sparse-target degeneracy in global morphology MSE.

STAB-03 / STAB-04: NEGATIVE
Foreground protection avoided death but produced severe overgrowth and invalid lesions.

STAB-05: NEGATIVE WITH DIRECTIONAL OCCUPANCY SIGNAL
Continuous alpha-energy pressure across all target-background cells reduced overgrowth relative to STAB-04 but remained expansive and invalid for regeneration inference.
Key seed-0 values:
- pre-damage active cells: 1206 / 1600;
- pre-lesion global MSE: 0.0701904967;
- DamageEffect: -0.0144327730;
- final recovery active cells: 1329 / 1600;
- persistence final active cells: 1378 / 1600.

STAB-06: NEGATIVE — NEAR-DEAD SIDE
Threshold-aligned background alive-margin pressure crossed the viability bracket too far.
Key seed-0 values:
- pre-damage active cells: 3 / 1600;
- pre-lesion global MSE: 0.0283585768;
- RelativeDamageEffect: 0.0062380726;
- final recovery active cells: 0;
- RecoveryFraction: 0.0.

STAB-07: NEGATIVE — SUPPORT-GEOMETRY ABLATION
HALO-1 exempted exactly one target-derived local support halo from dedicated continuous alpha pressure while retaining far-field occupancy pressure.

Frozen support geometry:
- radius-6 target foreground: 113 cells;
- one-cell halo including foreground: 169 cells;
- support ring only: 56 cells;
- far field: 1431 cells.

A target-derived viability floor of 113 hard-active cells was frozen before execution.

Exactly one fresh seed-0 candidate completed the frozen 200-iteration H96/M16 envelope.
Measured sandbox result:
- minimum recorded training loss: 0.1897521913;
- final recorded training loss: 0.2067640871;
- pre-damage active cells: 1094 / 1600;
- pre-lesion global MSE: 0.0625592172;
- post-lesion global MSE: 0.0531895496;
- DamageEffect: -0.0093696676;
- RelativeDamageEffect: -0.1497727759;
- lesion removed 47.90% of active cells;
- final recovery active cells: 1232 / 1600;
- stable T50/T90 and RecoveryFraction: undefined/not attained;
- persistence active cells: 1005 -> 1276;
- persistence global MSE: 0.0572690740 -> 0.0921664238;
- candidate worth widening: NO.

STAB-07 INTERPRETATION
HALO-1 restored robust viability relative to STAB-06's near-dead phenotype but remained substantially overgrown and dynamically expansive.

The lesion removed nearly half of active cells yet improved the common global morphology metric. Therefore substantial harmful/excess structure remained before damage and regeneration inference was invalid.

Relative to STAB-05, HALO-1 produced modest directional improvement:
- pre-damage activity 1206 -> 1094, approximately 9.29% lower;
- pre-lesion global MSE 0.0701904967 -> 0.0625592172, approximately 10.87% lower;
- final recovery activity 1329 -> 1232;
- persistence final activity 1378 -> 1276.

These changes establish that immutable target-support geometry influences the viability/occupancy tradeoff, but a binary one-cell exemption is insufficient for bounded canonical P0 behavior.

CURRENT SCIENTIFIC BRACKET
Canonical P0 is now bracketed across objective pressure and spatial support:
- sparse global morphology loss can make death competitive;
- foreground protection can make severe overgrowth competitive;
- continuous all-background alpha pressure partially reduces overgrowth but does not bound support;
- strong threshold-aligned background pressure can collapse support to near-death;
- one-cell support-halo exemption restores viability but still permits excessive support and expansion.

The next question is therefore not simply how much regularization to apply. The mechanism must preserve meaningful target support while controlling excess support geometry/cardinality and post-growth expansion.

DURABLE STAB-07 RECORDS
research/experiments/dg1a/dg1a-p0-stab07-spec.ice
research/experiments/dg1a/dg1a-p0-stab07-result.ice
evidence/dg1a/p0_stab07_sandbox.json
research/status/dg1a-p0-status.ice

Full local sandbox evidence SHA-256:
7c239b160e65c5bbf42e85657262c551853f6b42d98946cd47b5a10c0a5823b4

CURRENT DECISIONS
- STAB-07 is closed negative;
- HALO-1 is not widened to additional seeds;
- halo radius, coefficients, and thresholds are not tuned retroactively;
- the target-derived 113-cell viability floor and existing gates are retained;
- the global evaluation metric remains unchanged and must be interpreted jointly with viability/occupancy telemetry;
- all six historical training-loss modes remain preserved for reproducibility;
- STAB-05/06/07 jointly establish a useful occupancy/viability/support-geometry bracket;
- canonical full-grid P0 remains unresolved;
- DG-1B remains unopened.

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-08 — DESIGN / PREREGISTRATION ONLY.

STAB-08 should test one fixed mechanism that preserves meaningful target viability while constraining excess support geometry/cardinality or dynamic expansion. Candidate design classes include graded support geometry, a coupled target-support/excess-occupancy objective, or an immutable-target support-expansion penalty.

No STAB-08 mechanism is selected by this status ledger.
No STAB-08 scientific execution is authorized until one mechanism, one fixed parameterization, the common evaluation metric, frozen envelope, and complete gates are preregistered in .ice.

Do not convert STAB-08 into a coefficient or halo-radius sweep of STAB-07.

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
Remains a first-class future direction. It is not opened by STAB-07.

BOUNDARIES
Do not modify Wingless, ckb-plane, or Mind-Palace without explicit authorization.
Do not activate CKB runtime, Coinbase/live broker systems, TradeGuard, deployment/promotion, or external execution authority.
P0 remains morphology/developmental-substrate research and does not establish cognition or general intelligence.

NEXT ACTION
Design and preregister STAB-08. Do not execute it until its exact single factor and gates exist in .ice. Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling until canonical P0 viability/stability is adequately characterized.
