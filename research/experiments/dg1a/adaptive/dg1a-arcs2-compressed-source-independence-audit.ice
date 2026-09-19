TITLE: DG-1A-AR-CS2 — Compressed Source-Independence / Context Confidence Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE-BUT-BOUNDED PROVENANCE AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
SERIES_NOTE: SUPPLEMENTAL SERIES — CANONICAL R4 NUMBERING PRESERVED
BRANCH: dg1a-ar
PARENT: dg1a-arcs1-distributed-context-consensus-audit.ice

PURPOSE
AR-CS1 showed that decentralized context consensus needs to distinguish:

DISTINCT SENSOR EVIDENCE

from

RELAYED COPIES OF THE SAME EVIDENCE.

The explicit 8-sensor table used in AR-CS1 is an identifiability upper bound,
not an attractive final state representation.

AR-CS2 asks:

Can an idempotent compressed provenance sketch preserve enough distinct-source information to prevent echo amplification?

BOUNDARY
This is synthetic.

It does not:
- freeze a final provenance encoding;
- claim four or six bits are sufficient for larger organisms;
- solve common-mode sensor failure;
- replace AR-01 broadcast context;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

STATIC SENSOR-CONSENSUS BENCHMARK
Sensors:
8

True modes:
6

Trials:
200,000 per condition

Sensor survival and sensor mode error vary by condition.

Each surviving sensor produces one mode report.

The experiment then models relay duplication separately.

SCHEMES

EXACT DISTINCT-SOURCE MAJORITY
Every sensor has a unique identity.

Each source contributes at most one vote.

This is the upper-bound reference.

RAW RELAY-MESSAGE COUNT
A sensor report may be duplicated many times by relay propagation.

Each source receives a random positive copy count drawn from a broad lognormal-like distribution.

Consensus counts packet copies,
not source origins.

This intentionally tests echo amplification.

HASHED PROVENANCE SKETCH
Each sensor origin hashes into one of:

4
6
or
8

bounded provenance buckets.

For each candidate mode,
the local state retains the OR of source buckets observed for that mode.

Repeated copies of the same report are idempotent:
they do not increase the bucket count.

Consensus uses:
number of distinct occupied buckets per mode.

At 8 buckets,
the synthetic hash assignment is collision-free for the 8 sensor IDs and equals the exact bitmask upper bound.

At 4/6 buckets,
source collisions compress provenance but can undercount evidence.

MEMORY INTERPRETATION
For six candidate modes:

exact 8-source bitmask:
48 provenance bits

4-bucket per-mode sketch:
24 bits

6-bucket:
36 bits

This comparison ignores epoch/order storage and other implementation overhead.

It is a provenance-only accounting illustration.

PRIMARY CONDITION
sensor loss:
25%

mean surviving sensors:
~6

mode error:
10%

EXACT DISTINCT SOURCE
correct non-tied consensus:
99.58%

tie/defer:
0.36%

RAW COPIES
correct:
96.08%

tie:
0.24%

HASH-4
correct:
99.21%

tie:
0.71%

HASH-6
correct:
99.39%

tie:
0.54%

HASH-8 / exact bitmask
99.58%

HIGHER SENSOR ERROR
loss:
25%

mode error:
25%

EXACT
correct:
95.60%

defer/tie:
3.40%

RAW COPIES
correct:
86.42%

HASH-4
correct:
93.56%

HASH-6
correct:
94.52%

HASH-8
95.60%

PRIMARY POSITIVE
Idempotent provenance compression preserves most of the distinct-source advantage.

Raw packet counts lose much more accuracy because message duplication changes the apparent evidence weight.

Therefore:

MESSAGE MULTIPLICITY
is not
SENSOR EVIDENCE MULTIPLICITY.

SENSOR-LOSS STRESS
loss:
50%

mean survivors:
~4

mode error:
10%

EXACT:
96.46%

RAW COPIES:
93.43%

HASH-4:
95.44%

HASH-6:
95.95%

HASH-8:
96.46%

loss 50%
mode error 25%

EXACT:
86.56%

RAW:
80.99%

HASH-4:
83.97%

HASH-6:
85.23%

HASH-8:
86.56%

COMPRESSION COST
Hash collisions mostly create:

UNDERCOUNTING

and

ADDITIONAL TIES / DEFERRED DECISIONS.

They are substantially safer than raw packet duplication,
which can create false confidence in whichever source happens to replicate more aggressively.

This is favorable for a conservative organism:
uncertain evidence should preferably reduce confidence rather than fabricate confidence.

HIGH-RISK CONTEXT GATE
Using exact distinct-source evidence,
a separate gate requires:

at least 3 observed sources

and

>=75% of distinct source votes agree

before adopting a high-risk mode.

RESULTS

loss 25%
mode error 10%

accepted:
88.91%

false adoption among all trials:
approximately 0.002%

