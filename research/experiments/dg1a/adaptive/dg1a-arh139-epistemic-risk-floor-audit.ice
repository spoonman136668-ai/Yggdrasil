TITLE: DG-1A-AR-H139 — Non-Negotiable Epistemic Risk Floor / Compute-Shock Invariance Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX MIXED-POSITIVE RISK-FLOOR RESULT + CLAIM-SCOPE LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh138-evidence-price-abstention-phase-audit.ice
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


SECONDARY ROBUSTNESS EXTENSION

This section is an additional post-primary replication and boundary search.

It does not replace:
the corrected primary run above.

It deliberately changes the high-value stress operating point to test whether the fixed 5% floor remains sufficient when:
- current activity is sparser;
- evidence is more expensive;
- one active hidden-minority member carries very high value.

Stress:
20,000 paired exact-HIDDEN-10 worlds.

active fraction:
20%.

evidence price:
2.

H138 ECONOMIC OPTIMIZER

mean net:
-16.6421.

1st percentile:
-53.1241.

false-broadcast:
54.54%.

HARD-FLOOR-5

mean net:
-8.8517.

1st percentile:
-71.9570.

false-broadcast:
4.32%.

HARD-FLOOR-10

mean net:
-9.9510.

1st percentile:
-67.9533.

false-broadcast:
8.81%.

This extension finds a boundary not visible in the primary high-value stress:

A FIXED 5% CLAIM FLOOR
CAN GREATLY REDUCE
FALSE BROADCAST

while still failing to improve
THE EXTREME NET-VALUE TAIL

when:
evidence is expensive
and:
the residual miss event is sufficiently costly.

POST-PRIMARY STRICTER-FLOOR PROBE

Same sparse/high-price high-value stress.

delta 1%:

mean net:
-6.5148.

1st percentile:
-44.7003.

false-broadcast:
0.64%.

A still stricter exploratory delta 0.1% sweep produced:

mean net:
approximately -4.42.

1st percentile:
approximately -31.99.

false-broadcast:
approximately 0.02%.

epistemic abstention:
approximately 42.1%.

Interpretation:

RISK CLASS
SHOULD BE
A PROPERTY OF
THE CLAIM / LOSS CLASS,

not:
a price-selected knob.

Higher predicted miss severity may:
TIGHTEN
the required delta.

Higher evidence price may:
increase abstention.

It must not:
LOOSEN
the declared risk class.

ANALYTIC EXCHANGEABILITY CROSS-CHECK

For N = 40..100,
using the exact 10%-minority / 5%-miss certificate:

designed raw miss probability:

mean:
4.604%.

range:
4.088% to 4.999%.

If one counted observation is a majority-biased trigger,
and only the remaining k-1 observations are uniform without replacement:

effective raw miss:

mean:
5.156%.

range:
4.633% to 5.672%.

Relative miss inflation:
approximately 11.1% to 13.9%.

This analytically confirms the primary trigger-selection stress:

SELECTION PROVENANCE
IS PART OF
THE CERTIFICATE TYPE.

A non-exchangeable trigger should either:
- be excluded from the uniform certificate count;
- receive an explicitly modeled sampling weight;
- or force a different certificate class.

EXTENDED H140 REQUIREMENT

The already nominated H140 claim-scope contract should therefore carry:

- family identity;
- evidence epoch;
- detectable subgroup scale;
- tolerated miss probability;
- selection basis;
- exchangeability status;
- effective evidence;
- loss / severity class.

The core invariant becomes:

INVALID OR MISMATCHED EVIDENCE
FAILS LIKE
A TYPE ERROR.

Compute scarcity may reduce:
coverage.

It may not silently mutate:
scope,
sampling assumptions,
or
risk class.

SECONDARY PROVENANCE

secondary_high_value_worlds = 20000
secondary_active_fraction = 0.20
secondary_evidence_price = 2
secondary_h138_p01 = -53.1241
secondary_hard5_p01 = -71.9570
secondary_hard1_p01 = -44.7003
secondary_hard5_false_broadcast = 0.0432
secondary_hard1_false_broadcast = 0.0064
analytic_nonexchangeable_trigger_mean_miss = 0.05156
