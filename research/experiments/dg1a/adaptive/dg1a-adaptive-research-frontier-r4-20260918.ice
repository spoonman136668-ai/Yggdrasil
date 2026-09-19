TITLE: DG-1A Adaptive-Rule Research Frontier R4 — Local Causal Credit + Ordered Distributed Context
DATE: 2026-09-18
STATUS: ACTIVE RESEARCH FRONTIER
TRACK: DG-1A / ADAPTIVE RULES
BRANCH: dg1a-ar
CANONICAL_P0_HEAD_UNCHANGED: b45703418a7097782a032a142665c4642c2945fa

PURPOSE
Seal the adaptive-rule research state after:

AR-U7
through
AR-U12

and:

AR-C1
through
AR-C2.

This file is a research-navigation record.

It does not alter canonical STAB-18-R1 authority.

R1 STATUS
STAB-18-R1 remains:
- frozen;
- unexecuted;
- scientifically prior;
- canonical seed-0 / 200-iteration run unspent.

No adaptive-rule result modifies or bypasses R1.

NEW UTILITY / CAUSAL-CREDIT CHAIN

AR-U7
dg1a-aru7-cheap-causal-credit-approximation-audit.ice

Question:
Can local causal credit approach a paired counterfactual without duplicating a full future trajectory?

Primary result at delay 16:

naive delayed consequence:
54.22% causal-sign accuracy

8 sparse signed action-tagged probes:
62.27%

8 tagged probes
+
local disturbance reference:
91.12%

full paired future:
96.05%

16 reference-assisted probes:
97.15%.

Moving-optimum adaptation:

reference-assisted K=16:
97.5% stable recovery
final absolute error 0.0307

full paired:
99.8%
0.0229.

Conclusion:
sparse action tags + local disturbance prediction can approximate expensive counterfactual credit.

AR-U8
dg1a-aru8-local-disturbance-reference-audit.ice

Core identifiability result:

A useful local control must be:

DISTURBANCE-COUPLED

but

ACTION-DECOUPLED.

Temporal self-prediction fails under genuinely new post-action nonstationarity.

A live local reference remains useful if it experiences the shared disturbance.

But when reference contamination reaches the same causal effect as the target:

causal-sign accuracy falls to approximately chance.

Therefore:
prediction quality != causal-control validity.

AR-U9
dg1a-aru9-local-matched-control-selection-audit.ice

Negative:

"pick the most correlated neighbor"
is rejected.

Primary synthetic neighborhood:

no reference:
60.22%

correlation-only:
58.81%

top-3 covariance/exposure composite:
62.79%.

The most correlated references had:
high environmental coupling
but
high action contamination.

Matched-control selection is itself a causal-identifiability problem.

AR-U10
dg1a-aru10-action-leakage-correction-poc.ice

Hardly projecting the disturbance model away from every action-correlated dimension failed.

Reason:
environment information
and
action exposure
can overlap physically.

Better mechanism:

estimate each local signal's action leakage with tagged microprobes

then subtract:

predicted action leakage

from:

observed reference response

before estimating shared disturbance.

Primary result:

no reference:
60.39%

best single reference:
80.02%

raw neighborhood mean:
84.51%

action-leakage-corrected neighborhood mean:
88.88%.

Reference loss degrades gracefully.

Key negative:
stale leakage correction can become harmful when coupling changes.

AR-U11
dg1a-aru11-action-leakage-recalibration-audit.ice

Sparse recalibration can repair changed action-to-neighborhood coupling.

Examples:

coupling disappears:
stale correction ~84.6%
periodic recalibration ~88.8%

coupling doubles:
stale ~84.6%
periodic ~88.8%

coupling triples:
stale ~74.4%
periodic ~88.8%.

Continuous probing adapts faster but costs more exploration.

Therefore calibration must carry:

value
+
freshness/confidence
+
recalibration path.

AR-U12
dg1a-aru12-event-triggered-recalibration-audit.ice

Event-triggered calibration uses naturally tagged action-response innovation as a confidence monitor.

