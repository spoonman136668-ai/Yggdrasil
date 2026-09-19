TITLE: DG-1A-AR-H141 — Epistemic Effect System / Action-Derived Proof-Obligation Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE ACTION-SCOPE CONTRACTION RESULT + TOPOLOGY-QUALITY LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh140-typed-epistemic-certificate-audit.ice
PREREGISTRATION_COMMIT: be265af8a62d0f94ea56c9ab5a1fc057d9df3269

PURPOSE

H140 made knowledge type-safe.

It also exposed the next failure mode:

A CERTIFICATE
CAN BE PERFECTLY VALID

while:

THE ACTION
ASKED FOR
TOO WEAK
A CERTIFICATE.

Example:

a family-wide broadcast asks only for protection against hidden minorities of at least 20%.

A valid 20%-scope certificate may still permit severe harm to an undetected 5% subgroup.

Therefore:

THE CONTROLLER
MUST NOT
FREELY CHOOSE
ITS OWN
PROOF OBLIGATION.

H141 inverts the relationship.

Instead of:

controller chooses claim
->
certificate sought
->
action

test:

PROPOSED ACTION
->
ACTION EFFECT SIGNATURE
->
MANDATORY CLAIM TYPE
->
CERTIFICATE SEARCH
->
ACTION / SCOPE CONTRACTION / ABSTENTION.

CORE HYPOTHESIS

Resource scarcity should primarily change:

HOW FAR
THE ORGANISM
IS WILLING
TO ACT,

not:

HOW LITTLE
IT REQUIRES
TO JUSTIFY
THE SAME ACTION.

Candidate invariant:

RESOURCE SCARCITY
SHOULD SHRINK
THE RADIUS OF ACTION,

NOT:
THE QUALITY OF PROOF
FOR THE SAME RADIUS.

BOUNDARY

Synthetic research only.

It does not:
- implement living or biological tissue;
- establish production risk thresholds;
- establish production action scopes;
- execute or modify STAB-18-R1;
- spend canonical scientific execution;
- authorize runtime activation.

EVIDENCE CLASS TARGET

SYNTHETIC
MEASURED_SANDBOX

SYNTHETIC FAMILY

Family size:
80 to 120.

Each family is partitioned into:
4 to 6 latent subfamilies.

Subfamily membership is known imperfectly but fixed in the primary ecology.

Members have:
- active/inactive state;
- positive current value;
- majority/minority compatibility;
- subfamily identity.

Active fraction:
10%, 30%, 60%, 90%.

Evidence price:
0.5, 1, 2, 4, 8.

Regime prior:

COHERENT:
45%.

LOCAL-SUBFAMILY-DRIFT:
30%.

CROSS-SUBFAMILY-SPARSE-DRIFT:
15%.

WHOLE-FAMILY-SHIFT:
10%.

Primary worlds:
3,000 per activity/price cell.

20 primary cells.

Total primary worlds:
60,000.

ACTION SET

A0 — LOCAL

Affect:
trigger only.

Evidence obligation:
direct trigger observation.

No extrapolation certificate.

A1 — SUBFAMILY

Affect:
the trigger's nominated subfamily only.

Mandatory proof obligation:

within that subfamily:
minimum hidden fraction = 10%.

max miss probability:
5%.

Evidence must be:
current epoch,
uniform/exchangeable within the subfamily
or explicitly corrected.

A2 — FAMILY-WIDE

Affect:
entire family.

Mandatory proof obligation:

minimum hidden fraction = 5%.

max miss probability:
1%.

Evidence must be:
current epoch,
uniform/exchangeable across the family
or explicitly corrected.

The controller is not allowed to weaken these obligations.

ACTION EFFECT SIGNATURE

Each proposed action carries:

{
    action_scope,
    affected_population,
    max_hidden_fraction_class,
    max_miss_probability,
    evidence_epoch,
    selection_requirement
}

The proof obligation is generated from:
action_scope.

It is not selected by:
evidence price.

PRIMARY POLICIES

A — BLIND-GLOBAL

After a small compatible probe:
broadcast family-wide.

No typed proof obligation.

B — PRICE-DEGRADED-GLOBAL

Always prefers family-wide action.

When evidence is expensive,
may weaken the global proof from:

5% subgroup / 1% miss

to:

10% / 5%

or:

20% / 10%.

This is the negative comparator.

It keeps:
ACTION RADIUS

while shrinking:
PROOF QUALITY.

