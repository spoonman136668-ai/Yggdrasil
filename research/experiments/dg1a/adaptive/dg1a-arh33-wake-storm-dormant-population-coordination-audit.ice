TITLE: DG-1A-AR-H33 — Wake-Storm / Dormant-Population Coordination Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE LOCAL-WAKE RESULT + COVERAGE/LATENCY TRADEOFF
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh32-dormancy-memory-wake-reliability-audit.ice

PURPOSE
H31 established that dormancy can reduce permanently active structure and improve damage recovery.

H32 established that dormant cells can retain compact slow state rather than full frozen fast phenotype.

H33 tests the population-level wake failure:

WHAT IF A LARGE DORMANT RESERVE RECEIVES THE SAME WAKE SIGNAL?

A naive broadcast wake can recreate the exact active-resource spike dormancy was meant to avoid.

QUESTION
Can local damage/value signals coordinate wake-up without:
- a global role histogram;
- central wake scheduler;
- waking all dormant tissue;
- exhausting the active resource envelope?

BOUNDARY
This is synthetic.

It does not:
- freeze a wake threshold;
- freeze a neighborhood size;
- prove real Yggdrasil damage signals have this geometry;
- define biological sleep/wake chemistry;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SPATIAL ORGANISM
Grid:

20 x 20
=
400 cells.

Initial permanently active cells:

80.

Initial dormant reserve:

320.

Synthetic active-resource envelope:

180 simultaneously active cells.

Dormant cells consume negligible active capacity in this benchmark.

LOCAL DAMAGE
A smooth local damage field is applied sequentially to three different spatial regions.

Damage centers:

phase 1:
near (5,5).

phase 2:
near (14,14).

phase 3:
near (5,14).

The damage region therefore moves over time.

Each cell sees:
- local damage intensity;
- local active-neighbor count.

No cell receives:
global damaged-cell count
or
global wake target.

LOCAL COVERAGE
For each damaged position,
a 3 x 3 neighborhood has a synthetic target active count:

4.

Damage coverage is the damage-weighted fraction of this local capacity that is active.

PRIMARY CONFIRMATION
100 matched spatial seeds.

160 steps per seed.

POLICIES

BROADCAST WAKE-ALL
Any major damage event wakes every currently dormant cell.

Dormant cells outside the damaged region remain awake until a short inactivity timeout.

LOCAL DEFICIT GATE
A dormant cell wakes when:

local damage
*
local active deficit

exceeds a fixed local threshold.

LOCAL MARGINAL-VALUE GATE
A dormant cell compares:

local damage / active deficit value

against

a local maintenance-price proxy.

Wake only if marginal local value exceeds local price.

STAGGERED LOCAL LEASE
Use local marginal value,
but only a small spatially separated subset of high-bid dormant cells may wake each local round.

A short refractory/inhibitory field prevents immediate neighboring wake cascades.

This is a synthetic local lease,
not a central queue.

BROADCAST RESULT

peak active:
400.

mean active:
183.54.

fraction of steps above the 180-cell envelope:
16.88%.

integrated active-envelope excess:
5940 cell-steps.

mean cumulative wake events:
882.6.

first damage event immediate wakes:
320.

second relocation immediate wakes:
242.6.

third:
320.

peak simultaneously awakened cells outside current damage region:
245.53.

damage coverage:

phase-1 early:
99.88%.

phase-1 steady:
98.80%.

phase-2 early:
99.88%.

phase-2 steady:
98.79%.

phase-3 early:
99.88%.

phase-3 steady:
98.78%.

PRIMARY WAKE-STORM NEGATIVE
Broadcast wake achieves excellent immediate coverage
by activating essentially the entire dormant reserve.

This violates the resource objective.

The organism spends large active capacity on tissue that is not near the damage.

Thus:

FAST REPAIR
DOES NOT JUSTIFY
GLOBAL WAKE.

LOCAL DEFICIT GATE

peak active:
155.84.

mean active:
112.73.

steps above envelope:
0%.

integrated envelope excess:
0.

cumulative wakes:
113.87.

immediate wakes per damage relocation:

approximately:
37
39
38.

peak awakened cells outside current damage region:
41.76.

coverage:

phase 1:
92.74%.

phase 2:
93.12%.

phase 3:
93.00%.

PRIMARY LOCALIZATION POSITIVE
A purely local deficit signal recovers most damage coverage
while waking roughly:

one order of magnitude fewer cells

at each event than broadcast wake.

The active population stays below the tested resource envelope.

LOCAL MARGINAL-VALUE GATE

peak active:
143.07.

mean active:
107.09.

envelope violations:
0.

cumulative wakes:
94.15.

immediate wakes per event:

30.5
32.6
31.1.

peak outside-damage awakened:
35.51.

coverage:

phase 1:
90.40%.

phase 2:
90.88%.

phase 3:
90.60%.

PRIMARY VALUE-GATING RESULT
Adding a local resource/maintenance price further reduces:
- peak active structure;
- wake count;
- irrelevant wake outside the damage region.

The cost is a modest reduction in local damage coverage.

Thus wake control has the same:

FUNCTIONAL VALUE
vs
ACTIVE RESOURCE COST

tradeoff observed in:
H21
and
H26.

STAGGERED LOCAL LEASE
Primary strict staggered configuration.

