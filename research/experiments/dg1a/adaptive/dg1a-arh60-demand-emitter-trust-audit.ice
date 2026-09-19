TITLE: DG-1A-AR-H60 — Demand-Emitter Trust / False-Sink Retirement and Recovery Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE DUAL-TIMESCALE EMITTER-TRUST RESULT + REAUDIT TRADEOFF
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh59-target-free-demand-field-stigmergy-audit.ice

PURPOSE
H59 showed that:
- target-free demand fields can route resource locally;
- false demand should not train slow vasculature unless delivery has functional consequence.

But even if false demand cannot rewrite morphology,
resource can still be wasted following the false ephemeral field.

H60 asks:

CAN A DEMAND EMITTER ITSELF ACQUIRE
LOCAL REVERSIBLE ROUTING TRUST

from whether delivered resource produces useful uptake / consequence?

The desired behavior is:

repeated false sink
->
lose current routing authority.

temporarily failed sink
->
suppress quickly
but recover later.

rare high-value sink
->
must not be retired merely because it is infrequent.

BOUNDARY
This is synthetic.

It does not:
- freeze a production emitter-trust formula;
- define real Yggdrasil demand identities;
- freeze audit probability;
- solve correlated false consequence;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

EMITTER POPULATION
Five anonymous local demand emitters.

The policy receives:
source/provenance identity
+
local demand stake/value.

It does NOT receive:
semantic class labels.

E0 — COMMON VALID

request probability:
0.35 per step.

functional uptake probability:
0.90.

stake:
1.

E1 — CHRONIC FALSE

request:
0.35.

uptake:
0.05.

stake:
1.

E2 — TEMPORARILY FAILING / RECOVERING

request:
0.25.

stake:
2.

uptake:

steps 0..499:
0.90.

500..849:
0.05.

850..1499:
0.90.

No failure/recovery label is supplied.

E3 — RARE CRITICAL

request:
0.03.

uptake:
0.95.

stake:
10.

E4 — FREQUENT LOW-VALIDITY

request:
0.22.

uptake:
0.02.

stake:
3.

RESOURCE COST
Serving one emitter request costs:

0.25 synthetic resource units.

Only one emitter can receive the focused resource allocation per step.

If no emitter has positive estimated value:
the controller may abstain.

SIMULATION
1500 steps.

300 matched synthetic streams.

POLICIES

RANDOM ACTIVE EMITTER

RECENCY / FREQUENCY ONLY
Prefer emitters that request frequently,
weighted by current stake.

No functional uptake trust.

CUMULATIVE SUCCESS TRUST
Beta-style cumulative success estimate per emitter.

Score:

success trust
*
stake
-
resource cost.

RECENCY SUCCESS TRUST
Fast EMA of functional uptake.

No slow retained credibility.

DUAL-TIMESCALE TRUST + SPARSE REAUDIT

Each emitter stores:

FAST EXPRESSION TRUST

and

SLOW RETAINED CREDIBILITY.

Primary:

fast update:
0.15.

slow update:
0.01.

Normal routing authority uses:
fast trust.

If fast trust has suppressed an emitter
but
slow credibility remains positive,
the emitter receives a sparse:

15% re-audit opportunity

when no currently trusted request deserves the resource.

This is analogous to:
stored capability
vs
current authority.

RANDOM RESULT

mean functional reward:
614.88.

mean regret vs latent expected-value oracle:
502.30.

fraction of served requests that are truly negative-value:
52.23%.

rare-critical service when active:
55.72%.

FREQUENCY-ONLY RESULT

reward:
541.82.

regret:
569.05.

negative-value service:
56.37%.

rare-critical service:
35.26%.

PRIMARY FREQUENCY NEGATIVE
Reuse frequency is not a valid demand-trust signal.

The rare-critical sink is strongly under-served
despite being the highest-value request when it appears.

Frequent false sinks receive excessive routing authority.

Thus:

HOW OFTEN A SINK ASKS
IS NOT
HOW MUCH RESOURCE IT DESERVES.

CUMULATIVE SUCCESS TRUST

reward:
1067.79.

regret:
49.98.

