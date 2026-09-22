TITLE: YGGDRASIL A51 / T10C — One-Epoch Challenge-Field Echo Bridge
DATE: 2026-09-22
STATUS: PREREGISTERED TEMPORAL-COMPOSITION EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T10C / APPLICATION-A
BASE SUBSTRATE: A45 ECHO_PHASE
RECOVERY DONOR: frozen G5_FULL from F47/A48
MACRO DONOR: frozen A49 CH_PUSH_PULL from F49
COMPOSITION PARENT: A50
BRANCH: dg1a-ar

WHY A51 EXISTS

A50 tested direct same-epoch composition
of two independently validated layers:

G5 recovery;

and

A49 challenge push-pull.

Both remained locally active.

The combined arms improved several
macro quantities modestly,
but did not satisfy
A50 composition information gain
or layer synergy.

The direct handoff was rare.

Among G5-released cells:

D2 nonzero same-side challenge-field exposure
was approximately 3.1%.

D3 exposure
was approximately 2.3%.

The frozen mechanisms are phase-selective
in opposite directions.

G5 fires only when
the former side is locally SUPPORT.

A49 CH_PUSH_PULL is generated only by
surviving veterans
whose local mode is CHALLENGE.

Therefore:

the recovery layer
makes cells available
mainly after local challenge has ended;

the macro field
is strongest while challenge is still active.

A51 asks whether
one epoch of strictly local,
non-recursive challenge-field continuity

is enough to bridge those
otherwise valid mechanisms in time.

F51 FREEZE

Let the exact A51 implementation
freeze commit be:

F51.

No real A51 world,
population outcome,
field-overlap result,
macro result,
or scientific conclusion
may be derived before F51 exists.

WORLD SHAPE

384 fresh post-F51 trials.

48 contexts x 8 replicas.

48 cells.

48 epochs.

Environmental families remain
structurally identical
to A45/A48/A49/A50.

BASE ORGANISM

Preserve exact A45 ECHO_PHASE.

No refractory retuning.

No recruitment gain retuning.

No A37 lineage state.

FROZEN G5

Use exact F47/A48 G5_FULL:

for refractory FC / FS cell i
relative to former side s,

G5 TRUE iff:

local mode relative to s = SUPPORT;

M_post(i,s) > 0;

Q_raw(i,s) > 0.

If true:

state_i := U;

timer_i := 0;

same epoch.

No direct recommitment.

No side bonus.

No new threshold.

No new probability.

FROZEN CURRENT CHALLENGE FIELD

Preserve exact A49 CH_PUSH_PULL.

After committed-state decisions,
freeze surviving committed cells.

For an eligible U target i:

Q_C_ch_now(i)

=
radius-3 mean of surviving C cells
whose current C-relative mode = CHALLENGE.

Q_S_ch_now defined analogously.

ETA = 1/2.

Current push-pull:

lambda_C'
=
(lambda_C_parent + ETA * Q_C_ch_now)
*
(1 - Q_S_ch_now).

lambda_S'
=
(lambda_S_parent + ETA * Q_S_ch_now)
*
(1 - Q_C_ch_now).

lambda_H unchanged.

ONE-EPOCH CHALLENGE TRACE

Each cell j carries:

CH_prev_side(j)

with possible values:

NONE;
C;
S.

Initial state:

NONE.

At the recruitment-stage field snapshot
for epoch t,
a surviving committed C cell contributes
echo challenge occupancy iff:

CH_prev_side(j) = C.

A surviving committed S cell contributes
echo occupancy iff:

CH_prev_side(j) = S.

If the cell is no longer committed
to that same side,
the stored challenge trace
cannot contribute.

ECHO FIELD

For eligible U cell i:

Q_C_ch_echo(i)

=
radius-3 mean of surviving C cells
for which:

current C-relative mode = CHALLENGE

OR

CH_prev_side = C.

Q_S_ch_echo defined analogously.

A neighbor contributes at most 1.

