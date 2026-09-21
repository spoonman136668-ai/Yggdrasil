TITLE: YGGDRASIL A30 / T8N — Spatial Local Cross-Inhibition and Commitment Erosion
DATE: 2026-09-21
STATUS: PREREGISTERED LOCAL-INHIBITION MECHANISM EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8N / APPLICATION-A
PARENT: A29 Distributed Competing Signal Pools
BRANCH: dg1a-ar

PURPOSE

A29 improved attractor quality using distributed competing signal pools,
but 23% of strongly contradictory epochs still occurred while the population remained committed.

The failure was localized:

opposition can become materially strong after commitment,
while a central retreat gate waits for a global pool threshold.

A30 replaces central committed-state retreat with local cross-inhibitory erosion.

Every committed cell responds immediately to opposing pulses in its neighborhood.

No global retreat decision is required for local defection.

A30 tests whether this:

reduces erosion latency under broad opposition;
preserves commitment under small opposition;
preserves spatial structure;
avoids oscillation;
and resists strategic local minorities.

SCIENTIFIC ATTRIBUTION

Honeybee stop signaling motivates cross-inhibition between competing populations.

The 2025 nonlinear-inhibition result in Communications Physics
supports testing nonlinear inhibitory response in collective decision systems.

A30's specific:

spatial ring;
local detection radius;
Hill persistence law;
and wound-propagation tests

are Yggdrasil experimental hypotheses,
not claims that those exact mechanisms were demonstrated in honeybees.

FROZEN PARENT

A29 closure:

84d4d7a04b79e769b73dd4a2469be973564d0dfd.

A29 result:

POOL_FULL false candidate commitment:
10 / 161 = 6.21%.

strongly contradictory epochs remaining unresolved:
77.02%.

Thus approximately 23% of high-C/high-S contradiction
persisted in committed states.

A30 FREEZE

Let the exact A30 implementation freeze commit be:

F30.

No real A30 spatial world,
local opposition measurement,
cell defection,
or scientific outcome
may be derived before F30 exists.

DEDICATED SPATIAL MECHANISM HARNESS

A30 is a dedicated local-cross-inhibition mechanism test.

It does not claim exact A29 trajectory replay.

Population size:

48 cells.

Topology:

one-dimensional periodic ring.

Cell identities:

0 through 47.

Initial committed candidate population:

36 / 48 cells.

Initial unresolved cells:

12 / 48 cells.

Initial unresolved identities are evenly spaced:

0,4,8,...,44.

This produces a 75% committed starting population
while preserving regular spatial structure.

TRIAL COUNT

After F30 derive exactly:

384 fresh trials:

48 frozen challenge contexts
x
8 F30-derived replicas.

Each trial contains:

40 epochs.

Challenge begins at:

epoch 8.

LOCAL OPPOSITION FIELD

At each epoch,
the frozen challenge determines which cells emit one opposing pulse.

A cell may emit:

0 or 1

opposing pulse per epoch.

Opposition is exogenous challenge evidence.

It is never generated from future controller outcome.

LOCAL DENSITY

For radius r,
cell i observes positions:

i-r ... i ... i+r

with periodic wraparound.

Neighborhood size:

2r + 1.

Local opposition density:

L_op(i,t) =
opposing emitters in neighborhood
/
neighborhood size.

LOCAL HILL PERSISTENCE

For a candidate-committed cell:

p_stay =
1
/
(1 + (L_op / K)^n).

Fixed half-saturation:

K = 1/2.

If L_op = 0:

p_stay = 1.

A deterministic F30-derived uniform draw
decides whether the committed cell remains committed.

Thus A30 is stochastic in mechanism
but exactly reproducible.

The stochastic draw namespace includes:

F30;
trial;
arm;
epoch;
cell;
STAY.

NO GLOBAL RETREAT GATE EXISTS
inside local-Hill arms.

RECRUITMENT / WOUND HEALING

An unresolved cell may be recruited back to candidate commitment.

Define local committed density:

L_C(i,t).

Fixed recruitment response:

p_join =
H_3(L_C; K_join=3/5)
*
(1 - L_op),

where:

