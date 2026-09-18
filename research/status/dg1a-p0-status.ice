TITLE: DG-1A-P0 Current Status
DATE: 2026-09-17
STATUS: ACTIVE — STAB-15 CLOSED NEGATIVE / STAB-16 DESIGN NOT YET PREREGISTERED
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; MEASURED_SANDBOX FOR CANONICAL EXPERIMENTS

BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
03c01f658361ca1a80cd72afb284b563e0d223ae

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
- ATTRACT-16 fixed 16-step future target-state supervision;
- CEIL-800 formation-stage hard occupancy ceiling with restricted straight-through gradient;\n- TRACE-CEIL-800 trajectory-wide occupancy-pressure negative control;
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
11. global_plus_foreground_bg_alpha_attractor_t16_ceil800\n12. global_plus_foreground_bg_alpha_attractor_t16_ceil800_traceceil800
13. global_plus_foreground_bg_alpha_attractor_t16_ceil800_alloc_balanced_hard
14. global_plus_foreground_bg_alpha_attractor_t16_life4_ceil800

LATEST TEST STATUS
STAB-15 reconstructed sandbox regression:
192 passed
0 failed

Environment:
Python 3.13.5
PyTorch 2.10.0+cpu

STAB-15 scientific source revision:
5e3d52602ff38fbc2285cff9d495b79cfeb5826e

source_revision_verified_checkout = false
sandbox_source_byte_identity = false
evidence_class = MEASURED_SANDBOX

SCIENTIFIC FRONTIER
Full-grid 40 x 40 canonical stabilization remains unresolved but substantially narrowed.

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
Broad threshold-aligned alive-margin pressure crossed the bracket into near-death.

STAB-07
CLOSED NEGATIVE.
Binary one-cell target-support exemption restored viability but remained overgrown.

STAB-08
CLOSED NEGATIVE.
Static graded target-distance weighting worsened mature overgrowth.

STAB-09 — HOME-1
CLOSED NEGATIVE.
One mature-only virtual step improved nominal snapshot but persistence expanded strongly:
941 -> 1406 active; drift +465.

STAB-10 — HOME-T16
CLOSED NEGATIVE.
Sixteen-step local velocity control did not create a bounded target attractor:
1360 -> 1353 active; peak 1501; pre-damage active 1407.

STAB-11 — ATTRACT-16
CLOSED NEGATIVE WITH IMPORTANT DIRECTIONAL ATTRACTOR SIGNAL.
Direct future target-state supervision materially changed long-horizon dynamics:
- pre-damage active: 1252;
- persistence active: 1160 -> 592;
- persistence peak: 1335;
- persistence drift: -568;
- persistence MSE: 0.0616273582 -> 0.0547853708;
- lesion invalid;
- 9 / 14 gates failed.

Interpretation:
trajectory-level target supervision is directionally superior to local velocity suppression, but formation entered persistence severely overgrown.

STAB-12 — CEIL-800 + ATTRACT-16
CLOSED NEGATIVE WITH MAJOR NARROWING RESULT.

Exactly one fresh seed-0 candidate completed 200 / 200 iterations.

Measured training:
- final global morphology MSE: 0.0345974788;
- final ATTRACT-16 trajectory loss: 0.2073710412;
- final CEIL-800 loss: 0.0;
- final batch mean active: 588.375;
- final batch max active: 780;
- mature samples: 8 / 8;
- no non-finite state.

Measured growth/recovery:
- pre-damage active: 857;
- post-damage active: 435;
- final recovery active: 655;
- pre-lesion MSE: 0.0456747562;
- post-lesion MSE: 0.0457243808;
- final recovery MSE: 0.0318049565;
- DamageEffect: +0.0000496246;
- RelativeDamageEffect: 0.0010864774;
- active-cell removal: 49.24%;
- RecoveryFraction: 1.0;
- stable T50/T90: 59 / 59.

Measured persistence:
- initial active: 799;
- peak active: 1015;
- final active: 623;
- active drift: -176;
- initial MSE: 0.0444691367;
- maximum MSE: 0.0736930072;
- final MSE: 0.0434814841.

Preregistered gates:
5 / 14 failed.

Failed:
- pre-damage active <=800;
- maximum persistence active <=800;
- RelativeDamageEffect >=0.10;
- pre-lesion MSE <=0.0361635;
- final persistence MSE <=0.0361635.

Passed:
- final recovery occupancy;
- final persistence occupancy;
- negative persistence drift;
- positive DamageEffect;
- active-cell removal;
- stable T50;
- bounded RecoveryFraction;
- maximum persistence MSE ratio;
- finite-state gate.

