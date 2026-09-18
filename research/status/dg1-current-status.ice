TITLE: DG-1 Current Research Status
DATE: 2026-09-17
STATUS: ACTIVE — DG-1A P0 STAB-13 CLOSED NEGATIVE / STAB-14 DESIGN
TRACK: DG-1
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; MEASURED_SANDBOX FOR CANONICAL EXPERIMENTS

PURPOSE
Maintain the durable operator-readable DG-1 research frontier.
This status is not an execution authority.

ACTIVE BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
493073a538c108668e6ac7ea90456d981232c440

CURRENT OBJECTIVE
Establish a viable canonical DG-1A developmental substrate that:
- grows meaningful target morphology;
- maintains bounded support;
- enters a stable long-horizon homeostatic attractor;
- suffers meaningful damage;
- exhibits measurable stable repair;
before DG-1B functional computation is opened.

LATEST RECONSTRUCTED TEST STATUS
148 passed
0 failed

STAB-12 scientific source:
19c758e7d006b3a4da46ee5d5c15ce01acf5fba4

source_revision_verified_checkout = false
sandbox_source_byte_identity = false
evidence_class = MEASURED_SANDBOX

CURRENT FULL-GRID FINDINGS
STAB-01 through STAB-08 established the death/overgrowth bracket and showed that endpoint/static occupancy geometry alone is insufficient.

STAB-09 HOME-1:
local one-step homeostasis improved the nominal snapshot but persistence expanded strongly.

STAB-10 HOME-T16:
extending the same local velocity signal to 16 virtual steps produced only slight net contraction around a severely overgrown phenotype.

STAB-11 ATTRACT-16:
direct future target-state supervision materially changed the attractor:
- pre-damage active 1252;
- persistence 1160 -> 592;
- drift -568;
- lesion still invalid;
- 9 / 14 gates failed.

STAB-12 CEIL-800 + ATTRACT-16:
adding one-sided formation occupancy control materially narrowed the remaining defect:
- pre-damage active: 857;
- final recovery active: 655;
- persistence: 799 -> peak 1015 -> 623;
- drift: -176;
- pre-lesion MSE: 0.0456747562;
- final persistence MSE: 0.0434814841;
- DamageEffect: positive;
- RelativeDamageEffect: 0.0010864774;
- active removal: 49.24%;
- stable T50: 59;
- RecoveryFraction: 1.0;
- 5 / 14 gates failed.

STAB-12 INTERPRETATION
The canonical P0 problem has narrowed from gross unbounded support to:
TRANSIENT SUPPORT OVERSHOOT + INSUFFICIENT TARGET MORPHOLOGY / LESION SALIENCE.

The strongest observations are:
- formation is only 57 cells above the accepted ceiling at the canonical pre-damage snapshot;
- persistence begins inside the accepted occupancy window at 799;
- persistence transiently expands to 1015 before contracting to 623;
- morphology error rises with the transient expansion;
- removing nearly half the living support barely changes morphology.

This indicates excess living support is still too morphologically redundant or allocated outside the target-critical structure.

CURRENT DECISIONS
- STAB-12 closed negative;
- do not widen/tune CEIL-800;
- do not lower the 800 ceiling;
- do not change the CEIL straight-through mask;
- preserve ATTRACT-16 unchanged unless a future preregistered packet explicitly tests a new architecture;
- preserve all historical modes and all scientific gates;
- canonical full-grid P0 remains unresolved;
- DG-1B remains unopened.

STAB-13 TRACE-CEIL-800 + CEIL-800 + ATTRACT-16:
CLOSED NEGATIVE / CLEAR REGRESSION.
- scientific source: 422b8eec20f8089a40bb83b66f8452e0bf1b525e;
- regression: 163 passed / 0 failed;
- pre-damage active: 1193;
- persistence: 1130 -> peak 1517 -> 1456;
- drift: +326;
- final recovery active: 1439;
- DamageEffect: negative;
- pre-lesion MSE: 0.0645737201;
- final persistence MSE: 0.0938185528;
- 11 / 14 gates failed.

STAB-13 INTERPRETATION
Applying the existing 800-cell ceiling across ATTRACT-16's whole future trajectory did not remove transient overshoot.
It destroyed the near-bound STAB-12 regime and returned gross overgrowth, invalid lesion response, and failed recovery.

This closes repeated raw-cardinality pressure as the current direction.
Do not tune TRACE-CEIL horizon, ceiling, coefficient, reduction, or STE scope.

Return to STAB-12 as the useful directional baseline.
The unresolved seam is spatial/morphological allocation of living support.

NEXT BOUNDED PACKET
DG-1A-P0-STAB-14 — DESIGN / PREREGISTRATION ONLY.

Preferred seam:
spatially target-aligned living-support allocation using the STAB-12 baseline, without tightening the 800-cell ceiling and without more trajectory-wide raw-cardinality pressure.

The STAB-14 mechanism must:
- address transient overshoot rather than only endpoint count;
- distinguish useful target support from redundant living support;
- avoid STAB-06-style blanket threshold suppression;
- avoid post-result tuning of the 800 ceiling;
- remain one fixed preregistered mechanism.

FIBONACCI TRACK
DG-1A-FIB1 remains separate.
Do not introduce Fibonacci scheduling into canonical P0 while basic viability/homeostasis remains unresolved.

BOUNDARIES
Do not modify Wingless, ckb-plane, or Mind-Palace without explicit authorization.
Do not activate CKB runtime, Coinbase/live broker systems, TradeGuard, deployment/promotion, or external execution authority.
P0 remains morphology/developmental-substrate research and does not establish cognition or general intelligence.

NEXT ACTION
Research and preregister one discriminating STAB-14 spatial support-allocation mechanism.
Do not execute it before preregistration.
