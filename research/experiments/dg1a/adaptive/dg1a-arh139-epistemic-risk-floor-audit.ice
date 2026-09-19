TITLE: DG-1A-AR-H139 — Non-Negotiable Epistemic Risk Floor / Compute-Shock Invariance Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh138-evidence-price-abstention-phase-audit.ice

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
