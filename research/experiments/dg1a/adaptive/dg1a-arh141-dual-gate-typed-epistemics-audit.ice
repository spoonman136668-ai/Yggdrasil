TITLE: DG-1A-AR-H141 — Dual-Gate Claim Purchase / Resource-Rational Typed Epistemics Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE DUAL-GATE RESULT + TYPED MULTI-FAMILY ALLOCATION SUPPORT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh140-claim-scope-trigger-bias-audit.ice
PARENT_RESULT_COMMIT: 1656a4f3692eb65d1755023e450c1c168770649a
PREREGISTRATION_COMMIT: 5e36152db26ed46163bb52a86fa35214739f343a

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


EXECUTION RESULT

PRIMARY RUN

Preregistered generator used unchanged.

Seed:

20260919141.

Primary worlds:

18,000.

RESOURCE-BLIND TYPED

mean net:
-30.64192.

1st percentile:
-310.33130.

mean evidence:
22.66428.

active weighted coverage:
65.603%.

broadcast:
46.367%.

certificate purchase:
93.433%.

semantic overclaim:
0%.

claim-valid false-broadcast:
2.261%.

DUAL-GATE TYPED

mean net:
15.57741.

1st percentile:
-81.90970.

mean evidence:
11.18100.

active weighted coverage:
37.424%.

broadcast:
23.672%.

certificate purchase:
47.322%.

epistemic abstention:
46.111%.

semantic overclaim:
0%.

claim-valid false-broadcast:
1.130%.

DUAL-GATE + CAP-24

mean net:
7.53965.

1st percentile:
-79.39071.

mean evidence:
5.93994.

coverage:
26.587%.

broadcast:
16.783%.

certificate purchase:
31.689%.

epistemic abstention:
61.744%.

semantic overclaim:
0%.

claim-valid false-broadcast:
0.739%.

audit-cap refusal:
36.978%.

ECONOMIC TRADE-DOWN

mean net:
16.15495.

mean evidence:
10.36650.

broadcast:
31.167%.

semantic overclaim among broadcasts:
46.150%.

claim-valid false-broadcast:
6.477%.

EXPLICIT WEAKER OFFER

mean net:
4.12445.

mean evidence:
10.36650.

broadcast:
16.783%.

semantic overclaim:
0%.

claim-valid false-broadcast:
0.739%.

explicit weaker-offer rate:
26.983%.

SCALAR ECONOMIC COMPARATOR

mean net:
49.27680.

1st percentile:
-18.67943.

mean evidence:
4.50500.

coverage:
72.607%.

broadcast:
69.883%.

semantic overclaim among broadcasts:
87.956%.

claim-valid false-broadcast:
57.412%.

FULL-FAMILY

mean net:
-154.51323.

mean evidence:
70.09794.

coverage:
100%.

PRIMARY DUAL-GATE RESULT

The primary thesis passes.

Relative to resource-blind typed certification:

DUAL-GATE

changes:

mean net
from:
-30.64
to:
+15.58.

mean evidence
from:
22.66
to:
11.18.

semantic overclaim remains:

0%.

claim-valid false-broadcast decreases:

2.261%
to
1.130%.

Therefore:

RESOURCE ADMISSION
CAN
REDUCE COMPUTE

WITHOUT:

RELAXING
THE EPISTEMIC CONTRACT.

The reduction comes from:

NOT BUYING
THE CLAIM

rather than:

BUYING
A WEAKER CLAIM
AND CALLING IT
THE SAME THING.

RESOURCE PHASE MAP

DUAL-GATE certificate purchase rate:

ACTIVE 10%

price 0.5:
27.85%.

price 2:
0.45%.

price 8:
0%.

ACTIVE 40%

price 0.5:
93.40%.

price 2:
78.30%.

price 8:
4.10%.

ACTIVE 80%

price 0.5:
94.50%.

price 2:
92.65%.

price 8:
34.65%.

This is the desired two-axis phase transition.

At fixed activity:

higher price
reduces purchase.

At fixed price:

higher active value
increases purchase.

The claim contract itself does not change.

LOW-ACTIVITY SILENCE

At active 10%, price 8:

certificate purchase:
0%.

epistemic abstention:
94.85%.

broadcast:
0%.

