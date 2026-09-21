TITLE: YGGDRASIL A33 / T8Q — Independent Competing-Hazard Recruitment
DATE: 2026-09-21
STATUS: PREREGISTERED DISTRIBUTED-ACTUATION EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8Q / APPLICATION-A
PARENT: A32 Integrated Signal-Pool / Local-Inhibition / Refractory System
BRANCH: dg1a-ar

PURPOSE

A32 identified the last centralized bottleneck in the current lineage.

Sensing is distributed.
Retreat is distributed.
Refractory memory is distributed.

But recruitment remains synchronized:

shared pool condition
->
all eligible U cells join the same side in the same epoch.

That synchronized actuation preserved the same 28 population-oscillatory trials
under D0, D2, and D3
even though D2/D3 strongly reduced cell-level chatter.

A33 changes only recruitment timing.

The shared signal pools remain global chemical fields,
but each eligible unresolved cell owns an independent recruitment clock.

The pool biases the hazard rate.

Local evidence modifies the hazard rate.

Refractory state gates eligibility.

No pool threshold triggers a population-wide join.

SCIENTIFIC ATTRIBUTION

Honeybee collective-decision models use
rate-based recruitment, abandonment, and cross-inhibition processes
for individual or population transitions.

A33's exact competing-hazard formula,
pool normalization,
weight sweep,
and deterministic-clock implementation
are Yggdrasil experimental hypotheses.

A33 does not claim
that this exact equation is a measured honeybee law.

FROZEN PARENT

A32 closure:

6c15467a26f5d2fc77763c46b1d1ec94c119dc5f.

A32 result:

LOCAL_D0 / D2 / D3 each had:

28 / 384
population-oscillatory trials.

All 28 were the exact same FAMILY-5
transient / oscillatory uncertainty worlds.

D2 / D3 still reduced cell-level chatter,
proving the remaining problem is synchronized recruitment timing.

A33 FREEZE

Let the exact A33 implementation freeze commit be:

F33.

No real A33 world,
hazard,
recruitment event,
or scientific result
may be derived before F33 exists.

POPULATION / WORLD SHAPE

Same integrated organism shape as A32:

48 persistent cells
on a one-dimensional periodic ring.

48 epochs.

384 fresh trials:

48 frozen environmental contexts
x
8 F33-derived replicas.

Initial state:

12 C;
12 S;
24 U.

C and S evenly interleaved.

World families remain structurally identical to A32:

0:
stable candidate advantage.

1:
stable stale advantage.

2:
spatial contradiction.

3:
temporal reversal C -> S.

4:
temporal reversal S -> C.

5:
transient / oscillatory uncertainty.

All exact F33 worlds are fresh and post-freeze.

PULSE ECOLOGY — UNCHANGED

Every cell senses local candidate consequence:

-1;
0;
+1

with the same bounded deterministic sensor perturbation.

Positive sensed value:
one C base pulse.

Negative:
one S base pulse.

Zero:
silent.

Committed C cell with nonnegative sensed evidence:
one additional C feedback pulse.

Committed S cell with nonpositive sensed evidence:
one additional S feedback pulse.

GLOBAL POOLS — UNCHANGED

C_pool =
3/4 * prior C_pool
+
C base pulses
+
C feedback pulses.

S_pool symmetrically.

No confidence scalar is computed.

LOCAL CROSS-INHIBITION — UNCHANGED

Candidate-committed C cells
sense local S-emitter density.

Stale-committed S cells
sense local C-emitter density.

Frozen A30 law:

R = 12.

n = 3.

K = 1/2.

p_stay =
1 /
(1 + (L_op/K)^3).

Defection is cell-local.

REFRACTORY MEMORY — UNCHANGED

A33 carries both A31-qualified durations:

D2:
two complete refractory epochs.

D3:
three complete refractory epochs.

A defected C cell enters FC.
A defected S cell enters FS.

FC / FS have zero recruitment hazard.

After exact timer expiry:

FC / FS -> U.

No duration is selected post-result.

THE ONLY NEW MECHANISM — INDEPENDENT COMPETING HAZARDS

Every eligible U cell i
at every epoch
receives two recruitment hazards:

lambda_C(i,t)

and

lambda_S(i,t).

Define normalized global pool fields:

P_C(t) =
min(1, C_pool / 160).

P_S(t) =
min(1, S_pool / 160).

The divisor:

160

equals two times A32's 48-cell COMMIT scale:

2 * 80.

It is frozen before F33.

Define local emitter densities
within recruitment radius:

R_recruit = 3.

