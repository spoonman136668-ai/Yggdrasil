TITLE: DG-1A-AR-H140 — Typed Epistemic Certificate / Claim-Scope + Exchangeability Firewall Audit
DATE: 2026-09-19
STATUS: ANALYTIC + SYNTHETIC / MEASURED_SANDBOX POSITIVE TYPE-SAFETY RESULT + ACTION-OBLIGATION LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh139-epistemic-risk-floor-audit.ice
PREREGISTRATION_COMMIT: f71dd8beb75b69121bbca98b5e897a6c6194a50b

PURPOSE

H139 established that a non-negotiable risk floor prevents compute-price shocks from silently weakening a family-wide claim.

H139 also exposed three distinct ways a numerically valid confidence value can be misused:

1. CLAIM-SCOPE MISMATCH
A certificate against an unmarked minority of at least 10% does not certify an arbitrary 5% minority.

2. SELECTION-PROVENANCE MISMATCH
An action-triggered observation is not automatically exchangeable with a uniform random canary.

3. LOSS-CLASS MISMATCH
A fixed 5% miss floor can be too weak when a residual miss has unusually severe consequence.

H140 asks a different question:

CAN
EPISTEMIC VALIDITY
BE MADE
TYPE-SAFE?

Instead of storing:

confidence = 95%

store a contract describing:
WHAT was certified,
HOW evidence was selected,
WHEN it was valid,
and
WHAT loss class the claim belongs to.

BOUNDARY

Analytic + synthetic research only.

It does not:
- implement living or biological tissue;
- establish production confidence levels;
- establish production harm classes;
- execute or modify STAB-18-R1;
- spend canonical scientific execution;
- authorize runtime activation.

EVIDENCE CLASS TARGET

ANALYTIC
SYNTHETIC
MEASURED_SANDBOX

CORE OBJECT

CERTIFICATE TYPE

C = {
    family_id,
    evidence_epoch,
    min_hidden_fraction,
    max_miss_probability,
    selection_basis,
    exchangeability_status,
    risk_class,
    effective_evidence
}

CLAIM TYPE

Q = {
    family_id,
    required_epoch,
    required_min_hidden_fraction,
    required_max_miss_probability,
    risk_class
}

SUBSUMPTION RULE

A certificate may authorize a family-wide claim only if:

1. family_id matches;
2. evidence_epoch satisfies the required epoch;
3. certificate min_hidden_fraction <= requested min_hidden_fraction;
4. certificate max_miss_probability <= requested max_miss_probability;
5. counted evidence satisfies the declared selection model;
6. certificate risk_class is at least as strict as the requested claim class.

A certificate that does not subsume the claim is:

TYPE-INCOMPATIBLE.

It may:
- authorize a weaker/narrower claim if that claim is explicitly represented;
- trigger more evidence purchase;
- or produce abstention.

It may not:
silently authorize the stronger claim.

RISK CLASSES

These are synthetic working classes, not production recommendations.

LOW:
delta = 0.10.

STANDARD:
delta = 0.05.

HIGH:
delta = 0.01.

CATASTROPHIC:
delta = 0.001.

Risk class is chosen from the claim/loss state before evidence price is considered.

Evidence price may:
- affect whether the certificate is purchased;
- cause deferral;
- cause abstention.

Evidence price may not:
increase delta
for the same risk class.

SELECTION BASIS

UNIFORM:
uniform without-replacement sample from the relevant family population.

TRIGGERED-ACTIVE:
member appeared because current activation triggered inspection.

STRATIFIED-CALIBRATED:
sample follows a preregistered calibrated stratum design with a valid corresponding bound.

UNKNOWN:
selection mechanism cannot be certified.

PRIMARY PROVENANCE RULE

A TRIGGERED-ACTIVE observation does not count toward a UNIFORM hypergeometric certificate unless:

exchangeability_status = ESTABLISHED.

Otherwise:
it can resolve itself locally,
but certificate counting starts from the uniform post-trigger canaries.

This creates:

LOCAL EVIDENCE
and
CERTIFICATE EVIDENCE

