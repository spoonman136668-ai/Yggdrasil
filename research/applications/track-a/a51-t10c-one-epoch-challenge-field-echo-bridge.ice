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


PRE-F51 AMENDMENT 02 — SUPERSEDE ONE-EPOCH MECHANICAL GATE

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F51
AND BEFORE ANY A51 SCIENTIFIC OUTCOME.

The mechanical gate recorded
in the immediately preceding
implementation amendment:

source SHA256
5d649564b50889b9a2241088b0c6b983b1dbf6c86731b66ad5cb7f3436b99867;

mechanical output SHA256
946a14b0da72343080607ad48e53488270ad4c45cc4e614cca80465ced6ea484;

is valid only for
the superseded one-epoch-only
A51 design.

It is NOT eligible
to establish F51.

AUTHORITATIVE DESIGN

The authoritative A51 design
is Amendment 01:

MEASURED HANDOFF-LAG TTL SWEEP.

Required TTLs:

0;
1;
2;
3.

Required arms:

20.

A new candidate source
must implement that exact sweep.

A fresh pair
of complete mechanical sweeps
must pass byte-identically.

The F51 source identity
must be different from
the superseded one-epoch source.

No A51 scientific outcome
has been observed.

No post-result tuning occurred.

Reason for supersession:

the post-A50 observational diagnostic
was completed before F51
and directly measured
the challenge-to-recovery handoff lag.

A one-epoch bridge
is causally under-dosed
relative to that measured seam.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F51 AMENDMENT 03 — AUTHORITATIVE TTL IMPLEMENTATION / MECHANICAL GATE

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F51
AND BEFORE ANY A51 SCIENTIFIC OUTCOME.

AUTHORITATIVE SOURCE

Bytes:
92671.

SHA256:
8284fc44fbe2dd965c477ba845f92d44aefa85b802adfe1d672cf144fb45baee

This source implements the
measured handoff-lag TTL sweep:

TTL0;
TTL1;
TTL2;
TTL3.

ARMS

Exactly twenty arms.

Ten per D family:

BASE;
G5;

PUSH_TTL0;
G5_PUSH_TTL0;

PUSH_TTL1;
G5_PUSH_TTL1;

PUSH_TTL2;
G5_PUSH_TTL2;

PUSH_TTL3;
G5_PUSH_TTL3.

PARENT PARITY

Representative current-control comparisons:

96.

Behavioral mismatches:

0.

FORCED-TRACE REDUCTION

With TTL trace contribution
forced to the current-only field,
TTL arms reduce exactly
to their TTL0 donors.

Representative comparisons:

72.

Mismatches:

0.

INTEGRITY

All executable pre-primary
integrity probes:

PASS.

MECHANICAL VALIDATION

Mechanical seed:

MECHANICAL-A51-TTL-F51-CANDIDATE

Complete sweeps:

2.

Worlds per sweep:

384.

Arms:

20.

Output bytes per sweep:

271988.

Output SHA256:

be3ee9d3367633750075b72f73393f52b371494cfc0d3977529bcce8ef188eb6

BYTE IDENTICAL:

true.

stderr:

empty for both sweeps.

No mechanical-world
handoff coverage,
recruitment result,
macro result,
timing interaction,
minimum TTL,
qualification result,
or population outcome
is used as scientific evidence.

SOURCE-BUNDLE FORMAT

The exact source above
will be published
as deterministic gzip/base64
split into seven neutral text source parts.

Source SHA256:

8284fc44fbe2dd965c477ba845f92d44aefa85b802adfe1d672cf144fb45baee

Gzip bytes:

21204.

Gzip SHA256:

afff3bb623f846181a37e5936c383b1991b37aa39d756a9b774b1fb52da10bb8

Concatenated base64 characters:

28272.

Base64 SHA256:

2ccaa35afbbf97a127b8ce2789c9a589adcb08746cfb409a946db4bdc06ee08b

Source part count:

7.

The F51 loader must verify:

part count;
base64 identity;
gzip identity;
source identity;

before execution.

Any mismatch fails closed.

The superseded one-epoch-only
source and mechanical gate
remain provenance only
and cannot establish F51.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-F51 PRIMARY MANIFEST BINDING

DATE:
2026-09-22.

F51:
6c50bc7be90731a60ce2c2f16a668eeb4e99881b

AUTHORITATIVE SOURCE SHA256:
8284fc44fbe2dd965c477ba845f92d44aefa85b802adfe1d672cf144fb45baee

PRIMARY SEED:
A51-F51-6c50bc7be90731a60ce2c2f16a668eeb4e99881b-PRIMARY

WORLD COUNT:
384.

WORLD SHAPE:
48 contexts x 8 replicas.

PRIMARY WORLD MANIFEST SHA256:
f7a7d92cca0c636374d1b4e371992c271d68e901b69a7e3042a60b0a366a7cea

STATUS:
BOUND AFTER F51
AND BEFORE ANY A51 PRIMARY ARM EXECUTION.

AUTHORITATIVE DESIGN:
measured handoff-lag TTL sweep.

TTLs:
0;
1;
2;
3.

ARMS:
20.

No A51 TTL exposure result,
recruitment result,
macro result,
minimum effective TTL,
timing-synergy result,
qualification result,
or scientific comparison
was observed before this binding.

Two complete primary sweeps
must be byte-identical
before scientific analysis.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


A51 PRIMARY CLOSURE

DATE:
2026-09-22.

F51:
6c50bc7be90731a60ce2c2f16a668eeb4e99881b

MANIFEST-BINDING COMMIT:
fda3ebc9fc7819d50269a894e8a31aeb738ec99f

AUTHORITATIVE SOURCE SHA256:
8284fc44fbe2dd965c477ba845f92d44aefa85b802adfe1d672cf144fb45baee

PRIMARY SEED:
A51-F51-6c50bc7be90731a60ce2c2f16a668eeb4e99881b-PRIMARY

PRIMARY WORLD MANIFEST SHA256:
f7a7d92cca0c636374d1b4e371992c271d68e901b69a7e3042a60b0a366a7cea

PRIMARY RUNS:
2.

PRIMARY OUTPUT BYTES:
271793.

PRIMARY OUTPUT SHA256:
5b8c6d2acc1242246b0504ca15e793fe660bf13dced1f0ed503c357af4cdefe5

BYTE IDENTICAL:
true.

stderr:
empty for both runs.

All executable integrity probes:
PASS.

All TTL trace-freshness probes:
PASS.

SCIENTIFIC STATUS

A51_MINIMUM_EFFECTIVE_TTL_FOUND:
FALSE.

No TTL arm is A51-QUALIFIED.

TEMPORAL BRIDGE INFORMATION GAIN

D2:

TTL1:
FALSE.

TTL2:
TRUE.

TTL3:
TRUE.

D3:

TTL1:
FALSE.

TTL2:
TRUE.

TTL3:
TRUE.

MACRO INFORMATION GAIN

D2 TTL1:
FALSE.

D2 TTL2:
FALSE.

D2 TTL3:
FALSE.

D3 TTL1:
FALSE.

D3 TTL2:
FALSE.

D3 TTL3:
FALSE.

LAYER-TIMING SYNERGY

D2 TTL1:
FALSE.

D2 TTL2:
TRUE.

D2 TTL3:
FALSE.

D3 TTL1:
FALSE.

D3 TTL2:
TRUE.

D3 TTL3:
TRUE.

Thus TTL2 is the first
reproducible LOCAL HANDOFF BRIDGE
for both D families.

But no TTL satisfies
the complete minimum-effective-TTL definition
because the macro-information gate
is not crossed.

D2 DIRECT HANDOFF RESULT

G5_PUSH_TTL0:

nonzero selected
same-side challenge field
among G5 releases:
3.31%.

former-side recruitment:
24.16%.

opposite-side recruitment:
4.27%.

