TITLE: DG-1A-AR-U6 — Delayed / Confounded Causal Local Credit Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX CAUSAL-CREDIT AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru5-causal-local-consequence-credit-poc.ice

PURPOSE
Stress the clean AR-U5 perturb-and-observe meta-rule with the confounds that a real developmental organism will face:

- delayed effects;
- unrelated environmental drift;
- stochastic observation;
- simultaneous role changes;
- pseudorandom aliasing between probe selection and future dynamics.

Question:
When is naive local before/after consequence credit no longer causally interpretable?

BOUNDARY
This is a synthetic causal-identifiability audit.

It does not:
- alter or execute STAB-18-R1;
- claim Yggdrasil has a counterfactual simulator per cell;
- authorize expensive future probes;
- establish a production meta-rule.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX
ANALYTIC where explicitly stated.

PART A — DELAYED EFFECT WITH ENVIRONMENTAL DRIFT

LOCAL ROLE TOY
Current role gate:
a

Unknown local optimum:
a_star

Local structural consequence:
f(a) =
(a - a_star)^2

Probe:
increase role by:
epsilon = 0.08

True causal delta:
f(a + epsilon) - f(a)

Beneficial:
true delta < 0

Trials:
200,000 per condition

Initial a:
uniform 0.1..0.9

a_star:
uniform 0..1

Mean absolute true effect:
approximately 0.0488

Measurement noise standard deviation:
0.005

DELAY
Effects are evaluated after:

1
4
16
32

steps.

ENVIRONMENTAL DRIFT
Background local consequence follows a zero-mean random-walk disturbance.

Per-step sigma:

0.02
0.05
0.10
0.20

Three estimators are compared.

NAIVE BEFORE/AFTER
Compare:
future perturbed observation
minus
current observation.

PAIRED COMMON-DISTURBANCE COUNTERFACTUAL
At the future horizon compare:

perturbed future
minus
intact future

under the SAME environmental disturbance realization.

INDEPENDENT-FUTURE PAIR
Compare perturbed and intact futures under independent disturbances.

SIGN ACCURACY
Correctly classify whether the perturbation truly helps.

delay 1

sigma 0.02:
naive 89.79%
paired-common 96.47%
independent-pair 86.34%

sigma 0.05:
naive 78.62%
paired-common 96.49%
independent-pair 73.05%

sigma 0.10:
naive 67.77%
paired-common 96.52%
independent-pair 63.26%

sigma 0.20:
naive 59.56%
paired-common 96.50%
independent-pair 56.68%

delay 4

sigma 0.02:
naive 81.82%
paired-common 96.41%
independent-pair 76.44%

sigma 0.05:
naive 67.67%
paired-common 96.40%
independent-pair 63.08%

sigma 0.10:
naive 59.52%
paired-common 96.50%
independent-pair 56.82%

sigma 0.20:
naive 54.89%
paired-common 96.39%
independent-pair 53.49%

delay 16

sigma 0.02:
naive 71.16%
paired-common 96.43%
independent-pair 65.79%

sigma 0.05:
naive 59.52%
paired-common 96.44%
independent-pair 56.66%

sigma 0.10:
naive 55.08%
paired-common 96.46%
independent-pair 53.27%

sigma 0.20:
naive 52.53%
paired-common 96.52%
independent-pair 51.72%

delay 32

sigma 0.02:
naive 66.08%
paired-common 96.58%
independent-pair 61.66%

sigma 0.05:
naive 56.98%
paired-common 96.45%
independent-pair 54.80%

sigma 0.10:
naive 53.46%
paired-common 96.56%
independent-pair 52.32%

sigma 0.20:
naive 51.65%
paired-common 96.50%
independent-pair 51.13%

PRIMARY RESULT
Naive observational credit approaches chance as:

delay
x
environmental drift

increases.

Running intact and perturbed futures under unrelated disturbances is also poor.

The paired common-disturbance comparison removes the environmental drift term and remains limited mainly by measurement noise.

This is a causal-control result,
not evidence that a real cell can afford or implement such a counterfactual.

PART B — PSEUDORANDOM PROBE / FUTURE ALIASING

PURPOSE
Test the exact class of failure discovered before STAB-18-R1:

probe selection can be causally biased if it is constructed from the same random field that determines future dynamics.

TOY
Every tested perturbation is truly HARMFUL.

true causal delta:
+0.01

Probe fraction:
25%

A uniform random value u contributes to future environmental shock.

ALIASED CONDITION
Probe when:

u < 0.25

and use the same u in the future shock.

DOMAIN-SEPARATED CONDITION
Probe selection uses independent random v.

