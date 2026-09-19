TITLE: DG-1A-AR-H21 — Value-of-Information-Gated Context Validation Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE SELECTIVE-CHALLENGE RESULT + BLANKET-VALIDATION NEGATIVE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh20-functional-context-change-validation-audit.ice

PURPOSE
H20 established that a bounded functional challenge can distinguish:
- a genuine causal context transition;
- a persistent observational false context.

But H20 can still spend many probes whenever a context proposal becomes persistent.

H21 asks:

WHEN IS FUNCTIONAL CONTEXT VALIDATION WORTH ITS COST?

BOUNDARY
This is synthetic.

It does not:
- freeze a challenge cost;
- freeze a value function;
- prove the organism knows true challenge resolvability;
- define a central scheduler;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

EVENT POPULATION
20,000 persistent context proposals per synthetic run.

20 matched runs for the primary comparison.

Each proposal carries:

OBSERVATIONAL CONFIDENCE
q
=
estimated probability that the proposed context is genuine.

q is sampled between:
0.55
and
0.99

with a high-confidence skew.

FUNCTIONAL IMPACT
wrong-context cost:

0.5
2.0
6.0

with frequencies:

60%
30%
10%.

This is an abstract combination of:
functional stake
and
policy divergence.

CHALLENGE RESOLVABILITY
Two latent causal-difference classes.

STRONG:
45%.

H20 strong working point:

genuine transition:
old mechanism 0.10
proposed mechanism 0.85.

false context:
old 0.90
proposed 0.20.

MODERATE:
55%.

genuine:
old 0.40
proposed 0.65.

false/reversed:
old 0.65
proposed 0.40.

The resolvability class is used by the analytic VoI comparator.

It is NOT assumed available to a real local implementation.

URGENCY
15% of proposals have a hard challenge cap:

4 pairs.

Other proposals allow up to:

12 pairs.

CHALLENGE COST
Per paired functional challenge:

0.025 synthetic loss units.

AVAILABLE CHALLENGE COUNTS

0
2
4
8
12

subject to local urgency cap.

NO-CHALLENGE ACTION
If no functional challenge is purchased,
accept the persistent context proposal.

Expected functional loss:

(1 - q)
*
wrong-context impact.

CHALLENGE ACTION
For a challenge budget k,
use the H20 Beta-posterior acceptance rule.

If the proposed-context mechanism reaches:
P(new > old) >= 0.95

accept the new context.

Otherwise:
hold the old context.

Expected total loss includes:

functional wrong-context loss

+

challenge resource cost.

POLICIES

ACCEPT OBSERVATION
Never challenge.

FIXED-4
Always spend four paired functional challenges.

FIXED-8
Spend eight,
subject to urgent cap.

UNCERTAINTY-ONLY
Spend up to eight pairs when:
q < 0.78.

Ignore functional impact and challenge resolvability.

IMPACT-ONLY
Spend up to eight when:
wrong-context impact >= 2.

Ignore observational confidence and challenge resolvability.

ANALYTIC VoI UPPER BOUND
For each proposal,
choose:

0
2
4
8
or
12

to minimize expected:

functional routing loss
+
probe cost.

This comparator knows the synthetic challenge-resolvability class.

It is an upper-bound resource principle,
not an implementable Yggdrasil policy.

PRIMARY RESULTS
Mean weighted total loss per proposal.

ACCEPT OBSERVATION

loss:
0.22013

mean challenge pairs:
0.

FIXED-4

loss:
0.86098

pairs:
4.00.

FIXED-8

loss:
0.77941

effective mean pairs:
7.40.

UNCERTAINTY-ONLY

loss:
0.27325

pairs:
1.37.

IMPACT-ONLY

loss:
0.59320

pairs:
2.97.

ANALYTIC VoI

loss:
0.18837

pairs:
0.902.

PRIMARY BLANKET-VALIDATION NEGATIVE
Always purchasing causal context validation is strongly harmful in this mixed population.

Reason:

when the causal difference is weak,
a bounded challenge often cannot confirm the genuine transition,
so the organism pays probe cost
AND
delays or suppresses a real context change.

Thus:

MORE CAUSAL VALIDATION
IS NOT AUTOMATICALLY SAFER.

