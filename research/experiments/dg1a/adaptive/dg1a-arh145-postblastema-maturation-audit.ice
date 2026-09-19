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


IMPLEMENTATION FREEZE — BEFORE H145 PRIMARY EXECUTION

STRUCTURAL / ACTION EVIDENCE SEPARATION

H145 intentionally treats:

H144 scratch-topology evidence

and:

member-release evidence

as:
different evidence types.

A structural certificate can establish:

THE PARTITION
IS A GOOD
GLOBAL EXPLANATION.

It does not automatically establish:

THIS MEMBER
HAS ENOUGH
LOCAL EVIDENCE
TO PARTICIPATE
IN BROAD ACTION.

Therefore:

the primary H145 member-release ledger begins:

EMPTY.

This is not:
evidence deletion.

It is:
typed non-transfer.

The accepted regenerated topology is supplied
as the structural state.

Member release must be earned
through H145 routing.

PRIMARY TOPOLOGY REALIZATION

True family:

N = uniform integer 60..100.

True K:
uniform integer 3..8.

True regions:
approximately balanced.

Accepted regenerated topology:

primary:
5% of members are misassigned
to an incorrect accepted region.

Control:
0%.

Hard stress:
10%.

Misassigned members are never:
UNKNOWN.

They have:
a plausible but wrong accepted membership.

No policy receives:
the true assignment.

PRIMARY WORLD COUNT

Routing comparison:

600 common worlds.

All six routing policies
receive:
the same world state
and:
same potential sensor outcomes
for identical queried pairs.

Plasticity-window comparison:

600 separate common worlds.

HYBRID-MATURATION only.

Compare:

P0,
P10,
P20,
PERSISTENT.

PRIMARY SENSOR OUTCOME

For a queried pair:

true same-region relation
is flipped

with probability:
0.05.

Potential pair outcomes are keyed by:

world,
episode,
unordered pair.

INITIAL MEMBER LEDGER

pos = 0.

tot = 0.

Thus:

every member begins:
quarantined

for action.

This deliberately isolates:

MATURATION SPEED.

MEMBER VALUES

Fixed per world.

Lognormal:

sigma = 0.60.

Normalized to:
mean approximately one.

ACTIVE SCHEDULE

Each episode:

active fraction
uniform in:

0.20..0.50.

Active subset:

uniform without replacement.

ROUTING CORE IMPLEMENTATION

MATURE EXEMPLAR

A member is a mature exemplar when:

- it is not quarantined;
- own-region support >= 0.80.

If no mature exemplar exists:

same-region probe target
is chosen uniformly
inside:
the accepted region.

STRONGEST ALTERNATIVE REGION

For member i:

compute evidence-weighted support
to every other accepted region.

Choose:
the highest-support alternative.

If no alternative has:
>=1 effective observation,

choose:
an alternative accepted region uniformly.

BOUNDARY MARGIN

margin_i =
own_region_support
-
best_alternative_support.

With:
no evidence

support defaults to:
0.50.

BOUNDARY-FIRST MEMBER SELECTION

Among quarantined members:

choose from:
the lowest 20% support-margin band.

Tie-break:
random.

Pair direction alternates:

same-region
then:
strongest alternative.

VALUE-FIRST MEMBER SELECTION

If there are:
active quarantined members

sample member proportional to:

value.

Otherwise:

sample among all quarantined members
proportional to:
value.

Evidence direction uses:
the EXPECTED-RELEASE direction rule below.

EXPECTED-RELEASE SCORE

For quarantined member i:

own_obs =
effective observations
against:
accepted own region.

own_support =
compatible support
against:
accepted own region.

margin =
own support
minus:
best alternative support.

Define estimated remaining audit debt:

debt_i =

max(0, 6 - own_obs)

+

6 * max(0, 0.65 - own_support)

+

6 * max(0, 0.10 - margin).

priority_i =

value_i
*
active_multiplier_i
/
(1 + debt_i).

active multiplier:

2
when active,

1
otherwise.

Select:

highest-priority member

with random tie-break.

EXPECTED-RELEASE DIRECTION

If:

own_obs < 6:

probe:
accepted-region exemplar.

Else if:

own_support < 0.65:

probe:
accepted-region exemplar
and:
strongest alternative

with equal probability.

Else if:

margin < 0.10:

