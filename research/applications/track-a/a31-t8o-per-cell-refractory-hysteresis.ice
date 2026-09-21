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


PRE-RUN IMPLEMENTATION FREEZE 01 — A31 PER-CELL REFRACTORY HYSTERESIS

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F31-DERIVED SPATIAL WORLD,
REFRACTORY TRANSITION,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

094eaab7f8d717781cd4568915a61941114914bb.

SOURCE BUNDLE

Loader:

research/applications/track-a/a31_t8o_per_cell_refractory_hysteresis_v1.py

Loader Git blob:

e37781bf4120bddba2ac39da2d75484c13ef9e11.

Payload:

research/applications/track-a/a31_t8o_per_cell_refractory_hysteresis_v1.py.gz

Payload Git blob:

49f4f4d14eac80d8c76d622cda69b8823d0a62d2.

Decompressed source SHA-256:

dfb3290ee3d2c2efc059546930349ce18b3c3dc17a12367755c0006f03643192.

Decompressed source bytes:

13316.

Deterministic gzip SHA-256:

ad3ef270afc219e519ee8c9bb0975bacb90e4ba65549f704e2b9ec554226c771.

Compressed payload bytes:

4420.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake seed:

MECHANICAL-F31-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized semantic output SHA-256:

37ec7e3edee2ea3b4327988c09f39bd285bd0ef99eab9cd5d3070a2658601b50.

All P1-P20 integrity probes:

PASS.

D0:

oscillatory:
39 / 384
=
10.156%.

chatter-trial fraction:

64.84%.

broad median erosion latency:

0.

one-emitter robustness:

100%.

D1:

oscillatory:

4.95%.

chatter reduction vs D0:

15.66%.

recovery within D0 +4:

85.41%.

D1 did NOT qualify
because chatter reduction was below 25%.

D2:

oscillatory:

2.083%.

chatter reduction:

31.73%.

broad median erosion latency:

0.

one-emitter robustness:

100%.

strategic one/two-emitter collapse:

0%.

recovery within D0 +4:

83.26%.

D2 mechanically met every preregistered qualification criterion.

D3:

oscillatory:

2.083%.

chatter reduction:

57.03%.

recovery within D0 +4:

77.68%.

D3 failed the 80% recovery criterion.

D4:

oscillatory:

1.302%.

chatter reduction:

79.52%.

recovery within D0 +4:

78.97%.

D4 failed the 80% recovery criterion.

D6:

oscillatory:

0.260%.

chatter:

0.

recovery within D0 +4:

67.81%.

D6 failed recovery.

D8 negative control:

oscillatory:

0%.

chatter:

0.

recovery within D0 +4:

62.66%.

This demonstrates the expected tradeoff:

more refractory memory
suppresses chatter

but eventually makes recovery too sticky.

No duration,
qualification threshold,
inhibition law,
or recruitment law
is changed in response.

This is NON-SCIENTIFIC mechanical evidence only.

REAL A31 STATUS

No real F31-derived trial exists.

No real refractory outcome exists.

No real A31 manifest exists.

Let the resulting commit SHA be:

F31.

After F31 exists:

1. derive exactly 384 fresh challenge identities from F31;
2. bind the complete challenge manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. report every duration without post-result selection.

NO POST-RESULT DURATION TUNING.
NO INHIBITION CHANGE.
NO RECRUITMENT CHANGE.
NO QUALIFICATION CHANGE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A31 PER-CELL REFRACTORY HYSTERESIS

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A31 REFRACTORY TRANSITION
OR SCIENTIFIC OUTCOME.

F31:

154a59206aa9056d2b8ba40ca3ff95da648bebfe.

FROZEN SOURCE SHA-256:

dfb3290ee3d2c2efc059546930349ce18b3c3dc17a12367755c0006f03643192.

TRIAL COUNT:

384.

STRUCTURE:

48 frozen challenge contexts
x
8 F31-derived replicas.

CELLS:

48.

EPOCHS:

40.

COMPLETE CHALLENGE-MANIFEST SHA-256:

c743fe0b201de624d90057d203dcc54f7504d24278843bf9073cd42d0404be3f.

Serialized manifest-wrapper SHA-256:

24bbd2314791802141f5f3255777073041a947949277be5c61323edcb26723a8.

