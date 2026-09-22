TITLE: YGGDRASIL A47 / T9E — Evidence-Aligned One-Tick Refractory Acceleration
DATE: 2026-09-22
STATUS: PREREGISTERED RECOVERY-CONTROL EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T9E / APPLICATION-A
PARENT: A45 One-Epoch Cooperative Support Echo / ECHO_PHASE
NEGATIVE PARENT: A46 Cooperative-Confirmed Refractory Re-entry
DIAGNOSTIC PARENT: A46 Common-Random G5 Causal Isolation
BRANCH: dg1a-ar

EVIDENCE BASIS

A45 established that
the residual 5:3 phenotype
is predominantly:

favored majority
-> unresolved
-> favored majority,

not wrong-side capture.

A45 also showed
that refractory FC/FS debt
dominates the unresolved population
during early support recovery.

The A45 evidence-gate audit found:

on the first locked refractory epoch
of 5:3 recovery,

local SUPPORT:

100%;

SUPPORT + M_post > 0:

approximately 72-74%.

In balanced-periodic worlds
on the first locked refractory epoch:

SUPPORT:

approximately 47%;

SUPPORT + M_post > 0:

approximately 35-36%.

After true reversal,
the old side shows:

SUPPORT:

0%;

SUPPORT + M_post > 0:

0%.

A46 then tested
a stronger later gate:

SUPPORT + M_post > 0 + Q_raw > 0

with immediate release to U.

A46 was not qualified.

Its frozen independent-stream primary
showed no preregistered information gain.

A full post-closure common-random replay
showed a smaller causal effect:

D2 mean recovery latency:
3.487 -> 2.962 epochs;

D2 unresolved episode duration:
3.616 -> 3.190 epochs;

D3 mean recovery latency:
4.268 -> 3.250 epochs;

D3 unresolved episode duration:
4.795 -> 3.711 epochs.

Wrong-side capture remained zero.

But chatter increased,
and no 5:3 oscillator label was broken.

Therefore:

the recovery signal contains useful information;

immediate release is stronger
than the evidence justifies;

a smaller timer action
is the next causal test.

A47 QUESTION

Can locally supportive
current evidence
remove exactly one future refractory epoch

without exposing the cell
to same-epoch recruitment,

and does requiring
post-update former-side margin positivity

retain most of the recovery benefit
while reducing balanced/noisy activation?

F47 FREEZE

Let the exact A47 implementation freeze commit be:

F47.

No real A47 world,
population outcome,
or scientific result
may be derived before F47 exists.

WORLD SHAPE

384 fresh post-F47 trials.

48 contexts x 8 replicas.

48 cells.

48 epochs.

Environmental families remain structurally identical
to A45/A46.

PARENT DYNAMICS

Use A45 ECHO_PHASE unchanged
except for the explicit timer acceleration
in treatment arms.

Preserve:

A36 ecology;

A40 signed temporal state;

A43 margin cooperation;

A44 local SUPPORT / CHALLENGE / NEUTRAL mode;

A44 support-gated active recruitment;

A45 one-epoch non-recursive cooperative echo.

A46 immediate G5 re-entry
is NOT inherited.

No A37 lineage state exists.

REFRACTORY PARENT LAW

Committed C defection:

C -> FC.

Committed S defection:

S -> FS.

Parent refractory duration:

D2 = 2.

D3 = 3.

At each later epoch,
before ordinary U recruitment:

if timer <= 0:

refractory -> U.

Otherwise:

decrement timer by one;

remain refractory
for the current epoch.

FIRST LOCKED EPOCH

A refractory cell
is on its first locked epoch
iff:

timer = D

before ordinary timer decrement.

Acceleration can occur
only on this first locked epoch.

It cannot occur twice
within the same refractory episode.

CURRENT LOCAL SNAPSHOT

For former side s:

read the existing A44 local mode
relative to side s.

Read:

M_post(i,s)

from the already-updated
current signed B.

No pre-update margin
is used for the MPOST gate.

No cooperative Q field
is required.

No future evidence.

No global phase.

No majority label.

No environment-family identity.

SUPPORT_ACCEL CONTROL

gate_support(i)
=
1

iff:

cell is FC or FS;

timer = D;

local mode
relative to former side
is SUPPORT.

Otherwise:

0.

MPOST_ACCEL TREATMENT

gate_mpost(i)
=
1

iff:

cell is FC or FS;

timer = D;

local mode
relative to former side
is SUPPORT;

M_post(i,s) > 0.

Otherwise:

0.

