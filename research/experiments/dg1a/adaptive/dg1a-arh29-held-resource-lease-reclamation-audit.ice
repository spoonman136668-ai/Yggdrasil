TITLE: DG-1A-AR-H29 — Held-Resource Lease / Reclamation After Cell Death Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE SITE-ESCROW RESULT + DISCONNECTED-RESOURCE ACCESS LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh28-asynchronous-topology-resource-transport-audit.ice

PURPOSE
H28 preserved resource in transit under asynchronous delay, retry, and cell-generation change.

The remaining gap was different:

WHAT IF A CELL DISAPPEARS WHILE ALREADY HOLDING RESOURCE?

Strict accounting can still coexist with:
permanent resource unavailability.

H29 separates:

CONSERVATION

from

ACCESSIBILITY.

QUESTION
Can local tissue reclaim resource held by vanished cells without:
- central garbage collection;
- duplicate inheritance;
- resource inflation;
- automatic transfer of stale cell identity?

BOUNDARY
This is synthetic.

It does not:
- freeze a production substrate/escrow representation;
- establish biological extracellular energy semantics;
- require a fixed grid;
- solve resource recovery across permanently disconnected topology;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PRIMARY CLUSTER-DEATH STRESS
Spatial organism:

12 x 12
=
144 sites.

Initial total resource:
1000 units.

Resource is spatially heterogeneous.

A central 4 x 4 tissue block is intentionally resource-rich.

Mean resource initially held by the block:

32.67%
SD:
3.43%.

The entire 4 x 4 block disappears at once.

40 matched seeds.

COMPARATOR A — HARD CELL OWNERSHIP / LOSS
Resource owned by the dead cell disappears with that cell.

Mean final conserved resource:

67.33%
of initial.

Thus:
approximately one-third of the local adaptive resource is destroyed by cell death.

This violates the desired conservative resource economy.

COMPARATOR B — OLD-OWNER LOCK
Resource remains attributed to the dead cell identity.

Total accounting remains:

100%.

But accessible live-cell resource remains:

67.33%.

The resource is conserved
but unusable.

PRIMARY ACCESSIBILITY NEGATIVE
CONSERVATION
IS NOT
ACCESSIBILITY.

A resource system can be perfectly accounted for
while a large fraction is stranded behind extinct ownership.

COMPARATOR C — NAIVE AUTOMATIC REPLACEMENT INHERITANCE
At regeneration,
multiple replacement claims are allowed to inherit the prior cell's full resource.

This is an intentionally unsafe comparator.

Mean final resource:

132.67%
of initial.

The approximately:

32.67%

resource increase equals the original dead-region resource share.

Thus:

CELL REPLACEMENT
MUST NOT IMPLY
UNCONDITIONAL RESOURCE COPY.

Identity rollover needs explicit ownership transfer.

SITE-LEVEL ESCROW / LEASE
On cell death:

1.
the cell-owned resource is atomically removed from cell authority;

2.
the amount remains at the local spatial/site substrate as:

ESCROWED RESOURCE;

3.
no replacement cell automatically owns it;

4.
after lease expiry,
a live adjacent cell may claim the site escrow exactly once;

5.
if no live local claimant exists,
escrow remains locally conserved;

6.
when topology regenerates,
a valid new local generation may explicitly claim remaining site escrow.

Primary exploratory lease expiry:

5 steps.

The site escrow is:
resource state

not:
cell identity.

BOUNDARY RECLAMATION BEFORE REGENERATION
The 4 x 4 dead block remains absent until step 30.

After local lease expiry,
boundary escrows may be claimed by adjacent surviving cells.

Mean immediately accessible resource after death:

67.33%.

Mean accessible before regeneration:

92.06%.

Mean still trapped in disconnected interior escrows:

7.94%.

PRIMARY LOCAL-RECLAMATION POSITIVE
A purely local claim path recovers most resource from the boundary of the dead tissue.

No global sweep is required.

However:
interior resource with no live neighboring path remains unavailable.

This is correct.

The system does not teleport resource across disconnected topology.

REGENERATION
At step 30,
the dead 4 x 4 sites become occupied again by new cell generations.

New cells may claim only:
remaining local site escrow.

They do not inherit:
old cell identity
or
already reclaimed resource.

RESULT

final total resource:
100.000%.

final accessible resource:
100.000%.

between-seed numerical deviation:
approximately 1e-16.

No double inheritance occurred.

SCATTERED-DEATH STRESS
A separate benchmark removes:

10%

of sites randomly.

100 matched seeds.

Mean immediately accessible resource:

90.52%.

After local lease expiry and neighbor reclamation:

100.000%
accessible.

Remaining escrow:
0.

Total conservation:
100.000%.

