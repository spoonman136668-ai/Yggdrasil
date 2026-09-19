TITLE: DG-1A-AR-H136 — Representative Canary Topology / Subgroup-Coverage Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX MIXED-NEGATIVE PRIMARY HYPOTHESIS + REPRESENTATIVENESS LOWER-BOUND SIGNAL
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh135-debt-family-reactivation-audit.ice
PREREGISTRATION_COMMITS:
- de676115f3dd18bbd49f534bb14586f0c0d2fb3e
- cb6b26834cb4893a22c2433766a38c3216fbe6ec

PURPOSE

H135 established that a small fresh canary probe can make debt-family re-audition much safer than blind broadcast.

Its main failure mode was:

CANARY AGREEMENT
WITHOUT
REPRESENTATIVENESS
CAN CREATE FALSE CONFIDENCE.

H136 asks whether topological/context coverage can make the small probe representative enough to detect:

- coherent family reuse;
- sparse local drift;
- local subgroup drift;
- two disjoint subgroup drifts;
- whole-family change.

BOUNDARY

Synthetic research only.

It does not:
- implement living or biological tissue;
- freeze a production topology representation;
- establish one canonical canary algorithm;
- execute or modify STAB-18-R1;
- spend canonical scientific execution.

EVIDENCE

SYNTHETIC
MEASURED_SANDBOX

PREREGISTERED PRIMARY HYPOTHESIS

A coverage-constrained adaptive two-stage canary policy should:

- beat RANDOM and FIXED on mean net value;
- reduce false promotion relative to RANDOM;
- reduce subgroup false broadcast relative to RANDOM;
- stay below 9 mean audits/event;
- preserve >90% stable-family weighted coverage;
- preserve >75% whole-family-shift weighted coverage;
- hold subgroup false promotion below 10%;
- remain positive across all four topology classes.

PRIMARY SYNTHETIC ECOLOGY

2,500 worlds.

Family size:
24 to 90.

Topologies:
- uniform field;
- two-lobe field;
- corridor;
- ring/shell.

Member metadata:
- context coordinates;
- value;
- historical uncertainty;
- dormant residual state.

Fresh regimes:
- stable;
- sparse drift;
- one coherent subgroup drift;
- two disjoint subgroup drifts;
- whole-family shift.

Primary non-adaptive canary budget:
5 members including trigger.

Adaptive:
3-member first stage,
maximum 9.

Primary family-wide gate:

fresh agreement >= 0.80
AND
normalized residual dispersion <= 0.65
AND, for coverage-constrained policies,
normalized topology coverage radius <= 0.45.

COMPARATORS

A — RANDOM.

B — FIXED.

C — GEOMETRIC-DIVERSE.

D — UNCERTAINTY-WEIGHTED.

E — VALUE-WEIGHTED.

F — COVERAGE-CONSTRAINED.

G — ADAPTIVE TWO-STAGE.

PRIMARY RESULTS

ADAPTIVE TWO-STAGE

mean net:
92.37072.

10th percentile net:
6.50102.

1st percentile net:
-17.28860.

mean evidence:
4.1136 audits/event.

mean weighted coverage:
78.783%.

mean false-promotion rate:
12.995%.

broadcast rate:
89.16%.

mean topology coverage radius:
0.31607.

second-stage purchase rate:
60.04%.

RANDOM

mean net:
87.64755.

mean evidence:
5.0.

mean weighted coverage:
72.082%.

mean false-promotion rate:
10.085%.

broadcast rate:
78.92%.

FIXED

mean net:
87.47415.

mean evidence:
5.0.

mean weighted coverage:
71.583%.

mean false-promotion rate:
9.945%.

VALUE-WEIGHTED

mean net:
93.86870.

10th percentile net:
16.33029.

1st percentile net:
-0.13297.

mean weighted coverage:
74.687%.

mean false-promotion rate:
10.250%.

UNCERTAINTY-WEIGHTED

mean net:
75.22753.

mean weighted coverage:
63.043%.

mean false-promotion rate:
8.502%.

1st percentile net:
-244.38603.

COVERAGE-CONSTRAINED / GEOMETRIC

mean net:
91.49898.

mean weighted coverage:
75.666%.

mean false-promotion rate:
11.245%.

PRIMARY DECISION

The preregistered H136 hypothesis is NOT SUPPORTED.

It passes:

- adaptive mean net > RANDOM;
- adaptive mean net > FIXED;
- adaptive mean evidence < 9;
- stable-family coverage > 90%;
- whole-family-shift coverage > 75%;
- positive mean net in all four topology classes.

