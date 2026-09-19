TITLE: DG-1A-AR-H140 — Typed Epistemic Certificate / Claim-Scope + Exchangeability Firewall Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / ANALYTIC + SYNTHETIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh139-epistemic-risk-floor-audit.ice

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
