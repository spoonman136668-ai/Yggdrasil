TITLE: DG-1A-AR-H141 — Epistemic Effect System / Action-Derived Proof-Obligation Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh140-typed-epistemic-certificate-audit.ice

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
