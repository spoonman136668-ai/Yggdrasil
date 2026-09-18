TITLE: DG-1A-AR-U7 — Cheap Causal-Credit Approximation Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE APPROXIMATION AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru6-delayed-confounded-causal-credit-audit.ice

PURPOSE
Compare cheaper local causal-credit approximations against the expensive matched intact-vs-perturbed future control established in AR-U6.

Question:
Can local cells recover useful causal credit without running a full duplicate future trajectory for every perturbation?

BOUNDARY
This is synthetic.

It does not:
- authorize a Yggdrasil implementation;
- establish that a suitable local disturbance reference already exists;
- modify or execute STAB-18-R1;
- count as real functional regeneration.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BENCHMARK
A single bounded local role perturbation has true causal effect:

beta = +/- 0.025

The effect becomes fully expressed four steps after a declared causal delay.

Delays tested:
1
4
8
16
24

Local consequence contains:

COMMON ENVIRONMENTAL RANDOM-WALK DRIFT
per-step sigma:
0.05

LOCAL IDIOSYNCRATIC DRIFT
per-step sigma:
0.01

MEASUREMENT NOISE
sigma:
0.01

Trials:
200,000 per delay for the primary comparison.

METHOD A — NAIVE DELAYED CONSEQUENCE
One positive perturbation.

Estimate:
future consequence
-
pre-perturbation consequence

No disturbance control.

METHOD B — SPARSE SIGNED ACTION-TAGGED PROBES
Eight one-role-at-a-time perturbations.

Each probe sign is independently:
+1
or
-1

and is pseudorandomly domain-separated from environmental disturbance.

Estimate:

mean(
    probe_sign
    *
    delayed_consequence_change
)

This is a node-perturbation / eligibility-style local estimator.

No duplicate future state is required.

METHOD C — SPARSE TAGGED PROBES + LOCAL DISTURBANCE REFERENCE
Same eight signed probes.

Additionally subtract a local reference estimate built from four non-perturbed neighboring/reference observations that share the environmental disturbance.

Estimate:

mean(
    probe_sign
    *
    (
        local_consequence_change
        -
        local_reference_change
    )
)

The reference does not receive the role perturbation.

Primary benchmark assumes the reference shares the common disturbance exactly while retaining independent local/reference noise.

This is a strong synthetic assumption and is stress-tested separately below.

METHOD D — SHORT PAIRED LOCAL FUTURE
Matched intact/perturbed local future for only:
8 steps.

Same disturbance realization.

This is cheaper than a full paired horizon,
but it can only detect effects that have already arrived.

METHOD E — FULL PAIRED FUTURE CONTROL
Matched intact/perturbed future through:

delay + 4 steps

with the same disturbance realization.

This is the high-information but expensive reference control.

PRIMARY CAUSAL-SIGN ACCURACY

delay 1:
naive:
58.54%

sparse tagged x8:
73.12%

tagged + local reference x8:
99.15%

short paired 8:
96.16%

full paired:
96.15%

delay 4:
naive:
56.78%

sparse x8:
68.73%

reference x8:
97.77%

short paired 8:
96.08%

full paired:
96.15%

delay 8:
naive:
55.55%

sparse x8:
65.58%

reference x8:
95.48%

short paired 8:
49.85%

full paired:
96.06%

delay 16:
naive:
54.22%

sparse x8:
62.27%

reference x8:
91.12%

short paired 8:
49.83%

full paired:
96.05%

delay 24:
naive:
53.65%

sparse x8:
60.35%

reference x8:
87.69%

short paired 8:
50.06%

full paired:
96.12%

PRIMARY FINDINGS

1.
A fixed short paired probe is excellent only if its horizon reaches the causal effect.

Once the true effect arrives later than the short probe window,
accuracy collapses to chance.

Therefore:
SHORT COUNTERFACTUAL != UNIVERSAL CHEAP SOLUTION.

2.
Sparse signed perturbation reduces systematic confounding because disturbance is multiplied by an independent random action sign and averages toward zero.

However:
eight probes alone remain too noisy for long delays.

3.
Subtracting a LOCAL disturbance reference can recover most of the causal signal without duplicate future simulation.

At delay 16:

sparse x8:
62.27%

local-reference x8:
91.12%

full paired:
96.05%

PROBE-COUNT TRADEOFF
Delay:
16

same local-reference estimator

K=1:
68.31%

K=2:
75.25%

K=4:
82.84%

K=8:
91.04%

K=16:
97.15%

K=32:
99.63%

Therefore there is a continuous trade:

more local perturbation evidence
->
higher causal reliability
->
longer adaptation latency / more exploration.

Do not freeze K from this synthetic audit.

REFERENCE-QUALITY STRESS
Delay:
16

K:
8

Let rho denote the correlation between the environmental component of the local consequence and the environmental component of the reference.

rho = 0.00:
58.85%

rho = 0.25:
59.86%

rho = 0.50:
61.95%

rho = 0.75:
66.47%

rho = 0.90:
73.63%

rho = 0.95:
78.89%

rho = 1.00:
91.09%

IMPORTANT NEGATIVE
A poor local reference does not magically solve credit assignment.