as distinct currencies.

EPOCH RULE

A certificate is valid only inside its evidence epoch.

Synthetic epoch shift:
the family context changes after the certificate is created.

A stale certificate may not authorize the new epoch unless:
an explicit bridge/calibration test validates transfer.

Primary H140 uses:
NO TRANSFER BRIDGE.

Therefore:
epoch mismatch -> type failure -> reacquire evidence or abstain.

PRIMARY ECOLOGY

Family size:
40 to 100.

Actual hidden fractions:
0%, 5%, 10%, 20%.

Requested claim scales:
5%, 10%, 20%.

Active fractions:
10%, 40%, 80%.

Evidence prices:
0.5, 2, 8.

Risk classes:
LOW,
STANDARD,
HIGH,
CATASTROPHIC.

Trigger-selection regimes:

T0 — EXCHANGEABLE
activation independent of hidden membership.

T1 — MAJORITY-BIASED
active trigger is systematically less likely to lie in the hidden minority.

T2 — MINORITY-BIASED
active trigger is systematically more likely to lie in the hidden minority.

Epoch regimes:

E0 — CURRENT
certificate evidence and claim share the same epoch.

E1 — STALE
certificate was created before a context shift.

Primary measured-sandbox cells will sample across these factors with common worlds for policy comparisons.

At least:
2,500 worlds per primary policy condition.

POLICIES

A — UNTYPED-10-FLOOR5

H139-like comparator.

Assumes:
10% hidden-fraction target,
delta = 5%.

Counts the trigger toward the certificate.

Does not encode:
claim scale,
selection provenance,
risk class,
or epoch.

If numeric evidence count is met:
broadcast is permitted.

B — SCOPE-TYPED

Certificate carries:
min_hidden_fraction
and
delta.

Requested 5%, 10%, or 20% claim must be subsumed.

Selection provenance is still ignored.

Epoch is still ignored.

This isolates the value of explicit claim scope.

C — SCOPE + PROVENANCE TYPED

Adds:
selection_basis
and:
exchangeability_status.

Non-exchangeable trigger does not count toward uniform certificate evidence.

Requested scope and delta must both match.

Epoch still ignored.

D — FULL-TYPED CONTRACT

Adds:
risk_class
and:
evidence_epoch.

Rules:
- scope must match;
- provenance must match;
- stale epoch fails;
- risk class sets delta before price;
- price may cause abstention but cannot loosen delta.

If a weaker certificate exists:
the policy may emit a weaker explicitly typed claim,
but cannot use it for an action requiring the stronger claim.

E — PRICE-ADAPTIVE CONFIDENCE

Negative comparator.

Chooses among:
delta 0.001,
0.01,
0.05,
0.10

to maximize expected scalar net value after observing evidence price.

It is allowed to loosen confidence when evidence becomes expensive.

This comparator tests:
whether the H138 shortcut reappears when confidence level itself is economically tradable.

F — FULL-FAMILY

Audit every member.
Reference upper bound on direct evidence cost/coverage.

CERTIFICATE CALCULATION

For a UNIFORM certificate:

N = relevant family population.

m = ceil(f_required x N).

Choose the smallest k such that:

C(N-m,k) / C(N,k) <= delta.

For policy C/D:

a non-exchangeable trigger is not part of k.

If the trigger is exchangeable:
it may count.

For calibrated stratified evidence:
H140 primary does not grant free credit.

A separate exploratory extension may test valid weighted bounds,
but only after calibration on held-out synthetic worlds.

ECONOMICS

Use H139/H138 active-value-decoupled economics.

Active correct resolution:
+3 x value.

Active false promotion:
-5 x value.

Inactive false promotion:
-0.5 x value.

Unresolved active carry:
-0.15 x value.

Broadcast application:
-0.20 x N.

Inactive audit:
no immediate task reward.

Evidence price:
as above.

Primary type-validity metrics are evaluated separately from economic reward.

PRIMARY METRICS

