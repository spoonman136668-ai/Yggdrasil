TITLE: DG-1A-AR-H31 — Recursive Lineage Growth Under a Global Resource Envelope
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE BURST-GROWTH + DORMANCY RESULT / RESOURCE-ENVELOPE LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh30-cell-division-resource-inheritance-audit.ice

PURPOSE
H30 established conservative resource inheritance across cell division.

H31 tests the larger north-star question:

Can repeated local growth increase capability when needed
without making permanently active structure grow at the same rate?

The desired pattern is:

temporary expansion
+
repair
+
later contraction / dormancy

under one fixed resource envelope.

BOUNDARY
This is synthetic.

It does not:
- implement a full Yggdrasil developmental organism;
- freeze a final dormancy threshold;
- freeze resource inflow;
- prove the active-cell count maps directly to neural compute cost;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SYSTEM
Mean-field lineage population.

Initial cells:

active:
40

dormant:
10.

Initial resource reserve:
500.

Maximum reserve:
700.

Per-step external resource inflow:
65.

Maintenance cost:

active cell:
1.0

dormant cell:
0.08.

Division cost:
4.

TASK / DEVELOPMENTAL DEMAND
Demand schedule:

steps 0..299:
40.

300..599:
90.
Expansion challenge.

600..899:
50.
Consolidation period.

step 900:
30% active-cell damage.

900..1049:
80.
Repair challenge.

1050..1399:
50.
Late stable period.

CAPABILITY METRIC
Immediate service:

min(active_cells, demand)
/
demand.

This is intentionally simple.

It measures whether active structure can supply current synthetic demand.

POLICIES

NAIVE LOCAL DIVISION
When demand exceeds active capability,
many active cells independently divide.

No meaningful long-horizon resource check.

No dormancy.

RESOURCE-FLOOR GATING
Division is suppressed when reserve falls below a hard local/global floor.

No dormancy.

METABOLIC PRICE GATING
Division probability is reduced as active maintenance load approaches/exceeds sustainable inflow.

No dormancy.

LINEAGE ESCROW + DORMANCY
Rules:

1.
wake dormant cells before creating new cells;

2.
division pays explicit cost;

3.
division additionally checks a short synthetic maintenance runway;

4.
daughter growth is therefore bounded by current reserve;

5.
persistent excess active structure enters dormancy instead of remaining permanently active.

Dormancy is reversible.

PRIMARY CONFIRMATION
50 matched synthetic seeds.

1400 steps per seed.

NAIVE LOCAL DIVISION

mean service:
0.41652.

peak active:
93.74.

final active:
14.22.

final dormant:
9.0.

mean divisions:
1815.92.

mean cell deaths:
1842.70.

minimum resource pool:
approximately 0.

Expansion-period service:
0.26448.

Repair-period service:
0.15349.

Late service:
0.25975.

PRIMARY RUNAWAY NEGATIVE
The naive population repeatedly overshoots the resource envelope,
then starves.

It performs:

many divisions

without preserving:

stable active capability.

This is the lineage-level analogue of H26's probe storm.

MORE GROWTH ACTIVITY
DOES NOT IMPLY
MORE SUSTAINABLE CAPABILITY.

RESOURCE-FLOOR GATING

mean service:
0.92056.

peak active:
92.18.

final active:
64.0.

final dormant:
9.0.

divisions:
72.18.

deaths:
49.18.

Expansion service:
0.72775.

Consolidation service:
1.000.

Repair service:
0.80308.

Late service:
1.000.

METABOLIC PRICE GATING

mean service:
0.92107.

peak active:
90.52.

final active:
64.0.

final dormant:
9.0.

divisions:
70.52.

deaths:
47.52.

Expansion service:
0.72889.

Repair service:
0.80558.

Late:
1.000.

PRIMARY RESOURCE-GATE POSITIVE
Simple budget pressure prevents the catastrophic growth/starvation cycle.

However:
both non-dormant policies retain approximately:

64 active cells

during the late demand-50 period.

They preserve service,
but permanently active structure remains substantially above current functional demand.

LINEAGE ESCROW + DORMANCY

mean service:
0.92898.

peak active:
90.46.

final active:
52.0.

final dormant:
13.0.

divisions:
73.24.

deaths:
58.24.

Expansion service:
0.74096.

Consolidation service:
1.000.

Repair service:
0.85524.

Late service:
1.000.

mean final resource reserve:
646.96.

PRIMARY NORTH-STAR POSITIVE
The dormant-lineage policy maintains full late service with:

