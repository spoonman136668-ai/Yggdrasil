TITLE: YGGDRASIL A52 / T10D — Committed-Response Phase Offset Sweep
DATE: 2026-09-22
STATUS: PREREGISTERED RESPONSE-PHASE EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T10D / APPLICATION-A
CORE PARENT: A45 ECHO_PHASE
MACRO DONOR: frozen A49 CH_PUSH_PULL
RECOVERY / HANDOFF EVIDENCE: A48 / A50 / A51
BRANCH: dg1a-ar

WHY A52 EXISTS

A51 restored the measured
recovery-to-periphery timing handoff.

In hard 5:3 worlds:

D2 G5+push field exposure
rose from approximately 3%
under TTL0
to approximately 61-64%
under TTL2/TTL3.

D3 exposure
rose from approximately 2%
to approximately 51-62%.

Former-side recruitment
among G5-released cells
also increased materially.

TTL2 was the first
local temporal bridge
for both D families.

Yet no TTL arm
crossed the frozen macro-information gate.

Thus the remaining phenotype
is not explained by:

absence of core persistence;

absence of evidence-sensitive recovery;

absence of periphery influence;

or simple one-to-three-epoch
handoff mismatch.

The next justified question is broader:

does the committed core
respond at an unfavorable phase
relative to the periodic forcing?

A52 tests that question
without strengthening any signal.

TARGET FORCING

Hard target contexts:

46 and 47.

Their frozen environmental schedules are:

5:3;

and sign-inverted 3:5.

Both have period:

T_force = 8 epochs.

Secondary solved contexts:

44 and 45

are 6:2 / inverted 2:6
with the same period 8.

Therefore the preregistered
response delays:

0;
1;
2;
3;
4 epochs

correspond in the hard period-8 worlds to:

0;
1/8;
1/4;
3/8;
1/2 cycle.

No delay beyond 4.

No continuous delay.

No fitted phase.

No context-specific delay.

F52 FREEZE

Let the exact A52 implementation
freeze commit be:

F52.

No real A52 world,
phase-response result,
macro outcome,
or scientific conclusion
may be derived before F52 exists.

WORLD SHAPE

384 fresh post-F52 trials.

48 contexts x 8 replicas.

48 cells.

48 epochs.

Environmental families remain
structurally identical
to A45/A49/A51.

BASE ORGANISM

Use exact A45 ECHO_PHASE.

Preserve:

A36 ecology;

A40 signed temporal state;

A43 margin-weighted
cooperative reinforcement;

A44 local SUPPORT / CHALLENGE / NEUTRAL mode;

A44 support-gated active recruitment;

A45 one-epoch
non-recursive cooperative echo.

A52 does NOT use:

G5 recovery;

A51 TTL challenge memory;

new refractory timing;

new recruitment gains;

new radii.

Reason:

A52 isolates
committed-response phase.

MACRO FACTOR

A52 includes
the exact frozen A49
CH_PUSH_PULL
as an orthogonal factor.

P0:

A45 recruitment only.

P1:

A45 recruitment
plus frozen A49
current-CHALLENGE push-pull.

No TTL field memory.

No G5 recovery.

This tests whether
phase-shifted core persistence
needs the already-validated
challenge periphery mechanism
to convert persistence
into macro continuity.

DELAYED VARIABLE

A52 delays exactly one variable:

the PRESSURE value used
by the committed cell's
p_stay decision.

Everything required
to compute current A45 pressure
still updates in the current epoch.

For committed cell i
of side s at epoch t,
compute current:

L_op(t);

M_pre(t);

Q_raw(t);

Q_echo(t);

Q_eff(t);

local mode(t);

and therefore:

PRESSURE_now(t)

exactly as A45.

For CHALLENGE:

PRESSURE_now(t)
=
max(
0,
L_op(t)
-
M_pre(t)
-
Q_eff(t)
).

For SUPPORT / NEUTRAL:

PRESSURE_now(t)
=
max(
0,
L_op(t)
-
M_pre(t)
).

No equation changes.

PRESSURE HISTORY