same-epoch total recruitment:
40.27%.

G5_PUSH_TTL1:

field exposure:
13.65%.

increase versus TTL0:
+10.34 percentage points.

former-side recruitment:
25.38%.

increase:
+1.21 points.

TTL1 therefore fails
the frozen temporal-bridge threshold.

G5_PUSH_TTL2:

field exposure:
61.11%.

increase:
+57.79 percentage points.

former-side recruitment:
29.67%.

increase:
+5.50 points.

opposite-side recruitment:
2.97%.

change:
-1.30 points.

same-epoch total recruitment:
44.27%.

TTL2 therefore confirms
the measured approximately two-epoch
handoff lag.

G5_PUSH_TTL3:

field exposure:
64.36%.

increase:
+61.05 points.

former-side recruitment:
29.54%.

increase:
+5.38 points.

opposite-side recruitment:
3.05%.

Thus D2 gains little
additional local handoff
beyond TTL2.

D2 MACRO RESPONSE

TTL0:

burst-end favored fraction:
28.13%.

favored-majority burst-end frequency:
10.23%.

favored-to-unresolved transitions:
67.

mean unresolved duration:
3.590 epochs.

mean favored-majority recovery latency:
3.288 epochs.

median challenge-onset beta_F:
+0.04494 per cycle.

TTL2:

burst-end favored:
28.81%.

change:
+0.69 percentage point.

favored-majority frequency:
9.09%.

favored-to-unresolved:
68.

mean unresolved duration:
3.367 epochs.

reduction:
6.20%.

mean recovery latency:
3.088 epochs.

improvement:
0.20 epoch.

median beta_F:
+0.04435.

TTL3:

burst-end favored:
29.29%.

change:
+1.16 points.

favored-majority frequency:
11.36%.

favored-to-unresolved:
65.

reduction:
2.99%.

mean unresolved duration:
3.395 epochs.

reduction:
5.43%.

mean recovery latency:
3.000 epochs.

improvement:
0.288 epoch.

median beta_F:
+0.04926.

Therefore D2 local temporal handoff
is large,
but macro continuity changes only modestly.

D3 DIRECT HANDOFF RESULT

G5_PUSH_TTL0:

field exposure:
2.19%.

former-side recruitment:
24.47%.

opposite-side recruitment:
3.72%.

same-epoch total recruitment:
39.37%.

G5_PUSH_TTL1:

field exposure:
10.85%.

increase:
+8.66 points.

former-side recruitment:
25.34%.

increase:
+0.87 point.

TTL1 again fails
the temporal-bridge threshold.

G5_PUSH_TTL2:

field exposure:
50.82%.

increase:
+48.63 percentage points.

former-side recruitment:
28.35%.

increase:
+3.88 points.

opposite-side recruitment:
3.62%.

same-epoch total recruitment:
42.71%.

TTL2 therefore also confirms
the measured D3 handoff seam.

G5_PUSH_TTL3:

field exposure:
61.80%.

increase:
+59.62 points.

former-side recruitment:
29.16%.

increase:
+4.69 points.

opposite-side recruitment:
3.54%.

same-epoch total recruitment:
43.38%.

TTL3 captures additional D3
three-epoch handoff opportunities,
as predicted by the pre-A51 lag diagnostic.

D3 MACRO RESPONSE

TTL0:

burst-end favored fraction:
28.79%.

favored-majority burst-end frequency:
5.68%.

favored-to-unresolved transitions:
64.

mean unresolved duration:
3.600 epochs.

mean favored-majority recovery latency:
3.476 epochs.

median challenge-onset beta_F:
+0.07560 per cycle.

TTL2:

burst-end favored:
29.26%.

change:
+0.47 point.

favored-majority frequency:
9.09%.

favored-to-unresolved:
61.

reduction:
4.69%.

mean unresolved duration:
3.506 epochs.

reduction:
2.60%.

mean recovery latency:
3.256 epochs.

improvement:
0.220 epoch.

