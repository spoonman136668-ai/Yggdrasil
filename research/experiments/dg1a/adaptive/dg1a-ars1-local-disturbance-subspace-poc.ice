TITLE: DG-1A-AR-S1 — Local Disturbance Subspace / Action-Orthogonalization POC
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX MIXED-POSITIVE POC
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
SERIES_NOTE: SUPPLEMENTAL AR-S SERIES — CANONICAL R4 AR-U NUMBERING PRESERVED
BRANCH: dg1a-ar
PARENT: dg1a-aru9-local-matched-control-selection-audit.ice

PURPOSE
AR-U9 found that selecting one causal control from nearby cells is itself an identifiability problem.

The most correlated neighbor can be a poor control because it may lie inside the action's causal footprint.

This experiment tests the next proposed abstraction:

several local signals
->
learn shared disturbance representation
->
estimate which signal direction responds to the cell's own tagged perturbations
->
remove that action-responsive direction
->
use the remaining local subspace as a disturbance baseline.

QUESTION
Can a small local linear disturbance model separate useful shared environmental variation from action-contaminated reference variation better than:
- no reference;
- one highly correlated reference;
- naive all-neighbor regression;
- low-exposure reference selection?

BOUNDARY
This is synthetic.

It does not:
- prove current Yggdrasil latent state contains an identifiable disturbance subspace;
- authorize explicit reference channels;
- freeze a projection algorithm;
- modify or execute STAB-18-R1;
- count as functional regeneration.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SYNTHETIC LOCAL SYSTEM
Reference signals per target:
8

Latent shared environmental factors:
2

No-action history:
128 transitions

Target consequence:
shared latent disturbance projection
+
local observation noise.

Each reference:
its own projection of the same shared disturbance
+
local observation noise
+
possible action contamination.

Target action effect:
+/-0.04

Reference action contamination:
varies by local signal.

Disturbance and action exposure are intentionally partially confounded:
signals that are highly informative about the target's environment can also be highly exposed to the target's action.

ACTION-EXPOSURE MICROPROBES
Sparse signed target perturbations are used to estimate the vector of reference responses to the target action.

Primary working point:
48 microprobes.

The selector/model never observes:
- true causal graph;
- true contamination vector;
- true latent disturbance coordinates.

METHODS

NO REFERENCE
Use raw target consequence.

CORRELATION-ONE
Use the single reference most correlated with target no-action history.

NAIVE-ALL
Fit a small linear no-action predictor:

target disturbance
approximately
W * all references

Then subtract its prediction at test time.

This model has no protection against references carrying the target action effect.

LOW-EXPOSURE-3
Use three references selected for low estimated action exposure relative to predictive utility.

ACTION-ORTHOGONALIZED
Estimate the reference-space action-response vector:

c_hat

from sparse tagged microprobes.

Construct the local projection:

P =
I
-
(c_hat c_hat^T)
/
(||c_hat||^2 + epsilon)

Project no-action reference history through P.

Fit the disturbance predictor only in the projected reference space.

At test time:

local references
->
P
->
predicted no-action disturbance

Then:

causal residual =
observed target consequence
-
predicted disturbance.

ORACLE-ORTHOGONALIZED
Same construction using the true synthetic action-exposure vector.

This is a diagnostic upper bound,
not an available operational method.

PRIMARY CONTAMINATION SWEEP
Systems:
120 per condition

Test observations:
2000 per system

Primary true contamination scale varied.

contamination scale = 0.4

no reference:
51.49%

correlation-one:
67.42%

naive-all:
79.81%

low-exposure-3:
73.80%

estimated orthogonalization:
75.50%

oracle orthogonalization:
76.63%

IMPORTANT NEGATIVE
When action contamination is weak,
naive all-reference prediction is BETTER than removing an action-responsive direction.

Projection discards useful disturbance information.

Therefore:
ACTION ORTHOGONALIZATION MUST NOT BE ALWAYS-ON.

contamination scale = 0.8

correlation-one:
63.48%

naive-all:
73.57%

low-exposure-3:
69.47%

estimated orthogonalization:
73.04%

oracle:
76.63%

contamination scale = 1.2

correlation-one:
60.25%

naive-all:
68.09%

low-exposure-3:
65.26%

estimated orthogonalization:
71.79%

oracle:
76.33%

contamination scale = 1.8

correlation-one:
58.16%

naive-all:
64.58%

low-exposure-3:
61.95%

estimated orthogonalization:
71.81%

oracle:
76.48%

PRIMARY RESULT
As action contamination becomes strong,
naive disturbance prediction increasingly subtracts the causal effect itself.

Action-orthogonalized prediction becomes superior.

This creates a regime-dependent decision:

LOW ACTION EXPOSURE
prefer full predictive disturbance information.

HIGH ACTION EXPOSURE
remove action-responsive reference components before using them as counterfactual baseline.

ACTION-EXPOSURE IDENTIFIABILITY
Contamination scale:
1.2

Microprobe count | correlation(true exposure, estimated exposure) | orthogonalized sign accuracy

4:
24.28%
68.29%

8:
40.15%
70.22%

16:
52.70%
72.14%

24:
55.93%
72.70%

48:
71.85%
73.89%

96:
82.39%
75.43%

Oracle:
approximately 76.75%

