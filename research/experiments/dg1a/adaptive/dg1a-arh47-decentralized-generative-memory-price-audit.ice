TITLE: DG-1A-AR-H47 — Decentralized Generative-Memory Price Formation Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE LOCAL-PRICE-DIFFUSION RESULT + OVERDIFFUSION/GLOBAL-SCALAR NEGATIVES
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh46-endogenous-generative-memory-price-audit.ice

PURPOSE
H46 showed that generative-family branch price should depend on:
- current slow-memory occupancy;
- resource/runway pressure;
- release through retirement.

But H46 still used a global occupancy ratio.

H47 removes that hidden centralization.

QUESTION
Can a spatial developmental organism approximate useful structural-memory price using only:
- local occupancy;
- local reserve stress;
- bounded nearest-neighbor price diffusion;

without:
- a global capacity count;
- central allocator;
- organism-wide scalar price?

BOUNDARY
This is synthetic.

It does not:
- freeze a production diffusion rule;
- freeze four communication rounds;
- establish a literal spatial grid requirement;
- prove real hardware memory pressure is locally fungible;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SPATIAL ORGANISM
16 x 16 local memory regions.

Cells:
256.

A smooth crowded memory hotspot is embedded in a mostly sparse organism.

Local occupancy includes:
small independent measurement variation.

Hotspot resource/runway pressure is also elevated.

REFERENCE REGIONAL PRICE
A diagnostic centralized oracle computes:
local resource-sharing scarcity

using a three-round nearest-neighbor smoothed occupancy field.

Reference price:

0.45
+
3.0 * regional_occupancy^3
+
1.1 * local_pressure.

This oracle is used only for scoring.

Operational policies do not receive it.

CANDIDATE FAMILY-BRANCH VALUES
Every location receives an independent synthetic candidate structural value.

Correct decision:

ACCEPT
if candidate value exceeds the regional reference price.

PRIMARY CONFIRMATION
300 matched spatial seeds.

COMPARATOR A — ONE GLOBAL PRICE
Compute one organism-wide mean occupancy/pressure price
and apply it everywhere.

Decision accuracy vs regional oracle:
88.16%.

mean decision regret:
0.03392.

mean absolute price error:
0.22605.

HOTSPOT admission:

global scalar:
76.93%.

regional oracle:
31.77%.

SPARSE-REGION admission:

global:
76.71%.

oracle:
84.73%.

PRIMARY GLOBAL-SCALAR NEGATIVE
One organism-wide memory price is wrong in both directions simultaneously.

It:

UNDERPRICES
the crowded/high-pressure hotspot

while

OVERPRICING
sparse regions with available structural capacity.

Thus:

ONE GLOBAL MEMORY PRICE
CAN CREATE
LOCAL STRUCTURAL MONOPOLY
AND
REMOTE STRUCTURAL FREEZE
AT THE SAME TIME.

COMPARATOR B — PURELY LOCAL PRICE
Use only the cell's own noisy occupancy measurement.

Decision accuracy:
93.73%.

regret:
0.00962.

price MAE:
0.14483.

Hotspot admission:
27.05%.

Sparse:
82.35%.

This already improves strongly over a global scalar,
but local measurement noise and lack of nearby scarcity context remain visible.

NEIGHBOR PRICE / OCCUPANCY DIFFUSION
Each region exchanges only with:
nearest neighbors.

No global aggregation.

ONE ROUND

accuracy:
97.38%.

regret:
0.001660.

price MAE:
0.06009.

TWO ROUNDS

accuracy:
98.23%.

regret:
0.000713.

price MAE:
0.03836.

FOUR ROUNDS

accuracy:
98.72%.

regret:
0.000392.

price MAE:
0.02799.

hotspot admission:
33.64%.

oracle:
31.77%.

sparse admission:
84.56%.

oracle:
84.73%.

PRIMARY DECENTRALIZED POSITIVE
A small bounded neighborhood price field recovers almost all of the useful regional scarcity signal
without any cell observing organism-wide occupancy.

This is the desired architectural direction.

OVERDIFFUSION STRESS
SIX ROUNDS

accuracy:
98.57%.

regret:
0.000790.

price MAE:
0.03432.

hotspot admission:
36.85%.

The result begins to worsen.

Reason:

scarcity information is spreading farther than the region in which memory/resource competition is actually coupled.

PRIMARY OVERDIFFUSION NEGATIVE
More price propagation is not automatically better.

If the resource is locally constrained,
an overly smooth price field begins recreating:

GLOBAL PRICE CONTAMINATION.

Thus price communication needs a:
BOUNDED ECONOMIC HORIZON.