median beta_F:
+0.07783.

TTL3:

burst-end favored:
30.21%.

change:
+1.42 points.

favored-majority frequency:
9.09%.

favored-to-unresolved:
61.

reduction:
4.69%.

mean unresolved duration:
3.312 epochs.

reduction:
8.01%.

mean recovery latency:
3.110 epochs.

improvement:
0.366 epoch.

median beta_F:
+0.08140.

Thus D3 TTL3
is the strongest macro response,
but still remains below
the frozen A51 macro thresholds:

+2 percentage points
burst-end favored fraction;

and either:

10% fewer favored-to-unresolved transitions

or

10% shorter unresolved duration.

FIELD-ONLY SPECIFICITY

PUSH-only TTL persistence
also produces small improvements.

However the combined
G5 + TTL response
exceeds PUSH-only response
on enough preregistered metrics
for:

D2 TTL2;

D3 TTL2;

D3 TTL3

to satisfy
the frozen layer-timing-synergy rule.

Therefore the restored timing bridge
is not merely
generic field persistence.

There is measurable interaction
between recovery
and remembered challenge organization.

SAFETY / NON-REGRESSION

Across TTL0-TTL3:

direct favored-to-adverse flips:
0.

adverse-majority entries:
0
in the reported hard-target continuity metrics.

6:2 oscillator:
0%
for every reported TTL treatment.

Balanced false-majority:
0%.

D2 reversal acquisition:
89.84%.

D3 reversal acquisition:
87.50%.

Median old-majority loss:
3 epochs.

Service remains above
95% of paired BASE.

All trace freshness probes:
PASS.

All integrity probes:
PASS.

CREEP

Challenge-onset beta_F
remains positive
through the successful bridge arms.

There is no metastable
cycle-to-cycle core erosion.

CAUSAL INTERPRETATION

A51 confirms the A50 lag diagnosis.

The recovery/periphery handoff
was genuinely mistimed.

TTL1 is under-dosed.

TTL2 is the first duration
that restores enough local history
to change the released-cell recruitment stream.

TTL3 adds additional coverage,
especially in D3.

Therefore the local challenge message
really was arriving too early
relative to recovered-cell availability.

However A51 also shows
that this timing seam
is not the final macro bottleneck.

A large increase
in direct temporal overlap:

D2:
approximately 3% -> 61-64%;

D3:
approximately 2% -> 51-62%

produces only modest changes
in burst-end favored mass
and unresolved-state continuity.

The architecture therefore cannot
solve the remaining phenotype
simply by keeping
the A49 challenge field alive longer.

This rules out:

more TTL extension;

stronger push-pull gain;

stronger G5 recovery;

larger field radius;

or post-result threshold relaxation

as justified next steps.

The preregistered A51 failure attribution
is now satisfied:

TTL2 / TTL3 restore
high cross-layer temporal overlap;

favored recruitment among
G5-released cells rises;

local layer-timing interaction is measurable;

but macro continuity remains weak.

Therefore the next justified class is:

BROADER RESPONSE-PHASE /
FORCING ALIGNMENT.

That next experiment must
change the timing
of an explicitly defined
local response variable,

not merely extend
a recruitment-field memory.

PLAIN-SPEAK INTERPRETATION

We fixed the shift-change problem.

Two beats of local memory
were enough for both D2 and D3
to let many returning cells
hear the veterans' recent challenge message.

Three beats
caught even more of them,
especially in D3.

And those cells really did respond:

more returned to the veterans' side,
fewer joined the opposition.

So the timing bridge is real.

But the whole organism
barely moved.

We changed field exposure
from only a few percent
to roughly half or more
of the returning cells,

yet the population
still spent almost the same amount
of time falling into uncertainty.

That is a major narrowing result.

The problem is no longer:

"the core cannot survive";

"recovery is too slow";

"the core cannot influence neighbors";

or

"recovery and organization
miss each other in time."

We have now demonstrated
all four capabilities.