Candidate worth widening:
NO.

STAB-12 INTERPRETATION
CEIL-800 materially reduced formation overgrowth while preserving the useful ATTRACT-16 contraction.

Key progression:
STAB-11 pre-damage active 1252 -> STAB-12 857.
STAB-11 persistence initial 1160 -> STAB-12 799.
STAB-12 persistence final 623.
STAB-12 recovery final 655.
Lesion DamageEffect changed from negative to positive.

The canonical failure is no longer gross unbounded occupancy.

The remaining defect is:
TRANSIENT SUPPORT OVERSHOOT + INSUFFICIENT TARGET MORPHOLOGY / LESION SALIENCE.

Persistence begins in the accepted occupancy window, overshoots to 1015, then contracts to 623.
Morphology error rises during that overshoot and finishes above the frozen threshold.
The lesion removes nearly half the living support but changes morphology by only ~0.1%, indicating too much living support remains morphologically redundant or poorly allocated.

CURRENT MECHANISTIC BRACKET
1. sparse endpoint objectives can collapse to death;
2. foreground preservation can create overgrowth;
3. continuous occupancy pressure is useful but insufficient;
4. broad near-threshold pressure can kill viability;
5. static spatial support geometry alone is insufficient;
6. local velocity control is insufficient;
7. future target-state supervision can reverse long-horizon expansion;
8. one-sided formation occupancy control can nearly bound formation without destroying viability;
9. remaining failure is transient support allocation and morphology concentration, not simply endpoint count.

DURABLE STAB-12 RECORDS
research/experiments/dg1a/dg1a-p0-stab12-spec.ice
research/experiments/dg1a/dg1a-p0-stab12-result.ice
evidence/dg1a/p0_stab12_sandbox.json

CURRENT DECISIONS
- close STAB-12 as negative;
- do not widen CEIL-800;
- do not lower the 800 ceiling;
- do not increase CEIL-800 coefficient;
- do not change its STE mask;
- do not alter ATTRACT-16 horizon/coefficient/reduction;
- preserve all eleven historical modes;
- preserve viability floor 113 and occupancy ceiling 800;
- preserve persistence, lesion-validity, morphology, recovery, and finite-state gates;
- retain global visible morphology MSE as common evaluation metric;
- canonical full-grid P0 remains unresolved;
- do not begin DG-1B;
- do not introduce Fibonacci scheduling into canonical P0.

STAB-13 — TRACE-CEIL-800 + CEIL-800 + ATTRACT-16
CLOSED NEGATIVE / CLEAR REGRESSION.

Scientific source:
422b8eec20f8089a40bb83b66f8452e0bf1b525e

Regression:
163 passed
0 failed

Measured result:
- pre-damage active: 1193;
- final recovery active: 1439;
- persistence active: 1130 -> 1456;
- persistence peak: 1517;
- persistence drift: +326;
- pre-lesion MSE: 0.0645737201;
- final persistence MSE: 0.0938185528;
- DamageEffect: -0.0084298588;
- RelativeDamageEffect: -0.1305462783;
- stable T50: not attained;
- 11 / 14 gates failed.

Interpretation:
extending the exact same raw CEIL-800 pressure across ATTRACT-16's future trajectory destabilized the STAB-12 near-bound regime rather than suppressing transient overshoot.

STAB-13 therefore closes the raw-cardinality temporal-scope family:
- do not lengthen TRACE-CEIL;
- do not lower its ceiling;
- do not increase its coefficient;
- do not use max reduction as a post-result variant;
- do not alter the STE mask;
- do not weaken gates.

Return to STAB-12 as the useful directional baseline.

The unresolved seam is spatial / morphological allocation of living support, not more raw active-cell count pressure.

DURABLE STAB-13 RECORDS
research/experiments/dg1a/dg1a-p0-stab13-spec.ice
research/experiments/dg1a/dg1a-p0-stab13-result.ice
evidence/dg1a/p0_stab13_sandbox.json

STAB-14 — BALANCED-HARD-ALLOC + CEIL-800 + ATTRACT-16
CLOSED NEGATIVE / SPATIAL-ALLOCATION REGRESSION.

Scientific source:
81d70262fe2f3e66d83def3fa800fdef90f3fea0

Regression:
176 passed
0 failed

Measured training endpoint:
- global morphology MSE: 0.0589801818;
- support allocation loss: 0.3512153029;
- false-positive support rate: 0.6946872473;
- false-negative support rate: 0.0077433628;
- target true-positive cells mean: 112.125 / 113;
- batch mean active: 1145.125;
- batch max active: 1331.

