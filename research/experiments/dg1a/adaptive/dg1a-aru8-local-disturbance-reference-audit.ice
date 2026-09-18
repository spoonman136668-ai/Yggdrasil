TITLE: DG-1A-AR-U8 — Local Disturbance Reference / Forward-Model Identifiability Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX REFERENCE-IDENTIFIABILITY AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru7-cheap-causal-credit-approximation-audit.ice

PURPOSE
AR-U7 found that sparse action-tagged perturbations become much more causally reliable when local environmental disturbance can be estimated and subtracted.

This audit asks:
what properties must that local disturbance reference have?

Test:
- temporal self-prediction;
- nearby reference state;
- a small learned local reference model;
- post-perturbation nonstationarity;
- reference contamination by the same action.

BOUNDARY
This is synthetic.

It does not:
- establish a real Yggdrasil reference signal;
- reserve any hidden channel;
- authorize explicit control cells;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PART A — NONSTATIONARY LOCAL TREND BENCHMARK

Trials:
100,000 per condition.

Causal perturbation effect:
beta = +/- 0.025

Future horizon:
20 steps

Pre-action history:
16 local observations.

Common environmental dynamics:
slow local trend
+
common random-walk disturbance.

Target cell additionally has:
local idiosyncratic random walk
+
measurement noise.

Neighbor/reference cell:
shares the common environmental trend and disturbance,
but has independent idiosyncratic noise.

POST-ACTION NONSTATIONARITY
At the moment of perturbation,
the common local trend can change by a random amount.

shift_sd tested:

0
0.001
0.003
0.006
0.012

METHOD 1 — NAIVE
future local consequence
-
current consequence

METHOD 2 — TEMPORAL SELF-TREND
Fit a linear trend to the target cell's 16-step pre-action history.

Subtract the extrapolated 20-step trend from the observed future consequence.

METHOD 3 — LIVE NEIGHBOR REFERENCE
Subtract the actual future change observed in the nearby non-perturbed reference.

METHOD 4 — SIMPLE HYBRID
Use self-trend prediction plus the neighbor's deviation from its own pre-action trend as an innovation correction.

METHOD 5 — MATCHED PAIRED CONTROL
Synthetic gold-standard disturbance-matched future.

RESULTS

shift_sd = 0

naive:
63.27%

self-trend:
64.92%

live neighbor:
82.15%

hybrid:
72.48%

gold:
99.99%

shift_sd = 0.001

naive:
63.29%

self-trend:
64.47%

live neighbor:
81.92%

hybrid:
72.37%

gold:
99.98%

shift_sd = 0.003

naive:
60.52%

self-trend:
61.37%

live neighbor:
82.06%

hybrid:
72.31%

gold:
99.98%

shift_sd = 0.006

naive:
57.04%

self-trend:
57.28%

live neighbor:
82.21%

hybrid:
72.31%

gold:
99.98%

shift_sd = 0.012

naive:
53.91%

self-trend:
53.86%

live neighbor:
82.17%

hybrid:
72.25%

PRIMARY RESULT
A predictor based only on PRE-ACTION self-history cannot anticipate a genuinely new post-action environmental regime shift.

Its causal-sign accuracy collapses toward chance as nonstationarity increases.

The live nearby reference remains useful because it experiences the same new disturbance in real time.

Therefore:

TEMPORAL PREDICTION
and
CONTEMPORANEOUS DISTURBANCE REFERENCE

solve different problems.

REFERENCE CONTAMINATION TEST
The prior neighbor result assumes the local role perturbation does NOT materially affect the reference.

Let contamination fraction c mean:

reference receives:
c * beta

in addition to the environmental disturbance.

Use:
shift_sd = 0.006.

RESULTS

c = 0.00

live neighbor:
82.20%

c = 0.10:
79.50%

c = 0.25:
75.73%

c = 0.50:
67.58%

c = 0.75:
58.91%

c = 0.90:
53.55%

c = 1.00:
49.91%

c = 1.25:
41.15%

KEY NEGATIVE
When the action influences the reference by the same amount as the target:

target change
-
reference change

removes the causal effect itself.

At stronger-than-target contamination,
the estimated sign can invert.

Therefore:
A USEFUL LOCAL CONTROL MUST BE

DISTURBANCE-COUPLED

but

ACTION-DECOUPLED.

This is the central AR-U8 identifiability result.

PART B — SMALL LEARNED LOCAL REFERENCE MODEL

The previous test assumed a one-to-one scaling between target and reference disturbance.