The remaining failure
is at a broader timing level:

the organism's response as a whole
is still being driven
in a way that reproduces
the same hard-cycle phenotype.

So the next test
should stop making
the existing signals stronger
or longer.

It should ask whether
the response itself
needs to occur
at a different phase
relative to the forcing.

NORTH-STAR IMPLICATION

A51 strengthens
the realization case
even though it is not qualified.

It demonstrates that
distributed mechanisms can be
temporally composed
using only bounded local memory,
without a central scheduler.

That composition is measurable,
safe,
and non-eroding.

Its failure is one of magnitude
at the organism level,
not absence of the local capability.

The remaining research question
has narrowed to
temporal organization
of the whole distributed response.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


A51 PRIMARY CLOSURE

DATE:
2026-09-22.

F51:
6c50bc7be90731a60ce2c2f16a668eeb4e99881b

MANIFEST-BINDING COMMIT:
fda3ebc9fc7819d50269a894e8a31aeb738ec99f

AUTHORITATIVE SOURCE SHA256:
8284fc44fbe2dd965c477ba845f92d44aefa85b802adfe1d672cf144fb45baee

PRIMARY SEED:
A51-F51-6c50bc7be90731a60ce2c2f16a668eeb4e99881b-PRIMARY

PRIMARY WORLD MANIFEST SHA256:
f7a7d92cca0c636374d1b4e371992c271d68e901b69a7e3042a60b0a366a7cea

PRIMARY RUNS:
2.

PRIMARY OUTPUT BYTES:
271793.

PRIMARY OUTPUT SHA256:
5b8c6d2acc1242246b0504ca15e793fe660bf13dced1f0ed503c357af4cdefe5

BYTE IDENTICAL:
true.

stderr:
empty for both runs.

All executable integrity probes:
PASS.

SCIENTIFIC STATUS

A51_MINIMUM_EFFECTIVE_TTL_FOUND:
FALSE.

A51 QUALIFICATION:
no TTL qualifies.

TEMPORAL BRIDGE INFORMATION GAIN

D2 TTL1:
FALSE.

D2 TTL2:
TRUE.

D2 TTL3:
TRUE.

D3 TTL1:
FALSE.

D3 TTL2:
TRUE.

D3 TTL3:
TRUE.

MACRO INFORMATION GAIN

D2 TTL1:
FALSE.

D2 TTL2:
FALSE.

D2 TTL3:
FALSE.

D3 TTL1:
FALSE.

D3 TTL2:
FALSE.

D3 TTL3:
FALSE.

LAYER-TIMING SYNERGY

D2 TTL1:
FALSE.

D2 TTL2:
TRUE.

D2 TTL3:
FALSE.

D3 TTL1:
FALSE.

D3 TTL2:
TRUE.

D3 TTL3:
TRUE.

Thus:

the measured temporal handoff seam is real;

TTL2 is the first duration
that restores substantial overlap;

but no TTL crosses
the frozen macro-information threshold.

D2 HANDOFF

G5_PUSH_TTL0:

same-side field exposure
among G5-released cells:
3.31%.

former-side recruitment:
24.16%.

same-epoch recruitment:
40.27%.

G5_PUSH_TTL1:

field exposure:
13.65%.

former-side recruitment:
25.38%.

same-epoch recruitment:
41.07%.

G5_PUSH_TTL2:

field exposure:
61.11%.

former-side recruitment:
29.67%.

same-epoch recruitment:
44.27%.

G5_PUSH_TTL3:

field exposure:
64.36%.

former-side recruitment:
29.54%.

same-epoch recruitment:
44.21%.

Therefore TTL2 produces
the main D2 temporal-bridge jump.

TTL3 adds little further
released-cell coverage or recruitment.

D2 MACRO RESULT

G5_PUSH_TTL0:

mean 5:3 burst-end favored fraction:
28.125%.

favored-majority burst-end frequency:
10.23%.

favored-to-unresolved transitions:
67.

mean unresolved duration:
3.590 epochs.