Measured growth/recovery:
- pre-damage active: 1097;
- final recovery active: 1078;
- pre-lesion MSE: 0.0587935299;
- DamageEffect: -0.0050131604;
- RelativeDamageEffect: -0.0852672125;
- stable T50: not attained.

Measured persistence:
- initial active: 1014;
- peak active: 1477;
- final active: 1112;
- drift: +98;
- initial MSE: 0.0554905981;
- final MSE: 0.0712424740.

Preregistered gates:
11 / 14 failed.

Interpretation:
the hard target-mask allocation loss nearly saturated target foreground but tolerated widespread false-positive living support. The class-normalized 0.5 / 0.5 straight-through construction gives each missed foreground cell much greater gradient magnitude than each extra background cell because the foreground class is much smaller. The observed model repeatedly traded FP against FN and finished in a high-FP overgrown state.

This closes exact hard visible-target support equality as the current direction.

Do not:
- tune FP/FN weights;
- tune allocation coefficient;
- change alpha threshold;
- move BALANCED-HARD-ALLOC onto future ATTRACT states;
- tighten CEIL-800;
- alter ATTRACT-16;
- weaken gates.

Return to STAB-12 as the useful directional baseline.

The unresolved seam is now:
MORPHOLOGICALLY USEFUL SUPPORT REPRESENTATION.

A future mechanism must distinguish:
- visible target-critical structure;
- potentially useful hidden/auxiliary living support;
- redundant exterior living support.

It must not assume that every alive cell belongs exactly on the visible target mask.

DURABLE STAB-14 RECORDS
research/experiments/dg1a/dg1a-p0-stab14-spec.ice
research/experiments/dg1a/dg1a-p0-stab14-result.ice
evidence/dg1a/p0_stab14_sandbox.json

STAB-15 — LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16
CLOSED NEGATIVE / HIDDEN-LIFE COLLAPSE.

Scientific source:
5e3d52602ff38fbc2285cff9d495b79cfeb5826e

Regression:
192 passed
0 failed

Measured training endpoint:
- global visible MSE: 0.0287033431;
- foreground morphology MSE: 0.4064190388;
- ATTRACT mature samples: 0 / 8;
- hidden-life batch mean: 0.375;
- hidden-life batch max: 1;
- CEIL-800 loss: 0.0.

Measured growth/recovery:
- pre-damage hidden-life cells: 1;
- post-damage hidden-life cells: 0;
- final recovery hidden-life cells: 0;
- pre-lesion visible MSE: 0.0272321105;
- DamageEffect: +0.0002611615;
- RelativeDamageEffect: 0.0095902033;
- RecoveryFraction: 0.0;
- stable T50: not attained.

Measured persistence:
- initial hidden-life cells: 1;
- peak hidden-life cells: 1;
- final hidden-life cells: 0;
- drift: -1;
- initial visible MSE: 0.0272324514;
- final visible MSE: 0.0295742173.

Preregistered gates:
6 / 14 failed.

Interpretation:
decoupling liveness from visible alpha removed incidental survival pressure. Under visible-only morphology supervision, unchanged hidden L2, an upper-bound-only CEIL term, and mature-only ATTRACT, hidden life never reached the 113-cell maturity floor and repeatedly collapsed to seed/dead occupancy.

The low global visible MSE is the sparse-target blank-output pathology, not a viable morphology success. Foreground morphology MSE remained ~0.406.

This establishes:
- visible-alpha/liveness conflation is not itself the complete solution;
- a dedicated hidden-life channel is architecturally possible but needs positive viability-to-morphology coupling;
- an upper bound cannot create missing life;
- mature-only ATTRACT cannot help if life never reaches maturity.

Do not:
- exempt LIFE4 from hidden L2 after observing this result;
- reduce hidden L2;
- seed visible alpha as a rescue;
- add a direct hidden-life target mask inside STAB-15;
- lower maturity threshold;
- weaken viability gates.

DURABLE STAB-15 RECORDS
research/experiments/dg1a/dg1a-p0-stab15-spec.ice
research/experiments/dg1a/dg1a-p0-stab15-result.ice
evidence/dg1a/p0_stab15_sandbox.json

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-16 — DESIGN / PREREGISTRATION ONLY.

Preferred research seam:
a positive viability-to-morphology coupling for decoupled life that prevents hidden-life collapse without forcing life to equal the visible target mask and without merely tuning hidden L2 or the 800-cell ceiling.

No STAB-16 mechanism is selected by this status record.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling from this packet.

NEXT ACTION
Research and preregister one discriminating STAB-16 positive viability-to-morphology coupling mechanism.
Do not execute it before exact mechanism and gates exist in .ice.