The reference must actually predict/shared-control the disturbance affecting the perturbed cell.

Therefore:
LOCAL REFERENCE
is an information requirement,
not merely an extra channel.

MOVING-OPTIMUM ADAPTATION TEST
A second synthetic benchmark directly optimizes one bounded local role gate.

Hidden optimum:

first half:
0.8

second half:
0.2

The optimum switches at episode:
90

Total episodes:
180

Population:
1000 independent local learners

Role perturbation:
epsilon = 0.06

Role update step:
0.02

Causal delay:
16

Same environmental/noise model.

Stable recovery criterion:
absolute role error <= 0.05
for 10 consecutive episodes.

RESULTS

NAIVE
pre-switch last-10 mean absolute error:
0.2065

post-switch final last-10 error:
0.2089

stable recovery:
14.3%

median successful latency:
57 episodes

SPARSE TAGGED — K=4
pre:
0.1120

post:
0.1414

stable recovery:
13.4%

median:
68

SPARSE TAGGED — K=8
pre:
0.0834

post:
0.0981

stable recovery:
24.1%

median:
64

SPARSE TAGGED — K=16
pre:
0.0659

post:
0.0677

stable recovery:
41.8%

median:
63

LOCAL-REFERENCE TAGGED — K=4
pre:
0.0419

post:
0.0419

stable recovery:
80.0%

median:
48

LOCAL-REFERENCE TAGGED — K=8
pre:
0.0373

post:
0.0368

stable recovery:
91.8%

median:
43

LOCAL-REFERENCE TAGGED — K=16
pre:
0.0310

post:
0.0307

stable recovery:
97.5%

median:
38

SHORT PAIRED 8
At delay 16 the causal effect has not arrived.

pre:
0.3413

post:
0.3242

stable recovery:
21.6%

The occasional threshold crossing is random wandering,
not stable useful adaptation.

FULL PAIRED CONTROL
pre:
0.0233

post:
0.0229

stable recovery:
99.8%

median:
31

PRIMARY ADAPTATION RESULT
A local-reference + sparse action-tag mechanism approaches the adaptation quality of the full paired counterfactual without duplicating a complete future trajectory.

At K=16:

stable recovery:
97.5%

vs

full paired:
99.8%

final absolute error:
0.0307

vs

0.0229.

This is the strongest current cheap causal-credit approximation.

COMPUTE / TIME DISTINCTION
Do not conflate:

SIMULATION COMPUTE

with

BIOLOGICAL / LIVE ADAPTATION TIME.

FULL PAIRED FUTURE
requires duplicated future-state computation for every tested perturbation.

SPARSE TAGGED CREDIT
requires more real perturbation observations over time,
but no duplicate counterfactual organism.

LOCAL REFERENCE
requires an additional local disturbance estimate,
ideally from already-available neighborhood state.

Therefore sparse reference credit may trade:

less duplicated compute

for

more adaptation time.

LITERATURE ALIGNMENT
Learning From the Past with Cascading Eligibility Traces
ICLR 2026

reports that ordinary exponentially decaying eligibility traces blur events over long delays and introduces state-space/cascading traces for more temporally precise delayed credit.

TESS:
A Scalable Temporally and Spatially Local Learning Rule for Spiking Neural Networks
IJCNN 2025
DOI:
10.1109/IJCNN64981.2025.11227652

shows a temporally and spatially local learning rule using eligibility-trace-like mechanisms and local signals with memory/computation scaling linearly in neuron count.

Structural-credit literature also connects node perturbation with local policy-gradient / REINFORCE-style estimators.

These papers support the plausibility of local temporal/action traces.
They do NOT establish the Yggdrasil mechanism measured here.

ARCHITECTURAL CONSEQUENCE
The current preferred cheap credit abstraction is:

SPARSE ONE-ROLE PERTURBATION

+
ACTION TAG / ELIGIBILITY STATE

+
LOCAL DISTURBANCE PREDICTION OR REFERENCE

+
DELAYED LOCAL CONSEQUENCE

->
BOUNDED ROLE UPDATE.

Do not use:

many simultaneous role perturbations
+
one later scalar reward.

Do not use:

short fixed paired probes
for effects whose causal horizon is not known to fit inside the probe.

NEW HARD QUESTION
What real Yggdrasil signal can serve as the local disturbance prediction/reference?

Candidate sources to research:
- neighboring cells not undergoing the perturbation;
- learned local forward prediction;
- temporal prediction residual;
- redundant latent modules with independent disturbance errors;
- locally matched control patches.

This becomes the next bridge from synthetic credit to real NCA state.

NEXT
AR-U8 — LOCAL DISTURBANCE REFERENCE / FORWARD-MODEL IDENTIFIABILITY

Test:
- neighbor reference;
- temporal self-prediction;
- small learned local forward model;
- damaged/nonstationary neighborhoods;
- reference contamination by the same role perturbation.

The key question is whether a cheap reference remains causally useful when the reference itself is affected by the organism's action.

AR-C1 remains parallel:
repeated decentralized context ordering.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_trials_per_delay = 200000
adaptation_population = 1000