ACTION

For every locked refractory cell:

perform the parent timer decrement:

timer := timer - 1.

If the arm's acceleration gate is true:

timer := max(0,timer - 1).

The cell REMAINS REFRACTORY
for the current epoch
even if timer becomes zero.

There is:

no same-epoch release;

no same-epoch U recruitment;

no direct recommitment;

no special recruitment bonus.

At the next epoch,
ordinary parent logic
releases the cell to U
iff timer <= 0.

MAXIMUM EFFECT

Each refractory episode
can become recruitable
at most one epoch earlier
than A45.

No additional acceleration
can occur later
in the same episode.

A45 ECHO TRACE

Refractory cells carry
no active cooperative echo.

When a cell later returns to U
and is recruited again,
the new commitment begins
with zero echo,

exactly as in A45.

ARMS

Exactly six arms.

D2:

D2_ECHO_PHASE;
D2_SUPPORT_ACCEL;
D2_MPOST_ACCEL.

D3:

D3_ECHO_PHASE;
D3_SUPPORT_ACCEL;
D3_MPOST_ACCEL.

No immediate-release arm.

No Q gate.

No fixed unconditional shortening arm.

No timer-elimination arm.

No threshold magnitude.

No gain.

No new radius.

COMMON-RANDOM PRIMARY DESIGN

A47 uses common stateless action-random draws
within each D family.

For D2:

ECHO_PHASE;
SUPPORT_ACCEL;
MPOST_ACCEL

all use the exact A45
D2_ECHO_PHASE action-random namespace
and arm identity.

For D3:

all three use the exact A45
D3_ECHO_PHASE action-random namespace
and arm identity.

World generation,
sensor noise,
and heterogeneity
remain unchanged.

Random draws remain keyed by:

epoch;
cell;
event salt.

No sequential RNG cursor exists.

Therefore state divergence
cannot shift later random draws.

This primary design deliberately
reduces treatment/control stochastic variance
so the timer action
is causally isolated.

PRIMARY TARGET

Contexts 46 and 47:

5:3 biased periodic.

Retain full reporting
for all 48 contexts.

6:2 CONTROL

Contexts 44 and 45.

A47 must preserve
A45's 6:2 stability.

BALANCED CONTROL

Contexts 40-43.

TRUE REVERSAL CONTROL

Preserve all A45
true-reversal worlds and metrics.

WRONG-SIDE METRICS

For 5:3 report:

direct favored-to-adverse flips;

adverse-majority entries;

adverse-majority epochs;

maximum adverse-majority residence.

UNRESOLVED RECOVERY METRICS

For 5:3 report:

favored-to-unresolved transitions;

unresolved-to-favored transitions;

unresolved episode count;

mean episode duration;

median episode duration;

maximum episode duration;

favored-majority recovery latency
after adverse bursts;

recovery-never count.

RECOVERY COMPOSITION

At burst end
and support-recovery steps 1-5 report:

favored committed;

adverse committed;

U;

H;

FC;

FS;

total refractory;

total unresolved.

ACCELERATION MECHANISM METRICS

For every first-locked refractory observation report:

former side;

local mode;

M_post;

SUPPORT gate true/false;

MPOST gate true/false;

arm gate true/false;

timer before;

timer after;

whether accelerated.

Aggregate separately for:

5:3 favored-side recovery;

6:2 favored-side recovery;

balanced periodic;

true reversal old side;

true reversal new side;

nonperiodic.

ACTUAL RELEASE EFFECT

For accelerated episodes report:

epoch of acceleration;

epoch of eventual U release;

parent counterfactual release epoch;

whether recruited
within 1, 2, and 4 epochs after release;

recruited side;

time to next defection.

This verifies
that acceleration changes availability
by exactly one epoch
and no more.

CHATTER SAFETY

Report per arm:

total inherited chatter events;

balanced chatter events;

short same-side
commit -> refractory -> U -> same-side commit -> defect
within 4 epochs;

opposite-side recommitment
within 4 epochs;

mean commitment dwell;

median commitment dwell.

TRUE REVERSAL SAFETY

For old-side refractory cells
during the first four epochs
after true reversal report:

SUPPORT gate fires;

MPOST gate fires;

timer accelerations.

Desired:

zero accelerations
in MPOST_ACCEL.

BALANCED SELECTIVITY

Report first-locked:

SUPPORT gate rate;

MPOST gate rate;

actual acceleration rate;

false-majority rate;

majority residence;

chatter.

A47_ACCEL_INFORMATION_GAIN