mean majority-recovery latency:
3.288 epochs.

median challenge-onset beta_F:
+0.04494 per cycle.

G5_PUSH_TTL2:

burst-end favored:
28.812%.

favored-majority:
9.09%.

favored-to-unresolved:
68.

unresolved duration:
3.367 epochs.

recovery latency:
3.087 epochs.

median beta_F:
+0.04435.

G5_PUSH_TTL3:

burst-end favored:
29.285%.

favored-majority:
11.36%.

favored-to-unresolved:
65.

unresolved duration:
3.395 epochs.

recovery latency:
3.000 epochs.

median beta_F:
+0.04926.

Relative to TTL0,
TTL3 raises burst-end favored mass
by only 1.16 percentage points.

That is below
the frozen +2 point macro threshold.

Unresolved-duration improvement
also remains below 10%.

D3 HANDOFF

G5_PUSH_TTL0:

same-side field exposure:
2.19%.

former-side recruitment:
24.47%.

same-epoch recruitment:
39.37%.

G5_PUSH_TTL1:

field exposure:
10.85%.

former-side recruitment:
25.34%.

same-epoch recruitment:
39.97%.

G5_PUSH_TTL2:

field exposure:
50.82%.

former-side recruitment:
28.35%.

same-epoch recruitment:
42.71%.

G5_PUSH_TTL3:

field exposure:
61.80%.

former-side recruitment:
29.16%.

same-epoch recruitment:
43.38%.

TTL2 again produces
the first major bridge.

TTL3 adds additional D3 coverage
consistent with the measured
2-3 epoch handoff lag.

D3 MACRO RESULT

G5_PUSH_TTL0:

mean 5:3 burst-end favored fraction:
28.788%.

favored-majority burst-end frequency:
5.68%.

favored-to-unresolved transitions:
64.

mean unresolved duration:
3.600 epochs.

mean majority-recovery latency:
3.476 epochs.

median challenge-onset beta_F:
+0.07560.

G5_PUSH_TTL2:

burst-end favored:
29.261%.

favored-majority:
9.09%.

favored-to-unresolved:
61.

unresolved duration:
3.506 epochs.

recovery latency:
3.256 epochs.

median beta_F:
+0.07783.

G5_PUSH_TTL3:

burst-end favored:
30.208%.

favored-majority:
9.09%.

favored-to-unresolved:
61.

unresolved duration:
3.312 epochs.

recovery latency:
3.110 epochs.

median beta_F:
+0.08140.

Relative to TTL0,
TTL3 raises burst-end favored mass
by 1.42 percentage points.

Again this is below
the frozen +2 point macro threshold.

Unresolved duration improves
by approximately 8.0%,
also below the frozen 10% threshold.

FIELD-ONLY VERSUS COMBINED

D2 PUSH-only:

TTL0 burst-end favored:
27.509%.

TTL2:
28.078%.

TTL3:
28.906%.

D2 combined:

TTL0:
28.125%.

TTL2:
28.812%.

TTL3:
29.285%.

TTL2 shows
a positive timing interaction
and satisfies the frozen
layer-timing-synergy criterion.

D3 PUSH-only:

TTL0:
26.705%.

TTL2:
26.752%.

TTL3:
27.060%.

D3 combined:

TTL0:
28.788%.

TTL2:
29.261%.

TTL3:
30.208%.

Both TTL2 and TTL3
show positive layer-timing synergy.

Therefore A51 confirms
that recovery and periphery control
do have a genuine temporal interaction.

The interaction is simply
too small at the population scale
to satisfy A51 macro information gain.

TTL-ONLY FAVORED RECRUITMENT

The primary contains
hundreds of former-side recruitments
that occur under TTL-only field exposure.

D2:

TTL2 combined:
688 TTL-only former-side recruitments.

TTL3 combined:
691.

D3:

TTL2 combined:
932.

TTL3 combined:
982.

Thus the bridge is
mechanically and behaviorally active.

