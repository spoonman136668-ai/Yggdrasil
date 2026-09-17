TITLE: DG-1 Current Research Status
DATE: 2026-09-17
STATUS: ACTIVE — DG-1A P0 STAB-10 CLOSED NEGATIVE / STAB-11 DESIGN
TRACK: DG-1
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; MEASURED_SANDBOX FOR CANONICAL EXPERIMENTS

PURPOSE
Maintain the durable operator-readable DG-1 research frontier.
This status is not an execution authority.

ACTIVE BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
07205a54eb8371aa987c9483273484ce83d11181

CURRENT OBJECTIVE
Establish a viable canonical DG-1A developmental substrate that:
- grows meaningful target morphology;
- maintains bounded support;
- enters a stable long-horizon homeostatic attractor;
- suffers meaningful damage;
- exhibits measurable stable repair;
before DG-1B functional computation is opened.

IMPLEMENTED P0 SURFACE
The bounded fixed-grid NCA substrate now includes:
- deterministic seed and target generation;
- state-pool persistence/regeneration curricula;
- maturity-gated training damage;
- independent training/evaluation lesion geometry;
- recovery/persistence/resource telemetry;
- resumable deterministic training;
- target foreground/background objective helpers;
- static occupancy, alive-margin, support-halo, and target-distance mechanisms;
- target-derived maturity masks;
- RNG-neutral one-step HOME-1 virtual probes;
- RNG-neutral fixed 16-step HOME-T16 virtual trajectories;
- trajectory-mean positive target-background alpha velocity loss;
- virtual-probe / virtual-trajectory pool isolation;
- fail-closed finite/config/target-region validation.

HISTORICAL TRAINING MODES
1. global_mse
2. balanced_fg_bg
3. global_plus_foreground
4. global_plus_foreground_bg_alpha
5. global_plus_foreground_bg_alive_margin
6. global_plus_foreground_farfield_bg_alpha
7. global_plus_foreground_graded_bg_alpha
8. global_plus_foreground_bg_alpha_homeostasis
9. global_plus_foreground_bg_alpha_homeostasis_t16

LATEST RECONSTRUCTED TEST STATUS
123 passed
0 failed

Environment:
Python 3.13.5
PyTorch 2.10.0+cpu

STAB-10 scientific source revision:
7d19c34cb59d96d2d94e2d8e5b92fcf4c7255e77

source_revision_verified_checkout = false
sandbox_source_byte_identity = false
evidence_class = MEASURED_SANDBOX

CURRENT FULL-GRID FINDINGS
STAB-01 / STAB-02:
endpoint maturity/horizon changes did not stabilize P0; sparse global morphology can make death competitive.

STAB-03 / STAB-04:
foreground protection prevented death but made severe overgrowth competitive.

STAB-05:
continuous target-background alpha pressure reduced overgrowth but did not bound support.

STAB-06:
threshold-aligned pressure crossed into near-death.

STAB-07:
binary one-cell target-support exemption restored viability but remained severely overgrown.

STAB-08:
static graded target-distance weighting worsened the mature phenotype.

STAB-09 — CLOSED NEGATIVE / HOME-1
One mature-only virtual step improved the nominal 96-step snapshot relative to STAB-05/07/08 but did not establish long-horizon homeostasis:
- pre-damage active: 993;
- pre-lesion MSE: 0.0524558015;
- persistence active: 941 -> 1406;
- persistence peak: 1490;
- active drift: +465;
- lesion invalid.

STAB-10 — CLOSED NEGATIVE / HOME-T16
Preregistered factor:
extend the same HOME-1 local dynamic signal to exactly 16 sequential mature-only virtual steps, arithmetic-mean the per-transition positive background-alpha velocity loss, and change no other scientific factor.

Exactly one seed-0 candidate completed 200 / 200 iterations.

