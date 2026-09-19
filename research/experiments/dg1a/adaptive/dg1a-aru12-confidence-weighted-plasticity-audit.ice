TITLE: DG-1A-AR-U12 — Confidence-Weighted Plasticity / Evidence Accumulation Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE TRADEOFF AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru11-adaptive-causal-baseline-gating-audit.ice

PURPOSE
AR-U11 showed that hard confidence gating improves credit fidelity but slows adaptation because many usable credit events are discarded.

This audit compares four bounded local update policies:

A. ALWAYS UPDATE
B. HARD DEFER
C. CONTINUOUS CONFIDENCE-WEIGHTED PLASTICITY
D. EVIDENCE ACCUMULATION UNTIL CONFIDENT

QUESTION
Can the organism reduce mature-state drift and false reinforcement without giving up adaptation speed?

BOUNDARY
This is a synthetic one-dimensional local role-control benchmark.

It does not:
- prove a real Yggdrasil role gate behaves one-dimensionally;
- freeze a confidence threshold;
- authorize unlimited probing;
- modify or execute STAB-18-R1;
- count as functional regeneration.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

LOCAL ROLE BENCHMARK
Bounded local role parameter:
x in [0,1]

Hidden locally optimal role expression:

episodes 0..109:
0.8

episodes 110..219:
0.2

Thus the useful specialization must reverse once.

Population:
20,000 synthetic local learners for the primary condition.

Episodes:
220

LOCAL CONSEQUENCE
Quadratic local loss:

L(x) =
(x - target)^2

The learner does NOT receive the analytic gradient.

FINITE-DIFFERENCE CONSEQUENCE PROBE
Role perturbation:

epsilon = 0.06

Evaluate:
L(x + epsilon)
L(x - epsilon)

with independent consequence observation noise.

The finite-difference estimate is converted to a local direction estimate.

Primary consequence-noise SD:
0.03

Fixed role step:
0.02

Each probe pair consumes:
2 local consequence observations.

CONFIDENCE
Estimated signal-to-noise ratio:

confidence =
abs(estimated gradient)
/
estimated gradient-noise SD.

Primary hard confidence threshold:
1.5

METHOD A — ALWAYS UPDATE
One probe pair every episode.

Always take the full bounded role step using the estimated direction.

METHOD B — HARD DEFER
One probe pair every episode.

Take a full step only if:
confidence >= 1.5

otherwise:
hold the role state.

METHOD C — CONTINUOUS CONFIDENCE-WEIGHTED PLASTICITY
One probe pair every episode.

Always permit an update,
but multiply the role step by:

gain =
tanh(confidence / 1.5)

Low-confidence evidence therefore produces a small change rather than:
full change
or
no change.

METHOD D — EVIDENCE ACCUMULATION
Start with one probe pair.

If confidence < 1.5:
take another independent probe pair.

Continue until:
confidence >= 1.5

or

maximum probe pairs = 8.

Average the evidence.

Take a full role step only if threshold is reached.

PRIMARY RESULTS
consequence noise SD:
0.03

ALWAYS UPDATE

pre-switch mean absolute role error:
0.03779

final last-20 error:
0.03782

stable post-switch recovery:
95.20%

median switching latency:
45 episodes

false update fraction among updates:
26.39%

updates per agent:
220

consequence observations per agent:
440

mature-state role movement over final 30 pre-switch episodes:
0.6000

HARD DEFER

pre-switch error:
0.02954

final:
0.02931

stable recovery:
88.79%

median latency:
68

false-update fraction:
6.52%

updates per agent:
69.23

consequence observations:
440

mature-state movement:
0.08643

PRIMARY HARD-GATE RESULT
Hard deferral strongly suppresses mature-state drift and wrong updates,
but it learns substantially more slowly and fails to recover in more agents.

CONTINUOUS CONFIDENCE WEIGHTING

pre:
0.02449

final:
0.02446

stable recovery:
99.01%

median latency:
52

false-direction event fraction:
30.54%

episodes with some update:
220

consequence observations:
440

mature-state movement:
0.26233

