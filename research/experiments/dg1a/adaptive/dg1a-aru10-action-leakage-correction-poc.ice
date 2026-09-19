TITLE: DG-1A-AR-U10 — Local Disturbance Subspace / Action-Leakage Correction POC
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE / QUALIFIED POC
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru9-local-matched-control-selection-audit.ice

PURPOSE
AR-U9 showed that selecting one "best" local control is unreliable.

This POC tests a different strategy:

use several local signals to estimate shared disturbance,

while explicitly measuring and subtracting the part of those signals caused by the cell's own tagged action.

Question:
Can action-contaminated neighbors still contribute useful disturbance information if their action response is separately estimated?

BOUNDARY
Synthetic only.

This does not:
- establish a Yggdrasil disturbance subspace;
- reserve explicit reference cells;
- authorize lifetime weight changes;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PART A — HARD ACTION-ORTHOGONALIZATION NEGATIVE

Local candidate signals contain:

environment loading:
a_j

and

action-response loading:
b_j.

The two are intentionally partially correlated.

A no-action local linear predictor is learned from eight signals.

First attempt:

project the learned predictor weights into the subspace orthogonal to the estimated action-response vector.

RESULT

no reference:
60.25% causal-sign accuracy

best single reference:
71.58%

raw neighborhood mean:
79.51%

full local ridge predictor:
72.01%

hard action-orthogonalized ridge:
61.85%

The orthogonalized predictor nearly loses the reference advantage.

DIAGNOSTIC
Hard projection reduced mean absolute predictor/action overlap from:

approximately 0.275

to

approximately 0.020.

But it also removed environmental information because:
environment loading
and
action-response loading
were not orthogonal in the synthetic neighborhood.

KEY NEGATIVE
DO NOT REQUIRE THE DISTURBANCE REPRESENTATION ITSELF TO BE ORTHOGONAL TO ACTION.

If environmental and action pathways overlap physically,
hard subspace removal can destroy the signal needed to predict disturbance.

PART B — ACTION-LEAKAGE CORRECTION

Reformulate the problem.

The cell knows the identity/sign of its own bounded perturbation.

Each neighboring signal has a measurable action leakage:

leak_j * action_tag.

Use sparse microprobes to estimate:

leak_hat_j.

Then correct each live local signal:

reference_corrected_j =
reference_observed_j
-
leak_hat_j * current_action_tag.

Only AFTER that correction is the neighborhood used to estimate shared disturbance.

This preserves environment-carrying dimensions.

SYNTHETIC SETUP

references:
8

no-action history:
48 observations

action microprobes:
12 primary

environment SD:
0.15

reference noise SD:
0.03

target noise SD:
0.03

causal target effect:
+/-0.04

Action leakage magnitude is partially correlated with environment coupling.

Trials:
20,000 primary.

RESULTS

no disturbance reference:
60.39%

best single reference:
80.02%

raw neighborhood mean:
84.51%

raw neighborhood mean
after action-leakage correction:
88.88%

full ridge predictor:
77.67%

ridge predictor
after leakage correction:
79.07%

PRIMARY POSITIVE
A simple multi-reference neighborhood average plus explicit action-leakage subtraction outperformed:

- no reference;
- best single reference;
- uncorrected neighborhood mean;
- the tested small ridge predictor.

This supports a decomposition:

OBSERVED LOCAL CHANGE
=
SHARED DISTURBANCE
+
ACTION LEAKAGE
+
INDEPENDENT NOISE.

Estimate action leakage separately,
then use the remaining neighborhood signal as the disturbance baseline.

WHY SIMPLE MEAN OUTPERFORMED RIDGE IN THIS TOY
The synthetic environment has one dominant common disturbance factor.

A ridge predictor fitted finite noisy history can overfit local loading differences.

The neighborhood mean is a strong low-variance estimator of the common factor.

Do NOT generalize this to:
mean is always the best local model.

The result only says a complex forward model is not automatically superior.

MICROPROBE COUNT
Primary effect was not highly sensitive to probe count under the tested probe-noise regime.

Approximate corrected-mean causal-sign accuracy:

P=1:
88.97%

P=2:
88.97%

P=4:
88.53%

P=8:
89.01%

P=12:
89.05%