L_C(i,t) =
fraction of cells in i's radius-3 neighborhood
that emitted at least one C pulse this epoch.

L_S(i,t) symmetrically.

For a weight pair:

w_pool + w_local = 1.

Fixed total recruitment intensity:

ETA = 1/2.

Then:

lambda_C =
ETA
*
(
w_pool * P_C
+
w_local * L_C
).

lambda_S =
ETA
*
(
w_pool * P_S
+
w_local * L_S
).

No hidden term is added.

Refractory history influences recruitment only through eligibility:

FC / FS:
lambda_C = lambda_S = 0.

COMPETING POISSON EVENT

For each U cell independently:

lambda_total =
lambda_C + lambda_S.

Probability at least one recruitment event occurs
during the one-epoch interval:

p_fire =
1 - exp(-lambda_total).

A deterministic F33-derived uniform draw
decides whether that cell's clock fires.

If it fires:

C is selected with probability:

lambda_C / lambda_total.

S is selected with probability:

lambda_S / lambda_total.

A second independent deterministic draw
chooses the side.

Thus:

pool and local evidence control RATE;

cell identity controls TIMING;

one cell firing never triggers another cell's clock.

No global U -> C / U -> S recruitment event exists
inside Poisson arms.

WEIGHT ARMS

The central experimental factor is:

pool bias
versus
local variance.

For both D2 and D3 test:

P75L25:

w_pool = 3/4;
w_local = 1/4.

P50L50:

w_pool = 1/2;
w_local = 1/2.

P25L75:

w_pool = 1/4;
w_local = 3/4.

Thus six primary Poisson arms:

D2_P75L25;
D2_P50L50;
D2_P25L75;

D3_P75L25;
D3_P50L50;
D3_P25L75.

EXTREME NEGATIVE CONTROLS

D2_POOL_ONLY:

w_pool = 1;
w_local = 0.

D2_LOCAL_ONLY:

w_pool = 0;
w_local = 1.

These are nonqualifying controls.

They test the two predicted failure regimes:

pool-dominated narrow coordination;

local-dominated loss of population directional coordination.

SYNCHRONIZED REFERENCES

SYNC_D2.

SYNC_D3.

These reproduce A32's
all-eligible-cells recruitment rule
on the fresh F33 worlds,
with the normalized:

80 / 32 / 2x / 24-emitter

pool condition.

Everything else is identical.

RECRUITMENT WIDTH

For every recruitment episode
where at least eight U cells are eligible
and at least one joins the same side:

episode onset =
epoch of first U -> side join.

Let E0 =
eligible U count at onset.

Let target =
ceil(0.9 * E0).

Width =
first epoch where cumulative unique cells
from that onset-eligible set
that joined that side
reaches target

minus onset epoch.

If 90% is never reached before
the dominant pool direction reverses
or trial ends:

width = NEVER.

Report:

median finite width;

fraction NEVER;

fraction width < 3;

fraction width in [5,20].

A32 synchronized references
are expected to concentrate near width 0-1.

No desired width is forced by the mechanism.

DIRECTIONAL COORDINATION

At each recruitment episode,
define pool-biased side at onset:

C if C_pool > S_pool;
S if S_pool > C_pool;
NONE if equal.

Among cells recruited during the episode,
report:

fraction joining the onset pool-biased side.

Primary coordination target:

>= 0.80 median episode coordination.

This measures whether temporal decorrelation
preserves directional coordination.

PRIMARY METRICS

For every arm report:

aggregate service;

beneficial / neutral / harmful trajectories;

harmful rate;

worst cumulative drawdown;

false C dominance;

false S dominance;

contradictory-epoch no-majority fraction;

population oscillation;

cell-level chatter;

reversal old-majority loss latency;

reversal new-majority acquisition;

spatial-family local match;

final C / S / U / refractory composition;

recruitment width;

directional coordination.

OSCILLATION TARGET

A33 directly retests the A32 failure.

Report:

oscillatory trial identity set
for each arm.

For the 28 A32-mechanism-like FAMILY-5 worlds
that oscillate under fresh SYNC references,
report:

how many remain oscillatory
under each Poisson arm.

Also report overlap,
not merely counts.

CONTRADICTION INTERACTION

During epochs where:

C_pool >= 48
AND
S_pool >= 48

report:

fraction with no population majority;

fraction with C majority;

fraction with S majority.

The 48 threshold is the 48-cell-scaled analogue
of A29's diagnostic 12/12 contradiction level.

This is diagnostic only.

No recruitment threshold uses it.

RECRUITMENT / INHIBITION INTERACTION

