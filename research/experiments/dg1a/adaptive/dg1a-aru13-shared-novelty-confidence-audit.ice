TITLE: DG-1A-AR-U13 — Shared Novelty / Confidence Compression Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX MECHANISM-COMPRESSION AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-adaptive-research-frontier-r4-20260918.ice

PURPOSE
Test whether one compact confidence/novelty state can serve several adaptive subsystems:

- injury surprise;
- context disagreement;
- causal-calibration drift;

without collapsing different causes of surprise into one indiscriminate alarm.

QUESTION
Can Yggdrasil share the machinery that decides:

"how trustworthy is my current state/model?"

while preserving enough typed evidence to decide:

"what kind of corrective response is appropriate?"

BOUNDARY
This is synthetic.

It does not:
- allocate Yggdrasil channels;
- establish a real confidence variable;
- modify or execute STAB-18-R1;
- prove current latent state already contains these typed residuals.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX
ANALYTIC where explicitly stated.

SYNTHETIC EVENT CLASSES
Four equally represented classes:

0.
MAINTENANCE

1.
INJURY SURPRISE

2.
CONTEXT DISAGREEMENT

3.
CAUSAL-CALIBRATION DRIFT

RAW FEATURES
Six standardized local evidence features arranged into three semantic pairs:

INJURY PAIR
- temporal transition residual
- spatial / wound-like residual

CONTEXT PAIR
- sensor/mode disagreement
- context freshness gap

CALIBRATION PAIR
- action-response innovation
- leakage-model residual

Maintenance:
all means = 0

Injury:
injury pair mean = 2
other means = 0

Context:
context pair mean = 2
other means = 0

Calibration:
calibration pair mean = 2
other means = 0

Per-feature noise:
Gaussian sigma = 0.65

Samples:
30,000 per class
120,000 total.

The three surprise classes are deliberately matched in total expected magnitude.

This prevents a scalar novelty norm from encoding event identity accidentally through event strength.

REPRESENTATIONS TESTED

A. ONE SCALAR NOVELTY
Euclidean norm of all six standardized residuals.

This is the strongest simple version of:
"something unusual is happening."

B. THREE TYPED RESIDUAL SUMMARIES
For each semantic pair:
Euclidean pair norm.

Produces:
- injury residual magnitude;
- context residual magnitude;
- calibration residual magnitude.

C. FULL SIX RAW FEATURES

D. SHARED CONFIDENCE GATE + TYPED IDENTITY
Use ONE scalar novelty magnitude only to decide:

maintenance
vs
uncertain/event.

Then if uncertain:
select the response type from the largest of the three typed residual summaries.

This represents:
one shared confidence mechanism
plus
minimal cause identity.

TRAIN / TEST
Deterministic stratified 50/50 split.

Simple multinomial logistic decoders are used only as diagnostic readouts.

They are NOT proposed as organism mechanisms.

RESULTS

EVENT DETECTION
scalar novelty:

maintenance vs any surprise
ROC AUC:
0.98454

Therefore one scalar is highly effective at:
"something is wrong."

FOUR-CLASS EVENT IDENTITY

scalar novelty only:
46.90% accuracy

three typed residual summaries:
95.05%

all six raw features:
97.62%

KEY NEGATIVE
A single scalar cannot preserve cause identity when several event classes have similar novelty magnitude.

This is an information-compression limitation,
not a model-capacity problem.

If:
injury,
context disagreement,
and
calibration drift

all produce the same scalar confidence decrease,

then the scalar alone cannot determine whether the correct response is:

REPAIR

WAIT / SEEK CONTEXT CONSENSUS

or

RECALIBRATE CAUSAL CREDIT.

SHARED-GATE COMPACT MECHANISM
Choose a scalar novelty threshold on the training split that best separates:

maintenance
from
event.

Training event-detection accuracy:
94.575%

selected synthetic threshold:
2.0820

Held-out event-detection accuracy:
94.52%

Then:

if scalar novelty < threshold:
MAINTENANCE

else:
choose event identity from the largest typed residual pair.

Held-out four-class response accuracy:
94.045%

Per-class correct response:

maintenance:
88.46%

injury:
95.88%

context:
95.99%

calibration:
95.85%

PRIMARY POSITIVE
Most of the full six-feature performance can be retained with:

ONE SHARED NOVELTY / CONFIDENCE MAGNITUDE

plus

THREE SMALL TYPED RESIDUAL SUMMARIES.

This is a strong mechanism-compression result.

INTERPRETATION
The shared scalar should control:

HOW MUCH diagnostic/adaptive activity to recruit.

The typed evidence should control:

WHICH adaptive program is eligible.

Conceptual architecture:

typed local evidence
->
shared confidence / surprise magnitude
->
if low confidence:
temporarily recruit diagnosis/adaptation

while:

injury evidence
selects
repair inference

context disagreement
selects
consensus / hold

action-calibration innovation
selects
leakage recalibration.

DO NOT USE
surprise
->
one generic adaptive response.

That would recreate several previously observed failure modes:
- false repair;
- wrong-mode switching;
- unnecessary causal recalibration.

CROSS-DOMAIN FIT
This compresses three existing research rules without erasing their semantics.

INJURY
unexpected local state transition
should reduce confidence before repair escalation.

CONTEXT
sensor disagreement/staleness
should reduce confidence before committing a season.

CAUSAL CREDIT
unexpected action-response innovation
should reduce confidence before trusting stale leakage calibration.

Thus:

SURPRISE FIRST REDUCES CONFIDENCE

remains a shared principle.

But:

SURPRISE TYPE MUST REMAIN IDENTIFIABLE.

ANALYTIC LIMIT
Suppose two event causes C1 and C2 produce identical distributions over scalar confidence S:

P(S | C1)
=
P(S | C2)

but require different responses.

No policy:

response = f(S)

can distinguish them above prior probability.

Therefore no amount of downstream scalar-threshold tuning can recover semantic information that compression removed.

ARCHITECTURAL CONSEQUENCE
Do not reserve:

one independent confidence subsystem per adaptive function

unless future data requires it.

Also do not compress everything into:

one scalar alarm.

Preferred minimal abstraction:

SHARED CONFIDENCE MAGNITUDE

+
TYPED RESIDUAL EVIDENCE.

POSSIBLE REAL-YGGDRASIL MAPPING
From AR-U14 source audit:

shared confidence could eventually be estimated from:
- maintenance-relative residual z-score;
- prediction-error variance;
- disagreement / covariance shift;
- freshness of causal calibration.

Typed evidence can remain distributed in existing latent/perception features.

This suggests confidence may not need a dedicated semantic channel if:
- its magnitude can be computed by the shared local rule;
- typed residual identity remains represented in latent state.

DO NOT ALLOCATE A CHANNEL YET.

NEXT
AR-U14-DIAG — exact non-gating real-signal telemetry preregistration

and/or

AR-C3 — provenance compression.

The shortest path toward real applicability is:
freeze the diagnostic needed to determine whether current hidden channels already contain:
- typed novelty;
- action identity;
- consequence proxies;
- usable confidence structure.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
samples_per_class = 30000
total_samples = 120000