Future shock still uses u.

PAIRED CONDITION
Domain-separated probe selection plus:
perturbed future
and
intact future
share the same shock realization.

RESULTS

future shock scale = 0.04

aliased:
false-beneficial classification = 76.25%
mean observed delta = -0.00499

domain-separated observational:
false-beneficial = 25.19%
mean observed delta = +0.01003

paired common-shock:
false-beneficial = 0.019%
mean observed delta = +0.01001

shock scale = 0.08

aliased:
false-beneficial = 93.02%
mean observed delta = -0.01990

domain-separated observational:
false-beneficial = 37.65%
mean observed delta = +0.01008

paired:
false-beneficial = 0.020%
mean observed delta = +0.01000

shock scale = 0.12

aliased:
false-beneficial = 96.07%
mean observed delta = -0.03507

domain-separated observational:
false-beneficial = 41.80%
mean observed delta = +0.00989

paired:
false-beneficial = 0.021%
mean observed delta = +0.01000

shock scale = 0.20

aliased:
false-beneficial = 97.51%
mean observed delta = -0.06508

domain-separated observational:
false-beneficial = 45.17%
mean observed delta = +0.00980

paired:
false-beneficial = 0.018%
mean observed delta = +0.01000

INTERPRETATION
DOMAIN SEPARATION fixes BIAS.

It does not by itself remove observational VARIANCE.

PAIRED COMMON-DISTURBANCE comparison addresses the variance from the shared environmental disturbance.

This distinction is important:

domain separation
!=
complete causal estimator.

PART C — SIMULTANEOUS ROLE-CHANGE CREDIT

QUESTION
What happens if two local roles change at once
and the cell receives only one combined local consequence?

TOY
Two independently distributed role-effect gradients are perturbed simultaneously.

A negative total delta is treated as:
both role increases were useful.

Trials:
1,000,000

RESULT

approximately 49.94% of trials had one beneficial and one harmful role change.

Among trials where the combined consequence was beneficial,
approximately 24.89% of all reinforced role assignments were actually individually harmful.

Therefore:
a single scalar consequence applied indiscriminately to multiple simultaneous role changes creates severe attribution error even with zero environmental noise.

This is an IDENTIFIABILITY problem.

No temporal smoothing fixes it.

CAUSAL-CREDIT DESIGN CONSEQUENCE
A future local meta-rule needs a way to separate:

WHAT CHANGED

from

WHAT IMPROVED.

At minimum,
one of the following is required:

1. sparse one-role-at-a-time exploratory perturbations;
2. perturbations separated by known local domains/tags;
3. sufficiently rich local action memory to attribute consequences;
4. structured counterfactual prediction;
5. another mechanism providing identifiable action credit.

Do not allow every simultaneously changing local sensitivity to consume the same scalar reward.

RELATION TO STAB-18-R1
The causal lesson strongly matches the R1 pre-execution confound:

- intervention selection must not alias with future stochastic dynamics;
- paired counterfactual futures require controlled stochastic comparability;
- durable RNG restoration alone is not enough if the intervention and future update fields are structurally correlated.

AR-U6 independently demonstrates why this matters for future lifetime adaptation.

AR-U6 DOES NOT MODIFY R1.

PREFERRED FUTURE META-RULE SHAPE
A safer conceptual sequence is:

sparse bounded local perturbation
->
domain-separated perturbation identity
->
wait declared causal horizon
->
compare against local expected/intact consequence
under matched disturbance evidence
->
update only the perturbed sensitivity

rather than:

many role changes
->
observe one later scalar
->
reinforce everything that changed.

COMPUTE WARNING
Literal per-cell paired future rollouts would be expensive.

This audit establishes an INFORMATION requirement,
not a production implementation.

Before implementation,
research cheaper approximations such as:
- learned local forward prediction;
- temporal-difference residuals;
- staggered sparse perturbations;
- naturally occurring perturbations with action tags;
- local eligibility traces;
- shared population probes.

NEXT
AR-U7 — CHEAP CAUSAL CREDIT APPROXIMATIONS

Compare:
1. sparse staggered perturbation + eligibility trace;
2. local predictive-error residual;
3. short paired local probe where affordable;
4. naive delayed reward baseline.

Measure:
- causal-sign accuracy;
- adaptation quality;
- extra update cost;
- stability.

AR-C1 remains the other parallel frontier:
repeated decentralized context ordering.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX_AND_ANALYTIC
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
delayed_credit_trials_per_condition = 200000
aliasing_trials_per_condition = 500000
simultaneous_credit_trials = 1000000