negative-value service:
14.32%.

rare-critical service:
98.80%.

PRIMARY CUMULATIVE POSITIVE
Functional uptake history is highly informative.

Chronic false sinks lose most routing authority.

Rare high-value demand is retained.

But cumulative trust has a severe nonstationary weakness.

TEMPORARY-FAILURE WINDOW
E2 service while its true uptake collapses:

95.72%
of active E2 requests.

Cumulative history remains dominated by the old valid period.

Thus:

A FORMERLY GOOD SINK
CAN RETAIN OBSOLETE AUTHORITY.

After E2 recovers:

service:
95.96%.

Cumulative trust remembers useful history well,
but suppresses failure poorly.

RECENCY SUCCESS TRUST

reward:
1012.20.

regret:
102.38.

negative-value service:
10.95%.

rare-critical service:
98.83%.

E2 service during failure:
34.33%.

E2 service after recovery:
62.55%.

PRIMARY RECENCY TRADEOFF
Fast trust suppresses the failed emitter much better.

But:
once strongly suppressed,
the recovering emitter may receive too little evidence to prove it is useful again.

Thus:

FAST SUPPRESSION
CAN CREATE
RECOVERY STARVATION.

DUAL-TIMESCALE + SPARSE REAUDIT
Primary audit probability:

15%.

reward:
1069.01.

regret:
42.61.

negative-value service:
12.29%.

rare-critical service:
99.62%.

E2 service during failure:
24.96%.

E2 service after recovery:
88.32%.

PRIMARY DUAL-TIMESCALE POSITIVE
The dual-state policy combines the useful parts of:
cumulative memory
and
fast recency.

Compared with cumulative trust:

failed-emitter service falls from:
95.72%
to
24.96%.

Yet after the emitter becomes useful again,
service recovers to:
88.32%.

Compared with simple recency:

recovery rises from:
62.55%
to
88.32%.

Rare-critical service remains:
approximately 99.6%.

This is a strong synthetic result.

REAUDIT TRADEOFF
Audit probability sweep.

5% REAUDIT

reward:
1048.24.

negative-value service:
8.06%.

failure-window E2 service:
20.08%.

post-recovery E2:
74.68%.

10%

reward:
1066.38.

negative-value service:
10.21%.

failure:
22.28%.

recovery:
85.05%.

15%

reward:
1069.01.

negative:
12.29%.

failure:
24.96%.

recovery:
88.32%.

25%

reward:
1071.76.

negative:
16.11%.

failure:
30.14%.

recovery:
91.81%.

PRIMARY REAUDIT PRINCIPLE
More re-audit:

improves recovery

but

spends more resource on:
currently bad emitters.

Therefore:
re-audit is another value-of-information problem.

The primary 15% point is not frozen.

RARE-CRITICAL RESULT
The rare-critical sink requests resource only:

3%
of steps.

Frequency-based control serves it only:
35.3%
of the time it is active.

Dual functional trust serves it:
99.6%.

Thus:

INFREQUENCY
MUST NOT BE CONFUSED WITH
LOW EXPECTED FUTURE VALUE.

This directly echoes H34 dormant-lineage retirement.

INACTIVITY IS NOT NEGATIVE EVIDENCE
The successful dual policy does NOT decay emitter credibility merely because:
the sink has been quiet.

Trust changes primarily from:
observed functional consequence.

This is important for:
rare but critical functions.

However:
very long inactivity may make causal topology stale.

Therefore a future representation should retain:

SLOW CREDIBILITY

separately from:

CURRENT FRESHNESS.

Do not implement:
silence
as
failure.

CURRENT DEMAND-EMITTER STATE
A local demand source now plausibly carries:

PROVENANCE / SOURCE ID

+

FAST EXPRESSION TRUST

+

SLOW FUNCTIONAL CREDIBILITY

+

FRESHNESS / LAST VALIDATION AGE

+

FUNCTIONAL STAKE

+

RESOURCE COST

+

REAUDIT / ELIGIBILITY STATE.

This uses the same compact typed-meta-state principles from H23-H24.

RELATION TO H6
H6 separated:

stored inherited prior

from

current expression trust.

H60 finds the same architecture for:
demand sources.

SINK CREDIBILITY
can remain stored

while

CURRENT ROUTING AUTHORITY
is suppressed.

This makes recovery possible without:
trusting stale behavior continuously.

RELATION TO S9
S9 showed:
control trust must be reversible.

H60:
demand routing trust must also be reversible.

A once-valid emitter can fail.

A once-failed emitter can recover.

Source identity should not permanently encode:
good
or
bad.

RELATION TO H34
H34 showed:
rare high-value dormant lineages should not be pruned by frequency alone.

H60 shows:
rare high-value demand should not lose resource authority by frequency alone.

Expected functional value matters.

CURRENT TARGET-FREE RESOURCE LOOP
DEMAND EMITTER

->

EMITTER TRUST / STAKE

->

EPHEMERAL LOCAL DEMAND FIELD

->

CONSERVED RESOURCE FLOW

->

FUNCTIONAL UPTAKE CONSEQUENCE

->

FAST ROUTING-TRUST UPDATE

+

SLOW CREDIBILITY UPDATE

+

OPTIONAL SLOW VASCULATURE REINFORCEMENT.

This is now a surprisingly coherent developmental resource-control loop.

GENERAL PRINCIPLE
SEPARATE:

IS THIS CAPABILITY / SINK HISTORICALLY REAL?

from

SHOULD I ROUTE RESOURCE TO IT RIGHT NOW?

Then preserve:
a small audit path

so:
suppressed capability can prove itself again.

DECISION
AR-H60 is POSITIVE.

Supported synthetically:

- demand-source trust should be consequence-based rather than frequency-based;
- chronic false sinks can lose current routing authority;
- rare high-value sinks remain serviceable despite low frequency;
- cumulative trust adapts too slowly to emitter failure;
- pure fast trust can make recovery difficult;
- fast expression trust + slow credibility + sparse re-audit produces a strong stability/plasticity compromise;
- re-audit itself has a resource-cost tradeoff.

Not demonstrated:

- real Yggdrasil functional uptake signal;
- emitter identity under cell birth/death;
- distributed trust gossip between resource sources;
- colluding false sinks sharing consequence confounds;
- optimal re-audit policy;
- freshness handling after very long inactivity.

CLEAN SCIENTIFIC PAUSE
H56-H60 materially extend the architecture beyond ordinary scheduler metaphors:

H56:
hard active capacity can be enforced by conserved mobile activation credits.

H57:
high-frequency fungible flow can use conservative local fields rather than per-transfer history.

H58:
resource transport morphology can adapt through reversible directed conductance memory.

H59:
target-free diffusive demand fields can route resource locally,
and transport memory must be consequence-gated.

H60:
demand emitters themselves can carry reversible functional trust.

Together they suggest a software developmental metabolism:

LOCAL DEMAND

+
CONSERVATIVE RESOURCE FIELD

+
ADAPTIVE VASCULATURE

+
FUNCTIONAL UPTAKE CREDIT

+
DUAL-TIMESCALE SOURCE TRUST.

NEXT HIGH-VALUE MOVE
AR-H61 — FULL DEVELOPMENTAL METABOLISM LOOP / FIELD-TRUST COUPLING

Question:

What happens when all H56-H60 pieces operate simultaneously?

Integrate:

- conserved activation/resource field;
- diffusive target-free demand;
- directed decaying vasculature;
- emitter trust;
- false sinks;
- moving damage;
- rare critical demand;
- cell death/regeneration.

Primary risks:

- positive feedback:
trusted sink
-> more flow
-> more vasculature
-> more flow
-> monopolization;

- false-sink lock-in;

- rare-sink starvation;

- transport-memory hysteresis;

- coupled oscillation between emitter trust and conductance;

- resource trapped by topology change.

This should be the first end-to-end synthetic:
DEVELOPMENTAL METABOLISM
integration experiment.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
stream_steps = 1500
primary_matched_streams = 300
primary_fast_trust_alpha = 0.15
primary_slow_credibility_alpha = 0.01
primary_reaudit_probability = 0.15
