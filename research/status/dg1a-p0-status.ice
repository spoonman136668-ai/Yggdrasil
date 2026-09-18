TITLE: DG-1A-P0 Current Status
DATE: 2026-09-17
STATUS: ACTIVE — STAB-11 CLOSED NEGATIVE / STAB-12 DESIGN NOT YET PREREGISTERED
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; MEASURED_SANDBOX FOR CANONICAL EXPERIMENTS

BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
b3390553566e3fb6608a9b3e02d0b0b082361677

CURRENT PURPOSE
Establish a trustworthy canonical developmental NCA control with meaningful viable growth, bounded support, long-horizon homeostasis, meaningful damage, and stable regeneration before DG-1B functional computation or later Yggdrasil mechanisms are opened.

IMPLEMENTED SURFACE
- fixed-grid shared-rule NCA substrate;
- deterministic seed and repository-native target generation;
- state-pool persistence/regeneration curricula;
- maturity-gated training damage;
- independent training/evaluation lesion geometry;
- global/stable recovery metrics;
- persistence and active-cell trajectory telemetry;
- resource accounting;
- resumable deterministic training sessions;
- machine-readable evidence writer/runner;
- static morphology modes through STAB-08;
- HOME-1 mature-only one-step local velocity control;
- HOME-T16 fixed 16-step local velocity control;
- ATTRACT-16 fixed 16-step future target-trajectory supervision;
- RNG-neutral virtual trajectories;
- virtual-trajectory pool isolation;
- fail-closed config/finite-state validation.

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
10. global_plus_foreground_bg_alpha_attractor_t16

LATEST TEST STATUS
STAB-11 reconstructed sandbox regression:
135 passed
0 failed

Environment:
Python 3.13.5
PyTorch 2.10.0+cpu

STAB-11 scientific source revision:
6db241bce7ba21c51baedb80152f0e031bf233de

source_revision_verified_checkout = false
sandbox_source_byte_identity = false
evidence_class = MEASURED_SANDBOX

SCIENTIFIC FRONTIER
Full-grid 40 x 40 canonical stabilization remains unresolved.

STAB-01 / STAB-02
CLOSED NEGATIVE.
Maturity/horizon changes did not stabilize canonical P0; sparse endpoint morphology made death competitive.

STAB-03 / STAB-04
CLOSED NEGATIVE.
Foreground-emphasized objectives prevented death but made severe overgrowth competitive.

STAB-05
CLOSED NEGATIVE WITH OCCUPANCY SIGNAL.
Continuous target-background alpha pressure reduced overgrowth but did not bound support.

STAB-06
CLOSED NEGATIVE / NEAR-DEAD SIDE.
Threshold-aligned alive-margin pressure crossed the bracket into near-death.

STAB-07
CLOSED NEGATIVE.
Binary one-cell target-support exemption restored viability but remained overgrown.

STAB-08
CLOSED NEGATIVE.
Static graded target-distance weighting worsened the mature overgrowth phenotype.

STAB-09 — HOME-1
CLOSED NEGATIVE.
One mature-only virtual step improved the nominal snapshot but did not establish long-horizon homeostasis:
- pre-damage active: 993;
- pre-lesion MSE: 0.0524558015;
- persistence active: 941 -> 1406;
- persistence peak: 1490;
- active drift: +465;
- lesion invalid.

STAB-10 — HOME-T16
CLOSED NEGATIVE.
The same local positive-background-alpha velocity mechanism extended to exactly 16 virtual steps:
- pre-damage active: 1407;
- pre-lesion MSE: 0.0883897096;
- persistence active: 1360 -> 1353;
- persistence peak: 1501;
- drift: -7;
- lesion invalid;
- 10 / 14 gates failed.

Conclusion:
longer local velocity horizon alone did not create a bounded target attractor.

STAB-11 — ATTRACT-16
CLOSED NEGATIVE WITH IMPORTANT DIRECTIONAL ATTRACTOR SIGNAL.

Mechanism:
- mature when active count >= immutable target foreground cardinality 113;
- exactly 16 RNG-neutral virtual future steps;
- virtual states excluded from pool authority;
- each future state receives:
  GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAlphaMSE;
