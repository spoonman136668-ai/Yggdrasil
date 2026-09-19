TITLE: DG-1A-AR-H34 — Dormant-Lineage Retirement / Pruning-Value Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE EXPECTED-FUTURE-VALUE RETIREMENT RESULT + RARE-CRITICAL AGE-PRUNING NEGATIVE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh33-wake-storm-dormant-population-coordination-audit.ice

PURPOSE
H31-H33 established that dormancy can:
- reduce permanently active structure;
- preserve compact lineage memory;
- provide rapid local regenerative reserve.

But dormant state still has cost:

memory
+
lineage bookkeeping
+
future wake-search burden.

H34 asks:

HOW LONG SHOULD UNUSED DORMANT STRUCTURE BE RETAINED?

QUESTION
Can dormant-lineage retirement use:

EXPECTED FUTURE FUNCTIONAL VALUE

rather than:

AGE ALONE
or
REUSE FREQUENCY ALONE?

The critical failure case is:

RARE
BUT
HIGH-VALUE
regenerative lineage.

BOUNDARY
This is synthetic.

It does not:
- freeze a production pruning score;
- define final dormant-memory bytes;
- prove real lineage reuse follows Poisson/Bernoulli statistics;
- authorize semantic lineage classes;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

LINEAGE POPULATION
100 dormant lineages.

Synthetic latent classes are used only for evaluation.

The policies do NOT receive class labels.

COMMON LOW-BENEFIT

60 lineages.

reuse probability per step:
0.020.

functional reacquisition penalty if pruned:
1.

MEDIUM

25 lineages.

reuse probability:
0.005.

reacquisition penalty:
5.

RARE CRITICAL

10 lineages.

reuse probability:
0.001.

reacquisition penalty:
30.

DEAD / NEVER REUSED

5 lineages.

reuse:
0.

benefit:
0.

The rare-critical class therefore has:

low frequency

but

high expected functional value.

SIMULATION
5,000 time steps.

Primary memory cost per retained dormant lineage:

0.03 synthetic loss units per step.

100 matched seeds for the main policy comparison.

A reuse event for a pruned lineage incurs:
the lineage-specific reacquisition / missed-function cost.

After reacquisition,
the lineage becomes available again subject to the current retirement policy.

COMPARATORS

NEVER PRUNE
Keep all 100 dormant lineages.

AGE-ONLY
Prune any lineage unused for:

200 steps.

No functional-value term.

FREQUENCY-ONLY
Under a hard memory cap:
50 lineages.

Retain the lineages with highest estimated reuse rate.

VALUE-AWARE
Same 50-lineage memory cap.

Estimate reuse rate from history with a small shrinkage prior.

Rank by:

estimated reuse rate
*
last-known functional benefit.

The last-known benefit is assumed to come from the lineage's previous active/use phase.

No future event is known.

NEVER-PRUNE RESULT

mean retained:
100.

memory cost:
15,000.

miss cost:
0.

total:
15,000.

This is the upper-memory / zero-forgetting comparator.

AGE-ONLY RESULT

mean retained:
approximately 75.9.

mean total cost:
approximately 14,016.

Rare-critical reuse events:
approximately 50.7 per run.

Rare-critical misses:
approximately 41.7.

Rare-critical retained-at-reuse fraction:
17.8%.

PRIMARY AGE NEGATIVE
Age is a poor proxy for future value.

Rare-critical lineages are quiet long enough to exceed the fixed inactivity threshold,
so they are deleted even though one future reuse is extremely valuable.

Thus:

LONG INACTIVITY
DOES NOT IMPLY
LOW EXPECTED FUNCTIONAL VALUE.

FREQUENCY-ONLY RESULT
Hard cap:
50.

mean retained:
50.

mean total cost:
approximately 13,202.

Rare-critical misses:
approximately 50.7.

Rare-critical retained-at-reuse fraction:
approximately 0%.

PRIMARY FREQUENCY NEGATIVE
A pure reuse-frequency ranking is even worse for the rare-critical class.

The lineages are deliberately too infrequent to compete with common low-value memory on frequency alone.

Thus:

FREQUENT
DOES NOT IMPLY
VALUABLE.

VALUE-AWARE RESULT
Hard cap:
50.

mean retained:
50.

mean total cost:
approximately 12,093.

memory cost:
7,500.

miss / reacquisition cost:
approximately 4,593.

Rare-critical misses:
approximately 0.98.

Rare-critical retained-at-reuse fraction:
approximately 98.1%.

Medium misses:
approximately 85.8.

Common misses:
approximately 4,134.

PRIMARY POSITIVE
Expected-future-value ranking protects almost all rare critical dormant memory
while still deleting large amounts of low-value memory.

The policy intentionally accepts many missed common low-cost reuses
in order to preserve scarce memory capacity for:

lower-frequency
but
higher-consequence

lineages.

