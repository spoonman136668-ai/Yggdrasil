TITLE: DG-1A-AR-H17 — Context-Conditioned Delayed Structural Credit Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE CONTEXT-CONDITIONED CREDIT RESULT + FINGERPRINT-QUALITY LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh16-delayed-structural-confirmation-credit-audit.ice

PURPOSE
H16 established that delayed structural confirmation needs:
- nomination provenance;
- eligibility;
- credit freshness.

A fixed age horizon is crude.

A 70-opportunity-old confirmation may still be relevant if the local causal context is unchanged,
while a 10-opportunity-old confirmation may already be stale after a topology change.

H17 asks:

Can delayed nomination credit be conditioned on a compact non-semantic local context fingerprint?

QUESTION
Can the organism learn:

THIS NOMINATION MECHANISM WORKS IN CONTEXT-LIKE-THIS

without allocating a permanent semantic regime ID?

BOUNDARY
This is synthetic.

It does not:
- prove real Yggdrasil exposes this exact context coordinate;
- freeze logistic trust prediction;
- authorize one memory slot per environment;
- solve context identification under globally ambiguous observations;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

CAUSAL CONTEXT STREAM
1500 structural opportunities.

Latent local causal contexts:

A:
opportunities 0..499.

B:
500..999.

A again:
1000..1499.

Thus the lifecycle is:

A
->
B
->
A.

No semantic A/B label is provided to the controller.

NOMINATION MECHANISMS
Two anonymous candidate-generation mechanisms:

H0
and
H1.

Confirmation probabilities in context A:

H0:
0.90

H1:
0.20.

In context B:

H0:
0.10

H1:
0.85.

Thus the useful nomination mechanism depends strongly on local causal context.

DELAY
Structural confirmation delay:

base:
80 opportunities

uniform jitter:
+/-60.

Therefore feedback arrives approximately:

20 through 140 opportunities

after the nomination.

Feedback can cross context boundaries.

CONTEXT FINGERPRINT
Synthetic latent context coordinate:

A center:
-1.

B center:
+1.

Observed local context fingerprint:

latent_context
+
Gaussian noise.

Primary fingerprint noise SD:

0.20.

This is an anonymous continuous local descriptor.

It is not a semantic regime ID.

Each pending nomination stores:

- nomination mechanism identity;
- observed context fingerprint at nomination time;
- eventual confirmation outcome.

CONTEXT-CONDITIONED TRUST MODEL
Each nomination mechanism has a tiny two-parameter logistic trust predictor:

bias
+
weight * context_fingerprint.

At current time:

current local fingerprint
->
predicted confirmation probability
for H0 and H1.

Choose the higher predicted value with:

10% exploratory selection.

When delayed confirmation arrives:

update the model of
THE ORIGINAL NOMINATION MECHANISM

using:

THE STORED NOMINATION-TIME CONTEXT FINGERPRINT.

Learning rate:
0.08.

This is a bounded continuous trust map,
not one memory slot per context.

COMPARATORS

GLOBAL EXACT TRUST
Exact nomination provenance,
but one context-independent trust scalar per mechanism.

GLOBAL NAIVE
Delayed outcome is credited without correct temporal identity/context discipline.

GLOBAL AGE-GATED
Global exact trust with H16-style fixed age filtering.

CONTEXT-CURRENT
Use context-conditioned trust,
but train delayed outcomes using the context visible at feedback time.

This deliberately loses nomination-time context provenance.

CONTEXT-STORED
Use context-conditioned trust
and train each delayed outcome at the stored nomination-time fingerprint.

PRIMARY CONFIRMATION
100 matched synthetic streams.

PRIMARY RESULTS

GLOBAL EXACT TRUST

late A1 correct H0 selection:
0.9502

early B correct H1:
0.1745

late B:
0.9479

early returning A correct H0:
0.0686

late A2:
0.9496

total expected-selection regret:
259.40

median B adaptation latency:
128.5 opportunities

median A-return latency:
155.

INTERPRETATION
Exact delayed provenance prevents identity corruption,
but one global trust value must relearn from scratch after every context transition.

It has no way to remember:

H0 was good in A
while
H1 was good in B.

GLOBAL NAIVE

A1:
0.7239

B early:
0.3561

B late:
0.7861

A2 early:
0.3151

A2 late:
0.7500

regret:
431.30

B latency:
105

A2 latency:
106.5

with only:
98%

stable recovery in each transition test.

This is substantially worse overall.

GLOBAL AGE-GATED

A1:
0.9502

B early:
0.3135

B late:
0.9479

A2 early:
0.1001

A2 late:
0.9435

regret:
243.64

mean dropped confirmations:
690.24

B latency:
101

A2 latency:
150.5.

Age filtering reduces some obsolete credit
but still cannot remember context-dependent validity.

CONTEXT-CURRENT
Context-conditioned model,
but delayed outcomes are trained at feedback-time context.

A1:
0.9502

B early:
0.3054

B late:
0.9479

A2 early:
0.8700

A2 late:
0.9495

regret:
148.41

mean delayed outcomes whose current fingerprint sign differs from their nomination fingerprint:
160.04.

B latency:
111.

A-return latency:
0.

INTERPRETATION
Even an imperfect current-context model retains some useful contextual structure,
but cross-boundary delayed outcomes are trained into the wrong context region.

CONTEXT-STORED
Correct nomination-time context provenance.

A1:
0.9502

B early:
0.7213

B late:
0.9479

