TITLE: YGGDRASIL A32 / T8P — Integrated Signal-Pool Ecology With Local Cross-Inhibition and Refractory Memory
DATE: 2026-09-21
STATUS: PREREGISTERED INTEGRATION / CONFIRMATORY MECHANISM EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8P / APPLICATION-A
PARENTS:
A29 Distributed Competing Signal Pools
A30 Spatial Local Cross-Inhibition
A31 Per-Cell Refractory Hysteresis
BRANCH: dg1a-ar

PURPOSE

A29 established that distributed candidate/stale pulse pools
improve attractor quality relative to centralized block-sign control,
but contradictory signal often persisted after commitment.

A30 established that local nonlinear cross-inhibition
can erode commitment immediately under broad opposition,
but immediate re-entry produced chatter.

A31 established that short per-cell refractory memory,
especially D2 and D3,
suppresses that chatter without sacrificing fast erosion.

A32 integrates those mechanisms in one synthetic organism.

No new confidence statistic is introduced.

The question is:

CAN THE SIGNAL-POOL ORGANISM
MAKE AND REVISE COMMITMENTS
USING ONLY DISTRIBUTED PULSES,
LOCAL CROSS-INHIBITION,
AND SHORT CELL-LOCAL MEMORY?

A32 does not choose between D2 and D3 in advance.
Both frozen A31-qualified durations are carried forward.

FROZEN LINEAGE

A29 closure:
84d4d7a04b79e769b73dd4a2469be973564d0dfd.

A30 closure:
6b829b8d21b5da5e767892332737c500d4f7fa6c.

A31 closure:
00ade8b42cc725a544dadffbb3ad3ff38cffde05.

A32 FREEZE

Let the exact A32 implementation freeze commit be:

F32.

No real A32 world,
pulse,
pool state,
local defection,
refractory transition,
or scientific result
may be derived before F32 exists.

POPULATION

48 persistent cell identities
on a one-dimensional periodic ring.

Cell states:

C:
candidate committed.

S:
stale committed.

U:
unresolved / recruitable.

FC:
candidate-refractory.

FS:
stale-refractory.

FC and FS are local memory states only.
They do not represent scalar confidence.

INITIAL STATE

Exactly:

12 C;
12 S;
24 U.

C and S are evenly interleaved around the ring.
U occupies the remaining cells.

This begins from genuine unresolved competition
rather than a preselected winner.

TRIAL COUNT

384 fresh trials:

48 frozen environmental contexts
x
8 F32-derived replicas.

Each trial:

48 cells;
48 epochs.

All stochastic / noise decisions
are deterministic from:

F32;
trial;
arm;
epoch;
cell;
decision namespace.

ENVIRONMENTAL CONTEXT FAMILIES

48 contexts are divided into six frozen families,
8 contexts each.

FAMILY 0 — STABLE CANDIDATE ADVANTAGE

Candidate local consequence is predominantly +1,
with frozen local heterogeneity and bounded sensor noise.

FAMILY 1 — STABLE STALE ADVANTAGE

Candidate local consequence is predominantly -1.

FAMILY 2 — SPATIAL CONTRADICTION

One contiguous region favors candidate;
the opposing region favors stale.

Boundary and region sizes vary across the eight contexts.

FAMILY 3 — TEMPORAL REVERSAL C -> S

Early epochs favor candidate.
Later epochs favor stale.

Reversal epoch varies across contexts.

FAMILY 4 — TEMPORAL REVERSAL S -> C

Early epochs favor stale.
Later epochs favor candidate.

Reversal epoch varies across contexts.

FAMILY 5 — TRANSIENT / OSCILLATORY UNCERTAINTY

Alternating or pulsed local preference
with zero long-run directional advantage.

All exact context parameters
are generated deterministically from F32
and bound in the post-freeze manifest.

LOCAL SENSING AND PULSES

Every epoch,
each cell receives a true local candidate consequence:

-1;
0;
+1.

A deterministic bounded sensor perturbation:

-1;
0;
+1

is added and clipped to:

-1;
0;
+1.

If sensed value > 0:

emit one C pulse.

If sensed value < 0:

emit one S pulse.

If sensed value == 0:

silent.

Persistent experience therefore produces
higher pulse frequency naturally.

GLOBAL DECAYING POOLS

At every epoch:

C_pool =
3/4 * prior C_pool
+
base C pulses
+
C positive-feedback pulses.

S_pool =
3/4 * prior S_pool
+
base S pulses
+
S positive-feedback pulses.

Positive-feedback pulses:

a C cell with nonnegative sensed evidence
emits one additional C pulse.

an S cell with nonpositive sensed evidence
emits one additional S pulse.

FC / FS / U cells emit only their base sensed pulse.

No C_pool - S_pool confidence score is stored.

POOL-BASED RECRUITMENT

An eligible U cell may become C iff:

C_pool >= 20;

S_pool <= 8;

C_pool >= 2 * S_pool;

at least 6 distinct cells emitted C pulses this epoch.

Symmetrically U -> S.

If both pools are elevated or neither side meets its rule:

U remains U.

FC and FS are never recruitable.

A29-LIKE GLOBAL REFERENCE — GLOBAL

GLOBAL uses the same pulses and pools,
but recruitment is population-wide regime control.

GLOBAL maintains one regime:

U;
C;
or S.

U -> C / S uses the same A29-style pool conditions.

C -> U uses the A29 nonlinear global opposing-pool retreat rule.

S -> U symmetrically.

Cell states follow the global regime's
frozen population composition:

U:
24 U, 12 C, 12 S;
C:
36 C, 12 U;
S:
36 S, 12 U.

This is the integration reference.

LOCAL CROSS-INHIBITION — FROZEN FROM A30

For local integration arms:

C cells sense local S-pulse density
within radius:

R = 12.

S cells symmetrically sense local C-pulse density.

Hill response:

n = 3.

K = 1/2.

For committed cell:

p_stay =
1 /
(1 + (L_op / K)^3).

If defection occurs:

C -> FC;
S -> FS.

No global all-cell retreat exists in local arms.

REFRACTORY ARMS

LOCAL_D0

local cross-inhibition;
no refractory delay.

Defected cells:

C -> U;
S -> U.

LOCAL_D2

C -> FC for exactly 2 complete epochs.

S -> FS for exactly 2 complete epochs.

Then:

FC -> U;
FS -> U.

LOCAL_D3

same,
with exactly 3 complete refractory epochs.

D2 and D3 are carried forward
because both qualified independently in A31.

No duration is selected after observing A32.

LOCAL RECRUITMENT AFTER REFRACTORY

Once U,
re-entry still requires
the pool-based recruitment rule.

Thus local memory does not itself decide
which side wins.

It only prevents immediate recommitment.

PRIMARY OUTCOME

Each candidate-controlled cell receives
its true local candidate consequence.

Each stale-controlled or unresolved/refractory cell
receives zero candidate consequence.

Trajectory service delta versus all-stale
is the sum of realized candidate consequences
over C cells.

For environments favoring stale,
negative candidate consequence
therefore correctly penalizes candidate commitment.

PRIMARY METRICS

For GLOBAL / LOCAL_D0 / LOCAL_D2 / LOCAL_D3 report:

aggregate service delta versus all-stale;

trajectory:
beneficial;
neutral;
harmful;

harmful-trajectory rate;

worst cumulative drawdown;

end-state composition;

mean C / S / U / refractory occupancy;

transition counts;

pool statistics.

ATTRACTOR QUALITY

For each trial,
define oracle directional label
from the full frozen true-consequence field:

C-FAVORING:
sum true candidate consequence > 0.

S-FAVORING:
sum < 0.

NEUTRAL:
sum == 0.

Report:

false C dominance:
final C fraction > 1/2
on S-FAVORING trial.

false S dominance:
final S fraction > 1/2
on C-FAVORING trial.

unresolved final state.

CONTRADICTION METRIC

A contradictory epoch is:

C_pool >= 12
AND
S_pool >= 12.

For local arms report:

fraction of contradictory epochs
where neither C nor S exceeds 1/2 population share.

Also report:

contradictory epochs with majority C;

contradictory epochs with majority S.