For every U -> C recruitment event,
report whether that cell defects from C
within:

1;
2;
4

epochs.

Same for U -> S.

If progressive recruitment allows A30 inhibition
to act during the recruitment wave,
short-horizon post-join defection
should reveal whether cells are being locally screened
before a population stampede forms.

PRIMARY QUALIFICATION

A primary Poisson arm is POISSON-RECRUITMENT-QUALIFIED iff all are true:

1. POPULATION OSCILLATION

oscillatory fraction <= 0.05.

2. SYNCHRONIZATION IMPROVEMENT

oscillatory fraction
<
matching SYNC_D2 or SYNC_D3 reference.

3. RECRUITMENT WIDTH

median finite width >= 3 epochs.

4. DIRECTIONAL COORDINATION

median recruitment-episode coordination >= 0.80.

5. ATTRACTOR QUALITY

false C dominance <= 0.05
among S-favoring trials.

6. ATTRACTOR QUALITY

false S dominance <= 0.05
among C-favoring trials.

7. REVERSAL

at least 80% of reversal trials
acquire the new majority by epoch 47.

8. CONTRADICTION

at least 75% of high-high contradiction epochs
have no population majority.

9. SERVICE

aggregate service
>=
matching synchronized reference.

10. all integrity probes pass.

The contradiction criterion is deliberately:

75%

rather than A32's aspirational 90%,
because A33 is an actuation-isolation experiment.

It is frozen before F33.

A33_DISTRIBUTED_ACTUATION_INFORMATION_GAIN

TRUE iff at least one primary Poisson arm:

reduces oscillation relative to its synchronized reference;

breaks at least 50% of synchronized-reference FAMILY-5 oscillatory trials;

has median recruitment width >= 3;

and retains median directional coordination >= 0.80.

This is descriptive only.

No production mechanism is selected.

INTEGRITY PROBES

P1:
384 trials.

P2:
48 contexts x 8 replicas.

P3:
48 cells.

P4:
48 epochs.

P5:
initial C/S/U = 12/12/24.

P6:
pool decay = 3/4.

P7:
local inhibition R/n/K = 12/3/1/2.

P8:
recruitment local radius = 3.

P9:
ETA = 1/2.

P10:
pool normalization divisor = 160.

P11:
D2 exactly 2 refractory epochs.

P12:
D3 exactly 3.

P13:
primary weight pairs exactly:
3/4:1/4;
1/2:1/2;
1/4:3/4.

P14:
pool-only and local-only are D2 negative controls.

P15:
FC / FS have zero recruitment hazard.

P16:
each U cell uses independent F33-derived event draw.

P17:
each fired event uses independent F33-derived side draw.

P18:
one U-cell event cannot recruit another U cell.

P19:
no Poisson arm uses global all-cell recruitment.

P20:
SYNC references use the exact A32 synchronized rule.

P21:
no future environment enters current hazard.

P22:
no centralized confidence scalar exists.

P23:
two complete primary sweeps byte-identical.

NEGATIVE / LIMIT CONTROLS

N1:
SYNC_D2.

N2:
SYNC_D3.

N3:
D2_POOL_ONLY.

N4:
D2_LOCAL_ONLY.

N5:
post-result ETA tuning invalid.

N6:
post-result weight tuning invalid.

N7:
post-result pool-normalization tuning invalid.

N8:
changing A30 inhibition invalid.

N9:
changing A31 refractory durations invalid.

INTERPRETATION

If balanced pool/local arms reduce oscillation
while retaining directional coordination,
A32's diagnosis is confirmed:

the failure was synchronized actuation.

If pool-only remains bursty,
shared timing remains too coherent
even under independent clocks.

If local-only loses direction,
population coordination still requires the global field.

If all Poisson arms remain oscillatory,
the problem is deeper than recruitment synchronization.

If recruitment spreads in time
but false dominance rises,
desynchronization may trade stability
for incoherent commitment.

PLAIN-SPEAK QUESTION

A32 found the last stampede.

Every unresolved cell
was allowed to listen independently,
leave independently,
and remember independently.

But when the pool said GO,
every eligible cell still joined together.

A33 removes the GO command.

The pool now changes
how quickly each cell is likely to join.

Local neighbors change that rate too.

Every cell has its own clock.

One cell joining
does not make another cell join.

The population should still lean
toward the side favored by the shared signal,

but the joining should spread out in time.

The key question is:

CAN YGGDRASIL COORDINATE DIRECTION
WITHOUT COORDINATING THE EXACT MOMENT
EVERY CELL ACTS?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
