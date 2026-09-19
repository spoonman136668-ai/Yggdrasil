TITLE: DG-1A-AR-H64 — Self-Tuning Local Signal-Code Selection Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE LEARNED-CODE-SELECTION RESULT + ESTIMATOR-LAG LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh63-hybrid-field-pulse-signaling-audit.ice

PURPOSE
H63 established that:
- pulse signaling is efficient for sparse/urgent information;
- steady fields are efficient for chronic high-density persistent state;
- event rate alone is not sufficient to choose between them.

H64 asks:

CAN A LOCAL DEVELOPMENTAL RULE LEARN
HOW A SIGNAL SHOULD BE REPRESENTED

from its own recent communication statistics?

Candidate representations:

PULSE

FIELD

FIELD + URGENT DELTA PULSE.

BOUNDARY
This is synthetic.

It does not:
- freeze a production code-selection learner;
- freeze state bins;
- prove these three encodings are exhaustive;
- establish final communication prices;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

LOCAL OBSERVABLE STATISTICS
The learner does NOT receive semantic signal type.

It receives coarse local estimates of:

EVENT RATE

EVENT / STATE DURATION

FUNCTIONAL STAKE

URGENT FRACTION.

The state is binned into a compact local code-selection context.

No hidden regime label is supplied.

ACTIONS

PULSE

FIELD

FIELD + URGENT DELTA PULSE.

SYNTHETIC SIGNAL REGIMES

A — SPARSE SHORT URGENT

event rate:
0.10 / step.

duration:
3.

stake:
4.

urgent fraction:
0.80.

B — CHRONIC LONG

rate:
3.0 / step.

duration:
80.

stake:
1.

urgent:
0.10.

C — CHRONIC SHORT URGENT

rate:
2.5 / step.

duration:
5.

stake:
4.

urgent:
0.70.

D — SPARSE LONG

rate:
0.20 / step.

duration:
100.

stake:
1.5.

urgent:
0.20.

These labels are evaluation-only.

The learner sees only local statistics.

COMMUNICATION MODEL
Block size:
50 steps.

Normalized communication price:
0.08 per propagation unit.

FIELD

50 communication units per block.

Sudden-information latency:
3 steps.

Functional loss scales with:
latency / signal duration.

PULSE

one communication unit per event.

Concurrent pulses suffer:
collision / delivery degradation.

FIELD + DELTA PULSE

field carries background state.

Urgent events also emit pulses.

PRIMARY PER-REGIME ORACLE
Mean synthetic block losses.

REGIME A

PULSE:
0.98.

FIELD:
22.83.

OVERLAY:
8.52.

PULSE is overwhelmingly preferred.

REGIME B

PULSE:
76.48.

FIELD:
9.82.

OVERLAY:
10.53.

FIELD preferred.

REGIME C

PULSE:
202.89.

FIELD:
313.90.

OVERLAY:
170.92.

OVERLAY preferred in approximately:
83.7%
of realized blocks.

PULSE wins the remaining noisy subset.

REGIME D

PULSE:
1.58.

FIELD:
4.46.

OVERLAY:
4.53.

PULSE preferred in approximately:
99.9%
of blocks.

Thus all three codes have a useful region.

LEARNER
Local empirical action-value table.

Training:
180,000 synthetic communication blocks.

Training regimes change in segments of:
approximately 20..100 blocks.

Exploration:
12%.

Recent local-statistic estimator:
EMA weight 0.25.

The learner accumulates:
observed realized loss

for each:
local state
x
code choice.

It does not receive:
the oracle-best action label.

PRIMARY NONSTATIONARY EVALUATION
Sequence:

A
->
B
->
C
->
D
->
A.

250 blocks per regime segment.

20 matched evaluation streams.

LEARNED LOCAL CODE POLICY

mean total loss:
46,325.46.

EVENT-LEVEL ORACLE

45,246.10.

Learner / oracle ratio:
1.02384.

Thus the learned policy is only:

2.38%

above the realized event-level oracle.

Oracle-action match:
95.66%
of blocks.

PRIMARY POSITIVE
A compact local learner can recover nearly all of the value of manually choosing:

FIELD
vs
PULSE
vs
OVERLAY

without:
semantic signal-type labels.

This materially strengthens H63.

The communication code can itself be:
adaptive developmental state.

FIXED-CODE COMPARATORS
Same matched evaluation workload.

ALWAYS PULSE

mean loss:
70,766.48.

ALWAYS FIELD

93,510.06.

ALWAYS OVERLAY

50,736.86.

LEARNED

46,325.46.

Thus the learned local code selector improves on the best fixed code:

OVERLAY

by approximately:
8.7%.

