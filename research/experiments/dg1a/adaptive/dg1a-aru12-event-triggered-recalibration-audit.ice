TITLE: DG-1A-AR-U12 — Event-Triggered Causal Recalibration Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE META-RULE EFFICIENCY AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru11-action-leakage-recalibration-audit.ice

PURPOSE
AR-U11 showed that stale action-leakage calibration can be repaired by periodic or continuous local probing.

This audit asks whether a cell can reduce probe burden by increasing recalibration only when local action-response evidence becomes surprising.

BOUNDARY
Synthetic only.

This does not:
- freeze a threshold;
- prove Yggdrasil has the required innovation signal;
- authorize continuous perturbation of mature organisms;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SETUP
Same local disturbance/action-leakage environment as AR-U11.

Parallel learners:
10,000

references:
8

episodes:
120

coupling change:
episode 50

tested coupling factors after change:

0
0.5
2
3

Initial leakage calibration:
8 probes.

CAUSAL CREDIT
Use action-leakage-corrected neighborhood disturbance estimate.

FREE MONITOR SIGNAL
During ordinary role adaptation,
the cell already knows the sign/identity of its bounded action.

For each naturally tagged local action:
observe the neighborhood response.

Compute:

action_response_innovation =
observed_reference_response
-
predicted_reference_response_from_current_leakage_estimate.

Aggregate:
RMS across local references.

Maintain an innovation EWMA.

No extra exploratory probe is required merely to update this confidence monitor.

EVENT TRIGGER
Exploratory working threshold:

0.026

When the innovation EWMA exceeds threshold:

launch a burst of:
4 signed calibration probes.

Replace/update the local leakage estimate from the burst.

Reset the innovation confidence state.

The threshold is synthetic and NOT preregistered for Yggdrasil.

BASELINE PROBE BUDGETS FROM AR-U11

PERIODIC
2 probes every 8 post-change episodes.

Over the 70 post-change episodes:
approximately 18 extra probes per cell.

CONTINUOUS
1 probe each post-change episode:
approximately 70 extra probes.

EVENT-TRIGGERED
probe count depends on detected structural change.

NO COUPLING CHANGE
factor remains:
1

Using threshold 0.026:

mean extra probes across the full 120-episode run:
0.7136 per cell

fraction of cells triggering at least once:
13.58%

final causal-sign accuracy:
89.00%

This is the false-recalibration / stable-maintenance baseline.

COUPLING DISAPPEARS
factor:
0

first 8 post-change accuracy:
86.55%

final:
88.69%

stable >=88% for 5 episodes:
latency 8 episodes

mean extra probes:
5.7416 per cell

cells triggering:
98.99%

COUPLING HALVES
factor:
0.5

first 8:
87.70%

final:
88.56%

stable recovery:
15 episodes

mean extra probes:
3.7316

cells triggering:
68.35%

COUPLING DOUBLES
factor:
2

first 8:
86.63%

final:
88.71%

stable recovery:
8 episodes

mean extra probes:
5.6556

cells triggering:
98.94%

COUPLING TRIPLES
factor:
3

first 8:
85.62%

final:
88.97%

stable recovery:
8 episodes

mean extra probes:
5.8932

cells triggering:
99.99%

PRIMARY POSITIVE
A confidence-triggered probe burst recovered useful calibration after large structural coupling changes with far fewer dedicated probes than fixed periodic or continuous schedules.

Approximate post-change extra-probe comparison:

event-triggered:
about 4..6 probes per cell under substantial change

periodic-8:
about 18

continuous:
about 70.

In stable conditions,
event-triggered probing was almost absent.

THRESHOLD TRADEOFF
A stricter threshold:

0.028

reduced false triggering strongly.

Stable no-change:
mean extra probes:
0.032

cells triggering:
0.74%

But large-change recovery became slower / less uniform.

Examples:

factor 0:
stable recovery about 21 episodes

factor 2:
about 18

factor 3:
about 5

and factor 0.5 becomes marginal around the fixed 88% criterion.

Therefore the trigger threshold has a genuine:

PROBE COST
vs
DETECTION SENSITIVITY

tradeoff.

Do not threshold-ratchet on synthetic data.

DESIGN CONSEQUENCE
The most economical current meta-rule architecture is not:

probe at fixed high frequency forever.

Prefer:

ordinary tagged local action
->
compare expected vs observed local action footprint
->
update confidence

if confidence remains high:
reuse current causal calibration

if confidence falls:
temporarily increase local probing
->
recalibrate
->
return to low-probe maintenance.

This resembles an immune/repair-style response:

stable:
low activity

unexpected structural change:
temporary diagnostic escalation

resolved:
return to economical maintenance.

IMPORTANT DISTINCTION
The innovation monitor does NOT directly update role utility.

It only answers:

"Do I still trust my causal calibration?"

That separation prevents unexplained environmental novelty from being immediately converted into a role/sensitivity update.

CROSS-LAYER CONNECTION
The same architectural motif now appears at several scales:

INJURY
unexpected state transition
->
repair inference.

CONTEXT
unexpected / conflicting sensor state
->
consensus/freshness handling.

CAUSAL CREDIT
unexpected action footprint
->
recalibration.

A general developmental principle may be:

PREDICTION VIOLATION
should first reduce confidence / trigger diagnosis

before it directly changes the organism's long-term policy.

NEXT
AR-U13 — SHARED NOVELTY / CONFIDENCE STATE

Question:
Can one compact local confidence mechanism support:
- injury suspicion;
- context uncertainty;
- causal-calibration uncertainty

without collapsing all forms of surprise into one undifferentiated alarm?

This is a possible route to reducing engineered mechanism count.

PARALLEL
AR-C2:
multi-sensor context consensus + serial ordering.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
parallel_learners = 10000
exploratory_trigger_threshold = 0.026