This is the dormant-memory form of:
VALUE OF INFORMATION.

MEMORY-PRESSURE SWEEP
50 matched seeds per cap.

VALUE-AWARE policy.

CAP = 30

mean total cost:
11,205.6.

rare-critical misses:
1.64.

CAP = 40

total:
11,621.8.

rare misses:
1.12.

CAP = 50

12,093.1.

rare:
0.98.

CAP = 60

12,569.2.

rare:
0.70.

CAP = 70

13,048.8.

rare:
0.54.

PRIMARY MEMORY-PRESSURE RESULT
Under the tested memory price,
aggressive pruning can lower total synthetic loss
because persistent dormant-state cost is high.

Crucially,
value-aware ranking keeps rare-critical memory even at:
30 / 100 retained lineages.

This is the desired pressure response:

MEMORY SCARCITY
SHOULD REMOVE
LOW EXPECTED VALUE STATE

before:

RARE HIGH-CONSEQUENCE CAPABILITY.

Do not freeze:
cap 30
or
memory cost 0.03.

AGE
vs
VALUE
A dormant lineage needs at least conceptual equivalents of:

LAST USE TIME

+

REUSE HISTORY

+

LAST KNOWN FUNCTIONAL VALUE

+

CURRENT MEMORY PRICE

+

REACQUISITION COST / LATENCY.

Age remains useful,
but only as one component.

It should not be a deletion authority by itself.

REUSE VALUE
The relevant quantity is closer to:

EXPECTED FUTURE REUSE PROBABILITY

*
FUNCTIONAL CONSEQUENCE OF LOSING THE LINEAGE

minus

DORMANT STORAGE COST.

This is the same economic pattern already established for:

evidence collection;

context validation;

structural growth.

DORMANT RETIREMENT IS ANOTHER RESOURCE-ALLOCATION PROBLEM.

IMPORTANT MATURATION LIMIT
A newly created lineage may not yet have a reliable estimate of:
reuse rate
or
future functional value.

Therefore:
immediate aggressive pruning after one quiet period is unsafe.

A production design likely needs:
- uncertainty in the value estimate;
- conservative minimum retention / grace period;
- possibly lineage-family priors.

H34 does not freeze those mechanisms.

RELATION TO H31
H31:
dormancy is useful because active maintenance is expensive.

H34:
dormancy itself must also be priced.

The optimal lifecycle is not:

ACTIVE
or
DORMANT FOREVER.

It is:

ACTIVE

->
DORMANT

->
RETAIN WHILE EXPECTED FUTURE VALUE JUSTIFIES STORAGE

->
PRUNE WHEN IT DOES NOT.

RELATION TO H32
H32 reduced dormant-state size through compact slow memory.

H34 attacks the remaining multiplicative risk:

TOO MANY COMPACT DORMANT LINEAGES.

Even small per-lineage state becomes large if nothing is ever retired.

RELATION TO H21 / H26
H21:
not every uncertainty deserves validation.

H26:
not every high-demand layer deserves resource.

H34:

not every dormant lineage deserves permanent memory.

All three use:

EXPECTED FUNCTIONAL VALUE
PER
SCARCE RESOURCE.

DECISION
AR-H34 is POSITIVE WITH A VALUE-ESTIMATION MATURATION LIMIT.

Supported synthetically:

- never pruning can become more expensive than selective forgetting;
- age-only pruning deletes rare high-value regenerative memory;
- frequency-only pruning strongly favors common low-value reuse;
- value-aware pruning protects rare-critical dormant lineages;
- memory pressure can be increased while retaining high-value rare capability;
- dormant-state retirement should include reacquisition consequence, not only age.

Not demonstrated:

- real Yggdrasil lineage reuse prediction;
- real reacquisition cost;
- optimal memory price;
- value uncertainty / confidence representation;
- lineage-family priors;
- revival of pruned capability from shared genome;
- pruning under nonstationary future value.

NEXT CLEAN QUESTION
AR-H35 — NONSTATIONARY DORMANT-LINEAGE VALUE / REVERSIBLE RETIREMENT

Question:

What happens when:
- a formerly valuable dormant lineage becomes obsolete;
- a formerly unimportant lineage becomes critical after a regime shift?

A permanently deleted lineage cannot update its own value.

Test:

A.
hard deletion;

B.
tiny genome-level template retained after pruning;

C.
compressed tombstone / lineage sketch;

D.
rediscovery cost under later recurrence.

Desired:

pruned lineage should stop paying full dormant-state cost

while

the developmental system retains enough compressed generative information
to reconstruct useful capability if its niche returns.

This would distinguish:

FORGET CURRENT INSTANCE

from

LOSE THE ABILITY TO REGENERATE THAT FUNCTION.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_lineages = 100
primary_steps = 5000
main_policy_seeds = 100
memory_cost_per_lineage_step = 0.03
value_policy_primary_cap = 50
