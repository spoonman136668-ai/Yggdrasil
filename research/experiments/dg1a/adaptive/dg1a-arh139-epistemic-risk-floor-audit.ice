TITLE: DG-1A-AR-H139 — Non-Negotiable Epistemic Risk Floor / Compute-Shock Invariance Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX MIXED-POSITIVE RISK-FLOOR RESULT + CLAIM-SCOPE LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh138-evidence-price-abstention-phase-audit.ice
PREREGISTRATION_COMMIT: 57dd665730eb12063e73eda0fe955d2d5fe15852
PREREGISTRATION_COMMIT: 57dd665730eb12063e73eda0fe955d2d5fe15852

PURPOSE

H138 found a dangerous optimization shortcut:

when fresh evidence becomes expensive,
a scalar expected-value controller can stop buying confidence
and broadcast with less evidence
if current active reward is large enough.

That can increase mean reward while increasing hidden-minority miss risk.

H139 separates:

ECONOMIC VALUE

from:

EPISTEMIC ADMISSIBILITY.

Question:

SHOULD
THE EVIDENCE STANDARD
FOR A FAMILY-WIDE CLAIM
BE ALLOWED
TO FALL
WHEN COMPUTE
BECOMES EXPENSIVE?

Primary candidate answer:

NO.

Resource scarcity may reduce:
how often a family-wide claim is made.

It must not reduce:
the evidence required for the same admissibility class.

BOUNDARY

Synthetic research only.

It does not:
- implement living or biological tissue;
- establish a production confidence standard;
- prove 5% is universally correct;
- execute or modify STAB-18-R1;
- spend canonical scientific execution.

EVIDENCE CLASS TARGET

SYNTHETIC
MEASURED_SANDBOX

PRIMARY ECOLOGY

Same sparse-active-value ecology as H138.

Family size:
40 to 100.

Active fraction:
5%, 10%, 20%, 40%, 80%.

Evidence price:
0.5, 1, 2, 4, 8.

Regime prior:
CLEAN = 50%.
HIDDEN-10 = 35%.
HIDDEN-20 = 15%.

3,000 worlds per primary cell.

Minority identity is independent of:
active state,
member value,
ordinary topology
in the primary ecology.

PRIMARY EPISTEMIC CLAIM CLASS

The broadcast claim is:

THE STORED FAMILY MODEL
IS SAFE TO APPLY
FAMILY-WIDE
AGAINST
AN UNMARKED MINORITY
OF AT LEAST 10%.

For a uniform without-replacement audit:

admissibility at miss floor delta requires:

C(N-m,k) / C(N,k) <= delta

for:

m = ceil(0.10 N).

The primary hard floor uses:

delta = 0.05.

A secondary floor uses:

delta = 0.10.

POLICIES

A — H138 ECONOMIC OPTIMIZER

The completed H138 risk-aware policy.

It may:
broadcast from five compatible canaries
when expected value favors broadcast.

No hard epistemic floor.

B — HARD-FLOOR-5

Audit active trigger.

Use the same economic pre-probe gate as H138.

If family inference is worth considering:
buy to five canaries.

If dissent appears:
do not broadcast.

After five compatible canaries:

FAMILY-WIDE BROADCAST IS INADMISSIBLE

until the exact 10%-minority / 5%-miss certificate is complete.

If the certificate's estimated economic value is positive:
buy the certificate.

If it is not:
ABSTAIN.

There is no:
uncertified broadcast fallback.

C — HARD-FLOOR-10

Same,
but:
delta = 0.10.

D — HARD-FLOOR-5 / AUDIT-CAP-23

Same admissibility floor as B.

Per-family fresh audit capacity:
23 members.

If:
k_cert > 23,

the family-wide claim cannot be certified
inside the current audit budget.

Then:
ABSTAIN.

Do not:
lower the evidence floor.

This intentionally creates:
budget-driven epistemic silence
for some larger families.

E — HARM-BOUNDED

After five compatible canaries,
broadcast is allowed only if:

q_post * L_hidden <= 5.0 value units.

Otherwise:
buy the 5% certificate if economically positive,
else:
abstain.

This comparator tests:

harm admissibility

versus:

knowledge admissibility.

It can legitimately accept:
a higher claim-error probability
when predicted current harm is low.

F — FULL-FAMILY

Audit every member.

REFERENCE ECONOMICS

Use H138's active-value-decoupled scoring unchanged:

active correct resolution:
+3 x value.

active false promotion:
-5 x value.

inactive false promotion:
-0.5 x value.

unresolved active carry:
-0.15 x value.

broadcast application:
-0.20 x N.

audited inactive:
no immediate resolution reward.

PRIMARY METRICS

1. mean net value;
2. 1st-percentile net;
3. evidence audits/event;
4. active weighted coverage;
5. false-promotion rate;
6. conditional HIDDEN-10 false-broadcast rate;
7. conditional HIDDEN-20 false-broadcast rate;
8. broadcast rate;
9. certificate purchase rate;
10. epistemic abstention rate;
11. economic local/defer rate;
12. audit-cap refusal rate.

