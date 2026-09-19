TITLE: DG-1A-AR-H22 — Learned Context-Challenge Value Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE-BUT-SMALL LEARNED VoI RESULT + CONFOUNDING/STALENESS LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh21-voi-gated-context-validation-audit.ice

PURPOSE
H21 established that context validation itself needs a value-of-information gate.

Always challenging is harmful.

The analytic H21 comparator can be selective,
but it knows the hidden challenge-resolvability class.

H22 removes that privileged variable from the adaptive policy.

QUESTION
Can a bounded local learner estimate whether an 8-pair functional context challenge is worth purchasing from local history alone?

BOUNDARY
This is synthetic.

It does not:
- prove real Yggdrasil has these exact anonymous context descriptors;
- freeze the discrete state bins;
- establish an optimal reinforcement-learning rule;
- solve target-free causal reward;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

EVENT ECONOMY
Same context-proposal economics as H21.

Persistent context proposal confidence:

q in [0.55, 0.99].

Wrong-context functional impact:

0.5
2.0
6.0.

Hidden challenge-resolvability:

STRONG
or
MODERATE.

Strong proportion:

45%.

CHALLENGE ACTIONS
Two actions for the focused learned-policy audit:

ACCEPT OBSERVATIONAL CONTEXT
0 challenge pairs.

BUY CHALLENGE
8 paired functional probes.

Challenge cost:

0.025
per pair.

Thus purchased challenge cost:

0.20.

H20 challenge success statistics are used to generate stochastic local outcomes.

The learner is NOT given:
- true context;
- true challenge-resolvability class;
- true probability that the proposal is genuine.

OBSERVABLE LOCAL STATE
The learner receives only bounded coarse local features:

1.
observational context confidence bin;

2.
functional-impact bin;

3.
one anonymous local descriptor bit correlated with challenge resolvability.

The descriptor reports the strong-vs-moderate class correctly:

80%

of the time.

It is not a semantic label.

Context-confidence bins:

<0.65
0.65..0.75
0.75..0.85
0.85..0.92
>=0.92.

Functional-impact bins:

0.5
2
6.

Descriptor:

0
or
1.

Total discrete local states:

30.

LEARNER
Maintain empirical local action value:

Q(state, action).

Actions:

0-pair accept
or
8-pair challenge.

Exploration during maturation:

10%.

EMA learning rate:

0.005.

Observed training loss:

realized wrong-context consequence
+
probe cost.

After maturation,
evaluation is greedy with exploration disabled.

PRIMARY MATURATION RUN
10 matched seeds.

Training events per seed:

160,000.

Greedy evaluation events:

60,000.

PRIMARY RESULTS

LEARNED LOCAL CHALLENGE VALUE

mean true total loss:
0.215157

between-seed SD:
0.002997.

mean challenge pairs per proposal:
0.21315

SD:
0.07654.

NEVER CHALLENGE / ACCEPT OBSERVATION

expected loss:
0.220041

SD:
0.001178.

ALWAYS BUY 8-PAIR CHALLENGE

expected loss:
0.767673.

ANALYTIC EVENT-LEVEL ORACLE

expected loss:
0.186270.

PRIMARY POSITIVE
After sufficient experience,
the bounded local learner improves on never challenging:

0.22004
->
0.21516.

Improvement:
approximately 2.2%.

It does so with a very sparse challenge budget:

approximately 0.21 pairs per proposal on average.

The learned policy does not approach the event-level oracle.

This is expected because the observable state only imperfectly identifies challenge resolvability.

OBSERVABLE-STATE CEILING
A separate large synthetic population computes the best policy available from the same coarse observable state.

Best observable-state expected loss:

approximately 0.21516.

Mean challenge pairs:

approximately 0.172.

Thus the matured learner is close to the useful performance available from its bounded feature representation.

The remaining gap to:

0.18627

is primarily an information / representation gap,
not simply a training-duration gap.

IMPORTANT MATURATION NEGATIVE
During online training with continuing exploration,
the learner can perform worse than simply accepting the persistent observation.

The beneficial challenge action is:
- relatively rare;
- costly;
- high-variance.

Therefore:

EXPLORATION ITSELF HAS A REAL RESOURCE COST.

A developmental system needs a distinction between:

LEARNING THE RESOURCE POLICY

and

EXPLOITING A MATURE RESOURCE POLICY.

Do not assume an immature evidence allocator is immediately beneficial.

NONSTATIONARY RESOLVABILITY STRESS
The anonymous descriptor-to-resolvability relationship is reversed halfway through a fresh stream.

No semantic topology-change label is provided.

Policy quality is evaluated at checkpoints using greedy exploitation.

CUMULATIVE HISTORY
Before shift:

loss approximately:
0.21557

pairs:
0.171.

5,000 events after shift:

loss:
0.24730

pairs:
0.203.

15,000 after:

0.22849

pairs:
0.105.

40,000 after:

0.22633

pairs:
0.076.

90,000 after:

0.22002

pairs:
0.026.

INTERPRETATION
Permanent cumulative value history retains obsolete challenge economics for a long time.