Each cell carries
a side-specific FIFO history
for the current uninterrupted
commitment episode.

Stored record:

side;

PRESSURE_now;

source local mode;

source epoch.

The history:

begins empty
on a new commitment;

is retained only
while the cell remains
committed to the same side;

resets immediately on:

defection;

refractory state;

U;

H;

side change.

No history crosses
commitment episodes.

DECISION DELAY

For delay tau:

if the uninterrupted
same-side history contains
a pressure record
from exactly t - tau:

PRESSURE_decision(t)
=
PRESSURE_now(t - tau).

Otherwise:

PRESSURE_decision(t)
=
PRESSURE_now(t).

Thus the first tau epochs
of a new commitment episode
use ordinary current response.

There is no invented
pre-commitment history.

After choosing
PRESSURE_decision,
the current PRESSURE_now record
is stored for future epochs.

The p_stay law remains:

p_stay
=
1
/
(
1
+
(PRESSURE_decision / 0.5)^3
).

K = 0.5.

n = 3.

RANDOM DRAW TIMING

The stay/defect random draw
still occurs at current epoch t.

Use the exact inherited
stateless A45 action-random identity.

Only the probability input
is phase-shifted.

No action itself is queued.

No future event is read.

WHAT IS NOT DELAYED

A52 does NOT delay:

sensor input;

signed B update;

pool update;

local mode classification;

H release;

refractory processing;

A45 cooperative-Q trace update;

U recruitment;

A49 push-pull field;

environment state;

or random-number timing.

This is a committed-defection
response-phase experiment,
not a global simulation clock shift.

ARMS

Exactly twenty arms.

D2 P0:

D2_P0_TAU0;
D2_P0_TAU1;
D2_P0_TAU2;
D2_P0_TAU3;
D2_P0_TAU4.

D2 P1:

D2_P1_TAU0;
D2_P1_TAU1;
D2_P1_TAU2;
D2_P1_TAU3;
D2_P1_TAU4.

D3 P0:

D3_P0_TAU0;
D3_P0_TAU1;
D3_P0_TAU2;
D3_P0_TAU3;
D3_P0_TAU4.

D3 P1:

D3_P1_TAU0;
D3_P1_TAU1;
D3_P1_TAU2;
D3_P1_TAU3;
D3_P1_TAU4.

TAU0 P0
must reproduce exact A45 ECHO_PHASE.

TAU0 P1
must reproduce exact A49 CH_PUSH_PULL.

COMMON-RANDOM DESIGN

Within each D family,
all ten arms use
the same inherited
A45 ECHO_PHASE
stateless action-random identity.

A49 push-pull
is deterministic.

Delay is deterministic.

No sequential RNG cursor.

PRIMARY PHASE DIAGNOSTICS

For every committed-cell decision record:

current epoch;

side;

current local mode;

PRESSURE_now;

PRESSURE_decision;

source epoch
of decision pressure;

source age;

source local mode;

whether source
and current modes differ;

whether cell defects.

For each tau report:

fraction of decisions
using delayed pressure;

mean source age;

fraction of current CHALLENGE decisions
whose source mode was SUPPORT;

fraction of current CHALLENGE decisions
whose source mode was NEUTRAL;

fraction of current SUPPORT decisions
whose source mode was CHALLENGE.

These measure
actual phase displacement.

5:3 HIT-BY-HIT RESPONSE

At every 5:3 adverse burst
freeze the favored committed cohort
at burst onset.

For adverse hits 1,2,3 report:

cohort committed pre-fraction;

mean PRESSURE_now;

mean PRESSURE_decision;

source-mode composition;

defection fraction;

same-side neighbor count;

favored committed fraction
after the hit.

The central phase prediction is:

TAU2 / TAU3
should cause some hit-2 / hit-3
decisions to read
pre-challenge or earlier-challenge
pressure states.

TAU4 is a half-cycle
stress / anti-phase control.

No success is assumed
for any tau.

PERIODIC PHASE-ALIGNMENT METRICS

For contexts 44-47 report:

fraction of epochs
with a committed majority;

fraction of majority epochs
aligned with current
environmental base sign;

