TITLE: DG-1A-AR-H140 — Claim-Scope Contract / Trigger-Bias-Corrected Multiscale Certificate Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh139-epistemic-risk-floor-audit.ice
PARENT_RESULT_COMMIT: 73e2d1d7ef2eab8f58cd144b2fb85ca7424a8de1

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