This directly retests A29's 23% committed-contradiction failure.

LOCAL CHATTER

For each cell,
a chatter event is:

committed
->
defected/unresolved
->
recommitted to same side
->
defected from same side

within six epochs of first defection.

Report:

event count;
cells affected;
trials affected.

POPULATION OSCILLATION

A trial is oscillatory iff
population majority identity among:

C-majority;
S-majority;
no-majority

changes at least four times
after epoch 8.

REVERSAL PERFORMANCE

For FAMILY 3 and FAMILY 4 report:

time from true environmental reversal
to loss of old majority;

time to acquisition of new majority;

failure to reverse by epoch 47;

overshoot / return-to-old-majority count.

SPATIAL CONTRADICTION

For FAMILY 2 report:

fraction of cells whose final policy state
matches the sign of their local regional environment;

boundary width;

global deadlock rate.

INTEGRATION QUALIFICATION

LOCAL_D2 or LOCAL_D3 is INTEGRATION-QUALIFIED iff all are true:

1. harmful-trajectory rate <= 0.05;

2. false C dominance <= 0.05 among S-FAVORING trials;

3. false S dominance <= 0.05 among C-FAVORING trials;

4. at least 90% of contradictory epochs
have no population majority;

5. oscillatory trial fraction <= 0.05;

6. median old-majority loss latency
on temporal reversals <= 3 epochs;

7. at least 80% of reversal trials
acquire the new majority by epoch 47;

8. aggregate service >= GLOBAL;

9. all integrity probes pass.

A32_INTEGRATION_INFORMATION_GAIN

TRUE iff at least one of LOCAL_D2 / LOCAL_D3:

has fewer false dominance outcomes than GLOBAL;

has lower oscillation than LOCAL_D0;

has a higher contradiction-unresolved fraction than GLOBAL;

and aggregate service >= LOCAL_D0.

This is descriptive only.

No production mechanism is selected.

INTEGRITY PROBES

P1:
exactly 384 trials.

P2:
48 contexts x 8 replicas.

P3:
48 persistent cells.

P4:
48 epochs.

P5:
initial C/S/U exactly 12/12/24.

P6:
base pulse only C / S / silent.

P7:
pool decay exactly 3/4.

P8:
pool recruitment thresholds exactly 20 / 8 / 2x / 6 emitters.

P9:
local inhibition radius exactly 12.

P10:
local Hill n exactly 3.

P11:
local Hill K exactly 1/2.

P12:
LOCAL_D0 has no refractory delay.

P13:
LOCAL_D2 delay exactly 2 complete epochs.

P14:
LOCAL_D3 delay exactly 3 complete epochs.

P15:
FC / FS cannot be recruited.

P16:
no local arm performs global all-cell retreat.

P17:
GLOBAL has no cell-local cross-inhibition.

P18:
same frozen worlds used by all arms.

P19:
no future environment enters current decisions.

P20:
no centralized confidence scalar exists.

P21:
two complete primary sweeps byte-identical.

NEGATIVE / LIMIT CONTROLS

N1:
GLOBAL A29-like pooled regime reference.

N2:
LOCAL_D0 local erosion without memory.

N3:
post-result selection of D2 vs D3 invalid.

N4:
changing A29 pool thresholds invalid.

N5:
changing A30 R/n/K invalid.

N6:
changing A31 duration invalid.

N7:
adding another mechanism invalid in A32.

INTERPRETATION

If D2/D3 improve the integrated organism,
A29-A31 compose successfully.

If local erosion helps but D2/D3 do not,
refractory memory does not transfer from the dedicated harness.

If D2/D3 reduce chatter but harm attractor quality,
local memory is stabilizing the wrong states.

If contradiction still persists under majority commitment,
the pool-to-recruitment architecture itself remains too global.

If spatial contradiction is resolved locally
without a global winner,
the system has begun representing heterogeneous truth
as heterogeneous population state.

PLAIN-SPEAK QUESTION

We have tested the pieces separately.

A29:
cells talk through shared signal pools.

A30:
cells can locally abandon a commitment
when nearby evidence turns against it.

A31:
a contradicted cell remembers briefly
and cannot jump straight back in.

