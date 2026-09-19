TITLE: DG-1A-AR-H145 — Post-Blastema Maturation / Critical-Plasticity Window + Directed Evidence Routing Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh144-topology-blastema-audit.ice

PURPOSE

H144 established that:

de-novo relational reconstruction

can recover:
a globally damaged topology

without:
latent K
or:
original membership labels.

But H144 also exposed a second bottleneck:

STRUCTURAL RECOVERY
CAN OCCUR
BEFORE
ACTION MATURITY.

At low evidence budgets:

the recovered partition can be correct

while:
member-level support,
boundary support,
and:
action coverage

remain immature.

H145 asks:

HOW
SHOULD
A REGENERATED TOPOLOGY
MATURE
INTO
A CHEAPLY ACTIONABLE
STRUCTURE

WITHOUT:

RE-AUDITING EVERY MEMBER

OR:

REMAINING
PERMANENTLY PLASTIC?

BOUNDARY

Synthetic research only.

It does not:
- implement biological tissue;
- claim biological equivalence;
- establish production maturation thresholds;
- execute or modify STAB-18-R1;
- spend canonical scientific execution;
- authorize runtime activation.

EVIDENCE CLASS TARGET

SYNTHETIC
MEASURED_SANDBOX
POST-REDEVELOPMENT

ARCHITECTURAL PHASES

PHASE 1 — BLASTEMA

A de-novo topology has just been promoted.

Topology is:
provisionally fixed.

Broad action remains:
restricted.

PHASE 2 — MATURATION WINDOW

Structural plasticity is sharply reduced.

Evidence is routed toward:
the members and boundaries
whose verification most increases safe action coverage.

PHASE 3 — CONSOLIDATION

When the maturation contract is satisfied:

- broad action is enabled only on mature regions;
- scratch reconstruction machinery hibernates;
- topology mutation returns to normal bounded H143/H144 repair mode;
- directed maturation routing shuts down.

A mature topology should:

STOP
BEHAVING
LIKE
A WOUND.

PRIMARY ECOLOGY

Family size:
60..100.

True subfamilies:
4..6.

Promoted scratch topology quality:

PRIMARY:
98% member assignments correct.

ROBUSTNESS:
90%, 95%, 100%.

The residual wrong assignments are:
unknown to all policies.

Active fraction per episode:
20%..50%.

Member value:
positive lognormal,
mean approximately 1.

Maturation horizon:
20 episodes.

Primary sensor error:
5%.

Primary evidence budget:
0.5N pair observations / episode.

Robustness budgets:
0.25N,
0.5N,
1N,
2N.

RELATIONAL MATURATION EVIDENCE

Each evidence observation queries:
one member i

against:
one comparison member j.

Observation asks:

DO THESE TWO MEMBERS
CURRENTLY BELONG
TO THE SAME
FUNCTIONAL SUBFAMILY?

Sensor outcome is wrong with:
the frozen sensor-error rate.

Policies do not receive:
latent true labels.

For each member:

support is accumulated from:
- agreement with members assigned to its provisional region;
- disagreement with members assigned outside its provisional region.

Evidence is:
decayed at 0.95 / episode

during the maturation window.

MEMBER MATURITY CONTRACT

A member becomes:
ACTION-MATURE

only when:

effective observations >= 6

AND

estimated assignment support >= 0.80

AND

support margin above:
the strongest alternative region
>= 0.20.

A member remains:
QUARANTINED

otherwise.

Mature state is revocable
inside the maturation window

if:
fresh evidence violates the contract.

REGION MATURITY CONTRACT

A provisional subfamily becomes:
REGION-MATURE

only when:

- at least 70% of its current active-value mass
  belongs to action-mature members;

- at least 3 representative members
  satisfy the member maturity contract;

- sampled cut-boundary contradiction rate
  <= 5%.

Broad subfamily action is permitted only on:
region-mature
+
member-mature
members.

FAMILY MATURITY CONTRACT

The topology enters:
CONSOLIDATED

when:

- >=80% total active-value mass is action-mature;
- every provisional region has either:
  REGION-MATURE status
  or:
  explicit quarantine;
- no unresolved high-value member contributes
  >10% of current family active-value mass;
- the contract holds for:
  2 consecutive episodes.

After consolidation:

directed maturation routing stops.

Scratch lane:
HIBERNATES.

PRIMARY ROUTING POLICIES

A — UNIFORM

Query random member pairs.

B — UNCERTAINTY-FIRST

Prioritize members nearest:
the maturity threshold
or:
with conflicting support.

C — VALUE-FIRST

Prioritize:
currently active,
high-value,
unmature members.

D — BOUNDARY-FIRST

Prioritize:
low-margin members
and:
cross-region cut edges.

E — REPRESENTATIVE-CANARY

Spend evidence first on:
a small representative set
per provisional region.

