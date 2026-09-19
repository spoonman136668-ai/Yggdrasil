TITLE: DG-1A-AR-S8 — Control Selection / Provenance for Causal Value-of-Information
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE-WITH-MATURATION-LIMIT CONTROL-SELECTION AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
SERIES_NOTE: SUPPLEMENTAL AR-S SERIES — CANONICAL R4 AR-U NUMBERING PRESERVED
BRANCH: dg1a-ar
PARENT: dg1a-ars7-causally-controlled-learned-value-of-information-audit.ice

PURPOSE
S7 established that causal value-of-information learning needs a disturbance-coupled,
action-decoupled reference.

S8 asks the next local question:

when several possible local references exist,
can the organism learn WHICH one is a valid causal control without receiving a semantic control label?

BOUNDARY
This is synthetic.

It does not:
- prove current Yggdrasil exposes these exact control candidates;
- freeze a control-scoring formula;
- establish permanent source IDs;
- authorize a central control selector;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TARGET QUANTITY
The controller needs the causal sign of:

IS AN EXTRA EVIDENCE TRANCHE WORTH ITS COST?

Two hidden event families have true net probe-value approximately:

family 0:
-0.0770
extra probing is harmful after cost.

family 1:
+0.2000
extra probing is beneficial.

The controller does not receive those values.

Observed target change also contains a temporally correlated passive disturbance.

CONTROL CANDIDATES
Five unlabeled candidate references are provided.

R0 — NEAR / HIGH DISTURBANCE MATCH / HIGH ACTION CONTAMINATION

disturbance coupling:
0.95

action contamination:
0.60

measurement noise SD:
0.04

R1 — BALANCED

disturbance coupling:
0.80

action contamination:
0.08

noise:
0.06

R2 — FAR / ACTION-DECOUPLED / WEAK DISTURBANCE MATCH

disturbance coupling:
0.45

action contamination:
0

noise:
0.07

R3 — RELAY COPY OF R1

same underlying R1 evidence
+
small relay noise.

It is not an independent causal source.

R4 — STALE

disturbance coupling:
0.85

action contamination:
0

but delayed by:
3 local intervals.

noise:
0.04

CALIBRATION SIGNALS
No semantic reference labels are exposed.

Two observable diagnostics are used.

1.
DISTURBANCE FIT

During no-action periods,
fit each reference as a predictor of target passive change.

Measure:
residual RMSE.

2.
ACTION EXPOSURE

During randomized tagged microprobe periods,
measure how strongly the candidate reference responds to the known probe tag.

This estimates:
action contamination risk.

The probe tag is action identity,
not a semantic environment label.

CONTROL SCORE
Exploratory synthetic score:

score
=
disturbance_residual_RMSE
*
(
1
+
abs(action_exposure)
)

Lower is better.

This score is a discriminating research device only.

Do not freeze it.

PRIMARY CONFIRMATION
Calibration:
12000 no-action samples
+
12000 tagged microprobe samples.

Evaluation:
50000 fresh events.

16 matched seeds.

SELECTORS

RAW DISTURBANCE CORRELATION
choose the reference most correlated with passive target change.

ACTION-EXPOSURE ONLY
choose the candidate with smallest measured action exposure.

JOINT SCORE
use the disturbance-fit / exposure score above.

ORACLE
choose the candidate with lowest true causal-estimation MSE.

The oracle is unavailable to the learner.

PRIMARY SELECTION RESULT

RAW CORRELATION:

selected R0:
16 / 16 seeds.

ACTION-EXPOSURE ONLY:

selected R2:
10 / 16

selected stale R4:
6 / 16.

JOINT SCORE:

selected balanced R1:
16 / 16.

ORACLE:

selected R1:
16 / 16.

PRIMARY POSITIVE
Neither axis alone is sufficient.

MAXIMIZING DISTURBANCE MATCH
selects a causally contaminated nearby control.

MINIMIZING ACTION EXPOSURE
can select a reference that is too weakly coupled or too stale.

The joint criterion recovers the balanced control.

CANDIDATE AVERAGES
Across 16 confirmation seeds:

R0 — NEAR CONTAMINATED

disturbance residual RMSE:
0.05703

estimated action exposure:
0.59895

true causal-estimation MSE:
0.009188

causal-sign accuracy:
75.60%

probe-value decision regret:
0.02118

R1 — BALANCED

RMSE:
0.07906

action exposure:
0.07981

causal MSE:
0.006306

sign accuracy:
82.73%

regret:
0.01345

R2 — FAR / WEAK

RMSE:
0.11953

action exposure:
0.00102

causal MSE:
0.014399

sign accuracy:
71.49%

regret:
0.02227

R3 — COPY OF R1

RMSE:
0.07973

action exposure:
0.07980

causal MSE:
0.006408

sign accuracy:
82.48%

regret:
0.01365

R4 — STALE

RMSE:
0.10938

action exposure:
-0.00153

causal MSE:
0.012045

sign accuracy:
77.71%

regret:
0.01776

CONTROL GEOMETRY RESULT
The best control is not:

NEAREST

or

MOST CORRELATED

or

LEAST ACTION-RESPONSIVE

in isolation.

The useful causal reference lies on a tradeoff surface:

DISTURBANCE COUPLING

vs

ACTION DECOUPLING

vs

FRESHNESS.

