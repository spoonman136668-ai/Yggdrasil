TITLE: DG-1A-AR-H137 — Hidden-Minority Detection Lower Bound / Abstention Economy Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC + ANALYTIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh136-representative-canary-topology-audit.ice

PURPOSE

H136 showed that small canary sets can be geometrically representative while still missing a causally coherent minority.

H137 asks:

WHEN A MINORITY FAILURE MODE IS NOT PREDICTABLE FROM PRE-AUDIT METADATA,

what evidence budget is mathematically required to detect it with a chosen confidence?

And:

when that evidence budget is too expensive,

should the organism buy more evidence

or

abstain from family-wide promotion?

BOUNDARY

Synthetic + analytic research only.

It does not:
- implement biological tissue;
- establish production thresholds;
- prove one universal risk tolerance;
- execute or modify STAB-18-R1;
- spend canonical scientific execution.

ANALYTIC STARTING POINT

For family size N,
hidden minority size m,
and k uniformly sampled canaries without replacement,

the exact probability of missing every minority member is:

P_miss = C(N - m, k) / C(N, k)

when k <= N - m.

Large-N approximation:

P_miss approximately (1 - f)^k

where:

f = m / N.

For target miss probability delta,

approximate required sample count is:

k >= log(delta) / log(1 - f).

This is a detectability lower bound when:
- minority membership is not predictable from available metadata;
- canaries are not allowed oracle access to current residuals before purchase.

PRIMARY ANALYTIC GRID

N:
30, 50, 70, 90.

Hidden minority fraction:
5%, 10%, 20%, 30%.

Target miss probability:
5%.

Record:
- exact k required;
- approximate k required;
- gap between fixed budgets 5 and 9 and the exact certificate.

PRIMARY SYNTHETIC ECOLOGY

2,500 worlds.

Family size:
30 to 90.

Regimes:
R1 stable;
R2 hidden 5% minority;
R3 hidden 10% minority;
R4 hidden 20% minority;
R5 hidden 30% minority;
R6 whole-family coherent shift.

Hidden minority membership is deliberately independent of ordinary topology in the primary uninformative-metadata condition.

Member value is heterogeneous.

A separate stress makes the hidden minority disproportionately high value.

METADATA PREDICTABILITY CONDITIONS

P0 — UNINFORMATIVE
Metadata carries no useful minority signal.

P1 — WEAK
Risk score is weakly correlated with minority membership.

P2 — MEDIUM
Risk score is materially but imperfectly correlated.

P3 — STRONG
Risk score is strongly but imperfectly correlated.

COMPARATORS

A — FIXED-5 FORCED
Audit 5.
If fresh sampled evidence is coherent, broadcast.

B — FIXED-9 FORCED
Audit 9.
If fresh sampled evidence is coherent, broadcast.

C — CERTIFY-10
Buy enough uniform evidence to certify detection of a 10% hidden minority at <=5% miss probability, unless dissent is found earlier.
If the exact required k is reached with no dissent, broadcast.

D — METADATA-STRATIFIED-9
Use 9 canaries with risk-stratified selection.

E — COST-AWARE ESCALATE-OR-ABSTAIN
Begin with 5 canaries.
If dissent appears, do not broadcast.
If no dissent appears:
- compute the exact remaining sample requirement for the target minority certificate;
- buy additional evidence only when the expected value of family-wide resolution exceeds the evidence cost plus a preregistered risk reserve;
- otherwise abstain and keep unresolved debt dormant.

F — FULL FAMILY CHECK
Audit every member.

PRIMARY ECONOMIC SCALE

Correct resolution benefit:
3.0 x member value.

False promotion penalty:
5.0 x member value.

Audit cost:
1.0 per member.

Broadcast application cost:
0.20 per reached member.

Dormant unresolved carry cost:
0.15 x member value.

Risk reserve for policy E:
2.0 expected-value units per uncertified expected false member.

The scale is synthetic and comparative only.

PRIMARY METRICS

1. analytic miss probability;
2. exact required k;
3. mean net value;
4. evidence audits/event;
5. weighted coverage;
6. false-promotion rate;
7. hidden-minority miss/broadcast rate;
8. abstention rate;
9. 10th and 1st percentile net;
10. high-value-minority loss;
11. certificate cost as fraction of family size.

PRIMARY ACCEPTANCE SHAPE

The hidden-minority lower-bound claim is supported if:
- empirical miss rates agree with exact hypergeometric predictions within sampling error;
- fixed budgets 5 and 9 materially exceed 5% miss probability for hidden 5% and 10% minorities across much of N=30..90.

The abstention claim is supported if COST-AWARE ESCALATE-OR-ABSTAIN:
- reduces hidden-minority false promotion relative to FIXED-5 and FIXED-9;
- materially improves 1st-percentile net in high-value-minority stress;
- uses less evidence than FULL FAMILY CHECK;
- does not require universal escalation to the full family;
- preserves a defensible positive mean net or explicitly exposes a mean/tail tradeoff.

FAILURE CONDITIONS

Treat H137 as mixed/negative if:
- empirical miss rates contradict the analytic lower bound;
- metadata-stratified 9-canary selection reliably certifies uninformative hidden minorities;
- abstention fails to improve downside risk;
- confidence certification always costs essentially full-family audit;
- the result depends on one family size.

ROBUSTNESS

Target miss probability:
1%, 5%, 10%.

Hidden minority fraction:
5%, 10%, 20%, 30%.

Family size:
30..90.

Metadata predictive power:
uninformative, weak, medium, strong.

High-value minority multiplier:
1x, 2x, 3x.

INTERPRETATION GUARDRAIL

A positive lower-bound result means:

WHEN FAILURE MEMBERSHIP
IS HIDDEN
FROM AVAILABLE FEATURES,

NO CLEVER CANARY TOPOLOGY
CAN CREATE INFORMATION
THAT WAS NOT PURCHASED.

Metadata can reduce evidence cost only to the extent that it predicts the hidden partition.

Abstention is a legitimate developmental action:

KEEP THE DEBT DORMANT

rather than:

PROMOTE AN UNCERTIFIED FAMILY MODEL.

FROZEN BEFORE EXECUTION

Analytic grid, comparators, economic scale, primary metrics, acceptance shape, and robustness dimensions above are fixed before execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = ANALYTIC_PLUS_SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = 71027e77fc154268dc6f026f2e4c2a1d26d66eac
