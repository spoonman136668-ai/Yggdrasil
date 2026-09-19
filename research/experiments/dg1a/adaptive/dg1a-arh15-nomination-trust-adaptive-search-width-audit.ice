TITLE: DG-1A-AR-H15 — Nomination Trust / Adaptive Search-Width Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE REVERSIBLE SEARCH-TRUST AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh14-bounded-composite-candidate-generation-audit.ice

PURPOSE
H14 separated:

CHEAP STRUCTURAL NOMINATION

from

CAUSAL STRUCTURAL AUTHORITY.

A cheap top-K nomination can reduce expensive cooperative search by over 90%,
but persistent residual-correlated decoys can crowd a narrow shortlist.

H15 asks:

Can the search policy itself acquire reversible trust from its history of:
nomination
->
causal confirmation
or
causal rejection?

QUESTION
When should the organism trust a narrow cheap shortlist,
and when should it spend more resources on a wider search?

BOUNDARY
This is synthetic.

It does not:
- freeze a shortlist threshold;
- define a production trust update;
- prove real Yggdrasil has these exact nomination success rates;
- allow nomination trust to authorize permanent structural write;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

META-CONTROLLER TOY
H15 abstracts the H14 structural-search outcomes into repeated structural opportunities.

Two search modes are available.

NARROW-FIRST

top-4 nomination
->
6 candidate pairs.

If the narrow shortlist contains the true cooperative pair,
median causal-confirmation cost is approximated from H14 as:

576 pair-probe evaluations.

If the narrow shortlist fails,
the organism eventually falls back to the wider search.

narrow failure + fallback cost:

2520 pair-probe evaluations.

WIDE-DIRECT

top-6 nomination
->
15 candidate pairs.

Approximate direct confirmation cost:

1800 pair-probe evaluations.

These are synthetic cost abstractions derived from H14 working points.

They are not production constants.

ECONOMIC SWITCH THRESHOLD
Let:

p
=
current trust that narrow search will contain useful structure.

Expected narrow-first cost:

p * 576
+
(1-p) * 2520.

Wide-direct cost:

1800.

Thus narrow-first is cheaper when:

p > 0.37037.

This threshold comes from the tested synthetic costs.

It is not a biological constant.

TRUST EVIDENCE
After causal confirmation,
the controller can observe whether the causally validated structure was already inside the narrow shortlist.

Thus:

narrow nomination confirmed
->
trust success.

narrow missed but wide recovered
->
trust failure.

The trust update is downstream of causal confirmation.

Nomination correlation alone does not update trust positively.

SEARCH ENVIRONMENT
Three sequential phases.

PHASE A1
100 structural opportunities.

Mostly clean nomination geometry,
but 25% of opportunities contain isolated severe decoy bursts.

Clean narrow success probability:

0.995.

Severe decoy narrow success probability:

0.005.

The burst mixture creates noisy trust evidence.

PHASE B
100 opportunities.

Persistent severe decoy topology.

Narrow success probability:

0.005.

PHASE A2
100 opportunities.

Return to the mostly clean environment with the same 25% intermittent decoy bursts.

The wide search is treated as the reliable fallback working point for this meta-audit.

H14 measured approximately:
99% true-pair inclusion
for the wide top-6 shortlist under the severe decoy stress.

H15 approximates it as reliable in order to isolate trust dynamics.

COMPARATORS

STATIC NARROW-FIRST
Always try narrow before widening.

STATIC WIDE
Always use top-6 directly.

CUMULATIVE TRUST
All historical confirmation outcomes have equal permanent weight.

RECENCY TRUST — SLOW
EMA alpha:
0.02.

RECENCY TRUST — MEDIUM
alpha:
0.08.

RECENCY TRUST — FAST
alpha:
0.30.

RECENCY TRUST — VERY FAST
alpha:
0.60.

Decision:

if estimated narrow success trust
>= 0.37037

use narrow-first.

Otherwise:

use wide-direct.

PRIMARY CONFIRMATION
1000 matched synthetic trust streams.

MEAN PAIR-PROBE COST PER OPPORTUNITY

STATIC NARROW-FIRST

A1:
780.06 under the 10%-burst diagnostic precursor.

Under the final 25%-burst primary stream:

A1:
1068.04

B persistent decoy:
2509.17

A2:
1093.31.

STATIC WIDE

A1:
1800

B:
1800

A2:
1800.

Interpretation:

narrow-first is resource efficient when nomination geometry is mostly valid,
but extremely wasteful under persistent decoy crowding.

Wide-direct is robust but permanently expensive.

CUMULATIVE TRUST

A1:
1068.04

B:
2489.17

A2:
1093.31.

Wide-search fraction:

A1:
0.56%

B:
2.88%

A2:
3.46%.

PRIMARY CUMULATIVE NEGATIVE
Permanent history prevents trust from retiring quickly enough.

After a long clean history,
persistent decoy failure does not reduce trust below the economic switch threshold within most of the tested stress phase.

This repeats the S9 result:

PERMANENT TRUST
CAUSES AUTHORITY HANGOVER.

SLOW RECENCY
alpha 0.02.

Mean cost:

A1:
1063.98

B:
2036.90

A2:
1270.92.

Wide fraction:

A1:
0%

B:
66.68%

A2:
27.92%.

Median-like mean stable-switch latency into wide mode:

33.35 opportunities.

Return-to-narrow latency after clean restoration:

28.27.

Interpretation:

slow recency eventually adapts,
but spends too long paying failed narrow-search cost after topology change.

MEDIUM RECENCY
alpha 0.08.

Cost:

A1:
1064.04

B:
1863.71

A2:
1134.26.

Wide fraction:

A1:
0.005%

B:
91.05%

