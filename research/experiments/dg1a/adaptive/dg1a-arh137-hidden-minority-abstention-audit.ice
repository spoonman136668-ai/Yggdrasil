TITLE: DG-1A-AR-H137 — Hidden-Minority Detection Lower Bound / Abstention Economy Audit
DATE: 2026-09-19
STATUS: ANALYTIC + SYNTHETIC / MEASURED_SANDBOX POSITIVE DETECTABILITY LOWER BOUND + POSITIVE TAIL-RISK CERTIFICATION + MIXED ABSTENTION ECONOMY
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh136-representative-canary-topology-audit.ice
PREREGISTRATION_COMMIT: 2a0edee8170e9f23926425a1cac84b8dc6744b26

PURPOSE

H136 showed that a small canary set can be geometrically representative and still miss a causally coherent hidden minority.

H137 asks:

WHEN MINORITY MEMBERSHIP
IS NOT PREDICTABLE
FROM PRE-AUDIT METADATA,

what evidence budget is mathematically required to detect that minority with a chosen confidence?

And:

what is gained or lost by:

- forcing broadcast from a small sample;
- buying a statistical evidence certificate;
- using predictive metadata;
- escalating or abstaining?

BOUNDARY

Synthetic + analytic research only.

It does not:
- implement biological tissue;
- establish production thresholds;
- freeze one universal risk tolerance;
- execute or modify STAB-18-R1;
- spend canonical scientific execution.

EVIDENCE

ANALYTIC
SYNTHETIC
MEASURED_SANDBOX

ANALYTIC LOWER BOUND

For family size N,
hidden minority size m,
and k uniformly sampled canaries without replacement:

P_miss =
C(N - m, k)
/
C(N, k).

This is exact when:
- minority identity is hidden from pre-audit metadata;
- canaries do not have oracle access to current residuals before selection.

Large-N approximation:

P_miss approximately (1 - f)^k.

The finite-family hypergeometric correction matters substantially for small N.

PRIMARY EXACT 95%-DETECTION GRID

Target:
P_miss <= 0.05.

N = 30

5% hidden:
m = 2,
k_exact = 23,
certificate fraction = 76.67%.

10% hidden:
m = 3,
k_exact = 19,
certificate fraction = 63.33%.

20% hidden:
m = 6,
k_exact = 11,
certificate fraction = 36.67%.

30% hidden:
m = 9,
k_exact = 8,
certificate fraction = 26.67%.

N = 50

5% hidden:
m = 3,
k_exact = 31,
certificate fraction = 62.00%.

10% hidden:
m = 5,
k_exact = 22,
certificate fraction = 44.00%.

20% hidden:
m = 10,
k_exact = 12,
certificate fraction = 24.00%.

30% hidden:
m = 15,
k_exact = 8,
certificate fraction = 16.00%.

N = 70

5% hidden:
m = 4,
k_exact = 37,
certificate fraction = 52.86%.

10% hidden:
m = 7,
k_exact = 24,
certificate fraction = 34.29%.

20% hidden:
m = 14,
k_exact = 13,
certificate fraction = 18.57%.

30% hidden:
m = 21,
k_exact = 8,
certificate fraction = 11.43%.

N = 90

5% hidden:
m = 5,
k_exact = 40,
certificate fraction = 44.44%.

10% hidden:
m = 9,
k_exact = 25,
certificate fraction = 27.78%.

20% hidden:
m = 18,
k_exact = 13,
certificate fraction = 14.44%.

30% hidden:
m = 27,
k_exact = 8,
certificate fraction = 8.89%.

PRIMARY LOWER-BOUND RESULT

A 9-canary maximum is enough for:

approximately 30% hidden minorities at 95% detection

but:

NOT

for arbitrary 5% or 10% hidden minorities.

This is not a canary-placement bug.

Under uninformative metadata:

THE REQUIRED INFORMATION
HAS NOT BEEN PURCHASED.

FIXED-BUDGET MISS PROBABILITIES