A2 early:
0.9501

A2 late:
0.9496

regret:
92.84

B latency:
50

A-return latency:
0.

PRIMARY POSITIVE
Storing the context fingerprint from nomination time dramatically improves delayed trust assignment.

The first A -> B transition still requires learning B.

But when A returns,
the controller immediately reuses the previously learned A-conditioned trust relation.

Thus:

CONTEXT-CONDITIONED TRUST
CAN PRESERVE REUSABLE CAUSAL HISTORY
WITHOUT ONE SEMANTIC REGIME SLOT PER ENVIRONMENT.

RECURRENCE RESULT
Global trust:

after B,
A-return early accuracy:
6.9%.

Stored-context trust:

A-return early:
95.0%.

The difference is not merely faster forgetting.

It is retention of:

CONDITIONAL VALIDITY.

H0 did not become globally good or globally bad.

Its usefulness depended on context.

RELATION TO H16
H16 used:

AGE

as a proxy for credit relevance.

H17 shows a stronger abstraction:

CREDIT RELEVANCE
DEPENDS ON
CONTEXT SIMILARITY / CONDITIONING,
NOT AGE ALONE.

Old confirmation can remain useful when its causal context recurs.

CONTEXT-FINGERPRINT NOISE SWEEP
Stored-context policy.

100 matched streams per condition.

FINGERPRINT NOISE SD = 0

B early accuracy:
0.8449

A-return early:
0.9507

regret:
78.73

B adaptation latency:
24.

NOISE = 0.20

B early:
0.7213

A-return:
0.9501

regret:
92.84

B latency:
50.

NOISE = 0.50

B early:
0.5167

A-return:
0.8668

regret:
132.45

B latency:
86.5.

NOISE = 0.80

B early:
0.3785

A-return:
0.5732

regret:
196.90

B latency:
115

A-return latency:
98.

NOISE = 1.20

B early:
0.2785

A-return:
0.2281

late A-return:
0.8953

regret:
267.48

B latency:
146.5

A-return latency:
178.5.

PRIMARY FINGERPRINT NEGATIVE
Context-conditioned credit is only as good as the context representation.

As context fingerprints become noisy enough to overlap strongly,
the conditional trust map loses its advantage.

Therefore:

CONTEXT MEMORY
CANNOT MANUFACTURE
CONTEXT IDENTIFIABILITY.

This repeats the same general limit found in:
- source independence;
- temporal artifact rejection;
- causal control selection.

STORED CONTEXT
vs
CURRENT CONTEXT
The credit object should preserve:

WHAT LOCAL CONTEXT DID THIS DECISION ACTUALLY OCCUR IN?

not simply ask:

WHAT CONTEXT AM I IN NOW
WHEN THE RESULT FINALLY ARRIVES?

Delayed adaptive decisions need historical context provenance.

CURRENT DELAYED-CREDIT OBJECT
A pending structural decision should conceptually carry:

NOMINATION MECHANISM IDENTITY

+

CANDIDATE IDENTITY

+

NOMINATION-TIME CONTEXT FINGERPRINT

+

CREATION TIME

+

RESOURCE COST SPENT

+

ELIGIBILITY / AGE

+

EVENTUAL CAUSAL CONFIRMATION.

Then trust learning can condition on:

the decision's original context

rather than:
the feedback-time context.

GENERAL ARCHITECTURAL PRINCIPLE
Do not store only:

WHO ACTED?

Also store enough bounded context to answer:

UNDER WHAT LOCAL CONDITIONS DID THAT ACTION OCCUR?

This applies beyond structural nomination.

Potential future uses include:
- control trust;
- inherited-prior expression trust;
- value-of-information policy trust;
- role-transition credit.

DECISION
AR-H17 is POSITIVE WITH A CONTEXT-IDENTIFIABILITY LIMIT.

Supported synthetically:

- delayed credit benefits from stored nomination-time context;
- continuous context-conditioned trust can preserve context-specific causal history without semantic regime IDs;
- recurring contexts can reuse old trust immediately;
- fixed age filtering cannot provide the same recurrence benefit;
- feedback-time context is not a valid substitute for decision-time context;
- noisy/overlapping context fingerprints eventually destroy the advantage.

Not demonstrated:

- real Yggdrasil context fingerprints;
- optimal context representation;
- nonlinear context-conditioned trust;
- bounded distributed context fingerprints;
- provenance-safe context aggregation;
- context learning when the latent causal state is not directly observable.

NEXT CLEAN QUESTION
AR-H18 — PROVENANCE-DIVERSE CONTEXT FINGERPRINT CONFIDENCE

H17's current limit is context identifiability.

Question:

Can several partially independent local context cues produce a compact confidence-weighted fingerprint
that remains useful when any one cue becomes noisy or corrupted?

Compare:

A.
single context cue;

B.
raw average of multiple cues;

C.
provenance-aware independent-cue aggregation;

D.
common-mode cue corruption;

E.
confidence-gated fallback to global trust when context identity is unreliable.

Desired:

good independent context evidence
->
strong conditional trust.

ambiguous / correlated context evidence
->
reduce reliance on context-conditioned trust

rather than:
confidently route delayed credit into the wrong context.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_streams = 100
stream_opportunities = 1500
context_sequence = A,B,A
switches = 500,1000
confirmation_delay_base = 80
confirmation_delay_jitter = 60
primary_context_noise_sd = 0.20
context_trust_learning_rate = 0.08
exploration_fraction = 0.10