PRIMARY ACCEPTANCE SHAPE

The non-negotiable-risk-floor thesis is supported if:

- HARD-FLOOR-5 HIDDEN-10 false-broadcast remains approximately <=5% across evidence prices, subject to Monte Carlo sampling error;
- rising evidence price lowers broadcast/certificate frequency or raises abstention, rather than increasing admissible miss probability;
- HARD-FLOOR-5 does not show H138's price-shock increase in hidden-minority miss;
- HARD-FLOOR-10 produces higher coverage/lower evidence than HARD-FLOOR-5 but a measurably higher hidden miss rate;
- CAP-23 responds to insufficient budget by refusing claims, not by silently degrading confidence;
- the hard-floor policies use materially less evidence than FULL-FAMILY;
- hard floors improve severe downside under high-value hidden-minority stress;
- expected-value optimizer retains higher mean value in at least some cells, exposing the real safety/value tradeoff rather than hiding it.

FAILURE CONDITIONS

Treat H139 as mixed/negative if:

- hard-floor hidden miss rises materially with evidence price;
- budget caps trigger uncertified broadcasts;
- certification fails to control conditional HIDDEN-10 miss;
- hard floor effectively requires full-family audit everywhere;
- hard-floor abstention does not increase when certification becomes unaffordable;
- correlation stresses invalidate the statistical floor despite uniform sampling.

ROBUSTNESS

Price shock:
0.5 -> 8 after five compatible canaries.

Family size:
40, 70, 100.

Target hidden fraction:
5%, 10%, 20%.

Hard-floor delta:
1%, 5%, 10%.

Active/minority correlation:
independent,
active concentrated inside minority,
active concentrated outside minority.

Value/minority correlation:
independent,
one high-value active minority member.

Additional challenge:

PREDICTIVE METADATA
may be used to reduce audit cost only if:
its calibration has been established on held-out synthetic worlds.

Uncalibrated metadata:
cannot substitute for the statistical floor.

INTERPRETATION GUARDRAIL

H139 does not claim:

EVERY FAMILY BROADCAST
MUST USE
THE SAME SAMPLE COUNT.

It claims:

THE ADMISSIBILITY STANDARD
MUST NOT
BE RELAXED
MERELY BECAUSE
EVIDENCE BECAME EXPENSIVE.

Equivalent calibrated evidence
may satisfy the standard more cheaply.

If no admissible path fits the resource budget:

ABSTAIN.

FROZEN BEFORE EXECUTION

Ecology, claim class, policies, economics, primary metrics, acceptance shape, and robustness dimensions above are fixed before execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = 2e47dd4359eadee30765cb544f3d54e82b608c80


EXECUTION RESULT

CORRECTED PRIMARY RUN

The H139 implementation uses the preregistered:
- 10%-minority claim class;
- exact hypergeometric certificate;
- 5% and 10% miss floors;
- H138 active-value-decoupled economics;
- H138 pre-probe economic gate;
- certificate-or-abstain hard-floor behavior;
- audit-cap refusal behavior.

The previously discarded run that rounded the hidden-10 minority size was not used.

For this corrected run:

m = ceil(0.10 N).

Primary grid:
5 active fractions x 5 evidence prices.

3,000 worlds per cell.

Total:
75,000 worlds.

Deterministic replication seed:
20260919139.

IMPLEMENTATION REALIZATION NOTE

The repository preregistration inherited H138's "primary value variance" but did not encode the exact generating distribution used in the original H138 sandbox.

This corrected H139 run therefore records the explicit realization used here:

member value:
lognormal,
mean normalized to approximately 1,
sigma = 0.60.

Family size:
uniform integer 40..100.

Active count:
round(active_fraction x N),
minimum 1.

Minority membership:
uniform without replacement in the primary ecology.

Active status:
independent of minority membership in the primary ecology.

Trigger:
uniform among active members.

Fresh non-trigger audit order:
uniform without replacement.

This is a measured-sandbox realization,
not a claim that every H138 numeric aggregate is bit-for-bit reproduced.

The H138 comparator under this realization nevertheless reproduces the same qualitative phase behavior and approximately the previously recorded aggregate evidence use.

PRIMARY AGGREGATE RESULT

H138 ECONOMIC OPTIMIZER

mean net:
23.94272.

1st percentile net:
-35.66749.

mean evidence:
3.60109 audits/event.

active weighted coverage:
51.187%.

mean false-promotion rate:
1.631%.

conditional HIDDEN-10 false-broadcast rate:
29.853%.

conditional HIDDEN-20 false-broadcast rate:
16.673%.

broadcast rate:
41.588%.

certificate purchase:
2.915%.

economic local/defer:
57.500%.

HARD-FLOOR-5

