TITLE: DG-1A-AR-H140 — Claim-Scope Contract / Trigger-Bias-Corrected Multiscale Certificate Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX MIXED-POSITIVE TYPED-CONFIDENCE RESULT + RESOURCE-BLINDNESS LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh139-epistemic-risk-floor-audit.ice
PARENT_RESULT_COMMIT: 73e2d1d7ef2eab8f58cd144b2fb85ca7424a8de1
PREREGISTRATION_COMMIT: 22ae1e90ac6b38ad69f3cc1616233fd5944e2e99

PURPOSE

H139 established two boundaries:

1.
epistemic admissibility can remain invariant to compute price;

2.
the certificate is valid only for the failure class it actually certifies.

H139 also found a smaller exchangeability issue:

an active trigger may be statistically biased with respect to hidden-minority membership.

If that trigger is counted as though it were a uniform family sample,
the nominal hypergeometric floor can be slightly miscalibrated.

H140 asks:

CAN
THE ORGANISM
REPRESENT CONFIDENCE
AS A TYPED CLAIM CONTRACT

SO THAT:

- subgroup scale is explicit;
- miss probability is explicit;
- sampling assumptions are explicit;
- a biased trigger is never silently counted as uniform evidence;
- insufficient budget causes abstention or a weaker explicit claim,
  not semantic overclaim?

BOUNDARY

Synthetic research only.

It does not:
- implement living or biological tissue;
- establish production confidence thresholds;
- authorize deployment;
- execute or modify STAB-18-R1;
- spend canonical scientific execution.

EVIDENCE CLASS TARGET

SYNTHETIC
MEASURED_SANDBOX

PRIMARY CLAIM CONTRACT

A claim has the form:

SAFE_AGAINST_UNMARKED_MINORITY(
    minimum_fraction = f_required,
    miss_probability <= delta
)

Primary delta:

0.05.

Task-required minimum hidden fraction:

5%,
10%,
20%.

A certificate for 5% is stronger than:
10% or 20%.

A certificate for 10% is stronger than:
20%.

A certificate for 10% is NOT valid for:
5%.

A weaker certificate may be returned only if:
its weaker scope is explicitly represented.

It may not be relabeled:
CERTIFIED
without its scope.

PRIMARY ECOLOGY

Family size:

uniform integer 40..100.

Active fractions:

10%,
40%,
80%.

Evidence prices:

0.5,
2,
8.

Primary hidden regimes:

CLEAN:
40%.

HIDDEN-5:
20%.

HIDDEN-10:
25%.

HIDDEN-20:
15%.

Minority size:

ceil(f_hidden * N).

Task-required claim scope:

5%:
one third.

10%:
one third.

20%:
one third.

Task scope is independent of:
hidden regime,
member value,
and active status.

Primary active/minority relation:

independent.

Primary worlds per:
active fraction x evidence price cell:

2,000.

Primary cells:

9.

Primary total worlds:

18,000.

ROBUSTNESS WORLDS

Additional fixed-regime stress worlds:

at least 10,000 per major trigger-bias or claim-scope stress.

GENERATOR FROZEN FOR REPRODUCIBILITY

Primary deterministic seed:

20260919140.

Member values:

lognormal.

Underlying normal sigma:

0.60.

Underlying normal mean:

-0.5 * sigma^2.

Therefore:

expected member value is approximately 1.

Active count:

max(
1,
round(active_fraction * N)
).

Minority membership:

uniform without replacement
unless a named correlation stress overrides it.

Trigger:

uniform among ACTIVE members.

Non-trigger audit order:

uniform without replacement.

AUDIT ACCOUNTING

The active trigger is always audited first.

If the trigger contradicts the stored family model:

do not broadcast the stored family model.

Resolve the trigger locally.

For policies that count the trigger toward a certificate:

the trigger occupies one sample slot.

For trigger-corrected policies:

the active trigger is informational
but is NOT counted toward the uniform random certificate.

The certificate then uses:
fresh uniformly selected NON-TRIGGER members.

ECONOMICS

Use H139/H138 scoring.

Active correct resolution:

+3 x value.

Active false promotion:

-5 x value.

Inactive false promotion:

-0.5 x value.

Unresolved active carry:

-0.15 x value.

Family broadcast application:

-0.20 x N.

Audited inactive:

no immediate resolution reward.

Evidence:

-price per audited member.

POLICIES

A — GENERIC-10

Use a 10%-minority / 5%-miss certificate.

Count the active trigger as one sample.

If the certificate passes:

broadcast.

Expose only a generic CERTIFIED flag.

This intentionally represents the semantic-overclaim baseline.

If task scope is 5%:

GENERIC-10 still treats its generic flag as sufficient.

B — TYPED-10

Use the same 10% / 5% certificate.

The stored claim explicitly says:

minimum_fraction = 10%.

If task scope requires 5%:

the 10% certificate is insufficient.

Do not relabel it.

The policy may:

ABSTAIN
for the requested 5% claim.

If task requires:
10% or 20%,

the typed-10 certificate can satisfy the request.

C — SCOPE-MATCHED / TRIGGER-COUNTED

Choose certificate fraction:

f_cert = f_required.

Use exact hypergeometric 5%-miss count.

Count the active trigger as one uniform sample.

This tests:
scope typing without trigger correction.

D — SCOPE-MATCHED / TRIGGER-EXCLUDED

Choose:

f_cert = f_required.

The active trigger does not count toward the uniform certificate.

If trigger is compatible:

sample fresh non-trigger members until:

C((N-1)-m, k_random)
/
C(N-1, k_random)
<= 0.05,

where:

m = ceil(f_required * N).

Total audited members:

1 trigger
+
k_random uniform non-trigger audits.

If any dissent appears:

cancel broadcast.

E — SCOPE-MATCHED / BUDGET-CAPPED

Same as D.

Fresh total audit cap:

24 members including trigger.

If the requested claim cannot fit:

ABSTAIN.

Do not:
substitute a weaker scope.

Do not:
increase tolerated miss probability.

F — EXPLICIT DOWNGRADE

Same 24-audit cap.

Try the requested scope first.

If it cannot fit:

search weaker valid claim scopes in order:

5% -> 10% -> 20%.

A weaker claim may be returned only with:
its actual minimum_fraction.

A weaker returned claim does NOT authorize a task
whose requested scope is stronger.

This policy measures whether:
explicit semantic downgrade
preserves useful information
without overclaim.

G — FULL-FAMILY

Audit all members.

No false family promotion.

Reference upper-bound evidence policy.

PRIMARY METRICS

1.
mean net value.

2.
mean evidence audits/event.

3.
1st percentile net.

4.
active weighted coverage.

5.
family broadcast rate.

6.
epistemic abstention rate.

7.
semantic downgrade rate.

8.
SEMANTIC OVERCLAIM RATE:

fraction of broadcasts presented as satisfying a requested claim
when the evidence certificate is weaker than the requested scope.

9.
CLAIM-VALID FALSE-BROADCAST RATE:

for worlds whose actual hidden fraction is at least the requested minimum fraction,
probability the policy broadcasts without detecting the hidden minority.

10.
per-request-scope false-broadcast rate.

11.
per-actual-hidden-scale false-broadcast rate.

12.
trigger-bias calibration error.

13.
audit-cap refusal rate.

PRIMARY ACCEPTANCE SHAPE

The typed-contract thesis is supported if:

- GENERIC-10 materially overclaims 5%-scope tasks;
- TYPED-10 has zero semantic overclaim by refusing 5%-scope satisfaction;
- SCOPE-MATCHED policies eliminate the H139 hidden-5 scope mismatch;
- TRIGGER-EXCLUDED remains approximately <=5% false-broadcast under matching hidden-scale stresses even when active-trigger selection is biased;
- TRIGGER-COUNTED shows measurable calibration drift under at least one biased-trigger stress;
- budget-capped scope matching refuses unaffordable claims rather than weakening them;
- EXPLICIT DOWNGRADE can preserve a weaker useful claim while reporting zero semantic overclaim;
- all typed policies use materially less mean evidence than FULL-FAMILY in at least some operating regions;
- evidence price changes claim frequency or abstention, not the meaning of a successful certificate.

FAILURE CONDITIONS

Treat H140 as mixed/negative if:

- typed metadata fails to prevent semantic overclaim;
- trigger exclusion does not correct biased-trigger calibration;
- scope matching still mislabels 10%-scale evidence as 5%-scale evidence;
- explicit downgrade authorizes tasks outside the downgraded scope;
- capped policies silently relax delta;
- correct scope matching effectively becomes full-family audit across nearly all N;
- resource price changes certificate semantics.

TRIGGER-BIAS ROBUSTNESS

Exact HIDDEN-10 worlds.

Active fraction:

80%.

Evidence price:

0.5.

Compare:

independent activation;

active concentrated inside minority;

active concentrated outside minority.

The outside-minority case is the key challenge.

For trigger-counted sampling:

the active trigger is not exchangeable
with a uniform family draw.

For trigger-excluded sampling:

only the fresh non-trigger uniform draw
contributes to the statistical certificate.

SCOPE ROBUSTNESS

Exact hidden fractions:

5%,
10%,
20%.

Required scopes:

5%,
10%,
20%.

Measure the full:

actual hidden scale
x
required claim scale

matrix.

A broadcast is a claim-valid false broadcast only when:

actual hidden fraction >= required minimum fraction

AND:

the hidden minority is missed.

This distinction prevents:

a 20%-scope claim

from being incorrectly judged against:

a 5% hidden minority

that is outside the claim's declared scope.

PRICE-SHOCK ROBUSTNESS

Initial trigger/probe evidence price:

0.5.

After the first five total observations:

incremental price becomes:

8.

The typed certificate's:
fraction target
and
delta

must remain unchanged.

Only:

purchase / abstention / explicit weaker-scope response

may change.

INTERPRETATION GUARDRAIL

H140 does not claim:

5%
is the universally correct subgroup scale.

It tests:

whether epistemic guarantees remain semantically typed.

The architectural principle under test is:

CONFIDENCE
IS NOT
ONE NUMBER.

It is a contract over:

WHAT FAILURE
AT WHAT SCALE
UNDER WHAT SAMPLING ASSUMPTIONS
WITH WHAT MISS BOUND
WAS ACTUALLY TESTED.

FROZEN BEFORE EXECUTION

The generator,
seed,
primary ecology,
claim semantics,
policies,
economic scale,
audit cap,
metrics,
acceptance shape,
and robustness dimensions above
are fixed before execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = 73e2d1d7ef2eab8f58cd144b2fb85ca7424a8de1
primary_seed = 20260919140
primary_worlds = 18000
primary_delta = 0.05
primary_audit_cap = 24


EXECUTION RESULT

PRIMARY RUN

The preregistered deterministic generator was used unchanged.

Seed:

20260919140.

Primary worlds:

18,000.

Primary cells:

9.

Policies:

GENERIC-10,
TYPED-10,
SCOPE-MATCHED / TRIGGER-COUNTED,
SCOPE-MATCHED / TRIGGER-EXCLUDED,
CAP-24,
EXPLICIT DOWNGRADE,
FULL-FAMILY.

PRIMARY AGGREGATE

GENERIC-10

mean net:
-25.84958.

1st percentile:
-188.12199.

mean evidence:
20.80611.

active weighted coverage:
62.997%.

broadcast:
44.872%.

semantic overclaim among broadcasts:
32.784%.

claim-valid false-broadcast:
5.246%.