TRUE iff at least one MPOST_ACCEL arm
satisfies all:

1. mean 5:3 unresolved episode duration
   is at least 10% lower
   than paired ECHO_PHASE;

2. mean 5:3 favored-majority
   recovery latency
   is at least 0.5 epoch lower
   than paired ECHO_PHASE;

3. mean refractory fraction
   across support-recovery steps 1-3
   is lower than paired ECHO_PHASE;

4. 6:2 biased-periodic oscillation
   does not exceed paired ECHO_PHASE;

5. direct favored-to-adverse flips = 0;

6. adverse-majority entries = 0;

7. reversal acquisition >= 80%;

8. balanced false-majority <= 10%;

9. aggregate service >= 95%
   of paired ECHO_PHASE;

10. inherited total chatter
    does not exceed 125%
    of paired ECHO_PHASE;

11. all integrity probes pass.

A47_EVIDENCE_SELECTIVITY

TRUE iff at least one D family
satisfies all:

1. MPOST_ACCEL balanced acceleration rate
   is at least 20% lower
   than SUPPORT_ACCEL;

2. MPOST_ACCEL retains at least 75%
   of SUPPORT_ACCEL's reduction
   in mean 5:3 recovery latency
   versus ECHO_PHASE;

3. MPOST_ACCEL retained recovery benefit
   is positive;

4. MPOST_ACCEL balanced false-majority
   does not exceed SUPPORT_ACCEL;

5. MPOST_ACCEL balanced chatter
   does not exceed SUPPORT_ACCEL;

6. true-reversal old-side
   MPOST accelerations = 0.

A47 QUALIFICATION

D2_MPOST_ACCEL
or
D3_MPOST_ACCEL

is A47-QUALIFIED iff all are true:

1. overall inherited oscillator rate <= 5%;

2. 6:2 oscillation = 0%;

3. 5:3 direct adverse-majority entries = 0;

4. mean 5:3 unresolved duration
   is at least 20% lower
   than paired ECHO_PHASE;

5. median favored-majority recovery latency <= 2 epochs;

6. recovery-never count
   is lower than paired ECHO_PHASE;

7. balanced false-majority <= 10%;

8. reversal acquisition >= 80%;

9. median old-majority loss <= 4 epochs;

10. aggregate service >= 95%
    of paired ECHO_PHASE;

11. total inherited chatter
    does not exceed 125%
    of paired ECHO_PHASE;

12. old-side true-reversal
    MPOST accelerations = 0;

13. acceleration changes
    release timing by no more
    than exactly one epoch;

14. all integrity probes pass.

FAILURE ATTRIBUTION

If SUPPORT_ACCEL helps
but MPOST_ACCEL does not:

post-update margin filtering
removes too many useful
recovery opportunities.

If MPOST_ACCEL helps
and SUPPORT_ACCEL creates
more balanced chatter:

current signed evidence
is a useful selectivity signal.

If both help similarly
with similar safety:

local SUPPORT alone
is sufficient for
one-tick acceleration.

If neither improves recovery:

fixed refractory delay
is not the remaining bottleneck
at the one-epoch scale.

If recovery improves
but chatter exceeds 125%:

one-tick plasticity
is still too aggressive
under current commitment dynamics.

If 6:2 stability is lost
under common random draws:

the acceleration itself,
not stochastic realization,
destabilizes the already-solved regime.

If old-side acceleration occurs
after true reversal:

the gate is unsafe
and the mechanism class is rejected.

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
A45 ECHO_PHASE dynamics unchanged
outside timer acceleration.

P6:
D2 parent D = 2.

P7:
D3 parent D = 3.

P8:
acceleration only on timer = D.

P9:
acceleration occurs at most once
per refractory episode.

P10:
SUPPORT_ACCEL uses local mode only.

P11:
MPOST_ACCEL requires local SUPPORT.

P12:
MPOST_ACCEL requires M_post > 0.

P13:
no M magnitude threshold exists.

P14:
no Q field enters the acceleration gate.

P15:
no future evidence enters the gate.

P16:
no global phase enters the gate.

P17:
no majority label enters the gate.

P18:
no context/family identity enters the gate.

P19:
accelerated cell remains refractory
for current epoch.

P20:
no same-epoch recruitment
from acceleration.

P21:
release remains to U only.

P22:
normal recruitment decides
future commitment.

P23:
new commitment echo starts zero.

P24:
no old echo crosses refractory.

P25:
maximum release advance = 1 epoch.

P26:
paired arms use common
stateless action-random draws.