H_3(x;K)
=
x^3
/
(K^3 + x^3).

A deterministic F30-derived draw
decides recruitment.

This recruitment rule is frozen for every arm.

It allows small wounds to heal
and larger wounds to propagate.

It is not tuned per radius or Hill coefficient.

LOCAL ARM MATRIX

Radius sweep:

R1 = 1;
R3 = 3;
R6 = 6;
R12 = 12.

Hill steepness sweep:

N1 = 1;
N3 = 3;
N5 = 5.

Exactly 12 primary local arms:

R1N1;
R1N3;
R1N5;

R3N1;
R3N3;
R3N5;

R6N1;
R6N3;
R6N5;

R12N1;
R12N3;
R12N5.

No arm is selected after observing data.

K remains 1/2 in every arm.

OVERSHARP NEGATIVE CONTROL

R3N12:

radius = 3;
Hill n = 12.

This tests whether an extremely sharp local response
behaves like a digital threshold
and increases oscillation / chatter.

It is a negative control,
not a candidate arm.

CENTRAL A29-LIKE RETREAT REFERENCE

CENTRAL:

committed cells do not locally defect.

A global opposition pool evolves as:

S_t =
3/4 * S_(t-1)
+
number of opposing emitters.

Central retreat occurs iff:

S_t >= 48

AND

current opposing emitters >= 16.

When central retreat fires:

all currently committed cells
become unresolved together.

Unresolved recruitment uses
the same fixed local recruitment rule
as local arms.

This isolates:

delayed global retreat

versus:

parallel local erosion.

NO-INHIBITION REFERENCE

NO_INHIB:

committed cells never defect due to opposition.

Recruitment remains available.

CHALLENGE FAMILIES

48 fixed challenge contexts.

FAMILY 0 — SMALL SUSTAINED CLUSTERS

8 contexts.

Cluster sizes:

1,2,3,4,5,6,7,8.

Contiguous opposition.

Active:

epochs 8-23.

Purpose:

small-opposition robustness
and early wound formation.

FAMILY 1 — LARGE SUSTAINED CLUSTERS

8 contexts.

Cluster sizes:

4,8,12,16,20,24,28,32.

Contiguous opposition.

Active:

epochs 8-23.

Purpose:

critical cluster size
and propagation threshold.

FAMILY 2 — DISPERSED SUSTAINED OPPOSITION

8 contexts.

Emitter counts:

4,8,12,16,20,24,28,32.

Emitters distributed as evenly around the ring as possible.

Active:

epochs 8-23.

Purpose:

broad distributed opposition
without one spatial wound.

FAMILY 3 — TRANSIENT BROAD OPPOSITION

8 contexts.

Emitter counts and durations are frozen pairs:

24x1;
24x2;
24x4;
32x1;
32x2;
32x4;
40x1;
40x2.

Starts at epoch 8.

Purpose:

test whether brief broad pulses
cause spurious erosion.

FAMILY 4 — OSCILLATORY OPPOSITION

8 contexts.

Exactly 24 evenly distributed emitters.

Alternating ON / OFF periods:

1/1;
2/2;
3/3;
4/4;

plus four phase-shifted repeats.

Active from epoch 8 through 31.

Purpose:

detect limit cycles and local chatter.

FAMILY 5 — STRATEGIC MINORITY

8 contexts.

Cluster sizes:

1,2,3,4,1,2,3,4.

Clusters are placed in one of two frozen geometries:

inside the densest initial committed run;

or adjacent to an initial unresolved boundary.

Active:

epochs 8-23.

Purpose:

measure vulnerability to
small but well-placed opposition.

PRIMARY STATE READOUT

Committed fraction:

F_C(t)
=
number of candidate-committed cells
/
48.

A population is:

majority committed iff F_C > 1/2.

majority unresolved iff F_C < 1/2.

The experiment does not create
a global regime variable for local arms.

The fraction is measurement only.

EROSION LATENCY

For challenge trials that reach:

opposition >= 50% of population

for at least two consecutive epochs,

erosion latency is:

first epoch after challenge onset
where F_C < 1/2

minus challenge onset.

If F_C never falls below 1/2:

latency = NEVER.

Compare every local arm with CENTRAL
on identical worlds.

SMALL-OPPOSITION ROBUSTNESS

For one-emitter sustained cluster contexts:

starting committed count:

36.

Robustness requires:

committed count never falls below 32

during challenge.

This permits at most four net defections
from the initial committed population.

CRITICAL CLUSTER SIZE

For every local arm,
using FAMILY 1 sustained contiguous clusters:

critical cluster size
=
smallest cluster size
whose median replica
drives F_C below 1/2
by epoch 16.

If no tested cluster does:

NONE.

WOUND HEALING / PROPAGATION

For every contiguous-cluster trial:

wound size at epoch t
=
largest contiguous run of unresolved cells.

Classify:

HEALS:
maximum wound after challenge onset
eventually returns to <= initial wound size + 2
by epoch 31.

PROPAGATES:
wound reaches >= 24 cells.

PERSISTS:
neither.

OSCILLATION CHECK

Define majority crossing
when F_C moves across 1/2.

A trial is oscillatory iff
it crosses 1/2 at least three times
from epoch 8 through 39.

Report oscillatory fraction
for every arm.

EROSION PROFILE

For every local arm,
bin observed L_op into exact rational bins:

0;
(0,1/4];
(1/4,1/2];
(1/2,3/4];
(3/4,1].

Report:

committed-cell exposure count;

defection count;

empirical defection rate.

This measures whether erosion is
progressive and Hill-shaped.

SPATIAL CORRELATION

For every local arm,
report the difference:

defection rate among cells
with L_op >= 1/2

minus

defection rate among cells
with L_op < 1/4.

Positive separation demonstrates
that erosion follows local opposition.

STRATEGIC-MINORITY METRIC

For FAMILY 5 report:

collapse count:
F_C < 1/2 at any point.

Also report:

maximum wound size;
final committed fraction.

This makes the strategic-minority vulnerability explicit.

PRIMARY QUALIFICATION

A local arm is LOCAL-INHIBITION-QUALIFIED iff all are true:

1. BROAD RESPONSE

For sustained >=50% opposition challenges,
median erosion latency <= 3 epochs.

2. CENTRAL IMPROVEMENT

Median erosion latency is
at least one epoch faster than CENTRAL
on matched broad-opposition trials.

3. SMALL-MINORITY ROBUSTNESS

At least 95% of one-emitter sustained trials
satisfy committed count >= 32
throughout challenge.

4. STRATEGIC-MINORITY CONTAINMENT

No more than 5% of FAMILY 5
one- or two-emitter minority trials
collapse below 50% commitment.

5. OSCILLATION

Oscillatory fraction <= 0.05.

6. SPATIAL SELECTIVITY

High-local-opposition defection rate
exceeds low-local-opposition defection rate
by at least 0.25.

7. CRITICAL CLUSTER

A finite critical cluster size exists
and is strictly greater than 1
and no greater than 24.

8. all integrity probes pass.

A30 does not select a production arm.

Every qualifying arm is reported.

Any later integration into A29
requires a new preregistered experiment.

A30_LOCAL_INFORMATION_GAIN

TRUE iff at least one primary local arm:

beats CENTRAL erosion latency;

passes small-minority robustness;

and has oscillatory fraction lower than R3N12.

This is descriptive only.

INTEGRITY PROBES

P1:
exactly 384 real trials.

P2:
48 contexts x 8 replicas.

P3:
48 cells on periodic ring.

P4:
initial committed count exactly 36.

P5:
initial unresolved count exactly 12.

P6:
local pulse per cell per epoch exactly 0 or 1.

P7:
K exactly 1/2 in all local arms.

P8:
primary n values exactly 1 / 3 / 5.

P9:
primary radii exactly 1 / 3 / 6 / 12.

P10:
oversharp control exactly R3N12.

P11:
no local arm reads global opposition count
to decide cell defection.

P12:
CENTRAL has no local opposition defection.

P13:
same recruitment law in every arm.

P14:
all stochastic decisions are deterministic
from F30 namespaces.

P15:
no future epoch enters current local decision.