C — GLOBAL-OR-ABSTAIN

Family-wide action only.

Keeps:
5% subgroup / 1% miss

at every price.

If proof is uneconomic:
abstain.

This isolates the value of fixed global proof without scope contraction.

D — EFFECT-TYPED CONTRACTION

Try actions in descending useful scope:

1. FAMILY-WIDE,
but only with its fixed 5% / 1% proof;

2. if global proof is unaffordable or contradicted,
try SUBFAMILY with its fixed 10% / 5% proof;

3. if subfamily proof is unavailable,
fall back to LOCAL;

4. if even local action is negative,
ABSTAIN.

Evidence price may change:
which action is selected.

It may not change:
the proof obligation for a given action.

E — FULL-FAMILY

Audit every member.

Reference evidence upper bound.

ECONOMICS

Continue H138/H140 active-value-decoupled scoring.

Active correct resolution:
+3 x value.

Active false promotion:
-5 x value.

Inactive false promotion:
-0.5 x value.

Unresolved active carry:
-0.15 x value.

Application cost:

LOCAL:
0.

SUBFAMILY:
-0.20 x affected subfamily size.

FAMILY-WIDE:
-0.20 x family size.

Audited inactive:
no immediate task reward.

Fresh evidence:
-evidence_price per audit.

ACTION-SCOPE CONTRACT

A policy receives a proposed action benefit estimate.

It may decide:

DO NOT ATTEMPT THIS ACTION.

It may not decide:

ATTEMPT THE SAME ACTION
WITH A WEAKER CERTIFICATE.

If proof fails:

GLOBAL
may contract to:
SUBFAMILY.

SUBFAMILY
may contract to:
LOCAL.

This contraction is:
an action change,
not:
a confidence downgrade.

PRIMARY METRICS

1. mean net value;
2. 1st-percentile net;
3. evidence audits/event;
4. active weighted coverage;
5. false-promotion rate;
6. family-wide action rate;
7. subfamily action rate;
8. local action rate;
9. abstention rate;
10. type-invalid action count;
11. proof-obligation weakening count;
12. action-radius contraction rate;
13. hidden-drift containment by regime;
14. cost per correctly resolved active value.

PRIMARY ACCEPTANCE SHAPE

The epistemic-effect thesis is supported if:

- EFFECT-TYPED produces zero proof-obligation weakening events;
- rising evidence price reduces FAMILY-WIDE action rate;
- rising evidence price increases SUBFAMILY / LOCAL / ABSTAIN use;
- the proof requirement for each named action is invariant across price;
- EFFECT-TYPED obtains higher mean net than GLOBAL-OR-ABSTAIN in at least the medium/high-price region by recovering useful narrower actions;
- EFFECT-TYPED has materially lower false promotion and better severe-tail behavior than PRICE-DEGRADED-GLOBAL;
- low-price coherent-family worlds still permit broad action when its stronger proof is affordable;
- subfamily action contains LOCAL-SUBFAMILY-DRIFT better than blind/global-degraded action;
- full-family auditing is not required for most accepted actions;
- no type-invalid action is authorized.

FAILURE CONDITIONS

Treat H141 as mixed/negative if:

- scope contraction does not improve utility over global-or-abstain;
- subfamily action simply reproduces family-wide false promotion at smaller scale;
- proof obligations quietly vary with evidence price;
- action selection becomes nearly always local;
- family-wide action disappears even when cheap evidence and coherent families support it;
- subfamily boundaries are so unreliable that contraction has no containment value;
- evidence cost approaches FULL-FAMILY in most cells.

ROBUSTNESS

Subfamily count:
4, 5, 6.

Subfamily-size imbalance:
low,
medium,
high.

Hidden drift:

R1:
single-subfamily.

R2:
two-subfamily.

R3:
sparse cross-subfamily.

R4:
whole-family coherent shift.

Subfamily-label quality:

perfect;
10% label noise;
25% label noise.

Trigger location:

inside drift;
outside drift;
exchangeable.

Value concentration:

uniform-ish;
one high-value hidden member;
high-value active cluster.

Evidence-price shock:

0.5 -> 8
after the first local probe.

ACTION-OBLIGATION STRESS

A deliberately under-specified controller asks:

CAN I USE
A 20%-SCOPE / 10%-MISS CERTIFICATE
FOR FAMILY-WIDE ACTION?

The effect system must answer:

NO.

It may offer:

- SUBFAMILY action with its own valid contract;
- LOCAL action;
- or abstention.

It may not:
reinterpret the family-wide obligation.

OUT-OF-BOX EXTENSION

If H141 works,
the developmental system gains a new control variable:

ACTION RADIUS.

That enables a resource-adaptive architecture in which:

high resources
->
broad proof
->
broad action

medium resources
->
local/subfamily proof
->
bounded action

low resources
->
direct local evidence
->
local action or dormancy.

This is different from ordinary uncertainty thresholding.

The system does not merely become:
LESS CONFIDENT.

It becomes:
LESS GLOBAL.

Possible long-term implication:

COGNITIVE DEGRADATION
UNDER RESOURCE PRESSURE

could be designed to fail gracefully as:

REDUCED SCOPE
+
PRESERVED VALIDITY,

rather than:

UNCHANGED SCOPE
+
DEGRADED RELIABILITY.

FROZEN BEFORE EXECUTION

Ecology,
action set,
proof obligations,
policies,
economics,
metrics,
acceptance shape,
failure conditions,
and robustness dimensions above
are fixed before synthetic execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = 74e55461a101e695cd37f48f41a6855eaeb9bfb1


EXECUTION RESULT

PRIMARY SANDBOX

20 activity/price cells.

3,000 worlds per cell.

Total:
60,000 primary worlds.

Common worlds were used across comparators.

Primary implementation realization:

family size:
uniform integer 80..120.

subfamily count:
4..6.

primary observed subfamily-label noise:
10%.

member value:
positive lognormal,
mean approximately one,
sigma 0.60.

The WHOLE-FAMILY-SHIFT regime is represented as:
a coherent current candidate model
whose stored predecessor was stale.

Thus:
its current proposed family action has no hidden incompatible subgroup.

PRIMARY AGGREGATE RESULT

BLIND-GLOBAL

mean net:
66.1921.

1st percentile:
-42.1134.

mean evidence:
4.3861.

active weighted coverage:
73.10%.

mean false-promotion rate:
2.78%.

family-wide action:
74.18%.

type-invalid family-wide action:
74.18%.

PRICE-DEGRADED-GLOBAL

mean net:
42.1125.

1st percentile:
-45.8145.

mean evidence:
15.2754.

active weighted coverage:
44.38%.

mean false-promotion rate:
0.26%.

family-wide action:
39.87%.

proof weakening attempted:
55.65%.

type-invalid action:
22.87%.

GLOBAL-OR-ABSTAIN

mean net:
21.1352.

1st percentile:
-22.6832.

mean evidence:
16.3323.

active weighted coverage:
30.30%.

family-wide action:
25.47%.

abstention:
67.29%.

type-invalid action:
0.

EFFECT-TYPED CONTRACTION

mean net:
22.8007.

1st percentile:
-25.3605.

mean evidence:
18.1562.

active weighted coverage:
33.12%.

mean false-promotion rate:
0.36%.

family-wide action:
25.47%.

subfamily action:
10.84%.

local action:
63.69%.

action-radius contraction:
67.29%.

proof weakening:
0.

type-invalid action:
0.

FULL-FAMILY

mean net:
-156.0444.

mean evidence:
92.8020.

PRIMARY ACTION-RADIUS PHASE MAP

EFFECT-TYPED by evidence price:

PRICE 0.5

mean net:
60.0577.

family-wide:
43.38%.

subfamily:
19.07%.

local:
37.56%.

mean evidence:
30.36.

PRICE 1

mean net:
45.9364.

family-wide:
41.62%.

subfamily:
15.42%.

local:
42.97%.

mean evidence:
28.68.

PRICE 2

mean net:
23.8633.

family-wide:
27.97%.

subfamily:
13.10%.

local:
58.93%.

mean evidence:
20.01.

PRICE 4

mean net:
-3.9049.

family-wide:
14.39%.

subfamily:
6.60%.

local:
79.01%.

mean evidence:
10.73.

PRICE 8

mean net:
-11.9491.

family-wide:
0%.

subfamily:
approximately 0.01%.

local:
99.99%.

mean evidence:
approximately 1.

PHASE-TRANSITION RESULT

As evidence price rises:

THE RADIUS OF ACTION
CONTRACTS.

The proof obligation for:

FAMILY-WIDE

remains:
5% subgroup / 1% miss.

The proof obligation for:

SUBFAMILY

remains:
10% subgroup / 5% miss.

Neither changes with price.

