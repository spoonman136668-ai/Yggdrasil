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