INTERPRETATION
Scattered death is easy to reclaim because most lost sites remain adjacent to live tissue.

Clustered tissue loss is harder because topology itself creates an inaccessible interior.

Thus:

RESOURCE RECOVERY DEPENDS ON CONNECTIVITY.

COMBINED CELL-DEATH + IN-FLIGHT-TRANSFER STRESS
H29 is composed with H28's safe asynchronous transfer semantics.

Network:
64 local holders.

Initial resource:
1000.

At step:
1800

10 cells disappear simultaneously.

Any resource already owned by the cells moves to:
site escrow.

Any in-flight message targeting an invalid generation is:
not delivered.

Timed-out in-flight resource is refunded to:
the valid live sender
or
the sender site's escrow.

At step:
2600

the lost sites regenerate with new generations
and claim remaining local escrow.

50 matched seeds.

RESULT

mean final total resource:
1000.0000.

between-seed SD:
approximately 4.25e-14.

mean maximum conservation drift during the run:
1.98e-13.

final remaining escrow:
0.

all 64 sites active after regeneration.

PRIMARY COMPOSITION POSITIVE
The held-resource lease model composes cleanly with the H28 in-flight transaction model.

A cell can disappear while:
- holding local resource;
- having resource in flight;
- being the target of delayed transfers;

without:
- duplicate ownership;
- resource loss;
- stale-generation delivery.

RESOURCE OWNERSHIP STATES
The research now supports a stricter resource state machine.

A resource unit should be in exactly one state:

CELL-OWNED

or

SITE / LOCAL ESCROW

or

IN FLIGHT

or

CONSUMED.

Not:

owned by multiple descendants;

not:

simultaneously in flight and credited;

not:

implicitly attached forever to a dead cell ID.

CELL IDENTITY
and
RESOURCE LOCATION
must remain distinct.

LINEAGE INHERITANCE PRINCIPLE
A replacement/daughter cell should receive resource only through an explicit transition:

PARENT OWNERSHIP
->
LINEAGE / SITE ESCROW
->
NEW GENERATION CLAIM.

Not:

SAME LOCATION
->
AUTOMATIC FULL COPY.

RELATION TO H28
H28 solved:
resource in transit
under identity churn.

H29 solves:
resource already held
when identity disappears.

Together they define a local conservative lifecycle across:
send;
delay;
retry;
death;
replacement;
reclamation.

HARD CONNECTIVITY LIMIT
If an entire resource-containing region becomes topologically isolated
and no persistent local substrate remains connected to live tissue,
no purely local resource rule can make that resource immediately accessible elsewhere.

This is not a policy bug.

It is a connectivity constraint.

A conservative local system should prefer:

RESOURCE TEMPORARILY INACCESSIBLE

over:

RESOURCE DUPLICATED
or
TELEPORTED.

When connectivity returns,
explicit lease/claim semantics can restore accessibility.

DECISION
AR-H29 is POSITIVE WITH A DISCONNECTED-RESOURCE ACCESS LIMIT.

Supported synthetically:

- ephemeral cell ownership alone is unsafe for a conservative resource economy;
- conserved resource can still become operationally stranded;
- site-level escrow separates resource persistence from cell identity;
- local lease expiry allows neighboring tissue to reclaim dead-cell resource;
- clustered death exposes a real connectivity-limited inaccessible interior;
- regeneration can recover remaining escrow exactly once;
- site escrow composes with asynchronous in-flight transfer semantics without inflation or loss.

Not demonstrated:

- final site/substrate implementation;
- resource reclamation without any persistent local substrate;
- optimal lease duration;
- lineage-aware split fractions during cell division;
- resource semantics under simultaneous multi-daughter division;
- resource conservation when sites themselves are deleted from the graph.

NEXT CLEAN QUESTION
AR-H30 — CELL DIVISION / MULTI-DAUGHTER RESOURCE INHERITANCE

Question:

When one computational cell divides into multiple daughters,
how should:
- fast state;
- trust state;
- slow inherited priors;
- evidence/resource tokens;

be partitioned without:
- cloning scarce resource;
- duplicating causal authority;
- erasing useful lineage memory?

Compare:

A.
full copy to every daughter;

B.
equal split;

C.
function-weighted split;

D.
shared slow prior + split fast resource;

E.
temporary lineage escrow until daughter roles differentiate.

Primary risks:

- exponential resource inflation under repeated division;
- duplicated trust authority;
- over-correlated daughter evidence;
- premature fixed role inheritance;
- starvation of a daughter that becomes functionally critical.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
cluster_death_seeds = 40
scattered_death_seeds = 100
combined_async_death_seeds = 50
initial_resource = 1000
cluster_resource_share_mean = 0.32667
site_lease_expiry = 5
cluster_regeneration_step = 30
