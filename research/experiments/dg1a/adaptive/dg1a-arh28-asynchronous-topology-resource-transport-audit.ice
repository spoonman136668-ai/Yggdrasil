TITLE: DG-1A-AR-H28 — Asynchronous / Topology-Changing Resource Transport Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE ASYNC-CONSERVATION + STALE-PRICE EXPIRY RESULT / HELD-RESOURCE ORPHANING OPEN
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh27-distributed-local-evidence-budget-transport-audit.ice

PURPOSE
H27 showed that local demand-directed resource transport can approximate a centralized allocation advantage using only neighborhood communication.

H28 removes two hidden simplifications:

- synchronized transfer rounds;
- permanently stable cell identity / routing state.

QUESTION
Can local evidence/resource transport remain:
- conservative;
- non-duplicating;
- topology-safe;
- bounded against stale routing authority;

when:
- messages are delayed;
- retries occur;
- communication drops;
- cell generations change;
- price information arrives out of order?

BOUNDARY
This is synthetic.

It does not:
- freeze a production transfer protocol;
- freeze timeout/TTL values;
- define the final cell-identity system;
- solve resource already held by a permanently lost cell;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PART A — ASYNCHRONOUS TRANSFER INTEGRITY

SYNTHETIC NETWORK
64 local resource holders.

Initial total resource:
1000 units.

Local topology:
nearest-neighbor ring for this message-integrity stress.

Stream duration:
5000 asynchronous time steps.

New logical transfer probability:
0.22 per step.

Transfer amount:
bounded local fraction of donor holdings.

MESSAGE CONDITIONS

delivery delay:
1..8 asynchronous steps.

message/drop probability:
0.08.

retry timeout:
6 steps.

cell-generation churn probability:
0.0015 per step.

A generation change represents:
cell replacement
or
local identity rollover.

50 matched seeds.

UNSAFE RETRY COMPARATOR
Sender debits the logical transfer once.

Timed-out copies may be retried.

Receiver:
- does not enforce unique transfer ID;
- does not enforce destination generation;
- credits every arriving copy.

This deliberately exposes duplicate-delivery failure.

UNSAFE RESULT

mean final resource balance:
1050.4218

SD:
3.9536.

Mean maximum accounted resource drift:
50.6182 units.

Mean duplicate credits:
255.22
per run.

Mean stale-generation credits:
0.30
per run.

Mean retries:
373.54.

Mean dropped messages:
118.26.

PRIMARY UNSAFE NEGATIVE
Retryable asynchronous transfer without:
- idempotent transaction identity;
- generation validation;

manufactures resource.

The approximately 5% resource inflation is not a numerical issue.

It is a protocol failure.

SAFE LOCAL TRANSFER COMPARATOR
Each logical transfer carries:

TRANSFER ID

SENDER ID / GENERATION

DESTINATION ID / GENERATION

AMOUNT

CREATION TIME.

Sender debits exactly once.

Retries reuse the same transfer ID.

Receiver credits at most once.

A message targeting the wrong destination generation is not delivered.

Unsettled transfers remain explicit pending resource.

After bounded age,
unsettled resource is refunded to local sender/site reserve.

This is local accounting.

It does not require a global scheduler.

SAFE RESULT

mean final resource:
1000.0000.

between-seed SD:
approximately 5.1e-14.

mean maximum conservation drift:
2.11e-13.

duplicate credits:
0.

stale-generation credits:
0.

mean retries:
374.30.

mean refunds:
0.16.

mean dropped messages:
118.34.

PRIMARY ASYNC CONSERVATION POSITIVE
The safe local transfer protocol remains conservative to floating-point precision despite:

- delayed arrival;
- retries;
- dropped messages;
- out-of-order completion;
- cell-generation churn.

Thus:

ASYNCHRONOUS RESOURCE MOVEMENT
DOES NOT REQUIRE
GLOBAL SYNCHRONIZATION

if each transfer has:
- local ownership semantics;
- idempotent identity;
- generation validity;
- bounded settlement.

TRANSACTION PRINCIPLE
Evidence/resource tokens must behave more like:

CONSERVATIVE LEASED STATE

than:

FIRE-AND-FORGET SIGNALS.

A transfer should be in exactly one accounting state:

HELD BY SOURCE

or

IN FLIGHT

or

HELD BY DESTINATION

or

RETURNED / EXPIRED.

Never:
SOURCE + DESTINATION simultaneously.

PART B — ASYNCHRONOUS PRICE / DEMAND PROPAGATION

SPATIAL ORGANISM
12 x 12 grid.

Price information propagates through asynchronous local neighbor gossip.

Per macro-step:
144 random local price-update events.

Demand hotspots move at:
step 160.

The resource evaluator remains the H27 local conservative transport mechanism.

Two routing-state policies are compared.

UNBOUNDED STALE PRICE
A node can relay an old high-price record indefinitely.

No TTL.

No age decay.

TTL / AGE-BOUNDED PRICE
Every propagated price record carries:
- origin;
- timestamp;
- local age.

Effective authority decays exponentially.

Price records expire after:
12 macro-steps.

Exploratory decay timescale:
10.

