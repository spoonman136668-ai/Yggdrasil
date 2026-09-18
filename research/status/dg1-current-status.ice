TITLE: DG-1 Current Research Status
DATE: 2026-09-17
STATUS: ACTIVE — DG-1A P0 STAB-17 CLOSED NEGATIVE / STAB-18 DESIGN
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
226 passed
0 failed

STAB-17 scientific source:
23263694d9bd2188d7c6bc40fdc2a920754901e2

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

STAB-15 LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16:
CLOSED NEGATIVE / HIDDEN-LIFE COLLAPSE.
- scientific source: 5e3d52602ff38fbc2285cff9d495b79cfeb5826e;
- regression: 192 passed / 0 failed;
- pre-damage hidden-life cells: 1;
- persistence: 1 -> peak 1 -> 0;
- final recovery hidden-life cells: 0;
- pre-lesion visible MSE: 0.0272321105;
- foreground training MSE: 0.4064190388;
- RelativeDamageEffect: 0.0095902033;
- stable T50: not attained;
- ATTRACT mature samples: 0 / 8;
- 6 / 14 gates failed.

STAB-15 INTERPRETATION
Moving liveness to hidden channel 4 cleanly removed visible-alpha/liveness coupling, but the unchanged objective contained no positive incentive to maintain hidden life.

The life channel never reached the 113-cell maturity floor, so ATTRACT-16 never activated.
CEIL-800 was always inactive because life was far below its upper bound.
The system returned to the sparse-target blank-output pathology: low global visible MSE with very poor target-foreground morphology and no viable organism.

Do not tune hidden L2, seed visible alpha, lower maturity, or add a direct life target inside STAB-15.

The unresolved seam is now explicit:
POSITIVE VIABILITY-TO-MORPHOLOGY COUPLING FOR DECOUPLED LIFE.

STAB-16 FRONTIER-FLOOR-113 + LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16:
CLOSED NEGATIVE / VIABILITY RESTORED, MORPHOLOGY COUPLING UNRESOLVED.
- scientific source: 986e3953365a2aa47682a3147cc6ae56a64c9485;
- regression: 209 passed / 0 failed;
- pre-damage hidden-life cells: 1082;
- final recovery hidden-life cells: 797;
- persistence: 1047 -> peak 1049 -> 750;
- drift: -297;
- pre-lesion visible MSE: 0.0673088878;
- final persistence visible MSE: 0.0488450378;
- DamageEffect: negative;
- RelativeDamageEffect: -0.0768766287;
- stable T50: not attained;
- 8 / 14 gates failed.

STAB-16 INTERPRETATION
The local 113-cell viability floor solved STAB-15 hidden-life collapse without forcing hidden life to equal visible target geometry.
Hidden life became sustained and ATTRACT-16 remained active.

However, canonical formation still overgrew and lesion damage improved visible morphology, showing that much of the viable latent support remains redundant or negatively coupled to the phenotype.

The unresolved seam is now:
FUNCTIONAL COUPLING BETWEEN LATENT SUPPORT AND VISIBLE MORPHOLOGY.

STAB-12 remains the best overall phenotype by gate count.
STAB-16 establishes the architectural viability of decoupled hidden life with a minimal local survival signal.

STAB-17 MATURE-VIS-ANCHOR-R1 + FRONTIER-FLOOR-113 + LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16:
CLOSED NEGATIVE / LOCAL VISIBLE PROXIMITY MOSTLY ALREADY SATISFIED.
- scientific source: 23263694d9bd2188d7c6bc40fdc2a920754901e2;
- regression: 226 passed / 0 failed;
- pre-damage hidden-life cells: 1038;
- final recovery hidden-life cells: 681;
- persistence: 919 -> peak 1043 -> 690;
- drift: -229;
- pre-lesion visible MSE: 0.0655461326;
- final persistence visible MSE: 0.0668581352;
- DamageEffect: negative;
- RelativeDamageEffect: -0.1224298101;
- stable T50: not attained;
- 8 / 14 gates failed.

STAB-17 INTERPRETATION
The R1 mature visible anchor was zero or near-zero through most mature training checkpoints.
Hidden life was therefore already locally co-located with visible alpha, yet canonical morphology and lesion salience remained poor.

This falsifies simple local visible proximity as the missing latent-support coupling mechanism.

The unresolved seam is now:
CAUSAL CONTRIBUTION OF LATENT SUPPORT TO VISIBLE MORPHOLOGY.

STAB-12 remains the best overall phenotype by gate count.
STAB-16 remains the architectural proof that decoupled hidden life can be kept viable without exact target-mask equality.
STAB-17 shows proximity is not enough.

NEXT BOUNDED PACKET
DG-1A-P0-STAB-18 — DESIGN / PREREGISTRATION ONLY.

Preferred seam:
a causal-contribution mechanism that distinguishes useful hidden support from redundant support by measurable effect on visible morphology, without target-mask equality or raw count pressure.

The STAB-18 mechanism must:
- not simply reduce or remove hidden L2;
- not directly force hidden life to equal the visible target mask;
- not lower the 113 viability floor or 800 ceiling;
- preserve one fixed preregistered construction.

FIBONACCI TRACK
DG-1A-FIB1 remains separate.
Do not introduce Fibonacci scheduling into canonical P0 while basic viability/homeostasis remains unresolved.

BOUNDARIES
Do not modify Wingless, ckb-plane, or Mind-Palace without explicit authorization.
Do not activate CKB runtime, Coinbase/live broker systems, TradeGuard, deployment/promotion, or external execution authority.
P0 remains morphology/developmental-substrate research and does not establish cognition or general intelligence.

NEXT ACTION
Research and preregister one discriminating STAB-18 causal-contribution mechanism for latent support.
Do not execute it before preregistration.