fraction anti-aligned;

fraction unresolved.

Report by context separately.

Also report
cross-correlation descriptively
between:

base_seq sign;

and favored-minus-adverse
committed fraction

for integer lags:

-4 through +4.

The lag maximizing
absolute correlation
is descriptive only.

It does not enter dynamics
or qualification.

MACRO METRICS

Preserve A49/A51:

5:3 burst-end
favored committed fraction;

favored-majority burst-end frequency;

favored-to-unresolved transitions;

unresolved-to-favored transitions;

mean / median unresolved duration;

mean / median
favored-majority recovery latency;

recovery-never count;

5:3 oscillator;

6:2 oscillator;

challenge-onset beta_F creep.

TRUE REVERSAL

Preserve all A45
true-reversal metrics.

Additionally report:

old-side pressure-history age distribution
during post-reversal epochs 0-4;

fraction of old-side decisions
using pre-reversal pressure;

old-side defection fraction
by post-reversal epoch;

time until no surviving old-side cell
uses pre-reversal pressure.

The delay mechanism
must wash out automatically
because commitment histories reset
on defection / state loss.

BALANCED SAFETY

For contexts 40-43 report:

false-majority;

majority residence;

C-majority epochs;

S-majority epochs;

unresolved occupancy;

chatter.

No delay arm
may exceed 10%
balanced false-majority.

PHASE INFORMATION GAIN

For tau > 0
within a fixed D and P condition,

A52_PHASE_INFORMATION_GAIN(tau)
is TRUE iff all:

1. 5:3 oscillator
   is at least 25 percentage points
   lower than paired TAU0

   OR

   favored-to-unresolved transitions
   are at least 25% lower
   than TAU0;

2. mean 5:3 burst-end
   favored committed fraction
   is at least 5 percentage points
   higher than TAU0;

3. direct favored-to-adverse flips = 0;

4. adverse-majority entries
   do not exceed TAU0;

5. 6:2 oscillator
   does not exceed TAU0;

6. balanced false-majority <=10%
   and does not exceed TAU0;

7. reversal acquisition >=80%;

8. median old-majority loss <=4 epochs;

9. aggregate service >=95%
   of paired TAU0;

10. median challenge-onset beta_F >=0;

11. all integrity probes pass.

PUSH-PHASE INTERACTION

For each tau,
compare the delay effect under:

P0;

and

P1.

For higher-is-better metric Y:

I_phase_push(Y,tau)
=
[
Y(P1,tau) - Y(P1,0)
]
-
[
Y(P0,tau) - Y(P0,0)
].

For lower-is-better metric D:

I_phase_push(D,tau)
=
[
D(P1,0) - D(P1,tau)
]
-
[
D(P0,0) - D(P0,tau)
].

A52_PHASE_PUSH_SYNERGY(tau)
is TRUE iff:

A52_PHASE_INFORMATION_GAIN
is TRUE for P1 at tau;

and at least one
preregistered macro interaction
is positive;

and P1 at tau
rescues at least one
paired 5:3 burst endpoint
that:

P0 TAU0 loses;

P1 TAU0 loses;

P0 tau loses;

but

P1 tau retains favored majority.

Report
phase-push-only rescues.

QUALIFICATION

A P1 delay arm
is A52-QUALIFIED iff all:

1. 5:3 oscillator <=10%;

2. overall oscillator <=5%;

3. mean 5:3 burst-end
   favored committed fraction >=50%;

4. at least 50%
   of 5:3 burst endpoints
   retain favored majority;

5. favored-to-unresolved transitions
   reduced >=50%
   versus P1 TAU0;

6. mean unresolved duration
   reduced >=25%
   versus P1 TAU0;

7. direct favored-to-adverse flips = 0;

8. adverse-majority entries = 0;

9. 6:2 oscillator = 0%;

10. balanced false-majority <=10%;

11. reversal acquisition >=80%;

12. median old-majority loss <=4 epochs;

13. aggregate service >=95%
    of P1 TAU0;

14. median challenge-onset beta_F >=0;

15. at least one
    phase-push-only rescue exists;