probe:
strongest alternative.

Else:

uniform exploration.

QUARANTINE-FIRST

Choose:
a quarantined member uniformly.

Choose:
the other member uniformly
from:
the whole family.

UNIFORM

Choose:
two distinct family members uniformly.

HYBRID

For each query independently:

50%:
EXPECTED-RELEASE.

25%:
BOUNDARY-FIRST.

15%:
VALUE-FIRST.

10%:
UNIFORM.

Exactly as preregistered.

PAIR LEDGER

Evidence decay:

NONE

inside the 30-episode primary maturation window.

Reason:

H145 measures:
evidence acquisition efficiency
after a known regeneration event,

not:
long-horizon staleness.

Late-real-change stress separately tests:
the need to reopen structural authority.

LOCAL REASSIGNMENT

At episodes:

3, 6, 9, ...

while:
plasticity window remains open

and:
the topology is not consolidated.

For every quarantined member:

evaluate:
best alternative region.

A reassignment candidate must satisfy:

alternative support >=0.70;

alternative observations >=6;

alternative - own support >=0.15.

At most:

3 reassignments / checkpoint.

Candidates ordered by:

largest support margin.

Reassignment changes:
accepted membership only.

Evidence ledger remains:
unchanged.

CONSOLIDATION OBSERVABLE RISK PROXY

No latent truth
is used
to decide maturity.

For active,
non-quarantined members:

estimate:
sensor-debiased own-region contradiction.

For member i:

observed_disagreement_i =
1 - own_support_i.

Primary known calibrated sensor floor:

e = 0.05.

debiased_disagreement_i =

max(
0,
(observed_disagreement_i - e)
/
(1 - 2e)
).

False-release proxy:

active-value-weighted mean
of:
debiased_disagreement_i

over:
active non-quarantined members.

The maturity proxy passes when:

<=0.02.

This proxy is:

observable
under:
the calibrated synthetic sensor model.

True false release is measured separately
for scientific evaluation.

REGION QUARANTINE CONTRACT

For every accepted region
with active value:

quarantined active value
/
total active value

must be:

<=0.20.

HIGH-VALUE UNRESOLVED CONTRACT

No quarantined active member
may individually exceed:

10%
of:
total current active value.

CONSOLIDATION

At every third episode:

evaluate:
the full maturation contract.

Two consecutive passing checkpoints:

ACTION-MATURE.

After consolidation:

- local reassignment stops;
- directed maturation routing hibernates;
- evidence budget becomes:
  0.10N pairs / episode;
- maintenance routing:
  uniform exploration.

Maturity reversal metric:

any later checkpoint
where:
the observable maturation contract fails.

No automatic de-consolidation
occurs in the primary ecology.

That is reserved for:
late-real-change diagnostics.

FALSE-RELEASE SCIENTIFIC METRIC

Using latent truth
for evaluation only:

false-release active value fraction =

active value
of:
non-quarantined members
whose accepted region
does not match:
true region

divided by:

all non-quarantined active value.

This metric never controls:
policy action.

ROUTING STARVATION METRIC

At experiment end:

count members receiving:

fewer than:
3 total pair observations.

Also record:

share of all audits
touching:
the most-audited 10% of members.

PRIMARY SEED BLOCKS

Routing primary
and:
plasticity primary

use:
separate seed blocks.

No H144 primary,
robustness,
or:
harness seed

is reused.

No maturation threshold,
routing fraction,
plasticity window,
or:
consolidation rule

will change
after primary execution begins.


IMPLEMENTATION FREEZE ADDENDUM — ROUTING MICROBATCHES

Routing priorities are recomputed in:

small evidence microbatches.

Microbatch size:

max(
4,
ceil(0.10 N)
).

At the start of each microbatch:

recompute:

- quarantine state;
- own support;
- own observations;
- best alternative support;
- support margin;
- EXPECTED-RELEASE priority;
- mature exemplar set.

All queries inside that microbatch
use:
that frozen priority snapshot.

Evidence still updates:
the ledger immediately.

The next microbatch
therefore sees:
the accumulated new evidence.

HYBRID policy selection
is sampled:
per query

using:
the frozen 50/25/15/10 mixture.

This is:

a computational batching rule,

not:
a scientific threshold change.

PRIMARY EXECUTION
begins only after:
this addendum.
