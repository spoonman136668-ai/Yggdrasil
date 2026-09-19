TITLE: DG-1A-AR-H142 — Epistemic Contract Lifetime / Context-Drift Expiration Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh141-dual-gate-typed-epistemics-audit.ice
PARENT_RESULT_COMMIT: 87853b1304bb26dd5425264fe51a3eb35dfc9496

PURPOSE

H139-H141 established:

- typed epistemic contracts;
- fixed evidence semantics;
- resource admission after contract definition;
- abstention instead of silent evidence weakening.

Those experiments are one-shot.

A developmental organism is not one-shot.

It must:
- hibernate;
- retain dormant family memory;
- re-enter changed contexts;
- survive role changes;
- survive lineage changes;
- reuse old evidence when still valid;
- invalidate old evidence when the world has changed enough.

H142 asks:

ONCE
A FAMILY CLAIM
HAS BEEN
VALIDLY CERTIFIED,

HOW LONG
SHOULD
THAT CERTIFICATE
REMAIN USABLE?

The target failure is:

IMMORTAL CONFIDENCE.

A certificate that was once valid
must not remain valid forever
merely because it is stored.

BOUNDARY

Synthetic research only.

No living tissue.
No production lifetime threshold.
No deployment.
No STAB-18-R1 execution or modification.
No canonical scientific execution.

CLAIM CLASS

Primary cached claim:

SAFE_AGAINST_UNMARKED_MINORITY(
    minimum_fraction = 10%,
    miss_probability <= 5%,
    trigger_not_counted_as_uniform_sample
)

Full recertification uses the H141 trigger-excluded contract.

RESOURCE ADMISSION

When a policy decides that full recertification is required:

use the H141 DUAL-GATE resource rule.

If the fixed contract has positive estimated value:

BUY IT.

Otherwise:

ABSTAIN.

Do not:
reuse an expired contract
simply because recertification is expensive.

PRIMARY TEMPORAL ECOLOGY

Independent family episodes:

2,000.

Horizon:

250 time steps.

Primary seed:

20260919142.

Family size:

uniform integer 40..100.

Static member values:

lognormal,
sigma 0.60,
mean approximately 1.

Initial state:

family model valid.

Initial 10%-minority / 5%-miss certificate:

valid at t = 0.

Initial certificate cost is common to all policies
and excluded from comparative scoring.

CONTEXT

Two-dimensional observable context.

Ordinary per-step drift:

Normal(0, 0.03)
per dimension.

Context shock probability:

0.03 per step.

Shock increment:

Normal(0, 0.35)
per dimension.

ROLE EVENT

Observable role-switch event probability:

0.04 per step.

LINEAGE EVENT

Observable lineage-change event probability:

0.015 per step.

HIDDEN DRIFT BIRTH

When no hidden incompatible subgroup is present:

a new hidden subgroup may emerge.

Primary birth probability:

p_birth =
clip(
    0.001
    +
    0.08 * context_step_norm
    +
    0.06 * role_event
    +
    0.14 * lineage_event
    +
    0.10 * context_shock,
    0,
    0.40
).

If a hidden subgroup is born:

10% subgroup:
70%.

20% subgroup:
30%.

Minority size:

ceil(f_hidden * N).

Minority membership:

uniform without replacement.

A hidden subgroup persists until:
detected and repaired.

ACTIVATION

Active-use event probability:

0.35 per time step.

If inactive:

no task-resolution value exists.

No primary policy may spend member-audit compute
merely because the family is dormant.

This directly tests:

DORMANT MEMORY
WITHOUT
DORMANT COMPUTE.

On active-use events:

active fraction:

10%:
50%.

40%:
35%.

80%:
15%.

At least one active trigger exists.

Trigger:
uniform among active members.

Evidence price:
1.

REPAIR

If hidden drift is detected by:
trigger,
canary,
or full certificate,

family-wide broadcast is cancelled for that event.

A synthetic repair cost:

8 value units

is charged.

The hidden subgroup is cleared
before the next time step.

The family model is treated as repaired.

A successful full recertification after repair
creates a new certificate anchor.

CACHED-CERTIFICATE REUSE

If a cached certificate is considered valid:

audit active trigger.

If trigger contradicts:
detect + repair.

If trigger is compatible:
reuse cached family claim
and broadcast.

Thus even a stale certificate can occasionally be challenged by active experience.

POLICIES

A — NEVER-EXPIRE

Cached certificate never expires.

Only direct trigger contradiction can challenge it.

No periodic full recertification.

B — FIXED-TTL-20

Certificate expires after:

20 time steps

since last full certification.

On the next active-use event after expiration:

apply H141 resource admission
to the fixed 10% / 5% contract.

If purchase denied:

ABSTAIN.

C — CONTEXT-DISTANCE-0.50

Certificate expires when:

Euclidean distance
between current context
and full-certification anchor

>= 0.50.

On next active use:

dual-gate recertify or abstain.

D — HAZARD-DEBT-10

Maintain cheap observable hazard debt.

At each time step when hidden status is not directly known:

survival =
survival * (1 - p_birth).

hazard_debt =
1 - survival.

Certificate expires when:

hazard_debt >= 0.10.

On next active use:

dual-gate recertify or abstain.

A successful full recertification:

resets hazard debt to 0
and
moves the context anchor.

