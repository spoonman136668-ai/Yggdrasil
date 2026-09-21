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


PRE-RUN IMPLEMENTATION FREEZE 01 — A33 INDEPENDENT COMPETING-HAZARD RECRUITMENT

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F33-DERIVED WORLD,
HAZARD,
RECRUITMENT EVENT,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

7772b346b44cc583e70e24db60f9650fa71db903.

SOURCE BUNDLE

Loader:

research/applications/track-a/a33_t8q_independent_competing_hazard_recruitment_v1.py

Loader Git blob:

3197a1c9436628d8b46a3acff3e9df36e2366bf5.

Payload:

research/applications/track-a/a33_t8q_independent_competing_hazard_recruitment_v1.py.gz

Payload Git blob:

7c602605af82dd7a217505a9a0134db08ae1c392.

Decompressed source SHA-256:

d483897b88d2948e8c96f375e257702425b5d2ab32ec9599894a73967e03803e.

Decompressed source bytes:

22282.

Deterministic gzip SHA-256:

9be363718962dce8390046bb8a386e06a70e5ab3ad032eb1e6fafb4510373284.

Compressed payload bytes:

6101.

PRE-FREEZE IMPLEMENTATION REPAIRS

1. Recruitment-wave instrumentation.

The first developer-only pass grouped recruitment by joined side,
which made directional coordination trivially read 100%
and compressed apparent wave width.

The instrumentation was corrected before freeze.

A recruitment wave is now anchored to:

the pool-biased side at onset;

the exact U cells eligible at onset;

and ends only when the pool-biased side reverses
or the trial ends.

This changed measurement only.

It did NOT change:

hazards;
weights;
ETA;
local inhibition;
refractory duration;
or recruitment decisions.

2. Deterministic draw optimization.

The initial implementation performed a fresh SHA-256
for every cell-level stochastic draw.

This was replaced before freeze by:

one cryptographic seed per trial / arm;

then a frozen SplitMix64-style 64-bit mixer
for per-epoch / per-cell draws.

The statistical mechanism and identities remain deterministic.

No scientific rule changed.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake seed:

MECHANICAL-F33-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized output SHA-256:

610614f62838179d3338e603bd6d8e6541d5677231e2f3bff59816dd7caebd78.

Mechanical world-manifest SHA-256:

64b8885802b31850730e625f32616aa2287683ff42237164f8b062e390480853.

All P1-P23 integrity probes:

PASS.

SYNC_D2 mechanical reference:

oscillation:
7.55%.

harm:
19.01%.

recruitment width median:
0 epochs.

directional coordination:
1.0.

reversal acquisition:
87.5%.

SYNC_D3:

oscillation:
7.55%.

harm:
20.05%.

width:
0.

coordination:
1.0.

reversal acquisition:
87.5%.

D2_P75L25:

oscillation:
16.41%.

harm:
16.67%.

finite width median:
6 epochs.

width NEVER fraction:
86.11%.

directional coordination median:
71.20%.

D2_P50L50:

oscillation:
17.45%.

harm:
16.41%.

finite width median:
6 epochs.

width NEVER fraction:
86.23%.

directional coordination:
75.0%.

D2_P25L75:

oscillation:
16.67%.

harm:
16.67%.

finite width median:
6 epochs.

width NEVER fraction:
84.85%.

directional coordination:
81.82%.

D3_P75L25:

oscillation:
14.84%.

harm:
16.67%.

finite width median:
6 epochs.

directional coordination:
71.43%.

D3_P50L50:

oscillation:
15.89%.

harm:
16.41%.

finite width median:
7 epochs.

directional coordination:
75.30%.

D3_P25L75:

oscillation:
15.36%.

harm:
16.67%.

finite width median:
6 epochs.

directional coordination:
80.0%.

POOL-ONLY D2:

oscillation:
16.93%.

directional coordination:
66.67%.

LOCAL-ONLY D2:

oscillation:
17.97%.

directional coordination:
88.46%.

MECHANICAL PRIMARY RESULT

No primary Poisson arm qualified.

No primary Poisson arm met
A33_DISTRIBUTED_ACTUATION_INFORMATION_GAIN.

The synchronized FAMILY-5 oscillatory worlds
were not broken materially by Poisson recruitment
in the fake world.

The mechanical result therefore does NOT demonstrate
that independent clocks solve A32.

It demonstrates three separate effects:

1. independent hazards successfully spread recruitment in time;