TYPED-10

mean net:
-19.32636.

mean evidence:
14.25644.

coverage:
44.613%.

broadcast:
30.161%.

semantic overclaim:
0%.

claim-valid false-broadcast:
1.127%.

epistemic abstention:
30.717%.

SCOPE-MATCHED / TRIGGER-COUNTED

mean net:
-27.48149.

mean evidence:
21.99706.

coverage:
65.824%.

broadcast:
47.189%.

semantic overclaim:
0%.

claim-valid false-broadcast:
2.630%.

SCOPE-MATCHED / TRIGGER-EXCLUDED

mean net:
-29.34790.

mean evidence:
22.58544.

coverage:
65.862%.

broadcast:
46.594%.

semantic overclaim:
0%.

claim-valid false-broadcast:
2.312%.

CAP-24

mean net:
-9.37079.

mean evidence:
10.10022.

coverage:
40.992%.

broadcast:
29.944%.

semantic overclaim:
0%.

claim-valid false-broadcast:
1.301%.

epistemic abstention:
36.967%.

audit-cap refusal:
36.967%.

EXPLICIT DOWNGRADE

mean net:
-23.74937.

mean evidence:
16.92150.

coverage:
50.592%.

broadcast:
29.944%.

semantic overclaim:
0%.

claim-valid false-broadcast:
1.301%.

explicit downgrade:
36.967%.

weaker or requested claim returned:
48.956%.

FULL-FAMILY

mean net:
-154.59792.

mean evidence:
70.05994.

coverage:
100%.

false family promotion:
0%.

PRIMARY SEMANTIC RESULT

The typed-confidence thesis passes.

GENERIC-10 produces substantial semantic overclaim because it exposes:

CERTIFIED

without preserving:

WHAT WAS CERTIFIED.

Approximately one third of its successful broadcasts are presented as satisfying a stronger task claim than its actual 10%-minority certificate supports.

Observed semantic overclaim:

32.784%.

Every typed policy records:

0%.

Therefore:

A CERTIFICATE
MUST CARRY
ITS CLAIM DOMAIN.

A scalar or generic confidence flag is insufficient.

HIDDEN-5 / REQUIRED-5 STRESS INSIDE PRIMARY MATRIX

This is the direct H139 scope-mismatch test.

GENERIC-10

false-broadcast:
18.27%.

Every such broadcast is semantically overclaimed.

SCOPE-MATCHED / TRIGGER-COUNTED

false-broadcast:
4.49%.

SCOPE-MATCHED / TRIGGER-EXCLUDED

false-broadcast:
4.40%.

CAP-24

broadcast:
0%.

The 5%-scope certificate exceeds the cap in these cases,
so the policy refuses the claim.

EXPLICIT DOWNGRADE

task-authorizing broadcast:
0%.

It may return a weaker explicit claim,
but that weaker claim does not authorize the 5%-scope task.

Thus:

SCOPE MATCHING
REMOVES
THE H139
10%-CERTIFICATE / 5%-MINORITY
SEMANTIC FAILURE.

REQUEST / ACTUAL SCALE MATRIX

Representative matching or stronger challenges:

ACTUAL 10% / REQUIRED 10%

GENERIC-10:
4.89%.

SCOPE-COUNTED:
4.89%.

SCOPE-EXCLUDED:
4.29%.

ACTUAL 20% / REQUIRED 20%

SCOPE-COUNTED:
5.65%.

SCOPE-EXCLUDED:
4.49%.

The trigger-excluded policy remains inside the intended floor
in these sampled cells.

The trigger-counted 20% cell is slightly above 5%,
consistent with finite-sample noise plus trigger exchangeability effects.

TRIGGER-BIAS ROBUSTNESS

Exact HIDDEN-10.

Required scope:
10%.

Active fraction:
80%.

Evidence price:
0.5.

20,000 worlds per policy/correlation condition.

