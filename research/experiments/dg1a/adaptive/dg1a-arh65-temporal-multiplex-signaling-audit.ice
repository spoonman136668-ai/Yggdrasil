TITLE: DG-1A-AR-H65 — Phase / Frequency Multiplexed Developmental Signaling Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX CONDITIONAL POSITIVE TEMPORAL-MULTIPLEX RESULT + PROVENANCE/CLOCK LIMITS
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh64-self-tuning-signal-code-audit.ice

PURPOSE
H62-H64 established that:
- pulses can efficiently encode sparse urgent signals;
- fields better serve some chronic state;
- local rules can learn which code to use.

H65 asks a more aggressive compression question:

CAN SEVERAL DEVELOPMENTAL SIGNALS SHARE ONE PULSE SUBSTRATE

by encoding identity/value in:
- pulse frequency;
- inter-pulse interval;
- phase?

Potential gain:
fewer persistent logical signal channels.

Potential failures:
- aliasing;
- collision;
- timing noise;
- phase drift;
- hidden global-clock dependence;
- source birth/death ambiguity.

BOUNDARY
This is synthetic.

It does not:
- freeze frequency codes;
- freeze phase periods;
- prove real Yggdrasil timing precision supports this;
- authorize removal of provenance;
- require neural spike coding;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PART A — FREQUENCY / INTER-PULSE CODING WITH PROVENANCE
Three synthetic signal classes use nominal inter-pulse intervals:

4
7
11 time units.

Each source retains provenance.

The decoder therefore separates:
WHICH SOURCE EMITTED

from:
WHAT TEMPORAL CODE THAT SOURCE IS USING.

Timing jitter is Gaussian.

Pulse drop probability:
3%.

Decoder:
median of the most recent 5 observed inter-pulse intervals.

Choose nearest nominal code.

250 pulses per source.

200 matched trials per jitter level.

CLASSIFICATION ACCURACY

jitter SD = 0

99.98%.

0.25

99.99%.

0.50

99.98%.

1.00

99.64%.

1.50

96.99%.

2.00

91.79%.

PRIMARY FREQUENCY POSITIVE
With:
source provenance
and
well-separated temporal codes,

inter-pulse interval can carry signal identity robustly under moderate timing noise.

This offers:
one shared physical/local pulse substrate

with:
small source-local timing state.

PART B — FREQUENCY CODING WITHOUT PROVENANCE
The same three pulse trains are superposed.

The decoder sees only:
the aggregate pulse stream.

It does not know:
which source generated each event.

Even with zero timing noise:

classification accuracy:
approximately 51.66%.

Across jitter SD:
0
0.25
0.50
1.0
1.5
2.0

accuracy stays near:
50.7%..51.7%.

PRIMARY HARD SUPERPOSITION NEGATIVE
A mixture of several periodic pulse trains does not preserve:
individual inter-pulse intervals

after:
source identity is removed.

Thus:

TEMPORAL CODE
DOES NOT AUTOMATICALLY REPLACE
PROVENANCE.

This is an identifiability failure,
not a better-decoder issue in the current representation.

PART C — CLOSE FREQUENCY CODES
Nominal intervals:

7
8
11.

With provenance retained.

Accuracy:

jitter 0.25:
99.95%.

0.50:
97.54%.

1.00:
87.60%.

1.50:
79.24%.

PRIMARY CODE-SPACING RESULT
Timing-channel capacity is finite.

Closely spaced frequency codes consume:
noise margin.

Therefore:
more temporal code values

do not come for free.

PART D — PHASE-CODED SHARED CHANNEL
Three signal classes use:

common period:
12.

phases:
0
4
8.

Source provenance is NOT required for ordinary pulse classification.

Each observed pulse is classified from:
arrival phase modulo 12.

Pulses within:
0.75 time units

are treated as a collision group.

200 matched trials.

EFFECTIVE CORRECT RECOVERY
correct decoded symbols / true emitted symbols.

jitter SD = 0

100%.

0.25

100%.

0.50

99.99%.

1.00

95.35%.

1.50

81.58%.

2.00

68.28%.

PRIMARY PHASE POSITIVE
Phase coding can multiplex several logical signals on one shared pulse substrate
without explicit source provenance

when:
timing synchronization is strong.