1. type-invalid broadcast count;
2. false-broadcast rate conditional on actual hidden fraction;
3. miss rate relative to requested claim scope;
4. certificate evidence/event;
5. active weighted coverage;
6. mean net value;
7. 1st-percentile net;
8. epistemic abstention;
9. economic defer;
10. stale-certificate rejection rate;
11. trigger-credit rejection rate;
12. explicit claim-downgrade rate;
13. confidence-loosening events under price shock.

PRIMARY ACCEPTANCE SHAPE

The typed-certificate thesis is supported if:

- FULL-TYPED produces zero type-invalid broadcasts by construction and implementation;
- a 10%-scope certificate is never accepted for a requested 5%-scope claim;
- a non-exchangeable active trigger is never silently counted as uniform evidence;
- stale certificates are rejected after epoch change;
- empirical false-broadcast for valid uniform certificates tracks their requested delta within Monte Carlo error;
- HIGH and CATASTROPHIC classes remain at their preregistered delta under evidence-price shock;
- rising evidence price increases abstention or reduces coverage rather than loosening the risk class;
- FULL-TYPED uses materially less evidence than FULL-FAMILY in at least some ordinary current-epoch cells;
- FULL-TYPED improves high-value severe-tail behavior relative to the fixed STANDARD 5% floor in at least one preregistered high-harm stress;
- PRICE-ADAPTIVE CONFIDENCE demonstrates at least one regime where mean value improves while epistemic reliability worsens, confirming the need for the firewall.

FAILURE CONDITIONS

Treat H140 as mixed/negative if:

- typed metadata does not prevent scope leakage;
- provenance-aware counting still violates the requested uniform bound;
- epoch invalidation does not prevent stale reuse;
- risk class is effectively allowed to loosen with price;
- type safety requires full-family evidence almost everywhere;
- explicit claim downgrade becomes semantically indistinguishable from overclaim;
- high-harm risk classes merely add evidence cost without improving severe tails;
- implementation complexity provides no measurable protection over the untyped comparator.

PRIMARY HIGH-HARM STRESS

Exact HIDDEN-10.

One active minority member carries high value.

Two operating points are frozen:

H1:
active fraction 40%,
evidence price 1.

H2:
active fraction 20%,
evidence price 2.

Compare:
STANDARD 5%,
HIGH 1%,
CATASTROPHIC 0.1%.

This explicitly tests the H139 primary/secondary difference.

PRIMARY CLAIM-SCOPE MATRIX

Requested scope x actual hidden fraction:

requested 5%:
actual 5%, 10%, 20%.

requested 10%:
actual 5%, 10%, 20%.

requested 20%:
actual 5%, 10%, 20%.

A certificate's statistical guarantee is judged only inside its declared scope.

Type-invalid use is counted separately and is never excused by favorable empirical luck.

PRIMARY TRIGGER-PROVENANCE MATRIX

For requested 10% / STANDARD 5%:

exchangeable trigger;
majority-biased trigger;
minority-biased trigger.

Compare:

- trigger counted as uniform;
- trigger excluded;
- trigger counted only under established exchangeability.

The expected analytic boundary from H139 is:

counting a known majority-biased trigger can raise the nominal 5% raw miss above 5%.

H140 tests whether the provenance firewall removes this error.

PRIMARY EPOCH STRESS

Create a valid current-epoch certificate.

Then switch to a new hidden partition/context.

Compare:

UNTYPED:
reuses numeric confidence.

FULL-TYPED:
rejects stale epoch,
then reacquires evidence or abstains.

No free bridge is allowed in the primary test.

OUT-OF-BOX EXTENSION

If the typed contract succeeds,
the next research direction is not merely:
MORE AUDITS.

It is:

COMPOSABLE EPISTEMIC OBJECTS.

Potential future operations:

- certificate intersection across independent evidence sources;
- certificate narrowing;
- certificate expiry;
- certificate inheritance with explicit loss of strength;
- hierarchical family/subfamily certificates;
- proof-carrying memory where dormant representations retain not only content but the conditions under which that content was trusted.

