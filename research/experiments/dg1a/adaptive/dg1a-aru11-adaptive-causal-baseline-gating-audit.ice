TITLE: DG-1A-AR-U11 — Adaptive Causal Baseline Gating Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE-BUT-TRADEOFF AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru10-local-disturbance-subspace-poc.ice

PURPOSE
AR-U10 showed that:
- full local disturbance prediction is better when action contamination is weak;
- action-orthogonalized prediction becomes better when contamination is strong;
- both can become stale when the disturbance relationship shifts.

This audit tests a local confidence gate that chooses among:

FULL DISTURBANCE PREDICTION

ACTION-ORTHOGONALIZED PREDICTION

DEFER / DO NOT UPDATE ROLE CREDIT

QUESTION
Can cheap local risk estimates reduce false role reinforcement across heterogeneous regimes without a globally supervised selector?

BOUNDARY
This is synthetic.

It does not:
- freeze a production confidence threshold;
- prove current Yggdrasil state contains calibrated risk signals;
- modify or execute STAB-18-R1;
- count as functional regeneration.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

HETEROGENEOUS SYSTEM POPULATION
Synthetic local systems:
600

Reference signals:
8

Shared disturbance dimensions:
2

No-action history:
128 transitions

Action-exposure microprobes:
48

Recent no-action confidence window:
24 transitions

Test observations per system:
1500

True local action effect:
+/-0.04

The population mixes:

action-contamination scales:
0.35
0.80
1.20
1.80

disturbance-subspace shift:
0
0.06
0.12
0.25

action-footprint shift:
0
0.08
0.20

microprobe disturbance levels:
0.05
0.08
0.16

No condition label is exposed to the gate.

CANDIDATE BASELINES

FULL
Linear no-action predictor from all local references.

ORTHOGONALIZED
AR-U10 action-responsive projection followed by local disturbance prediction.

LOCAL RISK SIGNALS

RECENT DISTURBANCE-MODEL RESIDUAL
Using the recent 24-step no-action window:

RMSE_full

RMSE_orthogonalized

ESTIMATED ACTION LEAKAGE
For the full predictor:

Leak_full =
abs(
    W_full dot estimated_action_exposure
)

For the orthogonalized predictor,
the estimated exposure direction is projected out,
so estimated direct leakage is near zero by construction.

SIMPLE RISK PROXY

Risk_full =
recent_RMSE_full
+
effect_scale * Leak_full

Risk_orthogonalized =
recent_RMSE_orthogonalized
+
effect_scale * Leak_orthogonalized

SELECTOR
Use the predictor with lower estimated risk.

The gate does not observe:
- true contamination;
- true disturbance shift;
- true causal-sign accuracy.

RESULTS — ALWAYS-ON METHODS

always FULL:
mean causal-sign accuracy =
65.90%

always ORTHOGONALIZED:
67.26%

LOCAL RISK SELECTOR:
68.64%

The risk selector chose the actually better of the two methods in:
70.5% of synthetic systems.

PRIMARY POSITIVE
A simple local confidence estimate can improve over committing permanently to either causal baseline.

The gain is modest,
which is important.

This is NOT a solved classifier.

DEFER / CREDIT-SKIPPING TEST
If:

min(
    Risk_full,
    Risk_orthogonalized
)
>
threshold

then:
do not update the role from that credit event.

Results:

risk threshold 0.05

accepted coverage:
29.17%

accepted sign accuracy:
75.41%

false reinforcement among accepted:
24.59%

risk threshold 0.06

coverage:
47.67%

accepted accuracy:
74.86%

false reinforcement:
25.14%

risk threshold 0.07

coverage:
60.67%

accepted accuracy:
73.76%

false reinforcement:
26.24%

risk threshold 0.08

coverage:
70.50%

accepted accuracy:
72.72%

false reinforcement:
27.28%

risk threshold 0.10

coverage:
82.00%

accepted accuracy:
71.39%

false reinforcement:
28.61%

risk threshold 0.12

coverage:
87.33%

accepted accuracy:
70.59%

false reinforcement:
29.41%

risk threshold 0.15

coverage:
92.17%

accepted accuracy:
69.87%

false reinforcement:
30.13%

risk threshold 0.20

coverage:
96.00%

accepted accuracy:
69.30%

false reinforcement:
30.70%

PRIMARY TRADEOFF
Stricter confidence gating:

reduces false reinforcement

but

discards more usable credit.

Therefore:
CONFIDENCE GATING TRADES ADAPTATION SPEED FOR CREDIT FIDELITY.

There is no universally correct threshold in this audit.

A threshold that maximizes immediate accepted-credit accuracy may adapt too slowly.

A threshold that maximizes throughput may reinforce too many wrong local changes.

EFFECTIVE NET-CORRECT CREDIT
For descriptive comparison only:

coverage
*
(2 * accepted_accuracy - 1)

risk 0.05:
0.148

0.06:
0.237

0.07:
0.288

0.08:
0.320

0.10:
0.351

0.12:
0.360

0.15:
0.366

0.20:
0.371

This diagnostic increases toward looser thresholds in the tested population.

IMPORTANT:
do NOT convert this into a scientific gate.

It assumes symmetric value of correct and incorrect role updates.

A real organism may have strongly asymmetric risk:
one wrong update in a mature structure can be much more costly than one skipped opportunity.

INTERPRETATION
The confidence gate is most useful as a SAFETY / PLASTICITY MODULATOR,
not necessarily as a hard binary classifier.

A future rule could map confidence continuously to:

role-update gain

rather than:

update
or
no update.

Conceptually:

high confidence
->
larger bounded plasticity

moderate confidence
->
small update

low confidence
->
hold state / gather more evidence

This may avoid the sharp speed/fidelity trade created by binary deferral.

FAILURE ANALYSIS
The simple gate remains limited because:

1.
recent no-action residual estimates disturbance-model quality,
but not every future disturbance;

2.
action-exposure estimates remain noisy;

3.
action and disturbance can occupy the same local direction;

4.
the gate itself can become stale after regime changes;

5.
recent low prediction error does not guarantee low causal contamination.

Therefore:
CONFIDENCE
is not equivalent to
CAUSAL CERTAINTY.

ARCHITECTURAL CONSEQUENCE
The current local meta-rule now has a plausible bounded stack:

ACTION TAG

ELIGIBILITY

DISTURBANCE MODEL

ACTION-EXPOSURE MODEL

RECENT MODEL RESIDUAL

CONFIDENCE / PLASTICITY GAIN

LOCAL CONSEQUENCE

->
BOUNDED ROLE UPDATE.

This is substantially richer than:
prediction error -> change role.

But it is still local and compact.

NEXT
AR-U12 — CONTINUOUS CONFIDENCE-WEIGHTED PLASTICITY

Compare:

A.
always-update baseline

B.
hard defer gate

C.
continuous update gain proportional to confidence

D.
evidence-accumulation gate:
low confidence triggers more sparse microprobes before updating.

Measure:
- final adaptation error;
- switching latency;
- false role updates;
- exploratory perturbation count;
- mature-state drift.

PARALLEL
AR-C1 — repeated decentralized context ordering.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
synthetic_systems = 600
test_observations_per_system = 1500