This passes the central H141 invariant.

UTILITY OF CONTRACTION

Compared with GLOBAL-OR-ABSTAIN:

PRICE 0.5

EFFECT:
60.06.

GLOBAL-OR-ABSTAIN:
55.84.

PRICE 1

EFFECT:
45.94.

GLOBAL-OR-ABSTAIN:
42.67.

PRICE 2

EFFECT:
23.86.

GLOBAL-OR-ABSTAIN:
22.55.

Thus:
narrower certified action recovers useful work
that a global-only safe policy would discard.

At price 4:

EFFECT:
-3.90.

GLOBAL-OR-ABSTAIN:
-3.44.

At price 8:

both are approximately:
-11.95.

Therefore contraction is not universally free.

At very high evidence price:
even subfamily proof can become uneconomic.

The correct endpoint becomes:
LOCAL.

MEDIUM/HIGH-PRICE SAFETY COMPARISON

Across price >= 2:

PRICE-DEGRADED-GLOBAL

mean net:
37.3496.

1st percentile:
-54.4555.

mean false-promotion rate:
0.43%.

type-invalid action:
38.12%.

EFFECT-TYPED

mean net:
2.6698.

1st percentile:
-30.6066.

mean false-promotion rate:
0.20%.

type-invalid action:
0.

The degraded controller earns much more scalar reward.

It does so by:
maintaining a broad action radius
while weakening proof obligations.

The effect-typed controller gives up that reward
and materially improves:
epistemic validity,
false-promotion rate,
and severe tail.

LOCAL-SUBFAMILY-DRIFT RESULT

In the preregistered local-subfamily drift regime:

BLIND-GLOBAL

mean net:
1.8445.

1st percentile:
-53.6021.

false-promotion rate:
6.51%.

coverage:
29.16%.

PRICE-DEGRADED-GLOBAL

mean net:
-7.6756.

1st percentile:
-56.3433.

false-promotion:
0.38%.

GLOBAL-OR-ABSTAIN

mean net:
-5.9336.

1st percentile:
-23.3706.

false-promotion:
approximately 0%.

coverage:
5.83%.

EFFECT-TYPED

mean net:
-1.6595.

1st percentile:
-28.1614.

false-promotion:
0.63%.

coverage:
11.22%.

Thus subfamily contraction:

recovers more useful active value
than global abstention

while:

containing local drift
far better than blind global action.

It does not:
eliminate all subfamily false promotion.

That residual becomes important below.

LOW-PRICE COHERENT-FAMILY CHECK

COHERENT regime,
price 0.5.

EFFECT-TYPED:

family-wide action:
78.12%.

coverage:
82.57%.

mean net:
99.08.

Thus:
the strong global proof does not eliminate broad action
when evidence is cheap
and the family is coherent.

EVIDENCE-EFFICIENCY RESULT

Primary mean evidence:

EFFECT-TYPED:
18.16.

FULL-FAMILY:
92.80.

Therefore:
action-derived proof obligations do not collapse into full-family inspection.

SUDDEN PRICE-SHOCK STRESS

Active fraction:
90%.

Initial trigger evidence price:
0.5.

All evidence after trigger:
8.

20,000 worlds.

PRICE-DEGRADED-GLOBAL

mean net:
90.0958.

1st percentile:
-62.4760.

mean evidence:
8.4916.

coverage:
63.74%.

false-promotion:
1.03%.

family-wide action:
63.04%.

proof weakening:
92.56%.

type-invalid action:
63.04%.

EFFECT-TYPED

mean net:
-10.8499.

1st percentile:
-16.1497.

mean evidence:
1.0176.

family-wide action:
0%.

subfamily:
0.14%.

local:
99.86%.

proof weakening:
0.

type-invalid action:
0.

GLOBAL-OR-ABSTAIN

mean net:
-10.8299.

1st percentile:
-16.0641.

family-wide:
0%.

abstention:
92.56%.

PRICE-SHOCK INTERPRETATION

The effect system responds to a sudden compute shock by:

COLLAPSING
ACTION RADIUS

almost entirely to:
LOCAL.

The degraded controller responds by:

KEEPING
GLOBAL ACTION

and:

SELLING
PROOF QUALITY.

This creates a sharp scalar-reward difference.

That difference is real.

H141 does not hide it.

The claimed architectural principle is:

when validity is non-negotiable,
high resource pressure should degrade:

SCOPE

before:

EPISTEMIC CONTRACT.

