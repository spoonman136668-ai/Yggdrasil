TITLE: DG-1A-AR-H145 — Post-Blastema Maturation / Critical-Plasticity Window + Directed Evidence Routing Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh144-topology-blastema-audit.ice

PURPOSE

H144 established:

DE-NOVO
TOPOLOGY
RE-DEVELOPMENT

can recover
from:

broad scaffold corruption.

H144 also exposed a new split:

A TOPOLOGY
CAN BE
STRUCTURALLY CORRECT

while:

MOST MEMBERS
ARE STILL
TOO UNDER-EVIDENCED
FOR
BROAD ACTION.

At low evidence budget:

0.5N pairs / episode

the regenerated partition reached:

high structural agreement

while:

mean quarantine remained:
approximately 94%.

Therefore:

REGENERATION

and:

MATURATION

are:
different developmental phases.

H145 asks:

AFTER
A NEW TOPOLOGY
HAS BEEN
STRUCTURALLY RECOVERED,

HOW SHOULD
THE ORGANISM
SPEND
ITS NEXT
FEW AUDITS

SO THAT:

THE STRUCTURE
BECOMES
ACTIONABLE

WITHOUT:

RE-AUDITING
EVERY MEMBER

OR:

REMAINING
PERMANENTLY
PLASTIC?

BOUNDARY

Synthetic research only.

No biological tissue implementation.

The biological phrase:

critical plasticity window

is used only as:
an architectural analogy

for:

a temporary period
of elevated structural revisability

followed by:
consolidation.

H145 does not:

- claim biological equivalence;
- implement biological cells;
- establish production confidence thresholds;
- execute or modify STAB-18-R1;
- spend canonical scientific execution;
- authorize runtime activation.

EVIDENCE CLASS TARGET

SYNTHETIC
MEASURED_SANDBOX
POST-REGENERATION

PRIMARY STATE

Family size:

60..100.

Accepted regenerated topology:

3..8 regions.

The accepted topology is:

95% structurally correct

in the primary ecology.

A separate control uses:

100% correct topology.

A harder stress uses:

90% correct topology.

Incorrect members are:

misassigned to another accepted region.

No policy receives:

the true partition.

Each member has:

- accepted region;
- active/inactive state;
- positive value;
- local evidence ledger;
- quarantine state.

PRIMARY MEMBER MATURATION CONTRACT

A member may participate in:
broad region action

only when:

own-region effective observations >= 6

AND

own-region compatible support >= 0.65

AND

support margin over:
best alternative region

>= 0.10.

This is intentionally inherited from:

H142 / H143.

A member failing the contract remains:

QUARANTINED.

LOCAL REASSIGNMENT CONTRACT

During the plastic maturation window:

a member may move
to another accepted region

only when:

alternative support >= 0.70

AND

alternative observations >= 6

AND

alternative support margin >= 0.15.

No:
split
or:
merge

occurs inside the primary maturation phase.

If evidence indicates:
region-level structural failure,

the correct response is:
reopen H144 blastema logic,

not:
invent an unbounded local topology mutation lane.

PRIMARY HORIZON

30 post-promotion episodes.

Active fraction per episode:

20%..50%.

Member values:

positive lognormal,
mean approximately one,
sigma 0.60.

Evidence sensor error:

5%.

Primary evidence budget:

0.5N pair observations / episode.

This deliberately targets:
the H144 low-budget maturation failure.

ROBUSTNESS BUDGET

0.25N,
0.5N,
N,
2N.

ROBUSTNESS SENSOR ERROR

1%,
5%,
10%,
20%.

ROUTING POLICIES

A — UNIFORM

Sample pairs uniformly.

No member,
boundary,
or:
value prioritization.

B — QUARANTINE-FIRST

Prefer pairs touching:
quarantined members.

Inside that set:
uniform.

C — BOUNDARY-FIRST

Prefer members with:
the smallest current support margin.

For a selected member:

alternate between:

- same-accepted-region evidence;
- strongest competing-region evidence.

This explicitly tries to decide:

MEMBER BELONGS HERE

versus:

MEMBER BELONGS ELSEWHERE.

D — VALUE-FIRST

Prefer:

high-value
active
quarantined members.

Then:

buy evidence needed
to release
or:
reassign them.

E — EXPECTED-RELEASE

For each quarantined member:

estimate:

expected quarantined-value release
per additional audit.

Prioritize:

members closest to:

the maturation contract

weighted by:

current active value.

Evidence direction:

- if own-region observations are insufficient:
  probe accepted-region core;

- if own support is weak:
  probe accepted-region core;

- if support margin is weak:
  probe strongest alternative region.

F — HYBRID-MATURATION

Primary candidate.

Evidence allocation:

50%:
EXPECTED-RELEASE.

25%:
BOUNDARY-FIRST.

15%:
VALUE-FIRST.

10%:
uniform exploration.

The exact fractions above
are frozen before execution.

CORE EXEMPLARS

A member can serve as:
a region evidence exemplar

only when:

it already satisfies:
the maturation contract

and:

its accepted-region support >= 0.80.

If a region has no mature exemplar:

routing falls back to:
random members
inside that accepted region.

No latent true label
is used.

PLASTICITY SCHEDULES

P0 — LOCKED

No reassignment after blastema promotion.

Only:
quarantine release.

P10 — 10-EPISODE WINDOW

Local reassignment allowed:
episodes 1..10.

Then:
topology memberships lock.

