TITLE: DG-1A-P0 Current Status
DATE: 2026-09-17
STATUS: ACTIVE — STAB-03 CLOSED NEGATIVE / NEXT OBJECTIVE PACKET NOT YET EXECUTED
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; EXPLORATORY FOR SANDBOX RESULTS

BRANCH
dg1a-p0

VERIFIED BRANCH HEAD BEFORE THIS STATUS UPDATE
4627867bacfad9a80cdbb477de27f3ce05697ebf

CURRENT PURPOSE
Establish a trustworthy canonical developmental NCA control with bounded growth, persistence, meaningful damage, and stable regeneration before DG-1B functional computation or later Yggdrasil mechanisms are opened.

IMPLEMENTED SURFACE
- fixed-grid shared-rule NCA substrate;
- deterministic seed and repository-native target generation;
- state-pool persistence/regeneration curricula;
- maturity-gated training damage;
- independent training/evaluation lesion geometry;
- global and stable recovery metrics;
- persistence telemetry;
- resource accounting;
- resumable deterministic training sessions;
- machine-readable evidence writer and runner;
- explicit global_mse versus balanced_fg_bg training loss modes;
- foreground/background balanced morphology helper;
- fail-closed config validation.

LATEST TEST STATUS
Sandbox isolated regression after STAB-03 edge coverage:
54 passed
0 failed
Environment: Python 3 / PyTorch 2.10.0+cpu

This is not Windows or other authoritative hardware acceptance and is not commit-bound execution evidence.

SCIENTIFIC / EXPERIMENTAL FRONTIER
Small-grid P0 work established a replicated exploratory pattern in which maturity-gated regeneration differs strongly from growth-only post-lesion collapse, but confirmatory support remains blocked by commit-bound provenance requirements.

Full-grid 40 x 40 stabilization remains unresolved.

STAB-01 — CLOSED NEGATIVE
Increasing fixed maturity threshold to M32/M64 did not provide a valid monotonic stabilization mechanism.

STAB-02 — CLOSED NEGATIVE
Extending training development horizon to 64..128 produced an all-dead phenotype.
Key diagnostic: global unweighted morphology MSE allowed the sparse-target dead state to achieve approximately 0.0295742 loss.

STAB-03 — CLOSED NEGATIVE
Candidate: BAL-50 foreground/background-balanced training morphology loss.
Result:
- all-dead attractor avoided;
- pre-damage active cells: 1579 / 1600;
- pre-lesion global morphology MSE: 0.1411564797;
- 0.60 lesion removed 36.48% of active cells;
- damage changed global MSE from 0.1411564797 to 0.1050053090;
- DamageEffect = -0.0361511707;
- lesion therefore INVALID for regeneration inference;
- final active cells: 1164 / 1600;
- stable T50/T90 not defined/attained;
- preregistered STAB-03 improvement rule: FAIL.

STAB-03 FAILURE MODE
Foreground equalization prevented death but overcorrected toward an overgrown, poor-morphology phenotype. Damage improved the primary evaluation metric, proving excess/harmful structure was present before lesion.

DURABLE EVIDENCE
research/experiments/dg1a/dg1a-p0-stab03-result.ice
evidence/dg1a/p0_stab03_sandbox.json

CURRENT DECISIONS
- preserve global morphology MSE as the common evaluation metric;
- do not widen BAL-50 to additional seeds;
- do not tune BAL-50 weighting inside STAB-03;
- do not reopen STAB-01 or STAB-02 with after-the-fact parameter inserts;
- do not begin DG-1B yet;
- do not introduce Fibonacci scheduling into canonical P0 yet;
- retain Fibonacci as the separate DG-1A-FIB1 follow-on ablation;
- retain negative results as first-class research knowledge.

NEXT RECOMMENDED MECHANISM
Open a new preregistered objective-design packet, provisionally DG-1A-P0-STAB-04.

Candidate mechanism:
TrainingMorphologyLoss = GlobalVisibleMSE + ForegroundVisibleMSE

Reason:
- preserve occupancy-proportional global/background pressure;
- add explicit foreground pressure so the all-dead phenotype is no longer competitive;
- avoid converting STAB-03 into an after-the-fact BAL-50 weight sweep;
- preserve existing evaluation metrics and protocol.

STAB-04 must be preregistered before execution and should use one fixed coefficient, one fresh seed-0 candidate, the H96/M16 full-grid envelope, the existing 0.50 training lesion and 0.60 evaluation lesion, and explicit viability/morphology/active-cell/regeneration gates.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
No claim of cognition, functional specialization, continual learning, ancestor inheritance, or general intelligence is authorized.

NEXT ACTION
Preregister STAB-04 before implementation or execution. Do not change STAB-03 after inspection.