INDEPENDENT ACTIVATION

TRIGGER-COUNTED false-broadcast:
4.625%.

TRIGGER-EXCLUDED:
4.025%.

ACTIVE CONCENTRATED INSIDE MINORITY

TRIGGER-COUNTED:
4.565%.

TRIGGER-EXCLUDED:
4.025%.

ACTIVE CONCENTRATED OUTSIDE MINORITY

TRIGGER-COUNTED:
5.340%.

TRIGGER-EXCLUDED:
4.500%.

The preregistered trigger-bias hypothesis is supported.

When active selection makes the trigger preferentially majority-compatible:

COUNTING THAT TRIGGER
AS THOUGH IT WERE
A UNIFORM FAMILY DRAW

slightly weakens the nominal floor.

Excluding it from the uniform certificate restores calibration.

The cost is small.

Outside-minority stress mean evidence:

TRIGGER-COUNTED:
22.3159.

TRIGGER-EXCLUDED:
22.9758.

Approximately:

0.66 additional audit/event

buys:

correct sampling semantics.

CAP-24 RESULT

The cap behaves as intended.

When the requested scope cannot fit:

the policy refuses the claim.

Observed primary cap refusal:

36.967%.

Semantic overclaim:

0%.

This strongly supports:

RESOURCE LIMIT
MAY REMOVE
A CLAIM.

It must not:

CHANGE
WHAT THE CLAIM MEANS.

EXPLICIT DOWNGRADE RESULT

The downgrade policy preserves information without authorizing the wrong task.

Observed explicit downgrade:

36.967%.

Semantic overclaim:

0%.

It can return:

for example,

SAFE_AGAINST_MINORITY >= 10%

when:

SAFE_AGAINST_MINORITY >= 5%

was requested but unaffordable.

The returned weaker contract can remain useful for:

other decisions

while being explicitly insufficient for:

the stronger current task.

This is preferable to:

one undifferentiated
confidence score.

EVIDENCE EFFICIENCY

SCOPE-EXCLUDED mean evidence:

22.59.

FULL-FAMILY:

70.06.

Thus exact scope matching remains materially below full-family inspection.

For weaker requested scopes:

20% certificates are especially cheap.

For stronger 5% scope:

certificate sizes become much larger.

This is not an implementation defect.

It is the information cost of the stronger claim.

RESOURCE-PRICE LIMIT

H140 reveals a new problem.

The typed policies preserve certificate semantics across evidence prices,
but the preregistered policy set does not include an economic purchase gate.

As a result:

SCOPE-EXCLUDED broadcast rate is nearly price-invariant.

Price 0.5:

46.05%.

Price 2:

46.40%.

Price 8:

47.33%.

Mean evidence is also nearly invariant:

22.81,
22.44,
22.51.

But mean net collapses:

price 0.5:
37.7676.

price 2:
4.3169.

price 8:
-130.1282.

CAP-24 shows the same qualitative limitation.

Its cap changes behavior by certificate size,
not by evidence price.

Therefore H140 does NOT satisfy the preregistered resource-adaptation criterion.

This is a genuine negative result.

TYPED EPISTEMICS
SOLVE
SEMANTIC SAFETY.

They do not,
by themselves,
solve:

RESOURCE ALLOCATION.

PRICE-SHOCK ROBUSTNESS

Initial first-five evidence price:

0.5.

Incremental evidence price after five observations:

8.

12,000 high-activity worlds.

GENERIC-10

mean net:
-41.2363.

evidence:
20.8305.

broadcast:
44.367%.

semantic overclaim:
33.884%.

claim-valid false-broadcast:
5.642%.

SCOPE-EXCLUDED

mean net:
-51.8007.

evidence:
22.6694.

broadcast:
45.542%.

semantic overclaim:
0%.

claim-valid false-broadcast:
2.057%.

CAP-24

mean net:
-7.2556.

evidence:
10.0834.

