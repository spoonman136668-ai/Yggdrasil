TITLE: YGGDRASIL A27 / T8K — Negative-Feedback Homeostatic Authority Correction
DATE: 2026-09-21
STATUS: PREREGISTERED HOMEOSTATIC-CONTROL EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8K / APPLICATION-A
PARENT: A26 Threshold / Ultrasensitivity Calibration
BRANCH: dg1a-ar

PURPOSE

A24-A26 tested whether Yggdrasil could certify a patch
before granting broader authority.

Quorum helped identify broad present-tense support.
Temporal persistence filtered some transient positives.
Hard thresholds reduced actions but did not calibrate future benefit.

None was sufficient as sole activation authority.

A27 changes the question.

Instead of asking:

"can I know in advance that this patch will remain safe?"

A27 asks:

"if bounded patch authority starts becoming wrong,
can negative feedback detect the deviation
and reduce authority before damage compounds?"

A27 isolates homeostatic correction.

It does NOT add:

quorum authority;
temporal-filter authority;
threshold-gate authority;
positive-feedback commitment;
bet-hedging;
adaptive rule tuning.

FROZEN PARENT

A26 closure:

b265bbff9619a40896dd7946e6a334c7527b7e26.

A26 result:

stronger positive W1 magnitude
did not monotonically predict safer W2 consequence.

A27 FREEZE

Let the exact A27 implementation freeze commit be:

F27.

No real A27 trajectory,
feedback error,
authority update,
or outcome
may be derived before F27 exists.

FRESH TRAJECTORIES

After F27,
derive exactly:

384

fresh trajectories:

48 fixed A17 patch contexts
x
8 F27-derived replicas.

Each trajectory contains:

32 fresh demand epochs.

Control blocks:

B1 = epochs 0-3;
B2 = 4-7;
B3 = 8-11;
B4 = 12-15;
B5 = 16-19;
B6 = 20-23;
B7 = 24-27;
B8 = 28-31.

Replacement episodes:

0;
4;
8;
12;
16;
20;
24;
28.

Every 32-demand sequence has exact mean
equal to the candidate target prior.

All demand / replacement namespaces:

YGG-A27-*.

MATCHED STALE TWIN

Every controller runs beside
an exact all-stale twin.

At every replacement episode:

the controller and stale twin
receive the same replacement cell IDs.

During every epoch:

they receive the same demand.

Both use the inherited deterministic migration rule.

The stale twin is:

the operating setpoint reference;
the correction comparator;
and the rollback reference.

AUTHORITY VARIABLE

Candidate birth authority is:

A in {0,1,2,3}.

A means:

the first A newborns
in the canonical four-cell replacement order
use candidate target prior.

The remaining 4-A newborns
use stale-previous prior.

A = 0:
all stale-controlled births.

A = 3:
the established 75% provisional exposure.

No A27 controller may use:

A = 4.

No full candidate authority exists in A27.

INITIAL AUTHORITY

At epoch 0:

A_1 = 3.

Thus all homeostatic controllers
begin with the same 3-of-4 bounded exposure.

HOMEOSTATIC ERROR

After each four-epoch block Bi,
compute:

E_i =
controller service in Bi
-
matched stale-twin service in Bi.

Setpoint:

E_i >= 0.

Negative E_i means:

the current authority state
is underperforming the stable reference.

Feedback updates only authority
for FUTURE births.

It never rewrites
already-living cells.

REFERENCE CONTROLLERS

R0 — ALL STALE

A = 0 at every replacement.

R3 — STATIC C3

A = 3 at every replacement.

R4 — FULL CANDIDATE REFERENCE

All four births candidate-controlled
at every replacement.

R4 is reference only.

HOMEOSTATIC CONTROLLERS

H1 — ONE-STEP DOWN / HOLD

Start:

A = 3.

After each block except B8:

if E_i < 0:

A_next = max(0, A_current - 1).

if E_i >= 0:

A_next = A_current.

H1 never re-escalates.

It tests whether simple negative correction
can limit accumulating harm.

H2 — PROPORTIONAL DOWN / HOLD

Start:

A = 3.

After each block except B8:

if E_i < 0:

A_next =
max(0, A_current - min(3, abs(E_i))).

if E_i >= 0:

A_next = A_current.

H2 never re-escalates.

It tests whether larger observed deviation
should trigger stronger corrective reduction.

H3 — REVERSIBLE ONE-STEP HOMEOSTASIS

Start:

A = 3.

After each block except B8:

if E_i < 0:

A_next = max(0, A_current - 1).

if E_i == 0:

A_next = A_current.

if E_i > 0:

A_next = min(3, A_current + 1).

H3 may restore authority
only toward the original bounded setpoint A=3.

It can never exceed A=3.

This tests whether authority can recover
after local correction
without requiring a new patch-learning event.