It fails the safety-critical subgroup criteria:

- adaptive overall false-promotion rate is higher than RANDOM;
- subgroup false-broadcast rate is higher than RANDOM;
- subgroup false-promotion rate is far above 10%.

Therefore:

GEOMETRIC / CONTEXT COVERAGE
IS NOT
A SUFFICIENT CERTIFICATE
OF REPRESENTATIVENESS.

SUBGROUP-DRIFT PRIMARY SLICE

For one- and two-subgroup regimes:

ADAPTIVE

mean net:
28.5340.

mean evidence:
4.8191.

mean weighted coverage:
58.00%.

mean false-promotion rate:
22.16%.

broadcast rate:
74.61%.

subgroup false-broadcast rate:
74.61%.

RANDOM

mean net:
21.6810.

mean weighted coverage:
45.56%.

mean false-promotion rate:
16.73%.

broadcast / false-broadcast rate:
55.84%.

FIXED

mean net:
20.4695.

mean false-promotion rate:
16.59%.

broadcast / false-broadcast rate:
54.47%.

VALUE-WEIGHTED

mean net:
31.5228.

mean false-promotion rate:
17.19%.

broadcast / false-broadcast rate:
56.03%.

UNCERTAINTY-WEIGHTED

mean net:
-3.8992.

mean false-promotion rate:
13.54%.

broadcast / false-broadcast rate:
31.91%.

INTERPRETATION

Adaptive topological coverage increases the chance of broad family reuse.

That improves average coverage and net value.

But:

A SMALL DRIFT SUBGROUP
CAN OCCUPY
A SMALL TOPOLOGICAL REGION

THAT DOES NOT CONTROL
THE FAMILY'S
MAXIMUM COVERAGE RADIUS.

The canary set can be:

geometrically broad

and still:

causally blind.

STABLE-FAMILY SLICE

Adaptive weighted coverage:
96.23%.

Adaptive broadcast:
100%.

Adaptive mean net:
149.12.

WHOLE-FAMILY-SHIFT SLICE

Adaptive weighted coverage:
89.53%.

Adaptive broadcast:
97.23%.

Adaptive mean net:
123.99.

Thus H136 does not fail because the coverage mechanism cannot detect coherent family reuse.

It fails because:

COHERENT MINORITY STRUCTURE
IS NOT GUARANTEED
TO APPEAR
IN A SMALL GEOMETRIC SAMPLE.

TOPOLOGY-CLASS RESULT

Adaptive mean net remained positive and above RANDOM in:

corridor:
89.41 vs 86.41.

ring:
92.13 vs 87.53.

two-lobe:
93.01 vs 86.51.

uniform:
94.86 vs 90.02.

But adaptive false-promotion rates remained approximately:
10.95% to 14.75%
across topology classes.

The failure therefore is not confined to one geometry.

ROBUSTNESS SWEEP

27 preregistered combinations across:

topology coverage threshold:
0.35, 0.45, 0.55.

initial canaries:
3, 4, 5.

maximum budget:
7, 9, 12.

Adaptive mean net range:
82.72 to 106.60.

Adaptive mean evidence range:
3.72 to 5.88.

Adaptive stable coverage range:
95.46% to 98.15%.

Adaptive whole-shift coverage range:
77.46% to 93.96%.

But subgroup false-promotion rate range:
18.33% to 26.26%.

Subgroup false-broadcast range:
60.92% to 86.96%.

Even the best subgroup-false-rate working point remained:

18.33%.

That is:

well above
the preregistered 10% threshold.

Tightening geometric coverage therefore:

DOES NOT
SOLVE
THE HIDDEN-SUBGROUP PROBLEM.

HIGH-VALUE MINORITY STRESS

A targeted stress forced:

- a small 7% to 12% local subgroup;
- high value concentrated in that subgroup;
- trigger inside the minority subgroup;
- historical uncertainty concentrated in the wrong region.

1,200 worlds.

ADAPTIVE

mean net:
80.75867.

mean evidence:
5.21833.

mean weighted coverage:
77.999%.

mean false-promotion rate:
11.925%.

subgroup false-broadcast:
96.333%.

VALUE-WEIGHTED

mean net:
-230.68038.

mean weighted coverage:
21.110%.

mean false-promotion rate:
86.499%.

subgroup false-broadcast:
88.167%.

RANDOM

mean net:
51.33908.

mean false-promotion rate:
7.782%.