16. all integrity probes pass.

ANTI-PHASE FAILURE DIAGNOSTIC

TAU4 is explicitly retained
to expose half-cycle failure.

Report whether TAU4:

raises anti-aligned majority occupancy;

slows true reversal;

creates adverse-majority entries;

or lowers service.

Do not infer catastrophe
before execution.

If TAU4 is safe and useful,
report that result as observed.

MINIMUM EFFECTIVE PHASE OFFSET

If multiple tau values
satisfy A52 qualification,

the minimum effective phase offset
is the lowest tau.

If no tau qualifies:

A52_MINIMUM_EFFECTIVE_PHASE_FOUND = FALSE.

FAILURE ATTRIBUTION

If TAU2 / TAU3
materially shift decision-pressure source modes
but macro behavior barely changes:

the residual phenotype
is not primarily controlled
by committed-defection phase.

If phase delay improves P0
and P1 similarly:

response phase matters,
but A49 push-pull
is not specifically synergistic.

If P1 improves much more than P0:

phase-shifted core persistence
and challenge periphery control
interact.

If delay suppresses 5:3 oscillation
but creates anti-alignment
or reversal delay:

the phase manipulation
is dynamically effective
but unsafe.

If only TAU4 changes the phenotype:

the system requires
a large phase displacement,
and the mechanism class
must be reconsidered
rather than simply adopted.

If no tau
meaningfully changes macro behavior
despite verified phase displacement:

stop modifying
persistence,
recovery,
periphery strength,
and simple response delay.

The next research phase
must examine
higher-order developmental organization
or move into a task-bearing harness
to determine whether
the periodic benchmark
is over-constraining the architecture.

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
exact A45 ECHO_PHASE substrate.

P6:
P1 factor equals
exact A49 current CH_PUSH_PULL.

P7:
no G5.

P8:
no A51 TTL field memory.

P9:
tau set exactly
0,1,2,3,4.

P10:
only PRESSURE used by
committed p_stay is delayed.

P11:
PRESSURE_now equation unchanged.

P12:
p_stay equation unchanged.

P13:
current pressure is stored,
not delayed pressure.

P14:
history is side-specific.

P15:
history resets on defection.

P16:
history resets on refractory.

P17:
history resets on U.

P18:
history resets on H.

P19:
history resets on side change.

P20:
new commitment
has empty history.

P21:
warm-up uses current pressure.

P22:
no future pressure read.

P23:
no global phase read.

P24:
no context/family ID
enters delay dynamics.

P25:
environment sensing unchanged.

P26:
B update unchanged.

P27:
recruitment timing unchanged.

P28:
A49 field timing unchanged.

P29:
common inherited
stateless action random identity.

P30:
TAU0 P0
matches A45.

P31:
TAU0 P1
matches A49.

P32:
forcing delay disabled
makes all tau arms
reduce to their TAU0 donor.

P33:
two complete mechanical sweeps
byte-identical before F52.

P34:
F52 exists
before primary worlds.

P35:
post-F52 manifest bound
before primary execution.

P36:
two complete primary sweeps
byte-identical.

RESEARCH DISCIPLINE

Before F52:

focused A45 parity;

focused A49 parity;

forced-delay reduction;

trace-reset tests;

two complete mechanical sweeps
byte-identically.

No mechanical-world
phase or population outcome
may guide scientific interpretation.

F52 must exist
before fresh primary worlds.

No post-result:

delay value;

pressure equation;

gain;

radius;

recovery rule;

push-pull rule;

qualification threshold;

or arm addition.

PLAIN-SPEAK QUESTION

A51 proved
that the smaller timing handoff
was real.

We made the recovering cells
hear the veterans' recent message.

They listened.

But the whole organism
still kept falling into
the same hard-cycle pattern.

So A52 changes
a deeper piece of timing.

A committed cell
still senses the world now.

It still updates
its internal evidence now.

The population still recruits now.

But when the cell decides:

"do I abandon
my current commitment?"

we test whether that decision
should respond to pressure
from:

right now;

one turn ago;

two turns ago;

three turns ago;

or four turns ago.

