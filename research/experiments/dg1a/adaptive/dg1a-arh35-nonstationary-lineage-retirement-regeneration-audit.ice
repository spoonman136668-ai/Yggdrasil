TITLE: DG-1A-AR-H35 — Nonstationary Dormant-Lineage Value / Reversible Retirement Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE GENERATIVE-RETIREMENT RESULT + NICHE-SHIFT FIT REQUIREMENT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh34-dormant-lineage-retirement-value-audit.ice

PURPOSE
H34 established that dormant-lineage retirement should depend on expected future functional value,
not age or reuse frequency alone.

H35 asks the next lifecycle question:

WHEN A DORMANT LINEAGE IS PRUNED,
MUST THE ORGANISM LOSE THE ABILITY TO REGENERATE THAT FUNCTION?

A compact developmental system should distinguish:

DELETE THE CURRENT DORMANT INSTANCE

from

ERASE THE GENERATIVE POSSIBILITY FOREVER.

QUESTION
Can a tiny retained generative template or compressed lineage tombstone preserve future regenerative capability at much lower cost than full dormant state?

And:

what happens when the old niche returns in a changed form?

BOUNDARY
This is synthetic.

It does not:
- freeze template/tombstone sizes;
- prove real Yggdrasil can reconstruct a lineage from the tested state;
- establish final genome architecture;
- freeze recurrence costs;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

RETIREMENT POPULATION
100 dormant lineage instances.

All are pruned from active use for:

2000 synthetic steps.

At the end of the dormant interval,
each lineage returns with probability:

0.25.

Of returning lineages:

65%
return to approximately the same niche.

35%
return under a shifted local niche.

20%
of recurrence events are:
high urgency.

500 matched retirement populations for the primary comparison.

POLICIES

FULL DORMANT INSTANCE
Retain the full dormant state.

Per-lineage storage cost:
0.020 per step.

Same-niche wake latency proxy:
1.

Shifted-niche latency:
20
because the fully retained instance is stale and must be corrected.

HARD DELETE
Retain no lineage-specific information.

Storage:
0.

Any recurrence requires full rediscovery.

Wake/reacquisition latency:
25
for both same and shifted niches.

GENOME-LEVEL GENERATIVE TEMPLATE
Retain only a tiny generic reconstruction template.

Storage:
0.0015 per lineage-step.

Wake latency:
8
for both niche conditions.

The template is intentionally slower than a niche-specific tombstone
but less vulnerable to niche shift.

COMPRESSED TOMBSTONE
Retain a small lineage-specific reconstruction sketch.

Storage:
0.0020.

Same-niche latency:
3.

Shifted-niche latency:
15
because stale niche detail can mislead reconstruction.

FIT-GATED TOMBSTONE
Retain:
- compressed lineage sketch;
- minimal context/fit metadata.

Storage:
0.0022.

Same-niche latency:
4.

Shifted-niche latency:
8
because stale niche-specific information can be suppressed
and reconstruction falls back toward the generic/current context path.

TOTAL COST
Synthetic total cost combines:

persistent storage cost

+

urgency-weighted recurrence/reacquisition latency.

This is an abstract systems comparison,
not a biological unit.

PRIMARY RESULT
500 matched populations.

FULL DORMANT

mean total cost:
4341.59.

mean recurrence cost:
341.59.

mean recurrence latency:
7.68.

HARD DELETE

total:
1114.65.

recurrence cost:
1114.65.

mean latency:
25.

GENERIC TEMPLATE

total:
656.69.

recurrence cost:
356.69.

mean latency:
8.

COMPRESSED TOMBSTONE

total:
721.34.

recurrence cost:
321.34.

mean latency:
7.22.

FIT-GATED TOMBSTONE

total:
680.87.

recurrence cost:
240.87.

mean latency:
5.41.

PRIMARY POSITIVE
Full dormant retention is far too expensive under the tested long inactive period.

Hard deletion removes storage cost,
but recurrence is very expensive.

A tiny generative template or fit-gated tombstone preserves most of the regenerative capability at a small fraction of the storage cost.

Thus:

PRUNE CURRENT INSTANCE
DOES NOT HAVE TO MEAN
LOSE GENERATIVE CAPABILITY.

GENERIC TEMPLATE RESULT
The generic template has the lowest mean total cost in the primary moderate-urgency mixture:

656.69.

Reason:

it pays the lowest long-term storage cost
and
never carries strongly stale niche-specific state.

FIT-GATED TOMBSTONE RESULT
The fit-gated tombstone has slightly higher total cost:

680.87,

but much lower recurrence cost:

240.87

and lower mean wake latency:

5.41
vs
8.0.

Thus it is preferable when recurrence speed is more valuable.

URGENCY SWEEP
200 matched populations per condition.

NO URGENT RECURRENCE

hard delete:
619.6.

template:
498.3.

tombstone:
582.8.

fit-gated:
575.3.

10% urgent

template:
574.4.

fit-gated:
627.3.

20% urgent

template:
651.2.

fit-gated:
678.7.

40% urgent

template:
808.7.

fit-gated:
786.1.

70% urgent

template:
1054.1.

fit-gated:
951.9.

PRIMARY URGENCY CROSSOVER
As recurrence urgency rises,
the value of faster lineage reconstruction outweighs the extra retained-state cost.

Around the stronger urgency mixtures,
fit-gated tombstones become preferable to the generic template.

Therefore:

RETIREMENT DEPTH
SHOULD DEPEND ON
EXPECTED RECONSTRUCTION URGENCY / COST.