P16:
local defection decisions are cell-parallel.

P17:
no global all-cell retreat occurs
inside local arms.

P18:
challenge geometry is frozen before outcomes.

P19:
two complete primary sweeps byte-identical.

P20:
no centralized confidence score exists.

NEGATIVE / LIMIT CONTROLS

N1:
CENTRAL global retreat.

N2:
NO_INHIB.

N3:
R3N12 oversharp local response.

N4:
post-result radius tuning invalid.

N5:
post-result Hill-n tuning invalid.

N6:
post-result K tuning invalid.

N7:
future challenge information invalid.

INTERPRETATION

If one or more moderate nonlinear local arms
beat CENTRAL latency
while preserving small-minority robustness,
A30 supports endogenous distributed erosion.

If N1 linear arms are too sensitive,
the noise-robustness argument is supported.

If N12 oscillates more,
oversharp local switching behaves too digitally.

If radius 12 converges toward CENTRAL-like behavior,
large neighborhoods erase the advantage of locality.

If radius 1 fragments without propagation,
the locality scale is too narrow.

If small strategic minorities collapse commitment,
local cross-inhibition creates a placement vulnerability
that must be solved before integration.

PLAIN-SPEAK QUESTION

A29 had a delay.

The population could already be strongly disagreeing,
but committed cells stayed committed
until one global opposition pool became large enough.

A30 removes that waiting room.

Every committed cell listens to its own neighborhood.

A little opposition nearby
should barely matter.

A lot of opposition nearby
should make that cell increasingly likely
to abandon commitment immediately.

Different cells can defect at different times.

So retreat becomes a spreading population process,
not one central switch.

We test:

how steep the local response should be;

how far a cell should listen;

how quickly broad opposition erodes commitment;

whether tiny opposition is ignored;

whether wounds heal or spread;

whether the population oscillates;

and whether a small strategically placed minority
can exploit locality.

A30 asks:

CAN COMMITMENT UNRAVEL LOCALLY
AS EVIDENCE CHANGES,
WITHOUT WAITING FOR A CENTRAL JUDGE?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-IMPLEMENTATION CLARIFICATION 01 — FIXED RECRUITMENT RADIUS

DATE:
2026-09-21.

STATUS:
BOUND BEFORE IMPLEMENTATION FREEZE
AND BEFORE ANY REAL F30-DERIVED WORLD EXISTS.

The preregistered recruitment law depends on local committed density
and local opposition density.

Its sensing neighborhood is now fixed explicitly:

R_join = 3.

This radius is used for recruitment in:

all 12 primary local-inhibition arms;
R3N12;
CENTRAL;
NO_INHIB.

The inhibition-radius sweep:

R1 / R3 / R6 / R12

changes only committed-cell opposition sensing.

It does NOT change recruitment sensing.

Therefore the experiment isolates:

cross-inhibition locality

rather than jointly changing:

cross-inhibition locality
and wound-healing locality.

No other A30 rule is changed.

No scientific A30 trajectory has been derived.

No F30 exists yet.


PRE-RUN IMPLEMENTATION FREEZE 01 — A30 SPATIAL LOCAL CROSS-INHIBITION

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F30-DERIVED SPATIAL WORLD,
LOCAL OPPOSITION EXPOSURE,
CELL DEFECTION,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

e969503bacfb520efe4f9ba2df7a7ccebfe88e76.

SOURCE BUNDLE

Loader:

research/applications/track-a/a30_t8n_spatial_local_cross_inhibition_v1.py

Loader Git blob:

219eecd273b9ce27f4599569d1cc4809c0fe5de8.

Payload:

research/applications/track-a/a30_t8n_spatial_local_cross_inhibition_v1.py.gz

Payload Git blob:

f7d3d5febacdde18879d1376cea2ed9e427cd303.

Decompressed source SHA-256:

7f560e87e54210f1d24826403ff040cab69dda9422d9d4920009df1e3388d7d4.

Decompressed source bytes:

11081.

Deterministic gzip SHA-256:

7f6ffa717a2a1647ceb7fe50c55239654af38f42c76a7b64d07da3ec67ccb9e0.

Compressed payload bytes:

3994.

IMPLEMENTATION NOTE

The first developer-only mechanical attempt used exact Fraction arithmetic
and a cryptographic hash for every cell-level random decision.

It exceeded the local execution window.

Before freeze,
the implementation was replaced with algebraically equivalent
integer probability thresholds
and a frozen xorshift64* deterministic PRNG
seeded from cryptographic trial / arm identity.

No scientific rule changed.

No real F30-derived world existed.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake seed:

MECHANICAL-F30-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized semantic output SHA-256:

ef796873e2d5904e6cb7f9ab5c98469084521568e3da378279a5f0f2402fed7e.

All P1-P20 integrity probes:

PASS.

CENTRAL mechanical reference:

broad-opposition median erosion latency:

1 epoch.

one-emitter sustained robustness:

100%.

strategic one/two-emitter collapse rate:

0%.

oscillatory fraction:

0%.

critical contiguous cluster size:

16 cells.

R3N12 oversharp control:

broad median erosion latency:

0 epochs.

oscillatory fraction:

17.45%.

critical cluster size:

24.

This establishes that very sharp local switching
can create substantially more chatter.

Exactly one primary arm met
all preregistered criteria
in the developer-only fake world:

R12N3.

R12N3 mechanical behavior:

broad median erosion latency:

0 epochs.

one-emitter robustness:

100%.

strategic one/two-emitter collapse:

0%.

oscillatory fraction:

4.95%.

critical cluster size:

20.

spatial defection-rate separation:

0.621.

No threshold,
radius,
Hill coefficient,
recruitment rule,
or qualification rule
is changed in response.

The full 12-arm matrix remains frozen.

This mechanical result is NON-SCIENTIFIC.

REAL A30 STATUS

No real F30-derived trial exists.

No real local inhibition outcome exists.

No real A30 manifest exists.

Let the resulting commit SHA be:

F30.

After F30 exists:

1. derive exactly 384 fresh trial identities from F30;
2. bind the complete challenge manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. report all 12 primary arms plus R3N12, CENTRAL, and NO_INHIB.

NO POST-RESULT RADIUS TUNING.
NO POST-RESULT HILL-N TUNING.
NO POST-RESULT K TUNING.
NO POST-RESULT RECRUITMENT CHANGE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A30 SPATIAL LOCAL CROSS-INHIBITION

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A30 CELL DEFECTION
OR SCIENTIFIC OUTCOME.

F30:

9516d67c71915d2bdf572142b59f662f614922ab.

FROZEN SOURCE SHA-256:

7f560e87e54210f1d24826403ff040cab69dda9422d9d4920009df1e3388d7d4.

TRIAL COUNT:

384.

STRUCTURE:

48 frozen challenge contexts
x
8 F30-derived replicas.

CELLS:

48.

EPOCHS:

40.

COMPLETE CHALLENGE-MANIFEST SHA-256:

c2897d96fe41998afcbe70f48b9018595d3bd36f3b33c79e342a65b67fb01681.

Serialized manifest-wrapper SHA-256:

c56baa3d1eb52919945407ff0e4a8776a9f000ebfa7ee07ef2a17b71e353f2f8.

Serialized manifest-wrapper bytes:

267977.

The manifest binds:

trial identity;

challenge family;

replica;

and the exact opposing-emitter identities
for all 40 epochs.

PRIMARY STATUS AT MANIFEST BIND

Real local defections observed:

0.

Real wound outcomes observed:

0.

Real oscillation outcomes observed:

0.

Real qualification outcomes observed:

0.

The next permitted operation is:

two complete deterministic A30 primary sweeps
using F30 as the experimental seed.

NO CHALLENGE REDRAW.
NO ARM CHANGE.
NO RADIUS CHANGE.
NO HILL-N CHANGE.
NO K CHANGE.
NO RECRUITMENT CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-RUN CLOSURE — A30 / T8N SPATIAL LOCAL CROSS-INHIBITION

DATE:
2026-09-21.