The hard forcing cycle
is eight turns long.

So two turns
is a quarter-cycle shift.

Four turns
is half a cycle
and serves as
our anti-phase stress test.

Nothing gets louder.

Nothing gets a longer radius.

Nothing knows
the global phase.

We are asking one clean question:

IS THE CORE LOSING
BECAUSE IT RESPONDS
AT THE WRONG PHASE

RELATIVE TO
THE REPEATING PRESSURE?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F52 AMENDMENT 01 — IMPLEMENTATION / PARITY / MECHANICAL GATE

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F52
AND BEFORE ANY A52 SCIENTIFIC OUTCOME.

AUTHORIZED SOURCE

Bytes:
92868.

SHA256:
f1c2cfbd707621b18db101ea9a41f2264841acee10abcc5b80e4239c50ae60e1

ARMS

Exactly twenty arms.

For D2 and D3:

P0_TAU0..4;

P1_TAU0..4.

PARENT PARITY

Representative donor comparisons:

80.

Behavioral mismatches:

0.

TAU0 P0
reproduces exact
A45 ECHO_PHASE behavior
through the accepted A49 BASE donor.

TAU0 P1
reproduces exact
A49 CH_PUSH_PULL behavior.

FORCED-DELAY REDUCTION

For validation only,
disable delayed-pressure reads.

Then every tau > 0 arm
must reduce exactly
to its paired TAU0 donor.

Representative comparisons:

224.

Mismatches:

0.

This spans:

true reversal;

balanced periodic;

6:2 biased periodic;

5:3 biased periodic;

and nonperiodic families.

PRESSURE-HISTORY BOUNDARY

The implementation:

computes current A45 pressure
every epoch;

delays only the pressure value
consumed by p_stay;

stores current pressure,
never delayed pressure;

retains history only
through uninterrupted
same-side commitment;

uses current pressure
during warm-up;

resets history
on every loss
or change of commitment state;

reads no future value;

and preserves
the inherited stateless action draw
at the current epoch.

MECHANICAL VALIDATION

Mechanical seed:

MECHANICAL-A52-F52-CANDIDATE

Complete sweeps:

2.

Worlds per sweep:

384.

Arms:

20.

Output bytes per sweep:

301314.

Output SHA256:

50d9be5e85f1b157c2d26a2fad676dd67a5c2f52f07e9a07f8f0a4c381d53e0a

BYTE IDENTICAL:

true.

stderr:

empty for both sweeps.

All executable pre-primary
integrity probes:

PASS.

No mechanical-world
phase displacement,
oscillation,
burst-end,
reversal,
qualification,
synergy,
or population outcome
is used as scientific evidence.

LOCAL HARNESS NOTE

An unrelated duplicate local launcher
briefly reused an intermediate
mechanical filename.

That duplicate run was terminated
before evidence use.

The authoritative two passes
were preserved
under collision-safe immutable filenames
and are the byte-identical pair
reported above.

This is an execution-harness event,
not an experiment result.

SOURCE-BUNDLE FORMAT

The exact source above
will be published
as deterministic gzip/base64
split into seven neutral text source parts.

Source SHA256:

f1c2cfbd707621b18db101ea9a41f2264841acee10abcc5b80e4239c50ae60e1

Gzip bytes:

21350.

Gzip SHA256:

cbb20b48b21e6a6f7d2b47c5347ce4431d65c3202df0a8daa230472b805f2699

Concatenated base64 characters:

28468.

Base64 SHA256:

49dba6fdeed19093684c97a78e6690fdec2276229bcdd649f76e0554c16f2892

Source part count:

7.

The F52 loader must verify:

part count;
base64 identity;
gzip identity;
source identity;

before execution.

Any mismatch fails closed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-F52 PRIMARY MANIFEST BINDING

DATE:
2026-09-22.

F52:
e98f00e3feec76a7b8f08fd42cc60ce2d8bfe88d

AUTHORITATIVE SOURCE SHA256:
f1c2cfbd707621b18db101ea9a41f2264841acee10abcc5b80e4239c50ae60e1