NICHE-SHIFT SWEEP
Primary urgency:
20%.

SHIFTED RECURRENCE FRACTION = 0

template:
651.2.

ungated tombstone:
531.7.

fit-gated tombstone:
615.6.

When the old niche returns unchanged,
specific tombstone memory is highly useful.

SHIFT = 0.10

template:
651.2.

tombstone:
579.2.

fit-gated:
631.5.

SHIFT = 0.35

template:
651.2.

tombstone:
721.0.

fit-gated:
678.7.

SHIFT = 0.60

template:
651.2.

tombstone:
848.0.

fit-gated:
721.0.

SHIFT = 0.90

template:
651.2.

tombstone:
1005.2.

fit-gated:
773.4.

PRIMARY STALE-TOMBSTONE NEGATIVE
A niche-specific tombstone becomes actively harmful when recurrence occurs in a sufficiently changed context.

This is the same stale-prior problem seen in:
H6
H7
H32.

Specific historical memory is valuable only when:
the current niche still fits it.

FIT-GATING POSITIVE
Fit gating substantially reduces the shifted-niche penalty.

It does not fully beat the generic template in extreme shift,
because even the retained niche-specific sketch has cost.

Thus there is a real hierarchy:

FULL DORMANT INSTANCE

highest retention cost
fastest identical-context wake
highest stale-state risk.

FIT-GATED TOMBSTONE

medium-low storage
fast recurrence
bounded stale-state risk.

GENERIC TEMPLATE

lowest specialized storage
slower recurrence
best robustness to large niche shift.

HARD DELETE

lowest storage
highest reconstruction cost.

CURRENT RETIREMENT DEPTH
The organism should not make retirement binary.

A lineage can descend through levels:

ACTIVE

->
DORMANT FULL / COMPACT INSTANCE

->
COMPRESSED TOMBSTONE

->
GENERIC GENERATIVE TEMPLATE ONLY

->
NO LINEAGE-SPECIFIC INSTANCE.

Each step reduces:
memory cost

while increasing:
reconstruction latency
or
loss of local specialization.

This is a developmental memory hierarchy.

RELATION TO H34
H34 decides:

IS THIS DORMANT INSTANCE STILL WORTH FULL RETENTION?

H35 decides:

IF NOT,
HOW MUCH GENERATIVE INFORMATION SHOULD SURVIVE?

These are separate decisions.

RELATION TO H32
H32 showed:
fast phenotype should usually be discarded before slow reusable information.

H35 extends that principle over much longer retirement:

niche-specific lineage information can be compressed further,
while a generic developmental template preserves regeneration ability.

RELATION TO NORTH STAR
This is directly aligned with:

CAPABILITY GROWS

while

PERMANENTLY ACTIVE / FULL-STATE STRUCTURE
grows much more slowly.

Capability can persist in:
compressed generative form

instead of:
fully instantiated active or dormant tissue.

GENERAL PRINCIPLE
Yggdrasil should distinguish:

INSTANCE MEMORY

from

GENERATIVE MEMORY.

An instance can be deleted
while the compact developmental engine retains:
the ability to regrow a function.

DECISION
AR-H35 is POSITIVE WITH A NICHE-FIT REQUIREMENT.

Supported synthetically:

- full dormant-instance retention can be much more expensive than regenerative compressed memory;
- hard deletion creates large recurrence cost;
- tiny generative templates preserve broad regenerative capability cheaply;
- niche-specific tombstones accelerate same-context recurrence;
- stale tombstones become harmful under niche shift;
- fit gating reduces stale-recurrence failure;
- retirement depth should depend on expected future value and reconstruction urgency.

Not demonstrated:

- real Yggdrasil lineage regeneration from compressed templates;
- optimal tombstone representation;
- shared templates across many lineages;
- mutation of templates over generations;
- interaction between genome compression and structural memory rank;
- security against corrupt generative templates.

CLEAN SCIENTIFIC PAUSE
H27-H35 now form a coherent decentralized lifecycle architecture:

H27:
local resource pricing moves scarce evidence without a central scheduler.

H28:
async transfer requires idempotent ownership and stale-price expiry.

H29:
resource persistence must survive cell death separately from cell identity.

H30:
division conserves scarce resource while copied inherited information retains common provenance.

H31:
growth should price future maintenance and support dormancy.

H32:
dormancy retains compact slow prior + fit confidence rather than frozen fast phenotype.

H33:
wake should be local/value-gated rather than broadcast.

H34:
dormant instances should be retired by expected future value,
not age/frequency alone.

H35:
retirement can preserve generative capability through templates/tombstones.

NEXT HIGH-VALUE MOVE
AR-H36 — SHARED GENERATIVE TEMPLATE / LINEAGE-COMPRESSION SCALING

Question:

Can many related retired lineages share:
one compact generative basis

plus

small lineage-specific residual/tombstone state?

Compare:

A.
one full template per lineage;

B.
one family template + residuals;

C.
low-rank generative basis across lineages;

D.
over-compression causing distinct regenerative functions to collide;

E.
novel lineage outside the shared template manifold.

Desired:

retired capability count may grow

while

per-lineage permanent memory grows sublinearly.

This is the lineage-memory analogue of H7's shared low-rank inherited manifold.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_lineages = 100
dormant_interval = 2000
primary_populations = 500
return_probability = 0.25
primary_niche_shift_fraction = 0.35
primary_urgent_fraction = 0.20