It improves much more strongly over:
all pulse
and
all field.

PER-REGIME LEARNED LOSS

A SPARSE SHORT

learner:
0.9847 per block.

oracle:
0.9847.

Essentially exact.

B CHRONIC LONG

learner:
10.2736.

oracle:
9.8205.

C CHRONIC SHORT URGENT

learner:
171.4008.

oracle:
167.6185.

D SPARSE LONG

learner:
1.6580.

oracle:
1.5759.

The remaining gap is concentrated in:
boundary/noisy regimes

rather than:
grossly wrong code selection.

CODE-SWITCH LATENCY
100 fresh transition streams.

A -> B
pulse -> field.

mean stable switch latency:
6.72 blocks.

median:
7.

5th–95th percentile:
6..7.

B -> C
field -> overlay.

mean:
1.02 blocks.

median:
1.

C -> D
overlay -> pulse.

mean:
8.55.

median:
11.

5th–95th:
approximately 2..13.

D -> A
pulse -> pulse.

0 blocks.

PRIMARY ESTIMATOR-LAG RESULT
The learner does not need semantic change detection.

It switches because:
its local event statistics move into another value regime.

However:
EMA context estimation introduces real adaptation latency.

The slowest tested transition takes:
roughly 9 blocks on average.

Thus:

SELF-TUNING SIGNAL CODE
HAS THE SAME
STABILITY / PLASTICITY TRADEOFF

as other Yggdrasil adaptive state.

WHY H64 MATTERS
Communication representation is no longer necessarily:
a fixed architectural decision made by the developer.

A local process can potentially learn:

THIS INFORMATION SHOULD BE A FIELD.

THIS INFORMATION SHOULD BE A PULSE.

THIS INFORMATION NEEDS A FIELD PLUS FAST DELTAS.

This makes:
communication morphology

part of:
development.

RELATION TO H23-H24
H23-H24 established a generic typed meta-rule for:
trust
and
authority.

H64 suggests:
signal-code choice

can be another small typed state controlled by the same general machinery:

VALUE

+
RECENCY

+
RESOURCE PRICE

+
FIT / LOCAL STATISTICS.

No separate global network-protocol scheduler is required conceptually.

RELATION TO H56-H61
Yggdrasil now has adaptive state at several physical/computational layers:

RESOURCE AMOUNT

TRANSPORT CONDUCTANCE

DEMAND-EMITTER TRUST

SIGNAL REPRESENTATION.

Thus the organism is not only:
learning task state.

It is beginning to learn:
HOW ITS INTERNAL COMMUNICATION SHOULD EXIST.

GENERAL PRINCIPLE
DO NOT HARD-CODE
THE COMMUNICATION REPRESENTATION
IF LOCAL EXPERIENCE CAN PRICE IT.

But:

code switching itself has:
latency
and
state-estimation cost.

So:
representation should be reversible,
not twitchy.

DECISION
AR-H64 is POSITIVE WITH AN ESTIMATOR-LAG LIMIT.

Supported synthetically:

- local event statistics are sufficient to learn useful signal representation;
- field/pulse/overlay selection can be learned without semantic labels;
- the learned policy approaches event-level oracle performance;
- learned coding beats every fixed signaling code in the tested nonstationary workload;
- the code can switch after regime changes;
- local statistic estimation creates bounded adaptation lag.

Not demonstrated:

- distributed negotiation when neighboring cells prefer different codes;
- code inheritance across cell division;
- asynchronous switching while messages are in flight;
- learned pulse frequency / waveform;
- more than three signaling primitives;
- hardware-level communication savings.

NEXT CLEAN QUESTION
AR-H65 — PHASE / FREQUENCY MULTIPLEXED DEVELOPMENTAL SIGNALING

H62-H64 still assume:
different logical signals

are represented as:
different local fields
or
different pulse streams.

Question:

Can several developmental variables share ONE local pulse substrate
by encoding type/value in:

PULSE FREQUENCY

PHASE

or
INTER-PULSE INTERVAL?

Potential benefit:

fewer persistent state channels.

Potential failure:

- aliasing;
- phase collision;
- noise accumulation;
- frequency drift;
- one high-rate signal masking another;
- refractory interaction.

Compare:

A.
separate pulse channels;

B.
frequency-coded shared pulse channel;

C.
phase-coded multiplex;

D.
noisy relay timing;

E.
two nearby frequencies;

F.
birth/death of emitters.

Desired:

compact shared signaling substrate

without:
cross-signal semantic corruption.

This is deliberately exploratory.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
training_blocks = 180000
evaluation_blocks_per_stream = 1250
evaluation_streams = 20
oracle_action_match = 0.9566
learned_oracle_loss_ratio = 1.02384
