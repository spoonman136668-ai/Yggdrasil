TITLE: DG-1A-AR-H43 — Decentralized Shared-Template Version Convergence Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE DISTRIBUTED-CONVERGENCE RESULT + LAST-WRITER/RELAY-AUTHORITY NEGATIVES
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh42-value-gated-functional-template-validation-audit.ice

PURPOSE
H36-H42 still treated a family template as one logically shared object.

H43 removes that hidden centralization.

QUESTION
Can several lineage fragments maintain and converge a shared generative template using:
- local replica state;
- local candidate versions;
- delayed gossip;
- independent functional validation;

without:
- a central template server;
- synchronous global commit;
- last-writer-wins authority;
- raw message-count voting?

BOUNDARY
This is synthetic.

It does not:
- freeze a production distributed protocol;
- define final replica count;
- establish Byzantine security;
- authorize global consensus infrastructure;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

DISTRIBUTED FAMILY
Template fragments:
8.

The fragments are split into two communication groups during a temporary partition.

Each fragment retains:
- local live template value;
- local version lineage / counter;
- local functional canary access.

After reconnection:
candidate versions are exchanged only by delayed peer gossip.

No fragment has:
- a central authoritative template;
- a global scheduler;
- omniscient state.

FOCUSED TEMPLATE AXIS
For this version-convergence audit,
the family template is reduced to one synthetic coefficient axis.

Clean live value:
0.

Alternative candidate:
0.8.

Functional lineage variation SD:
0.55.

Functional consequence noise SD:
0.25.

VALIDATION
Each replica can evaluate candidate versions on local functional canaries.

Primary:
10 canary samples per local vote.

Votes are sent with asynchronous gossip delay:

1..5 synthetic blocks.

A replica promotes only after receiving:
at least 3 independent fragment votes
supporting the same candidate.

This quorum is an exploratory research device only.

SCENARIO A — POISONED HIGH-COUNTER REPLICA
True family remains:

0.

During the partition,
one isolated fragment receives a poisoned update stream and advances its local candidate to:

0.8.

Its local version counter becomes:

10,

while clean replicas remain around:
version 2.

Thus the poisoned replica is syntactically newer.

LAST-WRITER-WINS COMPARATOR
On reconnection,
select the numerically newest version.

2,000 matched runs.

Correct convergence:
0%.

Final template error:
0.64.

PRIMARY LWW NEGATIVE
A higher version counter is evidence of:
more local writes.

It is NOT evidence of:
better shared-template validity.

Last-writer-wins deterministically propagates the poisoned replica in this stress.

FUNCTIONALLY VALIDATED GOSSIP
Candidates:
0
and
0.8

are compared through independent fragment canaries.

2,000 matched runs.

Correct convergence:
99.9%.

Mean convergence latency after reconnection:
3.36 blocks.

Median:
3.

Final error among converged correct runs:
0.

PRIMARY DISTRIBUTED POSITIVE
A shared generative template can converge without a central template server when:
- candidate identity is preserved;
- replicas exchange candidate versions;
- promotion authority comes from independent functional evidence.

Version order alone is not promotion authority.

SCENARIO B — LEGITIMATE FAMILY DRIFT
True family has actually moved to:

0.8.

One side of the partition has already learned the newer family state.

The other side still retains:
0.

LAST-WRITER-WINS

correct:
100%.

latency:
1 block.

FUNCTIONALLY VALIDATED GOSSIP

correct:
99.95%.

mean latency:
3.34.

median:
3.

PRIMARY SAFETY / PLASTICITY COST
Validation is slower than blindly choosing the newest version.

But the same mechanism that adds approximately:
2 to 3 blocks

of convergence delay

also protects against the poisoned-newest scenario.

SCENARIO C — MIXED STALE / POISONED NEWEST VERSION
True family:
0.8.

Several fragments hold the legitimate:
0.8

version.

One isolated fragment carries a higher-counter stale/poisoned candidate:

-0.2

with counter:
12.

LAST-WRITER-WINS

correct convergence:
0%.

Final squared error:
1.0.

FUNCTIONALLY VALIDATED GOSSIP

correct:
100%.

mean latency:
3.37.

median:
3.

PRIMARY VERSION-AUTHORITY PRINCIPLE
VERSION IDENTITY
and
VERSION ORDER

are necessary for:
provenance
and
deduplication.

They are not sufficient for:
functional authority.