A32 puts those pieces in one organism.

Cells still never calculate:

"confidence = 82%."

They pulse.

They listen locally.

They join one side only when the shared pool is convincing.

They leave locally when their neighborhood contradicts them.

And after leaving,
they remember the contradiction for two or three epochs
before becoming recruitable again.

The question is:

DO THE PARTS STILL WORK
WHEN THEY HAVE TO LIVE TOGETHER?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-IMPLEMENTATION CLARIFICATION 01 — RECRUITMENT AND LOCAL PULSE DENSITY

DATE:
2026-09-21.

STATUS:
BOUND BEFORE IMPLEMENTATION FREEZE
AND BEFORE ANY REAL F32-DERIVED WORLD EXISTS.

LOCAL POOL RECRUITMENT

When the frozen C recruitment condition is satisfied
in a local arm:

every currently eligible U cell becomes C
at that epoch.

When the frozen S recruitment condition is satisfied:

every currently eligible U cell becomes S.

FC and FS cells remain ineligible
until their exact refractory timer expires.

There is no additional recruitment probability.

This keeps the A29-style shared pool
as the recruitment trigger
while local cross-inhibition controls retreat.

LOCAL OPPOSING PULSE DENSITY

For local cross-inhibition,
a neighbor counts as an opposing emitter
if it emitted at least one pulse
for the opposing side in the current epoch.

A cell emitting both a base pulse
and a same-side positive-feedback pulse
still counts as one local emitter.

Thus local opposition density remains bounded:

0 <= L_op <= 1.

Pulse multiplicity continues to affect
the global decaying signal pools,
but not the A30-derived local Hill density.

No other A32 rule changes.

No F32 exists yet.
No scientific A32 world has been derived.


PRE-IMPLEMENTATION AMENDMENT 02 — POPULATION-SCALE NORMALIZATION

DATE:
2026-09-21.

STATUS:
BOUND BEFORE IMPLEMENTATION FREEZE
AND BEFORE ANY REAL F32-DERIVED WORLD EXISTS.

A developer-only mechanical run exposed a dimensional mismatch.

A29's pool recruitment constants:

COMMIT = 20;
OPPOSITION_CEILING = 8;
POP_GATE = 6;

were defined on a 12-cell organism.

A32 uses:

48 cells.

Literal reuse therefore quadruples the expected pulse supply
without scaling the thresholds.

In the developer-only run,
the opposition ceiling became effectively unreachable
under ordinary mixed signaling
and the GLOBAL reference remained unresolved almost all the time.

This is a population-size scaling defect,
not a scientific result.

A32 now preserves the A29 per-capita thresholds
by scaling all population-count / pooled-signal constants by:

48 / 12 = 4.

Therefore the frozen A32 values are:

COMMIT = 80.

OPPOSITION_CEILING = 32.

POP_GATE = 24 distinct emitters.

GLOBAL nonlinear-retreat half-saturation:

K_RETREAT = 48.

GLOBAL opposing-emitter minimum:

16.

The dimensionless dominance condition remains:

winning pool >= 2 * opposing pool.

The local A30/A31 cross-inhibition law is NOT scaled:

R = 12;
n = 3;
K = 1/2,

because it already operates on local density rather than raw population count.

No other A32 rule changes.

The original 20 / 8 / 6 values remain documented
as their 12-cell A29 source constants,
but are not the 48-cell A32 execution constants.

No F32 exists yet.
No scientific A32 world has been derived.


PRE-RUN IMPLEMENTATION FREEZE 01 — A32 INTEGRATED SIGNAL-POOL / LOCAL-INHIBITION / REFRACTORY CONTROLLER

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F32-DERIVED WORLD,
PULSE,
POOL STATE,
LOCAL DEFECTION,
REFRACTORY TRANSITION,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

ad9096361d51a66addbaebe713e8618502c06858.

SOURCE

research/applications/track-a/a32_t8p_integrated_signal_pool_local_inhibition_refractory_v1.py

Git blob:

d03d623af8c9c78c4360e6d8198e831574fb715d.

PACKAGING NOTE

