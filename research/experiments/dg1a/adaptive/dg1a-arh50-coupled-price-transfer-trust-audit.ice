TITLE: DG-1A-AR-H50 — Coupled Resource-Transfer + Price-Manipulation Trust Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE TYPED-TRUST RESULT + CORROBORATED-JOINT-HAZARD BENEFIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh49-colluding-in-range-price-manipulation-audit.ice

PURPOSE
H27-H29 studied physical resource transport and ownership.

H47-H49 studied structural-memory price advice.

Until H50,
those two channels were mostly tested separately.

H50 asks:

WHAT HAPPENS WHEN THE SAME NEIGHBOR PROVIDES BOTH:

PRICE ADVICE

and

RESOURCE TRANSFER?

Should one bad channel destroy trust in the other?

BOUNDARY
This is synthetic.

It does not:
- freeze a production trust update;
- define final price/transfer protocols;
- establish adversarial security;
- require one price/transfer source topology;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

FOCUSED LOCAL NEIGHBORHOOD
One focal region interacts with:

4 local neighboring sources.

Each source can independently provide:

PRICE SIGNAL

and

RESOURCE TRANSFER.

One source becomes faulty during:

steps 280..559.

Three fault geometries are tested:

PRICE-ONLY FAULT

TRANSFER-ONLY FAULT

BOTH CHANNELS FAULT.

PRICE CHANNEL
Clean neighbor price noise SD:
0.06.

Faulty price source adds:
+0.45 synthetic price units.

TRANSFER CHANNEL
Clean fulfillment probability:
0.90.

Faulty transfer fulfillment:
0.12.

TRUST UPDATE
EMA rate:
0.06.

PRIMARY COMPARATORS

COLLAPSED SHARED TRUST

One trust scalar per source.

Price evidence
and
transfer evidence

are averaged into the same authority state.

That one scalar controls both:
price weighting
and
resource-allocation weighting.

TYPED TRUST

Each source retains:

PRICE TRUST

and

TRANSFER TRUST

as separate state.

Same provenance identity.

Different authority questions.

CORROBORATED TYPED TRUST

Keep price and transfer trust separate.

If BOTH channels independently show strong local failure at the same time,
apply an additional bounded joint-hazard decay to both trust states.

This is not state collapse.

It is:
cross-channel corroboration.

PRIMARY CONFIRMATION
50 to 60 matched synthetic seeds per comparison.

Fault-window metrics use the mature latter portion of the fault interval.

PRICE-ONLY FAULT

COLLAPSED SHARED TRUST

price error:
0.03925.

resource fulfillment:
0.90034.

faulty-source price weight:
0.1517.

faulty-source transfer share:
0.1515.

TYPED TRUST

price error:
0.02882.

resource fulfillment:
0.90029.

faulty price weight:
0.0014.

faulty transfer share:
0.2498.

CORROBORATED TYPED

same as typed to practical precision.

PRIMARY PRICE-ONLY RESULT
A price liar can still be a perfectly useful resource-transfer peer.

Collapsed trust unnecessarily suppresses transfer use:

approximately:
25%
->
15%.

Typed trust rejects the bad price
while preserving the clean physical-transfer path.

Thus:

BAD PRICE AUTHORITY
DOES NOT IMPLY
BAD RESOURCE OWNERSHIP / TRANSFER AUTHORITY.

TRANSFER-ONLY FAULT

COLLAPSED TRUST

price error:
0.02826.

resource fulfillment:
0.78042.

faulty price weight:
0.1536.

faulty transfer share:
0.1533.

TYPED TRUST

price error:
0.02809.

resource fulfillment:
0.86805.

faulty price weight:
0.2520.

faulty transfer share:
0.0407.

CORROBORATED TYPED

price error:
0.02820.

fulfillment:
0.86955.

faulty price weight:
0.2429.

faulty transfer share:
0.0386.

PRIMARY TRANSFER-ONLY RESULT
A transfer-defective peer may still provide useful scarcity/price information.

Typed trust sharply reduces physical resource allocation to the bad transfer source
without discarding most of its clean price contribution.

Collapsed trust underperforms on fulfillment because its mixed trust state does not learn the transfer failure strongly enough.

Thus:

BAD TRANSFER AUTHORITY
DOES NOT AUTOMATICALLY IMPLY
BAD PRICE-ADVICE AUTHORITY.

BOTH-CHANNEL FAULT

COLLAPSED TRUST

price error:
0.02891.

resource fulfillment:
0.88503.

faulty price weight:
0.0193.

faulty transfer share:
0.0192.

TYPED TRUST

price error:
0.02865.

resource fulfillment:
0.86805.

faulty price weight:
0.0013.

faulty transfer share:
0.0407.

INTERPRETATION
Typed trust correctly rejects price authority quickly,
but transfer trust learns the physical failure on its own timescale.

