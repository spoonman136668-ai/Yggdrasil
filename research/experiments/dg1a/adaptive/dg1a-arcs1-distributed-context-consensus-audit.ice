TITLE: DG-1A-AR-CS1 — Distributed Context Sensor Consensus Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE-BUT-TRADEOFF COMMUNICATION AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
SERIES_NOTE: SUPPLEMENTAL SERIES — CANONICAL R4 NUMBERING PRESERVED
BRANCH: dg1a-ar
PARENT: dg1a-arc1-repeated-context-ordering-audit.ice

PURPOSE
AR-C1 showed that repeated decentralized context requires ordering information and that a bounded serial epoch can recover correctly after missed transitions.

AR-CS1 removes the remaining single-source assumption.

Question:
Can several noisy/damaged environmental sensors establish a shared context using only local gossip and distinct-source evidence?

BOUNDARY
This is synthetic.

It does not:
- replace AR-01 broadcast context;
- prove explicit sensor IDs are the final Yggdrasil representation;
- create a new controller;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BODY
radius-14 disk
613 live cells

communication:
8-neighbor local

cell stochastic update probability:
0.5

message dropout:
50%

phase duration:
96 steps

repeated context switches:
8

ENVIRONMENTAL SENSORS
8 boundary sensors distributed around the organism.

Each sensor may:
- be physically unavailable;
- report the current mode incorrectly;
- remain one epoch stale for the current transition.

No one sensor is privileged as authoritative.

DISTRIBUTED SENSOR TABLE
For this synthetic upper-bound experiment,
each cell can retain the newest report it has seen from each of the 8 sensor origins.

Local gossip merges:
newest report per sensor origin.

Context selection then uses:
the highest currently known epoch
+
sensor votes for the mode at that epoch.

IMPORTANT
The explicit per-sensor table is an experimental identifiability scaffold.

It is NOT a recommended final representation.

Its purpose is to prevent one relayed packet from being counted repeatedly as though it were many independent observations.

SCHEMES

SINGLE-NEWEST
At the newest known epoch,
use one available sensor report.

MAJORITY
At the newest known epoch,
use the majority mode among all distinct sensor origins currently represented.

QUORUM-3
Do not adopt a new epoch/mode until at least:
3 distinct sensor origins
are represented at that epoch.

Then use their majority mode.

PRIMARY CONDITION
sensor loss:
25%
=> 6 surviving sensors

per-sensor mode error:
10%

per-switch stale-epoch probability:
10%

errors:
independent

fresh seeds:
8

RESULTS

SINGLE-NEWEST
mean switch success:
90.6%

mean end-of-phase current-context fraction:
90.6%

median 90% consensus latency:
20.25 steps

MAJORITY
switch success:
100%

end current-context fraction:
100%

median latency:
21.0 steps

QUORUM-3
switch success:
100%

end current:
100%

median latency:
31.25 steps

PRIMARY POSITIVE
Distinct-source majority removes most of the fragility of trusting whichever newest sensor packet arrives first.

Quorum does not improve final correctness in the primary condition,
but it delays adoption until independent evidence accumulates.

TRANSIENT FALSE-CONTEXT EXPOSURE
A separate 8-seed measurement records the fraction of cells that have already adopted the CURRENT epoch but the WRONG mode.

PRIMARY CONDITION

SINGLE-NEWEST
mean peak wrong-current-mode fraction:
18.3%

mean wrong-current-mode exposure across phase:
10.9%

MAJORITY
peak:
8.6%

phase-average:
1.5%

QUORUM-3
peak:
0.3%

phase-average:
approximately 0%

KEY RESULT
Quorum strongly suppresses transient false regime activation.

This matters because:
a wrong mode need not persist to be harmful.

A short incorrect REPAIR,
GROWTH,
or DORMANCY transition could still alter the organism.

Therefore context consensus should measure:
FALSE MODE EXPOSURE
not only final agreement.

HIGH MODE-ERROR STRESS
sensor loss:
25%

mode error:
25%

stale:
10%

SINGLE
switch success:
67.2%

end current:
67.2%

MAJORITY
switch success:
85.9%

end current:
91.4%

QUORUM-3
switch success:
85.9%

end current:
89.9%

Fresh transient-false measurement:

SINGLE
peak wrong:
33.0%

phase-average:
18.7%

MAJORITY
peak:
18.7%

phase-average:
5.4%

QUORUM
peak:
3.8%

phase-average:
2.1%

INTERPRETATION
Quorum again substantially reduces transient wrong-mode exposure,
but it cannot manufacture correct information when too many surviving sensors are wrong.

SENSOR-LOSS STRESS
sensor loss:
50%
=> 4 surviving sensors

mode error:
10%

SINGLE
switch success:
93.8%

MAJORITY
98.4%

QUORUM-3
93.8%

median latency:

single:
22.75

majority:
23.25

quorum:
37.25

NEGATIVE
A fixed quorum of 3 becomes expensive when only four independent sensors survive.

Quorum strength must therefore depend on:
AVAILABLE INDEPENDENT EVIDENCE.

Do not hard-code a fixed absolute quorum without accounting for sensor survival.

COMBINED SENSOR LOSS + HIGH MODE ERROR
50% sensor loss
25% mode error

SINGLE
switch success:
~82.8%

MAJORITY:
~93.8%

QUORUM-3:
~89.1%

Fresh transient wrong-mode measurement:

SINGLE
peak:
31.7%
phase-average:
18.5%

MAJORITY
peak:
22.5%
phase-average:
9.8%

QUORUM
peak:
3.1%
phase-average:
2.2%

Thus quorum preserves its strongest advantage:
suppression of premature wrong-mode adoption.

But majority preserves more availability.

COMMON-MODE ERROR STRESS
With correlated/shared sensor-error events,
both majority and quorum lose part of their advantage.

This is expected.

Distinct sensor identity does NOT guarantee independent sensor error.

The prior redundant-sensor audit remains applicable:

MORE SENSORS
!=
MORE INDEPENDENT INFORMATION.

STALE-EPOCH STRESS
At 25% stale-report probability:

single:
~96.9% switch success

majority:
~98.4%

quorum:
~95.3%

Epoch ordering from AR-C1 prevents stale reports from overwriting newer established context.

The remaining effect is availability/latency:
too few sensors may reach the new epoch quickly enough for the quorum.

CRITICAL INFORMATION REQUIREMENT
Consensus must distinguish:

DISTINCT SENSOR EVIDENCE

from

COPIES OF THE SAME SENSOR EVIDENCE.

Local relay can create thousands of packet copies from one original observation.

Counting those copies as independent votes would create false confidence.

The explicit sensor-origin table prevents this by construction.

A future compact implementation therefore needs some equivalent of:
- source lineage;
- independence tag;
- compressed provenance sketch;
or
- another mechanism preventing echo amplification.

Do not interpret raw message count as sensor consensus.

ARCHITECTURAL TRADEOFF
MAJORITY

advantages:
- fast;
- high availability;
- robust to moderate sensor loss.

risk:
- temporary wrong-mode exposure while evidence is still sparse.

QUORUM

advantages:
- dramatically lower transient false-mode activation;
- safer for high-impact context transitions.

cost:
- slower switching;
- can stall after sensor damage;
- fixed quorum is inappropriate under variable sensor availability.

PREFERRED DIRECTION
Context adoption should probably be:

CONFIDENCE-WEIGHTED

rather than:

FIRST PACKET
or
FIXED QUORUM.

Conceptually:

distinct source count
+
agreement fraction
+
source freshness
+
estimated source independence
+
transition urgency / risk

->
context confidence.

Then:

high confidence:
adopt mode

moderate confidence:
reduce mode-sensitive plasticity / wait for evidence

low confidence:
retain current safe regime.

This mirrors AR-U11/U12:
uncertainty should modulate how aggressively the organism changes state.

LITERATURE ALIGNMENT
2026 wireless-sensor-network work on consensus-based local data aggregation explicitly studies decentralized aggregation under node failures and communication/topology constraints.

Recent swarm-robotics work likewise combines decentralized state estimation and mutual/local sensing to remain coherent under loss of primary localization.

These fields support the general engineering premise:
distributed state estimates should fuse multiple locally available sources and remain fault tolerant.

They do not validate the specific Yggdrasil context protocol.

DECISION
AR-CS1 is POSITIVE but bounded.

Supported:
- several noisy sensors can support decentralized context;
- distinct-source majority is substantially better than single-newest adoption;
- quorum can strongly suppress transient wrong-mode exposure.

Not supported:
- fixed absolute quorum;
- treating sensor count as independence;
- counting relayed copies as independent votes;
- eliminating all need for context confidence.

NEXT
AR-C3 — COMPRESSED SOURCE-INDEPENDENCE / CONTEXT CONFIDENCE

Questions:
1. Can cells avoid storing an explicit 8-sensor table?
2. Can a compact sketch retain enough source-independence information to prevent echo amplification?
3. Can context confidence adapt after sensor death?
4. Can high-risk modes demand stronger evidence than low-risk modes?

Candidate comparisons:
- full sensor-origin table upper bound;
- simple count without lineage;
- bitmask / bounded provenance sketch;
- probabilistic source sketch;
- learned compact consensus state.

Measure:
- final context correctness;
- transient false-mode exposure;
- memory/state cost;
- switch latency;
- sensor-loss robustness.

PARALLEL
AR-U14 — value-of-information / urgency coupling.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
body_cells = 613
sensor_count = 8
fresh_seeds_per_condition = 8