NO RETROACTIVE REWRITE

Authority changes affect only
the next replacement births.

Existing living cells:

are not forcibly rewritten;
are not deleted;
are not relabeled;
retain inherited runtime state.

This is essential.

A27 tests negative feedback,
not global state replacement.

PRIMARY METRICS

For R3 / H1 / H2 / H3 report:

aggregate 32-epoch service;

aggregate delta versus R0;

aggregate delta versus R3;

trajectory-level:

beneficial vs R0;
neutral vs R0;
harmful vs R0;

harmful-trajectory rate;

worst cumulative drawdown
relative to stale twin;

median and mean cumulative delta;

authority occupancy:

epochs / blocks at A=0;
A=1;
A=2;
A=3;

authority-change count;

first correction block;

correction latency
from first negative E_i
to next lower-authority birth event;

number of negative blocks;

number of repeated negative blocks;

number of positive blocks after correction.

H3 additionally reports:

re-escalation count;

successful recoveries:
authority increases
and the next block E >= 0;

failed recoveries:
authority increases
and the next block E < 0.

HARM-CONTAINMENT METRICS

Let STATIC-HARMFUL be trajectories where:

R3 total service
<
R0 total service.

For H1 / H2 / H3 report:

STATIC-HARMFUL count;

STATIC-HARMFUL trajectories improved:

controller delta vs R0
>
R3 delta vs R0;

STATIC-HARMFUL trajectories fully rescued:

controller delta vs R0
>= 0;

STATIC-HARMFUL trajectories worsened.

BENEFIT-RETENTION METRICS

Let STATIC-BENEFICIAL be trajectories where:

R3 total service
>
R0 total service.

For H1 / H2 / H3 report:

STATIC-BENEFICIAL count;

retained beneficial:

controller delta vs R0
> 0;

neutralized:

controller delta vs R0
== 0;

converted harmful:

controller delta vs R0
< 0.

HOMEOSTATIC QUALIFICATION

A homeostatic controller is HOMEOSTATIC-QUALIFIED iff all are true:

trajectory harmful rate vs R0 <= 0.05

AND

aggregate 32-epoch service >= R0

AND

at least 50% of STATIC-HARMFUL trajectories improve over R3

AND

at least 50% of STATIC-BENEFICIAL trajectories remain beneficial

AND

worst cumulative drawdown
is no worse than R3's worst cumulative drawdown

AND

all integrity probes pass.

A27 does not select a production winner.

If multiple controllers qualify,
all are reported.

Any later combination with quorum,
persistence,
thresholding,
commitment,
or bet-hedging
requires a new preregistered experiment.

A27_HOMEOSTATIC_INFORMATION_GAIN

TRUE iff at least one of H1 / H2 / H3:

has lower harmful-trajectory rate than R3

AND

improves at least 50% of STATIC-HARMFUL trajectories

AND

retains at least 50% of STATIC-BENEFICIAL trajectories.

This is descriptive only.

INTEGRITY PROBES

P1:
exact A17 replay unchanged.

P2:
384 unique post-F27 trajectories.

P3:
32 demands per trajectory;
exact mean equals candidate target.

P4:
replacement episodes exactly
0 / 4 / 8 / 12 / 16 / 20 / 24 / 28;
four unique IDs each.

P5:
all controllers and twins
receive identical demand identities.

P6:
all controllers and twins
receive identical replacement IDs.

P7:
authority bounded exactly:

0 <= A <= 3.

P8:
initial authority exactly A=3.

P9:
H1 negative error:
one-step decrease;
nonnegative:
hold.

P10:
H2 negative error:
decrease by min(3,abs(E));
nonnegative:
hold.

P11:
H3 negative:
one-step decrease;
zero:
hold;
positive:
one-step increase capped at 3.

P12:
no controller can create A=4.

P13:
authority change affects future births only.

P14:
living cells are never forcibly rewritten
by feedback.

P15:
stale twin never consumes candidate authority.

P16:
learned patch remains preserved
at A=0.

P17:
restart equivalence
at every four-epoch block boundary.

P18:
two complete primary sweeps byte-identical.

P19:
no C-v3;
no duplicate context;
major history [v1,v2];
slot count 3.

NEGATIVE / LIMIT CONTROLS

N1 — STATIC C3

R3 reference.

N2 — FULL CANDIDATE

R4 reference.

N3 — CORRECT USING FUTURE BLOCK

Invalid future leakage.

N4 — FORCED REWRITE OF LIVING CELLS

Invalid A27 behavior.

N5 — DELETE PATCH WHEN A REACHES 0

Invalid learned-memory destruction.

N6 — AUTHORITY ABOVE 3

Outside A27 safety envelope.

N7 — QUORUM / TEMPORAL / THRESHOLD VETO

Not permitted in A27.

