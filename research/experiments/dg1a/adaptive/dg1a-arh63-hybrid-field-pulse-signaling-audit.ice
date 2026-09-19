TITLE: DG-1A-AR-H63 — Hybrid Field / Pulse Signaling Specialization Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE TYPED-HYBRID RESULT + EVENT-RATE-ONLY SWITCH NEGATIVE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh62-pulsed-wave-developmental-coordination-audit.ice

PURPOSE
H62 showed that event-triggered waves can carry sparse developmental information much more cheaply than continuously maintained steady fields,
but also exposed:
- refractory denial-of-service;
- pulse collision;
- source-starvation risk.

H63 asks:

SHOULD YGGDRASIL USE ONE LOCAL SIGNALING SUBSTRATE FOR EVERYTHING?

Or should communication representation specialize by:
- timescale;
- event density;
- signal persistence;
- latency tolerance?

BOUNDARY
This is synthetic.

It does not:
- freeze a production signal taxonomy;
- freeze event-rate thresholds;
- prove fields/pulses are the final primitives;
- establish final communication costs;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SPATIAL COMMUNICATION SCALE
Reference grid:
20 x 20.

Approximate nearest-neighbor propagation edge operations per whole-tissue local round:

1520.

STREAM
10,000 synthetic time steps.

Four signal families.

HOMEOSTATIC / RESOURCE CONTEXT

30 local emitters.

per-emitter update probability:
0.08 per step.

signal persistence:
long.

This is a chronic, high-density family.

DAMAGE

40 emitters.

baseline event probability:
0.002 per emitter-step.

during steps:
3000..4999

event probability rises to:
0.04.

This creates a temporary damage storm.

Typical signal duration:
10 steps.

WAKE / RECRUITMENT

80 emitters.

event probability:
0.001.

duration:
2.

CONTEXT CHANGE

10 emitters.

event probability:
0.0005.

duration:
300.

SIGNAL CHANNEL MODEL

STEADY FIELD

one local field-update round per step.

communication:
1520 edge operations per active signal family per step.

Sudden event information incurs approximately:
3-step effective field-formation latency.

Effective captured event value:

max(
0,
(duration - 3) / duration
).

PULSE / WAVE

one tissue-scale propagation per event.

communication:
1520 edge operations per event.

Primary clean pulse delivery:
98.5%.

Concurrent event collision reduces delivery probability gradually.

This is a synthetic communication abstraction,
not a production implementation.

POLICIES

ALL FIELD

all four signal families remain continuously field-coded.

ALL PULSE

every event is represented by a wave.

FIXED TYPED HYBRID

HOMEOSTATIC / RESOURCE CONTEXT:
field.

DAMAGE:
pulse.

WAKE:
pulse.

CONTEXT CHANGE:
pulse.

RATE-ADAPTIVE FIELD SWITCH

same as fixed hybrid,
but damage automatically changes:

PULSE
->
FIELD

when recent aggregate damage-event density exceeds:
0.65 events per step,

and returns to pulse below:
0.25.

FIELD + URGENT-PULSE OVERLAY

same event-rate switch,
but while damage is field-coded:

the field carries background damage state

and
30% high-urgency damage events also emit a pulse.

PRIMARY RESULTS

ALL FIELD

communication:
60.800 million local edge operations.

captured weighted signal value:
33,463.96.

fraction of ideal signal value captured:
79.53%.

PRIMARY ALL-FIELD NEGATIVE
Continuously maintaining fields for:
rare wake
and
rare context events

spends enormous communication bandwidth.

Short wake signals also lose most useful timing under the tested 3-step field latency.

ALL PULSE

communication:
43.756 million operations.

captured value:
38,934.36.

capture:
92.53%.

Pulse coding improves both:
communication
and
signal capture

relative to all-field in this event mix.

However:
the chronic homeostatic family alone consumes:

36.535 million pulse operations.

Thus:
a high-density persistent process creates a pulse storm.

FIXED TYPED HYBRID

communication:
22.422 million operations.

captured value:
39,676.25.

capture:
94.29%.

PRIMARY HYBRID POSITIVE
The typed hybrid dominates both one-channel extremes in the tested workload.

Compared with:

ALL FIELD

communication falls by:
approximately 63.1%.

captured signal value increases by:
approximately 18.6%.

Compared with:

ALL PULSE

communication falls by:
approximately 48.8%.

captured signal value also increases slightly.

The reason is simple:

chronic persistent homeostatic state is cheaper as:
one shared field,

while:
sparse urgent events

are cheaper and temporally sharper as:
pulses.

RATE-ADAPTIVE FIELD SWITCH

communication:
20.689 million operations.

captured value:
36,730.92.

capture:
87.29%.

The mode changes:
2 times

around the temporary damage storm.

PRIMARY RATE-ONLY NEGATIVE
Switching to:
FIELD

based only on:
HIGH EVENT RATE

saves communication

but loses too much:
short-timescale damage information.

During the damage storm:
the signal is dense

