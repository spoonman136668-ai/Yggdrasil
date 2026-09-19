TITLE: DG-1A-AR-S6 — Learned Local Value-of-Information Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE-BUT-IMPERFECT LEARNED RESOURCE-ALLOCATION AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
SERIES_NOTE: SUPPLEMENTAL AR-S SERIES — CANONICAL R4 AR-U NUMBERING PRESERVED
BRANCH: dg1a-ar
PARENT: dg1a-ars5-value-of-information-urgency-audit.ice

PURPOSE
AR-S5 established a value-of-information principle,
but its comparator knew:
- functional stake;
- observation noise;
- analytic information-gain curves.

S6 removes those privileged quantities from the adaptive policy.

QUESTION
Can a bounded local learner decide how much causal evidence to collect using only:
- anonymous local context;
- current noisy consequence evidence;
- recent realized local outcome;
- local probe cost;
- a hard time/probe cap;

without being told:
- repair vs maintenance;
- true functional stake;
- true consequence noise;
- or the optimal probe count?

BOUNDARY
This is synthetic.

It does not:
- prove a real Yggdrasil local reward signal;
- define biological utility units;
- establish a production reinforcement-learning algorithm;
- authorize a global scheduler;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

LATENT EVENT MIX
Three hidden local event families occur with probabilities:

0.60
0.30
0.10

The learner never receives those family IDs.

Primary hidden wrong-decision costs:

1
4
8

Primary hidden consequence-noise SD:

0.10
0.16
0.22

True binary action signal magnitude:

0.08

Hard local probe caps:

8
8
4

The cap is treated as an observable physical deadline / maximum local sensing opportunity,
not as a semantic event label.

EXTRA-PROBE COST
Each probe beyond the first costs:

0.03 synthetic local utility units.

ANONYMOUS LOCAL CONTEXT
Each event also carries two noisy non-semantic local descriptors.

The controller receives only those descriptors.

A three-cluster context quantizer is learned from:
2500 to 3500 cue-only observations

using unlabeled k-means.

No functional stake or noise labels are used by that clustering.

CURRENT EVIDENCE
The learner always receives the first consequence probe.

It uses:
- absolute first-probe magnitude;
- anonymous context cluster;
- a locally learned consequence-noise category;
- hard probe cap;

as bounded state.

LOCAL NOISE CALIBRATION
Noise is not supplied.

For events where at least two probes are collected,
the learner updates an EMA of within-event probe dispersion.

EMA rate:
0.02.

This supplies a history-based local noise proxy.

LEARNED PROBE POLICY
The controller maintains empirical expected total local loss for possible total probe counts:

1 through local cap.

For each bounded local state:

Q(state, probes)

is updated only from the action actually taken.

Update rate:
0.01.

Exploration:
5%.

The learned loss observation is:

realized wrong-decision consequence
+
explicit probe cost.

The learner is not given the decomposition into:
stake
or
noise.

It only sees the realized scalar local consequence.

PARAMETER-INFORMED COMPARATOR
An unavailable analytic comparator is allowed to know the true:
- stake;
- noise;
- signal;
- probe cap.

It selects the probe count minimizing expected:

stake * P(wrong | k)
+
probe_cost * (k-1).

This is a diagnostic ceiling,
not an implementable local policy.

FIXED COMPARATORS
FIXED-4:
use 4 probes subject to local cap.

FIXED-8:
use 8 probes subject to local cap.

Because 10% of events have a hard cap of 4,
FIXED-8 actually averages:

7.6 probe pairs/event.

PRIMARY LONG-HORIZON RESULT
Fresh synthetic confirmation:

4 matched seeds.

Events per seed:
130000.

Evaluation begins after:
60000 events.

Mean +/- between-seed SD.

LEARNED LOCAL VoI

weighted total loss:
0.463000 +/- 0.011380

mean probes/event:
4.040364 +/- 0.348842

PARAMETER-INFORMED ANALYTIC

weighted total loss:
0.434624 +/- 0.006841

FIXED-4

weighted total loss:
0.497093 +/- 0.007569

mean probes:
4

FIXED-8

weighted total loss:
0.481647 +/- 0.007520

effective mean probes:
7.6

PRIMARY POSITIVE
After sufficient local experience,
the learned policy beats:

FIXED-4

and

FIXED-8

without knowing the hidden stake or noise.

Relative weighted-loss improvement:

vs FIXED-4:
approximately 6.9%

vs FIXED-8:
approximately 3.9%.

Relative probe use versus FIXED-8:

4.04
vs
7.6

or approximately:

46.8% fewer probes.

The learned policy still trails the parameter-informed analytic comparator by approximately:

6.5%.

Thus:
local history can recover much of the value-of-information structure,
but not all of it.

LEARNING TRANSIENT
A shorter-horizon confirmation shows the policy needs experience.

4 matched seeds.

70000 events.

Evaluation after:
25000.

LEARNED:
loss 0.499587
probes 3.218456

ANALYTIC:
0.443461

FIXED-4:
0.503533

FIXED-8:
0.490191

At this earlier maturity point:

learned local VoI
already approximately matches FIXED-4 with fewer probes,

but still underperforms FIXED-8.

Therefore:
LEARNED EVIDENCE ECONOMY HAS A MATURATION COST.

This is important for a developmental system.

A young or newly reconfigured organism should not assume its local evidence-allocation policy is already calibrated.

NONSTATIONARY STRESS
At the midpoint of a fresh 80000-event run,
the mapping from anonymous context to hidden:
- stake;
- noise;

is changed.

No semantic change label is provided.

4 matched seeds.

LATE PRE-SHIFT WINDOW

learned loss:
0.499209

mean probes:
3.106969

analytic comparator:
0.439111

FIRST 8000 POST-SHIFT EVENTS

learned loss:
1.187432

mean probes:
4.387313

analytic:
0.960342

LAST 20000 EVENTS

learned loss:
1.072246

mean probes:
5.250700

analytic:
0.980907

INTERPRETATION
The distribution shift causes a large immediate performance penalty.

The learned controller responds by:
increasing evidence expenditure

from approximately:
3.11 probes

to:
4.39

then:
5.25.

Its excess loss over the analytic comparator falls from approximately:

0.2271

early post-shift

to:

0.0913

late post-shift.

Thus:
SURPRISE RECRUITS EVIDENCE

without an explicit regime-change label.

But adaptation is not instantaneous.

PRIMARY NONSTATIONARY NEGATIVE
History-derived value estimates can become stale.

Therefore:
VALUE-OF-INFORMATION ITSELF REQUIRES RECALIBRATION.

A learned evidence allocator needs:
- recency;
- surprise sensitivity;
- or controlled forgetting.

Otherwise the resource policy inherits the same stale-prior problem found in the H-series.

DELAYED-CONSEQUENCE STRESS
Short consequence delay was not automatically harmful.

In a stationary environment,
delayed updates introduced extra inertia and often reduced noisy policy chasing,
while increasing probe use.

This means:

DELAY
!=
AUTOMATIC FAILURE.

However large delay becomes dangerous after a regime change.

Fresh nonstationary stress:

3 matched seeds.

POST-SHIFT FIRST 8000 EVENTS.

DELAY 500:

learned loss:
1.209450

probes:
4.766375

analytic:
0.935320

DELAY 2000:

learned:
1.472253

probes:
3.390375

analytic:
0.935320

DELAY 5000:

learned:
1.687898

probes:
2.429917

analytic:
0.935320

LATE POST-SHIFT WINDOW

DELAY 500:
loss 1.083439
probes 5.684617
analytic 0.972218

DELAY 2000:
loss 1.080956
probes 5.963533
analytic 0.972218

DELAY 5000:
loss 1.118057
probes 5.856333
analytic 0.972218

PRIMARY DELAY RESULT
Long reward/consequence delay creates a severe:
CREDIT-LATENCY
problem immediately after distribution shift.

The controller continues acting from obsolete evidence economics until new outcomes arrive.

Once delayed feedback accumulates,
it partially recovers by recruiting more evidence.

Therefore local VoI needs to track:

not only
UNCERTAINTY

but also
FEEDBACK AGE / CREDIT LATENCY.

CONFOUNDED-CONSEQUENCE STRESS
A separate stress introduces an unrelated time-dependent improvement into the observed outcome.

Each extra probe makes the observed consequence look better by a synthetic confounding slope,
even though the true causal value of probing is unchanged.

The learner is evaluated on true unconfounded loss.

3 matched seeds.

65000 events.

Evaluation after 25000.

CONFOUND = 0

true loss:
0.492616

probes:
3.205533

CONFOUND = 0.03 PER EXTRA PROBE

true loss:
0.489983

probes:
3.427217

CONFOUND = 0.06

true loss:
0.490158

probes:
4.833883

CONFOUND = 0.09

true loss:
0.491089

probes:
5.087692

PRIMARY CONFOUNDING NEGATIVE
The learned controller mistakes:

CORRELATION WITH WAITING / PROBE COUNT

for

CAUSAL VALUE OF ADDITIONAL EVIDENCE.

Probe expenditure rises from:

3.21

to:

5.09

without a corresponding true-loss improvement.

Thus:
A LEARNED VoI CONTROLLER CAN WASTE ADAPTIVE RESOURCES
EVEN WHEN TASK ACCURACY LOOKS STABLE.

This is directly analogous to the earlier causal-credit result:

PREDICTION QUALITY
!=
CAUSAL-CONTROL VALIDITY.

Now:

OUTCOME CORRELATION
!=
CAUSAL VALUE OF INFORMATION.

ARCHITECTURAL CONSEQUENCE
The local adaptive-resource loop now needs at least:

CURRENT UNCERTAINTY

+

ANONYMOUS LOCAL CONTEXT

+

HISTORY-DERIVED NOISE / RELIABILITY

+

RECENT REALIZED FUNCTIONAL CONSEQUENCE

+

PROBE COST

+

DEADLINE / LOCAL CAP

+

RECENCY / SURPRISE

+

CREDIT LATENCY

+

CAUSAL CONTROL FOR WAITING / EXOGENOUS RECOVERY

->

HOW MUCH EVIDENCE TO COLLECT NOW.

DO NOT CENTRALIZE THIS
The benchmark uses one abstract local learner per decision stream.

It does not justify:
- a global evidence scheduler;
- a global semantic repair controller;
- a fixed role hierarchy.

The intended architectural interpretation remains local and bounded.

RELATION TO S4 / S5
S4:
evidence is a finite adaptive resource.

S5:
analytic value-of-information beats uncertainty-only or stake-only allocation.

S6:
much of that allocation principle can be learned from local history without privileged stake/noise labels.

But S6 also establishes three new failure modes:

1.
MATURATION LAG

2.
STALE VALUE ESTIMATES AFTER DISTRIBUTION SHIFT

3.
CAUSAL CONFOUNDING OF PROBE VALUE.

RELATION TO H5-H7
The same meta-principle appears in both memory and resource allocation:

A USEFUL LEARNED PRIOR
MUST BE SUPPRESSIBLE
WHEN CURRENT EVIDENCE NO LONGER FITS IT.

For memory:
this is expression trust / manifold-fit confidence.

For evidence allocation:
this is VoI-policy trust / recalibration confidence.

CURRENT EMERGING META-ARCHITECTURE
Fast local behavior should be controlled by several confidence layers that answer different questions:

STATE CONFIDENCE
what is probably happening?

CAUSAL-CREDIT CONFIDENCE
did my action cause the observed consequence?

MODEL-FIT CONFIDENCE
does my inherited structure represent this state?

VoI-POLICY CONFIDENCE
does my learned evidence-allocation rule still predict useful spending?

These should not be collapsed into one scalar.

DECISION
AR-S6 is POSITIVE-BUT-IMPERFECT.

Supported synthetically:

- useful local evidence allocation can be learned without true stake/noise labels;
- learned policy can beat fixed budgets at lower resource use after sufficient experience;
- surprise recruits additional evidence under nonstationarity;
- learned evidence economics require maturation;
- large feedback delay creates acute post-shift adaptation lag;
- confounded outcome timing can cause severe over-probing without true benefit.

Not demonstrated:

- real Yggdrasil local reward;
- real target-free functional stake;
- real causal VoI estimation;
- optimal policy representation;
- bounded implementation on current Yggdrasil cells;
- robustness to adversarial reward manipulation.

NEXT CLEAN EXPERIMENT
AR-S7 — CAUSALLY CONTROLLED LEARNED VALUE-OF-INFORMATION

Question:

Can the evidence allocator distinguish:

THE PROBE HELPED

from

THE WORLD CHANGED WHILE I WAS PROBING?

Candidate comparison:

A.
naive learned VoI from raw realized outcome;

B.
matched no-extra-probe control;

C.
local disturbance / waiting baseline;

D.
confidence-weighted causal VoI update.

Use the same confounding stress that caused S6 over-probing.

Desired:

retain most of S6's adaptive allocation benefit

while preventing:
spontaneous recovery
or
time-correlated environmental drift

from being credited to extra evidence collection.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_long_horizon_seeds = 4
primary_events_per_seed = 130000
primary_eval_start = 60000
nonstationary_seeds = 4
nonstationary_events = 80000
large_delay_seeds = 3
confounding_seeds = 3