Current challenge
and prior challenge
are UNIONED,
not added.

Therefore there is:

no double strength;

no gain;

no decay coefficient;

no recursive accumulation.

TRACE UPDATE

After the current epoch's recruitment stage:

if cell j survives committed to C
and its CURRENT local C-relative mode
was CHALLENGE:

CH_prev_side_next(j) = C.

If it survives committed to S
and current S-relative mode was CHALLENGE:

CH_prev_side_next(j) = S.

Otherwise:

CH_prev_side_next(j) = NONE.

Critically:

an echo-active cell
that is no longer currently challenged
does NOT refresh the trace.

Thus the echo lasts
exactly one subsequent epoch.

It cannot remember
the memory of the memory.

It resets on:

defection;

U;

H;

refractory state;

side change;

or any committed epoch
that is not currently CHALLENGE.

ECHO PUSH-PULL

For the echo-field arms:

lambda_C'
=
(lambda_C_parent + ETA * Q_C_ch_echo)
*
(1 - Q_S_ch_echo).

lambda_S'
=
(lambda_S_parent + ETA * Q_S_ch_echo)
*
(1 - Q_C_ch_echo).

lambda_H unchanged.

No other dynamics change.

ARMS

Exactly twelve arms.

D2:

D2_BASE;
D2_G5;
D2_PUSH_PULL_NOW;
D2_G5_PUSH_PULL_NOW;
D2_PUSH_PULL_ECHO1;
D2_G5_PUSH_PULL_ECHO1.

D3:

D3_BASE;
D3_G5;
D3_PUSH_PULL_NOW;
D3_G5_PUSH_PULL_NOW;
D3_PUSH_PULL_ECHO1;
D3_G5_PUSH_PULL_ECHO1.

CURRENT controls reproduce A50.

ECHO1 arms differ only
by one-epoch local challenge trace.

COMMON-RANDOM DESIGN

Within each D family,
all six arms share
the exact inherited
A45 ECHO_PHASE
stateless action-random identity.

G5 deterministic.

Current push-pull deterministic.

Echo push-pull deterministic.

No sequential RNG cursor.

PRIMARY TARGET

Hard 5:3 contexts:

46 and 47.

Secondary non-regression:

6:2 contexts 44 and 45.

Balanced control:

40 through 43.

True reversal:

all inherited reversal families.

PRIMARY TEMPORAL-HANDOFF METRIC

For every G5 release
in 5:3 worlds record:

release epoch;

former side;

Q_favored_ch_now;

Q_favored_ch_echo;

whether now-field is nonzero;

whether echo-field is nonzero;

whether same-epoch recruitment occurs;

joined side.

For G5_PUSH_PULL_NOW
and
G5_PUSH_PULL_ECHO1
report:

fraction of G5 releases
with nonzero favored challenge field;

same-epoch favored recruitment rate;

same-epoch adverse recruitment rate;

same-epoch H recruitment rate;

same-epoch remaining-U rate.

TEMPORAL BRIDGE INFORMATION GAIN

For a D family,
A51_TEMPORAL_BRIDGE_INFORMATION_GAIN = TRUE iff
G5_PUSH_PULL_ECHO1 satisfies all:

1. nonzero favored challenge-field exposure
   among G5-released cells
   is at least 10 percentage points
   higher than G5_PUSH_PULL_NOW;

2. same-epoch favored recruitment rate
   among G5-released cells
   is at least 3 percentage points
   higher than G5_PUSH_PULL_NOW;

3. direct favored-to-adverse flips = 0;

4. adverse-majority entries
   do not exceed BASE;

5. 6:2 oscillator
   does not exceed BASE;

6. balanced false-majority <=10%
   and does not exceed BASE;

7. reversal acquisition >=80%;

8. aggregate service >=95% of BASE;

9. all integrity probes pass.

MACRO METRICS

Preserve A49/A50:

burst-end favored committed fraction;