broadcast:
29.258%.

epistemic abstention:
37.125%.

claim-valid false-broadcast:
1.060%.

EXPLICIT DOWNGRADE

mean net:
-33.7660.

evidence:
16.9382.

broadcast:
29.258%.

explicit downgrade:
37.125%.

semantic overclaim:
0%.

The typed policies keep meaning stable through the shock.

But uncapped typed policies continue purchasing evidence
even when the resulting economics become strongly negative.

PRIMARY DECISION

AR-H140 is:

MIXED-POSITIVE.

POSITIVE FOR:

TYPED,
SCOPE-EXPLICIT
EPISTEMIC CONTRACTS

AND:

TRIGGER-BIAS-CORRECTED
CERTIFICATE ACCOUNTING.

SUPPORTED

- a generic CERTIFIED bit causes semantic overclaim;
- claim scope removes the H139 hidden-5 mismatch;
- a 10% certificate remains explicitly different from a 5% certificate;
- stronger certificates can satisfy weaker requested scopes;
- weaker certificates cannot satisfy stronger requested scopes;
- biased active triggers should not be counted as exchangeable uniform evidence;
- trigger exclusion restores the nominal miss floor under the tested bias;
- hard audit caps can refuse claims without changing their semantics;
- explicit downgrade preserves weaker information with zero task overclaim;
- typed scope matching remains much cheaper than full-family inspection on average.

NEGATIVE / LIMIT

- semantic typing alone does not make evidence spending resource-rational;
- the current scope-matched controller continues buying costly certificates under evidence-price shock;
- price changes net value but not claim frequency;
- a separate economic admission layer is still required.

GENERAL PRINCIPLE

YGGDRASIL SHOULD REPRESENT:

EPISTEMIC ADMISSIBILITY

AND:

RESOURCE ADMISSION

AS TWO DIFFERENT GATES.

Gate 1:

WHAT CLAIM
WOULD THIS EVIDENCE
LEGITIMATELY SUPPORT?

Gate 2:

IS THAT CLAIM
WORTH BUYING
RIGHT NOW?

The second gate may answer:

NO.

It may not answer:

BUY LESS EVIDENCE
AND PRETEND
THE SAME CLAIM
WAS CERTIFIED.

NEXT HIGH-VALUE MOVE

AR-H141 — DUAL-GATE CLAIM PURCHASE / RESOURCE-RATIONAL TYPED EPISTEMICS AUDIT

Question:

CAN
A TWO-GATE CONTROLLER

FIRST:

FIX
THE REQUIRED
EPISTEMIC CONTRACT

THEN:

DECIDE
WHETHER
TO BUY IT

WITHOUT:

EVER
TRADING DOWN
THE CLAIM
SILENTLY?

Compare:

A.
resource-blind scope-matched certificate;

B.
economic expected-value gate before certificate purchase;

C.
economic gate + hard epistemic contract;

D.
budget cap + hard contract;

E.
explicit weaker-scope offer that cannot authorize the stronger task;

F.
price shock after partial evidence;

G.
multi-family competition for one shared audit budget.

Desired:

RESOURCE PRICE
CHANGES
WHICH CLAIMS
GET PURCHASED,

NOT:

WHAT A PURCHASED CLAIM
MEANS.

Do not execute STAB-18-R1 during this lane.

EXECUTION PROVENANCE

evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_seed = 20260919140
primary_worlds = 18000
generic10_semantic_overclaim = 0.32784
generic10_claim_valid_false = 0.05246
scope_counted_claim_valid_false = 0.02630
scope_excluded_claim_valid_false = 0.02312
cap24_claim_valid_false = 0.01301
cap24_refusal = 0.36967
downgrade_rate = 0.36967
trigger_outside_counted_false = 0.05340
trigger_outside_excluded_false = 0.04500
scope_excluded_mean_evidence = 22.58544
full_mean_evidence = 70.05994
