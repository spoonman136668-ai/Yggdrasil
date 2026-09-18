TITLE: DG-1 Current Research Status
DATE: 2026-09-17
STATUS: ACTIVE — DG-1A P0 STAB-11 CLOSED NEGATIVE / STAB-12 DESIGN
TRACK: DG-1
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; MEASURED_SANDBOX FOR CANONICAL EXPERIMENTS

PURPOSE
Maintain the durable operator-readable DG-1 research frontier.
This status is not an execution authority.

ACTIVE BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
032dc0a47578ffdc4036d90be54e9955b4dc0a7b

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
- static morphology mechanisms through STAB-08;
- HOME-1 one-step local dynamic homeostasis;
- HOME-T16 fixed 16-step local velocity homeostasis;
- ATTRACT-16 fixed 16-step future target-state supervision;
- RNG-neutral virtual trajectories;
- virtual-trajectory pool isolation;
- fail-closed finite/config validation.

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

LATEST RECONSTRUCTED TEST STATUS
135 passed
0 failed

STAB-11 scientific source:
6db241bce7ba21c51baedb80152f0e031bf233de

source_revision_verified_checkout = false
sandbox_source_byte_identity = false
evidence_class = MEASURED_SANDBOX

CURRENT FULL-GRID FINDINGS
STAB-01 through STAB-08 established the death/overgrowth bracket and showed that endpoint/static occupancy geometry alone is insufficient.

STAB-09 HOME-1:
one-step local velocity control improved the nominal snapshot but persistence expanded strongly:
941 -> 1406 active; drift +465.

STAB-10 HOME-T16:
holding the same local velocity mechanism over 16 virtual steps produced only slight negative drift around a severely overgrown phenotype:
1360 -> 1353 active; peak 1501; pre-damage active 1407.

STAB-11 ATTRACT-16:
direct future target-state supervision over the same 16-step horizon materially changed the long-horizon dynamics:
- pre-damage active: 1252;
- pre-lesion MSE: 0.0665020347;
- persistence active: 1160 -> 592;
- persistence peak: 1335;
- persistence drift: -568;
- persistence MSE: 0.0616273582 -> 0.0547853708;
- final recovery active: 882;
- lesion improved morphology;
- 9 / 14 gates failed.

STAB-11 INTERPRETATION
Direct future target-state supervision is directionally superior to local velocity suppression for shaping the persistence attractor.

The candidate contracts toward the target regime over time rather than continuing to expand.

However, it reaches the persistence regime already severely overgrown.
The lesion remains invalid because removing 44.01% of active cells improves morphology.

Therefore the dominant unresolved seam is now:
FORMATION-STAGE VIABLE SUPPORT OCCUPANCY.

The next mechanism should control excess living support during formation while retaining the useful target-trajectory attractor signal.

CURRENT DECISIONS
- STAB-11 closed negative;
- ATTRACT-16 is not widened;
- no ATTRACT horizon/coefficient/reduction sweep;
- preserve all ten historical modes;
- preserve viability floor 113 and occupancy ceiling 800;
- preserve all lesion, recovery, persistence, morphology, and finite-state gates;
- global visible MSE remains the common evaluation metric;
- canonical full-grid P0 remains unresolved;
- DG-1B remains unopened.

NEXT BOUNDED PACKET
DG-1A-P0-STAB-12 — DESIGN / PREREGISTRATION ONLY.

Preferred seam:
a target-derived differentiable occupancy-setpoint mechanism applied during formation while retaining trajectory-level target supervision.

The next mechanism must differ materially from STAB-06 broad threshold pressure:
- it should penalize excess support relative to a target-derived cardinality/setpoint;
- it should not penalize every near-threshold background cell equally;
- it should preserve target foreground viability;
- it should remain one fixed preregistered construction, not a sweep.

FIBONACCI TRACK
DG-1A-FIB1 remains separate.
Do not introduce Fibonacci scheduling into canonical P0 while basic viability/homeostasis remains unresolved.

BOUNDARIES
Do not modify Wingless, ckb-plane, or Mind-Palace without explicit authorization.
Do not activate CKB runtime, Coinbase/live broker systems, TradeGuard, deployment/promotion, or external execution authority.
P0 remains morphology/developmental-substrate research and does not establish cognition or general intelligence.

NEXT ACTION
Research and preregister one discriminating STAB-12 formation-stage occupancy-setpoint mechanism.
Do not execute it before preregistration.