If innovation exceeds a threshold:
launch a temporary calibration-probe burst.

Exploratory threshold:
0.026

Large coupling changes:
approximately 4..6 extra probes per cell

vs

periodic-8:
approximately 18 post-change

continuous:
approximately 70.

Stable no-change run:
mean extra probes:
0.7136 per cell over 120 episodes.

Conclusion:
diagnostic activity can become transient and demand-triggered.

This matches the broader Yggdrasil objective:

stable maintenance should be cheap;
unexpected change should temporarily recruit diagnostic/adaptive activity.

CURRENT CHEAP CAUSAL-CREDIT STACK

1.
sparse one-role action perturbation

2.
action identity / eligibility state

3.
local multi-signal disturbance estimate

4.
action-leakage estimate into that disturbance representation

5.
freshness/confidence on leakage calibration

6.
event-triggered recalibration

7.
delayed local consequence

8.
bounded role/sensitivity update.

No globally stored network weights change during organism lifetime.

NEW CONTEXT / COMMUNICATION CHAIN

AR-C1
dg1a-arc1-repeated-context-ordering-audit.ice

Binary freshness is insufficient for repeated seasonal switching.

Mode-only overwrite:
unsafe under stale messages.

Successor-only:
works if every transition is observed,
but a component that misses multiple transitions can become stranded.

Bounded serial epoch + half-range ordering:

0 <
(new-old) mod M
<
M/2

supports repeated switching and catch-up.

Split-organism test:
right component misses 3 context transitions.

successor-only:
0/12 reached 90% current context
final current fraction ~47.6%

serial M=16:
12/12 recovered
about 33..38 steps
100% final current context.

Hard bound:
serial lag must remain < M/2 epochs.

A bounded serial cannot order arbitrarily ancient packets.

AR-C2
dg1a-arc2-multisensor-context-consensus-audit.ice

Several noisy sensors + ordered relay.

Primary comparison:
4 sensors
p_detect=0.90
p_wrong=0.10
message dropout=50%.

LATEST-NEWEST-PACKET WINS:
67.71% switch success
18-step median latency
~9.96% wrong committed current-context fraction.

TWO-INDEPENDENT-SENSOR QUORUM:
95.83% switch success
30-step median
~1.01% wrong committed.

At p_wrong=0.25:

latest:
29.17% switch success
28.61% wrong committed

quorum:
82.29% switch success
5.58% wrong committed.

SENSOR DAMAGE:
with 2 surviving sensors:
quorum remains fail-safe but loses liveness on disagreements.

with 1 surviving sensor:
0% new-context commitment
0% wrong commitment.

KEY DISTRIBUTED-SYSTEMS RESULT

RELAYED COPIES OF THE SAME SENSOR EVIDENCE
ARE NOT
INDEPENDENT EVIDENCE.

Evidence aggregation must be idempotent / provenance-safe.

The synthetic bitmask is only a control implementation.

Final Yggdrasil need not use literal permanent sensor IDs.

CURRENT DECENTRALIZED CONTEXT STACK

multiple partially independent sensors

->
bounded serial ordering

->
provenance-safe evidence relay

->
semantic quorum/confidence

->
committed mode

->
shared-rule seasonal modulation.

CROSS-DOMAIN CONVERGENCE

Several independent research paths now point to the same design rules.

RULE 1 — SURPRISE SHOULD FIRST REDUCE CONFIDENCE
Not every prediction error should immediately change policy.

Seen in:
- injury inference;
- context disagreement;
- causal-calibration drift.

RULE 2 — COPIES ARE NOT REDUNDANCY
Useful reliability comes from partially independent causal evidence.

Seen in:
- injury cues;
- seasonal sensors;
- local role-credit cues;
- context consensus.

RULE 3 — RELEVANCE AND SEPARABILITY MUST COEXIST
Useful local signals should share the relevant cause,
but retain enough independent error/action structure for causal discrimination.

Seen in:
- injury representation;
- local disturbance controls;
- sensor consensus.