Serialized manifest-wrapper bytes:

297262.

The manifest binds:

trial identity;
challenge family;
replica;
and exact opposition-emitter identities
for all 40 epochs.

PRIMARY STATUS AT MANIFEST BIND

Real refractory transitions observed:

0.

Real oscillation outcomes observed:

0.

Real recovery outcomes observed:

0.

Real qualification outcomes observed:

0.

The next permitted operation is:

two complete deterministic A31 primary sweeps
using F31 as the experimental seed.

NO CHALLENGE REDRAW.
NO DURATION CHANGE.
NO INHIBITION CHANGE.
NO RECRUITMENT CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-RUN CLOSURE — A31 / T8O PER-CELL REFRACTORY HYSTERESIS

DATE:
2026-09-21.

STATUS:
CLOSED / REPRODUCIBLE POSITIVE MECHANISM RESULT /
D2 AND D3 MET EVERY FROZEN QUALIFICATION CRITERION /
LOCAL REFRACTORY MEMORY SUPPRESSED CHATTER
WITHOUT SACRIFICING FAST BROAD-OPPOSITION EROSION /
NON-CANONICAL.

FROZEN IMPLEMENTATION

Implementation commit:

094eaab7f8d717781cd4568915a61941114914bb.

F31:

154a59206aa9056d2b8ba40ca3ff95da648bebfe.

Source SHA-256:

dfb3290ee3d2c2efc059546930349ce18b3c3dc17a12367755c0006f03643192.

BOUND PRIMARY MANIFEST

Manifest-bound commit:

9d8597203247f1136715a7cfb1b09664babd85b8.

Challenge-manifest SHA-256:

c743fe0b201de624d90057d203dcc54f7504d24278843bf9073cd42d0404be3f.

Manifest-wrapper SHA-256:

24bbd2314791802141f5f3255777073041a947949277be5c61323edcb26723a8.

PRIMARY REPRODUCIBILITY

Two complete F31-derived primary sweeps were byte-identical.

Serialized semantic output SHA-256:

cfca3d7ed4bc4ba71b556b260e67c8e788127676a0a706e64b76136ef84f6cef.

All P1-P20 integrity probes:

PASS.

PRIMARY RESULT

A31_REFRACTORY_INFORMATION_GAIN:

TRUE.

REFRACTORY-QUALIFIED durations:

D2;
D3.

No production duration is selected.

D0 — NO REFRACTORY MEMORY

Oscillatory:

49 / 384
=
12.7604%.

Chatter trials:

246 / 384
=
64.0625%.

Chatter events:

2524.

Broad-opposition median erosion latency:

0 epochs.

One-emitter robustness:

100%.

Strategic one/two-emitter collapse:

0%.

Finite D0 recoveries:

231.

D1 — ONE EPOCH

Oscillatory:

15 / 384
=
3.90625%.

Chatter trials:

219.

Chatter reduction vs D0:

10.98%.

Recovery within D0 +4:

89.61%.

Broad erosion latency:

0.

D1 DID NOT QUALIFY.

Failure:

chatter reduction < 25%.

Interpretation:

one epoch of refractory memory
strongly reduced majority-level oscillation,
but was too short to suppress enough per-cell recommit-defect chatter.

D2 — TWO EPOCHS

Oscillatory:

1 / 384
=
0.2604%.

Chatter trials:

171.

Chatter reduction vs D0:

30.49%.

Chatter events:

526

versus D0:

2524.

Broad erosion latency:

0.

Broad never-eroded:

0 / 48.

One-emitter robustness:

100%.

Strategic one/two-emitter collapse:

0%.

Recovery within D0 +4:

83.98%.

Mean refractory occupancy:

2.4375 cells.

Wounds:

HEALS = 177;
PERSISTS = 41;
PROPAGATES = 166.

D2 REFRACTORY-QUALIFIED:

TRUE.

D3 — THREE EPOCHS

Oscillatory:

7 / 384
=
1.8229%.

Chatter trials:

125.

Chatter reduction vs D0:

49.19%.

Chatter events:

225.

Broad erosion latency:

0.

One-emitter robustness:

100%.

Strategic one/two-emitter collapse:

0%.

Recovery within D0 +4:

81.39%.

Mean refractory occupancy:

3.1544 cells.

Wounds:

HEALS = 180;
PERSISTS = 32;
PROPAGATES = 172.

D3 REFRACTORY-QUALIFIED:

TRUE.

D4 — FOUR EPOCHS

Oscillatory:

1.0417%.

Chatter reduction:

78.86%.

Recovery within D0 +4:

77.49%.

D4 DID NOT QUALIFY.

Failure:

recovery < 80%.

D6 — SIX EPOCHS

Oscillatory:

0.5208%.

Chatter:

0.

Recovery within D0 +4:

70.13%.

D6 DID NOT QUALIFY.

D8 — OVERSLOW NEGATIVE CONTROL

Oscillatory:

0.78125%.

Chatter:

0.

Recovery within D0 +4:

64.07%.

D8 was nonqualifying by design
and confirms the sticky-memory failure mode.

TRADEOFF CURVE

The real sweep reproduced a coherent refractory-memory curve:

D0:

high oscillation;
high chatter;
fast recovery.

D1:

large oscillation improvement;
insufficient cell-level chatter suppression.

D2-D3:

low oscillation;
substantial chatter suppression;
acceptable recovery.

D4+:

very low chatter,
but recovery becomes too slow.

This supports a finite local-memory regime
rather than:

no memory

or:

permanent / excessive memory.

TECHNICAL INTERPRETATION

A31 directly resolves the specific A30 near-pass failure.

A30's R12N3 local cross-inhibition
already provided:

fast broad-opposition erosion;
small-minority robustness;
spatial selectivity.

Its remaining problem was
immediate re-recruitment and majority-boundary chatter.

A31 changed only
post-defection eligibility.

With two or three complete refractory epochs,
the system retained:

zero-median broad erosion latency;

100% one-emitter robustness;

0% collapse from the tested strategic one/two-emitter minorities;

while pushing oscillation
well below the frozen 5% ceiling.

Therefore:

LOCAL CROSS-INHIBITION
+
SHORT PER-CELL REFRACTORY MEMORY

is materially more stable
than local cross-inhibition with immediate re-entry.

The mechanism remains distributed.

A cell's local history changes
its own future eligibility.

There is no:

global confidence score;
global retreat gate;
global refractory timer;
or centralized state reset.

The memory is embodied in cell state.

IMPORTANT LIMIT

A31 is a dedicated mechanism harness.

It does not yet prove
that D2 or D3 should be integrated
into the full A29 distributed signal-pool organism.

That integration requires a separate
post-A31 preregistered experiment.

A31 also does not select between D2 and D3.

Both qualified.

Any later integration can preserve both
as frozen candidate mechanisms
or preregister an independent discrimination test.

PLAIN-SPEAK INTERPRETATION

This worked.

A30 taught a cell:

"if enough of my neighborhood disagrees,
leave commitment."

But the cell could immediately be talked back into commitment.

That caused chatter.

A31 gave the cell one extra piece of local state:

"I was just contradicted."

For a short time,
it cannot recommit.

Two or three epochs of that memory
was enough.

With no memory,
49 of 384 populations oscillated.

With two epochs of memory:

1 did.

With three epochs:

7 did.

The two-epoch system also cut
cell-level chatter by about 30%.

The three-epoch system cut it
by about 49%.

And both still reacted immediately
when broad opposition appeared.

Longer memory kept reducing chatter,
but started hurting recovery.

So we found a real middle region:

TOO LITTLE MEMORY:

cells forget contradiction too quickly.

TOO MUCH MEMORY:

cells stay uncertain too long.

SHORT LOCAL MEMORY:

the population changes its mind
without immediately changing it back.

That is exactly the hysteresis behavior
A31 was meant to test.

A24:
distributed breadth signal useful.

A25:
temporal persistence useful.

A26:
magnitude threshold insufficient.

A27:
negative feedback useful but noisy.

A28:
uncertainty-as-population-state useful.

A29:
local signal pools improve attractor quality.

A30:
local nonlinear retreat is fast and selective,
but chatters.

A31:
short per-cell refractory memory suppresses that chatter
while retaining fast retreat and minority robustness.

No autonomous production controller is authorized.

DG-1R-05 remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