- future losses arithmetic-mean reduced;
- auxiliary coefficient 1.0;
- normal endpoint keeps its static objective.

Exactly one fresh seed-0 candidate completed 200 / 200 iterations.

Measured training:
- initial loss: 0.4459555447;
- minimum/final loss: 0.3962120116;
- final attractor trajectory loss: 0.1982530355;
- mature samples: 8 / 8;
- no non-finite state.

Measured growth/recovery:
- pre-damage active: 1252 / 1600;
- pre-lesion MSE: 0.0665020347;
- post-lesion MSE: 0.0562916957;
- DamageEffect: -0.0102103390;
- RelativeDamageEffect: -0.1535342344;
- active-cell removal: 44.01%;
- final recovery active: 882;
- stable T50: not attained;
- recovery inference invalid because lesion improved morphology.

Measured persistence:
- initial active: 1160;
- final active: 592;
- peak active: 1335;
- active drift: -568;
- initial MSE: 0.0616273582;
- final MSE: 0.0547853708;
- maximum MSE: 0.0852470100.

Preregistered gates:
9 / 14 failed.

Candidate worth widening:
NO.

STAB-11 INTERPRETATION
ATTRACT-16 is the first tested mechanism in this series to produce strongly contractive long-horizon occupancy while also improving persistence morphology over the trajectory.

The persistence endpoint entered the allowed occupancy range:
1160 -> 592 active cells.

This is directional evidence that direct future target-state supervision shapes the attractor more effectively than local velocity suppression.

However, the system enters persistence already severely overgrown:
- pre-damage active: 1252;
- persistence initial active: 1160;
- persistence peak: 1335.

The lesion removed 44.01% of active cells and improved morphology, proving substantial harmful/excess support remained in the nominal mature phenotype.

Therefore the unresolved seam is now more specific:

FORMATION-STAGE VIABLE SUPPORT OCCUPANCY

The system has learned a directionally better long-horizon attractor but reaches that regime from an oversized phenotype.

CURRENT MECHANISTIC BRACKET
1. sparse endpoint objective can collapse to death;
2. foreground preservation can create overgrowth;
3. continuous occupancy pressure is directionally useful but insufficient;
4. broad threshold pressure can kill viability;
5. static spatial support geometry is insufficient;
6. local dynamic velocity control is insufficient;
7. trajectory-level target supervision can reverse long-horizon expansion;
8. trajectory supervision alone acts too late to prevent oversized mature formation.

DURABLE STAB-11 RECORDS
research/experiments/dg1a/dg1a-p0-stab11-spec.ice
research/experiments/dg1a/dg1a-p0-stab11-result.ice
evidence/dg1a/p0_stab11_sandbox.json

CURRENT DECISIONS
- close STAB-11 as negative;
- do not widen ATTRACT-16;
- do not sweep ATTRACT horizon, coefficient, or reduction;
- preserve all ten historical modes;
- preserve viability floor 113 and occupancy ceiling 800;
- preserve strengthened persistence, lesion-validity, morphology, recovery, and finite-state gates;
- retain global visible morphology MSE as common evaluation metric;
- retain STAB-05 through STAB-11 as first-class mechanistic negative/directional knowledge;
- canonical full-grid P0 remains unresolved;
- do not begin DG-1B;
- do not introduce Fibonacci scheduling into canonical P0.

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-12 — DESIGN / PREREGISTRATION ONLY.

Preferred research seam:
a target-derived differentiable occupancy-setpoint mechanism applied during formation while preserving the trajectory-level target supervision signal demonstrated by ATTRACT-16.

The next mechanism must avoid simply repeating STAB-06's broad threshold pressure.
It should penalize excess viable support relative to a target-derived setpoint rather than penalizing all near-threshold background activity indiscriminately.

No STAB-12 mechanism is selected by this status record.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling from this packet.

NEXT ACTION
Research and preregister one discriminating STAB-12 formation-stage occupancy-setpoint mechanism.
Do not execute it before exact mechanism and gates exist in .ice.