A candidate version should carry:

PARENT VERSION

+

GENERATION / CREATION IDENTITY

+

PROVENANCE

+

VALIDATION STATE.

But:
newer
does not mean:
better.

RELAY-COPY VOTE STRESS
One poisoned validation fragment can emit relay copies of the same underlying vote.

Seven clean physical fragments each vote correctly with approximately:

96%

probability.

One poisoned physical fragment votes incorrectly with approximately:

96%

probability.

Relay copies are perfectly correlated with the poisoned source.

10,000 synthetic vote trials per condition.

RAW MESSAGE-COUNT VOTING

0 relays:
correct majority:
99.8%.

2 relays:
97.22%.

4 relays:
75.8%.

6 relays:
3.99%.

8 relays:
3.99%.

12 relays:
3.99%.

PRIMARY RELAY NEGATIVE
Enough copies of one poisoned validation source can overwhelm independent clean fragments if:
messages
rather than
provenance sources

receive authority.

PROVENANCE-COLLAPSED VOTING
Relay messages are collapsed to the physical/source provenance that generated them.

Across the same relay-count sweep:

correct majority remains approximately:

99.8%.

Thus:

COPIED VALIDATION VOTES
DO NOT CREATE
NEW TEMPLATE-PROMOTION AUTHORITY.

RELATION TO H40
H40 established this principle for canary families.

H43 shows it remains necessary in distributed replica convergence.

A distributed protocol can still accidentally centralize authority in:
message multiplicity

unless:
source provenance
is preserved.

SPLIT-BRAIN INTERPRETATION
Temporary partition can produce:
multiple candidate versions.

That alone is not failure.

The failure would be:
treating local candidate authority as global irreversible authority.

The safe architecture is:

LOCAL VERSION MAY EXIST

while

GLOBAL/FAMILY PROMOTION REMAINS UNRESOLVED.

After reconnection:
independent functional evidence decides which version deserves wider authority.

CURRENT DISTRIBUTED TEMPLATE OBJECT
Each candidate should conceptually carry:

TEMPLATE FAMILY ID / FIT CONTEXT

+

VERSION ID

+

PARENT VERSION

+

CREATOR / SOURCE PROVENANCE

+

CREATION GENERATION

+

LOCAL VALIDATION STATE

+

PROMOTION TRUST

+

FUNCTIONAL CANARY EVIDENCE.

No single field supplies authority.

GENERAL PRINCIPLE
DISTRIBUTION
DOES NOT REQUIRE
LAST-WRITER-WINS.

And:

EVENTUAL CONVERGENCE
DOES NOT REQUIRE
A CENTRAL TEMPLATE SERVER.

A family template can behave more like:
a versioned developmental hypothesis

than:
one mutable global variable.

DECISION
AR-H43 is POSITIVE.

Supported synthetically:

- temporary partitions can produce divergent local template versions without permanent failure;
- last-writer-wins is unsafe when a poisoned/stale replica has the highest counter;
- independent functional validation recovers the correct shared version after reconnection;
- legitimate newer versions still converge through validation with modest added latency;
- raw relay-copy voting recreates provenance inflation;
- provenance-collapsed fragment voting resists relay domination.

Not demonstrated:

- production distributed consensus;
- full multi-dimensional basis-version merging;
- concurrent valid divergent family specializations;
- partially connected long-lived partitions;
- replica death during convergence;
- safe local use of unpromoted candidate versions.

NEXT CLEAN QUESTION
AR-H44 — LOCAL USE OF UNPROMOTED TEMPLATE VERSIONS DURING PARTITION

Question:

During a long partition,
should a fragment be allowed to USE a locally promising template candidate before family-wide validation is possible?

Compare:

A.
never use unpromoted versions;

B.
immediate local use;

C.
bounded local lease / reversible provisional expression;

D.
poisoned local candidate;

E.
legitimate local family shift.

Desired:

legitimate local shift
->
temporary local adaptation without waiting indefinitely for reconnection.

poisoned candidate
->
bounded local blast radius.

reconnection
->
candidate can either:
promote,
rollback,
or remain local specialization.

This should reuse:
H6/H25 separation of
stored state
from
current authority.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
replica_fragments = 8
primary_reconnection_runs_per_scenario = 2000
functional_vote_batch = 10
functional_vote_quorum = 3
gossip_delay_blocks = 1..5
relay_vote_trials = 10000