SUBFAMILY-TOPOLOGY ROBUSTNESS

A targeted label-quality sweep tested:

0% label noise;
10%;
25%.

Operating point:

active fraction 60%.
evidence price 2.

EFFECT-TYPED

0% label noise:

mean net:
23.5891.

1st percentile:
-22.3928.

false-promotion:
0.33%.

coverage:
63.64%.

10% label noise:

mean net:
22.9694.

1st percentile:
-23.3892.

false-promotion:
0.73%.

coverage:
62.93%.

25% label noise:

mean net:
22.5457.

1st percentile:
-24.0978.

false-promotion:
0.96%.

coverage:
61.63%.

TOPOLOGY-QUALITY LIMIT

Scope contraction assumes:

THE SUBFAMILY
IS A MEANINGFUL
ACTION BOUNDARY.

As subfamily labels become noisy:

- false promotion rises;
- coverage falls;
- severe tail worsens.

The effect system remains type-valid
with respect to the declared subfamily.

But:
the declared subfamily itself
can be a poor representation of causal structure.

This is analogous to H140's action-obligation limit one level deeper.

A valid certificate over:
THE WRONG PARTITION

can still support:
A POOR ACTION.

DECISION

AR-H141 is:

POSITIVE

for:

ACTION-DERIVED PROOF OBLIGATIONS
+
RESOURCE-DRIVEN ACTION-SCOPE CONTRACTION.

SUPPORTED

- proof requirements can be attached to actions rather than chosen opportunistically;
- compute price changes action radius without changing same-action proof quality;
- subfamily action recovers value that global-or-abstain loses in low/medium-price regions;
- effect-typed contraction improves severe-tail and false-promotion behavior relative to price-degraded global action in the medium/high-price region;
- coherent low-price families still support broad action;
- sudden price shock contracts almost completely to local action;
- no type-invalid or proof-weakened action is authorized by EFFECT-TYPED;
- evidence remains far below full-family audit.

LIMIT

ACTION SCOPE
IS ONLY AS GOOD AS
THE PARTITION
THAT DEFINES IT.

A typed:
SUBFAMILY ACTION

requires not only:
a certificate over members inside the named subfamily,

but confidence that:

THE SUBFAMILY BOUNDARY
IS ITSELF
THE RIGHT CAUSAL BOUNDARY.

NEXT HIGH-VALUE MOVE

AR-H142 — PROOF-BEARING TOPOLOGY / PARTITION-UNCERTAINTY FIREWALL AUDIT

Question:

CAN
THE ORGANISM
TREAT
ITS OWN
FAMILY / SUBFAMILY
BOUNDARIES

AS:
CHALLENGEABLE
EPISTEMIC OBJECTS?

Candidate principle:

DO NOT
CERTIFY
AN ACTION REGION

MORE STRONGLY
THAN
THE REGION'S
OWN BOUNDARY
IS JUSTIFIED.

Test:

A.
hard fixed subfamily labels;

B.
boundary-confidence tags;

C.
quarantine of uncertain boundary members;

D.
overlapping certificates for ambiguous members;

E.
recursive split when internal dissent clusters near a boundary;

F.
merge when adjacent subfamilies repeatedly co-move;

G.
price shock with topology uncertainty;

H.
adversarial/stale partition where hidden drift intentionally crosses the stored boundary.

Desired:

TOPOLOGY
SHOULD BE
PROOF-CARRYING,

not:
an unquestioned index.

Do not execute STAB-18-R1 during this lane.

EXECUTION PROVENANCE

evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_worlds_per_cell = 3000
primary_cells = 20
primary_total_worlds = 60000
primary_label_noise = 0.10
effect_mean_net = 22.8007
effect_p01 = -25.3605
effect_mean_evidence = 18.1562
effect_type_invalid = 0
effect_proof_weaken = 0
effect_global_rate_price_0_5 = 0.4338
effect_global_rate_price_8 = 0
effect_local_rate_price_0_5 = 0.3756
effect_local_rate_price_8 = 0.9999
effect_subfamily_rate_price_0_5 = 0.1907
effect_subfamily_rate_price_2 = 0.1310
degraded_mid_high_p01 = -54.4555
effect_mid_high_p01 = -30.6066
shock_degraded_type_invalid = 0.6304
shock_effect_type_invalid = 0
label_noise_0_effect_fpr = 0.0033
label_noise_25_effect_fpr = 0.0096
