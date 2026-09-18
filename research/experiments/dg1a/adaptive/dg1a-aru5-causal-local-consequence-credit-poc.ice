TITLE: DG-1A-AR-U5 — Causal Local Consequence Credit POC
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE META-RULE PRECURSOR
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru4-redundant-local-credit-cue-audit.ice

PURPOSE
Remove the hand-labelled mapping:

local cue
->
declared role utility

from the adaptive-role mechanism.

Question:
Can a cell discover whether increasing or decreasing a local role expression is useful by perturbing that role and observing only a LOCAL CONSEQUENCE scalar?

This is the closest current synthetic precursor to a bounded lifetime meta-rule.

BOUNDARY
This is NOT a trained Yggdrasil result.

This POC:
- uses a synthetic local consequence function;
- uses derivative-free perturb-and-observe adaptation;
- does not update globally stored neural-network weights;
- does not expose a global task score to cells;
- does not execute or modify STAB-18-R1;
- does not establish that Yggdrasil already has the required consequence signal.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BODY
149-cell radius-7 four-neighbor disk geometry.

LOCAL ACTIVE FUNCTIONS
relay
repair
inhibitor
growth

Each cell stores four bounded role gates:
a_i in [0,1]

No global role ratio is supplied.

HIDDEN LOCAL DEMAND
The synthetic environment contains local functional demands:

relay:
communication-corridor demand

repair:
damage-zone demand

inhibitor:
stress-zone demand

growth:
capacity-deficit demand

The cell is NOT given the demand vector as a utility input.

LOCAL CONSEQUENCE
Each cell can observe only one scalar local loss.

For cell x:

LocalLoss(x) =
sum_r [
    Demand(x,r) * (1 - a(x,r))^2
]
+
sum_r [
    RoleCost(r) * a(x,r)^2
]
+
0.25 * max(
    sum_r a(x,r) - 1.25,
    0
)^2

Role costs:

relay:
0.12

repair:
0.10

inhibitor:
0.10

growth:
0.12

Interpretation:
the local consequence combines:
- unmet local functional need;
- local metabolic/role cost;
- excess simultaneous specialization cost.

Cells do not receive the separate terms or their gradients.

CAUSAL / DERIVATIVE-FREE UPDATE
For an updating cell:

1. choose one role gate r;
2. form:
   a_plus  = a_r + epsilon
   a_minus = a_r - epsilon
3. evaluate the cell's own local consequence under:
   current
   plus
   minus
4. adopt the lowest-consequence local state.

epsilon:
0.06

stochastic cell update probability:
0.5

No global gradient is used.

No role-specific analytic utility is supplied.

This is a bounded local coordinate-search meta-rule.

STATIC DEVELOPMENT
Initial role gates:
approximately 0.20 plus small random heterogeneity.

Horizontal communication demand:
220 adaptation steps.

MOVING-DEMAND TEST
Then rotate the communication corridor by 90 degrees.

Vertical adaptation:
180 steps.

Fresh clean seeds:
8

CLEAN RESULTS

Mean pre-switch local consequence:
0.105368

Immediate consequence after switching demand:
0.244970

Final consequence:
0.105884

Recovery criterion:
local consequence returns to within 10% of that seed's pre-switch value for 10 consecutive steps.

Recovery:
8/8

Mean switching latency:
87 steps

SPATIAL RELAY REORGANIZATION

Before switch:

horizontal-corridor relay:
0.86026

vertical-corridor relay:
0.37029

After switch:

horizontal-corridor relay:
0.37688

vertical-corridor relay:
0.85669

Global relay load changed only modestly.

Therefore:
the perturb-and-observe rule discovers a different spatial specialization from consequence alone.

PRIMARY POSITIVE
A bounded local meta-rule can learn:

increase this function here

or

retire this function here

without receiving:
- a named role target;
- a global role histogram;
- a global performance signal;
- an analytic local utility gradient.

This is a materially stronger precursor than the hand-labelled utility market.