Validation must itself have positive expected value.

PRIMARY VoI POSITIVE
The analytic VoI policy improves total loss relative to simply accepting the persistent observation:

0.22013
->
0.18837.

Improvement:
approximately 14.4%.

At the same time it spends only:

0.90 paired challenges per proposal on average.

It challenges only approximately:

9.8%

of proposals.

Thus:
the best synthetic policy is highly selective.

WHERE THE VoI BUDGET GOES
Across a 200,000-proposal diagnostic population:

STRONG-RESOLVABILITY proposals

mean pairs:
1.994

fraction challenged:
21.78%.

MODERATE-RESOLVABILITY proposals

mean pairs:
0

fraction challenged:
0%.

Interpretation:

under the current H20 challenge model,
the analytic controller recognizes that moderate effects are not worth probing with the available bounded test.

This is a limitation of the test,
not evidence that moderate context effects are unimportant.

FUNCTIONAL IMPACT ALLOCATION

impact 0.5:

mean pairs:
0.005

challenged:
0.25%.

impact 2.0:

mean:
1.594

challenged:
20.30%.

impact 6.0:

mean:
4.174

challenged:
35.57%.

Thus high-impact ambiguity attracts more causal validation.

OBSERVATIONAL CONFIDENCE EFFECT
Lower-confidence proposals attract more challenge budget.

For proposals with:

q < 0.65

mean pairs:
1.77

challenged:
33.94%.

For:

q < 0.75

mean:
1.48

challenged:
18.92%.

Across the full high-confidence population:
only about 9.8% are challenged.

CHALLENGE-BUDGET DISTRIBUTION
Approximate analytic choices:

0 pairs:
90.20%.

2:
0.15%.

4:
0.34%.

8:
5.90%.

12:
3.41%.

This is a sparse adaptive validation economy.

PRIMARY PRINCIPLE
The organism should not ask:

CAN I GET MORE CAUSAL EVIDENCE?

It should ask:

IS THE EXPECTED FUNCTIONAL IMPROVEMENT FROM MORE CAUSAL EVIDENCE WORTH ITS RESOURCE COST AND DELAY?

This is the context-routing form of the S4-S9 evidence economy.

RELATION TO S4-S9
S4:
evidence is a finite adaptive resource.

S5:
allocate evidence by value,
not uncertainty alone.

S6:
learned VoI is possible
but can become stale/confounded.

S7-S9:
resource credit needs causal controls,
provenance,
and reversible trust.

H21 shows:
the SAME resource-economy abstraction applies to context validation.

No second evidence scheduler is required conceptually.

CURRENT CONTEXT-VALIDATION LOOP
PERSISTENT CONTEXT PROPOSAL

+

OBSERVATIONAL CONFIDENCE

+

PREDICTED POLICY DIVERGENCE

+

FUNCTIONAL STAKE

+

EXPECTED CHALLENGE RESOLVABILITY

+

PROBE COST

+

DEADLINE

->

ACCEPT OBSERVATION
or
HOLD
or
BUY FUNCTIONAL CHALLENGE.

Then:

CAUSAL CHALLENGE RESULT

->

CONTEXT AUTHORITY UPDATE.

IMPORTANT NEGATIVE
The analytic VoI comparator knows:
challenge resolvability.

A real Yggdrasil cell will not.

Therefore H21 establishes a VALUE PRINCIPLE,
not the implementation.

A learned controller could waste resources if it overestimates:
how informative a context challenge will be.

NEXT CLEAN QUESTION
AR-H22 — LEARNED CONTEXT-CHALLENGE VALUE

Question:

Can a bounded local learner estimate:
whether context challenge is worth purchasing

from its own history of:

context proposal
+
challenge cost
+
causal outcome
+
eventual functional consequence?

Required stress:

- challenge policy maturation;
- topology change;
- stale challenge-value estimates;
- passive consequence confounding;
- causal-control integrity.

The design should reuse S6-S9 machinery
rather than create a new global learner.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_events_per_run = 20000
primary_matched_runs = 20
strong_resolvability_fraction = 0.45
urgent_fraction = 0.15
pair_cost = 0.025
analytic_mean_pairs_per_proposal = 0.902
