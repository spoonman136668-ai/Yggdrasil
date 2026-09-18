TITLE: DG-1A-P0 Current Status
DATE: 2026-09-18
STATUS: ACTIVE — STAB-18 CLOSED UNEXECUTED / STAB-18-R1 PREREGISTERED + IMPLEMENTED / ACCEPTANCE IN PROGRESS
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; MEASURED_SANDBOX FOR CANONICAL EXPERIMENTS

BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
771235595b19602fa61189f3bf2b9d2fca1c63cf

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
15. global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800
16. global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_visanchor_r1

LATEST TEST STATUS
STAB-17 reconstructed sandbox regression:
226 passed
0 failed

Environment:
Python 3.13.5
PyTorch 2.10.0+cpu

STAB-17 scientific source revision:
23263694d9bd2188d7c6bc40fdc2a920754901e2

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

STAB-16 — FRONTIER-FLOOR-113 + LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16
CLOSED NEGATIVE / VIABILITY RESTORED, MORPHOLOGY COUPLING UNRESOLVED.

Scientific source:
986e3953365a2aa47682a3147cc6ae56a64c9485

Regression:
209 passed
0 failed

Measured result:
- pre-damage hidden-life cells: 1082;
- final recovery hidden-life cells: 797;
- persistence: 1047 -> peak 1049 -> 750;
- drift: -297;
- pre-lesion visible MSE: 0.0673088878;
- final persistence visible MSE: 0.0488450378;
- DamageEffect: -0.0051744804;
- RelativeDamageEffect: -0.0768766287;
- active-cell removal: 26.52%;
- stable T50: not attained;
- 8 / 14 gates failed.

Mechanistic result:
FRONTIER-FLOOR-113 eliminated STAB-15 hidden-life collapse without specifying a target life mask. Hidden life repeatedly entered the 113..800 deadband and ATTRACT-16 remained active. However, formation still entered evaluation overgrown, and lesion damage improved visible morphology instead of degrading it.

This establishes that decoupled hidden liveness can be viable with a minimal local survival signal, but latent support remains insufficiently coupled to useful visible morphology.

Do not tune:
- viability floor 113;
- frontier radius or definition;
- floor coefficient;
- CEIL-800;
- hidden L2;
- ATTRACT-16;
- life threshold;
- scientific gates.

Return references:
- STAB-12 remains the best overall canonical phenotype by gate count;
- STAB-16 is the strongest evidence that hidden liveness can be sustained without exact target-mask equality.

DURABLE STAB-16 RECORDS
research/experiments/dg1a/dg1a-p0-stab16-spec.ice
research/experiments/dg1a/dg1a-p0-stab16-result.ice
evidence/dg1a/p0_stab16_sandbox.json

STAB-17 — MATURE-VIS-ANCHOR-R1 + FRONTIER-FLOOR-113 + LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16
CLOSED NEGATIVE / LOCAL VISIBLE PROXIMITY MOSTLY ALREADY SATISFIED.

Scientific source:
23263694d9bd2188d7c6bc40fdc2a920754901e2

Regression:
226 passed
0 failed

Measured result:
- pre-damage hidden-life cells: 1038;
- final recovery hidden-life cells: 681;
- persistence: 919 -> peak 1043 -> 690;
- drift: -229;
- pre-lesion visible MSE: 0.0655461326;
- final persistence visible MSE: 0.0668581352;
- DamageEffect: -0.0080248006;
- RelativeDamageEffect: -0.1224298101;
- active-cell removal: 37.38%;
- stable T50: not attained;
- 8 / 14 gates failed.

Mechanistic result:
MATURE-VIS-ANCHOR-R1 was zero or near-zero for most mature checkpoints. Hidden life was already locally adjacent to current visible alpha, yet formation remained overgrown, lesion damage improved visible morphology, and morphology/recovery gates remained failed.

This falsifies simple R1 spatial proximity as the dominant latent-support usefulness seam.

Do not tune:
- anchor radius;
- anchor coefficient;
- visible threshold;
- anchor temporal scope;
- target-mask anchoring;
- FRONTIER-FLOOR-113;
- CEIL-800;
- hidden L2;
- ATTRACT-16;
- scientific gates.

Return references:
- STAB-12 remains the best overall canonical phenotype by gate count;
- STAB-16 remains the strongest evidence that decoupled hidden liveness can be sustained without exact target-mask equality;
- STAB-17 shows that geometric proximity to visible alpha is not sufficient evidence of functional usefulness.

DURABLE STAB-17 RECORDS
research/experiments/dg1a/dg1a-p0-stab17-spec.ice
research/experiments/dg1a/dg1a-p0-stab17-result.ice
evidence/dg1a/p0_stab17_sandbox.json