IMPORTANT LIMITATION
The local consequence function itself is still hand-designed.

The experiment therefore does NOT answer:
where the organism gets a trustworthy local consequence scalar.

That remains the major scientific problem for real meta-rules.

NOISY LOCAL CONSEQUENCE
A follow-up adds independent Gaussian observation noise to each local consequence measurement.

Because the perturbation decision compares:
current
plus
minus

the experiment also tested averaging multiple independent consequence probes.

Fresh exploratory seeds:
4 per condition.

NOISE sigma = 0.005

1 probe:
pre loss 0.10877
final 0.10932
recovery 4/4
median latency 76.5

4 probes:
pre 0.10696
final 0.10738
recovery 4/4
median latency 77

8 probes:
pre 0.10640
final 0.10680
recovery 4/4
median latency 77.5

NOISE sigma = 0.010

1 probe:
pre 0.11285
final 0.11335
recovery 4/4
median latency 80.5

4 probes:
pre 0.10877
final 0.10932
recovery 4/4
median latency 76.5

8 probes:
pre 0.10765
final 0.10813
recovery 4/4
median latency 76.5

NOISE sigma = 0.020

1 probe:
pre 0.12113
final 0.12237
recovery 4/4
median latency 89

4 probes:
pre 0.11285
final 0.11335
recovery 4/4
median latency 80.5

8 probes:
pre 0.11045
final 0.11093
recovery 4/4
median latency 78

NOISE sigma = 0.050

1 probe:
pre 0.14361
final 0.14793
recovery 4/4
median latency 116.5

4 probes:
pre 0.12515
final 0.12689
recovery 4/4
median latency 91.5

8 probes:
pre 0.11920
final 0.12041
recovery 4/4
median latency 88

INTERPRETATION OF NOISY RESULT
The relative recovery criterion alone can be misleading.

At sigma=0.05 with one probe,
the system still returns close to ITS OWN noisy pre-switch baseline,
but that baseline is already much worse than the clean baseline.

Therefore future meta-rule evaluation must report BOTH:

RELATIVE ADAPTIVE RECOVERY

and

ABSOLUTE FUNCTION / CONSEQUENCE QUALITY.

Do not call a noisy mechanism robust merely because it can recover to a degraded baseline.

REDUNDANT PROBE RESULT
Averaging several independent local consequence observations improves:
- absolute local consequence;
- switching latency;
- stability.

This is consistent with AR-U4,
but the same caution applies:

useful repeated evidence requires meaningfully independent measurement noise.

CAUSAL-CREDIT INTERPRETATION
The POC supports a future architecture of:

small bounded role perturbation
->
observe local consequence
->
retain/reverse role change
->
accumulate bounded local sensitivity

rather than:

global error
->
directly command cell identity.

This resembles a local bandit / derivative-free adaptation loop.

It is compatible with the standing meta-rule boundary:

do not modify globally stored shared network weights during organism lifetime.

WHAT REMAINS UNSOLVED
The crucial unsolved real-Yggdrasil questions are:

1. What local consequence variable is available without leaking global supervision?
2. How is consequence attributed to a specific recent role/action when several processes change simultaneously?
3. How long is the causal delay?
4. How is exogenous disturbance separated from self-caused improvement?
5. How does the organism prevent exploratory perturbations from destabilizing a mature structure?
6. Can this mechanism operate through existing hidden state rather than explicit engineered role registers?

NEXT
AR-U6 — CAUSAL CREDIT WITH DELAYED / CONFOUNDED CONSEQUENCES

Introduce:
- delayed local effects;
- simultaneous role changes;
- environmental disturbances;
- false correlations.

Ask whether:
simple perturb-and-observe credit breaks,
and whether temporal counterfactual memory or domain-separated local probes are required.

This connects directly to the causal-probe lessons from STAB-18-R1,
without modifying R1 itself.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
clean_fresh_seeds = 8
noise_exploratory_seeds_per_condition = 4
