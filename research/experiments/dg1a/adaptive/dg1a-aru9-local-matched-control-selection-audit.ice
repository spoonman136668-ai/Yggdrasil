TITLE: DG-1A-AR-U9 — Local Matched-Control Selection Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX PARTIAL / NEGATIVE IDENTIFIABILITY AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru8-local-disturbance-reference-audit.ice

PURPOSE
AR-U8 established that a useful local disturbance reference must be:

disturbance-coupled

but

action-decoupled.

This audit asks whether a cell can identify such references from several local candidates using only cheap local evidence.

Test candidate selection from:
- pre-perturbation covariance;
- sparse action-exposure microprobes;
- combinations of the two;
- multi-reference ensembles.

BOUNDARY
This is synthetic.

It does not:
- identify real Yggdrasil control cells;
- authorize explicit reference populations;
- establish the true causal graph;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PRIMARY SYNTHETIC NEIGHBORHOOD
Candidate references per target:
8

Trials:
50,000

No-action history:
48 transitions

Action-exposure microprobes:
8

True causal effect:
+/-0.04

Common environmental disturbance SD:
0.15

Target/reference idiosyncratic noise SD:
0.04

CANDIDATE CONSTRUCTION
Each candidate has:

q_j:
strength of shared environmental coupling with the target.

c_j:
fraction of the target action's causal effect that contaminates the candidate.

The primary benchmark intentionally makes these partially conflict:

closer / more environment-correlated candidates
tend also to be
more action-contaminated.

This models the realistic possibility that:
the neighbor most similar to the target
is also inside the target's causal footprint.

LOCAL OBSERVATIONS AVAILABLE FOR SELECTION

1. PRE-ACTION CORRELATION
Estimate target/reference covariance during no-action history.

2. ACTION-EXPOSURE MICROPROBE
Apply sparse signed target perturbations.

Estimate whether each reference responds systematically to the target's action.

The selector does NOT observe:
true q_j;
true c_j;
the true causal graph.

REFERENCE MODEL
For each candidate,
fit a scalar no-action mapping:

target disturbance
approximately
gamma_j * reference disturbance.

At test time,
causal credit uses:

target change
-
gamma_j * selected_reference_change.

SELECTION METHODS

NO REFERENCE
Use raw target consequence.

CORRELATION ONLY
Choose the candidate with the largest estimated pre-action correlation.

EXPOSURE ONLY
Choose the candidate with the smallest estimated action exposure.

COMPOSITE
Choose the candidate maximizing:

correlation
*
(1 - estimated_action_exposure)

with bounded exposure.

TOP-3 COMPOSITE ENSEMBLE
Use the three highest composite-score references.

Average their predicted disturbance using composite weights.

PRIMARY CAUSAL-SIGN ACCURACY

no reference:
60.22%

correlation only:
58.81%

exposure only:
60.97%

single composite:
61.07%

top-3 composite ensemble:
62.79%

LATENT SELECTION DIAGNOSTIC
This is not available to the selector during operation.

Correlation-only selected candidates had:

mean true environmental coupling q:
0.917

mean true action contamination c:
0.636

Composite-selected candidates had:

mean q:
0.681

mean c:
0.255

KEY NEGATIVE
MAXIMUM CORRELATION
is not equivalent to
BEST CAUSAL CONTROL.

The most disturbance-similar candidate can be a poor reference if it lies inside the action's causal footprint.

In the primary benchmark:
correlation-only control was WORSE than using no reference.

This is an important negative.

BETTER-OBSERVED / MORE-CANDIDATE FOLLOW-UP
A second benchmark used:

candidate references:
16

no-action history:
64

microprobes:
16

lower observation noise:
0.02 target/reference

microprobe observation noise:
0.008

Trials:
30,000

RESULTS

no reference:
approximately 60.6%

correlation only:
approximately 62.1%

exposure only:
approximately 61.4%

single composite:
approximately 62.4%

top-3 composite:
approximately 64.4%

Thus better history and more candidates improve control selection modestly.

However the simple heuristic remains far below the idealized clean-reference results from AR-U7/AR-U8.

MULTI-REFERENCE WEIGHTING
Weighting all references by:

correlation * (1 - exposure)

produced only modest additional gains.

Changing the weight sharpness or imposing simple action-exposure thresholds did not transform the result.

Therefore:
the remaining gap is not just a trivial threshold-selection problem.

INTERPRETATION
Matched-control selection is itself a causal-identifiability problem.

A candidate reference must balance:

HIGH SHARED DISTURBANCE INFORMATION

LOW ACTION EXPOSURE

LOW INDEPENDENT NOISE

FRESHNESS

STABILITY OF THE TARGET-REFERENCE RELATIONSHIP.

No single pairwise covariance statistic captures all of these.

CROSS-DOMAIN WARNING
The same local cell can be:
- a good state predictor;
- a bad causal control.

Prediction asks:
does this signal forecast my state?

Causal control asks:
does this signal share the disturbance while remaining outside the action pathway being tested?

These are different criteria.

ARCHITECTURAL CONSEQUENCE
Do not hard-code:

nearest neighbor
or
most correlated neighbor

as the Yggdrasil causal baseline.

A future system may need:
- a small SET of candidate controls;
- action-exposure tracking;
- robust ensemble prediction;
- reference replacement after damage;
- uncertainty/confidence on the control estimate.

POSSIBLE STRONGER DIRECTION
Rather than nominate permanent control cells,
learn a local disturbance subspace from several neighbors/latent channels.

Then:
remove components that respond consistently to the cell's own tagged perturbations.

Conceptually:

local neighborhood dynamics
->
shared disturbance representation

minus

action-responsive components

->
counterfactual baseline estimate.

This is closer to a learned local causal representation than a single matched-control cell.

IMPORTANT LIMITATION
This audit does not show that such a disturbance subspace is identifiable from current Yggdrasil state.

That is the next experimental question.

DECISION
AR-U7 remains promising,
but the clean local-reference assumption is not yet justified.

Simple covariance-based control selection is rejected.

Composite covariance + exposure screening is directionally useful but insufficient.

NEXT
AR-U10 — LOCAL DISTURBANCE SUBSPACE / ACTION-ORTHOGONALIZATION POC

Question:
Given several local signals,
can a tiny local linear latent model separate:

shared environmental disturbance

from

components systematically coupled to the cell's own action tag?

Compare against:
- best single reference;
- correlation-only reference;
- raw neighborhood average.

PARALLEL
AR-C1 — repeated decentralized context ordering.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_trials = 50000
followup_trials = 30000