This could let Yggdrasil treat:
KNOWLEDGE
as:
STATE WITH VALIDITY SEMANTICS,

rather than:
A SCALAR CONFIDENCE ATTACHED TO STATE.

RELATED CONCEPTUAL CROSS-CHECK

This direction is conceptually consistent with modern selective prediction and conformal-risk-control work:

- selective prediction treats abstention as a first-class action;
- conformal risk control separates a statistical guarantee from raw confidence score;
- recent group-conditional work emphasizes that a marginal guarantee does not automatically protect every subgroup;
- online selective methods emphasize that post-selection validity depends on the selection process.

H140 does not import those results as proof.

It uses them as:
DESIGN PRESSURE
for a developmental finite-population certificate system.

FROZEN BEFORE EXECUTION

Certificate fields,
subsumption rules,
risk classes,
selection basis,
epoch rule,
primary ecologies,
comparators,
metrics,
acceptance shape,
failure conditions,
and high-harm operating points above
are fixed before synthetic execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = ANALYTIC_PLUS_SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = ae6eb4fc335f672f1a72bfa2aeb92a29ed4be244


EXECUTION RESULT

H140 was executed as a set of linked targeted matrices rather than an indiscriminate full-factorial explosion.

Every measured policy condition used at least:
5,000 worlds

except larger targeted stresses which used:
10,000 to 20,000 worlds.

Common worlds were used within policy comparisons.

No H140 acceptance rule was changed after execution.

PRIMARY CLAIM-SCOPE MATRIX

Operating point:

active fraction:
80%.

evidence price:
0.5.

risk class:
STANDARD.

trigger:
exchangeable.

current epoch.

5,000 worlds per:
requested-scope x actual-hidden-fraction cell.

REQUESTED 5% SCOPE

ACTUAL HIDDEN 5%

UNTYPED-10-FLOOR5

false-broadcast:
20.86%.

type-invalid broadcast:
20.86%.

mean evidence:
12.218.

FULL-TYPED

false-broadcast:
4.84%.

type-invalid broadcast:
0%.

mean evidence:
13.966.

ACTUAL HIDDEN 10%

UNTYPED:
4.64% false-broadcast,
all broadcast use is type-invalid for the requested 5%-scope claim.

FULL-TYPED:
0.16% false-broadcast.

ACTUAL HIDDEN 20%

UNTYPED:
0.24%.

FULL-TYPED:
0%.

SCOPE-FIREWALL RESULT

A 10%-minority certificate can no longer silently satisfy a 5%-minority request.

The typed policy pays the correct evidence cost for the smaller subgroup scale.

This passes the primary scope-leakage gate.

REQUESTED 10% SCOPE

ACTUAL HIDDEN 10%

FULL-TYPED false-broadcast:
4.90%.

type-invalid:
0%.

ACTUAL HIDDEN 5%

FULL-TYPED false-broadcast:
19.86%.

type-invalid:
0%.

This is intentional and important.

The requested claim was:

detect an unmarked minority
of at least 10%.

A 5% hidden minority lies outside that contract.

The type system does not falsely claim protection.

But:
the family-wide action can still be harmful.

This becomes the main H140 architectural limit.

REQUESTED 20% SCOPE

ACTUAL HIDDEN 20%

FULL-TYPED false-broadcast:
4.64%.

ACTUAL HIDDEN 10%

false-broadcast:
21.64%.

ACTUAL HIDDEN 5%

false-broadcast:
45.08%.

type-invalid in all three requested-20% cells:
0%.

INTERPRETATION

TYPE SAFETY
PREVENTS
CLAIM LAUNDERING.

It does not guarantee:

THE CLAIM REQUESTED
WAS STRONG ENOUGH
FOR THE ACTION.

That proof obligation must come from:
the action's possible effects,
not:
an arbitrary requested confidence scope.

PRIMARY TRIGGER-PROVENANCE MATRIX

Requested claim:
10%-minority,
STANDARD 5%.

Actual hidden:
10%.

active fraction:
80%.

evidence price:
0.5.

20,000 worlds per trigger regime.