The normal compressed/base64 source-bundle write
was blocked by an automated connector safety scan.

A32 therefore uses a plain UTF-8 Python source artifact.

This is a packaging change only.

The experiment semantics,
mechanical results,
and freeze discipline are unchanged.

PRE-FREEZE POPULATION-SCALE REPAIR

The first developer-only integration attempt
used literal A29 12-cell pool constants
inside the 48-cell A32 organism.

That made the opposition ceiling effectively unreachable.

Before freeze,
the pool constants were dimensionally normalized by 4:

COMMIT:
20 -> 80.

OPPOSITION_CEILING:
8 -> 32.

POP_GATE:
6 -> 24.

GLOBAL retreat K:
12 -> 48.

GLOBAL opposing-emitter minimum:
4 -> 16.

The local density-based A30/A31 law remained unchanged:

R = 12;
n = 3;
K = 1/2.

This repair occurred before F32
and before any scientific A32 world existed.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake seed:

MECHANICAL-F32-NONPRIMARY.

Two complete developer-only sweeps were byte-identical.

Serialized output SHA-256:

f75955a097ba914c44f9f51bfe5fdbea1e0e4c12268e066dbf832ec64f1b5f20.

All P1-P21 integrity probes:

PASS.

Mechanical manifest:

384 trials.

Manifest SHA-256:

64ba0c322cc08177d953f801e6c153c615e945ad6181744fe286345b1ceb18d2.

MECHANICAL GLOBAL

aggregate service:

+154555.

harmful trajectories:

103 / 384;
26.82%.

false dominance:

47 total.

contradictory epochs without majority:

56.29%.

oscillatory:

3 / 384;
0.78%.

reversal acquisition:

79.69%.

MECHANICAL LOCAL_D0

aggregate service:

+220712.

harmful:

68 / 384;
17.71%.

false dominance:

57.

contradictory epochs without majority:

55.52%.

oscillatory:

30 / 384;
7.81%.

chatter trials:

184 / 384;
47.92%.

reversal acquisition:

87.5%.

MECHANICAL LOCAL_D2

aggregate service:

+214083.

harmful:

65 / 384;
16.93%.

false dominance:

57.

contradictory epochs without majority:

55.89%.

oscillatory:

31 / 384;
8.07%.

chatter trials:

123 / 384;
32.03%.

reversal acquisition:

87.5%.

MECHANICAL LOCAL_D3

aggregate service:

+212301.

harmful:

64 / 384;
16.67%.

false dominance:

57.

contradictory epochs without majority:

56.05%.

oscillatory:

30 / 384;
7.81%.

chatter trials:

84 / 384;
21.88%.

reversal acquisition:

87.5%.

No arm mechanically qualified.

A32_INTEGRATION_INFORMATION_GAIN:

FALSE

in the fake world.

MECHANICAL INTERPRETATION

The dedicated A31 refractory effect
did transfer at the CELL level:

D2 / D3 reduced recommit-defect chatter substantially.

But it did not transfer at the POPULATION level:

D2 / D3 did not reduce majority-state oscillation
relative to LOCAL_D0.

The likely structural cause is frozen into A32:

when a pool recruitment condition fires,
all currently eligible U cells
join the same side together.

Thus cell-local memory can desynchronize
recently defected cells,
while the shared recruitment event
still synchronizes the rest of the unresolved population.

This is not repaired before the scientific run.

The real experiment will determine
whether that composition failure replicates
on fresh post-F32 worlds.

REAL A32 STATUS

No F32-derived scientific world exists.

No real A32 pulse has been observed.

No real A32 result exists.

Let the resulting commit SHA be:

F32.

After F32 exists:

1. derive exactly 384 fresh worlds from F32;
2. bind the complete world manifest SHA;
3. only then execute two complete primary sweeps;
4. require byte-identical output;
5. report GLOBAL / LOCAL_D0 / LOCAL_D2 / LOCAL_D3
without post-result tuning.

NO RECRUITMENT CHANGE.
NO POOL CHANGE.
NO LOCAL-INHIBITION CHANGE.
NO REFRACTORY-DURATION CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A32 INTEGRATED SIGNAL-POOL / LOCAL-INHIBITION / REFRACTORY CONTROLLER

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A32 CONTROLLER OUTCOME.

