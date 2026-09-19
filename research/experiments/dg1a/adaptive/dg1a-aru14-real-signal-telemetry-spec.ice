TITLE: DG-1A-AR-U14-DIAG — Real-Yggdrasil Local Signal / Natural-Experiment Telemetry Preregistration
DATE: 2026-09-18
STATUS: NON-GATING OBSERVATIONAL / CAUSAL-DIAGNOSTIC PREREGISTRATION — UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru14-real-yggdrasil-signal-mapping-audit.ice

PURPOSE
Freeze a read-only diagnostic for answering:

Do current Yggdrasil trajectories already contain enough local information for:
- action identity;
- typed novelty;
- target-free consequence estimation;
- disturbance separation;
- confidence/freshness;

without adding explicit role or meta-rule registers?

KEY IDEA
Current NCA fire masking already provides a natural randomized local intervention.

At each step:
raw_delta is computed first.

Then each cell independently receives a stochastic fire decision.

Therefore, conditional on the pre-step state and raw_delta,
the fire mask creates natural variation between:

PROPOSED UPDATE EXECUTED

and

PROPOSED UPDATE SKIPPED.

This can be exploited diagnostically.

No new perturbation mechanism is required.

BOUNDARY
This diagnostic:
- does not train a new model;
- does not modify model weights;
- does not alter canonical R1 classification;
- does not change fire rate;
- does not change R1 RNG contracts;
- does not add target information to the cell;
- does not create explicit role channels;
- does not execute STAB-18-R1 from this research lane.

If run on canonical R1:
execute only AFTER canonical R1 training/evaluation/classification is complete.

If run on a historical sandbox checkpoint:
label all resulting evidence MEASURED_SANDBOX
and verify checkpoint byte identity first.

REQUIRED CHECKPOINT PROVENANCE
Record:
- checkpoint SHA256;
- source commit;
- config SHA256;
- device;
- precision;
- generator seeds;
- analysis code revision.

Do not execute if checkpoint bytes cannot be verified.

CURRENT REPOSITORY LIMIT
The Git tree inspected in AR-U14 contains checkpoint hashes for historical STAB-16 and STAB-17,
but not checkpoint bytes.

Therefore this chat/GitHub lane cannot execute the real-state diagnostic now.

No latent result is claimed.

TRAJECTORIES
Reuse the existing R1 latent diagnostic envelopes where applicable:

A. UNDAMAGED MAINTENANCE
- canonical growth;
- persistence;
- complete state recording.

B. CANONICAL DAMAGE / RECOVERY
- canonical growth;
- canonical lesion;
- recovery;
- complete state recording.

Do not introduce new lesion geometry for the primary diagnostic.

STEP-LEVEL TELEMETRY
For every recorded step t:

1.
state_t
all 16 channels

2.
perception_t
48 features:
identity/Sobel-x/Sobel-y for every channel

3.
raw_delta_t
update_net(perception_t)
before fire gating

4.
fire_mask_t
reconstructed exactly from a cloned pre-step generator state

5.
masked_delta_t

6.
pre_alive_t

7.
post_alive_t

8.
state_t_plus_1

9.
realized_delta_t =
state_t_plus_1 - state_t

10.
local neighborhood summaries:
- 3x3 state mean
- 3x3 state RMS
- 3x3 update mean
- 3x3 update RMS
- hidden-channel covariance summaries

11.
distance-to-lesion metadata
analysis only.

NATURAL RANDOMIZATION CONTRACT
For a given cell/time sample:

TREATMENT:
fire_mask_t = 1

CONTROL:
fire_mask_t = 0

The fire mask must remain the canonical stochastic draw.

Do NOT resample or balance treatment/control by changing the simulation.

Known propensity:
canonical fire probability = 0.5.

PRIMARY ELIGIBILITY
Use only samples where:
- cell is pre_alive;
- raw_delta magnitude is finite;
- raw_delta magnitude > 0.

Do not invent a post-hoc magnitude threshold for inclusion.

Magnitude may be used as a continuous covariate.

PRIMARY QUESTION 1 — ACTION CONSEQUENCE
For horizons:

1
2
4
8
16

estimate the effect of treatment on target-free local outcomes.

TARGET-FREE OUTCOMES

A.
future LIFE4 persistence

B.
future local birth/death/turnover

C.
future local visible-state stability

D.
future hidden-state predictability

E.
future neighborhood-consistency change

F.
future local update magnitude

These are diagnostic outcomes.

Do not assume any one is useful.

EXTERNAL VALIDATION OUTCOME
For analyst scoring ONLY,
compute future change in local visible target loss.

The target may be used to evaluate whether a target-free proxy aligns with useful morphology.

The target must NOT be included in any candidate local consequence feature.

PRIMARY QUESTION 2 — CAN CURRENT LATENT STATE PREDICT ACTION SIGN?
Using pre-action features only:

- state channels 0..15;
- perception;
- raw_delta;
- local temporal history;

fit simple held-out diagnostic decoders to predict:

whether executing the proposed update leads to better or worse external validation outcome at each horizon.

Use temporal block splits.

Report:
- ROC AUC;
- calibration;
- balanced accuracy;
- horizon dependence.

This is a decodability test,
not a production controller.

PRIMARY QUESTION 3 — TARGET-FREE CONSEQUENCE PROXY
For each target-free outcome candidate:

measure association with the externally scored useful-action label.

Report:
- single-proxy AUC;
- pooled AUC;
- incremental gain over raw state;
- stability across maintenance vs recovery.

Desired evidence:

a target-free local signal predicts whether a recent action was useful.

Negative evidence is equally important.

PRIMARY QUESTION 4 — TYPED NOVELTY
Construct observational typed residual summaries:

INJURY-TYPE
from:
- local temporal residual;
- lesion-proximal spatial response;
- hidden-channel injury discriminability.

CONTEXT-TYPE
not available in current architecture before AR-01.
Record as NOT MEASURABLE in baseline.

CALIBRATION-TYPE
from:
- action-response innovation;
- mismatch between expected and observed neighborhood consequence.

Question:
can injury novelty and action-calibration novelty be separated in current latent dynamics?

Do not force three-way U13 mapping before explicit context exists.

PRIMARY QUESTION 5 — DISTURBANCE REFERENCE
For every candidate local reference set:

measure BOTH:

A.
shared outcome-predictive covariance with the target cell

and

B.
action leakage:
association between the target cell's randomized fire treatment and future reference change.

Candidate sets:
- immediate neighbors;
- radius-2 ring;
- radius-3..4 ring;
- latent-channel modules;
- learned linear combination of nearby state deltas.

Do NOT choose the most correlated reference automatically.

PRIMARY CONTROL-QUALITY METRIC
For candidate control R:

DisturbanceUtility =
predictive improvement for untreated target-cell change

ActionLeakage =
effect of target fire treatment on R

A useful reference needs:

high DisturbanceUtility
and
low ActionLeakage.

Report the Pareto frontier.

Do not collapse both into one tuned score before seeing data.

CAUSAL-CONE MEASUREMENT
Source analysis gives a conservative upper support bound of:

radius <= 2H.

Measure empirical action leakage by radius at horizons:

1
2
4
8
16.

Question:
how much smaller is the empirical influence cone than the structural worst-case bound?

This is critical for deciding whether local matched controls are practical.

PRIMARY QUESTION 6 — CONFIDENCE / FRESHNESS
Construct OFFLINE candidate confidence signals from pre-action information only:

- maintenance-relative z-score;
- local prediction residual magnitude;
- cross-channel disagreement;
- control-reference disagreement;
- age since last large action-response innovation.

Test whether low confidence predicts:

- wrong action-sign decoder decisions;
- high control leakage error;
- injury-classification ambiguity.

Do not allocate a confidence channel from this diagnostic alone.

PRIMARY QUESTION 7 — ROLE-LIKE LATENT ORGANIZATION
Using only channels 5..15 and their local perception/history:

test whether stable latent subpopulations predict distinct action consequences.

Procedure:
- cluster/encode latent trajectories without role labels;
- measure held-out differences in natural-treatment effects;
- selectively analyze functional outcome sensitivity.

A cluster may be described as role-like only if:
its members have a reproducibly distinct causal effect profile.

Do not name:
relay
repair
inhibitor
growth
dormant

from geometry/state appearance alone.

FIRE-MASK IDENTIFIABILITY CAUTION
The stochastic fire mask is available to the analyst through generator reconstruction.

It is NOT currently stored as cell-local memory.

If useful credit requires knowing whether an action actually fired,
future online architecture may need a minimal execution/eligibility trace.

This diagnostic should quantify that necessity.

ALIVE-GATING CAUTION
realized_delta can include state zeroing due to living-mask failure.

Therefore action-effect analyses must distinguish:

raw proposed update

from

death/liveness gating.

Do not treat all realized state loss as the intended action.

PRIMARY DECISION BRANCHES

U14-D1
Current hidden/perception state predicts useful action sign
and
a target-free local consequence proxy performs well.

Interpretation:
existing latent dynamics may already support a minimal meta-rule.

Next:
test decoding/modulation before adding explicit registers.

U14-D2
Useful action sign is decodable,
but only when analyst-only fire/action identity is supplied.

Interpretation:
add the smallest local eligibility/action tag first.

U14-D3
Injury novelty is strong,
but useful local consequence is not decodable.

Interpretation:
repair detection and adaptive credit are separate seams.
Do not conflate them.

U14-D4
No target-free local proxy aligns with useful outcomes.

Interpretation:
current training objective may not produce organism-local utility information.
A new training/architecture intervention is required before functional regeneration.

U14-D5
Control candidates are highly action-contaminated at all useful horizons.

Interpretation:
same-organism matched controls are insufficient;
prefer predictive residual + leakage correction or sparse domain-separated probes.

SUCCESS IS NOT PREDECLARED
This diagnostic is exploratory/non-gating.

It does not have a pass/fail threshold.

Its purpose is to locate the information bottleneck.

DURABLE RESULT
When executed,
create:

research/experiments/dg1a/adaptive/dg1a-aru14-real-signal-telemetry-result.ice

and machine evidence containing:
- exact scalar tables;
- decoder metrics;
- reference Pareto data;
- leakage-vs-radius curves;
- confidence calibration;
- latent cluster causal profiles.

PROVENANCE
evidence_class = NON_GATING_DIAGNOSTIC_PREREGISTRATION
canonical_scientific_execution = false
canonical_r1_execution_spent = false
new_training_run = false
