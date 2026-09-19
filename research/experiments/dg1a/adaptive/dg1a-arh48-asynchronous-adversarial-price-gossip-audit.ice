TITLE: DG-1A-AR-H48 — Asynchronous / Adversarial Local Memory-Price Gossip Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE FRESHNESS-PROVENANCE PRICE RESULT + LOCAL-CROSSCHECK REQUIREMENT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh47-decentralized-generative-memory-price-audit.ice

PURPOSE
H47 showed that bounded neighbor price diffusion can approximate regional generative-memory scarcity without a global price scalar.

H48 removes two hidden simplifications:

- synchronous clean price propagation;
- truthful neighbor price messages.

QUESTION
Can local structural-memory pricing remain:
- fresh;
- spatially bounded;
- resistant to duplicate/stale messages;
- resistant to one temporarily faulty high-price region;

while still adapting to a real persistent scarcity increase?

BOUNDARY
This is synthetic.

It does not:
- freeze a production gossip protocol;
- establish adversarial security;
- freeze TTL = 3;
- freeze the local cross-check clamp;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SPATIAL PRICE SYSTEM
10 x 10 local regions.

Nearest-neighbor communication only.

Each region has:
- local true structural-memory scarcity;
- noisy local price observation;
- current local price estimate.

MESSAGE CONDITIONS
Asynchronous neighbor-message delay:

0..3 steps.

Duplicate-message probability:

12%.

Messages carry:
- sender identity;
- sender timestamp;
- price estimate.

PRIMARY FAULT
A compact local region becomes faulty for:

20 steps.

During the fault,
that region adds:

+1.5 synthetic price units

to emitted price messages.

The underlying true scarcity does NOT change.

Thus the region attempts to create:
false local structural inhibition.

PRIMARY COMPARATORS

RAW ARRIVAL GOSSIP
Average all arriving neighbor messages.

Duplicates count multiple times.

No sender-level freshness state.

Out-of-order arrivals can influence the current price.

TTL + PROVENANCE MEDIAN
Retain only the newest message per neighbor provenance.

Expire a neighbor price if:

age > 3 steps.

Aggregate:
local fresh observation
+
one current price per neighbor

using a robust median blend.

TTL + PROVENANCE + LOCAL CROSS-CHECK
Same as above,
but cap the neighbor-induced deviation from the region's own current local scarcity observation.

Primary cap:
0.45 synthetic price units.

This is a diagnostic bounded-influence rule,
not a frozen constant.

PRIMARY ADVERSARIAL CONFIRMATION
30 matched asynchronous streams per policy.

RAW GOSSIP

clean pre-fault mean absolute price error:
0.04019.

during fault:
0.26084.

faulty-region error:
1.11674.

post-fault 20-step error:
0.11287.

remote false-high-price fraction during fault:
0.315%.

mean recovery after fault ends:
11.5 steps.

PRIMARY RAW NEGATIVE
Delayed duplicate raw gossip allows:
one faulty price region
to dominate its local neighborhood

and
remain influential long after the fault stops.

The problem is not only:
bad value.

It is also:
stale duplicated authority.

TTL + PROVENANCE MEDIAN

clean error:
0.03383.

fault-period total error:
0.07382.

faulty-region error:
0.35602.

post-fault:
0.03620.

remote false-high-price fraction:
0%.

mean recovery:
1.17 steps.

PRIMARY FRESHNESS / PROVENANCE POSITIVE
Three simple distinctions remove most of the failure:

1.
WHO SENT THIS PRICE?

2.
HOW OLD IS IT?

3.
IS THIS A NEW SOURCE
OR A DUPLICATE MESSAGE FROM THE SAME SOURCE?

Duplicate/stale price messages no longer accumulate structural authority.

TTL + PROVENANCE + LOCAL CROSS-CHECK

clean error:
0.03383.

fault-period total error:
0.04479.

faulty-region error:
0.13272.

post-fault:
0.03442.

remote false-high-price fraction:
0%.

mean recovery:
approximately 0 steps at the tested five-step recovery criterion.

PRIMARY CROSS-CHECK POSITIVE
Neighbor prices should influence:
local opportunity cost,

but
should not be able to override:
all direct local resource evidence
in one step.

The local scarcity observation provides:
a bounded independent anchor.

