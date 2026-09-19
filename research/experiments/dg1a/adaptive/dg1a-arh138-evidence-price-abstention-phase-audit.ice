TITLE: DG-1A-AR-H138 — Evidence-Price / Active-Value Sparsity / Abstention Phase-Transition Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh137-hidden-minority-abstention-audit.ice

PURPOSE

H137 established an information lower bound for hidden-minority detection, but its economic toy made broad auditing artificially attractive because every audited dormant member earned immediate resolution value.

H138 removes that artifact.

Question:

WHEN
ONLY A SMALL FRACTION
OF A DEBT FAMILY
IS CURRENTLY ACTIVE,

AND
FRESH EVIDENCE HAS
REAL COMPUTE / LATENCY / OPPORTUNITY COST,

where is the policy boundary between:

- immediate family broadcast;
- buy a statistical evidence certificate;
- local-only resolution;
- abstain / keep the family debt dormant?

BOUNDARY

Synthetic research only.

It does not:
- implement living or biological tissue;
- establish production prices;
- freeze a universal risk tolerance;
- execute or modify STAB-18-R1;
- spend canonical scientific execution.

EVIDENCE CLASS TARGET

SYNTHETIC
MEASURED_SANDBOX

PRIMARY HYPOTHESIS

Once audit cost and immediate resolution value are decoupled:

1. full-family auditing should cease to dominate in sparse/high-price regimes;
2. an economic phase transition should emerge:
   - low price / high active value -> certify or broadcast;
   - high price / low active value -> local-only or abstain;
3. a risk-aware choose-among-broadcast/certify/defer policy should improve downside risk relative to forced small-sample broadcast without universally purchasing the certificate.

PRIMARY ECOLOGY

3,000 worlds per primary price/activity working point.

Family size:
40 to 100.

Current active fraction:
5%, 10%, 20%, 40%, 80%.

Effective evidence price per audited member:
0.5, 1, 2, 4, 8 value units.

Effective evidence price includes:
- compute;
- latency;
- opportunity cost of consuming scarce audit capacity.

Family regimes:
- CLEAN: no incompatible hidden minority;
- HIDDEN-10: approximately 10% incompatible hidden minority;
- HIDDEN-20: approximately 20% incompatible hidden minority.

Primary regime prior:
CLEAN = 50%.
HIDDEN-10 = 35%.
HIDDEN-20 = 15%.

Minority identity is independent of:
- active status;
- member value;
- ordinary context coordinates.

Thus no free metadata shortcut exists in the primary ecology.

MEMBER STATE

Each member has:
- active/inactive state;
- positive value weight;
- majority/minority compatibility state.

At least one active trigger exists.

The trigger is audited first.

If it is incompatible with the stored family model:
do not broadcast the stored family model.

ACTIVE-VALUE DECOUPLING

Only ACTIVE members produce immediate task-resolution value.

Correct resolution of an active member:
+3.0 x value.

An audited inactive member:
produces no immediate resolution reward.

It still costs evidence price.

FALSE PROMOTION COST

If family broadcast reaches an incompatible ACTIVE member:
-5.0 x value.

If family broadcast reaches an incompatible INACTIVE member:
-0.5 x value
as deferred representation-debt damage.

UNRESOLVED ACTIVE CARRY

An active member left unresolved:
-0.15 x value.

Inactive unresolved members:
no immediate carry charge.

BROADCAST APPLICATION COST

Family-wide promotion:
-0.20 x N.

AUDIT SEMANTICS

An audited active member can be resolved locally using its fresh observation.

An audited inactive member supplies information only.

This is intentionally different from H137:
evidence purchase is not automatically productive work.

POLICIES

A — LOCAL-ONLY

Audit trigger only.
Resolve trigger locally.
Never broadcast.

B — FIXED-5 FORCED

Audit trigger plus random members to a total of 5.
If every audited member is compatible with the stored family model:
broadcast.
Otherwise:
no family broadcast.

C — FIXED-9 FORCED

Same with total 9.

D — CERTIFY-10

After trigger compatibility:
buy enough uniformly sampled evidence to make the exact hypergeometric miss probability for a hidden 10% minority <= 5%.

If any dissent appears:
no broadcast.

If the certificate completes with no dissent:
broadcast.

E — FULL-FAMILY

Audit every member.
Resolve active members locally.
Never incur false family promotion.

F — ECONOMIC RISK-AWARE CHOICE

Always audit the active trigger.

If trigger contradicts the stored family:
remain local.

If trigger is compatible:

Stage 1:
buy to 5 total canaries only if the best estimated family-wide action has positive value relative to staying local.

After five compatible observations:

estimate three actions:

1. BROADCAST NOW.
2. CERTIFY-10 THEN BROADCAST IF NO DISSENT.
3. DEFER FAMILY-WIDE INFERENCE.