mean net:
7.26990.

1st percentile net:
-48.88667.

mean evidence:
8.41480 audits/event.

active weighted coverage:
36.395%.

mean false-promotion rate:
0.0714%.

conditional HIDDEN-10 false-broadcast rate:
1.845%.

conditional HIDDEN-20 false-broadcast rate:
0.062%.

broadcast rate:
21.039%.

certificate purchase:
30.193%.

epistemic abstention:
12.412%.

economic local/defer:
57.395%.

HARD-FLOOR-10

mean net:
9.13332.

1st percentile net:
-56.32179.

mean evidence:
7.53064 audits/event.

active weighted coverage:
38.418%.

mean false-promotion rate:
0.1629%.

conditional HIDDEN-10 false-broadcast rate:
4.044%.

conditional HIDDEN-20 false-broadcast rate:
0.363%.

broadcast rate:
23.956%.

certificate purchase:
33.367%.

epistemic abstention:
9.239%.

economic local/defer:
57.395%.

HARD-FLOOR-5 / AUDIT-CAP-23

mean net:
2.56361.

1st percentile net:
-42.51922.

mean evidence:
6.71096 audits/event.

active weighted coverage:
30.143%.

conditional HIDDEN-10 false-broadcast rate:
1.397%.

conditional HIDDEN-20 false-broadcast rate:
0.036%.

broadcast rate:
14.909%.

certificate purchase:
21.372%.

epistemic abstention:
21.233%.

audit-cap refusal:
12.053%.

HARM-BOUNDED

mean net:
8.54833.

1st percentile net:
-48.99467.

mean evidence:
7.52473 audits/event.

active weighted coverage:
40.806%.

conditional HIDDEN-10 false-broadcast rate:
9.197%.

conditional HIDDEN-20 false-broadcast rate:
4.334%.

broadcast rate:
27.261%.

certificate purchase:
24.783%.

epistemic abstention:
7.828%.

FULL-FAMILY

mean net:
-152.09246.

mean evidence:
70.09465 audits/event.

active weighted coverage:
100%.

false family promotion:
0%.

PRIMARY RISK-FLOOR RESULT

The core H139 thesis passes in the corrected primary ecology.

HARD-FLOOR-5 HIDDEN-10 false-broadcast remains below the preregistered 5% floor at every evidence price.

By evidence price:

PRICE 0.5

HARD-FLOOR-5:
HIDDEN-10 false-broadcast:
2.810%.

certificate purchase:
48.753%.

epistemic abstention:
0.967%.

evidence:
11.9797.

PRICE 1

HIDDEN-10 false-broadcast:
2.858%.

certificate:
42.540%.

epistemic abstention:
5.107%.

evidence:
10.8056.

PRICE 2

HIDDEN-10 false-broadcast:
1.833%.

certificate:
31.273%.

epistemic abstention:
13.507%.

evidence:
8.7106.

PRICE 4

HIDDEN-10 false-broadcast:
1.315%.

certificate:
20.327%.

epistemic abstention:
19.807%.

evidence:
6.5747.

PRICE 8

HIDDEN-10 false-broadcast:
0.405%.

certificate:
8.073%.

epistemic abstention:
22.673%.

evidence:
4.0034.

Thus:

AS EVIDENCE PRICE RISES,

THE POLICY
MAKES FEWER
FAMILY-WIDE CLAIMS

AND

ABSTAINS MORE.

It does not:

RELAX
THE CLAIM'S
EVIDENCE FLOOR.

This is the desired compute-shock invariance shape.

MEAN-VALUE / EPISTEMIC TRADEOFF

The H138 economic optimizer retains much higher aggregate mean value:

23.94

versus:

HARD-FLOOR-5:
7.27.

The difference is not a free improvement.

The risk floor purchases:

epistemic admissibility

with:

evidence,
abstention,
and foregone immediate coverage.

Therefore:

SAFETY
AND
SCALAR MEAN VALUE

ARE
NON-IDENTICAL OBJECTIVES.

HARD-5 VERSUS HARD-10

The preregistered tradeoff is observed.

HARD-10 uses less evidence:

7.53
versus
8.41.

It obtains more active weighted coverage:

38.42%
versus
36.40%.

But it accepts a higher HIDDEN-10 false-broadcast rate:

4.04%
versus
1.85%.

Therefore:

A LOOSER FLOOR
BUYS
MORE COVERAGE
WITH
MORE EPISTEMIC RISK.

AUDIT-CAP RESULT

The CAP-23 policy does not silently weaken its floor.

When the exact 5% certificate does not fit the cap:

it refuses the family-wide claim.

Observed audit-cap refusal:

12.053%.

Observed HIDDEN-10 false-broadcast:

1.397%.

This supports:

BUDGET FAILURE
SHOULD PRODUCE
EPISTEMIC SILENCE,

NOT:

QUIETLY
LOWERED CONFIDENCE.

