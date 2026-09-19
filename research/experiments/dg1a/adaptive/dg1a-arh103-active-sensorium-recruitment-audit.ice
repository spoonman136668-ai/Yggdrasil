TITLE: DG-1A-AR-H103 — Active Sensorium Recruitment / Residual-Driven Sensing Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE COST-AWARE SENSOR RECRUITMENT RESULT + RE-AUDITION / SENSOR-FIT TRADEOFF
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh102-latent-interaction-context-audit.ice

PURPOSE
H102 assumes:
a useful local cue
is already being observed.

H103 removes that privilege.

QUESTION
When persistent causal residuals suggest:
MISSING CONTEXT INFORMATION,

can the organism recruit:
additional sensing
selectively

rather than:
observing every candidate variable forever?

A second question:

what happens when:
the currently useful sensor
later becomes:
uninformative

and:
a previously dormant sensor
becomes useful?

BOUNDARY
This is synthetic.

It does not:
- create entirely new physical sensors;
- freeze the candidate sensor pool;
- freeze sensing costs;
- prove log-loss is the final information-value metric;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

HIDDEN INTERFACE MODE
Same H102-style latent mode.

Interface outcome probability:

Z=0:
0.88.

Z=1:
0.35.

Candidate sensors are:
unlabelled local variables.

Each has:
different context information
and
different per-observation cost.

PRIMARY CANDIDATE SENSOR POOL

S0
strong cue.
context separation:
mu = 0.8.
cost:
0.008.

S1
moderate cheap cue.
mu = 0.5.
cost:
0.002.

S2
very strong but expensive cue.
mu = 1.15.
cost:
0.05.

S3
weak cheap cue.
mu = 0.25.
cost:
0.001.

S4
initially uninformative.
mu = 0.
cost:
0.001.

For informative cues:

C | Z=0 ~ Normal(-mu,1).

C | Z=1 ~ Normal(+mu,1).

SENSOR AUDITION
Primary:

60 training observations
+
60 independent validation observations
per candidate.

Each candidate learns:
a simple one-threshold context model.

The validation score measures:

held-out predictive log-loss reduction
minus:
sensor-use cost.

No semantic cue label is supplied.

DEPLOYMENT
600 subsequent interface events.

PRIMARY MATCHED AUDITION CONFIRMATION
4,000 matched synthetic auditions.

COST-AWARE SINGLE-SENSOR RECRUITMENT

mean net deployment value after:
audition cost
and
sensor-use cost:

+2.18
synthetic information-value units
over:
600 deployment events.

mean deployed net value:
+0.0160 / event
before:
one-time audition cost.

INFORMATION-MAXIMIZING RECRUITMENT

mean total:
+2.81.

mean deployed:
+0.0171 / event.

RANDOM SENSOR

mean total:
-8.26.

mean deployed:
approximately -0.00137 / event.

PRIMARY RECRUITMENT POSITIVE
Residual-driven sensor audition can:
pay for itself

when:
the selected cue provides:
enough predictive consequence information.

Random sensing does not.

OBSERVE-EVERYTHING CONTROL
A multivariate model observes:
all five candidate sensors
continuously.

1,000 matched deployment tests.

Mean information gain after:
continuous sensor cost:

approximately:
+0.00179 / event.

This is:
positive
but
far below:
targeted recruited sensing.

PRIMARY SENSORIUM-SPARSITY RESULT
Permanently observing:
every available variable

throws away much of:
the value
of
resource-priced sensing.

The goal is not:

MAXIMUM SENSOR COUNT.

It is:

USEFUL INFORMATION
PER
ACTIVE SENSING COST.

AUDITION-LENGTH SWEEP
Training and validation sizes
were varied together.

The resulting net value
is:
non-monotonic.

Longer auditions:
reduce model-selection noise

but:
consume more sensing resource
before:
deployment.

Therefore:

MORE EVIDENCE
IS NOT AUTOMATICALLY
MORE VALUABLE.

Sensor recruitment itself
is:
a value-of-information decision.

SENSOR-LIFECYCLE STRESS
After initial recruitment,
the environment changes.

At:
step 600

the sensing geometry shifts.

PHASE 1

S0:
strong.

S1:
moderate.

S2:
very strong / expensive.

S3:
weak.

S4:
uninformative.

PHASE 2

S0:
becomes uninformative.

S1:
weakens strongly.

S2:
weakens.

S3:
remains weak.

S4:
becomes strongly informative:
mu = 0.95.

No:
sensor-regime-change label
is supplied.

POLICIES

FIXED ACTIVE SENSOR

never re-evaluate:
the chosen sensor.

PERIODIC FULL RE-AUDITION

rerun:
the full sensor audition
at:
fixed intervals.

RESIDUAL-TRIGGERED RE-AUDITION

track:
active sensor predictive fit
against:
the unspecialized baseline.

Persistent:
active-sensor excess log loss

opens:
a new sensor audition.