The policy selects the highest estimated incremental value.

No action with estimated incremental value <= 0 is taken.

PRIMARY POLICY PRIOR

The risk-aware estimator assumes:

hidden-family prior q = 0.50.

Target hidden fraction:
10%.

After k compatible samples:

q_post =
q * P_miss(k)
/
[(1-q) + q * P_miss(k)].

This is a deliberately simple risk prior.
The HIDDEN-20 regime tests misspecification.

VALUE ESTIMATOR

Let:

A =
remaining unaudited active value mass.

D =
remaining unaudited inactive value mass.

f =
0.10 target hidden fraction.

p =
effective evidence price.

Clean broadcast gain relative to defer:

G_clean =
3.15 * A
-
0.20 * N.

The 3.15 includes:
+3.0 correct active resolution
plus:
0.15 avoided unresolved carry.

Expected hidden-family penalty relative to clean broadcast:

L_hidden =
8.0 * f * A
+
0.5 * f * D.

Thus:

G_hidden =
G_clean - L_hidden.

Immediate broadcast estimate:

EV_broadcast =
(1 - q_post) * G_clean
+
q_post * G_hidden.

CERTIFICATE ESTIMATOR

Let:

k_cert =
exact hypergeometric sample count needed for:
10% hidden minority,
P_miss <= 0.05.

Let:
extra = max(0, k_cert - k).

Let:
r =
P_miss(k_cert) / P_miss(k)
conditional probability that a target hidden family remains undetected after buying the certificate.

Approximate active-value mass resolved locally by the extra random audits:

audit_resolution_gain =
3.15 * A * extra / max(1, N - k).

Then:

EV_certify =
-extra * p
+
audit_resolution_gain
+
(1 - q_post) * G_clean
+
q_post * r * G_hidden.

If dissent is actually observed during certification:
broadcast is cancelled.

DEFER estimate:

EV_defer = 0.

PRE-STAGE-1 PURCHASE

Before buying from one trigger audit to five:

the policy computes the same three-action family opportunity approximately at k=1.

If:
max(EV_broadcast, EV_certify) <= cost of the four extra stage-1 canaries,
it stays LOCAL-ONLY.

This explicitly allows:
not buying even the first family probe.

PRIMARY METRICS

1. mean net value;
2. 10th percentile net;
3. 1st percentile net;
4. evidence audits/event;
5. weighted active coverage;
6. false-promotion rate;
7. hidden-minority miss/broadcast rate;
8. family-broadcast rate;
9. certificate-purchase rate;
10. local-only/defer rate;
11. full-family advantage/disadvantage;
12. policy-choice phase map by active fraction and evidence price.

PRIMARY ACCEPTANCE SHAPE

A genuine resource phase transition is supported if:

- FULL-FAMILY is not the best mean policy across the whole grid;
- risk-aware LOCAL/DEFER rate rises materially as evidence price increases at fixed activity;
- risk-aware LOCAL/DEFER rate falls materially as active fraction increases at fixed price;
- certificate purchases concentrate in intermediate regimes rather than occurring almost always;
- broadcast-now concentrates in high-active / low-price regimes;
- risk-aware mean evidence is materially below FULL-FAMILY evidence;
- risk-aware 1st-percentile net is better than FIXED-5 in high-price or high-hidden-risk cells;
- no single action dominates every price/activity cell.

FAILURE CONDITIONS

Treat H138 as mixed/negative if:

- full audit still dominates almost everywhere;
- risk-aware policy almost always certifies;
- risk-aware policy almost always broadcasts;
- risk-aware policy almost always defers;
- active sparsity fails to change evidence demand;
- evidence price fails to change action choice;
- the phase map is driven only by family size artifact.

ROBUSTNESS

Family size:
40, 70, 100.

Hidden prior used by policy:
0.25, 0.50, 0.75.

Target certification miss:
1%, 5%, 10%.

Deferred inactive false-promotion penalty:
0.25, 0.5, 1.0.

Active value distribution:
low variance,
primary variance,
high variance.

Additional stresses:

- active members concentrated inside hidden minority;
- active members concentrated outside hidden minority;
- one high-value active minority member;
- sudden evidence-price spike;
- audit budget contention between multiple candidate families.

INTERPRETATION GUARDRAIL

A positive result would support:

DORMANT FAMILY MEMORY
DOES NOT IMPLY
DORMANT FAMILY COMPUTE.

The organism may retain:
cheap debt-family state

while refusing to spend:
fresh audit capacity

until:
current active value
justifies the evidence price and tail risk.

FROZEN BEFORE EXECUTION

Ecology, economic scale, policies, risk-aware estimator, primary metrics, acceptance shape, and robustness dimensions above are fixed before execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = 294e34590c091553c8b3cad4f0b768ece070bcf0