This sharply limits the faulty-region blast radius.

REAL SCARCITY SHIFT CONTROL
A defense against false price inflation must not suppress genuine price increases.

A separate test removes the faulty sender.

At step:
25

the same local region undergoes a REAL persistent scarcity increase:

+1.0 price-equivalent units.

40 matched streams.

RAW GOSSIP

pre-shift error:
0.04017.

early post-shift error:
0.10712.

late:
0.10337.

TTL + MEDIAN

pre:
0.03397.

early:
0.05329.

late:
0.03427.

TTL + CROSS-CHECK

pre:
0.03397.

early:
0.04128.

late:
0.03427.

PRIMARY ADAPTATION POSITIVE
Freshness/provenance filtering does not freeze a real scarcity shift.

The local direct resource evidence changes immediately,
so the cross-check permits price increase.

This is the desired asymmetry:

NEIGHBOR-ONLY INFLATION
gets bounded.

LOCAL + NEIGHBOR PERSISTENT SCARCITY
is allowed to propagate.

STALE HIGH-PRICE EXPIRY
When the faulty region stops emitting inflated prices,
TTL-based policies return near baseline within approximately:

0 to 1 step

in the tested asynchronous model.

Raw gossip takes:

~11.5 steps.

Thus:
OLD SCARCITY
SHOULD NOT RETAIN PRICE AUTHORITY
MERELY BECAUSE IT IS STILL IN MESSAGE HISTORY.

RELATION TO H28
H28 showed asynchronous resource transfer needs:
- unique transaction identity;
- generation validation;
- stale-state expiry.

H48 shows price gossip needs the analogous control-plane properties:

- source identity;
- message freshness;
- duplicate collapse;
- stale authority expiry.

RESOURCE STATE
and
PRICE STATE
are different objects,
but both need provenance-safe asynchronous handling.

RELATION TO S9
S9 showed:
a formerly valid causal control can become invalid
without disappearing.

H48 adds:
a formerly valid neighbor price can become stale
without becoming syntactically malformed.

Thus price trust needs:
RECENCY.

CURRENT LOCAL PRICE MESSAGE
A structural-price signal should conceptually carry:

SOURCE / PROVENANCE

+

SOURCE GENERATION

+

OBSERVATION / CREATION TIME

+

PRICE VALUE

+

LOCAL TRUST

+

OPTIONAL RESOURCE-STATE EVIDENCE.

Raw price values without those fields should not receive durable authority.

GENERAL PRINCIPLE
PRICE IS ADVISORY STATE,
NOT COMMAND AUTHORITY.

Neighbor price signals can alter:
local structural opportunity cost.

They should not directly:
forbid growth
or
rewrite memory.

The local organism still compares:
candidate value
against
its current trusted price estimate.

DECISION
AR-H48 is POSITIVE.

Supported synthetically:

- asynchronous duplicate/stale price gossip can amplify a faulty high-price region;
- per-source freshness and duplicate collapse strongly reduce that failure;
- local resource cross-check further bounds neighbor-only price manipulation;
- stale inflated prices expire quickly under TTL;
- real persistent scarcity still raises price under the same defense.

Not demonstrated:

- subtle within-bound price manipulation;
- colluding faulty neighbors;
- optimal TTL;
- learned local cross-check gain;
- topology churn during gossip;
- coupling between price trust and cell-generation identity.

NEXT CLEAN QUESTION
AR-H49 — COLLUDING / IN-RANGE LOCAL PRICE MANIPULATION

H48's faulty region used a large obvious price inflation.

Question:

What if several neighboring sources collude
and
each stays inside the local cross-check bound?

A coordinated cluster may slowly bias the price field
without any one message looking extreme.

Compare:

A.
bounded median only;

B.
source/provenance diversity;

C.
independent local occupancy consequence;

D.
temporal price-change budget;

E.
real slow scarcity increase.

Desired:

coordinated neighbor-only drift
->
limited structural inhibition.

genuine gradual local scarcity
->
price should still rise.

This is the price-system analogue of:
H10/H18/H40 common-mode evidence failures.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
grid = 10x10
fault_duration_steps = 20
message_delay = 0..3
duplicate_probability = 0.12
primary_fault_streams = 30
real_shift_streams = 40