STATUS:
CLOSED / REPRODUCIBLE MIXED-POSITIVE MECHANISM RESULT /
LOCAL NONLINEAR CROSS-INHIBITION REDUCED BROAD-OPPOSITION RETREAT LATENCY
WHILE PRESERVING SMALL-MINORITY ROBUSTNESS,
BUT NO PRIMARY ARM MET THE FROZEN OSCILLATION CEILING /
NO ARM QUALIFIED /
NON-CANONICAL.

FROZEN IMPLEMENTATION

Implementation commit:

e969503bacfb520efe4f9ba2df7a7ccebfe88e76.

F30:

9516d67c71915d2bdf572142b59f662f614922ab.

Source SHA-256:

7f560e87e54210f1d24826403ff040cab69dda9422d9d4920009df1e3388d7d4.

BOUND PRIMARY MANIFEST

Manifest-bound commit:

de8e7f008bc84c763f0be6d1843046c5c16a8a9c.

Challenge-manifest SHA-256:

c2897d96fe41998afcbe70f48b9018595d3bd36f3b33c79e342a65b67fb01681.

PRIMARY REPRODUCIBILITY

Two complete F30-derived primary sweeps were byte-identical.

Serialized semantic output SHA-256:

06bb2a6da5dc77d2111106d4e13575862289283f1dd30dcd788cb1c377ba4a26.

All P1-P20 integrity probes:

PASS.

PRIMARY RESULT

A30_ANY_LOCAL_INHIBITION_QUALIFIED:

FALSE.

A30_LOCAL_INFORMATION_GAIN:

TRUE.

Five primary local arms met the descriptive information-gain condition:

R3N3;
R3N5;
R6N5;
R12N3;
R12N5.

They:

beat CENTRAL broad-opposition erosion latency;

preserved one-emitter robustness;

and oscillated less than the oversharp R3N12 control.

CENTRAL REFERENCE

Broad-opposition median erosion latency:

1 epoch.

Broad trials never eroding below 50%:

0 / 48.

One-emitter sustained robustness:

100%.

Strategic one/two-emitter collapse rate:

0%.

Oscillatory fraction:

0%.

Critical contiguous cluster size:

16 cells.

NO_INHIB REFERENCE

Broad opposition never drove commitment below 50%.

This confirms that the observed erosion
comes from inhibition rather than recruitment alone.

LOCAL LATENCY

Several moderate nonlinear local arms
crossed below 50% commitment in the same epoch
that broad opposition appeared:

R3N5:
median latency 0.

R6N5:
median latency 0.

R12N3:
median latency 0.

R12N5:
median latency 0.

R3N3:

median latency 0.5 epochs.

Thus local parallel erosion
removed approximately one epoch
of central-pool waiting
in this dedicated mechanism harness.

This does not numerically reproduce
A29's 23% contradictory-committed fraction.

It demonstrates the proposed mechanism
for eliminating central waiting latency.

SMALL-OPPOSITION ROBUSTNESS

Every primary arm preserved:

100%

of one-emitter sustained trials
above the frozen robustness floor.

Every primary arm also had:

0%

collapse rate
for the preregistered strategic
one- and two-emitter minority subset.

Thus A30 did not expose
a catastrophic strategic-minority vulnerability
at the tested 48-cell scale.

CRITICAL CLUSTER SIZE

Observed critical contiguous cluster sizes included:

R1N1:
24.

R3N1:
20.

R3N3:
24.

R3N5:
24.

R6N1:
16.

R6N3:
20.

R6N5:
24.

R12N1:
12.

R12N3:
16.

R12N5:
20.

Thus locality materially changed
the spatial wound-propagation boundary.

Large sensing radius plus low Hill steepness
allowed smaller opposing clusters
to produce population collapse.

EROSION PROFILE

The empirical defection profile was strongly local-density dependent.

R3N3:

low opposition bin <= 1/4:
2.40% defection.

(1/4,1/2]:
26.34%.

(1/2,3/4]:
63.39%.

(3/4,1]:
85.76%.

R3N5:

low opposition bin <= 1/4:
0.23%.

(1/4,1/2]:
17.97%.

(1/2,3/4]:
69.43%.

(3/4,1]:
95.08%.

Thus n=3 to n=5 produced
the intended ultrasensitive erosion:

small local opposition has very little effect;

high local opposition produces rapid defection.

OVERSHARP CONTROL

R3N12:

low opposition:
0%.

mid-low:
8.09%.

mid-high:
85.52%.

highest opposition:
100%.

Oscillatory fraction:

17.71%.

This supports the preregistered concern
that an extremely sharp local response
behaves like a digital switch
and produces substantially more population chatter.

OSCILLATION FAILURE

No primary arm satisfied
all frozen qualification criteria.

The closest arm was:

R12N3.

R12N3:

broad median latency:
0.

one-emitter robustness:
100%.

strategic one/two-emitter collapse:
0%.

critical cluster:
16.

spatial defection-rate separation:
0.6143.

oscillatory fraction:
5.2083%.

Frozen oscillation ceiling:

5%.

Thus R12N3 failed qualification
by the oscillation criterion.

The 5% ceiling is NOT moved.

R12N5:

oscillation:
5.73%.

R6N5:

6.51%.

R3N3:

7.81%.

R3N5:

8.07%.

The latency improvement is therefore real,
but immediate local erosion plus re-recruitment
can create majority-boundary chatter.

SPATIAL WOUND RESULT

Local arms produced distinct
heal / persist / propagate mixtures.

Examples:

R1N5:

HEALS = 252;
PERSISTS = 59;
PROPAGATES = 73.

R12N3:

HEALS = 210;
PERSISTS = 10;
PROPAGATES = 164.

CENTRAL:

HEALS = 208;
PERSISTS = 0;
PROPAGATES = 176.

This confirms that locality produces
spatially structured wound behavior
rather than merely approximating
one global retreat gate.

TECHNICAL INTERPRETATION

A30 supports the central mechanism hypothesis:

LOCAL CROSS-INHIBITION
CAN BEGIN ERODING COMMITMENT
BEFORE A GLOBAL OPPOSITION POOL
FINISHES ACCUMULATING.

The effect is:

parallel;
cell-local;
spatially selective;
and nonlinear.

The experiment also supports
the user's predicted steepness tradeoff.

Linear / shallow response:

is slower
and more sensitive across moderate opposition.

Moderate n=3 / n=5:

suppresses low-density opposition strongly
while rapidly eroding high-density opposition.

Oversharp n=12:

approaches digital local switching
and markedly increases oscillation.

The unresolved failure is now:

LOCAL RETREAT IS FAST ENOUGH,
BUT RE-RECRUITMENT IS NOT HYSTERETIC ENOUGH.

After local defection,
cells can be recruited back
while the spatial conflict is still unresolved.

That produces repeated crossings
of the population majority boundary.

This suggests a clean next mechanism:

PER-CELL HYSTERESIS / REFRACTORY MEMORY.

A defected cell should not immediately
be eligible for recommitment
under the same threshold that governs erosion.

A later experiment can test
a short local refractory state
or asymmetric local re-entry threshold
while leaving the successful A30
cross-inhibition law unchanged.

That would directly test
whether local hysteresis removes chatter
without restoring central control.

PLAIN-SPEAK INTERPRETATION

The basic A30 idea worked.

When half the population
started sending opposition,
local cells reacted immediately.

Several local designs
dropped below majority commitment
in the same epoch opposition arrived.

The central controller needed another epoch.

Tiny opposition was ignored.

Even strategically placed
one- and two-cell minorities
did not collapse the population.

And the response really was nonlinear.

With a moderate Hill curve,
small opposition barely caused defection,
while dense opposition caused most nearby cells to defect.

But we hit the next problem.

The cells can change their minds too quickly
in both directions.

They defect locally.

Then recruitment pulls some of them back.

Then opposition pushes them out again.

The oversharp version made this especially obvious.

So A30 says:

LOCAL EROSION WORKS.

The missing piece is:

LOCAL MEMORY AFTER EROSION.

A cell that has just been forced out of commitment
probably needs a short refractory / uncertain period,
or a harder threshold for recommitment,
before it can be pulled straight back in.

That is a local hysteresis problem,
not a confidence-score problem.

No autonomous controller is authorized.

DG-1R-05 remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