KEY RESULT
Action-orthogonalization quality is limited by the quality of ACTION IDENTITY / EXPOSURE evidence.

The projection does not manufacture causal information.

More accurate tagged perturbation evidence improves the subspace.

PRIMARY WORKING POINT
For subsequent stress tests:

contamination scale:
1.2

microprobes:
48

Systems:
150 per condition

stationary:

no reference:
51.55%

correlation-one:
59.62%

naive-all:
68.18%

low-exposure-3:
65.99%

estimated orthogonalized:
73.85%

oracle:
76.25%

estimated exposure correlation:
70.18%

ACTION-FOOTPRINT SHIFT

moderate action-exposure shift = 0.10:

naive-all:
68.38%

orthogonalized:
73.65%

oracle:
76.19%

larger shift = 0.25:

naive:
68.96%

orthogonalized:
73.18%

oracle:
75.66%

The estimated projection degrades only modestly in this synthetic action-footprint shift.

DISTURBANCE-SUBSPACE NONSTATIONARITY

subspace shift = 0.10:

correlation-one:
56.25%

naive-all:
62.10%

orthogonalized:
61.52%

oracle orthogonalized:
62.06%

subspace shift = 0.25:

correlation-one:
53.52%

naive-all:
57.14%

orthogonalized:
55.72%

oracle:
55.96%

HARD NEGATIVE
When the shared disturbance relationship itself changes,
action orthogonalization does NOT solve the problem.

Both naive and orthogonalized predictors become stale.

Therefore two distinct adaptation problems remain:

ACTION CONTAMINATION
which dimensions reflect my own intervention?

DISTURBANCE NONSTATIONARITY
which dimensions still predict the environment?

They require different update signals.

HIGH ACTION/DISTURBANCE ALIGNMENT
A stress condition makes the action-contamination direction strongly aligned with the most disturbance-informative reference direction.

Results:

naive-all:
67.31%

estimated orthogonalized:
66.85%

oracle orthogonalized:
68.47%

NEGATIVE
If the same local signal direction carries BOTH:
critical disturbance information
and
action effect,

linear orthogonalization faces an information tradeoff.

Removing action exposure also removes environmental information.

This is not fixable by a sharper projection threshold.

MICROPROBE ENVIRONMENTAL DRIFT
Doubling microprobe disturbance variation reduced estimated exposure correlation:

70.18%
->
52.93%

and reduced orthogonalized sign accuracy:

73.85%
->
71.00%.

Thus tagged exposure probes themselves need disturbance control / repeated evidence.

INTERPRETATION
AR-S1 rejects the idea that one static causal filter solves local credit.

A useful local causal baseline likely needs TWO adaptive decompositions:

1. DISTURBANCE MODEL
learn which local signals predict shared environmental change.

2. ACTION-EXPOSURE MODEL
learn which local signal components respond to the cell's own tagged actions.

Then use the action-exposure estimate to decide whether:
- retain the disturbance direction;
- down-weight it;
- project it away;
- mark the estimate low-confidence.

The right operation depends on identifiability.

CORE ARCHITECTURAL STATE
The emerging local meta-rule now needs at least conceptual equivalents of:

ACTION TAG
what did I change?

ELIGIBILITY
which recent change can still receive credit?

DISTURBANCE REPRESENTATION
what changed locally for reasons shared with my neighborhood/environment?

ACTION-EXPOSURE REPRESENTATION
which parts of that disturbance estimate also respond to my own action?

CONFIDENCE
is the local decomposition identifiable enough to update a role?

Do not collapse these into one prediction-error scalar.

RELATION TO CAUSAL INTERFERENCE LITERATURE
Contemporary causal-inference work under network interference emphasizes that treatment spillovers break ordinary control assumptions and require explicit modeling of local interference structures.

This synthetic result expresses the same problem in developmental/local-learning form:

a neighbor can be predictive
while simultaneously being causally contaminated by the focal cell's action.

Prediction quality alone is insufficient for causal control.

RELATION TO LOCAL LEARNING
Local eligibility-trace and node-perturbation methods demonstrate that action-linked local learning signals can be computationally local.

AR-S1 adds a separate requirement:

the local baseline used with those traces must itself be screened for action contamination.

DECISION
AR-S1 is MIXED POSITIVE.

SUPPORTED:
- local action-responsive subspace estimation can improve causal credit when contamination is material;
- tagged microprobes provide useful action-exposure information;
- several local signals are more promising than a permanent single control cell.

NOT SUPPORTED:
- always-on action projection;
- one static learned disturbance model;
- correlation as causal-control validity;
- projection as a solution to disturbance nonstationarity;
- clean separation when action and disturbance occupy the same local direction.

NEXT
AR-U11 — ADAPTIVE CAUSAL BASELINE GATING

Question:
Can a cheap local confidence mechanism decide WHEN to trust:
- full disturbance prediction;
- action-orthogonalized prediction;
- no update / defer credit?

Candidate signals:
- estimated action exposure;
- disturbance-model residual;
- temporal stability;
- disagreement among local references.

Measure:
- causal-sign accuracy;
- false role reinforcement;
- skipped-credit rate;
- adaptation latency;
- robustness under disturbance regime shifts.

PARALLEL FRONTIER
AR-C1 — repeated decentralized context ordering.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_systems_per_condition = 120
stress_systems_per_condition = 150
test_observations_per_system = 2000