INTERPRETATION
Continuous weighting can tolerate many imperfect direction estimates because low-confidence errors produce only small role motion.

Therefore:
FALSE UPDATE COUNT ALONE
is not enough to characterize plasticity safety.

UPDATE MAGNITUDE matters.

EVIDENCE ACCUMULATION

pre:
0.01898

final:
0.01893

stable recovery:
100.00%

median latency:
31

false-update fraction among accepted updates:
11.51%

mean accepted updates per agent:
124.15

mean consequence observations per agent:
2167.09

mature-state movement:
0.25408

PRIMARY POSITIVE
Adaptive evidence collection achieves the best combination of:
- low final error;
- reliable switching;
- low latency;
- bounded drift;

but requires about:
4.9x
the consequence observations of the fixed one-pair methods.

Thus it trades:
SENSING / EXPLORATION COST
for
CAUSAL-CREDIT RELIABILITY.

NOISE STRESS
Fresh populations:
12,000 learners per strategy/condition.

NOISE SD = 0.015

always:
final error 0.02668
recovery 99.80%
median latency 33

hard:
0.01612
99.99%
39

continuous:
0.01741
100%
35

accumulate:
0.01304
100%
28

NOISE SD = 0.030

always:
0.03737
95.29%
45

hard:
0.02952
88.87%
69

continuous:
0.02445
99.08%
52

accumulate:
0.01904
100%
31

NOISE SD = 0.050

always:
0.04872
81.63%
59

hard:
0.07427
28.56%
87

continuous:
0.03635
79.95%
74

accumulate:
0.02493
99.86%
39

NOISE SD = 0.080

always:
0.06405
58.61%
69

hard:
0.13517
4.76%
90

continuous:
0.07132
33.78%
86

accumulate:
0.03161
96.57%
54

KEY NOISE RESULT
The hard gate becomes pathological under high noise:
it rejects too much evidence and stops adapting.

Continuous confidence weighting degrades more gracefully,
but fixed one-pair evidence eventually becomes too unreliable.

Evidence accumulation remains robust much longer because it spends more observations when uncertainty is high.

PROBE-COST GROWTH
Mean consequence observations per agent:

noise 0.015:
~2056

noise 0.030:
~2167

noise 0.050:
~2273

noise 0.080:
~2379

The mechanism automatically spends more evidence under harder conditions.

This is desirable in principle,
but a real organism cannot treat sensing/probing as free.

ARCHITECTURAL CONSEQUENCE
The preferred adaptive-plasticity shape is moving toward:

LOW UNCERTAINTY
->
small number of probes
->
normal bounded plasticity

HIGH UNCERTAINTY
->
reduce update gain
and/or
collect more evidence

VERY HIGH / UNRESOLVED UNCERTAINTY
->
hold mature role state.

This is closer to:
adaptive computation / adaptive sensing

than:
fixed learning rate.

IMPORTANT DISTINCTION
A mature organism should not maximize:
number of role updates.

It should maximize:
useful consequence improvement per adaptation cost.

Future evaluation therefore needs:

FUNCTIONAL BENEFIT

FALSE / HARMFUL ROLE MOVEMENT

PROBE / SENSING COST

TIME TO ADAPT

MATURE-STATE DRIFT

simultaneously.

DO NOT optimize only one.

PREFERRED COMBINED RULE
A plausible bounded controller is:

confidence
->
plasticity gain

and

if confidence remains low:
->
request additional sparse evidence

subject to a local probe budget.

This combines:
continuous confidence weighting
with
bounded evidence accumulation.

NEXT
AR-U13 — BUDGETED ACTIVE EVIDENCE COLLECTION

Give the local organism a finite perturbation/sensing budget.

Question:
Can it learn when additional causal evidence is worth its cost?

Compare:
- fixed 1 probe;
- fixed 4 probes;
- fixed 8 probes;
- confidence-triggered adaptive probes;
- explicit probe-cost utility.

Measure:
- functional adaptation;
- total probes;
- adaptation latency;
- mature drift;
- net utility after probe cost.

PARALLEL
AR-C1 — repeated decentralized context ordering.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_population = 20000
noise_stress_population_per_condition = 12000