T0 — EXCHANGEABLE TRIGGER

SCOPE:
4.61% false-broadcast.

PROVENANCE-TYPED:
4.61%.

FULL-TYPED:
4.61%.

T1 — MAJORITY-BIASED TRIGGER

SCOPE-ONLY,
which incorrectly counts the trigger as uniform:

false-broadcast:
5.36%.

type-invalid broadcast:
5.36%.

PROVENANCE-TYPED:

false-broadcast:
4.72%.

trigger-credit rejection:
100%.

FULL-TYPED:

false-broadcast:
4.72%.

type-invalid:
0%.

T2 — MINORITY-BIASED TRIGGER

The trigger detects the hidden minority before family broadcast in the tested stress.

false-broadcast:
approximately 0%.

PROVENANCE RESULT

The H139 analytic concern is experimentally confirmed.

A counted sample is not characterized only by:

HOW MANY OBSERVATIONS.

It is also characterized by:

WHY THOSE OBSERVATIONS
ENTERED THE SAMPLE.

Excluding a known non-exchangeable trigger restores the requested miss bound in the majority-biased stress.

PRIMARY EPOCH STRESS

A previously valid numeric certificate is carried across a context shift.

New epoch:
independent current hidden partition.

Requested claim:
10% / STANDARD 5%.

Actual hidden:
10%.

10,000 worlds.

UNTYPED

stale numeric confidence is reused.

false-broadcast:
90.01%.

type-invalid broadcast:
90.01%.

SCOPE-TYPED

false-broadcast:
90.01%.

type-invalid:
90.01%.

SCOPE + PROVENANCE

false-broadcast:
90.01%.

type-invalid:
90.01%.

FULL-TYPED

stale certificate rejection:
100%.

fresh certificate purchase:
56.78%.

false-broadcast after reacquisition:
4.38%.

type-invalid broadcast:
0%.

EPOCH RESULT

CONFIDENCE
IS TEMPORAL STATE.

A confidence value without:
an evidence epoch

is unsafe to reuse after context change.

PRIMARY PRICE-SHOCK / RISK-CLASS STRESS

Mixed regime prior:

CLEAN:
50%.

HIDDEN-10:
35%.

HIDDEN-20:
15%.

active fraction:
80%.

first five evidence price:
0.5.

post-probe shock:
8.

20,000 worlds per risk-class comparison.

STANDARD

FULL-TYPED

mean net:
6.44.

HIDDEN-10 false-broadcast:
2.56%.

type-invalid broadcast:
0%.

PRICE-ADAPTIVE CONFIDENCE

mean net:
18.40.

selected delta after shock:
approximately 10%.

HIDDEN-10 false-broadcast:
7.76%.

type-invalid broadcast:
45.60%.

Thus:
the adaptive scalar policy buys more reward
by weakening the declared confidence contract.

HIGH

FULL-TYPED

mean net:
1.06.

1st percentile:
-10.43.

HIDDEN-10 false-broadcast:
0%.

epistemic abstention:
73.11%.

risk delta remains:
1%.

PRICE-ADAPTIVE

mean net:
19.02.

1st percentile:
-65.34.

selected delta:
approximately 10%.

HIDDEN-10 false-broadcast:
8.27%.

type-invalid broadcast:
46.72%.

CATASTROPHIC

FULL-TYPED

mean net:
1.13.

1st percentile:
-9.73.

HIDDEN-10 false-broadcast:
0%.

epistemic abstention:
73.93%.

risk delta remains:
0.1%.

PRICE-ADAPTIVE

mean net:
18.66.

1st percentile:
-65.18.

selected delta:
approximately 10%.

HIDDEN-10 false-broadcast:
7.88%.

type-invalid broadcast:
46.13%.

PRICE-SHOCK RESULT

The preregistered negative comparator succeeds in exposing the failure mode:

MEAN REWARD
CAN IMPROVE

while:

THE CLAIM'S
EPISTEMIC CONTRACT
IS VIOLATED.

FULL-TYPED refuses that trade.

Price changes:
coverage
and
abstention.