This is not a failure to reason.

It is:

RESOURCE-RATIONAL
EPISTEMIC SILENCE.

The stored family remains available.

Fresh broad inference is simply not worth purchasing.

HIGH-VALUE / LOW-PRICE PURCHASE

At active 80%, price 0.5:

certificate purchase:
94.50%.

broadcast:
45.55%.

mean net:
83.8982.

The same controller that abstains under sparse/high-price conditions
buys the contract aggressively when current value supports it.

Thus:

THE ORGANISM
DOES NOT NEED
ONE PERMANENT
EVIDENCE SPENDING MODE.

ECONOMIC TRADE-DOWN FAILURE

The deliberate unsafe comparator demonstrates why the two gates must remain ordered.

When the requested contract is too costly:

ECONOMIC TRADE-DOWN

frequently substitutes a weaker scope
and uses it to authorize the stronger task.

Observed semantic overclaim:

46.15%.

Observed claim-valid false-broadcast:

6.477%.

Mean net is slightly higher than strict DUAL:

16.15
versus
15.58.

This is another example where:

A SMALL
SCALAR REWARD IMPROVEMENT

CAN PURCHASE:

A LARGE
SEMANTIC SAFETY LOSS.

Therefore:

RESOURCE OPTIMIZATION
MUST NOT
MUTATE
CLAIM MEANING.

SCALAR OPTIMIZER FAILURE

The H138-like scalar comparator is even more extreme.

It obtains:

mean net:
49.28.

But:

87.956%
of its broadcasts
are epistemically overclaimed.

Claim-valid false-broadcast:

57.412%.

At high active value and expensive evidence:

it often broadcasts from almost no fresh certificate evidence.

For example:

ACTIVE 80% / PRICE 8

broadcast:
93.40%.

certificate purchase:
0%.

semantic overclaim:
100%.

claim-valid false-broadcast:
86.86%.

This is economically attractive
inside the toy scalar objective

and:

architecturally unacceptable
as a confidence mechanism.

PRICE-SHOCK STRESS

First five total observations:
price 0.5.

Then incremental evidence price:
8.

Active fractions:
40% and 80%.

12,000 worlds.

RESOURCE-BLIND TYPED

mean net:
-74.17048.

1st percentile:
-253.79029.

mean evidence:
22.44233.

broadcast:
47.083%.

claim-valid false-broadcast:
2.385%.

DUAL-GATE TYPED

mean net:
4.49232.

1st percentile:
-106.46098.

mean evidence:
7.73333.

broadcast:
19.650%.

epistemic abstention:
46.108%.

semantic overclaim:
0%.

claim-valid false-broadcast:
0.744%.

SCALAR OPTIMIZER

mean net:
72.32266.

mean evidence:
3.96600.

broadcast:
77.600%.

semantic overclaim:
100%.

claim-valid false-broadcast:
59.134%.

The dual gate responds to the compute shock by:

ABORTING
SOME PURCHASES

while keeping:

THE SAME
CERTIFICATE DEFINITION.

This directly satisfies the H141 shock objective.

MULTI-FAMILY SHARED-BUDGET ROBUSTNESS

5,000 epochs.

4 compatible-trigger candidate families per epoch.

Representative evidence price:
2.

Shared fresh non-trigger audit budget:

48.

FIRST-COME TYPED

mean net per epoch:
49.80189.

1st percentile:
-53.89957.

mean shared audits used:
33.6694.

mean selected families:
1.6708.

semantic overclaim:
0%.

claim-valid false-broadcast:
0.930%.

HIGHEST EV PER AUDIT

mean net:
62.36723.

1st percentile:
-42.31099.

shared audits:
32.0972.

selected:
1.7326.

semantic overclaim:
0%.

claim-valid false-broadcast:
0.902%.

HIGHEST TOTAL EV

mean net:
63.74244.

1st percentile:
-41.32477.

shared audits:
33.2406.

selected:
1.6932.

semantic overclaim:
0%.

claim-valid false-broadcast:
0.902%.

SCOPE-LOOSENING SCALAR ALLOCATOR

mean net:
110.55683.

1st percentile:
-35.42432.

shared audits:
31.1044.

selected:
2.5838.

semantic overclaim:
66.278%.

