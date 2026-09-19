TITLE: DG-1A-AR-C1 — Repeated Decentralized Context Ordering Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE / BOUNDED COMMUNICATION AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-ar01-local-context-propagation-audit.ice

PURPOSE
The earlier local-context relay audit solved one seasonal transition with a binary freshness marker.

That mechanism cannot order arbitrary repeated future switches.

AR-C1 asks:

Can a purely local relay preserve context ordering across many seasonal transitions,
stale messages,
wraparound,
message dropout,
and temporary component disconnection?

BOUNDARY
Synthetic communication audit only.

It does not:
- replace AR-01 broadcast context;
- modify Yggdrasil;
- create a second controller;
- authorize a particular hidden-state encoding;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX
ANALYTIC where explicitly marked.

BODY
40 x 40 lattice
radius-14 disk
613 live cells

communication:
8-neighbor local only

stochastic cell update:
0.5

sensor cells:
4 boundary sources for repeated steady-state tests

message dropout:
50% primary
75% stress

local communication may return a neighbor state from a bounded number of prior update snapshots,
creating stale-message exposure.

MODES
Six cyclic seasonal modes.

CONTEXT PACKET
mode
+
bounded serial epoch.

SERIAL ORDER RULE
Let modulus:
M

current local epoch:
e_local

candidate neighbor epoch:
e_msg

compute:

d =
(e_msg - e_local) mod M

accept candidate as newer only if:

0 < d < M/2.

This is standard half-range modular ordering logic.

No cell uses a global clock.

Sensor/source increments the epoch only when the external context actually changes.

BASELINES

MODE-ONLY ANY-DIFFERENT
If a neighbor mode differs,
adopt it.

SUCCESSOR-ONLY
Accept only the cyclic next mode:

m_new =
(m_local + 1) mod 6.

SERIAL
Use the bounded modular epoch rule above.

PRIMARY REPEATED-SWITCH TEST
Switch period:
96 steps

message dropout:
50%

stale neighbor history:
up to 8 prior snapshots

12 repeated mode switches

4 seeds for the baseline comparison.

MODE-ONLY RESULT
switches reaching 90% current-mode consensus:
0%

mean end-of-phase current fraction:
approximately 18.65%

mean stale overwrites per seed:
15,338

NEGATIVE
Without an ordering variable,
old messages can overwrite new context indefinitely.

SUCCESSOR-ONLY
switch success:
100%

median 90% consensus latency:
42 steps

mean end-of-phase current fraction:
1.0

stale overwrite:
0

SERIAL M=16
switch success:
100%

median latency:
42 steps

mean end-of-phase current fraction:
1.0

stale overwrite:
0

INTERPRETATION
When every component receives every transition,
successor-only and serial ordering both work.

Therefore the serial tag is NOT justified merely by ordinary repeated switching.

Its value appears when transitions are MISSED.

WRAPAROUND TEST
Serial ordering only.

message dropout:
50%

stale history:
16 snapshots

switch period:
96

repeated switches:
30

seeds:
6

M = 8:
switch success:
100%

median latency:
57 steps

95th-percentile latency:
62 steps

mean end-of-phase current fraction:
1.0

stale overwrites:
0

M = 16:
same measured result within resolution:
100% success
57-step median
62-step p95
1.0 end fraction
0 stale overwrites.

Thus modular wraparound itself is safe when lag remains well inside the half-range ordering bound.

HIGH-DROPOUT STRESS
message dropout:
75%

stale history:
16

switch period:
128

20 switches
6 seeds

M=8:
100% switch success
median latency:
80.5
p95:
86
end fraction:
1.0
stale overwrite:
0

M=16:
same measured result within resolution.

MISSED-TRANSITION COMPONENT TEST
This is the discriminating experiment.

Use only one environmental sensor on the LEFT boundary.

Temporarily partition the organism along a vertical cut.

The right component:
- has no sensor;
- cannot receive messages from the left during the partition.

The environmental source advances through THREE mode/epoch changes while the right component remains isolated.