It does not mutate:
the risk class.

PRIMARY HIGH-HARM STRESS

Exact HIDDEN-10.

One active hidden-minority member carries high value.

20,000 worlds per operating point.

H1

active fraction:
40%.

evidence price:
1.

STANDARD 5%

mean net:
1.2473.

1st percentile:
-31.0931.

false-broadcast:
4.48%.

HIGH 1%

mean net:
1.9710.

1st percentile:
-13.7943.

false-broadcast:
0.86%.

CATASTROPHIC 0.1%

mean net:
2.2211.

1st percentile:
-12.1126.

false-broadcast:
0.06%.

H2

active fraction:
20%.

evidence price:
2.

STANDARD 5%

mean net:
-8.7316.

1st percentile:
-78.4514.

false-broadcast:
4.43%.

HIGH 1%

mean net:
-5.8573.

1st percentile:
-43.4957.

false-broadcast:
0.48%.

epistemic abstention:
18.42%.

CATASTROPHIC 0.1%

mean net:
-3.9660.

1st percentile:
-31.5824.

false-broadcast:
0.01%.

epistemic abstention:
39.98%.

HIGH-HARM RESULT

The H139 secondary boundary is reproduced.

In both frozen high-harm operating points:

a stricter risk class improves:
mean net
and
severe tail.

The mechanism is not free evidence.

At H2,
CATASTROPHIC becomes safer partly by:

REFUSING
TO MAKE
THE FAMILY-WIDE CLAIM.

Thus:

LOSS SEVERITY
CAN TIGHTEN
THE PROOF OBLIGATION.

Evidence price cannot loosen it.

EXPLICIT DOWNGRADE STRESS

Requested claim:
5% subgroup scope.

risk class:
CATASTROPHIC.

active fraction:
40%.

evidence price:
2.

When the requested strong certificate is uneconomic:

explicit weaker-claim downgrade is available in:
31.28% of worlds.

strong-claim broadcast:
approximately 0%.

epistemic abstention:
31.64%.

The weaker claim is represented as:
A DIFFERENT TYPE.

It does not authorize:
the stronger action requirement.

This demonstrates that:

SAYING LESS

and:

OVERCLAIMING

can be made mechanically distinct.

EVIDENCE-EFFICIENCY CHECK

Representative hard scope:

requested:
5% / STANDARD 5%.

actual hidden:
5%.

active:
80%.

evidence price:
0.5.

FULL-TYPED

mean evidence:
13.70.

FULL-FAMILY

mean evidence:
70.31.

Therefore:
type safety does not collapse into full-family inspection.

PRIMARY TYPE-SAFETY SUMMARY

Across measured H140 primary modules:

FULL-TYPED type-invalid broadcasts:
0.

Observed protections:

- claim-scope mismatch is rejected;
- non-exchangeable trigger credit is rejected;
- stale epoch reuse is rejected;
- risk-class loosening under compute shock is rejected;
- explicit weaker claims remain semantically distinct;
- empirical in-scope miss rates track the declared bound;
- strict high-harm classes improve severe tails;
- evidence remains far below full-family inspection in ordinary cells.

PRIMARY LIMIT

The strongest H140 limit is not inside the certificate.

It is upstream:

WHO DECIDES
WHAT MUST BE CERTIFIED?

A perfectly type-safe 20%-minority certificate can coexist with:

a damaging undetected 5% minority

if the family-wide action was allowed to request only:
20% scope.

Therefore:

A CERTIFICATE SYSTEM
CANNOT
DEFINE ITS OWN
PROOF OBLIGATION.

The proof obligation must be derived from:

THE ACTION
+
THE ACTION'S
POSSIBLE FAILURE EFFECTS.

OUT-OF-BOX GENERALIZATION

This suggests an architecture analogous to:
an effect system
or:
proof-carrying action.

Not merely:

STATE
+
CONFIDENCE.

Instead:

PROPOSED ACTION
->
DERIVED EPISTEMIC OBLIGATIONS
->
MATCHING CERTIFICATES
->
ACTION OR ABSTENTION.