A second benchmark allows the reference to experience the same latent environment with an unknown scale:

reference_scale
uniform in:
0.5..1.5

Each synthetic cell receives:
32 prior no-action target/reference transitions.

A local linear model is fit:

target_disturbance
approximately
gamma * reference_disturbance
+
intercept

Then the learned model predicts the target's no-action future from the current reference.

Trials:
100,000 per condition.

Common disturbance SD:
0.12

Target/reference idiosyncratic noise SD:
0.03

EFFECT:
+/-0.025

STATIONARY SCALE

naive:
57.82%

raw neighbor subtraction:
68.11%

learned scaled reference:
71.49%

gold:
99.98%

REFERENCE-SCALE NONSTATIONARITY

scale_shift_sd = 0.10

raw neighbor:
68.42%

learned:
71.14%

scale_shift_sd = 0.25

raw:
67.09%

learned:
69.26%

scale_shift_sd = 0.50

raw:
64.74%

learned:
65.88%

INTERPRETATION
A tiny learned local forward/reference model can improve on raw subtraction when target/reference coupling has stable local structure.

Its benefit degrades when the coupling itself changes.

Therefore:
LEARNED LOCAL PREDICTION
is useful only to the extent that the local disturbance relationship remains predictable.

LEARNED-REFERENCE CONTAMINATION
With modest scale nonstationarity:
scale_shift_sd = 0.10

action contamination:

c = 0.00
raw:
68.06%
learned:
70.95%

c = 0.10
raw:
66.72%
learned:
69.35%

c = 0.25
raw:
63.91%
learned:
66.32%

c = 0.50
raw:
59.32%
learned:
61.24%

c = 0.75
raw:
54.89%
learned:
56.27%

c = 1.00
raw:
49.74%
learned:
50.52%

The learned predictor does NOT solve action contamination.

That is expected:
the model cannot distinguish disturbance from a causal effect that enters its reference through the same channel.

ARCHITECTURAL CONSEQUENCE
A cheap local causal-credit system should not rely on one undifferentiated predictor.

The evidence suggests THREE conceptually different signals:

1. SELF TEMPORAL PREDICTION
What would this cell normally have done?

Useful for:
stationary local dynamics.

2. CONTEMPORANEOUS LOCAL DISTURBANCE REFERENCE
What changed nearby that was probably environmental/shared?

Useful for:
unexpected common disturbances.

3. ACTION TAG / ELIGIBILITY
What did this cell itself change?

Necessary to prevent the reference/predictor from absorbing the action being credited.

A useful estimator must separate:
SELF-CAUSED CHANGE
from
SHARED ENVIRONMENTAL CHANGE.

REFERENCE-SELECTION PROBLEM
The real Yggdrasil problem is now sharper.

A nearby cell is NOT automatically a valid control.

A valid local reference should have:
- high shared-disturbance covariance;
- low causal exposure to the probed action;
- adequate temporal freshness;
- sufficient independent measurement noise structure.

This resembles a local matched-control selection problem.

CROSS-DOMAIN CONNECTION
The same "partially independent but relevant" requirement now appears in:

injury cues;
seasonal sensors;
role-credit cues;
disturbance references.

The desired relationship is not:
maximum similarity.

It is:

SHARED RELEVANT CAUSE

with

INDEPENDENT ERROR / ACTION EXPOSURE.

LITERATURE ALIGNMENT
Recent predictive-coding/local-learning work demonstrates that useful learning signals can be constructed from local prediction errors rather than global backpropagated errors.

Examples include:
- predictive-coding-based local Hebbian SNN learning;
- TESS-style temporally/spatially local learning;
- fully local spatio-temporal credit frameworks.

These support the feasibility of local prediction-error machinery.

They do NOT solve the matched-reference identifiability problem demonstrated here.

IMPORTANT NEGATIVE
Do not define:

prediction error
==
causal credit.

Prediction error can contain:
- environmental novelty;
- neighbor disturbance;
- self-caused change;
- damage;
- measurement noise.

Causal role credit needs an action-linked decomposition of that error.

NEXT
AR-U9 — LOCAL MATCHED-CONTROL SELECTION

Synthetic question:
Can a cell choose useful local references from several neighbors using only:
- pre-perturbation covariance;
- perturbation exposure tests;
- temporal consistency;

without knowing the true causal graph?

Stress:
- damaged neighborhoods;
- moving roles;
- reference loss;
- correlated common-mode noise.

PARALLEL:
AR-C1 repeated decentralized context ordering.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_trials_per_condition = 100000
learned_reference_history = 32