COMPUTE-SHOCK STRESS

Separate stress:

first five compatible canaries cost:
0.5 each.

Then incremental certificate evidence price jumps to:
8.

Stress active fractions:
40% and 80%.

12,000 total worlds.

H138 ECONOMIC OPTIMIZER

mean net:
70.86714.

mean evidence:
4.7150.

conditional HIDDEN-10 false-broadcast:
55.445%.

certificate purchase:
0%.

broadcast:
73.942%.

HARD-FLOOR-5

mean net:
-0.04141.

mean evidence:
8.3640.

conditional HIDDEN-10 false-broadcast:
1.113%.

certificate purchase:
20.108%.

epistemic abstention:
53.833%.

broadcast:
13.875%.

HARD-FLOOR-10

mean net:
5.97185.

conditional HIDDEN-10 false-broadcast:
4.235%.

epistemic abstention:
41.633%.

CAP-23

conditional HIDDEN-10 false-broadcast:
0.774%.

epistemic abstention:
62.483%.

audit-cap refusal:
20.283%.

This is the strongest H139 confirmation.

When evidence suddenly becomes expensive:

the scalar optimizer frequently sells confidence.

The hard-floor controller instead:

withdraws the claim.

CLAIM-SCOPE ROBUSTNESS

The most important H139 boundary is:

A CERTIFICATE
IS ONLY VALID
FOR
THE FAILURE CLASS
IT CERTIFIES.

A 10%-minority / 5%-miss certificate was challenged against exact hidden fractions:

5%,
10%,
20%.

High-activity,
cheap-evidence stress:

12,000 worlds per hidden fraction.

ACTUAL HIDDEN 5%

false-broadcast:
20.058%.

ACTUAL HIDDEN 10%

false-broadcast:
4.558%.

ACTUAL HIDDEN 20%

false-broadcast:
0.200%.

Therefore:

THE 10% CERTIFICATE
DOES NOT
PROTECT AGAINST
AN ARBITRARY 5% MINORITY.

This is not a failure of the hypergeometric bound.

It is:

CLAIM-SCOPE MISMATCH.

A family may be certified against:

UNMARKED SUBGROUPS
AT OR ABOVE
ONE SIZE SCALE

without being certified against:

SMALLER SUBGROUPS.

DELTA ROBUSTNESS

Exact HIDDEN-10 stress,
high activity,
cheap evidence.

Target delta 1%:

observed false-broadcast:
0.942%.

mean evidence:
19.1152.

Target delta 5%:

observed:
4.867%.

mean evidence:
14.1303.

Target delta 10%:

observed:
9.083%.

mean evidence:
11.7687.

The empirical miss curve tracks the intended risk floor.

HIGH-VALUE MINORITY STRESS

One active minority member is forced to high value.

Exact HIDDEN-10.

Active fraction:
40%.

Evidence price:
1.

15,000 worlds per policy.

H138 ECONOMIC OPTIMIZER

mean net:
3.8347.

1st percentile:
-30.8763.

false-broadcast:
54.420%.

HARD-FLOOR-5

mean net:
4.8574.

1st percentile:
-27.5957.

false-broadcast:
4.680%.

HARD-FLOOR-10

1st percentile:
-29.7391.

false-broadcast:
8.853%.

CAP-23

1st percentile:
-27.9646.

false-broadcast:
3.607%.

HARM-BOUNDED

1st percentile:
-25.4689.

false-broadcast:
4.507%.

The hard floor materially suppresses catastrophic false family promotion in this stress.

HARM-BOUNDED INTERPRETATION

HARM-BOUNDED is not equivalent to an epistemic certificate.

Primary HIDDEN-10 false-broadcast:

9.197%.

This can be rational if:

current predicted harm
is the objective.

It is not valid if the claim being made is:

THE FAMILY MODEL
IS CERTIFIED
AGAINST
AN UNMARKED 10% MINORITY
AT 5% MISS RISK.

Thus:

HARM ADMISSIBILITY

and:

KNOWLEDGE ADMISSIBILITY

must remain distinct types.

TRIGGER-SELECTION CORRELATION LIMIT

The primary exact hypergeometric calculation assumes the counted sample is uniform with respect to minority identity.

The active trigger is uniform over members only when:

activation
is independent of
minority membership.

A high-activity HIDDEN-10 stress with active members deliberately concentrated outside the minority produced:

independent activation:
4.585% false-broadcast.

active concentrated inside minority:
4.520%.

active concentrated outside minority:
5.040%.

The outside-minority case shows the expected small upward pressure because the trigger is no longer an exchangeable uniform draw.

This is near the Monte Carlo boundary,
not a large failure,
but it establishes the rule:

A BIASED TRIGGER
MUST NOT
BE COUNTED
AS UNIFORM EVIDENCE
WITHOUT CALIBRATION.

FAMILY-SIZE EVIDENCE RESULT

