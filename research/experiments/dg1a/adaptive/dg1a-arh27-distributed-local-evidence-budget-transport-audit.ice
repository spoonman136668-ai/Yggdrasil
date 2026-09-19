TITLE: DG-1A-AR-H27 — Distributed Local Evidence-Budget Transport Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE DECENTRALIZED-TRANSPORT RESULT + BID-TRUST LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh26-shared-evidence-budget-contention-audit.ice

PURPOSE
H26 showed that several adaptive layers can share one bounded evidence economy using:

marginal value
+
anti-starvation/bootstrap access.

However H26 still used one abstract shared token pool.

H27 removes that centralized abstraction.

QUESTION
Can a spatially distributed developmental organism move evidence/resource tokens toward valuable local uncertainty using only:

- local resource state;
- local demand / value signal;
- neighborhood communication;
- conservative local transfer;

without:
- a global queue;
- one global scheduler;
- a global role histogram;
- or omniscient global routing?

BOUNDARY
This is synthetic.

It does not:
- prove the exact transport rule belongs in Yggdrasil;
- freeze the lattice topology;
- freeze signal-propagation depth;
- establish biological energy accounting;
- authorize a centralized scheduler;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SPATIAL ORGANISM
Grid:
12 x 12

cells:
144.

Per-step total synthetic evidence/resource supply:
95 units.

Supply is spatially heterogeneous.

Primary generation:
18 source cells
+
small background supply.

Demand is spatially localized into two smooth high-value regions.

Each cell has:
- local resource amount;
- local demand capacity;
- local marginal value.

GLOBAL ORACLE
A diagnostic upper bound pools all 95 resource units globally and allocates them to the highest-value available demand.

This is NOT an allowed operational mechanism.

All reported utility ratios are relative to this global oracle.

LOCAL OWNERSHIP
Each cell can use only the resource generated at its own location.

No movement.

UNDIRECTED DIFFUSION
Resource diffuses locally across nearest-neighbor edges for four rounds.

The diffusion does not see functional demand.

LOCAL PRICE / DEMAND TRANSPORT
Each cell forms a local marginal bid from:

local value
*
unmet local demand.

The bid is propagated only through nearest-neighbor communication.

Resource moves conservatively along the locally observed uphill price gradient.

Primary transport:

6 movement rounds.

Price propagation:

4 nearest-neighbor rounds.

No cell has global state.

No cell can directly select a non-neighbor destination.

PRIMARY STATIONARY CONFIRMATION
40 matched spatial seeds.

LOCAL OWNERSHIP

oracle-relative utility:
0.24760
SD:
0.04077.

high-demand dead-zone fraction:
0.9000
SD:
0.0522.

UNDIRECTED DIFFUSION

utility:
0.43633
SD:
0.06256.

dead-zone:
0.91827
SD:
0.0765.

LOCAL PRICE TRANSPORT

utility:
0.63390
SD:
0.04612.

dead-zone:
0.51442
SD:
0.0814.

PRIMARY POSITIVE
Purely local demand-directed transport recovers substantially more of the globally pooled upper-bound value than:

local ownership

or

undirected diffusion.

The improvement is not merely from moving tokens.

Undirected diffusion moves tokens too,
but it does not know which local regions currently have high marginal functional value.

Thus:

RESOURCE MOBILITY
and
RESOURCE DIRECTION

are separate requirements.

IMPORTANT DIFFUSION NEGATIVE
Undirected diffusion improves total utility relative to immobile ownership
while slightly worsening the fraction of strongly under-served high-demand cells in this benchmark.

Reason:

diffusion smooths the resource field
rather than concentrating it into high-value demand zones.

Therefore:

EVEN RESOURCE DISTRIBUTION
IS NOT THE SAME AS
FUNCTIONALLY USEFUL RESOURCE DISTRIBUTION.

HOTSPOT RELOCATION STRESS
Demand hotspots move at:

step 150.

Primary transport retains a recency-weighted local price memory.

Price-memory update rate:

0.08.

30 matched seeds.

PRE-SWITCH STEADY ORACLE-RELATIVE UTILITY

0.63646
SD:
0.04753.

FIRST 20 POST-SWITCH STEPS

0.57541
SD:
0.05584.

NEW STEADY WINDOW

0.62237
SD:
0.05259.

95%-of-new-steady recovery latency:

mean:
5.57 steps.

median:
5.

PRIMARY RELOCATION RESULT
Local transport can follow a moving high-demand region without centralized reassignment.

A finite price-memory hangover exists,
but it decays over a small number of local update steps.

This is desirable:

some continuity

without

permanent resource ownership.

HIGH-DEMAND CONTRACTION / DISAPPEARANCE
A separate run removes the two localized high-demand regions after step 200,
leaving only low uniform background demand.

30 matched seeds.

PRE-DISAPPEARANCE utility:
0.63646.

FIRST 20 POST-DISAPPEARANCE:
0.58199.

LATE POST-DISAPPEARANCE:
0.91844.

whole-grid severe under-service fraction:

early:
0.46799.

late:
0.02870.

PRIMARY RELEASE RESULT
Resource transport does not remain permanently captured by an old high-demand region.

Once local price memory decays,
resource redistributes across the low-demand tissue.

This supports:

TEMPORARY RESOURCE CONCENTRATION

rather than:

PERMANENT RESOURCE OWNERSHIP.

LOCAL BID-MONOPOLY STRESS
A false local bid field is injected into a low-value region.

