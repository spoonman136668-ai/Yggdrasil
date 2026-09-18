TITLE: DG-1A-AR-U1 — Multi-Role Local Utility Market Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX MIXED-POSITIVE PRECURSOR
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-ar05-utility-driven-relay-role-market-poc.ice

PURPOSE
Extend the successful single-role relay utility market to simultaneous local functional demands without prescribing any global role histogram.

Question:
Can several soft functions coexist, specialize spatially, and recover after selective role-state erasure using only local demand, local cost, and a shared bounded update rule?

BOUNDARY
This is NOT Yggdrasil functional regeneration.

This audit:
- does not train Yggdrasil;
- does not alter or execute STAB-18-R1;
- uses hand-designed synthetic local utility functions;
- does not claim these roles exist in real Yggdrasil latent state;
- does not use a global target role ratio.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BODY
2D four-neighbor disk graph
radius = 7
live nodes = 149

PERSISTENT LOCAL DEMANDS
Several demands coexist spatially.

COMMUNICATION
Six fixed source-destination message demands.

DAMAGE
A compact local integrity-deficit zone.

GROWTH
A separate compact local capacity-deficit zone.

INSTABILITY
A separate local stress-injection zone.

QUIET REGIONS
Regions with little direct functional demand.

SOFT FUNCTIONS
Four independently expressed active gates:

relay
repair
inhibitor
growth

Dormancy is the low-active-load complement:

dormant =
1 - max(active_role_gates)

clipped to [0,1].

This factorized representation permits mixed function.
Roles are not constrained to sum to one.

FUNCTIONAL EFFECTS

RELAY
Higher local relay gate lowers communication edge cost.

REPAIR
Higher local repair gate restores local integrity.

INHIBITOR
Higher local inhibitor gate damps local stress.

GROWTH
Higher local growth gate restores local structural capacity.

DORMANCY
Low active-role load reduces synthetic energy expenditure.

LOCAL UTILITY INPUTS
Cells receive only local quantities:

relay:
message traffic traversing the cell

repair:
own + one-hop integrity deficit

inhibitor:
own + one-hop stress

growth:
own + one-hop capacity deficit

No cell receives:
- global role counts;
- target role coordinates;
- global route cost;
- global task score;
- a desired role histogram.

EARLY NEGATIVE — SIMPLEX / SATURATING ROLE STATE
The first multi-role formulation used normalized role probabilities.

It produced useful repair/growth adaptation but:
- relay recovery remained incomplete;
- inhibitor recovery was slow;
- saturated role state showed strong canalization;
- moving demand could add new specialization without retiring old specialization.

Do not discard this negative.

The failure suggested:
ROLE EXPRESSION SHOULD NOT BE A HARD ZERO-SUM SIMPLEX
and
SATURATED ROLE STATE NEEDS A DIRECT RETIREMENT PATH.

BOUNDED KINETIC ROLE RULE
A factorized role gate a_i in [0,1] is updated from normalized local utility q_i.

For each updating cell:

da_i =
q_i * (1 - a_i)
-
0.10 * (1 - q_i) * a_i
-
0.12 * max(sum_j(a_j) - 1.25, 0) * a_i

Then:

a_i <- clip(
    a_i + 0.16 * da_i,
    0,
    1
)

Stochastic cell update probability:
0.5

Interpretation:

q_i * (1-a_i):
local functional demand recruits the role.

0.10 * (1-q_i) * a_i:
unused specialization retires.

resource term:
discourages unconstrained accumulation of simultaneous active functions.

No target population fraction appears.

FRESH BASELINE
Fresh seeds:
10..17
n = 8

Development:
220 steps

Mean last-20-step metrics:

communication route cost:
23.6665

damage deficit:
0.10412

growth/capacity deficit:
0.09000

stress:
0.11170

Spatial specialization:

global relay gate:
0.46687

repair gate inside damage zone:
0.45082

inhibitor gate inside stress zone:
0.50716

growth gate inside growth-demand zone:
0.44733

derived dormancy in quiet region:
0.40148

The roles coexist without a global quota.

SELECTIVE ROLE-STATE ERASURE
For each active function separately:

1. rank cells by that function's gate;
2. erase enough highest-function gate values to remove approximately 80% of total role mass;
3. keep all cells and morphology present;
4. for repair/growth/inhibitor, apply a standardized matching challenge;
5. allow the same local utility rule to adapt;
6. compare against a frozen-role control.

Recovery criterion:
functional metric returns to within 10% of the seed's pre-ablation value and remains there for 10 consecutive steps.

RELAY
Pre:
23.6665 route cost