Eventually it mostly stops challenging rather than relearning the new useful allocation.

MEDIUM RECENCY EMA
alpha:
0.005.

Before shift:

loss:
0.21719

pairs:
0.178.

5,000 after:

0.21942

pairs:
0.048.

15,000 after:

0.21759

pairs:
0.035.

40,000 after:

0.21936

pairs:
0.059.

90,000 after:

0.21646

pairs:
0.072.

Interpretation:

recency-weighted value can relearn the new challenge mapping
and recover a sparse useful challenge policy.

VERY FAST RECENCY NEGATIVE
A faster value learner reacts quickly,
but challenge allocation becomes unstable.

In the tested stream,
mean challenge pairs later rise again to approximately:

0.197

with no corresponding major loss advantage.

Thus the recurring:

STABILITY
vs
PLASTICITY

tradeoff applies to:
CHALLENGE VALUE TRUST.

PASSIVE-IMPROVEMENT CONFOUND
A challenge consumes time.

Suppose the observed local outcome passively improves while the challenge is being performed.

If the learner sees only:

outcome_after_challenge,

it can falsely credit the improvement to:
buying challenge evidence.

The true task loss is unchanged.

Training-time confounding bonus is swept.

10 matched seeds.

CONFOUND = 0

true evaluation loss:
0.21516

pairs:
0.213.

CONFOUND = 0.05

loss:
0.21486

pairs:
0.214.

CONFOUND = 0.10

loss:
0.21722

pairs:
0.347.

CONFOUND = 0.20

loss:
0.23638

pairs:
1.218.

CONFOUND = 0.30

loss:
0.26526

pairs:
2.265.

PRIMARY CONFOUNDING NEGATIVE
A strong passive-improvement confound causes:

OVER-CHALLENGING

and

WORSE TRUE FUNCTION.

At confound 0.30,
challenge expenditure rises by over:

10x

relative to the unconfounded learned policy,
while true loss becomes worse than never challenging.

Therefore:

OUTCOME IMPROVED WHILE I GATHERED CONTEXT EVIDENCE

does not imply:

GATHERING CONTEXT EVIDENCE CAUSED THE IMPROVEMENT.

MATCHED-CONTROL CONSEQUENCE
The S7-S9 causal-control machinery is therefore required here too.

A learned context-challenge value should update from something closer to:

TARGET OUTCOME CHANGE

minus

ACTION-DECOUPLED WAITING / DISTURBANCE CHANGE.

H22 does not create a second causal-control architecture.

It reuses the existing one.

CURRENT CONTEXT-CHALLENGE VALUE STATE
A bounded local challenge allocator now plausibly needs:

OBSERVATIONAL CONTEXT CONFIDENCE

+

PREDICTED FUNCTIONAL IMPACT

+

ANONYMOUS CHALLENGE-RESOLVABILITY FEATURES

+

RECENT CHALLENGE VALUE HISTORY

+

PROBE COST

+

DEADLINE

+

VALUE-POLICY TRUST / RECENCY

+

CAUSAL WAITING CONTROL

->

BUY CHALLENGE
or
ACCEPT / HOLD.

GENERAL PRINCIPLE
The value of information is itself:
learned state.

Therefore it can be:
- immature;
- stale;
- confounded;
- miscalibrated.

A resource allocator needs confidence and causal hygiene just like the behavior it regulates.

DECISION
AR-H22 is POSITIVE-BUT-SMALL.

Supported synthetically:

- bounded local history can learn a sparse context-challenge policy without true resolvability labels;
- the learned policy can beat never challenging;
- its attainable gain is limited by the information in its local state representation;
- resource-policy maturation has real cost;
- cumulative challenge-value history becomes stale after topology change;
- recency helps relearn challenge economics;
- passive environmental improvement can cause severe over-challenging.

Not demonstrated:

- real Yggdrasil context-challenge value learning;
- real local functional impact estimation;
- real target-free challenge reward;
- optimal exploration schedule;
- optimal state representation;
- safe challenge policy under mature critical structures.

NEXT CLEAN QUESTION
AR-H23 — SHARED META-CONTROLLER VS SEPARATE ADAPTIVE TRUST LOOPS

Across H5-H22,
many subsystems now independently require:

recency
+
confidence
+
causal control
+
resource cost
+
reversible trust.

Question:

Can these be represented by one compact generic local meta-rule
parameterized by evidence type,
rather than separate bespoke controllers for:

memory expression,
control trust,
nomination trust,
context trust,
and challenge-value trust?

Test:

A.
independent tuned controllers;

B.
one shared update form with small typed state;

C.
shared form with one collapsed confidence scalar;

D.
cross-domain interference when one domain shifts;

E.
memory/resource savings versus performance loss.

Desired:

reuse the same local computational motif

without
collapsing distinct confidence meanings into one unstable global scalar.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
training_events_per_seed = 160000
evaluation_events_per_seed = 60000
primary_matched_seeds = 10
learner_alpha = 0.005
training_exploration = 0.10
challenge_pairs_if_purchased = 8