An action should carry an:

EPISTEMIC EFFECT SIGNATURE.

Candidate fields:

- population affected;
- maximum tolerated hidden subgroup;
- maximum tolerated miss probability;
- harm class;
- temporal horizon;
- allowed evidence epoch;
- required sampling assumptions;
- allowed unresolved value mass.

A family-wide action cannot ask for:
a conveniently weak certificate.

Its effect signature determines:
the minimum admissible proof.

If that proof is unaffordable:

the system can:
- abstain;
- act locally;
- shrink the action scope;
- split the family;
- quarantine uncertified members.

It cannot:
weaken the proof while preserving the same action.

DECISION

AR-H140 is:

POSITIVE

for:

TYPED EPISTEMIC CERTIFICATES.

SUPPORTED

- certificate semantics can be separated from scalar economic optimization;
- explicit scope prevents 10%-certificate -> 5%-claim laundering;
- selection provenance is necessary for finite-population guarantees;
- epoch is a required component of reusable confidence;
- risk class can remain invariant under compute-price shock;
- stricter harm classes can improve severe tails;
- explicit claim downgrade is meaningfully different from overclaim;
- typed contracts can remain much cheaper than full-family evidence.

NEWLY ESTABLISHED LIMIT

TYPE-SAFE KNOWLEDGE
IS NOT ENOUGH.

The requested claim itself must be:
ACTION-SAFE.

NEXT HIGH-VALUE MOVE

AR-H141 — EPISTEMIC EFFECT SYSTEM / ACTION-DERIVED PROOF-OBLIGATION AUDIT

Question:

CAN
THE ACTION ITSELF
DERIVE
THE MINIMUM EVIDENCE
IT IS ALLOWED
TO REQUIRE?

Instead of letting the controller choose:

claim scope
and then:
seek a certificate,

invert the relationship:

ACTION EFFECTS
->
MANDATORY CLAIM TYPE
->
CERTIFICATE SEARCH.

Primary idea:

FAMILY-WIDE BROADCAST

carries a stronger proof obligation than:

LOCAL UPDATE.

If a family-wide obligation cannot be satisfied:

do not weaken the certificate.

Shrink:
THE ACTION.

Potential mechanisms:

A.
proof-carrying action signature;

B.
maximum unresolved-harm envelope;

C.
automatic subgroup-scale requirement from affected value mass;

D.
partial/subfamily broadcast;

E.
recursive split until each action scope is certifiable;

F.
quarantine of uncertified members;

G.
budget shock causes action-scope contraction rather than confidence degradation.

Desired invariant:

RESOURCE SCARCITY
SHOULD SHRINK
THE RADIUS OF ACTION,

NOT:
THE QUALITY OF PROOF
FOR THE SAME RADIUS.

Do not execute STAB-18-R1 during this lane.

EXECUTION PROVENANCE

evidence_class = ANALYTIC_PLUS_SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
scope_matrix_worlds_per_cell = 5000
trigger_matrix_worlds_per_regime = 20000
epoch_worlds = 10000
price_shock_worlds_per_risk_class = 20000
high_harm_worlds_per_point = 20000
full_typed_type_invalid_broadcasts = 0
scope5_actual5_untyped_false = 0.2086
scope5_actual5_full_typed_false = 0.0484
majority_trigger_scope_only_false = 0.0536
majority_trigger_full_typed_false = 0.0472
stale_untyped_false = 0.9001
stale_full_typed_false = 0.0438
high_shock_full_typed_h10_false = 0
high_shock_price_adapt_h10_false = 0.0827
catastrophic_shock_full_typed_h10_false = 0
catastrophic_shock_price_adapt_h10_false = 0.0788
h1_standard_p01 = -31.0931
h1_high_p01 = -13.7943
h1_catastrophic_p01 = -12.1126
h2_standard_p01 = -78.4514
h2_high_p01 = -43.4957
h2_catastrophic_p01 = -31.5824
representative_full_typed_evidence = 13.70
representative_full_family_evidence = 70.31