The decoy occupies:

13 of 144 cells

approximately:
9.0% of the grid.

The false bid is strong,
but does not correspond to real functional demand.

40 matched seeds.

NO DECOY BASELINE

local-price utility:
0.63390.

UNGATED FALSE BID

utility:
0.52522
SD:
0.06808.

fraction of all resource pulled into the decoy region:
0.22420
=
22.4%.

PRIMARY MONOPOLY NEGATIVE
A persistent high local bid can create spatial resource capture even under a conservative nearest-neighbor transport rule.

Thus:

DECENTRALIZATION
DOES NOT AUTOMATICALLY PREVENT
LOCAL MONOPOLY.

A bad local price can propagate influence through the neighborhood and attract real resource.

TRUST-WEIGHTED BID
Reuse the generic trust architecture from H23-H26.

The false bid component receives low current authority:

trust:
0.08.

The real local demand component remains fully trusted.

Operational bid becomes approximately:

trusted real demand
+
trust_weight
*
untrusted excess demand signal.

RESULT

utility:
0.62958
SD:
0.04558.

resource in decoy region:
0.07772
=
7.8%.

Compared with ungated:

utility recovers from:
0.52522
to
0.62958.

Decoy resource capture falls from:
22.4%
to
7.8%.

The trusted result is close to the no-decoy baseline:
0.63390.

PRIMARY BID-TRUST POSITIVE
The same distinction established elsewhere now applies to distributed resource bids:

A DEMAND SIGNAL EXISTS

does not imply:

THAT SIGNAL DESERVES CURRENT RESOURCE-ROUTING AUTHORITY.

Local resource price should therefore be modulated by:
- source provenance;
- current trust;
- estimated resolvability;
- marginal value.

CONSERVATION / OVERSUBSCRIPTION AUDIT
100 random spatial resource/demand systems.

8 conservative transfer rounds.

Maximum absolute resource-conservation error:

2.84e-14

synthetic units.

Mean absolute error:

9.24e-15.

Minimum observed cell resource:

0.00478.

No negative resource state occurred.

PRIMARY CONSERVATION RESULT
The tested local transfer rule is conservative.

Multiple neighboring demands do not create duplicate resource.

A cell can only transfer a bounded fraction of resource it actually holds.

This is a necessary property for a distributed evidence economy.

It is not sufficient for optimal allocation.

RELATION TO H26
H26 established:

marginal value
+
bounded fairness/bootstrap

for one abstract shared budget.

H27 shows a plausible decentralized interpretation:

LOCAL MARGINAL PRICE

diffuses through a neighborhood

and

RESOURCE MOVES CONSERVATIVELY UP THAT PRICE FIELD.

However H27 also adds:

PRICE AUTHORITY MUST ITSELF BE TRUSTED.

Otherwise:
one pathological region can become a resource sink.

RELATION TO H23-H25
H23:
share the meta-rule,
not one global trust scalar.

H25:
stored state
!=
current authority.

H27:

local demand signal
!=
current resource-routing authority.

The recurring design pattern is now:

LOCAL CAPABILITY / SIGNAL

+

TYPED CURRENT TRUST

->

CURRENT AUTHORITY.

NO CENTRAL SCHEDULER REQUIRED BY THE RESULT
The tested mechanism uses only:

nearest-neighbor price communication;

nearest-neighbor conservative token transfer;

local demand;

local trust.

The global oracle is used only for evaluation.

The result therefore supports the possibility of a decentralized resource economy.

It does NOT show the current transport is globally optimal.

PRIMARY LIMITATIONS
The current model assumes:
- a fixed grid;
- synchronous local updates;
- continuous divisible tokens;
- fixed transport cost;
- trusted location topology;
- static transport neighborhood;
- no cell birth/death during transport.

It also allows several price-propagation rounds per decision interval.

Real implementation cost must be measured separately.

DECISION
AR-H27 is POSITIVE WITH A BID-TRUST LIMIT.

Supported synthetically:

- local price-directed transport substantially outperforms immobile ownership and undirected diffusion;
- demand relocation can be followed with bounded lag;
- resource capture is reversible when demand disappears;
- conservative local movement prevents resource duplication / oversubscription;
- a false persistent local bid can create resource monopoly;
- typed trust on the bid signal can strongly suppress that monopoly.

Not demonstrated:

- optimal local transport law;
- real Yggdrasil token representation;
- transport under cell birth/death;
- asynchronous propagation;
- network topology changes;
- transport energy cost;
- global conservation under developmental growth.

NEXT CLEAN QUESTION
AR-H28 — ASYNCHRONOUS / TOPOLOGY-CHANGING RESOURCE TRANSPORT

Question:

Does the local price economy remain stable when:
- cells update at different times;
- links appear/disappear;
- cells divide or deactivate;
- the neighborhood graph changes while resource is in motion?

Primary risks:

- duplicate transfer after topology mutation;
- orphaned resource;
- price echoes;
- oscillatory back-and-forth transport;
- resource trapped in disconnected tissue;
- stale price propagation after cell death.

Desired:

strict local conservation;

bounded stale-price lifetime;

eventual release of stranded resource where connectivity returns;

no assumption of globally synchronized rounds.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
grid = 12x12
primary_stationary_seeds = 40
relocation_seeds = 30
disappearance_seeds = 30
decoy_monopoly_seeds = 40
conservation_random_systems = 100
per_step_total_resource = 95