approximately 52 active cells

instead of:

64 active cells

for the non-dormant budgeted policies.

This is an active-structure reduction of approximately:

18.75%.

The dormant cells preserve latent regenerative capacity
without paying full active maintenance.

Thus:

CAPABILITY RESERVE
CAN BE RETAINED
WITHOUT KEEPING ALL STRUCTURE PERMANENTLY ACTIVE.

CONTRACTION AFTER EXPANSION
Demand falls:

90
->
50

at step 600.

LINEAGE ESCROW + DORMANCY

median time to return to:
<=55 active cells

15 steps.

RESOURCE-FLOOR

does not reach <=55
within the 300-step consolidation window.

METABOLIC PRICE

does not reach <=55
within the window.

PRIMARY CONTRACTION RESULT
Growth control alone is insufficient.

A developmental system also needs:

ACTIVE-STRUCTURE RELEASE.

Dormancy provides a reversible release mechanism.

DAMAGE / REGENERATION RESULT
At step 900,
30% of active cells are removed.

Demand simultaneously rises to:
80.

Measure time until service stays >=90% for 10 consecutive steps.

NAIVE

mean latency:
110.76.

median:
150
=
tested horizon cap.

RESOURCE-FLOOR

no seed reaches the criterion within the 150-step repair window.

METABOLIC PRICE

no seed reaches it within the window.

LINEAGE ESCROW + DORMANCY

mean recovery latency:
2.16 steps.

median:
2.

recovery within window:
100%.

PRIMARY REGENERATION POSITIVE
Dormant cells can wake before expensive new division.

This produces a large repair advantage.

The same cells that reduced permanent active cost during stable conditions become:

rapid regenerative reserve

when damage occurs.

This directly supports the architectural role of:

HIBERNATION / DORMANCY

as more than energy saving.

It is:
stored recoverable capability.

RESOURCE ENVELOPE PRINCIPLE
The system needs at least three distinct lifecycle actions:

DIVIDE
increase structural capacity.

DORMANT
retain lineage state at low active cost.

DIE / PRUNE
release structure entirely.

These actions should not be collapsed.

A mature region can:
sleep

without:
forgetting

or:
dying.

RELATION TO H30
H30:
division-time scarce resource should be split/escrowed,
not copied.

H31:
population-level growth should also be bounded by:
future maintenance liability.

Division is not only:
a one-time creation cost.

It creates:
ongoing resource obligation.

RELATION TO H26
H26:
short-horizon marginal VoI can starve slow structure,
so long-horizon access matters.

H31 shows the complementary population rule:

short-horizon growth benefit can create long-horizon maintenance debt.

Therefore resource price should eventually include:

EXPECTED FUTURE MAINTENANCE.

RELATION TO END GOAL
The current synthetic result directly supports the Yggdrasil objective:

CAPABILITY CAN EXPAND
during challenge

while

PERMANENTLY ACTIVE STRUCTURE
returns toward a lower stable level afterward.

This is still a synthetic systems result.

It is not a real Yggdrasil performance result.

DECISION
AR-H31 is POSITIVE.

Supported synthetically:

- unconstrained recursive local division can produce severe growth/starvation oscillation;
- explicit resource pressure stabilizes population growth;
- growth gating alone leaves excess structure permanently active;
- reversible dormancy reduces stable active structure while maintaining task service;
- dormant lineages provide rapid regenerative capacity after damage;
- division decisions should price future maintenance obligation, not only creation cost.

Not demonstrated:

- real Yggdrasil dormancy representation;
- wake/sleep decision from target-free local signals;
- information degradation during long dormancy;
- memory integrity after repeated wake cycles;
- spatial dormancy coordination;
- optimal pruning versus dormancy;
- capability scaling beyond simple active-cell count.

NEXT CLEAN QUESTION
AR-H32 — DORMANCY MEMORY RETENTION / WAKE RELIABILITY

Question:

How much state should a dormant cell retain?

Compare:

A.
full frozen state;

B.
slow prior only;

C.
compressed lineage sketch;

D.
near-stateless dormancy.

Stress:
- long sleep durations;
- context changes during sleep;
- repeated sleep/wake cycles;
- stale inherited state on wake;
- resource cost of retained dormant state.

Desired:

dormant tissue should wake quickly
without:
carrying indefinitely stale fast state
or
paying near-active memory cost.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_matched_seeds = 50
simulation_steps = 1400
resource_inflow_per_step = 65
initial_active_cells = 40
initial_dormant_cells = 10
damage_step = 900