RESOURCE-RELEASE / RETIREMENT STRESS
A crowded hotspot undergoes a local H34/H35-style retirement event.

Local memory occupancy is sharply released.

The reference regional price is recomputed from the new resource state.

300 matched seeds.

NO NEIGHBOR PROPAGATION

overall price MAE:
0.08743.

former-hotspot mean estimated price:
0.6455.

true regional:
0.6692.

adjacent ring estimated:
0.8083.

true:
0.7110.

Interpretation:
the released cells see their own new affordability immediately,
but neighbors retain an overly expensive local view.

ONE ROUND

MAE:
0.03440.

adjacent ring:
0.7401.

TWO ROUNDS

MAE:
0.02221.

ring:
0.7218.

THREE ROUNDS

MAE:
0.01728.

former hotspot:
0.6697
vs true:
0.6692.

adjacent ring:
0.7118
vs true:
0.7110.

PRIMARY RELEASE POSITIVE
When old structural memory is retired,
lower structural price propagates locally through the same bounded neighborhood mechanism.

New structural affordability can therefore reopen around the released resource
without broadcasting:

GLOBAL MEMORY IS NOW CHEAP.

FOUR / SIX ROUND RESULT
Additional diffusion continues to reduce broad noise slightly at first,
then increasingly undershoots the adjacent-ring scarcity boundary.

At six rounds:

former-hotspot price:
0.6790.

ring:
0.6964
vs regional reference:
0.7110.

This confirms the locality tradeoff.

RELATION TO H27
H27 showed:
scarce evidence/resource tokens can move along local demand/price gradients without central scheduling.

H47 shows:
slow generative-memory opportunity cost can also be represented by a local price field.

These may share:
the same generic local economic machinery.

They need not share:
the same timescale
or
the same fungibility assumptions.

RELATION TO H46
H46's global price is best interpreted as:
a conceptual resource-economy reference.

H47 replaces it operationally with:

LOCAL SCARCITY
+
BOUNDED NEIGHBOR INFORMATION.

A global count is not required.

CURRENT DECENTRALIZED STRUCTURAL ECONOMY
LOCAL SLOW-MEMORY OCCUPANCY

+

LOCAL MAINTENANCE / RUNWAY PRESSURE

+

BOUNDED NEIGHBOR PRICE INFORMATION

->

LOCAL GENERATIVE-MEMORY PRICE.

Then:

candidate future value

vs

local structural price

->

lease locally
or
write/retain/merge/split generative structure.

GENERAL PRINCIPLE
RESOURCE PRICE SHOULD PROPAGATE
ONLY AS FAR AS
THE RESOURCE COMPETITION IT REPRESENTS.

Too little propagation:
misses neighborhood scarcity.

Too much:
turns local scarcity into organism-wide inhibition.

DECISION
AR-H47 is POSITIVE.

Supported synthetically:

- purely local structural pricing outperforms one global scalar in spatially heterogeneous memory conditions;
- bounded nearest-neighbor diffusion substantially improves local price accuracy;
- four-round diffusion reaches ~98.7% decision agreement with the regional oracle in the tested grid;
- global price simultaneously over-admits crowded regions and suppresses sparse ones;
- local retirement lowers structural price and that affordability propagates to nearby tissue;
- excessive diffusion begins washing out local scarcity boundaries.

Not demonstrated:

- real Yggdrasil memory-locality geometry;
- learned price-propagation radius;
- asynchronous price gossip;
- topological cell birth/death during price formation;
- price manipulation by misreporting cells;
- coupling of memory price with evidence-token price.

NEXT CLEAN QUESTION
AR-H48 — ASYNCHRONOUS / ADVERSARIAL LOCAL PRICE GOSSIP

H47 assumes clean synchronous neighbor price propagation.

Question:

What happens when local structural-price messages are:
- delayed;
- duplicated;
- stale;
- selectively inflated;
- or sent by a temporarily faulty neighborhood?

Compare:

A.
raw latest-price gossip;

B.
TTL/freshness-gated prices;

C.
provenance-aware family/source weighting;

D.
local functional occupancy cross-check;

E.
persistent real scarcity shift.

Desired:

stale or isolated inflated price
->
bounded local inhibition.

real persistent neighborhood scarcity
->
price rise propagates.

resource release
->
old high prices expire rather than suppressing growth indefinitely.

This should reuse:
H28 asynchronous transfer integrity
and
S9 reversible trust.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
grid = 16x16
primary_spatial_seeds = 300
primary_neighbor_rounds = 4
release_stress_seeds = 300