This is consistent with S1/S2 and extends the same rule to resource credit.

PROVENANCE / COPY RESULT
R3 is only a relay copy of R1.

Observed no-action correlation between R1 and R3:

approximately:
0.99577.

Treating R1 and R3 as two independent controls would therefore nearly double the apparent source count
while adding almost no independent disturbance information.

For two equal-variance estimates with correlation ~0.996:

naive independence assumption predicts:
approximately 2x effective evidence.

Actual averaging reduces variance by almost none.

Thus:

COPIES ARE NOT REDUNDANCY

also applies to causal controls.

Control confidence must track source provenance / independence.

SELECTION MATURATION
The selector does not identify the balanced control reliably from very little calibration evidence.

Fresh 100-run sweep:

100 calibration samples:

R1 selected:
53%

R0 contaminated selected:
27%

R3 copy selected:
20%.

300 samples:

R1:
76%

R3:
12%

R0:
12%.

1000 samples:

R1:
95%

R3:
5%.

3000 samples:

R1:
100%.

12000 samples:

R1:
100%.

PRIMARY MATURATION NEGATIVE
CONTROL SELECTION ITSELF REQUIRES EVIDENCE.

A young or recently reorganized local region should not assume that its causal-control identity is already known.

This adds another adaptive resource cost:

EVIDENCE ABOUT THE QUALITY OF THE EVIDENCE CONTROL.

NO-VALID-CONTROL STRESS
A separate synthetic stress makes all references meaningfully action-contaminated.

Example contamination set:

R0:
0.8

R1:
0.5

R2:
0.3

R3:
0.5

R4:
0.3.

Using the same exploratory score,
the best observed score rises above:
0.10

in approximately:
90%

of fresh 3000-sample calibration runs.

With a stronger contaminated set:

0.9
0.7
0.5
0.7
0.4

all tested runs had:
minimum score > 0.10.

Interpretation:

sometimes there is no trustworthy local control.

The correct response is not:
choose the least-bad control and become confident.

It is:

DEFER / REDUCE CAUSAL-LEARNING CONFIDENCE.

This preserves the earlier:

credit fidelity
vs
adaptation throughput

tradeoff.

IMPORTANT DESIGN RULE
A local adaptive controller should represent:

CONTROL QUALITY

as a first-class uncertainty.

It needs to distinguish:

I HAVE A GOOD CAUSAL CONTROL

from

I ONLY HAVE THE BEST OF SEVERAL BAD CONTROLS.

CURRENT CAUSAL RESOURCE-CREDIT STACK

TARGET CONSEQUENCE CHANGE

+

CANDIDATE DISTURBANCE REFERENCES

+

SOURCE PROVENANCE

+

DISTURBANCE FIT

+

ACTION-EXPOSURE ESTIMATE

+

FRESHNESS

+

CONTROL-QUALITY CONFIDENCE

->

CAUSAL VALUE OF ADDITIONAL EVIDENCE.

Then:

if control quality is high:
learn probe value.

if control quality is low:
reduce update magnitude
or
defer.

RELATION TO CONTEXT / PROVENANCE LANE
The same source-independence rules recur:

- repeated relay copies must not become multiple independent controls;
- new physical cells do not automatically create new causal sources;
- stale evidence is not negative evidence;
- confidence should depend on effective independent source count.

Thus provenance is not merely a context-consensus mechanism.

It is also part of:
CAUSAL CREDIT
and
RESOURCE CREDIT.

RELATION TO H7
H7 added:
MODEL-FIT CONFIDENCE

for inherited structure.

S8 adds:
CONTROL-FIT CONFIDENCE

for causal resource learning.

These are structurally similar but answer different questions.

MODEL-FIT:
does inherited representation fit the current state?

CONTROL-FIT:
does this reference validly isolate the disturbance from my action?

Do not collapse them.

DECISION
AR-S8 is POSITIVE WITH A MATURATION LIMIT.

Supported synthetically:

- candidate causal controls can be ranked from observable disturbance-fit and action-exposure evidence;
- a joint score can outperform either criterion alone;
- raw proximity/correlation can prefer contaminated controls;
- action-decoupling alone can prefer weak or stale controls;
- relay copies must not inflate control confidence;
- reliable control selection requires accumulated calibration evidence;
- explicit deferral is appropriate when no candidate control is trustworthy.

Not demonstrated:

- real Yggdrasil candidate-control topology;
- real online action-exposure estimates for causal VoI;
- optimal control score;
- optimal calibration budget;
- real provenance compression for controls;
- control validity under overlapping long causal cones.

NEXT CLEAN QUESTION
AR-S9 — ONLINE CONTROL-SET CHANGE / CONTROL RETIREMENT

Question:

when the local causal topology changes,
can the organism:
- detect that a previously valid control has become action-contaminated;
- retire it;
- promote a previously weaker control;
- avoid catastrophic confidence during the transition?

Test:
- gradual action-footprint expansion;
- sudden sensor/control relocation;
- stale-but-previously-valid reference;
- source birth/death;
- copied relays;
- no-valid-control intervals.

Desired:

CONTROL TRUST
should be reversible
just like functional role and inherited expression trust.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_confirmation_seeds = 16
primary_calibration_no_action = 12000
primary_calibration_tagged_probe = 12000
primary_evaluation_events = 50000
selector_maturation_runs_per_condition = 100