For the 10%-minority / 5%-miss certificate:

N = 40:
k_cert = 21.

N = 70:
k_cert = 24.

N = 100:
k_cert = 25.

Thus certificate cost rises sublinearly over this range and remains far below full-family inspection.

Representative active=40%, price=1 runs:

N=40:
mean evidence 16.77
versus full 40.

N=70:
18.98
versus full 70.

N=100:
19.88
versus full 100.

The hard floor therefore does not collapse into full-family audit everywhere.

PRIMARY DECISION

AR-H139 is:

MIXED-POSITIVE.

POSITIVE FOR:

NON-NEGOTIABLE,
CLAIM-SCOPED
EPISTEMIC RISK FLOORS.

SUPPORTED

- evidence price can change whether a claim is attempted;
- evidence price need not change the admissibility requirement for the same claim;
- compute shocks can correctly produce abstention instead of lower-confidence broadcast;
- a hard 5% floor controls the preregistered HIDDEN-10 claim class;
- a 10% floor spends less evidence and accepts more miss risk;
- audit caps can refuse claims without degrading the floor;
- full-family inspection is not required everywhere;
- hard floors substantially reduce high-value hidden-minority catastrophic promotion;
- scalar expected-value optimization can remain more profitable while being less epistemically reliable.

LIMITS

- certification is typed by its target failure class;
- a 10%-minority certificate does not certify 5%-minority safety;
- biased trigger selection can slightly invalidate exchangeability if counted as uniform evidence;
- the exact H138 primary value generator was not fully encoded in the repository preregistration, so this result is a deterministic measured-sandbox realization rather than a bit-for-bit H138 replay;
- no production confidence threshold is established.

GENERAL PRINCIPLE

CONFIDENCE
SHOULD NOT
BE A SCALAR
THAT CAN BE SOLD
FOR COMPUTE.

It should be:

A TYPED EPISTEMIC CONTRACT

specifying at least:

- failure class;
- detectable subgroup scale;
- tolerated miss probability;
- sampling assumptions;
- evidence provenance;
- expiration/context conditions.

If resources cannot satisfy that contract:

THE ORGANISM
SHOULD SAY LESS.

It should not:

CLAIM THE SAME THING
WITH LESS EVIDENCE.

NEXT HIGH-VALUE MOVE

AR-H140 — CLAIM-SCOPE CONTRACT / TRIGGER-BIAS-CORRECTED MULTISCALE CERTIFICATE AUDIT

Question:

CAN
A DEVELOPMENTAL ORGANISM
CARRY
TYPED CONFIDENCE

SO THAT:

A 10% SUBGROUP CERTIFICATE
IS NEVER
MISTAKEN FOR

A 5% SUBGROUP CERTIFICATE,

AND

A BIASED ACTIVE TRIGGER
IS NEVER
COUNTED AS
UNIFORM EVIDENCE?

Candidate mechanisms:

A.
explicit claim-scope tags;

B.
trigger-excluded uniform certificate counts;

C.
task-requested subgroup scale;

D.
multiscale 5% / 10% / 20% contracts;

E.
certificate downgrade to a weaker claim rather than silent overclaim;

F.
abstention when the requested scope cannot fit current audit budget.

Do not execute STAB-18-R1 during this lane.

EXECUTION PROVENANCE

evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
corrected_primary_worlds = 75000
corrected_primary_seed = 20260919139
hidden_fraction_rule = ceil
hard5_mean_net = 7.269899
hard5_mean_evidence = 8.414800
hard5_h10_false_broadcast = 0.018454
hard10_h10_false_broadcast = 0.040439
cap23_refusal_rate = 0.120533
shock_h138_h10_false_broadcast = 0.55445
shock_hard5_h10_false_broadcast = 0.01113
hidden5_under_10pct_certificate_false_broadcast = 0.200583
delta01_h10_false_broadcast = 0.009417
delta05_h10_false_broadcast = 0.048667
delta10_h10_false_broadcast = 0.090833


EXECUTION NOTE

The corrected execution uses the preregistered claim class exactly:

m = ceil(0.10 N).

The earlier exploratory run that inherited rounded minority sizing was discarded before acceptance analysis.

Primary synthetic implementation:
- 25 price/activity cells;
- 3,000 worlds per cell;
- 75,000 worlds total;
- N uniformly sampled from 40..100;
- active count = ceil(active_fraction x N), minimum one;
- primary member values are positive lognormal weights with mean approximately one;
- regime prior exactly as preregistered;
- hidden identity independent of activity and value in the primary grid;
- one active trigger is selected, then remaining audit order is uniform without replacement;
- common worlds are reused across policy comparators.

This remains:
SYNTHETIC / MEASURED_SANDBOX.

PRIMARY RESULT

Across all 75,000 primary worlds:

H138 ECONOMIC OPTIMIZER

mean net:
24.55904.

1st percentile net:
-25.26996.