claim-valid false-broadcast:
13.301%.

The safe typed allocators improve substantially over first-come scheduling
without changing claim semantics.

The scope-loosening allocator buys much higher toy reward by:

quietly weakening requested evidence contracts.

That behavior is rejected as an architectural principle.

MULTI-FAMILY PRINCIPLE

A shared audit budget should choose:

WHICH
VALID CONTRACTS
TO FUND.

It should not choose:

HOW MUCH
TO LIE
ABOUT EACH CONTRACT.

Safe scheduling can optimize:

EV,
EV per audit,
urgency,
active value,
or other resource criteria

after:

each candidate claim
has a fixed epistemic type.

PRIMARY DECISION

AR-H141 is:

POSITIVE.

SUPPORTED

- epistemic contract and resource admission should be separate gates;
- evidence price can change purchase frequency without changing certificate semantics;
- active value can change purchase frequency without changing certificate semantics;
- dual gating materially improves resource efficiency relative to resource-blind certification;
- dual gating preserves zero semantic overclaim;
- strict dual gating remains inside the tested claim-valid miss floor;
- compute shocks correctly create abstention;
- audit caps correctly create refusal;
- explicit weaker offers preserve information without authorizing stronger tasks;
- scalar economic trade-down creates semantic overclaim;
- multi-family resource competition can be scheduled safely over fixed typed contracts;
- resource allocation and epistemic meaning need not be entangled.

NOT YET DEMONSTRATED

- certificate validity through time;
- certificate decay under context drift;
- evidence reuse across neighboring families without hidden dependence;
- online recalibration of hidden priors;
- changing task scope after a certificate is cached;
- challenge propagation when one certified family later contradicts itself;
- long-horizon interaction between certificate debt and structural regeneration.

GENERAL PRINCIPLE

THE CONTROL ORDER SHOULD BE:

1.
DEFINE
THE CLAIM.

2.
DEFINE
THE EVIDENCE
THAT WOULD MAKE
THAT CLAIM ADMISSIBLE.

3.
PRICE
THAT FIXED CONTRACT.

4.
BUY
OR
ABSTAIN.

Never:

1.
choose what is affordable;

2.
rename it
as the claim
you wanted.

This gives Yggdrasil a clean separation between:

WHAT IT KNOWS

and:

WHAT IT CAN AFFORD
TO FIND OUT
RIGHT NOW.

NEXT HIGH-VALUE MOVE

AR-H142 — EPISTEMIC CONTRACT LIFETIME / CONTEXT-DRIFT EXPIRATION AUDIT

Question:

ONCE
A FAMILY CLAIM
HAS BEEN
VALIDLY CERTIFIED,

HOW LONG
SHOULD
THAT CERTIFICATE
REMAIN USABLE

AS:

TIME,
CONTEXT,
ROLE,
LINEAGE,
AND LOCAL STATE
CHANGE?

Candidate mechanisms:

A.
never-expire cached certificate;

B.
fixed TTL;

C.
context-distance expiration;

D.
hazard-integrated evidence debt;

E.
challenge-triggered invalidation;

F.
partial canary refresh;

G.
full recertification only when accumulated drift justifies it.

Desired:

DO NOT
PAY
TO RECERTIFY
EVERYTHING
CONTINUOUSLY.

But also:

DO NOT
LET
OLD CONFIDENCE
BECOME
IMMORTAL.

This directly connects typed epistemics
to:

developmental memory,
hibernation,
reactivation,
and regeneration.

Do not execute STAB-18-R1 during this lane.

EXECUTION PROVENANCE

evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_seed = 20260919141
primary_worlds = 18000
dual_mean_net = 15.57741
dual_mean_evidence = 11.18100
dual_semantic_overclaim = 0
dual_claim_valid_false = 0.01130
dual_cap_refusal = 0.36978
trade_down_semantic_overclaim = 0.46150
scalar_semantic_overclaim = 0.87956
scalar_claim_valid_false = 0.57412
shock_dual_mean_net = 4.49232
shock_dual_claim_valid_false = 0.00744
multi_ev_per_audit_mean_net = 62.36723
multi_total_ev_mean_net = 63.74244
multi_loosen_semantic_overclaim = 0.66278