PRIMARY SEED:
A52-F52-e98f00e3feec76a7b8f08fd42cc60ce2d8bfe88d-PRIMARY

WORLD COUNT:
384.

WORLD SHAPE:
48 contexts x 8 replicas.

PRIMARY WORLD MANIFEST SHA256:
1d2db1f6c74babaf25fd728d15a56e5a4fcac3427e416e70b6e111bb584021fd

STATUS:
BOUND AFTER F52
AND BEFORE ANY A52 PRIMARY ARM EXECUTION.

No A52 phase-displacement result,
oscillation result,
burst-end result,
phase-push interaction,
anti-phase result,
qualification result,
or scientific comparison
was observed before this binding.

Two complete primary sweeps
must be byte-identical
before scientific analysis.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


A52 PRIMARY CLOSURE

DATE:
2026-09-22.

F52:
e98f00e3feec76a7b8f08fd42cc60ce2d8bfe88d

MANIFEST-BINDING COMMIT:
e7d443c14f4b5ad752ce10cb0dacef4819d8f8a4

AUTHORITATIVE SOURCE SHA256:
f1c2cfbd707621b18db101ea9a41f2264841acee10abcc5b80e4239c50ae60e1

PRIMARY SEED:
A52-F52-e98f00e3feec76a7b8f08fd42cc60ce2d8bfe88d-PRIMARY

PRIMARY WORLD MANIFEST SHA256:
1d2db1f6c74babaf25fd728d15a56e5a4fcac3427e416e70b6e111bb584021fd

PRIMARY RUNS:
2.

PRIMARY OUTPUT BYTES:
301307.

PRIMARY OUTPUT SHA256:
08d49d7055f04f39bed34fb0b5ec3158b6a69af4199dfbc4bad0504ad511fb5b

BYTE IDENTICAL:
true.

stderr:
empty for both runs.

All executable integrity probes:
PASS.

SCIENTIFIC STATUS

A52_MINIMUM_EFFECTIVE_PHASE_FOUND:
FALSE.

A52 QUALIFICATION:
no arm qualifies.

A52_PHASE_INFORMATION_GAIN:
FALSE for every tau > 0
under both P0 and P1.

A52_PHASE_PUSH_SYNERGY:
FALSE for every tau.

However:

the phase intervention is
strongly behaviorally active.

A52 is therefore
not a null phase result.

D2 P1 CURRENT-PHASE CONTROL

TAU0:

5:3 oscillator:
100.00%.

overall oscillator:
7.29%.

mean 5:3 burst-end
favored committed fraction:
30.00%.

favored-majority burst-end frequency:
9.09%.

favored-to-unresolved transitions:
63.

mean unresolved duration:
3.667 epochs.

mean majority-recovery latency:
3.500 epochs.

reversal acquisition:
88.28%.

median old-majority loss:
3 epochs.

median challenge-onset beta_F:
+0.05045 per cycle.

aggregate service:
236695.

D2 P1 TAU1

5:3 oscillator:
100.00%.

overall oscillator:
7.55%.

burst-end favored fraction:
62.22%.

favored-majority burst-end frequency:
78.41%.

favored-to-unresolved:
56.

mean unresolved duration:
4.028 epochs.

mean recovery latency:
1.568 epochs.

reversal acquisition:
87.50%.

median old-majority loss:
4 epochs.

median beta_F:
+0.063.

aggregate service:
227289.

Thus TAU1
more than doubles
burst-end favored mass

and greatly increases
burst-end favored-majority residence,

yet does not reduce
the inherited 5:3 oscillator label.

D2 P1 TAU2

5:3 oscillator:
100.00%.

burst-end favored:
59.38%.

favored-majority frequency:
76.14%.

median old-majority loss:
5 epochs.

median beta_F:
+0.032.

TAU2 remains
strongly phase-displacing
but exceeds the frozen
true-reversal latency boundary.

D2 P1 TAU3

5:3 oscillator:
100.00%.

burst-end favored:
47.82%.

favored-majority:
44.32%.

median old-majority loss:
6 epochs.

D2 P1 TAU4

5:3 oscillator:
93.75%.