Immediate after role-state erasure:
69.3656

Adaptive final at 160 steps:
25.2403

Frozen final:
70.5354

Recovery:
7/8 seeds by 160 steps

Median successful recovery latency:
78 steps

Extended to 240 steps:
still 7/8 under the unchanged 10% criterion.

The remaining seed ended about 12.3% above its own pre-ablation route cost.

Therefore relay recovery is strong but not complete under this criterion.

REPAIR
Pre damage deficit:
0.10412

Immediate:
0.68645

Adaptive final:
0.10011

Frozen final:
1.00000

Recovery:
8/8

Median latency:
44 steps

GROWTH
Pre capacity deficit:
0.09000

Immediate:
0.68155

Adaptive final:
0.08698

Frozen final:
1.00000

Recovery:
8/8

Median latency:
50 steps

INHIBITOR
Pre stress:
0.11170

Immediate:
0.76167

Adaptive final:
0.10999

Frozen final:
0.48437

Recovery:
8/8

Median latency:
37.5 steps

PRIMARY POSITIVE
A single local bounded utility rule can maintain several simultaneous soft functions and restore four distinct functional metrics after severe role-state erasure.

No global role histogram is required.

IMPORTANT DISTINCTION
ROLE-STATE ERASURE is not the same as permanently removing the cells that previously carried the function.

The erased cells remain able to express the role again.

STRICT SPECIALIST-UNAVAILABILITY TEST
A stricter relay diagnostic permanently forbade the cells carrying 70% of pre-ablation relay mass from ever expressing relay again.

Mean permanently unavailable nodes:
52.625 of 149

Pre route cost:
23.6665

Adaptive final after 300 steps:
approximately 40.68

No seed recovered to the original 10% criterion.

This is a NEGATIVE.

ORACLE STRUCTURAL BOUND
However, the fixed graph itself imposes a large irreducible cost.

For the same permanently disabled relay cells:
set EVERY surviving eligible node's relay gate to 1.

This is an impossible-for-the-local-rule oracle upper bound.

Mean oracle route cost:
31.1870

Oracle / pre-ablation ratio:
1.3180

Therefore:
the original <=10% recovery target is physically impossible after this lesion on the fixed graph.

Even an omniscient assignment of maximal relay function to every remaining eligible node cannot recover the original path geometry.

At 30%, 50%, and 70% permanently unavailable relay mass,
the adaptive final route cost remained approximately 29-32% above the corresponding oracle optimum after 240 steps.

Thus TWO effects coexist:

1. STRUCTURAL LIMIT
important relay positions are physically unavailable.

2. ADAPTATION GAP
the local utility rule does not fully exploit the best remaining configuration.

This distinction must be preserved in future functional-regeneration experiments.

SCIENTIFIC CONSEQUENCE
A functional lesion should not be judged only against the pre-lesion optimum.

For sufficiently severe lesions:
PRE-LESION PERFORMANCE MAY BE UNREACHABLE.

Future evaluation needs both:

PRE-LESION BASELINE

and

POST-LESION FEASIBLE ORACLE / CAPACITY BOUND

where such a bound can be estimated without leaking it to cells.

Define normalized attainable recovery:

AttainableRecovery =
(DamagedMetric - AdaptiveMetric)
/
(DamagedMetric - OracleMetric)

for lower-is-better metrics.

Do not use this definition retroactively as a pass gate for existing work.
It is a future measurement recommendation.

LITERATURE ALIGNMENT
Béna and Goodman,
Dynamics of specialization in neural modules under resource constraints,
Nature Communications 16, 187 (2025),
DOI: 10.1038/s41467-024-55188-9

Relevant findings:
- structural modularity does not by itself guarantee functional specialization;
- specialization is promoted by meaningfully separable environmental features;
- stronger resource constraints can promote specialization;
- specialization changes dynamically over time with information flow.

This is consistent with the current utility-market direction:
functional demand and cost should shape specialization rather than a hand-imposed structural role map.

INTERPRETATION
The strongest current synthetic mechanism is:

local demand
+
bounded local cost
+
role recruitment
+
explicit role retirement
->
dynamic soft specialization.

The crucial negative is:

functional regeneration can be limited by the surviving substrate geometry,
not only by the intelligence of the adaptation rule.

NEXT
AR-U2:
move the functional demand after specialization.

Test whether roles truly relocate,
whether obsolete specialization retires,
and whether repeated demand switching causes accumulation/canalization.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
fresh_baseline_seeds = 8
role_erasure_fraction = 0.80
strict_relay_unavailability_fraction = 0.70