2. increasing local weight improves directional coordination
under this mechanism;

3. temporal desynchronization alone can INCREASE
population-level oscillation.

This is an important falsifiable setup.

No ETA,
weight,
normalization,
qualification,
or refractory rule
is changed in response.

REAL A33 STATUS

No real F33-derived world exists.

No real hazard has been observed.

No real recruitment outcome has been observed.

No real A33 manifest exists.

Let the resulting commit SHA be:

F33.

After F33 exists:

1. derive exactly 384 fresh worlds from F33;
2. bind the complete world-manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. report synchronized references,
all six primary Poisson arms,
and both extreme controls.

NO POST-RESULT ETA TUNING.
NO POST-RESULT WEIGHT TUNING.
NO POST-RESULT NORMALIZATION TUNING.
NO POST-RESULT REFRACTORY CHANGE.
NO POST-RESULT LOCAL-INHIBITION CHANGE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A33 INDEPENDENT COMPETING-HAZARD RECRUITMENT

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A33 ARM EXECUTION
OR SCIENTIFIC OUTCOME.

F33:

3809ccb3af68310227607e4d8d6a63865d84564a.

FROZEN SOURCE SHA-256:

d483897b88d2948e8c96f375e257702425b5d2ab32ec9599894a73967e03803e.

TRIAL COUNT:

384.

STRUCTURE:

48 frozen environmental contexts
x
8 F33-derived replicas.

CELLS:

48.

EPOCHS:

48.

COMPLETE WORLD-MANIFEST SHA-256:

0b591e2604b944f84f2f46dd27e959235cf3e39f25fff84b24c556309aa7b918.

Serialized manifest-wrapper SHA-256:

d969f66df06e9656d365ef8ec033ff453a51887adfed2285b7a374b381ccc868.

Serialized manifest-wrapper bytes:

40002.

The bound identity includes:

context;
replica;
family;
reversal location where applicable;
spatial region where applicable;
full true local-consequence field hash;
full sensed field hash.

PRIMARY STATUS AT MANIFEST BIND

Real synchronized-reference outcomes observed:

0.

Real Poisson-hazard outcomes observed:

0.

Real recruitment-width outcomes observed:

0.

Real oscillation outcomes observed:

0.

The next permitted operation is:

two complete deterministic A33 primary sweeps
using F33 as seed.

NO WORLD REDRAW.
NO HAZARD CHANGE.
NO ETA CHANGE.
NO WEIGHT CHANGE.
NO REFRACTORY CHANGE.
NO LOCAL-INHIBITION CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-RUN CLOSURE — A33 / T8Q INDEPENDENT COMPETING-HAZARD RECRUITMENT

DATE:
2026-09-21.

STATUS:
CLOSED / REPRODUCIBLE NEGATIVE MECHANISM RESULT /
INDEPENDENT RECRUITMENT CLOCKS BROADENED ACTUATION IN TIME
BUT INCREASED POPULATION OSCILLATION /
NO PRIMARY ARM QUALIFIED /
NON-CANONICAL.

FROZEN IMPLEMENTATION

Implementation commit:

7772b346b44cc583e70e24db60f9650fa71db903.

F33:

3809ccb3af68310227607e4d8d6a63865d84564a.

Source SHA-256:

d483897b88d2948e8c96f375e257702425b5d2ab32ec9599894a73967e03803e.

BOUND PRIMARY MANIFEST

Manifest-bound commit:

86e3b25449266d03baac008354eb2216227d8807.

World-manifest SHA-256:

0b591e2604b944f84f2f46dd27e959235cf3e39f25fff84b24c556309aa7b918.

Manifest-wrapper SHA-256:

d969f66df06e9656d365ef8ec033ff453a51887adfed2285b7a374b381ccc868.

PRIMARY REPRODUCIBILITY

Two complete F33-derived primary sweeps were byte-identical.

Serialized semantic output SHA-256:

de72ca3e6abc41a9746ee0a45b76a14b57a039a1472fccd1fd9fcf49a3a5d6cb.

All P1-P23 integrity probes:

PASS.

PRIMARY RESULT

A33_ANY_POISSON_RECRUITMENT_QUALIFIED:

FALSE.

A33_DISTRIBUTED_ACTUATION_INFORMATION_GAIN:

FALSE.

SYNCHRONIZED REFERENCES

SYNC_D2:

aggregate service:
214054.