burst-end favored:
41.67%.

median old-majority loss:
7 epochs.

reversal acquisition:
81.25%.

TAU4 therefore
does not provide
a safe anti-phase solution.

D3 P1 CURRENT-PHASE CONTROL

TAU0:

5:3 oscillator:
100.00%.

overall oscillator:
6.51%.

mean 5:3 burst-end
favored fraction:
28.12%.

favored-majority burst-end frequency:
5.68%.

favored-to-unresolved:
65.

mean unresolved duration:
4.425 epochs.

mean recovery latency:
4.300 epochs.

reversal acquisition:
87.50%.

median old-majority loss:
3 epochs.

median beta_F:
+0.053.

aggregate service:
231801.

D3 P1 TAU1

5:3 oscillator:
100.00%.

burst-end favored fraction:
55.80%.

favored-majority frequency:
70.45%.

favored-to-unresolved:
60.

mean unresolved duration:
4.824 epochs.

mean recovery latency:
1.614 epochs.

reversal acquisition:
87.50%.

median old-majority loss:
4 epochs.

median beta_F:
+0.049.

Again:

one epoch of committed-response delay
substantially changes
the macro population state

without resolving
the inherited 5:3 oscillator label.

D3 P1 TAU2

5:3 oscillator:
93.75%.

burst-end favored:
51.42%.

favored-majority frequency:
54.55%.

median old-majority loss:
5 epochs.

median beta_F:
+0.015.

D3 P1 TAU3

5:3 oscillator:
81.25%.

overall oscillator:
5.73%.

burst-end favored:
44.41%.

favored-majority frequency:
36.36%.

favored-to-unresolved:
55.

mean unresolved duration:
7.190 epochs.

mean recovery latency:
4.934 epochs.

reversal acquisition:
81.25%.

median old-majority loss:
6 epochs.

median beta_F:
+0.001.

D3 P1 TAU4

5:3 oscillator:
93.75%.

burst-end favored:
39.87%.

median old-majority loss:
7 epochs.

reversal acquisition:
75.00%.

TAU4 fails
the reversal-acquisition boundary.

PUSH-FREE PHASE DISCRIMINATOR

The strongest oscillator suppression
appears without A49 push-pull.

D3 P0 TAU0:

5:3 oscillator:
100.00%.

overall oscillator:
5.99%.

burst-end favored:
23.67%.

median old-majority loss:
3 epochs.

D3 P0 TAU2:

5:3 oscillator:
75.00%.

burst-end favored:
45.83%.

median old-majority loss:
5 epochs.

median beta_F:
-0.010.

D3 P0 TAU3:

5:3 oscillator:
50.00%.

overall oscillator:
4.69%.

burst-end favored:
39.30%.

favored-to-unresolved transitions:
42.

median old-majority loss:
6 epochs.

reversal acquisition:
81.25%.

median beta_F:
-0.012.

Thus a three-epoch
committed-pressure delay
cuts the hard 5:3 oscillator
by 50 percentage points

and drives overall oscillator
below the frozen 5% target,

but does so while:

slowing true reversal;

lengthening unresolved episodes;

and introducing negative
cycle-to-cycle core creep.

This is a dynamically effective
but unsafe / metastable
phase manipulation.

PHASE-DISPLACEMENT VERIFICATION

The delay mechanism
was strongly active.

For tau > 0,
approximately 83-95%
of committed decisions
read delayed pressure.

Mean delayed source age
matches the requested tau.

At the third 5:3 adverse hit,
for example:

D3 P1 TAU0:

mean current pressure:
0.564.

mean decision pressure:
0.564.

defection fraction:
57.2%.

D3 P1 TAU1:

mean current pressure:
0.581.

mean decision pressure:
0.245.

defection fraction:
15.2%.

D3 P1 TAU2:

mean current pressure:
0.595.

mean decision pressure:
0.061.

defection fraction:
1.9%.

D3 P1 TAU3:

mean current pressure:
0.607.

mean decision pressure:
0.078.

defection fraction:
8.4%.

Therefore the delay
materially changes
committed-cell response phase.