PRIMARY LIFECYCLE CONFIRMATION
300 matched 1,200-event streams.

FIXED

mean lifecycle net:
-44.55.

final active S4:
3.7%.

No adaptation mechanism.

PERIODIC RE-AUDITION

mean net:
-28.27.

mean sensor switches:
1.62.

final S4:
71.3%.

mean detected-S4 switch latency:
approximately 360 steps
after the phase change.

RESIDUAL-TRIGGERED

mean net:
-20.11.

mean switches:
2.66.

final S4:
82.0%.

mean S4 switch latency:
approximately 247.7 steps.

PRIMARY RE-AUDITION POSITIVE
The active sensing policy can:
recover
when:
the old sensor stops carrying:
useful context information.

Residual-triggered recruitment:

finds the new useful sensor:
more reliably

and:
approximately 112 steps earlier

than:
the periodic comparator
in the tested stream.

STRICT-COST INTERPRETATION
The lifecycle net values are:
negative
under the deliberately strict accounting used for:
multiple full auditions.

This is important.

Sensor adaptation is not:
free.

The positive result is:
comparative and architectural:

residual-triggered re-audition
wastes substantially less value
than:
staying fixed
or:
blind periodic re-audition.

A production design needs:
cheaper staged auditions
or
longer amortization horizons.

SENSOR-FIT CONFIDENCE
H103 suggests each recruited sensor should carry:

CURRENT FIT

+

INFORMATION VALUE

+

ACTIVE OBSERVATION COST

+

LAST VALIDATION SUPPORT

+

FAILURE PROVENANCE

+

DORMANT / ACTIVE STATUS.

A sensor can remain:
known
without remaining:
actively sampled.

CURRENT SENSORIUM LIFECYCLE

UNEXPLAINED RESIDUAL

->
TEMPORARY SENSOR AUDITION

->
INDEPENDENT VALIDATION

->
ACTIVE SENSOR RECRUITMENT

->
FIT MONITORING

->
SUPPRESSION / DORMANCY

->
RE-AUDITION
when:
fit collapses.

RELATION TO H34
Dormant capabilities:
should not be:
deleted
because:
they are currently unused.

H103:
unused sensors
may also retain:
future option value.

A dormant cue can later become:
the most informative variable.

RELATION TO H64
H64:
communication code
is:
adaptive state.

H103:
observation code / active sensorium
is also:
adaptive state.

The organism can change:
WHAT IT PAYS ATTENTION TO.

RELATION TO H84
H84:
choose:
which functional challenge
has:
highest information value.

H103:
choose:
which internal variable
is:
worth observing.

Both are:
evidence-allocation problems.

GENERAL PRINCIPLE
DO NOT BUILD
A PERMANENT MAXIMAL SENSORIUM

if:
most variables are:
contextually useless
or
expensive.

Instead:

RECRUIT SENSING
WHEN
UNEXPLAINED RESIDUAL
JUSTIFIES
THE COST.

Then:
retire active observation
when:
the cue stops helping.

DECISION
AR-H103 is POSITIVE
for:
active cost-aware sensorium recruitment

WITH:
a re-audition / fit-monitoring cost tradeoff.

Supported synthetically:

- residual-driven sensor audition can identify useful context variables;
- random sensor choice is harmful after sensing cost;
- observing every candidate continuously is much less efficient than targeted recruitment;
- audition duration has diminishing / non-monotonic value;
- previously useful sensors can become stale;
- dormant sensors can later become valuable;
- residual-triggered re-audition outperforms fixed sensing and blind periodic re-audition in the tested shift;
- sensor capability and current observation authority should remain separate.

Not demonstrated:

- creation of new derived observables;
- sensor fusion;
- safe physical sensing;
- optimal staged audition;
- distributed sensor recruitment;
- sensor inheritance across division.

NEXT HIGH-VALUE MOVE
AR-H104 — DERIVED SENSOR SYNTHESIS / OBSERVABLE CONSTRUCTION

H103 can select:
which existing variable
to observe.

But:
the useful context variable
may not exist:
as one raw sensor.

Question:

can the organism construct:
a NEW DERIVED OBSERVABLE
from:
cheap raw signals?

Candidate setup:

no single raw variable
predicts:
the latent interface mode
well.

But:
a simple relation does.

Examples:

difference:
x1 - x2.

ratio.

coincidence.

temporal derivative.

local neighbor contrast.

Compare:

A.
raw-sensor selection only;

B.
observe every raw variable;

C.
small library of generic sensor transforms;

D.
residual-driven derived-observable nomination;

E.
validation / memory price;

F.
spurious algebraic sensor under noise.

Desired:

MISSING CONTEXT
->
CREATE
A SMALL USEFUL MEASUREMENT

rather than:
only:
look harder
at the existing variables.

This would make:
the effective sensorium
generative,
not just:
selective.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
candidate_sensors = 5
audition_train = 60
audition_validation = 60
deployment_events = 600
lifecycle_stream = 1200
lifecycle_matched_streams = 300