STAB-18 — ORIGINAL CAUSAL-LATENT-DROPOUT25-PRUNE-T16
CLOSED UNEXECUTED — ACCEPTANCE-DISCOVERED RNG STREAM ALIASING CONFOUND.

Original preregistration:
research/experiments/dg1a/dg1a-p0-stab18-spec.ice
preregistration commit:
e6cb795c0bfa7de96400214bb0978878658368c3

Original frozen implementation source:
1e50388cc4fe0f86ac68e304cca62e7944b7a8bf

The original candidate was never scientifically executed and is not a scientific negative.

Acceptance review found:
- the original probe helper saved the main generator state;
- it sampled torch.rand([B,1,H,W]) for ProbeDrop < 0.25;
- it restored the main generator state;
- the first future NCA step then sampled torch.rand([B,1,H,W]) from that same restored state for fire mask <= 0.50;
- therefore ProbeDrop was necessarily a subset of the first-step fire mask.

Conclusion:
save/restore gave zero durable RNG consumption but did not provide pseudorandom-domain independence.
The original causal measurement was confounded by immediate update-schedule membership.

STAB-18-R1 — CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP
PREREGISTERED / IMPLEMENTED / ACCEPTANCE IN PROGRESS — NOT EXECUTED.

R1 preregistration:
research/experiments/dg1a/dg1a-p0-stab18-r1-spec.ice
commit:
f9e09f36470c1d718c3e30a1a954cd18570b83f2

R1 fixed loss mode:
global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16_domainsep

R1 correction:
- preserve Bernoulli probe fraction 0.25;
- preserve mature-only LIFE4 probe scope;
- preserve T16 matched intact/counterfactual trajectories;
- preserve causal delta classification and one-sided LIFE4 STE prune gradient;
- preserve FRONTIER-FLOOR-113, CEIL-800, ATTRACT-16, hidden L2, canonical envelope, and all 14 gates;
- derive a temporary probe-generator seed as SHA256(main_generator_state_bytes || fixed domain tag);
- use first 8 digest bytes unsigned big-endian, masked to 63 bits;
- never sample the probe from the main trajectory generator;
- discard the temporary probe generator after mask generation.

Fixed domain tag:
DG1A_P0_STAB18_R1_CAUSAL_PROBE_V1

Reference seed contract:
main torch.Generator manual_seed(1)
=> probe seed 3494006018084941813

Runtime-equivalent reference check completed:
- 9 x 9 all-live LIFE4 fixture;
- 14 cells selected by R1 probe;
- 7 selected probe cells have first-main-stream random value > 0.50;
- R1 probe is not equal to first-main-stream < 0.25;
- main generator state unchanged;
- same main generator state reproduces same mask;
- different main generator state changes mask.

R1 implementation commits:
- normal training: 26b319443f43cf10a08f4185c782e28e87de5002
- normal branch join repair: b7bda76423822935b04cf01b418027f226e45bba
- resumable parity: de0d8e24696730c1ce9f2d482ecb1a654c751c5c
- resumable branch join repair: 8fd556f7bd6de4e2fcb34ca31279edca9d23151c
- config allow mode: 84bcbb9eb7fa2e62c9bf43d4b67d298a241d8aed
- frozen R1 YAML: 46c17de13b59d0bac2fb1dd0c1236b43f87a9f75
- R1 contracts: 4265688cda2c5a6f43cd59185881a54512c746a2
- R1 contract import repair: 771235595b19602fa61189f3bf2b9d2fca1c63cf

R1 test surface:
tests/test_stab18_r1_domain_separation.py
20 test functions present.
Executable pytest is not yet claimed because the current sandbox cannot resolve github.com and the reconstructed checkout from the prior sandbox was reset.

Historical acceptance evidence preserved:
- original STAB-18 targeted contracts before discovery: 19 passed / 0 failed;
- core historical regression: 54 passed / 0 failed;
- reconstructed STAB-06: 10 passed / 0 failed;
- reconstructed STAB-07: 10 passed / 0 failed;
- reconstructed STAB-08: 11 passed / 0 failed;
- reconstructed STAB-09: 12 passed / 0 failed;
- reconstructed STAB-10: 11 passed / 0 failed;
- reconstructed STAB-11: 12 passed / 0 failed;
- reconstructed STAB-12: 13 passed / 0 failed;
- reconstructed STAB-13: 15 passed / 0 failed;
- reconstructed STAB-14: 13 passed / 0 failed.

STAB-15 acceptance defect:
The original STAB-15 test helper hard-coded TargetSpec(radius=6) while two tests requested a 9 x 9 target. The radius-fit validator already existed before STAB-15 was introduced, so this was a historical fixture defect rather than a scientific-code regression.