N8 — POSITIVE-FEEDBACK LOCK-IN

Not tested in A27.

INTERPRETATION

If H1 succeeds,
simple bounded negative correction
is sufficient to contain damage.

If H2 improves over H1,
error magnitude carries useful
corrective-control information
even though it failed as a predictive threshold in A26.

If H3 retains more beneficial trajectories
without reintroducing harm,
reversible homeostasis is useful.

If all controllers remain harmful,
feedback based only on matched service error
reacts too late or observes the wrong variable.

That would motivate richer homeostatic state
rather than threshold tuning.

PLAIN-SPEAK QUESTION

A24-A26 kept asking:

"can we be sure before we act?"

A27 accepts that sometimes we cannot.

So we let the patch control
three of four newborn cells.

Then every four steps
we compare the living result
with an old-policy twin.

If the new policy starts doing worse,
Yggdrasil turns its authority down.

One controller turns it down slowly.

One turns it down harder
when the error is bigger.

One can cautiously turn authority back up
if performance recovers.

Nobody gets full control.

Nobody rewrites cells that are already alive.

The patch is never deleted.

So A27 asks:

IF YGGDRASIL CANNOT PREDICT PERFECTLY,
CAN IT NOTICE THAT IT IS DRIFTING WRONG
AND CORRECT ITSELF FAST ENOUGH?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A27 NEGATIVE-FEEDBACK HOMEOSTATIC AUTHORITY CORRECTION

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F27-DERIVED TRAJECTORY,
FEEDBACK ERROR,
AUTHORITY UPDATE,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

0fd99b7ad6552252eaf8d068a09b8491f4bb4838.

SOURCE BUNDLE

Loader:

research/applications/track-a/a27_t8k_negative_feedback_homeostatic_v1.py

Loader Git blob:

b556c304885945380223d5a6d6efebc113638c0e.

Payload:

research/applications/track-a/a27_t8k_negative_feedback_homeostatic_v1.py.gz

Payload Git blob:

c9aa60e3188917dd71aa5c499af3fc32450b91b9.

Decompressed source SHA-256:

d7f97f2acd4e4cac1e8d1990ca4111e263d5942ebec9968b9ae2e803c4c655c3.

Decompressed source bytes:

17362.

Deterministic gzip SHA-256:

2811e1af86bd40af4387eb5d9f8e5dc05ac2a85d2660f64b01890c7a296da028.

Compressed payload bytes:

5243.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake freeze:

MECHANICAL-F27-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized result-file SHA-256:

10369829b58a815fb2a9dc7928b9ed158032d0b60b4e294fd6f0ba1f8eb745d3.

Serialized semantic output SHA-256:

bd47a797b31a063740bacb98e885aebde6d4049bf125d8e5982a0f879f3ebeae.

All P1-P19 integrity probes:

PASS.

Exact A17 replay:

3978 candidate first-four;
3950 stale first-four;
37 / 48 candidate >= stale;
exact 11 below-stale pairs reproduced.

MECHANICAL STATIC C3

Aggregate delta versus stale:

-59.

Harmful trajectories:

159 / 384;
41.41%.

Worst cumulative drawdown:

-11.

MECHANICAL H1

Aggregate delta versus stale:

+1.

Delta versus static C3:

+60.

Harmful trajectories:

163 / 384;
42.45%.

Static-harmful improved:

55.35%.

Static-beneficial retained:

85.47%.

Worst cumulative drawdown:

-12.

MECHANICAL H2

Aggregate delta versus stale:

+18.

Delta versus static C3:

+77.

Harmful trajectories:

166 / 384;
43.23%.

Static-harmful improved:

57.23%.

Static-beneficial retained:

84.88%.

Worst cumulative drawdown:

-8.

MECHANICAL H3

Aggregate delta versus stale:

-12.

Delta versus static C3:

+47.

Harmful trajectories:

169 / 384;
44.01%.

Static-harmful improved:

52.83%.

Static-beneficial retained:

84.88%.

Worst cumulative drawdown:

-12.

No controller qualified.

A27_HOMEOSTATIC_INFORMATION_GAIN:

FALSE

in the fake world.

This is NON-SCIENTIFIC mechanical evidence only.

It demonstrates that:

negative feedback can improve aggregate service
or worst drawdown
without necessarily reducing trajectory-level harm;

the homeostatic criteria are nontrivial;

and the implementation can legitimately return no qualifying controller.

REAL A27 STATUS

No real F27 trajectory has been derived.

No real feedback error has been observed.

No real authority update has been observed.

No real A27 manifest exists.

No real A27 outcome has been observed.

Let the resulting commit SHA be:

F27.

After F27 exists:

1. derive exactly 384 fresh 32-epoch trajectories from F27;
2. bind the complete manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. report R3 / H1 / H2 / H3 without post-result controller selection.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