Because the two typed states do not automatically reinforce one another,
the bad transfer path persists somewhat longer.

This is the legitimate cost of keeping trust meanings separate.

CORROBORATED JOINT-HAZARD RESULT

price error:
0.02878.

resource fulfillment:
0.90033.

faulty price weight:
0.0004.

faulty transfer share:
0.0001.

PRIMARY JOINT-FAILURE POSITIVE
When:

PRICE TRUST EVIDENCE
and
TRANSFER TRUST EVIDENCE

independently fail together,
that agreement is useful meta-evidence that the common source/provenance is unhealthy.

A bounded joint-hazard signal can accelerate suppression of BOTH authorities.

This improves combined-fault fulfillment from:

0.868
with fully independent typed trust

to:

approximately 0.900,

while not affecting the price-only case
and only minimally affecting the transfer-only case.

CORE ARCHITECTURAL RESULT
H50 rejects two extremes.

EXTREME 1:
ONE TRUST NUMBER PER SOURCE.

This causes cross-channel interference.

EXTREME 2:
COMPLETELY ISOLATED TRUST CHANNELS.

This fails to exploit genuinely corroborated source-level failure.

Preferred abstraction:

SHARED PROVENANCE IDENTITY

+

SEPARATE TYPED AUTHORITY STATE

+

OPTIONAL JOINT-HAZARD CORROBORATION.

RELATION TO H23
H23 established:

SHARE THE UPDATE MOTIF,
NOT THE TRUST SCALAR.

H50 validates the same rule in a concrete systems interface.

Price trust
and
transfer trust

can share:
- provenance;
- source identity;
- update machinery;
- anomaly history.

They should not automatically share:
one authority magnitude.

RELATION TO H28 / H48
H28:
resource-transfer state needs:
transaction identity
+
generation validation
+
idempotence.

H48:
price state needs:
source identity
+
freshness
+
duplicate collapse
+
local cross-check.

H50:
the two channels may come from the same neighbor,
but their trust semantics remain distinct.

CURRENT NEIGHBOR PROVENANCE OBJECT
A local peer can conceptually carry:

SOURCE ID / GENERATION

+

PRICE TRUST

+

TRANSFER TRUST

+

PRICE FRESHNESS

+

TRANSFER FULFILLMENT HISTORY

+

JOINT HAZARD / SOURCE HEALTH

+

OPTIONAL COPY / FAMILY PROVENANCE.

This is compact typed state,
not two independent controllers.

GENERAL PRINCIPLE
PROVENANCE SHOULD BE SHARED.

AUTHORITY SHOULD BE TYPED.

CROSS-CHANNEL FAILURE MAY INFORM SOURCE HEALTH,
BUT SHOULD NOT ERASE OTHERWISE VALID CHANNEL STATE WITHOUT EVIDENCE.

HARD LIMIT
If a faulty source can make:
its price messages
and
its transfer behavior

look mutually consistent
while both remain harmful,
joint corroboration can become false reassurance.

Thus:
CROSS-CHANNEL AGREEMENT
IS NOT
CAUSAL VALIDITY.

Direct local consequence remains necessary.

DECISION
AR-H50 is POSITIVE.

Supported synthetically:

- one shared trust scalar creates cross-channel interference;
- price-only faults should not destroy transfer authority;
- transfer-only faults should not destroy price authority;
- typed trust preserves unaffected capability;
- correlated failure across independently measured channels can accelerate source-level hazard suppression;
- shared provenance can coexist with separate authority state.

Not demonstrated:

- real Yggdrasil peer/source-health representation;
- optimal cross-channel hazard coupling;
- subtle mutually consistent dual-channel manipulation;
- topology churn during simultaneous price/transfer faults;
- multi-hop provenance for coupled channels.

NEXT CLEAN QUESTION
AR-H51 — MUTUALLY CONSISTENT DUAL-CHANNEL MANIPULATION

Question:

What if a faulty region manipulates BOTH:
price advice
and
resource transfer

in a mutually consistent way?

Example:

advertise high scarcity

and

withhold resource,

so the two channels agree.

A joint-hazard rule may interpret that agreement as:
real scarcity

rather than:
coordinated manipulation.

Compare:

A.
typed trust + joint corroboration;

B.
independent local resource consequence;

C.
matched neighboring controls;

D.
functional cost of obeying the advertised scarcity;

E.
real genuine scarcity event with the same two-channel signature.

Desired:

coordinated false scarcity
->
do not permanently suppress structural growth.

genuine scarcity
->
price and transfer restrictions should still be respected.

This is another causal-identifiability problem,
not merely a filtering problem.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
local_sources = 4
fault_interval = 280..559
primary_trust_alpha = 0.06
price_fault_delta = 0.45
clean_transfer_fulfillment = 0.90
faulty_transfer_fulfillment = 0.12
primary_matched_seeds = 50..60