E — CHALLENGE-ONLY

No time,
context,
or hazard expiration.

Trigger contradiction:
repair.

Otherwise:
reuse.

This isolates:
experience-only correction.

F — NAIVE-CANARY-RESET

Use HAZARD-DEBT accumulation.

When:

hazard_debt >= 0.10

on an active-use event:

audit:
trigger
+
4 fresh random non-trigger canaries.

If any dissent:

repair.

If all five are compatible:

RESET hazard debt to 0

and
treat the strong 10% / 5% cached contract
as renewed.

No full certificate.

This intentionally tests:

WEAK EVIDENCE
RENEWING
A STRONG CLAIM.

G — CANARY-CHALLENGE + HARD EXPIRATION

Hazard debt accumulates.

At:

hazard_debt >= 0.05

on active use:

audit trigger
+
4 fresh random non-trigger canaries.

If dissent:
repair.

Compatible canaries:
DO NOT
renew the full typed contract.

At:

hazard_debt >= 0.10:

full H141 dual-gate recertification
or
abstention.

The canary layer may:

CHALLENGE.

It may not:

RENEW
THE STRONGER CLAIM.

H — FULL-CERT-EVERY-ACTIVE

On every active-use event after a compatible trigger:

buy the full trigger-excluded 10% / 5% certificate.

No economic gate.

Reference high-evidence policy.

PRIMARY SCORING

Use H141/H140 event economics.

Active correct resolution:
+3 x value.

Active false promotion:
-5 x value.

Inactive false promotion:
-0.5 x value.

Unresolved active carry:
-0.15 x value.

Broadcast:
-0.20 x N.

Evidence audit:
-1 each.

Repair:
-8 value units.

Inactive time step:
no immediate task reward.

PRIMARY METRICS

1.
mean net value per active-use event.

2.
total net per episode.

3.
member audits per time step.

4.
member audits per active-use event.

5.
active weighted coverage.

6.
false-broadcast rate.

7.
false broadcast on FIRST ACTIVE USE after hidden-drift birth.

8.
mean detection latency after hidden-drift birth.

9.
95th percentile detection latency.

10.
full recertification rate.

11.
canary audit rate.

12.
epistemic abstention rate.

13.
stale-certificate reuse rate.

14.
hidden-drift births repaired.

15.
dormant audit rate.

16.
mean certificate age at reuse.

PRIMARY ACCEPTANCE SHAPE

Hazard-aware certificate lifetime is supported if:

- NEVER-EXPIRE and CHALLENGE-ONLY accumulate materially more stale false broadcast than expiring policies;
- HAZARD-DEBT uses less evidence than FULL-CERT-EVERY-ACTIVE;
- HAZARD-DEBT detects hidden drift faster than FIXED-TTL-20 after shocks or lineage events;
- HAZARD-DEBT spends little or no member-audit compute during inactive periods;
- resource denial after expiration produces abstention, not stale reuse;
- NAIVE-CANARY-RESET shows higher stale false broadcast than hard-expiration HAZARD-DEBT;
- CANARY-CHALLENGE can improve detection latency without allowing weak canaries to renew the strong contract;
- CONTEXT-DISTANCE reacts well to geometric shocks but is weaker than hazard debt when role/lineage changes occur without large context movement;
- no policy requires continuous full recertification.

FAILURE CONDITIONS

Treat H142 as mixed/negative if:

- hazard debt provides no advantage over fixed TTL;
- context or hazard expiry creates nearly continuous recertification;
- dormant periods still consume substantial member-audit evidence;
- canary challenge provides no useful early-warning value;
- hazard policy remains highly stale after lineage/role changes;
- resource admission causes expired-contract reuse instead of abstention;
- full-every-active remains economically dominant despite evidence cost.

ROBUSTNESS

Repeat targeted sweeps over:

hazard expiration:
5%, 10%, 20%.

TTL:
10, 20, 40.

context distance:
0.25, 0.50, 1.00.

active-use probability:
0.10, 0.35, 0.70.

evidence price:
0.5, 1, 4.

drift ecology:
quiet,
primary,
shock-heavy,
lineage-heavy.

INTERPRETATION GUARDRAIL

H142 does not claim:

confidence literally has a universal clock-based expiration.

It tests:

whether old evidence must remain challengeable
as the conditions under which it was acquired diverge from the present.

The candidate architectural principle is:

A CERTIFICATE
IS A TEMPORAL OBJECT.

It has:

- scope;
- evidence provenance;
- context anchor;
- age;
- hazard debt;
- challenge history;
- renewal rules.

PARTIAL EVIDENCE
MAY
CHALLENGE
A STRONG CLAIM.

It should not automatically:

RENEW
A STRONGER CLAIM.

FROZEN BEFORE EXECUTION

Generator,
seed,
temporal hazard,
activation process,
claim class,
resource admission,
repair semantics,
policies,
thresholds,
metrics,
acceptance shape,
and robustness dimensions above are fixed before execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = 87853b1304bb26dd5425264fe51a3eb35dfc9496
primary_seed = 20260919142
episodes = 2000
horizon = 250
claim_fraction = 0.10
claim_delta = 0.05
hazard_expiry = 0.10
canary_challenge = 0.05
fixed_ttl = 20
context_expiry = 0.50