For a hidden 10% minority:

N = 30:
k=5 miss = 56.65%.
k=9 miss = 32.76%.

N = 50:
k=5 miss = 57.66%.
k=9 miss = 35.37%.

N = 70:
k=5 miss = 58.08%.
k=9 miss = 36.39%.

N = 90:
k=5 miss = 58.30%.
k=9 miss = 36.94%.

For a hidden 5% minority:

N = 30:
k=5 miss = 68.97%.
k=9 miss = 48.28%.

N = 50:
k=5 miss = 72.40%.
k=9 miss = 54.39%.

N = 70:
k=5 miss = 73.84%.
k=9 miss = 56.92%.

N = 90:
k=5 miss = 74.64%.
k=9 miss = 58.30%.

EMPIRICAL CHECK

20,000 Monte Carlo draws per:
N / hidden-fraction / k cell.

Tested:
N = 30, 50, 70, 90.
f = 5%, 10%, 20%, 30%.
k = 5, 9.

Maximum absolute empirical-minus-exact miss-probability error:

0.00633.

Thus the synthetic miss behavior agrees with the exact hypergeometric prediction within ordinary sampling error.

PRIMARY ANALYTIC CLAIM

SUPPORTED.

TARGET-CONFIDENCE SENSITIVITY

For a hidden 10% minority:

N = 30

99% detection:
k = 23.

95% detection:
k = 19.

90% detection:
k = 16.

N = 50

99%:
29.

95%:
22.

90%:
18.

N = 70

99%:
33.

95%:
24.

90%:
19.

N = 90

99%:
35.

95%:
25.

90%:
20.

Thus:

DETECTION CONFIDENCE
IS A DIRECT
EVIDENCE-BUDGET CONTROL KNOB.

SYNTHETIC POLICY ECOLOGY

Primary:
2,500 worlds.

Family size:
30 to 90.

Regimes:
- stable;
- hidden 5%;
- hidden 10%;
- hidden 20%;
- hidden 30%;
- coherent whole-family shift.

Primary metadata condition:
uninformative.

Economic scale retained from preregistration:

correct resolution:
+3 x value.

false promotion:
-5 x value.

audit:
-1 per member.

broadcast application:
-0.20 per member.

unresolved carry:
-0.15 x value.

PRIMARY POLICY RESULTS

FIXED-5 FORCED

mean net:
96.77124.

10th percentile:
-5.28174.

1st percentile:
-9.98781.

mean evidence:
4.2864.

weighted coverage:
64.255%.

mean false-promotion rate:
3.518%.

hidden-minority false-broadcast / miss rate:
25.36%.

broadcast rate:
65.60%.

FIXED-9 FORCED

mean net:
86.23572.

10th percentile:
-5.32633.

1st percentile:
-10.45066.

mean evidence:
6.7292.

weighted coverage:
56.574%.

mean false-promotion rate:
1.604%.

hidden-minority miss:
14.28%.

broadcast:
54.52%.

CERTIFY-10

Target:
95% detection of a 10% hidden minority.

mean net:
71.89025.

10th percentile:
-5.58568.

1st percentile:
-10.76472.

mean evidence:
12.754.

weighted coverage:
49.829%.

mean false-promotion rate:
0.426%.

hidden-minority miss:
3.96%.

broadcast:
44.20%.

COST-AWARE ESCALATE-OR-ABSTAIN

mean net:
73.08590.

10th percentile:
-0.86004.

1st percentile:
-5.54560.

mean evidence:
13.492.

weighted coverage:
50.952%.

mean false-promotion rate:
0.385%.

hidden-minority miss:
3.60%.

broadcast:
43.84%.

METADATA-STRATIFIED-9
under uninformative metadata:

mean net:
91.37631.

1st percentile:
1.93688.

evidence:
9.

weighted coverage:
60.956%.

false-promotion rate:
1.663%.

hidden-minority miss:
14.72%.

This is statistically similar in hidden-minority detection to another 9-sample policy when metadata carries no real signal.