favored-majority burst-end frequency;

favored-to-unresolved transitions;

unresolved-to-favored transitions;

mean unresolved episode duration;

mean favored-majority recovery latency;

recovery-never count;

refractory fraction;

challenge-onset beta_F creep.

A51 MACRO INFORMATION GAIN

For a D family,
A51_MACRO_INFORMATION_GAIN = TRUE iff
G5_PUSH_PULL_ECHO1 satisfies all:

1. A51_TEMPORAL_BRIDGE_INFORMATION_GAIN = TRUE;

2. mean 5:3 burst-end favored fraction
   exceeds G5_PUSH_PULL_NOW
   by at least 2 percentage points;

3. favored-to-unresolved transitions
   are at least 10% lower
   than G5_PUSH_PULL_NOW

   OR

   mean unresolved duration
   is at least 10% lower
   than G5_PUSH_PULL_NOW;

4. median challenge-onset beta_F >=0;

5. all safety / non-regression criteria pass.

ECHO-SPECIFICITY CONTROL

Compare:

PUSH_PULL_ECHO1
versus
PUSH_PULL_NOW

without G5.

If echo alone
produces the entire macro gain,
then A51 is a field-persistence result,
not a recovery-field bridge result.

A51_LAYER_TIMING_SYNERGY = TRUE iff:

G5_PUSH_PULL_ECHO1
improves burst-end favored fraction
over G5_PUSH_PULL_NOW
by more than
the improvement of
PUSH_PULL_ECHO1
over PUSH_PULL_NOW;

and

A51_TEMPORAL_BRIDGE_INFORMATION_GAIN = TRUE;

and

at least one G5-released-cell
favored recruitment
is attributable to echo-only field exposure
in a paired 5:3 endpoint
where the NOW field was zero.

QUALIFICATION

D2_G5_PUSH_PULL_ECHO1
or
D3_G5_PUSH_PULL_ECHO1

is A51-QUALIFIED iff all are true:

1. A51_TEMPORAL_BRIDGE_INFORMATION_GAIN = TRUE;

2. A51_MACRO_INFORMATION_GAIN = TRUE;

3. mean 5:3 burst-end favored fraction >=35%;

4. favored-majority burst-end frequency
   is at least 20 percentage points
   above BASE;

5. direct favored-to-adverse flips = 0;

6. adverse-majority entries = 0;

7. 6:2 oscillator = 0%;

8. balanced false-majority <=10%;

9. reversal acquisition >=80%;

10. median old-majority loss <=4 epochs;

11. aggregate service >=95% of BASE;

12. median challenge-onset beta_F >=0;

13. all trace freshness probes pass;

14. all integrity probes pass.

TRACE FRESHNESS PROBES

Verify every epoch:

noncommitted cells
cannot contribute challenge echo;

a side-changed cell
cannot inherit opposite-side challenge echo;

an echo-only contribution
does not refresh itself;

a current CHALLENGE committed cell
sets exactly one next-epoch trace;

a current SUPPORT or NEUTRAL cell
sets no next-epoch trace;

a trace contributes for at most
one subsequent epoch.

FAILURE ATTRIBUTION

If echo-field exposure
among G5 releases rises strongly
but favored recruitment does not:

field timing overlap is improved,
but field direction/amplitude
does not control the released reservoir.

If favored recruitment rises
but macro continuity does not:

temporal handoff is real
but still too small
to explain the remaining macro phenotype.

If echo alone
and G5+echo improve equally:

one-epoch challenge-field persistence
is useful,
but not specifically because of recovery composition.

If G5+echo improves
more than echo alone:

the recovery and periphery layers
have a genuine temporal interaction.

If echo creates
balanced false-majority,
6:2 regression,
or slower true reversal:

one epoch of challenge-field persistence
is already too sticky.

If overlap remains low
despite the echo:

the mismatch exceeds
one local epoch
and the broader response-phase /
forcing-alignment hypothesis
becomes the next justified class.