but
still latency-sensitive.

Thus:

EVENT DENSITY
IS NOT ENOUGH
TO CHOOSE A SIGNAL CODE.

FIELD + URGENT-PULSE OVERLAY

communication:
22.113 million operations.

captured value:
37,820.08.

capture:
89.88%.

This recovers part of the damage information lost by the field-only switch,
but still underperforms the fixed typed hybrid on signal capture.

The communication saving relative to fixed hybrid is small:

22.42M
vs
22.11M.

Therefore the tested adaptive switch is not worth the fidelity loss.

CROSSOVER MAP
Signal representation was swept by:

aggregate event density

and

event duration.

Normalized communication:

FIELD:
1 whole-tissue update unit per step.

PULSE:
events_per_step units.

Tested event densities:

0.1
0.5
1
2
5 events / step.

Tested durations:

2
5
10
50
200 steps.

RESULT
At:

0.1
and
0.5 events/step

PULSE dominates:
lower communication
and
equal/higher temporal capture

for every tested duration.

At:
1 event/step

the two encodings enter:
a cost/fidelity tradeoff region.

At:
2 events/step

FIELD begins to dominate only for:
very long duration
approximately 200-step signals.

At:
5 events/step

FIELD dominates for:
50
and
200-step persistent signals,

but short:
2
5
10-step events

still remain:
latency/fidelity tradeoffs.

PRIMARY CODING PRINCIPLE
The relevant variable is closer to:

SPATIOTEMPORAL SIGNAL ENTROPY / EVENT DENSITY

PLUS

REQUIRED TEMPORAL PRECISION

than:
semantic signal type alone.

A high-rate signal can still deserve pulse coding
if timing precision is critical.

A low-rate long-lived signal can still deserve a cached event representation.

TYPE
should not become:
a permanent hardcoded communication law.

CURRENT WORKING SIGNAL ARCHITECTURE
SLOW / PERSISTENT / HIGH-DENSITY STATE

->
LOCAL FIELD.

SPARSE / URGENT / EVENT-LIKE STATE

->
PULSE / WAVE.

MIXED CASE

->
potential:
FIELD BASELINE
+
PULSE DELTAS.

But:
the tested damage overlay did not yet justify its added complexity.

RELATION TO H23
H23 established:

SHARE UPDATE FORM,
PRESERVE TYPED STATE.

H63 suggests the communication analogue:

SHARE LOCAL COMMUNICATION SUBSTRATES,
PRESERVE SIGNAL-TIMESCALE / FIDELITY REQUIREMENTS.

Do not force:
one signaling code
on every developmental variable.

RELATION TO H62
H62 showed:
event timing can encode spatial structure efficiently.

H63 adds:
that efficiency disappears when too many emitters pulse too often.

Thus:
waves are not universally superior to fields.

The useful architecture is:
heterogeneous signaling.

OUTSIDE-STATUS-QUO IMPLICATION
The developmental genome may not only specify:

WHAT STATE TO UPDATE.

It may also learn or encode:

HOW THAT STATE SHOULD BE COMMUNICATED.

A variable could exist as:
- continuous local field;
- sparse pulse;
- cached event;
- slow structural memory;

depending on:
its information statistics.

This is closer to:
communication-code specialization

than:
a conventional fixed neural message bus.

DECISION
AR-H63 is POSITIVE FOR TYPED HYBRID SIGNALING,
with a NEGATIVE for event-rate-only channel switching.

Supported synthetically:

- all-field communication wastes large bandwidth on sparse events;
- all-pulse communication wastes bandwidth on chronic high-density state;
- a typed field/pulse hybrid strongly reduces communication and improves signal capture;
- event density alone is insufficient for adaptive channel selection;
- duration / temporal precision materially changes the field-vs-pulse crossover;
- pulse-over-field overlay can recover some urgent detail but was not cost-effective at the tested point.

Not demonstrated:

- learned signal-code choice;
- local estimation of signal entropy/duration;
- asynchronous channel switching;
- signal-code inheritance;
- compression of multiple pulse families;
- real hardware communication cost.

NEXT CLEAN QUESTION
AR-H64 — SELF-TUNING SIGNAL REPRESENTATION / LOCAL CODE SELECTION

Question:

Can a local developmental rule learn whether a signal should be represented as:

FIELD

PULSE

or
FIELD + DELTA PULSE

from its own communication history?

Candidate local statistics:

- event rate;
- persistence / duration;
- temporal prediction error;
- urgency / consequence of latency;
- communication cost;
- neighboring redundancy.

Required stress:

- sparse -> chronic transition;
- chronic -> sparse transition;
- short events becoming persistent;
- false pulse storms;
- field inertia after rapid context shift.

Desired:

the communication code itself becomes:
reversible developmental state

rather than:
a manually assigned architecture constant.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
stream_steps = 10000
grid = 20x20
local_edge_ops_per_round = 1520
fixed_hybrid_ops = 22421520
fixed_hybrid_capture = 0.942899