A2:
9.10%.

Stable switch latency after persistent decoy onset:

8.97 opportunities.

Return-to-narrow latency:

9.46.

This is a strong stability/plasticity working point.

FAST RECENCY
alpha 0.30.

Cost:

A1:
1089.87

B:
1817.28

A2:
1114.44.

Wide fraction:

A1:
3.62%

B:
97.58%

A2:
6.45%.

Stable switch latency:

2.46 opportunities.

Return-to-narrow:

3.82.

The fast controller adapts quickly while preserving reasonably low clean-phase wide-search use.

VERY FAST RECENCY
alpha 0.60.

Cost:

A1:
1173.14

B:
1813.10

A2:
1182.47.

Wide fraction:

A1:
14.81%

B:
98.16%

A2:
15.91%.

Stable switch latency:

1.36.

Return-to-narrow:

4.20.

PRIMARY VERY-FAST NEGATIVE
The very-fast trust estimator reacts almost immediately to persistent decoys,
but isolated decoy bursts in otherwise useful conditions repeatedly suppress narrow-search trust.

This creates unnecessary wide-search activation.

Thus:

FAST REACTIVITY
IS NOT
STABLE SEARCH POLICY.

PRIMARY POSITIVE
A recency-weighted nomination-trust state can:

use the cheap narrow shortlist during stable valid conditions;

retire narrow-search authority when persistent causal rejection appears;

activate a more expensive wider search;

and later restore narrow-search authority when causal confirmation returns.

No semantic topology-change label is required.

TRUST AUTHORITY BOUNDARY
Nomination trust controls:

HOW MUCH SEARCH BUDGET TO SPEND.

It does NOT control:

WHETHER STRUCTURE IS PERMANENTLY WRITTEN.

Permanent structural write still requires:

H12/H13 functional causal confirmation.

Therefore a bad trust estimate can cause:

extra probe cost
or
slower discovery,

but should not directly create false heredity.

RELATION TO S9
S9 showed:

CONTROL SOURCE IDENTITY
!=
CURRENT CONTROL TRUST.

H15 establishes the analogous rule:

NOMINATION HEURISTIC EXISTS
!=
NOMINATION HEURISTIC DESERVES CURRENT SEARCH-BUDGET AUTHORITY.

Both use reversible trust rather than permanent authority.

RELATION TO H6
H6 separated:

stored inherited prior

from

current expression trust.

The same architecture pattern now appears again:

NOMINATION MECHANISM

is durable capability.

NOMINATION TRUST

is current permission to spend expensive search resources through it.

DO NOT DELETE THE HEURISTIC
When trust falls,
the nomination mechanism should normally be:

SUPPRESSED

not:

DESTROYED.

If the causal topology reverts,
trust can recover.

CURRENT STRUCTURAL-SEARCH CONTROL STACK
CHEAP NOMINATION SIGNAL

+

NOMINATION PROVENANCE / TYPE

+

CAUSAL CONFIRMATION HISTORY

+

RECENCY

+

SEARCH COST

+

CURRENT NOMINATION TRUST

->

NARROW
or
WIDE
STRUCTURAL SEARCH BUDGET.

Then:

CANDIDATE PAIRS

->

FUNCTIONAL CAUSAL MICROPROBES

->

PERSISTENT COOPERATIVE UTILITY

->

PERMANENT STRUCTURAL WRITE.

GENERAL PRINCIPLE
Yggdrasil increasingly separates:

CAPABILITY

from

CURRENT AUTHORITY.

Examples:

stored prior
vs
expression trust;

source provenance
vs
control trust;

nomination heuristic
vs
search-budget trust.

This lets durable mechanisms survive temporary invalidity without continuing to control behavior.

DECISION
AR-H15 is POSITIVE.

Supported synthetically:

- nomination validity can change over time;
- cumulative trust preserves obsolete search authority;
- moderate recency rapidly shifts search budget after persistent causal rejection;
- very fast trust overreacts to intermittent decoy bursts;
- nomination trust can later recover after topology reversion;
- search-budget authority can be separated from permanent structural-write authority.

Not demonstrated:

- real Yggdrasil nomination-trust signal;
- optimal trust timescale;
- optimal search-width ladder;
- simultaneous trust over multiple nomination heuristics;
- interaction with hard global metabolic budgets;
- trust under delayed causal structural confirmation.

CLEAN SCIENTIFIC PAUSE
H12-H15 now form a coherent structural-discovery architecture:

H12:
candidate structure must earn functional causal value.

H13:
useful structure can be cooperative / non-additive.

H14:
cheap weak evidence can nominate which composite structures deserve expensive causal testing.

H15:
nomination mechanisms need reversible trust that controls search budget,
not hereditary authority.

The next work should not merely sweep more trust alphas or shortlist widths.

NEXT HIGH-VALUE QUESTION
AR-H16 — DELAYED STRUCTURAL CONFIRMATION / TRUST CREDIT

Question:

What happens when causal confirmation of a structural nomination arrives much later than the nomination itself?

Can the organism correctly update:
- which nomination mechanism deserved credit;
- which search-width choice was efficient;

without attributing delayed success to a newer unrelated nomination state?

This connects:
H15 nomination trust

with:
S6 delayed resource credit
and
eligibility-trace logic.

Desired:

retain action / nomination eligibility until structural consequence arrives;

expire stale nomination credit;

avoid rewarding whichever heuristic happens to be active when delayed confirmation finally appears.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
meta_streams = 1000
phase_opportunities = 100,100,100
primary_clean_burst_probability = 0.25
narrow_success_cost = 576
narrow_failure_with_fallback_cost = 2520
wide_direct_cost = 1800
economic_trust_threshold = 0.37037