It is not a null mechanism.

SAFETY / NON-REGRESSION

For all G5+TTL arms:

direct favored-to-adverse flips:
0.

adverse-majority entries:
0.

6:2 oscillator:
0%.

balanced false-majority:
0%.

D2 reversal acquisition:
89.84%.

D3 reversal acquisition:
87.50%.

Median old-majority loss:
3 epochs.

Aggregate service
remains above
95% of paired BASE.

Median challenge-onset beta_F
remains positive
for all TTL arms.

No metastable core erosion
is hidden by the TTL bridge.

POST-PRIMARY TRUE-REVERSAL MEMORY SAFETY DIAGNOSTIC

Because the primary summary
did not separately emit
the preregistered count
of remembered old-side
challenge-field recruitment
during the first four
post-reversal epochs,
an observational replay
was run against
the exact F51 primary seed
for all true-reversal contexts.

The replay changes
no dynamics.

Diagnostic runs:
2.

Diagnostic SHA256:
8a0f4e053ff5358aed64ebd747148585673d8188b772c0868970abe56f54041b

BYTE IDENTICAL:
true.

Across:

D2 TTL1;
D2 TTL2;
D2 TTL3;
D3 TTL1;
D3 TTL2;
D3 TTL3:

old-side remembered-field opportunities
during the first four
post-reversal epochs:

0.

old-side memory-induced
lambda-boost opportunities:

0.

old-side memory-boosted recruitments:

0.

Median old-majority loss:

3 epochs.

Reversal acquisition remains:

D2:
89.84%.

D3:
87.50%.

Thus the bounded TTL bridge
does not create
an observed old-side
post-reversal recruitment hazard
in the tested worlds.

CAUSAL INTERPRETATION

A50 correctly diagnosed
a temporal handoff problem.

A51 confirms it causally.

The one-epoch bridge
is under-dosed.

TTL2 is the first duration
that restores large-scale
released-cell exposure
to the recently active
challenge organization field.

TTL3 extends D3 coverage
further.

Released cells then recruit
toward their former/favored side
more often.

Therefore:

expired challenge-field timing
was a real missing signal.

However:

fixing that handoff
does not substantially change
the macro attractor.

The organism becomes
locally better coordinated
without crossing
the population-scale continuity threshold.

This rules out
simple bounded challenge-field persistence
as the final missing macro mechanism.

It also makes
stronger field amplitude,
larger radius,
stronger G5,
or TTL >3
poorly justified next moves.

The preregistered failure branch
is therefore reached:

temporal overlap rises strongly;

favored recruitment rises;

safety remains clean;

but macro continuity remains weak.

The next justified class is:

broader local response-phase /
forcing alignment.

PLAIN-SPEAK INTERPRETATION

We fixed the shift-change problem.

At two turns of memory,
the returning cells
finally hear the message
the challenged veterans
were sending.

At three turns,
even more of them hear it.

And they respond.

They join the favored side
more often.

So A50's timing diagnosis
was correct.

But the whole organism
still does not change enough.

That is important.

The problem is no longer:

the message vanished too early.

We restored the message
and the cells used it.

Yet the population still follows
essentially the same large cycle.

So simply letting
the old challenge message linger longer
is not the answer.

The remaining issue
looks one level deeper:

the timing of the organism's
actual response
relative to the repeating disturbance.

We have now earned
the right to test that directly.

Not by making the signal louder.

Not by increasing its radius.

Not by making memory longer.

By changing
WHEN a local response
takes effect.

NORTH-STAR IMPLICATION

A51 is a strong mechanistic result
despite failing qualification.

The architecture can now demonstrate:

local state persistence;

cooperative continuity;

adaptive recovery;

spatial periphery control;

and bounded temporal handoff
between independent local mechanisms.

Those layers compose
without a central scheduler.

The remaining macro failure
survives even after
the measured handoff seam
is repaired.

That substantially narrows
the realization problem
to temporal organization
of local responses
under repeated forcing.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
