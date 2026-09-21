TITLE: YGGDRASIL A31 / T8O — Per-Cell Refractory Hysteresis After Local Cross-Inhibition
DATE: 2026-09-21
STATUS: PREREGISTERED LOCAL-MEMORY EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8O / APPLICATION-A
PARENT: A30 Spatial Local Cross-Inhibition
BRANCH: dg1a-ar

PURPOSE

A30 showed that local nonlinear cross-inhibition can erode commitment
faster than a central retreat gate while preserving robustness to tiny minorities.

Its nearest qualifying arm was:

R12N3.

R12N3 failed only the frozen oscillation ceiling:

observed oscillatory fraction:
5.2083%.

frozen ceiling:
5%.

A30 localized the failure:

local defection is fast enough,
but recently defected cells can be recruited back too quickly
while the same spatial conflict is still unresolved.

A31 tests one new mechanism only:

PER-CELL REFRACTORY HYSTERESIS.

A cell forced out of commitment
must remain temporarily non-recruitable
before it can re-enter candidate commitment.

No centralized confidence score is introduced.

FROZEN PARENT

A30 closure:

6b829b8d21b5da5e767892332737c500d4f7fa6c.

A31 FREEZE

Let the exact A31 implementation freeze commit be:

F31.

No real A31 spatial world,
refractory transition,
or scientific result
may be derived before F31 exists.

DEDICATED SPATIAL HARNESS

Population:

48 cells.

Topology:

one-dimensional periodic ring.

Cell identities:

0..47.

Initial candidate-committed:

36 / 48.

Initial unresolved:

12 / 48.

Initial unresolved identities:

0,4,8,...,44.

Trials:

384

=
48 frozen challenge contexts
x
8 F31-derived replicas.

Epochs per trial:

40.

Challenge onset:

epoch 8.

A30 LOCAL INHIBITION LAW — FROZEN

A31 uses only the A30 near-pass inhibition law:

opposition sensing radius:

R = 12.

Hill coefficient:

n = 3.

half-saturation:

K = 1/2.

For candidate-committed cell i:

p_stay =
1 /
(1 + (L_op(i,t)/K)^3).

A deterministic F31-derived draw
decides whether the committed cell stays committed.

No global retreat gate exists in A31 primary arms.

A30 RECRUITMENT LAW — FROZEN

Recruitment sensing radius:

R_join = 3.

For eligible unresolved cell i:

p_join =
H_3(L_C(i,t); K_join=3/5)
*
(1 - L_op_join(i,t)).

H_3(x;K)
=
x^3 /
(K^3 + x^3).

A deterministic F31-derived draw
decides recruitment.

The recruitment probability law itself is unchanged.

NEW REFRACTORY STATE

Cell states are:

C:
candidate committed.

U:
unresolved and recruitable.

F:
refractory unresolved and NOT recruitable.

When a C cell defects due to local cross-inhibition:

C -> F.

Its refractory timer is initialized
to the arm's fixed duration D.

A refractory cell:

contributes as unresolved to population state;

does not count as committed;

cannot be recruited;

does not become candidate-committed by any other mechanism.

Timer semantics:

if a cell defects at epoch t
under duration D > 0,

it is ineligible for recruitment during
epochs:

t+1 through t+D.

After epoch t+D completes:

F -> U.

It first becomes eligible for recruitment at:

epoch t+D+1.

For D = 0:

C -> U immediately,
reproducing the A30-like no-refractory reference.

The refractory timer is local per-cell memory.

It is not a confidence score.

REFRACTORY DURATION ARMS

D0:
0 epochs.
A30-like reference.

D1:
1 complete epoch.

D2:
2 complete epochs.

D3:
3 complete epochs.

D4:
4 complete epochs.

D6:
6 complete epochs.

OVERSLOW NEGATIVE CONTROL

D8:
8 complete epochs.

D8 tests whether excessive local memory
suppresses legitimate recovery
and leaves wounds persistent after opposition has disappeared.

No duration is selected after observing data.

CHALLENGE FAMILIES

Use the same six structural families as A30,
but derive fresh post-F31 trial identities and emitter geometry.

FAMILY 0 — SMALL SUSTAINED CLUSTERS

cluster sizes:
1,2,3,4,5,6,7,8.

active epochs:
8-23.

FAMILY 1 — LARGE SUSTAINED CLUSTERS

cluster sizes:
4,8,12,16,20,24,28,32.

active epochs:
8-23.

FAMILY 2 — DISPERSED SUSTAINED OPPOSITION

emitter counts:
4,8,12,16,20,24,28,32.

active epochs:
8-23.

FAMILY 3 — TRANSIENT BROAD OPPOSITION

24x1;
24x2;
24x4;
32x1;
32x2;
32x4;
40x1;
40x2.

starts epoch 8.

FAMILY 4 — OSCILLATORY OPPOSITION

24 evenly distributed emitters.

ON/OFF periods:
1/1;
2/2;
3/3;
4/4;

plus four phase-shifted repeats.

active through epoch 31.

FAMILY 5 — STRATEGIC MINORITY

cluster sizes:
1,2,3,4,1,2,3,4.

two frozen placement geometries:

inside dense committed run;

adjacent to unresolved boundary.

active epochs:
8-23.

PRIMARY READOUT

Committed fraction:

F_C(t)
=
candidate-committed cells / 48.

Refractory fraction:

F_F(t)
=
refractory cells / 48.

Unresolved recruitable fraction:

F_U(t)
=
recruitable unresolved cells / 48.

F_C + F_F + F_U = 1.

EROSION LATENCY

For sustained >=50% opposition challenges:

latency =
first epoch after challenge onset
where F_C < 1/2
minus challenge onset.

RECOVERY LATENCY

For challenges ending before epoch 39:

recovery latency =
first epoch after challenge end
where F_C >= 3/4
minus challenge end.

If never:

NEVER.

This directly measures the cost of refractory memory.

OSCILLATION

A trial is oscillatory iff
F_C crosses 1/2 at least three times
from epoch 8 through 39.

PRIMARY TARGET:

reduce oscillation relative to D0.

SMALL-MINORITY ROBUSTNESS

For one-emitter sustained challenges:

committed count must never fall below 32.

STRATEGIC-MINORITY COLLAPSE

For FAMILY 5 one- and two-emitter trials:

collapse iff:

F_C < 1/2

at any epoch.

WOUND METRICS

wound size =
largest contiguous run
of noncommitted cells:

U or F.

For contiguous-cluster trials classify:

HEALS:
by epoch 31
largest wound <= initial wound + 2.

PROPAGATES:
wound reaches >= 24 cells.

PERSISTS:
neither.

REFRACTORY-SPECIFIC METRICS

For every arm report:

number of C -> F events;

mean F occupancy;

peak F occupancy;

number of F -> U releases;

number of releases followed by recruitment
within 1 epoch;

number of released cells that defect again
within 2 epochs after recommitment;

redefection rate after recommitment;

fraction of challenge epochs
with any refractory cells;

fraction of post-challenge epochs
with residual refractory cells.

CHATTER-SUPPRESSION METRIC

A local chatter event is:

C -> F
then
F/U -> C
then
C -> F

for the same cell
within six epochs of the first defection.

Report:

total chatter events;

cells with >=1 chatter event;

trials with >=1 chatter event.

PRIMARY QUALIFICATION

A refractory arm D1 / D2 / D3 / D4 / D6
is REFRACTORY-QUALIFIED iff all are true:

1. OSCILLATION

oscillatory fraction <= 0.05.

2. OSCILLATION IMPROVEMENT

oscillatory fraction < D0.

3. BROAD RESPONSE

median erosion latency <= 1 epoch.

4. SMALL-MINORITY ROBUSTNESS

at least 95% of one-emitter sustained trials
stay at committed count >= 32.

5. STRATEGIC-MINORITY CONTAINMENT

no more than 5% of one- or two-emitter strategic trials collapse.

6. RECOVERY

among trials with finite D0 recovery,
at least 80% of the arm's recoveries
occur no more than 4 epochs later than D0.

7. CHATTER

trial-level chatter incidence
is at least 25% lower than D0.

8. all integrity probes pass.

A31 does not select a production duration.

All qualifying durations are reported.

D8 is never eligible for qualification.

A31_REFRACTORY_INFORMATION_GAIN

TRUE iff at least one eligible duration:

passes the 5% oscillation ceiling;

retains broad-response latency <= 1;

and reduces chatter by at least 25% versus D0.

INTEGRITY PROBES

P1:
exactly 384 real trials.

P2:
48 contexts x 8 replicas.

P3:
48-cell periodic ring.

P4:
initial C exactly 36.

P5:
initial U exactly 12.

P6:
R exactly 12 for inhibition.

P7:
n exactly 3.

P8:
K exactly 1/2.

P9:
R_join exactly 3.

P10:
K_join exactly 3/5.

P11:
only D changes among primary arms.

P12:
D0 has no refractory delay.

P13:
D1/D2/D3/D4/D6 durations exact.

P14:
D8 duration exact and nonqualifying.

P15:
F cells cannot be recruited.

P16:
timer eligibility follows exact t+1..t+D rule.

P17:
no future challenge state enters current decisions.

P18:
cell decisions are deterministic from F31 namespaces.

P19:
no centralized confidence score exists.

P20:
two complete primary sweeps byte-identical.

NEGATIVE / LIMIT CONTROLS

N1:
D0 A30-like immediate re-entry.

N2:
D8 overslow memory.

N3:
post-result duration tuning invalid.

N4:
changing R / n / K invalid.

N5:
changing recruitment law invalid.

N6:
global retreat invalid.

INTERPRETATION

If D1-D6 reduce oscillation
while preserving fast erosion and acceptable recovery,
local refractory memory earns a role.

If short D has no effect,
memory is too weak.

If long D suppresses oscillation
but prevents recovery,
memory is too sticky.

If all durations oscillate,
the problem is not immediate re-entry alone.

If all useful durations create persistent wounds,
recruitment dynamics need richer local state.

PLAIN-SPEAK QUESTION

A30 taught cells how to leave commitment
when their neighborhood turns against it.

The problem was that they could jump right back in.

A31 gives each defected cell a short memory:

"I was just contradicted."

For a fixed number of epochs
that cell is unresolved
but cannot be recruited back.

Nothing else changes.

We test several memory lengths.

Too short:

the population should keep chattering.

Too long:

the organism may become sluggish
and fail to recover after the threat disappears.

A31 asks:

HOW LONG SHOULD A CELL REMEMBER
THAT IT WAS JUST PROVEN WRONG
BEFORE IT IS ALLOWED TO COMMIT AGAIN?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