Measured training:
- minimum/final loss: 0.2100088596;
- final HOME-T16 trajectory loss: 0.0178935546;
- final mature samples: 8 / 8;
- no non-finite state.

Measured growth/recovery:
- pre-damage active: 1407 / 1600;
- pre-lesion MSE: 0.0883897096;
- post-lesion MSE: 0.0698274300;
- DamageEffect: -0.0185622796;
- RelativeDamageEffect: -0.2100049851;
- active-cell removal: 40.94%;
- final recovery active: 1339;
- stable T50: not attained.

Measured persistence:
- active: 1360 -> 1353;
- peak active: 1501;
- drift: -7;
- MSE: 0.0818152428 -> 0.0922317058;
- maximum MSE: 0.1109334379.

Preregistered gates:
10 / 14 failed.

Candidate worth widening:
NO.

STAB-10 INTERPRETATION
HOME-T16 shows that HOME-1's failure is not adequately explained by a one-step probe horizon.

The longer local velocity horizon produced slightly negative net persistence drift, but only around a grossly overgrown phenotype, with a transient peak of 1501 active cells.

The nominal mature snapshot worsened relative to HOME-1:
- active cells 993 -> 1407;
- pre-lesion MSE 0.0524558015 -> 0.0883897096.

The lesion again improved morphology.
Therefore the canonical target is still not a bounded attractor and regeneration remains invalid.

CURRENT SCIENTIFIC BRACKET
P0 now supports the following mechanism-level conclusions:
- sparse endpoint loss can make death competitive;
- foreground preservation can make severe overgrowth competitive;
- continuous occupancy pressure is directionally useful but insufficient;
- stronger threshold pressure can kill viability;
- static spatial support geometry is insufficient;
- one-step dynamic control can improve a short-horizon snapshot without stabilizing the attractor;
- extending the same local velocity control to 16 steps still does not produce bounded support and can worsen the mature phenotype.

Do not ratchet nearby HOME virtual horizons.
The next discriminating mechanism should change objective architecture.

DURABLE STAB-10 RECORDS
research/experiments/dg1a/dg1a-p0-stab10-spec.ice
research/experiments/dg1a/dg1a-p0-stab10-result.ice
evidence/dg1a/p0_stab10_sandbox.json
research/status/dg1a-p0-status.ice

CURRENT DECISIONS
- STAB-10 is closed negative;
- HOME-T16 is not widened;
- no nearby virtual-horizon or coefficient sweep;
- preserve all nine historical modes;
- preserve viability floor 113 and occupancy ceiling 800;
- preserve lesion-validity, recovery, persistence, morphology, and finite-state gates;
- global visible MSE remains the common evaluation metric;
- canonical full-grid P0 remains unresolved;
- DG-1B remains unopened.

NEXT BOUNDED PACKET
DG-1A-P0-STAB-11 — DESIGN / PREREGISTRATION ONLY.

Preferred research seam:
an explicit persistence / attractor-state training mechanism, likely a bounded persistence curriculum term coupled to target-derived viability.

No STAB-11 mechanism is selected here.
Before execution, STAB-11 must preregister:
- one mechanism;
- one fixed parameterization;
- unchanged common evaluation metric;
- canonical envelope;
- complete viability, occupancy, lesion, recovery, persistence, morphology, and finite-state gates.

FIBONACCI TRACK
DG-1A-FIB1 remains preserved and separate.
Do not introduce Fibonacci scheduling into canonical P0 while basic viability/homeostasis remains unresolved.

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

BOUNDARIES
Do not modify Wingless, ckb-plane, or Mind-Palace without explicit authorization.
Do not activate CKB runtime, Coinbase/live broker systems, TradeGuard, deployment/promotion, or external execution authority.
P0 remains morphology/developmental-substrate research and does not establish cognition or general intelligence.

NEXT ACTION
Research and preregister one discriminating STAB-11 persistence/attractor-state mechanism.
Do not execute it before preregistration.