Unlike frequency superposition,
individual pulse identity is directly encoded in:
phase.

PHASE COLLISION / NOISE LIMIT
As timing noise approaches:
the phase spacing,

classification error
and
pulse collision
rise rapidly.

Thus:
phase coding is compact
but
timing-sensitive.

PART E — EMITTER BIRTH / PHASE RESET
A new emitter of a known phase-coded class is created.

If it begins at:
a random local oscillator phase

with no synchronization to the established tissue reference:

mean classification accuracy:
33.53%.

This is essentially:
chance across three phase classes.

If the new emitter is explicitly aligned to:
the shared phase reference:

accuracy:
100%
at jitter SD 0.25.

PRIMARY HIDDEN-CLOCK NEGATIVE
Phase multiplexing appears provenance-free
only because it assumes:

A SHARED TEMPORAL REFERENCE.

Cell birth / oscillator reset exposes that hidden dependency.

Thus:
phase coding trades:
source provenance

for:
clock / phase provenance.

Nothing is free.

CURRENT TEMPORAL-CODE OPTIONS

FREQUENCY + SOURCE PROVENANCE

strength:
robust to absolute phase reset.

cost:
requires source-separated timing history.

PHASE CODE

strength:
individual pulses can carry class identity without source labels.

cost:
requires synchronized temporal reference.

SEPARATE CHANNELS

strength:
lowest semantic aliasing.

cost:
more persistent local state / substrates.

GENERAL PRINCIPLE
SIGNAL IDENTITY CAN LIVE IN:

SPACE

SOURCE

AMPLITUDE

FREQUENCY

PHASE

or
COMBINATIONS OF THEM.

Yggdrasil should not assume:
semantic information must occupy
one dedicated scalar channel per variable.

But:
compression moves the identifiability burden somewhere else.

REMOVE PROVENANCE
->
need stronger timing code.

REMOVE SHARED CLOCK
->
need source identity or self-synchronization.

PACK MORE FREQUENCIES
->
need lower timing noise.

OUTSIDE-STATUS-QUO IMPLICATION
A developmental communication substrate could eventually behave more like:

A DYNAMIC LOCAL SIGNAL ECOLOGY

than:
a fixed tensor of named channels.

Information could be carried by:
- continuous fields;
- pulse presence;
- pulse rate;
- pulse phase;
- source provenance;
- conductance history.

The compact developmental genome could learn:
which representation is worth using locally.

IMPORTANT NEGATIVE
Temporal multiplexing should not be adopted merely because it reduces channel count.

If:
timing precision
or
synchronization

costs more than the saved state,
it is a net loss.

The correct measure remains:
functional consequence
+
communication/resource cost.

DECISION
AR-H65 is CONDITIONALLY POSITIVE.

Supported synthetically:

- frequency codes are robust under moderate noise when provenance separates pulse trains;
- frequency superposition without provenance is strongly ambiguous;
- phase coding can multiplex several classes on one shared channel;
- phase coding degrades under timing noise/collision;
- close frequency codes reduce noise margin;
- phase coding secretly depends on a shared phase reference;
- random-phase emitter birth destroys phase classification unless synchronization is restored.

Not demonstrated:

- local oscillator synchronization;
- asynchronous topology-changing phase reference;
- mixed frequency + phase code;
- continuous-valued temporal coding;
- pulse-energy cost;
- code evolution across generations.

NEXT CLEAN QUESTION
AR-H66 — SELF-SYNCHRONIZING LOCAL OSCILLATOR SUBSTRATE

Question:

Can a tissue of local oscillators establish:
a usable phase reference

through:
nearest-neighbor coupling only,

without:
a global clock?

Compare:

A.
independent oscillators;

B.
oracle global phase;

C.
nearest-neighbor phase coupling;

D.
timing noise;

E.
cell birth with random phase;

F.
topology damage / reconnection;

G.
coupling too strong causing loss of useful phase diversity.

Desired:

new cells
->
entrain locally.

damaged / disconnected patch
->
resynchronize after reconnection.

No cell should receive:
global time.

This is inspired by:
locally coupled developmental oscillators,
but remains computational software research.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
frequency_codes = 4,7,11
phase_period = 12
phase_codes = 0,4,8
trials_per_condition = 200
