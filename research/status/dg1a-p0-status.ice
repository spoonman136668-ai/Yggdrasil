TITLE: DG-1A-P0 Current Status
DATE: 2026-09-17
STATUS: ACTIVE — STAB-09 CLOSED NEGATIVE / STAB-10 DESIGN NOT YET PREREGISTERED
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; EXPLORATORY FOR SANDBOX RESULTS

BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
e61018ed25b44b8f55b31996a4f9fc2477b6824a

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
- target foreground morphology helper;
- target-background alpha energy;
- threshold-aligned alive margin;
- one-cell support halo / far-field geometry;
- immutable target Chebyshev-distance weights;
- graded background alpha energy;
- target-derived homeostasis maturity mask;
- mature-only background-alpha velocity loss;
- RNG-neutral one-step virtual homeostasis probe;
- virtual-probe pool isolation;
- fail-closed config/target-region validation.

HISTORICAL TRAINING MODES
1. global_mse
2. balanced_fg_bg
3. global_plus_foreground
4. global_plus_foreground_bg_alpha
5. global_plus_foreground_bg_alive_margin
6. global_plus_foreground_farfield_bg_alpha
7. global_plus_foreground_graded_bg_alpha
8. global_plus_foreground_bg_alpha_homeostasis

LATEST TEST STATUS
STAB-09 reconstructed sandbox regression:
112 passed
0 failed

Execution groups:
- 106 non-runner tests: PASS, return code 0;
- six subprocess runner-evidence tests: PASS, all return code 0.

Environment:
Python 3.13.5
PyTorch 2.10.0+cpu

STAB-09 execution source revision:
089ea0e6dd3a220ebc2e92e7ef819de24f87d0ef

The source was semantically reconstructed from connected GitHub readbacks.
Native byte-identical checkout was not established.
Treat STAB-09 as MEASURED SANDBOX evidence, not commit-bound confirmatory acceptance.

SCIENTIFIC FRONTIER
Full-grid 40 x 40 canonical stabilization remains unresolved.

STAB-01 / STAB-02
CLOSED NEGATIVE.
Maturity/horizon changes did not stabilize canonical P0; longer development exposed the sparse-target all-dead attractor.

STAB-03 / STAB-04
CLOSED NEGATIVE.
Foreground-emphasized objectives avoided death but produced severe overgrowth and invalid lesions.

STAB-05 — CLOSED NEGATIVE WITH OCCUPANCY SIGNAL
Uniform continuous target-background alpha pressure:
- pre-damage active: 1206;
- pre-lesion MSE: 0.0701904967;
- final recovery active: 1329;
- persistence final active: 1378;
- lesion invalid.

STAB-06 — CLOSED NEGATIVE / NEAR-DEAD SIDE
Threshold-aligned alive-margin pressure:
- pre-damage active: 3;
- final recovery active: 0;
- RecoveryFraction: 0.0.

STAB-07 — CLOSED NEGATIVE / BINARY SUPPORT GEOMETRY
One-cell target-support halo exemption:
- pre-damage active: 1094;
- pre-lesion MSE: 0.0625592172;
- final recovery active: 1232;
- persistence active: 1005 -> 1276;
- lesion invalid.

STAB-08 — CLOSED NEGATIVE / GRADED STATIC SUPPORT GEOMETRY
Immutable target-distance weighting d/(d+1):
- pre-damage active: 1440;
- pre-lesion MSE: 0.1016835570;
- final recovery active: 1095;
- persistence active: 1348 -> 1102;
- lesion invalid.

STAB-09 — CLOSED NEGATIVE / ONE-STEP DYNAMIC HOMEOSTASIS
Candidate: HOME-1

Base static objective:
GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAlphaMSE

Dynamic term:
- rollout sample mature when hard-active count >= immutable target foreground cardinality;
- canonical maturity cardinality = 113;
- mature samples receive exactly one virtual NCA step;
- main RNG state is restored after probe;
- probe is never written into state pool;
- positive target-background alpha velocity is normalized by alive threshold 0.1 and added with coefficient 1.0.

Exactly one fresh seed-0 candidate completed 200 / 200 training iterations.

Measured training:
- initial loss: 0.4459555447;
- minimum loss: 0.2287646085;
- final loss: 0.2449941188;
- final HOME velocity loss: 0.0189204682;
- mature samples in final batch: 8 / 8;
- no non-finite state.

