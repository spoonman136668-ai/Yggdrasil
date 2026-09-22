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


PRE-F47 AMENDMENT 02 — POST-FIXA MECHANICAL GATE / SOURCE IDENTITY

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F47
AND BEFORE ANY A47 SCIENTIFIC OUTCOME.

AUTHORIZED CANDIDATE SOURCE

Bytes:
83463.

SHA256:
11ec74adb551e493077c4a931773e11e0d3ece4c59bc05f741a7d2b154fe3b73

Focused A45 ECHO_PHASE parent parity:

72 representative comparisons.

Behavioral mismatches:

0.

POST-FIXA MECHANICAL VALIDATION

Mechanical seed:

MECHANICAL-A47-F47-POSTFIXA-V2

Complete sweeps:

2.

Worlds per sweep:

384.

Arms:

6.

Output bytes per sweep:

76911.

Output SHA256:

efd46fd3eec0d42877ca2250e7fecb9dee673070e57d304d9ec4840fd2824365

BYTE IDENTICAL:

true.

stderr:

empty for both sweeps.

All executable pre-primary integrity probes:

PASS.

All acceleration arms observed:

release advance minimum = 1 epoch;

release advance maximum = 1 epoch.

Old-side accelerations
during the first four true-reversal epochs:

0
for every SUPPORT_ACCEL
and MPOST_ACCEL arm.

No mechanical-world population outcome
is used as scientific evidence.

SOURCE-BUNDLE FORMAT

F47 will publish
the exact authorized source
as deterministic gzip/base64
split into seven neutral text source parts.

Source SHA256:

11ec74adb551e493077c4a931773e11e0d3ece4c59bc05f741a7d2b154fe3b73

Gzip bytes:

19745.

Gzip SHA256:

07e65da46ec82102b5604581590284a67f63c88ca20a4245584923fa41d7af25

Concatenated base64 characters:

26328.

Base64 SHA256:

58790fce63d95b5f840dfcecd1582c857f0b02989aff651d98fec1d3f470c48f

Source part count:

7.

The F47 loader must verify:

part count;

base64 identity;

gzip identity;

source identity;

before execution.

Any mismatch fails closed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F47 AMENDMENT 03 — RECOVERY DOSE RESPONSE / STAGGERED RE-ENTRY / AXIS DECOUPLING

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F47
AND BEFORE ANY A47 SCIENTIFIC OUTCOME.

SUPERSESSION

This amendment supersedes
the original six-arm
one-tick-only A47 design
and supersedes the post-FIXA
mechanical gate bound in Amendment 02.

No F47 exists.

Therefore no A47 scientific outcome
has been observed,
and the design may still be corrected
without post-result tuning.

A fresh implementation,
focused parity gate,
and two complete mechanical sweeps
are required before F47.

RECOVERY BASELINE

A47 BASE is:

A45 ECHO_PHASE.

It is not A40.

A40 remains a historical control lineage,
but A47 is specifically testing
refractory recovery
on top of the accepted A45 organism.

FIXED ELIGIBILITY GATE

All A47 dose arms
use the same repaired A46 G5 eligibility signal.

For a currently refractory FC/FS cell
relative to its former side s:

G5(i)
=
local mode SUPPORT

AND

M_post(i,s) > 0

AND

Q_raw(i,s) > 0.

Q_raw timing
remains exactly the repaired A46 timing:

current committed-neighbor topology
weighted by B_pre margins.

The gate is checked
on every locked refractory epoch.

Dose arms differ only
in what happens
the first time G5 becomes true
within a refractory episode.

Each episode may receive
at most one dose action.

No gate threshold magnitude.
No new radius.
No gain.

DOSE DEFINITION

At an eligible locked epoch,
the ordinary parent timer behavior
would decrement the refractory timer by one
and keep the cell refractory
for the current epoch.

T1:

perform the parent decrement,
then remove one additional future refractory tick.

The cell remains refractory
for the current epoch.

T2:

perform the parent decrement,
then remove two additional future refractory ticks.

The cell remains refractory
for the current epoch.

FULL:

A46 upper-bound action.

If G5 is true,
release the cell to U immediately
in the current epoch.

The cell may then enter
ordinary same-epoch U recruitment,
exactly as repaired A46.

No direct recommitment.

No former-side recruitment bonus.

WHY THERE IS NO T3 ARM

Parent refractory durations are:

D2 = 2;

D3 = 3.

After the current parent decrement,
the maximum number
of remaining future locked epochs is:

D2:
1.

D3:
2.

Therefore:

D2 T2 and T3
would be dynamically identical to T1
if the cell must remain refractory
for the current epoch.

D3 T3
would be dynamically identical to T2.

