TITLE: DG-1A-AR-H42 — Value-Gated Functional Template Validation Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE SELECTIVE-FUNCTIONAL-VALIDATION RESULT + BLANKET-CHALLENGE NEGATIVE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh41-functional-regeneration-canary-audit.ice

PURPOSE
H41 showed that a bounded functional regeneration challenge can reject a globally common-mode poisoned template candidate that passes every observational canary.

But functional regeneration challenge is not free.

It consumes:
- probe/resource budget;
- lineage evaluation time;
- temporary perturbation capacity.

H42 asks:

WHEN IS FUNCTIONAL TEMPLATE VALIDATION WORTH BUYING?

BOUNDARY
This is synthetic.

It does not:
- freeze a challenge-value formula;
- freeze probe cost;
- prove real Yggdrasil can estimate common-mode risk;
- create a central scheduler;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

CANDIDATE VERSION POPULATION
500,000 synthetic candidate shared-template promotion events for the expected-value sweep.

20 matched realized runs:
50,000 candidates each.

Every candidate has already passed:
- local fit;
- temporal persistence;
- observational canaries.

Each candidate exposes bounded observable metadata:

1.
ESTIMATED COMMON-MODE / PROVENANCE RISK

2.
TEMPLATE LEVERAGE
number of retired lineage-equivalents depending on the shared state.

Tested leverage:
5
30
120.

Population frequencies:
55%
30%
15%.

3.
CANDIDATE FUNCTIONAL DIVERGENCE MAGNITUDE

0.2
0.4
0.6
0.8.

4.
RECURRENCE / DECISION URGENCY

ordinary:
1x

high:
4x.

High urgency frequency:
18%.

COMMON-MODE RISK
Most candidates have low estimated correlated-canary risk.

A smaller tail has elevated risk.

Risk is calibrated as the synthetic probability that:
the candidate is actually a globally common-mode poison
despite observational agreement.

The policy does NOT observe the realized poison label.

FUNCTIONAL CHALLENGE MODEL
Use the H41 matched-control sequential challenge.

Approximate challenge behavior by candidate divergence.

DIVERGENCE = 0.2

poison false-accept:
6.27%.

legitimate accept:
22.25%.

mean pairs:
approximately 25.6.

DIVERGENCE = 0.4

poison false-accept:
2.48%.

legitimate accept:
50.95%.

mean pairs:
approximately 21.5.

DIVERGENCE = 0.6

poison false-accept:
0.93%.

legitimate accept:
82.14%.

mean pairs:
approximately 15.5.

DIVERGENCE = 0.8

poison false-accept:
0.34%.

legitimate accept:
96.87%.

mean pairs:
approximately 10.6.

Thus:
larger functional divergence is cheaper to validate
and
more discriminating.

CHALLENGE COST
0.002 synthetic loss units per paired challenge.

POISON PROMOTION COST
Scales with:

template leverage
*
divergence^2.

Primary multiplier:
0.02.

LEGITIMATE HOLD / REJECTION DELAY COST
Scales with:

template leverage
*
divergence^2
*
urgency.

Primary multiplier:
0.004.

These are synthetic contrast units only.

POLICIES

NEVER FUNCTIONALLY CHALLENGE
Promote every observationally accepted candidate.

ALWAYS CHALLENGE
Run H41 functional validation on every candidate.

RISK-THRESHOLD
Challenge only if estimated common-mode risk exceeds a fixed threshold.

LEVERAGE-ONLY
Challenge all versions supporting at least 30 lineage-equivalents.

ANALYTIC MARGINAL VoI
Using only the observable candidate metadata and calibrated challenge statistics,
compare:

expected loss if promoted without challenge

vs

expected:
challenge cost
+
residual poison risk
+
legitimate delay risk.

Buy the challenge only when expected loss decreases.

PRIMARY EXPECTED-VALUE RESULT
500,000 candidate population.

NEVER CHALLENGE

mean loss per candidate:
0.004632.

challenge fraction:
0%.

ALWAYS CHALLENGE

mean loss:
0.044617.

challenge:
100%.

PRIMARY BLANKET-CHALLENGE NEGATIVE
Always functionally validating every candidate is almost:

10x

worse than observational promotion alone
in this mixed low-risk population.

Reason:
most candidates either:
- have very low common-mode risk;
- have low leverage;
- have too little functional divergence for the bounded challenge to resolve efficiently.

Thus:

FUNCTIONAL VALIDATION
IS NOT
A UNIVERSAL FINAL STEP.

It must itself be value-gated.

FIXED RISK THRESHOLDS
Example:

risk > 0.04

mean loss:
0.008023.

challenge fraction:
14.17%.

risk > 0.10

loss:
0.005654.

challenge:
6.74%.

These improve resource selectivity relative to always-challenge
but still underperform:
never challenge

in the tested population.

PRIMARY NEGATIVE
COMMON-MODE RISK ALONE
IS NOT
VALUE OF VALIDATION.

A low-leverage template may not justify expensive challenge even when corruption risk is non-trivial.

A high-leverage template may justify challenge at lower corruption risk.