Fixture-only repair:
714cb10bf5963d47b07ecaf8184ea89a179692a5

No assertions were weakened or removed.

Compatibility proof after R1:
- STAB-15 normal/resumable execution branches are byte-identical to original STAB-18 source 1e50388...;
- STAB-16 normal/resumable execution branches are byte-identical;
- STAB-17 normal/resumable execution branches are byte-identical;
- original STAB-18 normal/resumable execution branches are byte-identical;
- R1 is isolated behind a new loss mode.

Acceptance still outstanding before scientific execution:
- executable STAB-04 / STAB-05 replay;
- executable repaired STAB-15 replay;
- executable STAB-16 / STAB-17 replay;
- executable STAB-18-R1 targeted contracts;
- final combined reconstructed regression.

Scientific execution state:
NOT STARTED.
No seed-0 R1 training may begin until the complete executable acceptance surface is green.

NEXT BOUNDED PACKET
DG-1A-P0-STAB-18-R1 — ACCEPTANCE CLOSEOUT, THEN EXACTLY ONE SEED-0 CANONICAL RUN.

Preferred research seam:
causal contribution of latent support to visible morphology under a domain-separated intervention.

The R1 mechanism is frozen by preregistration.
Do not tune it during acceptance or after observing the scientific run.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling from this packet.

NEXT ACTION
Finish the remaining executable historical regression plus STAB-18-R1 contracts with zero failures. If and only if acceptance is fully green, execute exactly one canonical seed-0 STAB-18-R1 200-iteration candidate with no tuning.


RESEARCH-FRONTIER RECONCILIATION — 2026-09-18
This section records post-preregistration research/audit work only.
It does NOT change STAB-18-R1 implementation, scientific source, acceptance requirements, seed budget, or gates.

CURRENT VERIFIED BRANCH HEAD AT RECONCILIATION
4bbc7a835be218b69ac9a93c988608c4751929be

FROZEN STAB-18-R1 SCIENTIFIC IMPLEMENTATION BASIS
e7710a29768ebc852a19796ea42eba4c10629412

CANONICAL R1 STATE
- scientific execution: NOT STARTED;
- single seed-0 / 200-iteration budget: UNSPENT;
- 14 scientific gates: UNCHANGED;
- mandatory historical executable acceptance: STILL OUTSTANDING;
- no post-hoc tuning authorized.

POST-PREREGISTRATION RESEARCH AUDITS
1. CAUSAL CREDIT RESOLUTION
research/experiments/dg1a/dg1a-p0-stab18-r1-credit-resolution-audit.ice
Finding:
the frozen 25% global group probe is scientifically meaningful but coarse; in balanced additive toys it can apply substantial collateral pressure to beneficial cells.

2. LOCAL PROBE RESOLUTION
research/experiments/dg1a/dg1a-p0-stab18-r1-local-probe-resolution-audit.ice
Finding:
if latent causal roles have even modest spatial correlation, small local counterfactual probes can outperform global 25% dropout on both attribution precision and causal-signal magnitude.
This is contingency research only; R1 remains global25.

3. DAMAGE-OCCUPANCY RELATION
research/experiments/dg1a/dg1a-p0-stab18-r1-damage-occupancy-audit.ice
Finding:
across viable STAB-04..17 candidates, mature occupancy and RelativeDamageEffect are strongly negatively associated post hoc.
Severe overgrowth repeatedly predicts lesions that improve morphology.
The relation is descriptive, non-IID, and NON-GATING.

4. INJURY-RECRUITMENT GAP
research/experiments/dg1a/dg1a-p0-stab18-r1-injury-recruitment-audit.ice
Finding:
pre-LIFE4 viable STAB-07..14 candidates restored a median ~92% of lesion-removed active population, whereas STAB-16/17 restored ~0.7% / ~8.0%.
The gap survives a basic post-lesion occupancy-matching control.

5. LIFE4 GRADIENT-TOPOLOGY AUDIT
research/experiments/dg1a/dg1a-p0-stab18-r1-life4-gradient-topology-audit.ice
Finding:
LIFE4 decoupling removes the direct visible-alpha/liveness gradient bridge.
FRONTIER-FLOOR-113 restores baseline viability but supplies no positive frontier gradient while LIFE4 count remains >=113.
R1 adds additional explicit downward causal pressure but no injury-conditioned upward recruitment signal.

6. TEMPORAL WOUND-SIGNAL FEASIBILITY
research/experiments/dg1a/dg1a-p0-stab18-r1-temporal-wound-signal-audit.ice
Finding:
current binary LIFE4 geometry cannot reliably distinguish acute internal wound boundary from stable exterior boundary; one-step temporal support information can.
Canonical synthetic wounds are locally detectable and spatially traversable within the existing rollout horizon.