P27:
ECHO_PHASE controls
reproduce A45 under the new F47 seed.

P28:
no A37 lineage state exists.

P29:
two complete mechanical sweeps
byte-identical before F47.

P30:
F47 exists before real worlds are derived.

P31:
post-F47 world manifest bound
before primary arm execution.

P32:
two complete primary sweeps
byte-identical.

RESEARCH DISCIPLINE

Mechanical fake-world validation
must pass twice byte-identically
before F47.

Focused A45 parent parity
must pass before F47.

Common-random identity
must be mechanically verified
before F47.

F47 must exist
before fresh A47 primary worlds are derived.

No post-result:

timer change;

gate threshold;

gate condition;

arm;

qualification;

RNG pairing;

radius;

or world-family tuning.

PLAIN-SPEAK QUESTION

A46 taught us
that the cell's recovery signal
contains useful information,

but immediately taking
the safety lock off
is too large a move.

A47 makes the smallest change possible.

A benched cell
still has to sit out
the current turn.

It cannot jump straight back
into the population.

But on its first waiting turn,
if the neighborhood supports
its old side again,

we test whether
one turn can be removed
from the rest of its sentence.

Then we ask
one extra question:

is neighborhood support alone enough,

or should the cell also require
its own updated evidence
to agree with that old side?

Because every arm sees
the same random breaks,

a difference this time
can be attributed much more directly
to that one timer decision.

The test is:

CAN LOCAL EVIDENCE
MAKE REFRACTORY RECOVERY
ONE BEAT MORE FLEXIBLE

WITHOUT REOPENING
CHATTER,
WRONG-SIDE CAPTURE,
OR TRUE-REVERSAL STUBBORNNESS?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F47 AMENDMENT 01 — POST-A46-FIXA AUTHORIZATION

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F47
AND BEFORE ANY A47 SCIENTIFIC OUTCOME.

PREDECESSOR REPAIR

After the initial A47 preregistration,
a material parent-mechanism defect
was discovered in the original A46
G5 treatment implementation.

A46-FIXA repaired that conformance defect
without changing the A46 scientific design.

A46-FIXA closure:

ad2e61b09dcfed79b33523a470ffa57f320593e9.

F46A:

6a52b0ed4372371727649e4f14f5967d28345551.

Repaired primary SHA256:

d66b8475be964cab80da82af3c868fec98c9015d66d9fd374d609e02e670de12.

REPAIRED PREDECESSOR RESULT

D3 repaired G5_REENTRY
satisfies the original A46
recovery-information-gain rule.

Relative to D3 ECHO_PHASE:

mean unresolved episode:

5.408 -> 3.975 epochs
(-26.50%);

mean favored-majority recovery latency:

6.506 -> 5.034 epochs
(-1.472 epochs);

mean refractory fraction
across recovery steps 1-3:

45.71% -> 28.62%
(-37.39%);

aggregate service:

+1.05%;

5:3 epoch-3 core persistence:

+3.21 percentage points.

6:2 oscillation remains:

0%.

5:3 wrong-side majority entries:

0.

Old-side G5 fires
during the first four true-reversal epochs:

0.

D3 G5 remains NOT QUALIFIED
because the hard 5:3 inherited oscillator phenotype
is not removed
and the stronger qualification thresholds
are not met.

D2 improves
but does not cross
the original A46 information-gain threshold.

A47 AUTHORIZATION

The repaired predecessor therefore confirms
the causal premise behind A47:

refractory timing
is a real post-disturbance recovery bottleneck;

immediate re-entry provides useful recovery benefit;

but the full immediate-release action
is stronger than necessary
and carries extra local cycling cost.

The A47 mechanism,
arms,
gates,
criteria,
and common-random design
remain exactly as originally preregistered.

No scientific rule changes.

No threshold changes.

No timer changes.

No arm changes.

No RNG-pairing changes.

PREVIOUS A47 MECHANICAL WORK

Any A47 mechanical sweep
performed before A46-FIXA closure
is diagnostic-only.

It cannot qualify F47.

A fresh pair of complete
post-FIXA mechanical sweeps
must pass byte-identically
before F47.

CURRENT A47 CANDIDATE SOURCE

SHA256:

11ec74adb551e493077c4a931773e11e0d3ece4c59bc05f741a7d2b154fe3b73

Focused A45 parent parity
already observed:

72 representative ECHO_PHASE comparisons;

behavioral mismatches:

0.

The fresh formal mechanical gate
must re-confirm
all executable integrity conditions.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