The negative qualification result
cannot be attributed
to an inactive intervention.

TRUE-REVERSAL COST

The principal safety cost
is deterministic stale-pressure carryover
after a genuine reversal.

For tau = 1:

nearly 100%
of old-side decisions
at post-reversal epoch 0
use pressure computed
before the reversal.

For tau = 2:

the first two
post-reversal decision epochs
are almost entirely driven
by pre-reversal pressure.

For tau = 3:

the first three
post-reversal decision epochs
are almost entirely driven
by pre-reversal pressure.

For tau = 4:

the first four
post-reversal decision epochs
are almost entirely driven
by pre-reversal pressure.

Median old-majority loss
therefore rises nearly linearly:

TAU0:
3 epochs.

TAU1:
4 epochs.

TAU2:
5 epochs.

TAU3:
6 epochs.

TAU4:
7 epochs.

This is the dominant reason
larger fixed delays
fail the preregistered safety boundary.

ANTI-PHASE RESULT

TAU4 does not reveal
a hidden half-cycle solution.

It reduces reversal acquisition
to:

D2:
81.25%.

D3:
75.00%.

and pushes old-majority loss
to 7 epochs.

TAU4 therefore acts
as the intended anti-phase
failure stress test.

CAUSAL INTERPRETATION

A52 confirms
that committed-response phase
is a real causal axis.

The organism is not
insensitive to phase.

Changing only
the age of the pressure value
consumed by p_stay

can:

double burst-end favored mass;

greatly alter majority residence;

cut hard 5:3 oscillation
in some arms;

and move overall oscillator
below 5%.

Therefore the periodic benchmark
is not merely immune
to temporal reorganization.

But a fixed unconditional delay
is the wrong controller.

The same mechanism
that protects the core
from transient challenge

also forces cells
to keep using stale
pre-reversal pressure
after the environment
has genuinely changed.

The resulting tradeoff is:

more transient-challenge persistence

versus

slower genuine reversal
and eventual metastable creep.

A52 therefore does NOT justify:

larger tau;

tau > 4;

stronger push-pull;

stronger recovery;

larger spatial radius;

or post-result threshold relaxation.

It DOES justify
one final local phase-control question:

can delayed pressure
be used only while
the cell's CURRENT signed evidence
still supports its existing commitment,

and be discarded immediately
once current evidence
has crossed against that side?

That hypothesis targets
the measured safety failure:

stale phase information
surviving beyond
current evidence validity.

A post-closure observational diagnostic
should verify this seam
before any A53 implementation.

PLAIN-SPEAK INTERPRETATION

Phase matters.

A lot.

When we make a committed cell
react to pressure
from one or two turns ago,

the core can enter an attack
with roughly twice
as much favored population left standing.

At three turns of delay,
one D3 control even cuts
the hard oscillator in half.

So the organism really is
responding at a timing-sensitive point.

But fixed delay has a serious flaw.

When the world truly changes,
the cell keeps listening
to yesterday's pressure.

One turn of delay
costs roughly one extra turn
of old-side persistence.

Two turns cost two.

Three cost three.

Four cost four.

So we found
a real timing lever,

but the simple version
is too dumb.

It cannot tell the difference between:

"a temporary attack
I should ride through"

and

"the world genuinely changed
and I should let go."

That is now
the exact remaining stability question.

If current signed evidence
can act as the local veto
that cancels stale phase memory
when the commitment is no longer justified,

we may keep
the transient-challenge benefit
without paying
the true-reversal penalty.

If that final local veto
does not work,
we should stop refining
this periodic benchmark
and freeze the developmental substrate
for Task 1.

NORTH-STAR IMPLICATION

A52 strengthens
the realization case
despite failing qualification.

The architecture now demonstrates
that organism-level behavior
is controllable
through local response timing.

The remaining abstract-stability uncertainty
has narrowed to whether
phase memory can be locally invalidated
when current evidence
contradicts the old commitment.

This is a finite,
testable boundary.

A53 should be treated
as the last targeted
periodic-benchmark stabilization experiment
before developmental-substrate freeze
and Task 1.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