harmful:
69 / 384
=
17.97%.

false C dominance:
15.34%.

false S dominance:
13.04%.

oscillation:
33 / 384
=
8.59%.

recruitment width median:
0 epochs.

directional coordination:
100%.

reversal acquisition:
86.72%.

SYNC_D3:

aggregate service:
212057.

harmful:
70 / 384
=
18.23%.

oscillation:
33 / 384
=
8.59%.

width:
0.

coordination:
100%.

reversal acquisition:
86.72%.

PRIMARY POISSON ARMS

D2_P75L25:

aggregate service:
234990.

harmful:
65 / 384
=
16.93%.

oscillation:
67 / 384
=
17.45%.

finite recruitment-width median:
6 epochs.

width NEVER fraction:
86.68%.

directional coordination median:
70.0%.

reversal acquisition:
98.44%.

D2_P50L50:

aggregate service:
238824.

harmful:
62 / 384
=
16.15%.

oscillation:
64 / 384
=
16.67%.

finite width median:
6 epochs.

width NEVER:
86.36%.

directional coordination:
76.0%.

reversal acquisition:
100%.

D2_P25L75:

aggregate service:
242761.

harmful:
62 / 384
=
16.15%.

oscillation:
67 / 384
=
17.45%.

finite width median:
6 epochs.

width NEVER:
84.24%.

directional coordination:
82.76%.

reversal acquisition:
100%.

D3_P75L25:

aggregate service:
226023.

harmful:
62 / 384
=
16.15%.

oscillation:
56 / 384
=
14.58%.

finite width median:
6 epochs.

directional coordination:
71.43%.

reversal acquisition:
98.44%.

D3_P50L50:

aggregate service:
229342.

harmful:
62 / 384
=
16.15%.

oscillation:
60 / 384
=
15.63%.

finite width median:
6 epochs.

directional coordination:
76.92%.

reversal acquisition:
99.22%.

D3_P25L75:

aggregate service:
232739.

harmful:
64 / 384
=
16.67%.

oscillation:
58 / 384
=
15.10%.

finite width median:
6 epochs.

directional coordination:
81.82%.

reversal acquisition:
100%.

EXTREME CONTROLS

D2_POOL_ONLY:

aggregate service:
231183.

oscillation:
16.41%.

directional coordination:
66.67%.

D2_LOCAL_ONLY:

aggregate service:
247328.

oscillation:
17.97%.

directional coordination:
88.89%.

POOL / LOCAL TRADEOFF

The preregistered ratio sweep behaved directionally as expected in one respect.

As local weight increased:

directional coordination rose.

For D2:

70.0%
->
76.0%
->
82.76%.

For D3:

71.43%
->
76.92%
->
81.82%.

POOL_ONLY was lowest:

66.67%.

LOCAL_ONLY was highest:

88.89%.

Thus local evidence materially improves
which side individual cells choose.

However,
this did NOT translate into lower oscillation.

RECRUITMENT WIDTH RESULT

The synchronized references had:

median width = 0 epochs.

Primary Poisson arms had:

median finite width = 6 epochs.

Thus independent competing hazards
successfully removed the all-at-once recruitment step.

This directly validates the temporal-desynchronization mechanism.

But:

roughly 84-87% of recruitment waves
never recruited 90% of the onset-eligible cells
before pool bias reversed or the trial ended.

Therefore the Poisson system often produced:

progressive
but incomplete

recruitment waves.

OSCILLATION FAILURE

Every primary Poisson arm
oscillated MORE than its synchronized reference.

SYNC:

8.59%.

Primary Poisson range:

14.58%
to
17.45%.

The preregistered FAMILY-5 oscillatory worlds
were not broken.

Synchronized FAMILY-5 oscillatory set:

31 trials.

Broken by primary Poisson arms:

D2_P75L25:
0.

D2_P50L50:
0.

D2_P25L75:
0.

D3_P75L25:
2.

D3_P50L50:
0.

D3_P25L75:
1.

Thus timing decorrelation alone
did not attack the core transient / oscillatory family.

FAMILY-5 CHURN DIAGNOSTIC

Within FAMILY 5 only:

SYNC_D2:

oscillatory:
31 / 64.

median majority changes:
1.

mean majority changes:
3.89.

joins:
7943.

D2_P75L25:

oscillatory:
38 / 64.

median majority changes:
7.5.

mean:
5.39.

joins:
20163.

D2_P50L50:

oscillatory:
37 / 64.

median majority changes:
7.

joins:
19591.

D2_P25L75:

oscillatory:
40 / 64.

median majority changes:
9.

joins:
19081.

D3 arms reduced this churn somewhat
but remained worse than synchronization.

The distributed clocks therefore did not merely
spread one recruitment wave.

They enabled many more
continuous recruitment / defection cycles.

CELL-LEVEL CHURN

Across the full 384-world primary:

D2_P75L25:

53687 joins;
8173 chatter events.

D2_P50L50:

51937 joins;
7169 chatter events.

D2_P25L75:

50243 joins;
6053 chatter events.

D3_P75L25:

49416 joins;
4939 chatter events.

D3_P50L50:

48043 joins;
4095 chatter events.

D3_P25L75:

46753 joins;
3375 chatter events.

Increasing local weighting
and longer refractory memory
both reduce micro-level churn.

But not enough
to outperform synchronized population dynamics.

CONTRADICTION RESULT

High-high contradiction no-majority fraction:

SYNC references:
100%

under the A33 diagnostic threshold.

Primary Poisson arms:

D2:
78.41% to 80.49%.

D3:
85.64% to 85.90%.

So independent recruitment
made majority commitment MORE likely
during strongly contradictory pooled evidence.

This is the opposite of the desired uncertainty behavior.

ATTRACTOR QUALITY

False dominance also worsened.

SYNC_D2:

false C:
15.34%.

false S:
13.04%.

Poisson primary arms:

false C:
18.75% to 19.89%.

false S:
16.43% to 17.87%.

Thus the service gains
did not correspond to cleaner final attractor classification.

TECHNICAL INTERPRETATION

A33 falsifies the simple hypothesis:

SYNCHRONIZED ACTUATION
IS THE ONLY CAUSE
OF A32 POPULATION OSCILLATION.

Independent timing removed the stampede.

But it exposed a second actuation problem.

When evidence is contradictory:

lambda_C remains positive;

lambda_S remains positive.

Eligible cells therefore continue
joining both sides independently.

Local cross-inhibition then removes some of those cells.

Refractory memory delays re-entry.

When the timer expires,
both hazards may still be active.

The result is:

CONTINUOUS TWO-SIDED RECRUITMENT CHURN.

The synchronized rule had an accidental stabilizing feature:

it required strong directional dominance
before recruitment occurred.

That acted as a recruitment deadband.

A33 removed both:

synchronization

and

the deadband.

The first removal was desirable.

The second was not.

Therefore the next architectural requirement is:

DISTRIBUTED TIMING
+
CONTRADICTION-SENSITIVE HAZARD SUPPRESSION.

The clean next mechanism is NOT
to restore a global all-cell gate.

Instead,
each cell's recruitment hazard should collapse
when opposing evidence is simultaneously strong.

For example,
future preregistration could test a local or mixed form such as:

lambda_C
proportional to
candidate support
times
opposition suppression.

And symmetrically for S.

This would preserve:

independent clocks;
distributed actuation;
local evidence;

while creating a deadband
during unresolved contradiction.

That is a new experiment.

No such suppression is added post hoc to A33.

PLAIN-SPEAK INTERPRETATION

The independent clocks did exactly one thing
we wanted:

they stopped everybody from joining at once.

Recruitment stretched from:

basically zero epochs

to:

about six epochs.

But that did not calm the population.

It made the population busier.

Why?

Because when both sides had evidence,
both clocks kept running.

Some cells joined candidate.

Some joined stale.

Local opposition knocked cells back out.

Their short memory expired.

Then both clocks were still running.

So they joined again.

We removed:

"EVERYBODY GO NOW."

But replaced it with:

"EVERYBODY KEEP CONSIDERING BOTH SIDES ALL THE TIME."

That is better distributed.

It is not more stable.

The synchronized system had one useful property
we did not appreciate enough:

when evidence was contradictory,
it often refused to recruit anyone.

That quiet zone mattered.

So the next problem is now:

KEEP THE INDEPENDENT CLOCKS,

but teach each cell:

"if both sides are shouting strongly,
this is not a good time to join either side."

That would make uncertainty suppress action
without bringing back a central judge.

A29:
distributed sensing.

A30:
distributed retreat.

A31:
distributed memory.

A33:
distributed recruitment timing works mechanically,
but needs distributed contradiction suppression.

No autonomous controller is authorized.

DG-1R-05 remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