LEVERAGE-ONLY

challenge fraction:
44.97%.

mean loss:
0.024594.

This is also substantially worse than never challenge.

Thus:
HIGH LEVERAGE
ALONE
IS NOT ENOUGH.

ANALYTIC MARGINAL VoI

mean loss:
0.003483.

challenge fraction:
2.2804%.

mean challenge pairs per candidate:
0.2701.

PRIMARY VoI POSITIVE
Selective value-gating reduces expected loss:

0.004632
->
0.003483.

Improvement:
approximately 24.8%.

It buys functional regeneration challenge for only:

2.28%

of candidates.

Thus:
rare high-value validation can outperform both:
never validating
and
validating everything.

REALIZED MONTE CARLO CONFIRMATION
20 matched runs.

50,000 candidates per run.

NEVER CHALLENGE

realized loss:
0.004473
SD:
0.000229.

ALWAYS CHALLENGE

loss:
0.044619
SD:
0.000227.

mean challenge pairs per candidate:
17.8221.

VoI-GATED

loss:
0.003390
SD:
0.000136.

challenge fraction:
2.2535%.

mean pairs per candidate:
0.26645.

The realized ordering matches the expected-value result.

WHERE FUNCTIONAL CHALLENGE BUDGET GOES

BY TEMPLATE LEVERAGE

leverage 5:

challenge fraction:
0%.

leverage 30:

2.97%.

leverage 120:

9.28%.

BY CANDIDATE DIVERGENCE

0.2:
0%.

0.4:
0.12%.

0.6:
1.69%.

0.8:
6.96%.

INTERPRETATION
The challenge budget naturally concentrates where:
- a bad promotion affects many capabilities;
- candidate/live functional consequences are sufficiently different;
- the H41 challenge is likely to resolve the question.

This is the desired resource economy.

IMPORTANT WEAK-DIVERGENCE RESULT
Small candidate changes can be:
high leverage

but still:
poor challenge targets

because the functional validator requires many trials and often remains unresolved.

Therefore:
SHARED-STATE LEVERAGE
must be combined with:
EXPECTED TEST RESOLVABILITY.

RELATION TO H21
H21 established:
context validation should be VoI-gated.

H42 establishes the same rule for:
shared generative-template promotion.

The same evidence-economy abstraction can be reused.

RELATION TO S4-S9
Functional validation consumes the same class of scarce adaptive evidence resource as:
- action credit;
- context challenge;
- structural probing.

H42 does not justify:
a separate template-validation scheduler.

It supports:
one shared marginal-value resource economy
with typed local demand.

CURRENT TEMPLATE-PROMOTION DECISION
OBSERVATIONAL PROMOTION CONFIDENCE

+

EFFECTIVE CANARY INDEPENDENCE

+

ESTIMATED COMMON-MODE FAILURE RISK

+

TEMPLATE LEVERAGE

+

EXPECTED FUNCTIONAL DIVERGENCE

+

CHALLENGE RESOLVABILITY

+

CHALLENGE COST

+

RECURRENCE URGENCY

->

PROMOTE ON OBSERVATION
or
BUY FUNCTIONAL CHALLENGE
or
HOLD.

GENERAL PRINCIPLE
THE STRONGEST EVIDENCE
SHOULD NOT AUTOMATICALLY BE
THE MOST FREQUENTLY USED EVIDENCE.

High-cost causal validation should be reserved for:
high expected decision value.

This keeps the developmental architecture:
resource bounded
without
giving up a route out of global observational confounding.

DECISION
AR-H42 is POSITIVE.

Supported synthetically:

- blanket functional template validation can be much worse than observational promotion;
- common-mode risk alone is not enough to allocate challenge resources;
- leverage alone is not enough;
- marginal value can concentrate functional challenge on rare high-impact candidates;
- selective challenge lowers synthetic loss while using very little average probe budget;
- high-leverage/high-divergence candidates receive most challenge resources.

Not demonstrated:

- real common-mode risk estimation;
- learned challenge-value policy for template promotion;
- real functional divergence prediction;
- safe real regeneration probes;
- global budget interaction with simultaneous context/action challenges.

NEXT CLEAN QUESTION
AR-H43 — DECENTRALIZED SHARED-TEMPLATE VERSION CONVERGENCE

H36-H42 still treat one family template version as logically shared.

Question:

Can a distributed developmental organism maintain a shared generative template without:
- a central template server;
- synchronous global commit;
- split-brain family versions;
- stale fragment promotion?

Test:
- several lineage fragments holding local template replicas;
- delayed/partitioned communication;
- candidate shadow versions;
- provenance-diverse validation;
- generation/version IDs;
- merge after partition;
- one fragment receiving poisoned updates.

Desired:

temporary network partition
->
bounded local version divergence.

reconnection
->
safe convergence to a functionally validated version

without:
last-writer-wins corruption
or
duplicating template authority.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
expected_value_candidates = 500000
realized_runs = 20
realized_candidates_per_run = 50000
challenge_pair_cost = 0.002
voi_challenge_fraction = 0.022804
voi_mean_pairs_per_candidate = 0.2701