Then:
reconnect the components

and hold the current mode long enough to measure catch-up.

Message dropout:
50%

stale history:
8

12 fresh seeds.

MODE-ONLY
No seed reached 90% current context.

Final current-mode fraction:
roughly 14..24%

Thousands of stale overwrites occur.

SUCCESSOR-ONLY
No seed reached 90%.

Final current-mode fraction:
0.47635
for every tested seed.

Interpretation:
the left component is current.

The right component is waiting for a missing intermediate successor mode that no longer exists in the live message field.

It is stranded.

SERIAL M=16
12/12 recovered.

90% current-context catch-up latency:

33
34
35
35
35
36
36
37
37
38
38
38

median:
approximately 36 steps.

Final current context:
100%.

stale overwrite:
0.

PRIMARY POSITIVE
A bounded serial tag lets a disconnected/out-of-date component jump directly to the newest context after reconnection.

This solves the failure mode that successor-only ordering cannot.

SERIAL-WIDTH STRESS
The half-range rule creates a hard bound.

For modulus M:

unambiguous forward ordering requires:
lag in epochs < M/2.

A second split-component experiment varied how many mode transitions were missed.

M=8:

miss 3 transitions:
8/8 recovered

miss 4:
8/8 eventually recovered in the tested dynamic field,
although the direct half-range difference is ambiguous and recovery depends on transient intermediate states.

miss 5:
0/8 recovered

miss 6:
0/8 recovered

M=16:

miss 3:
8/8

miss 4:
8/8

miss 5:
8/8

miss 6:
8/8

For M=16 and misses 3..6:
typical post-reconnection catch-up was about 33..38 steps.

HARD ANALYTIC LIMIT
A bounded modulo counter cannot distinguish arbitrarily old messages.

With the half-range comparison:

if a component can lag by:
>= M/2 epochs

then some old/new epoch pairs become ambiguous or reverse ordered.

This is not a training problem.

Therefore context-epoch width must be chosen from a declared bound on:

maximum plausible context lag
+
message lifetime
+
partition duration expressed in context transitions.

Do NOT blindly choose the smallest counter.

ARCHITECTURAL CONSEQUENCE
A future decentralized context packet needs at least:

MODE VALUE

+
ORDER / GENERATION INFORMATION.

One workable compact abstraction is:

bounded serial epoch
+
half-range newer-than comparison.

But the state need not literally be an integer register in the final learned organism.

The scientific requirement is:

cells must distinguish:
NEW CONTEXT
from
STALE CONTEXT

across repeated transitions.

RELATION TO FRESHNESS
The previous binary freshness bit answers:

have I heard THIS one transition?

The serial tag answers:

which of several transitions is newer?

These are different information problems.

SENSORLESS COMPONENT LIMIT
The earlier information-theoretic constraint remains.

During disconnection,
a component with:
- no sensor;
- no communication path;
- no predictive information about future external context

cannot know new exogenous mode changes.

AR-C1 does not bypass that limit.

It only ensures correct catch-up after a valid newer message becomes reachable.

DESIGN RECOMMENDATION
Keep AR-01 global broadcast for the first real seasonal-mode discrimination.

For a later decentralized-context experiment:

sensor observation
->
mode + bounded ordering state
->
fresh local relay
->
newer-than acceptance
->
distributed context memory.

Stress:
- partitions;
- missed transitions;
- wraparound;
- stale messages;
- sensor loss;
- varying switch period.

Do not use:
mode-only overwrite.

Do not rely solely on:
successor-only transitions.

NEXT
AR-C2 — DISTRIBUTED CONTEXT WITHOUT A SINGLE SENSOR AUTHORITY

Test:
- several sensors with independent noisy mode observations;
- local consensus;
- conflicting epochs;
- sensor damage;
- no assumption that one sensor always has the authoritative packet.

This connects AR-C1 to the prior redundant-sensor consensus audit.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX_AND_ANALYTIC
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
body_cells = 613