Measured growth/recovery:
- pre-damage active: 993 / 1600;
- pre-lesion global MSE: 0.0524558015;
- post-lesion global MSE: 0.0499905869;
- DamageEffect: -0.0024652146;
- RelativeDamageEffect: -0.0469960330;
- active-cell removal: 48.54%;
- final recovery active: 1393;
- RecoveryFraction: undefined;
- stable T50/T90: not attained.

Measured persistence/homeostasis:
- initial active: 941;
- final active: 1406;
- maximum active: 1490;
- active-cell drift: +465;
- initial MSE: 0.0493245237;
- final MSE: 0.0822274983.

STAB-09 FAILURE MODE
VIABLE BUT OVERGROWN PHENOTYPE WITH LONG-HORIZON HOMEOSTASIS FAILURE AND INVALID LESION.

The lesion removed nearly half of the active phenotype yet improved morphology, proving substantial harmful/excess structure remained before damage.

The new dynamic persistence gates failed directly:
- final persistence activity > 800;
- maximum persistence activity > 800;
- final active-cell drift was strongly positive rather than <= 0.

DIRECTIONAL SIGNAL
HOME-1 improved the nominal 96-step growth snapshot relative to STAB-05/07/08.

Versus STAB-05:
- active cells 1206 -> 993, approximately 17.66% lower;
- MSE 0.0701904967 -> 0.0524558015, approximately 25.27% lower.

Versus STAB-07:
- active cells 1094 -> 993, approximately 9.23% lower;
- MSE 0.0625592172 -> 0.0524558015, approximately 16.15% lower.

Versus STAB-08:
- active cells 1440 -> 993, approximately 31.04% lower;
- MSE 0.1016835570 -> 0.0524558015, approximately 48.41% lower.

This directional improvement does not satisfy the absolute gates and does not establish long-horizon stability.

CURRENT OBJECTIVE DIAGNOSIS
Canonical P0 now distinguishes endpoint quality from attractor quality:

1. static sparse-target morphology can make death competitive;
2. foreground protection can produce severe overgrowth;
3. continuous occupancy pressure partially suppresses overgrowth;
4. stronger threshold pressure can collapse viability;
5. static spatial support geometry does not solve the bracket;
6. one-step mature-only velocity control can improve the nominal growth snapshot;
7. one-step local control does not enforce 96-step homeostasis;
8. the learned rule can have acceptable/improved short-horizon behavior while retaining a strongly expansive longer-horizon attractor.

The next mechanism should therefore train or interrogate a longer homeostatic trajectory rather than another local one-step derivative or static endpoint penalty.

DURABLE STAB-09 RECORDS
research/experiments/dg1a/dg1a-p0-stab09-spec.ice
research/experiments/dg1a/dg1a-p0-stab09-result.ice
evidence/dg1a/p0_stab09_sandbox.json

Full local sandbox evidence SHA-256:
2efa48b1a32ac2604b75034ebce98e1acefa91ff86d5c4427b4bd24bec48a916

CURRENT DECISIONS
- close STAB-09 as negative;
- do not widen HOME-1;
- do not tune maturity rule, probe horizon, velocity normalization, coefficients, thresholds, or gates retroactively;
- preserve the 113-cell viability floor;
- preserve the 800-cell occupancy ceiling;
- preserve the strengthened persistence gates:
  * maximum persistence active cells <= 800;
  * final active-cell drift <= 0;
- preserve global visible morphology MSE as common evaluation metric;
- preserve all eight historical modes;
- retain STAB-05 through STAB-09 as first-class mechanistic negative knowledge;
- do not reopen STAB-01 through STAB-09 with post-result parameter inserts;
- do not begin DG-1B yet;
- do not introduce Fibonacci scheduling into canonical P0 yet;
- retain Fibonacci as separate DG-1A-FIB1 follow-on ablation.

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-10 — DESIGN / PREREGISTRATION ONLY.

STAB-10 should test one fixed LONGER-HORIZON homeostasis mechanism.

Plausible design classes:
- bounded multi-step virtual persistence probe;
- short trajectory-integrated excess-support expansion loss;
- explicit persistence curriculum term coupled to target-derived viability.

NO STAB-10 mechanism is selected by this status record.

Before execution, STAB-10 must preregister:
- one explicit longer-horizon mechanism;
- one fixed parameterization;
- unchanged common evaluation metric;
- frozen envelope;
- explicit viability, occupancy, lesion-validity, morphology, recovery, persistence/homeostasis, and finite-state gates.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling from this packet.

NEXT ACTION
Design and preregister STAB-10.
Do not execute it until its exact mechanism and gates exist in .ice.