If overlap rises
and both local layers are active
but the macro phenotype remains forcing-locked:

do not strengthen
recovery or push-pull.

Proceed to a preregistered
response-phase experiment
with explicit delay-buffer semantics.

CREEP GUARD

Preserve A49/A50
challenge-onset core-creep diagnostic.

No apparent stabilization
may qualify
with median beta_F < 0.

PHASE-OFFSET BOUNDARY

A51 is NOT
the broader phase-offset experiment.

It changes only
how long a locally observed
CHALLENGE state
remains available
to the periphery field.

It does not delay:

B update;

committed-state decision;

defection;

environment sensing;

or recruitment scheduling.

If A51 fails
after demonstrably increasing
cross-layer temporal overlap,
then a true response-delay
experiment becomes justified.

PLAIN-SPEAK QUESTION

A50 showed us
that recovery and push-pull
are mostly working
on different shifts.

The recovery rule
lets cells off the bench
when their old side
is supported again.

But the push-pull organizer
is only active
while the veterans
are still under attack.

By the time
the benched cells return,
that challenge signal
has usually disappeared.

A51 gives the challenged core
one beat of memory.

If a veteran
was under challenge
last epoch
and is still committed now,

its challenge field
can influence the nearby periphery
for one more epoch.

Then the memory disappears.

It cannot refresh itself.

It cannot accumulate.

There is no central clock.

The question is:

IS ONE LOCAL BEAT
OF CHALLENGE MEMORY

ENOUGH FOR
RECOVERING CELLS
AND ORGANIZING VETERANS

TO FINALLY ARRIVE
ON THE SAME SHIFT?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F51 AMENDMENT 01 — MEASURED HANDOFF-LAG TTL SWEEP

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F51
AND BEFORE ANY A51 SCIENTIFIC OUTCOME.

SUPERSESSION

The original one-epoch-only A51 design
was preregistered before
the post-A50 handoff-lag diagnostic
was completed.

That diagnostic is now bound at:

ca5ef4c465289e8f5272c4d1848f855bfa0b0338.

No F51 exists.

No A51 scientific outcome
has been observed.

Therefore the one-epoch-only design
is superseded before freeze
by this measured TTL sweep.

MEASURED LAG

In exact frozen A50 5:3 worlds:

D2 G5_PUSH_PULL releases:

n = 1029.

Current same-side challenge field nonzero:

0.00%.

Current same-side committed-core occupancy nonzero:

100.00%.

Last nonzero same-side challenge field:

lag 1:
0.00%.

lag 2:
97.18%.

lag 3:
2.82%.

within 3:
100.00%.

D3 favored-former-side releases:

n = 1576.

Current same-side challenge field nonzero:

0.00%.

Current same-side committed-core occupancy nonzero:

99.87%.

Last nonzero same-side challenge field:

lag 1:
0.00%.

lag 2:
70.88%.

lag 3:
21.64%.

lag >=4:
7.36%.

NEVER:
0.13%.

within 3:
92.51%.

Thus a one-epoch bridge
is predicted to miss
almost the entire measured target seam.

The spatial core remains present.

The missing quantity
is recent CHALLENGE-mode field state.

A51 QUESTION

What is the minimum
strictly local,
non-recursive
challenge-field memory duration

that restores temporal overlap
between:

recovered G5-released cells

and

the same-side challenge organization
that existed shortly before release,

without creating stale-side bias,
balanced capture,
or reversal rigidity?

TTL ARMS

Freeze four field-memory durations:

TTL0 = current A50 behavior.

TTL1 = one subsequent epoch.

TTL2 = two subsequent epochs.

TTL3 = three subsequent epochs.

TTL is measured
from the most recent epoch
in which the veteran
was currently CHALLENGE
for its committed side.

No duration beyond 3
is permitted in A51.

No continuous decay.

No fitted duration.

No context-specific duration.

TRACE STATE

Each cell j carries:

CH_trace_side(j)

in:

NONE;
C;
S.

and:

CH_trace_age(j)

as a nonnegative integer
or NONE.

Initial state:

CH_trace_side = NONE.

CH_trace_age = NONE.

CURRENT CHALLENGE

At the frozen A49
post-defection challenge-field snapshot:

if a surviving committed C cell
has current C-relative mode CHALLENGE:

CH_trace_side_next = C;

CH_trace_age_next = 0.

Analogously for S.

NON-CHALLENGE SURVIVAL

If a cell remains committed
to the same side
but is not currently CHALLENGE:

an existing same-side trace
may age by one epoch.

The trace does not refresh.

The stored trace side
remains unchanged.

If age exceeds
the arm's TTL,
it becomes inactive.

RESET

Trace resets immediately on:

defection;

refractory state;

U;

H;

side change;

loss of commitment.

A trace cannot cross sides.

FIELD CONTRIBUTION

For TTLk arm,
a surviving committed cell
contributes to the challenge field iff:

it is currently CHALLENGE

OR

it has a same-side trace
with:

1 <= age <= k.

A neighbor contributes
at most one occupancy unit.

Current challenge
and remembered challenge
are UNIONED,
not added.

Therefore:

no amplitude accumulation;

no recursive strengthening;

no gain;

no decay coefficient.

TTL0 reproduces
the exact A50 NOW field.

PUSH-PULL EQUATIONS

Preserve exact A49/A50
challenge occupancy push-pull.

For eligible U target i:

Q_C_ch_TTLk

=
radius-3 mean
of surviving committed C neighbors
that satisfy
the TTLk field-contribution rule.

Q_S analogously.

Then:

lambda_C'
=
(
lambda_C_parent
+
ETA * Q_C_ch_TTLk
)
*
(
1 - Q_S_ch_TTLk
).

lambda_S'
=
(
lambda_S_parent
+
ETA * Q_S_ch_TTLk
)
*
(
1 - Q_C_ch_TTLk
).

ETA = 1/2.

lambda_H unchanged.

No new gain.

No new radius.

No field threshold.

FROZEN G5

Preserve exact repaired
F47/A48/A50 G5_FULL.

No G5 gate,
timing,
or action changes.

ARMS

Exactly twenty arms.

D2:

D2_BASE;
D2_G5;

D2_PUSH_TTL0;
D2_G5_PUSH_TTL0;

D2_PUSH_TTL1;
D2_G5_PUSH_TTL1;

D2_PUSH_TTL2;
D2_G5_PUSH_TTL2;

D2_PUSH_TTL3;
D2_G5_PUSH_TTL3.

D3:

D3_BASE;
D3_G5;

D3_PUSH_TTL0;
D3_G5_PUSH_TTL0;

D3_PUSH_TTL1;
D3_G5_PUSH_TTL1;

D3_PUSH_TTL2;
D3_G5_PUSH_TTL2;

D3_PUSH_TTL3;
D3_G5_PUSH_TTL3.

TTL0 controls reproduce A50.

The PUSH-only TTL arms
measure field persistence
without recovery composition.

The G5+PUSH TTL arms
measure the cross-layer handoff.

COMMON-RANDOM DESIGN

Within each D family,
all ten arms use
the exact inherited
A45 ECHO_PHASE
stateless action-random identity
for all inherited stochastic events.

G5 deterministic.

TTL field deterministic.

No sequential RNG cursor.

PRIMARY TARGET

5:3 contexts:

46 and 47.

Secondary:

6:2 contexts 44 and 45.

Balanced:

40 through 43.

True reversal:

all inherited reversal families.

PRIMARY HANDOFF METRIC

For every G5 release
in 5:3 worlds report:

TTL arm;

release epoch;

former side;

current same-side challenge field;

remembered same-side challenge field;

effective same-side TTL field;

trace age distribution;

whether exposure is:

CURRENT;

TTL1-only;