conditional accuracy among accepted:
approximately 99.998%

loss 25%
mode error 25%

accepted:
55.89%

false adoption:
0.03%

conditional accuracy:
99.95%

loss 50%
mode error 10%

accepted:
74.72%

false adoption:
0.01%

conditional accuracy:
99.99%

loss 50%
mode error 25%

accepted:
50.85%

false adoption:
0.08%

conditional accuracy:
99.84%

PRIMARY CONFIDENCE RESULT
Strong distinct-source agreement can nearly eliminate false high-risk context adoption in the INDEPENDENT-error toy.

The cost is substantial deferral under:
- high sensor error;
- sensor loss.

This directly mirrors the AR-U11/U12 plasticity result:

higher certainty
->
safer state change

but
->
lower update availability.

COMMON-MODE SENSOR ERROR
A hard limitation remains.

Primary loss:
25%

independent sensor error:
10%

add a shared event in which all surviving sensors report the same wrong mode.

Shared wrong-event probability:

0%:
exact majority accuracy ~99.58%

5%:
~94.59%

10%:
~89.61%

20%:
~79.65%

The 75%-agreement high-risk gate cannot detect this failure because the wrong sensors AGREE.

At shared wrong-event probability 10%:

gate acceptance:
~89.94%

false adoption:
~9.97%

conditional accuracy:
~88.91%

HARD NEGATIVE
CONSENSUS CANNOT CREATE INDEPENDENCE.

If all sources share one failure mode,
strong agreement can be strongly wrong.

Therefore:
SOURCE COUNT
and
SOURCE AGREEMENT
are not sufficient confidence variables.

Future context confidence also needs evidence about:
SOURCE ERROR DIVERSITY / INDEPENDENCE.

RELATION TO PRIOR YGGDRASIL RESULTS
This is now the fourth place where the same principle appears:

INJURY CUES

SEASONAL SENSORS

ROLE-CREDIT CUES

CONTEXT PROVENANCE

Redundancy helps only when the evidence contains sufficiently independent error modes.

CROSS-DOMAIN DESIGN RULE
Useful distributed confidence requires:

DISTINCT PROVENANCE

+
PARTIALLY INDEPENDENT FAILURE MODES.

One without the other is insufficient.

RAW DUPLICATION NEGATIVE
The relay system can produce many copies of one sensor observation.

Any learned or engineered context-confidence state must avoid interpreting:

more copies
as
more independent evidence.

Idempotent evidence accumulation is therefore attractive.

POSSIBLE COMPACT REPRESENTATIONS
Do not freeze one.

Candidates include:

BITMASK
exact for small source populations.

HASHED BITSET / BLOOM-LIKE PROVENANCE
compact but collision-prone.

SMALL LEARNED SOURCE-SIGNATURE STATE
could compress provenance but must be explicitly tested for echo amplification.

DIVERSITY SKETCH
track not only how many sources agree,
but whether evidence comes through meaningfully different sensing/error pathways.

SOURCE CLUSTERS
count independent sensor classes/modules rather than individual sensors.

ARCHITECTURAL CONSEQUENCE
A future context-confidence state may need at least conceptual equivalents of:

EPOCH / ORDER

MODE

DISTINCT-EVIDENCE ESTIMATE

AGREEMENT

SOURCE-DIVERSITY / INDEPENDENCE ESTIMATE

FRESHNESS

Then:
context-switch plasticity can depend on confidence and risk.

This remains compact compared with permanently broadcasting an authoritative global mode to every cell,
but it is more information than a single mode bit.

LITERATURE ALIGNMENT
Recent wireless-sensor-network research continues to study consensus-based local aggregation under node failures and constrained local communication.

Recent swarm-robotics systems similarly use decentralized fusion and consensus to remain coherent under unreliable primary sensing.

The engineering literature supports fault-tolerant local fusion as a real systems problem.

It does not establish the Yggdrasil provenance sketch.

DECISION
AR-CS2 is POSITIVE within the tested small-sensor regime.

Supported:
- idempotent source sketches can preserve most distinct-source value;
- small sketches can trade memory for additional ties/deferral;
- high-risk context can demand stronger evidence.

Not solved:
- common-mode sensor error;
- scalable source-diversity estimation;
- learned provenance without echo inflation;
- larger sensor populations;
- dynamic source classes.

NEXT
AR-C4 — SENSOR-DIVERSITY / COMMON-MODE FAILURE DETECTION

Question:
Can the organism estimate whether agreeing sensors are actually independent?

Test sensors grouped into correlated error families.

Compare:
- raw source count;
- source-family count;
- covariance/disagreement history;
- compressed diversity sketch.

Measure whether context confidence can reject:
many agreeing sensors
that all fail together.

PARALLEL
AR-U14 — value-of-information / urgency coupling.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
trials_per_condition = 200000
sensor_count = 8