subgroup false-broadcast:
59.833%.

PRIMARY VALUE-WEIGHTING FAILURE

When the highest-value members belong to a coherent minority anomaly,
value-weighted canaries can:

over-sample the anomaly

then:

mistake it
for the family-wide model.

This creates:

VALUE-AMPLIFIED FALSE CONSENSUS.

Therefore:

VALUE
IS NOT
REPRESENTATIVENESS.

UNCERTAINTY-WEIGHTING LIMIT

Uncertainty-weighted selection is more conservative in the primary ecology.

But:

- it sacrifices too much coverage/net value;
- if uncertainty metadata points to the wrong region, it is not a representativeness guarantee;
- uncertainty is useful as one sampling axis, not as the sole audit topology.

GENERAL PRINCIPLE

A SMALL CANARY SET
CANNOT CERTIFY
AN ARBITRARY HIDDEN MINORITY

UNLESS:

SOME PRE-AUDIT FEATURE
CORRELATES
WITH THAT MINORITY

OR:

THE ORGANISM
BUYS
ENOUGH EVIDENCE

OR:

THE ORGANISM
ABSTAINS
FROM FAMILY-WIDE PROMOTION.

This is the central H136 result.

The failure is deeper than:

pick better geometric points.

It is:

AN INFORMATION LIMIT.

REPRESENTATIVENESS
MUST BE DEFINED
IN THE SPACE
WHERE FAILURE MODES
CAN ACTUALLY DIFFER.

That space may include:

- context;
- lineage;
- historical residual signature;
- translator family;
- uncertainty;
- value;
- causal source independence;
- recent disturbance history;
- prior contradiction topology.

No one axis is sufficient by itself.

DECISION

AR-H136 is:

MIXED-NEGATIVE

for:

RAW TOPOLOGY-COVERAGE CANARIES

and:

STRONGLY POSITIVE

for the new inference:

REPRESENTATIVENESS REQUIRES
AN EVIDENCE-SUFFICIENCY CERTIFICATE,
NOT JUST
A GEOMETRIC COVERAGE CERTIFICATE.

NEXT HIGH-VALUE MOVE

AR-H137 — HIDDEN-MINORITY DETECTION LOWER BOUND / ABSTENTION ECONOMY AUDIT

Question:

IF
A COHERENT MINORITY
IS NOT PREDICTABLE
FROM PRE-AUDIT METADATA,

HOW MANY CANARIES
ARE REQUIRED
TO DETECT IT
WITH A CHOSEN CONFIDENCE?

And:

WHEN THAT EVIDENCE COST
IS TOO HIGH,

SHOULD THE ORGANISM:

BUY MORE EVIDENCE

or:

REFUSE
FAMILY-WIDE PROMOTION?

Analytic starting point:

For a hidden minority fraction f
sampled without useful predictive metadata,

miss probability is approximately:

(1 - f)^k

for k independent canaries.

To make miss probability <= delta:

k >= log(delta) / log(1 - f).

This implies approximately:

f = 10%, delta = 5%:
about 29 canaries.

f = 20%, delta = 5%:
about 14 canaries.

f = 30%, delta = 5%:
about 9 canaries.

Thus:

A FIXED MAXIMUM BUDGET OF 9

CANNOT
GUARANTEE
95% DETECTION

OF AN ARBITRARY
10% HIDDEN MINORITY.

H137 should test:

A.
forced fixed-budget broadcast;

B.
confidence-bound evidence purchase;

C.
metadata-stratified sampling at varying predictive power;

D.
abstain / keep debt dormant;

E.
cost-aware escalation;

F.
rare high-value minority;

G.
whole-family shift.

Desired principle:

IF REPRESENTATIVENESS
CANNOT BE CERTIFIED
CHEAPLY,

DO NOT
TURN
UNCERTAINTY
INTO
FAMILY-WIDE FACT.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_worlds = 2500
adaptive_mean_net = 92.37072
adaptive_mean_evidence = 4.1136
adaptive_mean_coverage = 0.78783
adaptive_mean_false_rate = 0.12995
random_mean_net = 87.64755
random_mean_false_rate = 0.10085
value_mean_net = 93.86870
value_mean_false_rate = 0.10250
subgroup_adaptive_false_rate = 0.2216
subgroup_random_false_rate = 0.1673
robustness_combinations = 27
best_robust_subgroup_false_rate = 0.18328334795517717
high_value_minority_value_policy_net = -230.68038
high_value_minority_value_policy_false_rate = 0.86499