Duplicating those arms
would create fake dose resolution.

Accordingly the legitimate
deferred-action dose ladder is:

D2:
T1 only.

D3:
T1 and T2.

FULL remains distinct
because it also removes
the current-epoch refractory lock.

ARMS

Exactly nine arms.

D2:

D2_BASE_ECHO_PHASE;
D2_G5_T1;
D2_G5_FULL;
D2_G5_FULL_STAGGER.

D3:

D3_BASE_ECHO_PHASE;
D3_G5_T1;
D3_G5_T2;
D3_G5_FULL;
D3_G5_FULL_STAGGER.

No redundant D2 T2/T3.
No redundant D3 T3.

No SUPPORT-only arm
in the dose-response primary.

The earlier SUPPORT-only evidence
remains useful observational context,
but it is not needed
to identify dose
once G5 is fixed.

STAGGERED FULL ARM

The stagger arm tests
whether A46 short-cycle chatter
is partly a synchronized-release artifact.

Eligibility remains G5.

While a cell is still refractory
and has not previously taken
a stagger action in the episode:

if G5 is false:

use parent refractory behavior.

If G5 is true:

draw one stateless Bernoulli
with fixed probability:

p = 1/2.

This is a preregistered timing probe,
not a fitted parameter.

Use a dedicated A47
stagger event salt.

If the draw succeeds:

apply FULL immediate re-entry to U.

If the draw fails:

use parent refractory behavior
for the current epoch.

A still-locked cell
may be tested again
on a later locked epoch
if G5 remains true.

No sequential RNG cursor exists.

The stagger draw
does not alter any other action draw.

RATIONALE FOR FIXED p = 1/2

Do not introduce
an undefined evidence-strength function g.

That would mix:

signal calibration;

dose;

and timing.

A fixed one-half probability
isolates only
population-level synchronization.

No probability sweep is allowed in A47.

COMMON-RANDOM DISCIPLINE

All nine arms share
the A45 ECHO_PHASE
stateless action-random identity
for every inherited stochastic event.

Dose actions T1/T2/FULL
are deterministic once G5 is true.

FULL_STAGGER adds only
the dedicated stagger Bernoulli.

Worlds,
sensor noise,
heterogeneity,
and all inherited event salts
remain paired.

This makes treatment/control differences
causally attributable
to recovery action.

RECOVERY AXIS

A47 is a recovery-layer experiment.

Primary scientific axis:

how quickly the organism
returns from disturbance-induced uncertainty
to stable favored participation.

The inherited oscillator metric
must still be reported
for lineage comparability.

But 5:3 inherited oscillator percentage
is NOT an A47 qualification criterion.

Reason:

A45 post-closure diagnosis showed
that the residual 5:3 detector
primarily counts:

favored
-> unresolved
-> favored

cycles,

with zero adverse-majority entries
in the audited phenotype.

A47 must not be labeled a recovery failure
because a broader macro-state metric
that includes temporary uncertainty
remains high.

NON-REGRESSION AXES

Although not a recovery target,
the already-solved 6:2 regime
remains a required non-regression check.

Also preserve:

wrong-side safety;

true-reversal safety;

balanced uncertainty;

service;

and chatter.

PRIMARY RECOVERY METRICS

For contexts 46/47 report:

mean unresolved-episode duration;

median unresolved-episode duration;

maximum unresolved-episode duration;

mean favored-majority recovery latency;

median favored-majority recovery latency;

recovery-never count;

mean refractory fraction
across support-recovery steps 1-3;

favored-to-unresolved transitions;

unresolved-to-favored transitions;

burst-end favored fraction;

support-recovery composition steps 1-5.

DOSE EFFECTIVENESS

For each non-BASE dose arm,
define RECOVERY_EFFECTIVE iff all are true:

1. mean 5:3 unresolved-episode duration
   is at least 25% lower
   than paired BASE;

2. mean 5:3 favored-majority recovery latency
   is at least 1.0 epoch lower
   than paired BASE;

3. mean refractory fraction
   across support-recovery steps 1-3
   is lower than paired BASE;

4. direct favored-to-adverse flips = 0;

5. adverse-majority entries = 0;

6. 6:2 oscillation
   does not exceed paired BASE;

7. reversal acquisition >= 80%;

8. balanced false-majority
   does not exceed paired BASE
   and remains <= 10%;

9. aggregate service >= 95%
   of paired BASE;

10. old-side G5 actions
    during the first four
    true-reversal epochs = 0;

11. all integrity probes pass.

CHATTER COST

Normalize short-cycle chatter by commitments:

R_chatter
=
same-side short-cycle events
/
max(1,total commitments).

For each D family,
define FULL excess chatter:

E_FULL
=
max(
0,
R_chatter(FULL)
-
R_chatter(BASE)
).

A sub-FULL dose has
ACCEPTABLE_CHATTER_COST iff:

its excess chatter rate

<=

75% of E_FULL.

Thus the accepted sub-FULL dose
must remove at least 25%
of the immediate-release excess chatter.

If E_FULL = 0:

all arms with no increase
over BASE pass the chatter constraint.

MINIMUM EFFECTIVE DOSE

Within each D family,
the minimum effective dose is
the lowest action intensity
that is:

RECOVERY_EFFECTIVE;

ACCEPTABLE_CHATTER_COST;

and safety-clean.

Dose order:

D2:
T1 < FULL.

D3:
T1 < T2 < FULL.

FULL is retained
as the repaired-A46 upper bound
even if its chatter cost
prevents selection
as the preferred recovery dose.

A47_RECOVERY_INFORMATION_GAIN

TRUE iff at least one
non-BASE dose arm
is RECOVERY_EFFECTIVE.

A47_MINIMUM_EFFECTIVE_DOSE_FOUND

TRUE iff at least one
sub-FULL dose arm
is both:

RECOVERY_EFFECTIVE;

and

ACCEPTABLE_CHATTER_COST.

STAGGER HYPOTHESIS

FULL_STAGGER tests
whether synchronized immediate re-entry
is a material source
of A46 chatter.

For each D family,
define FULL_STAGGER_INFORMATION_GAIN TRUE iff:

1. FULL_STAGGER retains at least 75%
   of FULL's reduction
   in mean recovery latency
   versus BASE;

2. FULL_STAGGER retains at least 75%
   of FULL's reduction
   in mean unresolved duration
   versus BASE;

3. FULL_STAGGER excess chatter rate
   is at least 25% lower
   than FULL excess chatter rate;

4. wrong-side entries remain zero;

5. 6:2 non-regression passes;

6. reversal acquisition >= 80%;

7. balanced false-majority
   does not exceed BASE
   and remains <=10%;

8. service >=95% of BASE;

9. all integrity probes pass.

If true:

a meaningful fraction
of immediate-release chatter
is attributable
to synchronized timing.

If false because recovery benefit collapses:

the immediate action,
not merely synchrony,
is carrying the recovery effect.

If false because chatter does not fall:

the chatter is not primarily
a synchronized-release artifact.

QUALIFICATION

A47 recovery-layer qualification
does NOT require
a 5:3 inherited oscillator ceiling.

An arm is A47-RECOVERY-QUALIFIED iff:

RECOVERY_EFFECTIVE;

wrong-side safe;

true-reversal safe;

balanced safe;

6:2 non-regressing;

service-preserving;

and all integrity probes pass.

A sub-FULL arm
may additionally be designated:

MINIMUM-DOSE CANDIDATE

only if
ACCEPTABLE_CHATTER_COST also passes.

The inherited:

overall oscillator rate;

biased-periodic oscillator rate;

5:3 oscillator rate

remain mandatory reported metrics
but are explicitly OUT OF SCOPE
for recovery-layer qualification.

STRATEGIC EXIT RULE

If A47 identifies
a minimum effective sub-FULL dose

and the recovery layer
passes its safety constraints:

freeze that recovery behavior
as the recovery-layer candidate.

Do not continue
strengthening refractory modulation
merely to lower
the inherited 5:3 oscillator score.

Return the research program
to the separate
population-organization / oscillation track.

The next macro experiment
must use the accepted recovery layer
as a frozen substrate,
not retune it.

A41 exclusion
and A42 active recruitment
remain relevant donor mechanisms
for that separate push-pull question,

but any successor composition
must be preregistered
against the actual closed A41/A42 results
before implementation.

PLAIN-SPEAK UPDATE

A46 proved
that some cells are sitting out
longer than necessary.

But opening the gate completely
makes more local chatter.

A47 will no longer ask only:

does shaving one turn help?

It asks:

HOW MUCH OF THE WAIT
DO WE REALLY NEED TO REMOVE?

For D3
we can legitimately test:

one future turn;

two future turns;

or immediate release.

For D2
there is only one future turn
available to shave,
so pretending there are
T2 and T3 doses
would just duplicate the same behavior.

We also test
whether the chatter comes from
too many cells standing up
at exactly the same time.

The stagger arm
uses the same readiness signal
but spreads immediate release
across cells probabilistically.

And most importantly:

A47 will be judged
on the problem it is actually solving.

Recovery.

Not whether it single-handedly
solves every remaining
macro population cycle.

If we find
the smallest recovery dose
that works safely
and with less chatter,

we lock that layer.

Then we return
to the separate question
of how a recovered core
controls the surrounding population.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