FULL FAMILY CHECK

mean net:
129.44423.

mean evidence:
60.3108.

coverage:
100%.

false promotion:
0.

PRIMARY POLICY INTERPRETATION

The aggressive fixed-5 policy has the highest mean net among bounded policies in the primary low-tail-cost ecology.

But it purchases that mean by:

ACCEPTING
A LARGE
UNCERTIFIED
HIDDEN-MINORITY MISS RATE.

CERTIFY-10 and COST-AWARE:

reduce hidden-minority false broadcast by roughly:
7x
relative to FIXED-5,

at the cost of:
more evidence
and:
lower mean coverage.

Thus:

CERTIFICATION
IS NOT FREE.

It trades:
average opportunistic reuse

for:
lower false-family promotion risk.

HIGH-VALUE MINORITY STRESS

Minority member values multiplied by 3x.

2,500 worlds.

FIXED-5

mean net:
83.44178.

1st percentile net:
-163.91975.

hidden-minority miss:
26.92%.

FIXED-9

mean net:
81.75164.

1st percentile:
-59.30959.

hidden-minority miss:
15.28%.

CERTIFY-10

mean net:
73.74392.

1st percentile:
-12.65201.

hidden-minority miss:
4.28%.

COST-AWARE

mean net:
76.38467.

1st percentile:
-6.11913.

hidden-minority miss:
4.20%.

PRIMARY TAIL-RISK POSITIVE

As hidden-minority value rises:

small forced-broadcast samples develop:
catastrophic negative tails.

The 3x stress changes FIXED-5 1st percentile from:

approximately -10

to:

approximately -164.

Certification policies hold the 1st-percentile loss near:

-6 to -13.

This supports:

EVIDENCE CERTIFICATION
AS A TAIL-RISK CONTROL,

even when:
its mean value is lower.

2x HIGH-VALUE STRESS

FIXED-5:
mean net 91.392,
1st percentile -65.5455.

FIXED-9:
mean net 85.0583,
1st percentile -12.9662.

CERTIFY-10:
mean net 73.2059,
1st percentile -10.8339.

COST-AWARE:
mean net 75.2560,
1st percentile -5.5151.

The downside transition is smooth:

as minority value rises,
uncertified small-sample broadcast becomes increasingly fragile.

METADATA PREDICTABILITY RESULT

9-canary metadata-stratified hidden-minority miss rate:

UNINFORMATIVE:
15.61%.

WEAK:
13.17%.

MEDIUM:
8.11%.

STRONG:
1.33%.

The strong-predictor condition beats the fixed 9-canary hidden-minority miss rate dramatically.

But:

this improvement appears only because:
metadata now contains information about minority identity.

Thus H137 confirms:

METADATA
CAN BUY
EVIDENCE EFFICIENCY

ONLY TO THE EXTENT
THAT IT PREDICTS
THE HIDDEN PARTITION.

No predictive signal:
no free reduction in the statistical sample requirement.

ABSTENTION ECONOMY RESULT

The preregistered COST-AWARE policy did not frequently abstain for economic-price reasons after unanimous first-stage evidence.

Across 5,000 diagnostic worlds:

unanimous first-stage cases:
3,301.

economic escalation margin <= 0:
0.

minimum positive escalation margin:
34.72 value units.

Therefore:

under the current synthetic reward scale,
additional evidence is economically too cheap relative to:
per-member resolution benefit.

COST-AWARE abstention is driven primarily by:
observed dissent,

not:
evidence-price refusal.

This is a real limitation of the current toy economics.

FULL-AUDIT DOMINANCE LIMIT

FULL FAMILY CHECK has the highest primary mean net:

129.44.

Why?

Because the current toy gives:
+3 resolution benefit
for each audited member
against:
1 audit cost.

Therefore:
auditing another member
is often intrinsically profitable.

That makes:

EVIDENCE
ARTIFICIALLY CHEAP.