mean evidence:
3.39605 audits/event.

weighted active coverage:
50.428%.

mean false-promotion rate:
1.806%.

broadcast rate:
42.556%.

certificate purchase:
3.077%.

HIDDEN-10 false-broadcast:
30.805%.

HIDDEN-20 false-broadcast:
16.624%.

HARD-FLOOR-5

mean net:
7.87350.

1st percentile net:
-41.46809.

mean evidence:
7.34124 audits/event.

weighted active coverage:
34.055%.

mean false-promotion rate:
0.115%.

broadcast rate:
21.668%.

certificate purchase:
31.136%.

epistemic abstention:
12.451%.

economic local/defer:
38.385%.

HIDDEN-10 false-broadcast:
1.966%.

HIDDEN-20 false-broadcast:
0.089%.

HARD-FLOOR-10

mean net:
9.96029.

1st percentile net:
-42.33122.

mean evidence:
6.72547 audits/event.

weighted active coverage:
36.532%.

mean false-promotion rate:
0.242%.

broadcast rate:
24.657%.

certificate purchase:
34.203%.

epistemic abstention:
9.384%.

HIDDEN-10 false-broadcast:
4.438%.

HIDDEN-20 false-broadcast:
0.310%.

HARD-FLOOR-5 / CAP-23

mean net:
3.05564.

1st percentile net:
-41.07270.

mean evidence:
6.00559 audits/event.

weighted active coverage:
28.289%.

broadcast rate:
15.633%.

certificate purchase:
22.423%.

epistemic abstention:
21.164%.

audit-cap refusal:
11.843%.

HIDDEN-10 false-broadcast:
1.399%.

HIDDEN-20 false-broadcast:
0.089%.

HARM-BOUNDED

mean net:
9.20360.

1st percentile net:
-41.48392.

mean evidence:
6.59541 audits/event.

weighted active coverage:
38.982%.

broadcast rate:
28.184%.

HIDDEN-10 false-broadcast:
9.453%.

HIDDEN-20 false-broadcast:
4.349%.

FULL-FAMILY

mean net:
-150.92793.

1st percentile net:
-728.91933.

mean evidence:
70.082 audits/event.

weighted active coverage:
100%.

PRIMARY ACCEPTANCE FINDING

The central compute-shock invariance thesis is supported.

HARD-FLOOR-5 keeps the preregistered HIDDEN-10 family-wide false-broadcast probability below the 5% claim floor in every primary evidence-price slice.

Observed HIDDEN-10 false-broadcast by evidence price:

price 0.5:
3.26%.

price 1:
2.64%.

price 2:
2.21%.

price 4:
1.07%.

price 8:
0.66%.

Increasing evidence price does not cause:
A WEAKER CLAIM STANDARD.

It causes:
LESS CERTIFICATION
+
MORE ABSTENTION / LOCALITY.

This is the desired direction.

By contrast,
H138 remains economically aggressive:

HIDDEN-10 false-broadcast by price:
29.29%,
35.81%,
33.40%,
31.95%,
23.54%.

The scalar economic controller has no invariant epistemic floor.

FLOOR-10 TRADEOFF

The looser 10% floor:
- consumes less evidence;
- preserves more active coverage;
- broadcasts more often;
- has a measurably higher HIDDEN-10 false-broadcast rate.

Thus confidence level creates a real:
EVIDENCE / COVERAGE / ERROR
tradeoff.

This passes the preregistered comparison.

CAP-23 RESULT

CAP-23 never converts insufficient audit budget into an uncertified broadcast.

It refuses the family-wide claim.

Primary cap-refusal rate:
11.843%.

Therefore:

BUDGET EXHAUSTION
CAN PRODUCE
EPISTEMIC SILENCE

without:
CONFIDENCE DEGRADATION.

CERTIFICATE SIZE

Exact 10%-minority certificate counts:

N = 40:
delta 10% -> 17 audits.
delta 5% -> 21 audits.
delta 1% -> 27 audits.

N = 70:
delta 10% -> 19 audits.
delta 5% -> 24 audits.
delta 1% -> 33 audits.

N = 100:
delta 10% -> 20 audits.
delta 5% -> 25 audits.
delta 1% -> 36 audits.

The hard floor therefore does NOT require full-family audit.

PRICE-SHOCK STRESS

Fresh evidence price begins at:
0.5

through the five-member probe,

then jumps to:
8.

ACTIVE 40%

H138 steady-low:
mean net 41.35.
HIDDEN-10 false-broadcast 40.25%.

H138 price shock:
mean net 43.52.
HIDDEN-10 false-broadcast 56.80%.

Again:
the shortcut can increase mean value
while making the claim substantially less reliable.

HARD-FLOOR-5 steady-low:
mean net 32.31.
HIDDEN-10 false-broadcast 4.73%.

HARD-FLOOR-5 price shock:
mean net 1.02.
epistemic abstention 74.30%.
HIDDEN-10 false-broadcast 0%.