20 matched seeds.

UNBOUNDED PRICE RESULT

pre-switch oracle-relative utility:
0.59296.

first 20 post-switch:
0.57471.

late post-switch:
0.57471.

fraction of local price records classified as stale/overstated:

early post-switch:
91.01%.

late:
41.13%.

PRIMARY STALE-ECHO NEGATIVE
Without expiration,
old high-price information persists after the demand region moves.

The spatial network develops:

PRICE ECHO.

Resource keeps receiving obsolete routing pressure.

Utility never recovers to a new steady routing solution in the tested horizon.

TTL-BOUNDED PRICE RESULT

pre-switch utility:
0.64048.

first 20 post-switch:
0.61568.

late post-switch:
0.62480.

stale/overstated price fraction:

early:
19.52%.

late:
0%.

PRIMARY PRICE-EXPIRY POSITIVE
Bounded price age removes stale routing authority after topology/demand change.

The result supports:

ROUTING SIGNAL EXISTS

separately from:

ROUTING SIGNAL IS STILL CURRENTLY VALID.

This matches:
H23-H25 trust-state separation.

WHY PRICE TTL IS NOT ENOUGH BY ITSELF
A short TTL can prevent stale echo,
but an overly short TTL would:
- increase communication;
- reduce long-range resource guidance;
- erase useful stable price gradients.

Therefore:
price lifetime is another:
STABILITY
vs
PLASTICITY

tradeoff.

H28 does not freeze:
12 steps
or
timescale 10.

CELL GENERATION PRINCIPLE
Resource-transfer messages need generation identity.

Price messages also need:
- age;
- provenance;
- bounded authority lifetime.

A newly created/replaced cell should not silently inherit:
all in-flight transactions
or
all stale routing authority
from the prior occupant of that site.

IDENTITY
and
LOCATION
must remain distinguishable.

CURRENT DISTRIBUTED RESOURCE OBJECTS

RESOURCE TOKEN / LEASE

fields:
- amount;
- current owner;
- transfer ID if in motion;
- sender generation;
- destination generation;
- creation time;
- settlement state.

PRICE / DEMAND SIGNAL

fields:
- local value;
- source/provenance;
- generation or validity epoch where available;
- timestamp;
- age / TTL;
- trust.

TRANSFER AUTHORITY
depends on:

local token ownership

+

valid neighbor link / destination generation

+

trusted current price gradient.

RELATION TO H27
H27:
local price transport is useful,
but bad bids can monopolize resource.

H28:
even good bids become bad when they outlive the context that generated them.

Thus resource routing needs both:

BID TRUST

and

BID FRESHNESS.

RELATION TO H25
H25 established:

stored state
!=
current authority.

H28 extends that to distributed routing:

a price record may still exist in local memory
without retaining transfer authority after its TTL / context validity expires.

IMPORTANT OPEN NEGATIVE
H28 solves:

RESOURCE IN TRANSIT

under cell-generation change.

It does NOT yet solve:

RESOURCE ALREADY HELD BY A CELL
THAT DISAPPEARS PERMANENTLY.

If a cell dies while holding local resource,
strict conservation can coexist with:
permanent resource unavailability.

That is:

ORPHANED RESOURCE.

This is a distinct problem.

Conservation alone does not guarantee:
resource accessibility.

DECISION
AR-H28 is POSITIVE WITH A HELD-RESOURCE ORPHANING OPEN PROBLEM.

Supported synthetically:

- asynchronous retries need idempotent transfer identity;
- generation validation prevents stale delivery into replacement cells;
- local pending/refund semantics preserve exact resource conservation;
- global synchronization is unnecessary for transfer integrity;
- stale asynchronous price propagation can create persistent routing echoes;
- bounded age/TTL removes stale routing authority and restores adaptation after demand relocation.

Not demonstrated:

- permanent held-resource reclamation after cell death;
- topology partition healing;
- safe resource inheritance on cell division;
- distributed transfer under arbitrary graph changes;
- optimal price TTL;
- implementation cost on current Yggdrasil runtime.

NEXT CLEAN QUESTION
AR-H29 — HELD-RESOURCE LEASE / RECLAMATION AFTER CELL DEATH

Question:

When a cell disappears while holding resource,
can local tissue reclaim that resource without:
- central accounting;
- duplicate ownership;
- immediate global garbage collection?

Candidate mechanisms:

A.
hard ownership:
resource dies with the cell.

B.
site-held escrow:
resource remains at the spatial site until a valid neighboring lineage claims it.

C.
time-bounded lease:
cell ownership expires unless locally renewed.

D.
generation-aware inheritance:
daughter/replacement receives resource only through explicit lineage transfer.

Stress:
- sudden cell death;
- clustered tissue loss;
- later regeneration;
- partition/reconnection;
- simultaneous transfer in flight.

Desired:

conservation
+
eventual accessibility
+
no double inheritance.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
async_transfer_seeds = 50
async_transfer_steps = 5000
initial_transfer_resource = 1000
message_drop_probability = 0.08
cell_generation_churn_probability = 0.0015
async_price_seeds = 20
price_switch_step = 160
price_ttl = 12