F32:

04c32ff5195fa295872a729e4203eab0bd69fba5.

TRIAL COUNT:

384.

STRUCTURE:

48 frozen environmental contexts
x
8 F32-derived replicas.

CELLS:

48.

EPOCHS:

48.

COMPLETE WORLD-MANIFEST SHA-256:

ac1c775d35efbe9471dfb9786f81ee646d368e3c75d022d401866ff3baaf92c6.

Serialized manifest-wrapper SHA-256:

46c2485e0d6f9c2c5594629f016b6d5d1aa74742868eb725c70dff62621ec97d.

Serialized manifest-wrapper bytes:

40003.

The manifest binds:

trial identity;
context family;
replica;
reversal epoch where applicable;
spatial region where applicable;
all 48 x 48 true local consequence values;
all 48 x 48 sensed local consequence values.

PRIMARY STATUS AT MANIFEST BIND

Real GLOBAL outcomes observed:

0.

Real LOCAL_D0 outcomes observed:

0.

Real LOCAL_D2 outcomes observed:

0.

Real LOCAL_D3 outcomes observed:

0.

The next permitted operation is:

two complete deterministic A32 primary sweeps
using F32 as the experimental seed.

NO WORLD REDRAW.
NO RECRUITMENT CHANGE.
NO POOL CHANGE.
NO LOCAL-INHIBITION CHANGE.
NO REFRACTORY CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-FREEZE AMENDMENT 03 — INTEGRITY PROBE SCALE CONSISTENCY

DATE:
2026-09-21.

STATUS:
BOUND BEFORE F32
AND BEFORE ANY REAL F32-DERIVED WORLD EXISTS.

The original preregistration text for integrity probe P8
still names the source A29 12-cell constants:

20 / 8 / 6.

PRE-IMPLEMENTATION AMENDMENT 02
already normalized those execution constants
for A32's 48-cell population.

Therefore P8 is superseded for A32 execution and reads:

P8:
pool recruitment thresholds exactly:

COMMIT = 80;
OPPOSITION_CEILING = 32;
POP_GATE = 24 emitters;

with the dimensionless 2x dominance condition unchanged.

This amendment changes no mechanism,
world generation,
metric,
qualification rule,
or scientific outcome.

No F32 exists yet.
No scientific A32 world has been derived.


PRE-RUN IMPLEMENTATION FREEZE 01 — A32 INTEGRATED SIGNAL-POOL / LOCAL-INHIBITION / REFRACTORY SYSTEM

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F32-DERIVED WORLD,
PULSE,
POOL STATE,
LOCAL DEFECTION,
REFRACTORY TRANSITION,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

ad9096361d51a66addbaebe713e8618502c06858.

SOURCE

research/applications/track-a/a32_t8p_integrated_signal_pool_local_inhibition_refractory_v1.py

Git blob:

d03d623af8c9c78c4360e6d8198e831574fb715d.

Source SHA-256:

ca346e8bd0866481c10fc3c0e6c92dcb9b685468e2f88244d98f634907028aa0.

Source bytes:

15967.

EXECUTION CONSTANTS

population:

48.

epochs:

48.

pool decay:

3 / 4.

COMMIT:

80.

OPPOSITION_CEILING:

32.

POP_GATE:

24.

dominance:

2x.

GLOBAL retreat K:

48.

GLOBAL opposing-emitter minimum:

16.

LOCAL inhibition:

R = 12;
n = 3;
K = 1/2.

Refractory durations:

D0 = 0;
D2 = 2;
D3 = 3.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake seed:

MECHANICAL-F32-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized output SHA-256:

f75955a097ba914c44f9f51bfe5fdbea1e0e4c12268e066dbf832ec64f1b5f20.

Serialized output bytes:

3451.

Mechanical manifest SHA-256:

64ba0c322cc08177d953f801e6c153c615e945ad6181744fe286345b1ceb18d2.

All P1-P21 integrity probes:

PASS.

MECHANICAL GLOBAL

aggregate service:

154555.

harmful trajectories:

103 / 384
=
26.82%.

false C dominance:

14.88%.

false S dominance:

10.38%.

contradiction no-majority fraction:

56.29%.

oscillation:

0.78%.

reversal acquisition:

79.69%.

MECHANICAL LOCAL_D0

aggregate service:

220712.

harmful:

68 / 384
=
17.71%.

chatter trials:

184 / 384
=
47.92%.

oscillation:

30 / 384
=
7.81%.

contradiction no-majority fraction:

55.52%.

reversal acquisition:

87.50%.

MECHANICAL LOCAL_D2

aggregate service:

214083.

harmful:

65 / 384
=
16.93%.

chatter trials:

123 / 384
=
32.03%.

oscillation:

31 / 384
=
8.07%.

contradiction no-majority fraction:

55.89%.

reversal acquisition:

87.50%.

MECHANICAL LOCAL_D3

aggregate service:

212301.

harmful:

64 / 384
=
16.67%.

chatter trials:

84 / 384
=
21.88%.

oscillation:

30 / 384
=
7.81%.

contradiction no-majority fraction:

56.05%.

reversal acquisition:

87.50%.

No integrated arm qualified.

A32_INTEGRATION_INFORMATION_GAIN:

FALSE

in the fake world.

MECHANICAL INTERPRETATION

The dedicated A31 refractory mechanism
still reduces per-cell recommit / defect chatter
after integration.

However:

GLOBAL POOL RECRUITMENT SYNCHRONIZES
ALL ELIGIBLE UNRESOLVED CELLS
ONTO THE SAME SIDE AT ONCE.

That synchronized re-entry can preserve
population-level majority oscillation
even while individual-cell chatter falls.

This is an important possible composability failure.

It is NOT repaired before the real test.

No recruitment probability,
pool threshold,
local inhibition rule,
or refractory duration
is changed in response.

This mechanical result is NON-SCIENTIFIC.

REAL A32 STATUS

No real F32-derived world exists.

No real integrated outcome has been observed.

Let the resulting commit SHA be:

F32.

After F32 exists:

1. derive exactly 384 fresh worlds from F32;
2. bind the complete world-manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. report GLOBAL / LOCAL_D0 / LOCAL_D2 / LOCAL_D3 without post-result selection.

NO POST-RESULT RECRUITMENT CHANGE.
NO POST-RESULT DURATION CHANGE.
NO POST-RESULT POOL CHANGE.
NO POST-RESULT LOCAL-INHIBITION CHANGE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A32 INTEGRATED SIGNAL ECOLOGY

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A32 ARM EXECUTION
OR SCIENTIFIC OUTCOME.

F32:

acf6050b5677efd715fb14abde70c93237c3d334.

FROZEN SOURCE SHA-256:

ca346e8bd0866481c10fc3c0e6c92dcb9b685468e2f88244d98f634907028aa0.

TRIAL COUNT:

384.

STRUCTURE:

48 frozen environmental contexts
x
8 F32-derived replicas.

CELLS:

48.

EPOCHS:

48.

COMPLETE WORLD-MANIFEST SHA-256:

2d51a59cff8dd43808ae9bb7d7f9d5281c5fe12540b91f367240190202b23300.

Serialized manifest-wrapper SHA-256:

14d7450a8d2d6a819cd3eb25abaed69c183031e8d7c36b25aa52ea806261c992.

Serialized manifest-wrapper bytes:

40016.

The bound world identity includes:

context;
replica;
family;
reversal location where applicable;
spatial region where applicable;
full 48 x 48 true local consequence field;
full 48 x 48 sensed field.

PRIMARY STATUS AT MANIFEST BIND

Real GLOBAL outcome observed:

0.

Real LOCAL_D0 outcome observed:

0.

Real LOCAL_D2 outcome observed:

0.

Real LOCAL_D3 outcome observed:

0.

The next permitted operation is:

two complete deterministic A32 primary sweeps
using F32 as seed.

NO WORLD REDRAW.
NO RECRUITMENT CHANGE.
NO POOL CHANGE.
NO LOCAL-INHIBITION CHANGE.
NO REFRACTORY CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