ACTIVE 80%

H138 steady-low:
mean net 90.75.
HIDDEN-10 false-broadcast 31.06%.

H138 price shock:
mean net 97.30.
HIDDEN-10 false-broadcast 53.53%.

HARD-FLOOR-5 steady-low:
mean net 76.79.
HIDDEN-10 false-broadcast 4.16%.

HARD-FLOOR-5 price shock:
mean net 6.49.
certificate purchase 40.24%.
epistemic abstention 32.50%.
HIDDEN-10 false-broadcast 2.34%.

COMPUTE-SHOCK CONCLUSION

The hard floor converts:
COMPUTE SHOCK

into:
ABSTENTION / REDUCED COVERAGE / LOWER REWARD,

not:
WEAKER EVIDENCE FOR THE SAME CLAIM.

This is the strongest positive H139 result.

HIGH-VALUE HIDDEN-MINORITY STRESS

A separate stress forces one hidden-minority active member to carry very high value.

20,000 paired worlds.
active fraction:
20%.

evidence price:
2.

H138

mean net:
-16.6421.

1st percentile:
-53.1241.

HIDDEN-10 false-broadcast:
54.54%.

HARD-FLOOR-5

mean net:
-8.8517.

1st percentile:
-71.9570.

HIDDEN-10 false-broadcast:
4.32%.

HARD-FLOOR-10

mean net:
-9.9510.

1st percentile:
-67.9533.

HIDDEN-10 false-broadcast:
8.81%.

CRITICAL FAILURE

The preregistered statement:

HARD FLOORS IMPROVE SEVERE DOWNSIDE
UNDER HIGH-VALUE HIDDEN-MINORITY STRESS

does NOT pass for the fixed 5% floor
when severe downside is measured by the preregistered net-value tail.

The 5% floor dramatically reduces false broadcasts,
and improves mean net relative to H138,

but:
its remaining rare misses
plus:
its evidence expenditure

produce a worse 1st-percentile net.

Therefore H139 is NOT a clean positive result.

EXPLORATORY STRICTER-FLOOR CHECK

This is post-primary exploratory analysis.
It does not alter H139 acceptance.

Using the same high-value hidden-minority ecology:

delta 1%:

mean net:
-6.5148.

1st percentile:
-44.7003.

false-broadcast:
0.64%.

This improves the 1st-percentile tail relative to H138.

A still stricter exploratory sweep:

delta 0.1%:

mean net:
approximately -4.42.

1st percentile:
approximately -31.99.

false-broadcast:
approximately 0.02%.

epistemic abstention:
approximately 42.1%.

Interpretation:

THE APPROPRIATE CONFIDENCE CLASS
DEPENDS ON
THE LOSS SEVERITY
OF A RARE MISS.

But:

EVIDENCE PRICE
MUST NOT
BE ALLOWED
TO LOOSEN THAT CLASS.

Cost may force:
ABSTENTION.

Harm may justify:
A STRICTER FLOOR.

CLAIM-SCOPE STRESS

The H139 certificate explicitly claims protection against:

AN UNMARKED MINORITY
OF AT LEAST 10%.

It does NOT certify arbitrary smaller minorities.

Exact analytic raw miss probability for the H139 5% certificate,
averaged over N = 40..100:

actual hidden fraction 5%:
20.34%.

range:
15.88% to 23.61%.

actual hidden fraction 10%:
4.60%.

range:
4.09% to 5.00%.

actual hidden fraction 20%:
0.17%.

range:
0.10% to 0.29%.

Monte Carlo stress at:
active fraction 40%,
evidence price 1:

HARD-FLOOR-5 false-broadcast:

actual hidden 5%:
20.79%.

actual hidden 10%:
4.65%.

actual hidden 20%:
0.15%.

This is not a failure of the hypergeometric certificate.

It is a failure of:
UNSCOPED INTERPRETATION.

A certificate for:
10%-OR-LARGER MINORITIES

must never be silently read as:
ARBITRARY-MINORITY SAFETY.

NEW LIMIT — EVIDENCE PROVENANCE / EXCHANGEABILITY

H139 also exposes a subtler statistical issue.

The exact certificate assumes:
UNIFORM WITHOUT-REPLACEMENT EVIDENCE.

But the first member can be:
AN ACTION-TRIGGERED OBSERVATION.

If trigger selection is correlated with hidden membership,
then it is not automatically exchangeable with a random canary.

Analytic stress:

For N = 40..100,
the designed 10%-minority / 5%-miss certificate has raw miss:

mean:
4.604%.

range:
4.088% to 4.999%.

If one counted certificate observation is instead known to be a majority-biased trigger,
and only the remaining k-1 observations are uniform:

effective raw miss becomes:

mean:
5.156%.

range:
4.633% to 5.672%.

Relative miss inflation:
approximately 11.1% to 13.9%.

Thus:

