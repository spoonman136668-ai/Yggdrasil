TITLE: DG-1 Current Research Status
DATE: 2026-09-17
STATUS: ACTIVE — DG-1A P0 VIABILITY / BOUNDED-SUPPORT STABILIZATION
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
64fb65cfa179bf76459843bb31998dfba60681ae

P0 IMPLEMENTATION STATUS
The bounded P0 substrate, training curricula, recovery/persistence telemetry, resource accounting, resumable training, evidence paths, and five explicit historical training-loss modes are implemented:
- global_mse;
- balanced_fg_bg;
- global_plus_foreground;
- global_plus_foreground_bg_alpha;
- global_plus_foreground_bg_alive_margin.

Latest reconstructed sandbox regression:
79 passed
0 failed
Python 3.13.5 / PyTorch 2.10.0+cpu

The STAB-06 execution source was semantically reconstructed from connected GitHub readbacks of implementation/test revision:
6e8d79b0fd47b7031b05f03b395bf49c1649f00e

Byte identity with a native checkout was not established. Treat STAB-06 as measured sandbox evidence, not commit-bound confirmatory scientific acceptance.

CURRENT FULL-GRID FINDINGS
STAB-01: NEGATIVE
Fixed maturity-threshold increases did not provide a valid monotonic stabilization mechanism.

STAB-02: NEGATIVE
Longer 64..128 development horizons converged to an all-dead phenotype, exposing sparse-target degeneracy in global morphology MSE.

STAB-03: NEGATIVE
Equal foreground/background regional weighting prevented death but produced severe overgrowth and an invalid lesion.

STAB-04: NEGATIVE
GlobalVisibleMSE + ForegroundVisibleMSE produced 1578 / 1600 pre-damage active cells, pre-lesion global MSE 0.1845480204, and negative DamageEffect.

STAB-05: NEGATIVE WITH DIRECTIONAL SIGNAL
OCC-A1 added continuous target-background alpha-energy pressure.
It reduced pre-damage activity from STAB-04's 1578 to 1206 and pre-lesion global MSE from 0.1845480204 to 0.0701904967, but remained overgrown, expanded under persistence/recovery, and still had an invalid lesion.

STAB-06: NEGATIVE — OPPOSITE-SIDE FAILURE
AM-05 replaced continuous alpha-energy pressure with a threshold-aligned alive-margin term:

BackgroundAliveMarginLoss = mean((ReLU(alpha - 0.05) / 0.05)^2 over target-background pixels)

Exactly one fresh seed-0 candidate completed the frozen H96/M16 envelope.
Measured sandbox result:
- 200 / 200 training iterations;
- minimum recorded loss: 0.3612360060;
- final recorded loss: 0.3881474733;
- pre-damage active cells: 3 / 1600;
- pre-lesion global MSE: 0.0283585768;
- post-lesion global MSE: 0.0285354797;
- DamageEffect: 0.0001769029;
- RelativeDamageEffect: 0.0062380726;
- final recovery active cells: 0 / 1600;
- bounded RecoveryFraction: 0.0;
- stable T50/T90: not attained;
- normalized recovery AUC: 0.0036180955;
- persistence active cells: 2 -> 5;
- candidate worth widening: NO.

STAB-06 INTERPRETATION
AM-05 suppressed occupancy strongly enough to eliminate the previous overgrowth regime but reopened the sparse-target near-dead attractor.

Its pre-lesion global MSE is numerically below the morphology gate only because the phenotype had three active cells. Recovery converged to zero active cells and final global MSE approximately 0.0295742, the known near-all-zero target loss regime.

The lesion technically increased error, but RelativeDamageEffect was only approximately 0.00624 versus the preregistered minimum 0.10. The lesion was therefore not meaningful enough to support regeneration inference.

Persistence numerical gates passed on an almost-dead state and do not establish viable morphology stability.

CURRENT SCIENTIFIC BRACKET
Canonical P0 is now more tightly bracketed:
- global sparse-target morphology MSE can make death competitive;
- strong foreground protection can make severe overgrowth competitive;
- continuous background alpha-energy regularization partially reduces overgrowth but does not bound support;
- the tested threshold-aligned margin regularizer crosses too far and produces near-death.

The next research problem is to preserve meaningful foreground/support viability while bounding excess occupancy. It should not be treated as a simple scalar-weight sweep between STAB-05 and STAB-06.

DURABLE STAB-06 RECORDS
research/experiments/dg1a/dg1a-p0-stab06-spec.ice
research/experiments/dg1a/dg1a-p0-stab06-result.ice
evidence/dg1a/p0_stab06_sandbox.json
research/status/dg1a-p0-status.ice

Full local sandbox evidence SHA-256:
ba29d40ae653d61a6bee97668e402158d4f42f235502b3925280a1136cf6bf59

CURRENT DECISIONS
- STAB-06 is closed negative;
- AM-05 is not widened to additional seeds;
- its coefficient, margin floor, margin width, and alive threshold are not tuned retroactively;
- the global evaluation metric remains unchanged and must be interpreted jointly with viability telemetry;
- all five historical training-loss modes remain preserved for reproducibility;
- STAB-05 and STAB-06 jointly establish an occupancy/viability bracket worth retaining as first-class negative knowledge;
- canonical full-grid P0 remains unresolved;
- DG-1B remains unopened.

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-07 — DESIGN / PREREGISTRATION ONLY.

STAB-07 should test one fixed mechanism that couples meaningful viable target support with bounded excess occupancy. Candidate design classes include a coupled viability/occupancy constraint or target-support geometry control.

No STAB-07 mechanism is selected by this status ledger.
No STAB-07 scientific execution is authorized until one mechanism, one fixed parameterization, the common evaluation metric, frozen envelope, and complete gates are preregistered in .ice.

Do not convert STAB-07 into a coefficient or margin sweep of STAB-06.

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
Remains a first-class future direction. It is not opened by STAB-06.

BOUNDARIES
Do not modify Wingless, ckb-plane, or Mind-Palace without explicit authorization.
Do not activate CKB runtime, Coinbase/live broker systems, TradeGuard, deployment/promotion, or external execution authority.
P0 remains morphology/developmental-substrate research and does not establish cognition or general intelligence.

NEXT ACTION
Design and preregister STAB-07. Do not execute it until its exact single factor and gates exist in .ice. Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling until canonical P0 viability/stability is adequately characterized.