This does not invalidate the hidden-minority lower bound.

It does mean:

H137 CANNOT YET
ESTABLISH
THE ECONOMIC
ABSTENTION BOUNDARY

for a resource-constrained organism.

GENERAL PRINCIPLE

H137 establishes two separate layers:

LAYER 1 — INFORMATION LAW

If minority identity is hidden from available metadata,
the probability of missing it is governed by the amount of evidence purchased.

No sampling cleverness removes that requirement.

LAYER 2 — ECONOMIC POLICY

Whether to buy the required evidence
depends on:

- evidence cost;
- active-member value;
- latency;
- opportunity cost;
- tail-risk tolerance;
- how many members are actually worth resolving now.

The current H137 economic toy makes evidence too cheap to locate that boundary cleanly.

DECISION

AR-H137 is:

POSITIVE

for:

HIDDEN-MINORITY DETECTION LOWER BOUND

and:

POSITIVE

for:

CERTIFICATION AS TAIL-RISK CONTROL.

It is:

MIXED / INCOMPLETE

for:

ECONOMIC ABSTENTION POLICY

because:
the current per-audit reward structure makes escalation almost always economically favorable.

SUPPORTED

- empirical miss rates match hypergeometric predictions;
- fixed 5/9 budgets cannot certify small hidden minorities;
- 95% detection of a hidden 10% minority often requires roughly 19 to 25 audits for N=30..90;
- hidden 5% minorities can require 23 to 40 audits;
- high-value hidden minorities create severe downside tails under forced small-sample broadcast;
- statistical certification sharply reduces those tails;
- predictive metadata reduces sample cost only when it genuinely carries minority information.

NOT DEMONSTRATED

- realistic compute/latency price of evidence;
- sparse activation where most dormant members have no immediate resolution value;
- dynamic evidence prices under load;
- multi-family competition for audit budget;
- optimal risk reserve;
- sequential Bayesian stopping with learned priors;
- adversarial metadata corruption.

NEXT HIGH-VALUE MOVE

AR-H138 — EVIDENCE-PRICE / ACTIVE-VALUE SPARSITY / ABSTENTION PHASE-TRANSITION AUDIT

Question:

WHEN
ONLY A SMALL FRACTION
OF DEBT-FAMILY MEMBERS
ARE CURRENTLY
WORTH RESOLVING,

and:

AUDIT CAPACITY
HAS
REAL OPPORTUNITY COST,

where is the boundary between:

BROADCAST,

BUY MORE EVIDENCE,

LOCAL-ONLY RESOLUTION,

and:

ABSTAIN / KEEP DEBT DORMANT?

Critical change:

DO NOT
PAY
A +3 RESOLUTION BENEFIT
FOR EVERY AUDITED DORMANT MEMBER.

Instead model:

- active-value sparsity;
- audit compute price;
- latency/opportunity cost;
- competing family audit demand;
- tail-risk reserve.

Hypothesis:

A genuine abstention region should emerge
once:

EVIDENCE COST
AND
ACTIVE VALUE
ARE DECOUPLED.

Desired result:

THE ORGANISM
SHOULD KNOW
WHEN
NOT TO THINK
ABOUT A DORMANT FAMILY
YET.

This is directly aligned with:

permanently active structure
and:
resource-bounded developmental intelligence.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class = ANALYTIC_PLUS_SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_worlds = 2500
empirical_draws_per_grid_cell = 20000
max_empirical_exact_miss_error = 0.00633
fixed5_hidden_miss = 0.2536
fixed9_hidden_miss = 0.1428
certify10_hidden_miss = 0.0396
costaware_hidden_miss = 0.0360
fixed5_primary_mean_net = 96.77124
certify10_primary_mean_net = 71.89025
costaware_primary_mean_net = 73.08590
fixed5_high_value_3x_p01 = -163.91975
certify10_high_value_3x_p01 = -12.65201
costaware_high_value_3x_p01 = -6.11913
full_family_primary_mean_evidence = 60.3108
