TITLE: DG-1 Current Research Status
DATE: 2026-09-17
STATUS: ACTIVE — DG-1A P0 STAB-14 CLOSED NEGATIVE / STAB-15 DESIGN
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
176 passed
0 failed

STAB-14 scientific source:
81d70262fe2f3e66d83def3fa800fdef90f3fea0

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

STAB-14 BALANCED-HARD-ALLOC + CEIL-800 + ATTRACT-16:
CLOSED NEGATIVE / SPATIAL-ALLOCATION REGRESSION.
- scientific source: 81d70262fe2f3e66d83def3fa800fdef90f3fea0;
- regression: 176 passed / 0 failed;
- pre-damage active: 1097;
- persistence: 1014 -> peak 1477 -> 1112;
- drift: +98;
- final recovery active: 1078;
- DamageEffect: negative;
- pre-lesion MSE: 0.0587935299;
- final persistence MSE: 0.0712424740;
- support FP rate at final training record: 0.6946872473;
- support FN rate: 0.0077433628;
- target TP cells mean: 112.125 / 113;
- 11 / 14 gates failed.

STAB-14 INTERPRETATION
Exact hard living-support equality with the visible target mask is not the missing solution.
The allocation loss strongly protected target foreground but allowed large redundant exterior living support and destroyed the STAB-12 near-bound regime.

This closes hard target-mask overlap as the current direction.
Do not tune FP/FN weights, allocation coefficient, threshold, temporal scope, CEIL-800, or ATTRACT-16 after observing this result.

Return to STAB-12 as the useful baseline.
The unresolved seam is now morphologically useful support representation: auxiliary living support may be legitimate, but redundant exterior support must be distinguishable from target-critical or functionally coupled support.

NEXT BOUNDED PACKET
DG-1A-P0-STAB-15 — DESIGN / PREREGISTRATION ONLY.

Preferred seam:
a morphology-aware support-usefulness mechanism using the STAB-12 baseline that can retain useful auxiliary living cells without rewarding redundant exterior support.

The STAB-15 mechanism must:
- avoid another raw-cardinality extension;
- avoid exact hard visible-target mask equality;
- preserve CEIL-800 and ATTRACT-16 unchanged unless explicitly superseded;
- remain one fixed preregistered mechanism.

FIBONACCI TRACK
DG-1A-FIB1 remains separate.
Do not introduce Fibonacci scheduling into canonical P0 while basic viability/homeostasis remains unresolved.

BOUNDARIES
Do not modify Wingless, ckb-plane, or Mind-Palace without explicit authorization.
Do not activate CKB runtime, Coinbase/live broker systems, TradeGuard, deployment/promotion, or external execution authority.
P0 remains morphology/developmental-substrate research and does not establish cognition or general intelligence.

NEXT ACTION
Research and preregister one discriminating STAB-15 morphologically useful-support mechanism.
Do not execute it before preregistration.