TTL2-only;

TTL3-only;

or NONE;

same-epoch recruitment;

joined side.

For each G5+PUSH TTL arm report:

fraction of G5 releases
with nonzero same-side
effective challenge field;

same-epoch favored recruitment;

same-epoch adverse recruitment;

H recruitment;

remaining U.

MEASURED-COVERAGE EXPECTATION

This is descriptive,
not a qualification threshold.

The pre-A51 lag diagnostic predicts:

TTL1:
little target coverage.

TTL2:
approximately 97% potential D2 coverage
and approximately 71% potential D3 coverage
if relevant veterans remain committed.

TTL3:
up to 100% D2
and approximately 92.5% D3
potential coverage.

Actual A51 exposure
may be lower
because veteran survival,
side continuity,
and radius geometry
remain enforced.

TEMPORAL BRIDGE INFORMATION GAIN

For TTL k > 0
within each D family,
TEMPORAL_BRIDGE_INFORMATION_GAIN(k)
is TRUE iff G5_PUSH_TTLk satisfies all:

1. nonzero same-side
   field exposure among G5 releases
   is at least 20 percentage points
   higher than G5_PUSH_TTL0;

2. same-epoch favored recruitment rate
   among G5 releases
   is at least 3 percentage points
   higher than G5_PUSH_TTL0;

3. adverse recruitment rate
   among G5 releases
   does not increase
   versus G5_PUSH_TTL0;

4. direct favored-to-adverse flips = 0;

5. adverse-majority entries
   do not exceed BASE;

6. 6:2 oscillator
   does not exceed BASE;

7. balanced false-majority <=10%
   and does not exceed BASE;

8. reversal acquisition >=80%;

9. aggregate service >=95% of BASE;

10. all trace freshness
    and integrity probes pass.

MACRO INFORMATION GAIN

For TTL k > 0,
A51_MACRO_INFORMATION_GAIN(k)
is TRUE iff:

1. TEMPORAL_BRIDGE_INFORMATION_GAIN(k) = TRUE;

2. mean 5:3 burst-end
   favored committed fraction
   exceeds G5_PUSH_TTL0
   by at least 2 percentage points;

3. favored-to-unresolved transitions
   are at least 10% lower
   than G5_PUSH_TTL0

   OR

   mean unresolved duration
   is at least 10% lower
   than G5_PUSH_TTL0;

4. median challenge-onset beta_F >=0;

5. all safety/non-regression
   criteria pass.

LAYER-TIMING SPECIFICITY

For each TTL k > 0,
compute the macro improvement:

Delta_combined(k)
=
G5_PUSH_TTLk
-
G5_PUSH_TTL0.

Compute field-only improvement:

Delta_push(k)
=
PUSH_TTLk
-
PUSH_TTL0.

For higher-is-better metrics,
timing interaction is positive iff:

Delta_combined(k)
>
Delta_push(k).

For lower-is-better metrics,
timing interaction is positive iff
the combined reduction
exceeds the PUSH-only reduction.

A51_LAYER_TIMING_SYNERGY(k) = TRUE iff:

TEMPORAL_BRIDGE_INFORMATION_GAIN(k) = TRUE;

at least one preregistered
macro timing interaction is positive;

and

at least one G5-released cell
is recruited favored
under TTL-only field exposure
where its TTL0 field was zero.

MINIMUM EFFECTIVE TTL

The minimum effective TTL
is the lowest k in:

1;
2;
3

that satisfies:

TEMPORAL_BRIDGE_INFORMATION_GAIN(k);

A51_MACRO_INFORMATION_GAIN(k);

A51_LAYER_TIMING_SYNERGY(k);

and all safety/non-regression criteria.

If no k qualifies:

A51_MINIMUM_EFFECTIVE_TTL_FOUND = FALSE.

Do not extend TTL beyond 3
post-result.

QUALIFICATION

A G5_PUSH_TTLk arm
is A51-QUALIFIED iff:

1. k is the minimum effective TTL;

2. mean 5:3 burst-end
   favored fraction >=35%;

3. favored-majority
   burst-end frequency
   is at least 20 percentage points
   above BASE;

4. direct favored-to-adverse flips = 0;

5. adverse-majority entries = 0;

6. 6:2 oscillator = 0%;

7. balanced false-majority <=10%;

8. reversal acquisition >=80%;

9. median old-majority loss <=4 epochs;

10. aggregate service >=95% of BASE;

11. median challenge-onset beta_F >=0;

12. old-side remembered-field
    recruitment after true reversal
    passes the safety boundary below;

13. all trace freshness
    and integrity probes pass.

TRUE-REVERSAL MEMORY SAFETY

For the first four epochs
after true reversal,
relative to the OLD side,
report:

U opportunities
with old-side TTL field >0;

old-side recruitment events
whose transformed probability
was increased by TTL memory;

old-side adverse-majority entries;

old-majority loss latency.

For A51 safety:

TTL memory must not create
any old-side majority entry
that is absent in TTL0.

And median old-majority loss
must remain <=4 epochs.

BALANCED MEMORY SAFETY

For contexts 40-43 report:

fraction of U opportunities
with TTL-only field;

C-majority epochs;

S-majority epochs;

false-majority;

majority residence;

chatter.

No TTL arm may exceed
10% balanced false-majority.

TRACE FRESHNESS PROBES

Verify:

current challenge sets age 0;

age increments only
for uninterrupted same-side commitment;

remembered field
does not refresh itself;

defection resets trace;

refractory resets trace;

U resets trace;

H resets trace;

side change resets trace;

age never decreases
except reset/current challenge;

TTL0 exactly reproduces A50 current field;

TTL1 contribution requires age 1;

TTL2 requires age <=2;

TTL3 requires age <=3;

no contribution after arm TTL;

no trace enters
G5 eligibility;

no trace enters
committed-state persistence.

FAILURE ATTRIBUTION

If TTL1 has little exposure
and TTL2 sharply increases exposure:

the measured two-epoch handoff lag
is causally confirmed.

If TTL2 covers D2 strongly
but D3 requires TTL3:

the fixed refractory duration
creates a real D-specific
handoff timescale.

If exposure rises
but favored recruitment does not:

the expired challenge field
was not the effective missing signal.

If favored recruitment rises
but macro continuity does not:

the handoff exists,
but recruitable turnover
still cannot explain
the macro phenotype.

If PUSH-only TTL
improves as much as
G5+PUSH TTL:

the mechanism is
challenge-field persistence,
not cross-layer recovery synergy.

If G5+PUSH improves
more than PUSH-only:

recovery and periphery control
have a genuine temporal handoff.

If TTL3 is required
but creates reversal/balanced cost:

the local bridge window
is too long for safe static memory.

Do not extend it further.

If TTL2/TTL3
restore high cross-layer overlap
and local favored recruitment
but macro continuity remains weak:

the next justified class
is broader response-phase /
forcing alignment.

No stronger recovery,
push-pull gain,
or radius change
is justified by that outcome.

CREEP GUARD

Preserve A49/A50
challenge-onset beta_F.

No TTL arm qualifies
with median beta_F < 0.

RESEARCH DISCIPLINE

Before F51:

BASE must equal
A50 BASE / A45 ECHO_PHASE.

G5 must equal
A50 G5.

PUSH_TTL0 must equal
A50 PUSH_PULL.

G5_PUSH_TTL0 must equal
A50 COMBINED.

When all trace state
is forced empty,
every TTL arm
must reduce to its TTL0 donor.

Run two complete
mechanical sweeps
byte-identically.

F51 must exist
before fresh primary worlds.

Bind post-F51 manifest
before primary arm execution.

Run two complete primaries
byte-identically.

No post-result:

TTL extension;

gain;

decay;

radius;

G5 retuning;