P20 — 20-EPISODE WINDOW

Reassignment allowed:
episodes 1..20.

PERSISTENT — ALWAYS PLASTIC

Local reassignment remains allowed:
all 30 episodes.

The primary routing comparison uses:

P10.

A separate plasticity-window comparison
uses:

HYBRID-MATURATION

under:

P0,
P10,
P20,
PERSISTENT.

CONSOLIDATION CONTRACT

The topology is:
ACTION-MATURE

when:

for two consecutive checkpoints:

- >=80% of active value is non-quarantined;
- false-release proxy <=2%;
- no region has >20% of its active value quarantined;
- no unresolved high-value member exceeds:
  10% of current total active value.

Checkpoints:

every 3 episodes.

After maturation:

scratch reconstruction
and:
maturation-specific routing

hibernate.

Maintenance evidence becomes:

0.10N pairs / episode.

The 30-episode experiment continues
to test:
whether maturation remains stable.

PRIMARY METRICS

1. episodes to action maturity;
2. action-maturity success by episode 30;
3. evidence audits to maturity;
4. active-value coverage;
5. quarantined value fraction;
6. member reassignment count;
7. correct reassignment fraction;
8. false-release rate;
9. high-value false release;
10. evidence per unit quarantined value released;
11. maintenance stability after consolidation;
12. maturity reversals;
13. routing concentration / starvation.

PRIMARY ACCEPTANCE SHAPE

Post-blastema maturation is supported if:

- at 0.5N evidence, HYBRID-MATURATION reaches action maturity materially more often than UNIFORM;
- HYBRID releases substantially more active value than UNIFORM without a material increase in false release;
- EXPECTED-RELEASE or HYBRID improves evidence-per-released-value over QUARANTINE-FIRST;
- BOUNDARY-FIRST reduces incorrect member release when the accepted scratch topology contains 5% misassignments;
- at least one bounded plasticity window outperforms both P0 and PERSISTENT on the safety/coverage frontier;
- consolidation reduces ongoing maturation compute without causing immediate coverage collapse;
- high-value misassigned members are preferentially repaired or quarantined rather than falsely matured;
- no policy requires full all-pairs evidence.

FAILURE CONDITIONS

Treat H145 as mixed/negative if:

- directed routing does not beat uniform evidence;
- value-first routing systematically sacrifices low-value boundary safety;
- expected-release routing creates evidence starvation for hard members;
- bounded plasticity cannot repair the 5% scratch error;
- persistent plasticity is always superior without churn cost;
- consolidation locks incorrect memberships faster than they can be repaired;
- action maturity is achieved only by relaxing the inherited member-evidence contract;
- low evidence budget makes maturation effectively impossible under every routing policy.

HARD MISASSIGNMENT STRESS

Force:

one high-value active member

to be:
misassigned after scratch reconstruction.

Compare:

UNIFORM,
VALUE-FIRST,
BOUNDARY-FIRST,
EXPECTED-RELEASE,
HYBRID.

Desired:

the system should not:

"mature"
the wrong membership

merely because:
the member is valuable.

Value may prioritize:

EVIDENCE ACQUISITION.

It may not:

override:
membership validity.

TRANSIENT-NOISE STRESS

Episodes 8..12:

sensor error temporarily rises.

Compare:

P10,
P20,
PERSISTENT.

Desired:

a bounded plasticity window
should permit:
needed early repair

without:
allowing late transient noise
to cause indefinite membership churn.

LATE-REAL-CHANGE STRESS

After consolidation:

episode 24

one small true member subset
changes functional region.

The matured topology must not:

silently stay wrong forever.

It should:

raise:
a structural alarm

and:

reopen:
H144-style regeneration / repair authority

rather than:

keeping:
permanent high plasticity.

This is a diagnostic stress.

It does not authorize:
a second scheduler
or:
a second orchestration authority.

OUT-OF-BOX DEVELOPMENTAL INTERPRETATION

H145 tests a three-stage structural lifecycle:

1.
BLASTEMA

recover:
global structure.

2.
MATURATION

route:
evidence toward
under-supported members
and:
boundaries.

3.
CONSOLIDATION

reduce:
plasticity
and:
active structural compute.

Damage later may:

REOPEN
the cycle.

This is different from:

always-plastic learning.

It creates:

PUNCTUATED
STRUCTURAL PLASTICITY.

EXTERNAL CONCEPTUAL CROSS-CHECK

This is context,
not evidence.

Recent work on:

dynamic spectral community tracking

supports treating:
community structure

as:
temporally evolving
rather than:
independent static clusterings.

Graph sparsification work
also supports the broader possibility that:

sparse relational evidence

can preserve:
spectral structure

if:
approximation error
is tracked.

Separately,
2025 axolotl positional-memory research
reports:
reprogrammable positional identity
during regeneration.

For Yggdrasil,
the useful abstraction is only:

A TEMPORARY
REPROGRAMMABLE STATE

CAN LATER
RE-STABILIZE.

No biological implementation is inferred.

FROZEN BEFORE EXECUTION

Primary state,
member maturation contract,
reassignment contract,
horizon,
budget,
sensor error,
routing policies,
hybrid fractions,
plasticity schedules,
consolidation contract,
metrics,
acceptance shape,
failure conditions,
and stresses above

are fixed before execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = SYNTHETIC_MEASURED_SANDBOX_POST_REGENERATION
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = f592bc0abcd5d665ac4735f75b906cb1081c61d3