EVIDENCE COUNT
ALONE
IS NOT ENOUGH.

The organism must preserve:
HOW EVIDENCE WAS SELECTED.

A non-exchangeable trigger should not be credited as random certificate evidence
unless its selection mechanism is modeled.

OUT-OF-BOX INTERPRETATION

A useful way to treat this is:

EPISTEMIC EVIDENCE
SHOULD HAVE A TYPE.

A family-wide certificate is not just:

confidence = 95%.

It should carry at least:

- claim scope;
- minimum hidden-fraction class;
- allowed miss probability;
- population/family identity;
- evidence epoch;
- selection mechanism;
- exchangeability / calibration status;
- severity class;
- evidence count or equivalent effective sample information.

Then:

A CLAIM
CAN CONSUME
ONLY EVIDENCE
WHOSE TYPE
MATCHES
THE CLAIM.

This prevents:

CONFIDENCE LAUNDERING.

Examples of confidence laundering:

- using a 10%-minority certificate to claim 5%-minority safety;
- counting a biased trigger as a uniform canary;
- reusing stale evidence after context shift;
- weakening delta because compute price increased;
- treating low-harm and catastrophic-harm claims as the same confidence class.

DECISION

AR-H139 is:

MIXED-POSITIVE.

SUPPORTED

- a non-negotiable epistemic floor prevents the H138 compute-price shortcut;
- compute shock can be converted into abstention instead of weaker evidence;
- the 5% floor controls its explicitly scoped 10%-minority claim in the primary ecology;
- the 10% floor produces the expected evidence / coverage / miss tradeoff;
- CAP-23 refuses claims instead of silently degrading confidence;
- hard-floor evidence is far below full-family evidence;
- the expected-value optimizer retains materially higher mean reward in many cells, confirming a real reward/safety tradeoff.

NOT SUPPORTED

- a universal fixed 5% floor as sufficient protection for every harm class;
- the preregistered severe-net-tail improvement under the high-value hidden-minority stress.

NEWLY ESTABLISHED LIMITS

1. CLAIM SCOPE

A 10%-minority certificate does not protect arbitrary smaller hidden groups.

2. EVIDENCE PROVENANCE

A sample's selection mechanism matters.
Non-exchangeable trigger evidence cannot be counted as if it were random.

3. LOSS CLASS

A fixed miss probability can still be too weak when rare misses are extremely costly.

4. VALUE / VALIDITY SEPARATION

Economic value may choose:
whether to act
or:
whether to buy admissible evidence.

It must not choose:
what an already-declared confidence class means.

NEXT HIGH-VALUE MOVE

AR-H140 — TYPED EPISTEMIC CERTIFICATE / CLAIM-SCOPE + EXCHANGEABILITY FIREWALL AUDIT

Core question:

CAN
THE ORGANISM
MAKE FAMILY-WIDE KNOWLEDGE
TYPE-SAFE?

Test a certificate object whose validity is conditional on:

CLAIM SCOPE
+
SELECTION PROVENANCE
+
RISK CLASS
+
EVIDENCE EPOCH.

Candidate architecture:

CERTIFICATE = {
family,
epoch,
minimum_hidden_fraction,
delta,
selection_basis,
exchangeability_status,
risk_class,
effective_evidence
}.

A claim may broadcast only if:
the certificate type subsumes the claim type.

High-harm claims:
may tighten delta.

Compute scarcity:
may cause abstention.

Neither:
may silently mutate the meaning of an existing certificate.

Primary H140 attacks:

- 5% vs 10% hidden subgroup scope mismatch;
- majority-biased action triggers;
- minority-biased triggers;
- stale certificate reuse after context change;
- high-value hidden minority;
- sudden evidence-price shock;
- calibrated predictive strata as possible cheaper equivalent evidence.

The central desired property is:

INVALID EVIDENCE
SHOULD FAIL
LIKE A TYPE ERROR,

NOT:
LIKE A SMALLER CONFIDENCE NUMBER.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_worlds_per_cell = 3000
primary_cells = 25
primary_total_worlds = 75000
corrected_hidden_count_rule = ceil(0.10N)
hard5_primary_h10_false_broadcast = 0.01966
hard10_primary_h10_false_broadcast = 0.04438
h138_primary_h10_false_broadcast = 0.30805
hard5_mean_evidence = 7.34124
full_family_mean_evidence = 70.082
cap23_refusal_rate = 0.11843
shock_active40_h138_h10_false = 0.5680
shock_active40_hard5_h10_false = 0
shock_active80_h138_h10_false = 0.5353
shock_active80_hard5_h10_false = 0.0234
high_value_h138_p01 = -53.1241
high_value_hard5_p01 = -71.9570
high_value_hard1_p01 = -44.7003
scope5_analytic_mean_miss = 0.20337
scope10_analytic_mean_miss = 0.04605
nonexchangeable_trigger_mean_miss = 0.05156