RULE 4 — ADAPTATION REQUIRES RETIREMENT
Useful specialization must be able to disappear when demand disappears.

Seen in:
- moving relay roles;
- stale action calibration;
- context freshness.

RULE 5 — MISSING / STALE != NEGATIVE
Absence of fresh evidence is not evidence that a function is useless or a previous calibration remains valid.

CURRENT TIMESCALE STACK

FASTEST
ordinary NCA state/update

FAST
soft functional role expression

MEDIUM
eligibility/action identity and local consequence memory

MEDIUM-SLOW
disturbance model / action-leakage calibration / confidence

SLOWER
future bounded heritable micro-genome

The timescale separation is emerging from measured causal-identifiability constraints,
not from aesthetic design preference.

LITERATURE ALIGNMENT

Current 2025-2026 local-learning literature supports continued investigation of:
- eligibility traces;
- cascading temporal traces;
- predictive coding/local prediction errors;
- fully local spatio-temporal credit;
- node perturbation / local policy-gradient ideas.

Relevant anchors already reviewed include:

Learning From the Past with Cascading Eligibility Traces
ICLR 2026

TESS:
A Scalable Temporally and Spatially Local Learning Rule for Spiking Neural Networks
IJCNN 2025
DOI:
10.1109/IJCNN64981.2025.11227652

Recent predictive-coding / fully local credit-assignment work.

These support mechanism plausibility only.
They are not Yggdrasil results.

WHAT IS NOW SUPPORTED SYNTHETICALLY

[yes]
shared rule + compact context

[yes]
context corruption map

[yes]
fast local context relay

[yes]
repeated ordered context switching

[yes]
multi-sensor semantic consensus

[yes]
soft role recovery

[yes]
utility-driven useful spatial specialization

[yes]
moving-demand role relocation

[yes]
multi-role coexistence

[yes]
bounded local perturb-and-observe adaptation

[yes]
delayed/confounded credit failure characterized

[yes]
cheap causal-credit approximation

[yes]
action-leakage correction

[yes]
freshness-aware recalibration

[yes]
event-triggered probe economy.

NOT SHOWN

[no]
real Yggdrasil emergent functional roles

[no]
real Yggdrasil local causal-credit representation

[no]
real NCA learning of these meta-rules

[no]
functional computational regeneration

[no]
developmental cognition

[no]
heritable useful micro-genome evolution.

NEXT PRIMARY FRONTIERS

AR-U13 — SHARED NOVELTY / CONFIDENCE STATE

Question:
Can one compact confidence representation distinguish:
- injury surprise;
- context uncertainty;
- causal-calibration uncertainty

without collapsing all surprise into one alarm?

The goal is mechanism compression.

AR-C3 — PROVENANCE COMPRESSION

Question:
Can independent-evidence counting remain idempotent without explicit permanent sensor IDs?

Test:
- compact source sketches;
- spatial sectors;
- randomized signatures;
- relay loops;
- collisions.

AR-U14 — REAL-YGGDRASIL SIGNAL MAPPING AUDIT

Before any functional-regeneration spend:
map synthetic variables onto observables that CURRENT Yggdrasil can actually produce.

Candidate mapping targets:
- local prediction residual;
- local temporal state delta;
- neighborhood covariance;
- existing hidden-channel diversity;
- action/update identity;
- local consequence proxy.

This should be diagnostic / non-gating first.

READINESS POSITION
The adaptive-rule research has moved beyond:
"can cells switch roles?"

The main remaining bridge is:

CAN CURRENT YGGDRASIL LATENT DYNAMICS SUPPLY
THE LOCAL INFORMATION VARIABLES
THAT THE SYNTHETIC META-RULES REQUIRE?

That should be answered before engineering explicit role registers or a real functional-regeneration experiment.

NEXT ACTION
AR-U13
or
AR-U14 signal-mapping diagnostic design.

Prefer AR-U14 if the goal is shortest path toward real Yggdrasil applicability.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = RESEARCH_FRONTIER_SUMMARY
canonical_scientific_execution = false
canonical_r1_execution_spent = false