field-strength tuning;

arm addition;

or qualification change.

PLAIN-SPEAK UPDATE

A51 was originally going to give
the challenge signal
one extra beat of memory.

The measurement says
that would almost certainly
be too short.

The recovered cells
usually come back
two or three beats
after the challenge signal.

So we will not guess.

We test:

no memory;

one beat;

two beats;

three beats.

The message never gets louder.

It never copies itself.

It simply remains locally available
for a bounded number of turns
while the same veteran
is still committed.

Then we ask:

what is the shortest memory
that actually lets
the returning cells
hear the organizers' recent message?

And does that temporal handoff
change the whole population

without making the organism
cling to an obsolete side
after the world truly changes?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F51 AMENDMENT 01 — IMPLEMENTATION / PARITY / MECHANICAL GATE

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F51
AND BEFORE ANY A51 SCIENTIFIC OUTCOME.

AUTHORIZED SOURCE

Bytes:
91080.

SHA256:
5d649564b50889b9a2241088b0c6b983b1dbf6c86731b66ad5cb7f3436b99867

ARMS

Exactly twelve arms.

D2:

D2_BASE;
D2_G5;
D2_PUSH_PULL_NOW;
D2_G5_PUSH_PULL_NOW;
D2_PUSH_PULL_ECHO1;
D2_G5_PUSH_PULL_ECHO1.

D3:

D3_BASE;
D3_G5;
D3_PUSH_PULL_NOW;
D3_G5_PUSH_PULL_NOW;
D3_PUSH_PULL_ECHO1;
D3_G5_PUSH_PULL_ECHO1.

PARENT PARITY

A51 current-field controls
reproduce A50 behavior exactly.

Representative comparisons:

96.

Behavioral mismatches:

0.

A51 appends
now-field / echo-field
observational diagnostics
to G5 action records.

Those diagnostic-only fields
are excluded from
the behavioral parity comparator.

FORCED-ECHO REDUCTION

For validation only,
force the A51 echo field
to equal the current A49 field.

Then:

PUSH_PULL_ECHO1
must reduce exactly to
PUSH_PULL_NOW;

G5_PUSH_PULL_ECHO1
must reduce exactly to
G5_PUSH_PULL_NOW.

Representative comparisons:

48.

Mismatches:

0.

TRACE FRESHNESS

All A51 challenge-trace
freshness probes:

PASS.

The trace:

contributes only
from same-side committed survivors;

cannot cross side;

does not refresh itself;

is set only by
current CHALLENGE mode;

and clears
under non-challenge commitment.

MECHANICAL VALIDATION

Mechanical seed:

MECHANICAL-A51-F51-CANDIDATE

Complete sweeps:

2.

Worlds per sweep:

384.

Arms:

12.

Output bytes per sweep:

162017.

Output SHA256:

946a14b0da72343080607ad48e53488270ad4c45cc4e614cca80465ced6ea484

BYTE IDENTICAL:

true.

stderr:

empty for both sweeps.

All executable pre-primary
integrity probes:

PASS.

No mechanical-world
temporal-overlap result,
macro result,
timing-synergy result,
qualification result,
or population outcome
is used as scientific evidence.

SOURCE-BUNDLE FORMAT

The exact source above
will be published
as deterministic gzip/base64
split into seven neutral text source parts.

Source SHA256:

5d649564b50889b9a2241088b0c6b983b1dbf6c86731b66ad5cb7f3436b99867

Gzip bytes:

20888.

Gzip SHA256:

99ea5997fea4a43370c54ab66e8d2aab12bae0d7655ce7c3cabb093f37a927ce

Concatenated base64 characters:

27852.

Base64 SHA256:

ccf713951107bb62b6b00f887ffd93ebf5d30f4f10fe60c5bfc47b4344d2a93b

Source part count:

7.

The F51 loader must verify:

part count;
base64 identity;
gzip identity;
source identity;

before execution.

Any mismatch fails closed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