peak active:
103.70.

mean active:
89.76.

envelope violations:
0.

cumulative wakes:
35.42.

immediate wakes:

approximately:
2.4
2.2
2.6
per damage event.

coverage:

early phase 1:
71.97%.

steady phase 1:
77.61%.

phase 2 steady:
77.09%.

phase 3 steady:
77.34%.

PRIMARY STAGGERING NEGATIVE
Very aggressive local wake staggering prevents any storm,
but it under-recruits regenerative capacity.

The system becomes too conservative.

Therefore:

ANTI-STORM CONTROL
CAN BECOME
REPAIR STARVATION.

LESS-STRICT LOCAL LEASE
A second exploratory configuration allows more local winners.

100 matched seeds.

peak active:
114.81.

mean active:
94.66.

envelope violations:
0.

cumulative wakes:
52.13.

early damage coverage:
approximately 82%.

steady:
approximately 85.3%.

This recovers more function,
but still trails the non-staggered local deficit/marginal policies.

PRIMARY TRADEOFF
Wake coordination needs a tunable continuum:

BROADCAST
->
too much active structure.

EXTREME STAGGERING
->
too little regenerative response.

The desired region lies between:
local marginal value
and
bounded local anti-cascade inhibition.

MOVING-DAMAGE RESULT
Because wake decisions are local,
the active reserve follows the damage region.

The second and third damage regions recruit new nearby dormant cells
without requiring:
global reassignment.

Cells outside the new damage region naturally return toward dormancy after inactivity.

This preserves:
distributed regenerative reserve.

RELATION TO H26
H26 showed:
a persistent noisy adaptive layer can monopolize evidence tokens.

H33 shows the population analogue:

a global wake signal can monopolize active compute.

Both require:

MARGINAL VALUE
+
BOUNDED ANTI-CASCADE CONTROL.

RELATION TO H31
H31 showed:
dormancy reduces stable active structure
and
enables fast repair.

H33 adds:

the dormant reserve must be activated SELECTIVELY.

Dormancy without wake coordination merely postpones a resource spike.

RELATION TO H27
H27 established local resource pricing.

H33 supports using the same local economic motif for wake control:

damage value
+
local active deficit
+
local resource price
+
wake cost

->

current wake authority.

No separate global scheduler is required conceptually.

CURRENT WAKE PIPELINE
DORMANT CELL

+

CURRENT LOCAL DAMAGE

+

LOCAL ACTIVE-COVERAGE DEFICIT

+

WAKE MEMORY / FIT CONFIDENCE

+

LOCAL RESOURCE PRICE

+

NEIGHBOR WAKE INHIBITION

->

WAKE
or
REMAIN DORMANT.

Then:

persistent absence of local functional need

->

return to dormancy.

GENERAL PRINCIPLE
Dormant capacity should be:

LOCALLY RECRUITABLE

not:

GLOBALLY BROADCAST-ACTIVATED.

The organism should repair:

WHERE CAPABILITY IS NEEDED

rather than:

EVERYWHERE AT ONCE.

DECISION
AR-H33 is POSITIVE WITH A COVERAGE/LATENCY TRADEOFF.

Supported synthetically:

- broadcast wake creates a severe active-resource storm;
- local damage/deficit gating eliminates envelope oversubscription in the tested population;
- marginal-value gating reduces unnecessary wake further;
- moving damage recruits spatially local dormant reserve;
- excessive anti-cascade staggering can starve repair;
- wake control should balance marginal local value against active-resource price and local anti-cascade inhibition.

Not demonstrated:

- final wake signaling rule;
- real spatial resource field;
- optimal refractory range;
- asynchronous wake races;
- overlapping multiple damage regions;
- wake decisions under adversarial false damage;
- long-term pruning of dormant lineages that are never reused.

CLEAN SCIENTIFIC PAUSING POINT
H27-H33 now form a coherent decentralized lifecycle/resource sequence:

H27:
local resource price can move evidence without central scheduling.

H28:
async transfer requires idempotent identity, generation validity, and stale-price expiry.

H29:
dead-cell-held resource needs lease/escrow separate from cell identity.

H30:
division must conserve scarce resource while copied inherited information retains shared provenance.

H31:
growth should price future maintenance and support reversible dormancy.

H32:
dormancy should retain compact slow prior + fit confidence,
not full stale fast phenotype.

H33:
dormant reserve should wake locally by functional value,
not broadcast globally.

NEXT HIGH-VALUE QUESTION
AR-H34 — DORMANT-LINEAGE RETIREMENT / PRUNING VALUE

Question:

How long should unused dormant structure be retained?

Permanent dormancy still consumes:
memory
+
lineage bookkeeping
+
potential wake-search cost.

Compare:

A.
never prune dormant lineages;

B.
age-only retirement;

C.
reuse-frequency / functional-value retirement;

D.
memory-pressure adaptive retirement;

E.
rare but critical lineage that has long inactivity before sudden reuse.

Desired:

unused low-value lineage
->
eventual deletion.

rare but high-value regenerative lineage
->
retain if its expected future value justifies storage.

This is the dormant-memory analogue of:
value-of-information.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
grid = 20x20
primary_seeds = 100
initial_active = 80
initial_dormant = 320
active_envelope = 180
simulation_steps = 160
