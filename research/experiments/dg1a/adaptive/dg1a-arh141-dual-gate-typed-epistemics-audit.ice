TITLE: DG-1A-AR-H141 — Dual-Gate Claim Purchase / Resource-Rational Typed Epistemics Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh140-claim-scope-trigger-bias-audit.ice
PARENT_RESULT_COMMIT: 1656a4f3692eb65d1755023e450c1c168770649a

PURPOSE

H140 showed that typed claim contracts prevent semantic overclaim,
but a resource-blind typed controller can keep buying expensive evidence even when the economics become strongly negative.

H141 tests a two-gate architecture:

GATE 1 — EPISTEMIC CONTRACT

Determine exactly what claim would be required:

SAFE_AGAINST_UNMARKED_MINORITY(
    minimum_fraction = f_required,
    miss_probability <= 0.05,
    trigger_not_counted_as_uniform_sample
)

GATE 2 — RESOURCE ADMISSION

Given that fixed contract:

BUY IT
or
ABSTAIN.

Gate 2 may not:
- relax delta;
- increase minimum_fraction;
- count biased trigger evidence;
- silently substitute a weaker claim;
- authorize the task with a weaker certificate.

BOUNDARY

Synthetic research only.

No living tissue.
No production threshold.
No deployment.
No STAB-18-R1 execution or modification.
No canonical scientific execution.

PRIMARY GENERATOR

Use H140 generator exactly.

Seed:

20260919141.

Family size:
uniform integer 40..100.

Active fractions:
10%, 40%, 80%.

Evidence prices:
0.5, 2, 8.

Hidden regimes:
CLEAN 40%.
HIDDEN-5 20%.
HIDDEN-10 25%.
HIDDEN-20 15%.

Required task scope:
5%, 10%, 20%, equiprobable.

Member values:
lognormal,
sigma 0.60,
mean normalized approximately 1.

Minority size:
ceil(f_hidden * N).

Primary active/minority relation:
independent.

Trigger:
uniform among active members.

Uniform certificate:
fresh non-trigger samples only.

Primary worlds:
2,000 per active/price cell.

Total:
18,000.

PRIMARY HIDDEN PRIORS FOR RESOURCE GATE

For required 5% scope:

q = 0.60.

Conditional expected hidden fraction:
0.1083333333.

For required 10%:

q = 0.40.

Conditional expected hidden fraction:
0.1375.

For required 20%:

q = 0.15.

Conditional expected hidden fraction:
0.20.

These values are frozen from the primary regime prior.

RESOURCE ESTIMATOR

After a compatible active trigger:

A =
remaining unaudited active value.

D =
remaining unaudited inactive value.

Let:
f_loss =
conditional expected hidden fraction for the requested scope.

Clean family-wide gain relative to defer:

G_clean =
3.15 * A
-
0.20 * N.

Hidden-family loss relative to clean broadcast:

L_hidden =
8.0 * f_loss * A
+
0.5 * f_loss * D.

G_hidden =
G_clean - L_hidden.

Let:

k_random =
trigger-excluded exact sample count needed for
the requested f_required
at
delta <= 0.05.

Audit-resolution approximation:

audit_gain =
3.15 * A * k_random / max(1, N - 1).

Let:

r =
exact hypergeometric miss probability
for the requested scope
after k_random fresh non-trigger samples.

Estimated certificate value:

EV_contract =
-k_random * evidence_price
+
audit_gain
+
(1-q) * G_clean
+
q * r * G_hidden.

This is a deliberately simple admission estimator.

The epistemic contract is fixed before EV_contract is evaluated.

POLICIES

A — RESOURCE-BLIND TYPED

H140 SCOPE-MATCHED / TRIGGER-EXCLUDED.

Always buy the requested certificate after compatible trigger.

B — DUAL-GATE TYPED

Fix requested certificate.

If:

EV_contract > 0

buy it.

Otherwise:

ABSTAIN.

No weaker fallback.

C — DUAL-GATE + CAP-24

Same as B.

Also require:

1 trigger + k_random <= 24.

If not:

ABSTAIN.

D — ECONOMIC TRADE-DOWN

Deliberate unsafe comparator.

If requested certificate has:

EV_contract <= 0
or
does not fit cap 24,

search weaker scopes:

5% -> 10% -> 20%.

If a weaker certificate has positive estimated value and fits:

use it to authorize the original task anyway.

This intentionally violates H140 semantics.

E — EXPLICIT WEAKER OFFER

Same search as D.

But a weaker certificate:

does NOT authorize the original task.

It may be returned as a typed weaker claim.

Task action remains:

ABSTAIN.

F — H138-LIKE ECONOMIC BROADCAST

After compatible trigger,
choose the highest estimated scalar value among:

uncertified family broadcast,
requested certificate,
defer.

This comparator is allowed to sell epistemic confidence.

G — FULL-FAMILY

Audit every member.

REFERENCE SCORING

Same H140/H139 scoring.

Active correct resolution:
+3 x value.

Active false promotion:
-5 x value.

Inactive false promotion:
-0.5 x value.

Unresolved active carry:
-0.15 x value.

Family broadcast:
-0.20 x N.

Evidence:
-price per audited member.

PRIMARY METRICS

1. mean net value.
2. 1st percentile net.
3. evidence/event.
4. active weighted coverage.
5. broadcast rate.
6. epistemic abstention.
7. certificate purchase rate.
8. semantic overclaim.
9. claim-valid false-broadcast.
10. requested-scope satisfaction rate.
11. explicit weaker-offer rate.
12. cap refusal.
13. policy phase map by active fraction and evidence price.

PRIMARY ACCEPTANCE SHAPE

Dual-gate typed architecture is supported if:

- semantic overclaim remains zero for B and C;
- claim-valid false-broadcast remains approximately <=5% for B and C;
- rising evidence price materially lowers certificate purchase and raises abstention;
- rising active fraction materially raises purchase at fixed price;
- purchased certificate semantics are invariant to price;
- B materially improves mean net versus resource-blind A in high-price cells;
- B uses materially less evidence than A at high price;
- D produces semantic overclaim, showing why economic trade-down is unsafe;
- E preserves zero overclaim while exposing weaker information;
- C refuses claims that exceed cap rather than weakening scope;
- no typed policy requires full-family evidence everywhere.

FAILURE CONDITIONS

Treat H141 as mixed/negative if:

- resource gating changes certificate semantics;
- B still buys nearly all certificates at price 8;
- B nearly always abstains even at high active value / low price;
- B's claim-valid false-broadcast exceeds the fixed contract floor materially;
- C silently weakens claims;
- D fails to create semantic overclaim under scarcity;
- economic admission produces no useful resource phase transition.

PRICE-SHOCK STRESS

First five observations:
price 0.5.

After five:
incremental price 8.

The required contract remains fixed.

DUAL-GATE may:
continue purchase
or
abstain.

It may not:
reduce evidence requirement for the same claim.

MULTI-FAMILY ROBUSTNESS

Each decision epoch presents:
4 candidate dormant families.

Each has:
its own N,
active value,
required scope,
and compatible trigger.

Shared fresh-audit budget:
48 non-trigger audits.

Compare:

1.
first-come purchase;

2.
highest EV_contract per audit;

3.
highest total EV_contract;

4.
scope-loosening scalar optimizer.

The typed allocators may leave budget unused if no admissible contract has positive value.

Primary multi-family question:

CAN
RESOURCE COMPETITION
CHANGE
WHICH CLAIMS
ARE PURCHASED

WITHOUT
CHANGING
WHAT ANY PURCHASED CLAIM
MEANS?

INTERPRETATION GUARDRAIL

H141 tests separation of:

EPISTEMIC ADMISSIBILITY

from:

ECONOMIC ADMISSION.

A negative economic decision:

DOES NOT
INVALIDATE
THE CONTRACT.

It means:

DO NOT BUY
THAT CONTRACT
NOW.

FROZEN BEFORE EXECUTION

Generator,
seed,
priors,
resource estimator,
policies,
cap,
metrics,
acceptance shape,
price shock,
and multi-family robustness are frozen before execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = 1656a4f3692eb65d1755023e450c1c168770649a
primary_seed = 20260919141
primary_worlds = 18000
delta = 0.05
audit_cap = 24