7. ACTUAL-PERCEPTION WOUND-MEMORY POC
research/experiments/dg1a/dg1a-p0-stab18-r1-wound-memory-perception-poc.ice
Finding:
the existing identity/Sobel NCA perception plus a small local MLP is sufficient to decode a synthetic temporal support-memory cue without increasing state width or receptive field.

8. RECURRENT REPAIR ROLLOUT POC
research/experiments/dg1a/dg1a-p0-stab18-r1-wound-memory-repair-rollout-poc.ice
Finding:
a clean held-out synthetic wound can be filled layer-by-layer with zero outward growth, but ungated memory propagation becomes unstable under small maintenance turnover.
A distinct injury-licensing stage is therefore required.

9. WOUND-MEMORY ROBUSTNESS BOUNDARY
research/experiments/dg1a/dg1a-p0-stab18-r1-wound-memory-robustness-audit.ice
Finding:
persistent structured analog memory noise can trigger rare catastrophic or frequent false repair cascades.
Spatial consensus helps but is insufficient at stronger persistent noise.
Raw wound memory is NOT ready to become a candidate.

10. SPATIOTEMPORAL INJURY-GATE AUDIT
research/experiments/dg1a/dg1a-p0-stab18-r1-spatiotemporal-injury-gate-audit.ice
Finding:
time persistence + local cluster agreement suppress moderate noise but cannot reliably separate highly persistent structured noise without large wound-recall loss.
Do not ratchet threshold/persistence/component parameters.

11. REDUNDANT INJURY-CUE RELIABILITY
research/experiments/dg1a/dg1a-p0-stab18-r1-redundant-injury-cue-audit.ice
Finding:
multiple overlapping injury cues can sharply reduce false decisions only when their error modes retain meaningful independence.
Raw duplicated channels with highly correlated noise give little reliability gain.
This yields a testable Yggdrasil hypothesis for repair-associated redundancy.

12. REPAIR-SIGNAL LIFETIME GEOMETRY NEGATIVE
research/experiments/dg1a/dg1a-p0-stab18-r1-repair-signal-lifetime-geometry-audit.ice
Finding:
for the canonical 35% central lesion across tested 113..797-cell disk bodies, a simple isotropic repair wave can reach the ordinary exterior before it reaches the deepest wound cell.
Signal TTL/decay alone therefore cannot guarantee inward repair without outward growth.
Propagation and LIFE4 recruitment must remain contextually distinct.

13. OOD GEOMETRY GENERALIZATION
research/experiments/dg1a/dg1a-p0-stab18-r1-wound-cue-geometry-generalization-audit.ice
Finding:
a temporal classifier trained only on disks generalized strongly across 140 lesions on ellipse/rectangle/cross/dumbbell/crescent/annulus/C-shape morphologies, including stable internal cavities.
Hard concave/large-wound cases remain incomplete, supporting richer learned predictive state rather than a single scalar memory cue.

14. AUXILIARY LATENT INJURY DIAGNOSTIC PREREGISTRATION
research/experiments/dg1a/dg1a-p0-stab18-r1-latent-injury-diagnostic-spec.ice
Finding:
a non-gating post-R1 observational protocol is now frozen before the R1 result exists.
It measures per-channel injury discriminability, pooled ensemble gain, hidden noise covariance/effective dimension, spatial lesion response, LIFE4/alpha turnover, and maintenance-to-recovery regime changes.
The synthetic validation explicitly prevents covariance/effective-rank alone from being misread as redundant injury information.

CURRENT CONTINGENCY MODEL
The post-R1 research branch is now decomposed into three control problems:

A. MAINTENANCE ECONOMY
retain causally useful latent support and suppress redundant/harmful bulk.
STAB-18-R1 is the frozen canonical test of this seam.

B. INJURY-STATE INFERENCE
if repair remains absent after useful maintenance is established, infer acute damage from robust local multi-cue predictive error rather than absolute population count or one noisy memory scalar.

C. REPAIR RECRUITMENT / TERMINATION
communicate injury through transient local state while licensing LIFE4 recruitment contextually toward missing internal support, then return toward economical maintenance.
Signal propagation must not be equated with unrestricted growth.

RESEARCH STOPPING RULE
Do NOT implement a new repair mechanism before R1 is resolved.
The contingency work exists to reduce post-R1 search entropy, not to bypass the frozen experiment.

NEXT CANONICAL ACTION REMAINS UNCHANGED
Finish mandatory executable historical acceptance with zero failures.
If and only if acceptance is fully green:
execute exactly one seed-0 STAB-18-R1 candidate,
apply all 14 gates,
then execute the already-preregistered non-gating latent diagnostic on the saved checkpoint.