P=24:
89.08%

P=48:
89.30%

This occurs because:
- action leakage is coherent across the local references;
- neighborhood averaging suppresses estimation noise.

Do not infer that one probe is sufficient in real Yggdrasil.

MICROPROBE OBSERVATION NOISE
With 8 probes:

probe noise 0.005:
corrected mean ~89.02%

0.010:
~88.72%

0.020:
~88.98%

0.040:
~88.19%

0.080:
~87.42%

The mechanism degrades gradually.

REFERENCE LOSS
Randomly remove reference signals at evaluation.

loss 0%:
uncorrected 85.21%
corrected 89.15%

loss 25%:
uncorrected 83.55%
corrected 87.35%

loss 50%:
uncorrected 81.13%
corrected 84.64%

loss 75%:
uncorrected 77.52%
corrected 79.75%

The ensemble degrades gracefully as local controls disappear.

This is preferable to dependence on one dedicated control cell.

ACTION-LEAKAGE DRIFT
Random zero-mean change in individual leakage strengths at test:

shift SD 0.00:
uncorrected 84.61%
corrected 88.76%

0.10:
85.03%
89.15%

0.25:
84.79%
88.78%

0.50:
84.56%
89.07%

1.00:
83.53%
88.42%

Random heterogeneous drift is partly averaged out by the local ensemble.

SYSTEMATIC LEAKAGE-STATE CHANGE
A more dangerous test scales ALL actual action leakage after the probe calibration.

factor 0:
uncorrected 89.03%
corrected 85.09%

factor 0.5:
uncorrected 87.84%
corrected 87.78%

factor 1.0:
uncorrected 85.19%
corrected 89.31%

factor 1.5:
uncorrected 80.19%
corrected 87.86%

factor 2.0:
uncorrected 74.60%
corrected 84.90%

factor 3.0:
uncorrected 63.42%
corrected 74.54%

IMPORTANT NEGATIVE
A stale leakage estimate can HURT.

If the action-to-reference coupling disappears but the cell continues subtracting the old estimate,
the correction invents a false opposite disturbance.

Therefore:
ACTION-LEAKAGE ESTIMATE MUST CARRY FRESHNESS / CONFIDENCE.

This independently reinforces the AR-U3 rule:

MISSING OR STALE INFORMATION
must not be treated as
CURRENT CERTAINTY.

ARCHITECTURAL READING
The strongest current cheap causal-credit stack is now:

1.
SPARSE ONE-ROLE ACTION TAG

2.
LOCAL ELIGIBILITY / ACTION IDENTITY

3.
MULTI-SIGNAL LOCAL DISTURBANCE ESTIMATE

4.
EXPLICIT ESTIMATE OF ACTION LEAKAGE INTO THAT DISTURBANCE ESTIMATE

5.
FRESHNESS / CONFIDENCE ON THE LEAKAGE ESTIMATE

6.
DELAYED LOCAL CONSEQUENCE

7.
BOUNDED ROLE/SENSITIVITY UPDATE.

This is more robust than:
one permanent control neighbor.

CROSS-DOMAIN PATTERN
Useful Yggdrasil local state increasingly needs TWO properties at once:

RELEVANCE:
share the important environmental cause.

SEPARABILITY:
retain enough independent action/error structure to identify what caused what.

That pattern has now appeared in:
- injury cues;
- seasonal sensors;
- local utility cues;
- local disturbance references.

LITERATURE CONTEXT
Predictive-coding research demonstrates that local prediction errors can drive learning without conventional global backpropagation.

Recent 2025-2026 work also explores fully local spatio-temporal credit and scalable local-learning rules.

The current POC adds a narrower causal warning:

a locally predictive signal can still be an invalid causal baseline if it also carries the action being evaluated.

Prediction quality alone is insufficient.

NEXT
AR-U11 — ACTION-LEAKAGE FRESHNESS / ONLINE RECALIBRATION

Question:
Can the cell detect that its action-to-neighborhood coupling has changed and suspend/recalibrate causal correction before stale subtraction causes harm?

Test:
- damage that removes neighbors;
- role relocation;
- sudden coupling increase/decrease;
- temporary partitions.

PARALLEL
AR-C1 — repeated decentralized context ordering.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_trials = 20000