Then:
expand only when region maturity is uncertain.

F — EXPECTED-RELEASE

Estimate:

expected active-value mass
released from quarantine
per additional audit.

Prioritize:
highest expected release / audit.

G — HYBRID

Score candidate evidence using:

boundary risk
+
active value
+
quarantine-release potential
+
minimum representative coverage.

No single term may consume:
more than 50%
of the episode evidence budget.

This prevents:
a pure value monoculture
or:
a pure boundary monoculture.

NEGATIVE COMPARATOR

H — PERMANENT-PLASTIC

Continue:
scratch / topology reconstruction work

throughout all 20 maturation episodes.

No consolidation.

This comparator tests whether:
continued structural plasticity
adds value

or:
wastes compute
after the partition is already mostly correct.

PRIMARY METRICS

1. episodes to 50% active-value maturity;
2. episodes to 80% active-value maturity;
3. consolidation rate by episode 20;
4. active safe-action coverage;
5. false mature-member rate;
6. false region-maturity rate;
7. high-value unresolved mass;
8. evidence observations to consolidation;
9. evidence observations per released active-value unit;
10. scratch / structural compute after promotion;
11. re-quarantine rate;
12. residual wrong-assignment discovery rate;
13. mature-member precision;
14. mature-member recall;
15. final quarantined fraction;
16. post-consolidation evidence cost.

PRIMARY ACCEPTANCE SHAPE

Post-blastema maturation is supported if:

- at least one directed-routing policy reaches 80% active-value maturity materially faster than UNIFORM;
- the winning directed policy uses fewer observations-to-consolidation than UNIFORM;
- mature-member precision remains >=99% in the primary 5%-sensor-error ecology;
- residual wrong assignments are preferentially quarantined rather than falsely matured;
- HYBRID or EXPECTED-RELEASE avoids the high-noise / high-value failure mode of VALUE-FIRST;
- BOUNDARY-FIRST materially improves residual-wrong-assignment discovery;
- REPRESENTATIVE-CANARY reduces evidence but does not silently mature unsupported members;
- directed maturation shuts down after consolidation;
- PERMANENT-PLASTIC spends materially more structural compute without commensurate action benefit;
- consolidation remains possible at the primary 0.5N evidence budget.

FAILURE CONDITIONS

Treat H145 as mixed/negative if:

- directed routing only improves speed by falsely maturing wrong members;
- mature-member precision falls below 99% primary;
- UNIFORM is as efficient as directed policies;
- policies repeatedly oscillate mature/quarantined status;
- 0.5N evidence is insufficient for useful maturation;
- high-value members monopolize evidence and hide boundary errors;
- representative canaries cause unsupported extrapolation;
- consolidation requires continued scratch reconstruction;
- post-blastema evidence cost approaches full-family repeated audit.

PRIMARY CONFIRMATION SIZE

Primary:

2,000 worlds per routing policy.

8 policies.

16,000 policy-worlds.

Common-world discipline:

policies within a world receive:
- identical provisional topology;
- identical active schedule;
- identical member values;
- identical potential sensor outcomes for identical queried pairs.

ROBUSTNESS

Sensor error:
1%, 5%, 10%, 20%.

Residual topology error:
0%, 2%, 5%, 10%.

Evidence budget:
0.25N, 0.5N, 1N, 2N.

Value concentration:
low,
primary,
high.

Residual errors:
uniform;
boundary-concentrated;
high-value concentrated;
single-region concentrated.

Activity:
uniform;
bursting;
one-region-dominant.

MATURATION-WINDOW ROBUSTNESS

Compare:

10 episodes,
20 episodes,
40 episodes.

Question:

is there a useful:
CRITICAL PLASTICITY WINDOW

after which:
continued specialized maturation
has sharply diminishing returns?

OUT-OF-BOX EXTENSION

If H145 succeeds,
the organism gains a developmental lifecycle:

RE-DEVELOP
->
MATURATION
->
CONSOLIDATION
->
HIBERNATION.

That creates:
temporary high plasticity

without:
permanent global plasticity.

A later experiment should test the separate prospective hypothesis already recorded in H144:

BOUNDED INCREMENTAL PATCHING
INSIDE
A STRUCTURAL TRUST REGION

with:
cumulative repair debt
and:
damage spatial distribution

as the handoff signal to:
blastema redevelopment.

H145 does not test that trust-region hypothesis.

FROZEN BEFORE EXECUTION

Ecology,
post-blastema topology quality,
maturity contracts,
routing policies,
negative comparator,
metrics,
acceptance shape,
failure conditions,
confirmation size,
and robustness dimensions above

are fixed before synthetic execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = SYNTHETIC_MEASURED_SANDBOX_POST_REDEVELOPMENT
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = 97b71ab018682cf02dfe2be7370d0451dd191c93
