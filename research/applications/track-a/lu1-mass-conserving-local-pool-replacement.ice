TITLE: LU-1 — Mass-Conserving Local Recruitment-Pool Replacement
DATE: 2026-09-23
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT

LU-0B closure:
c974b4def2973e72feec8b6be078c9255a0070d0.

LU0BF1:
3cbcb11042a177e76db8877a6e5d826aaa7aa9c7.

LU-0 closure:
074513c64a64318053fcbfcabdc9207202849063.

Developmental Substrate V0.1:
4d3887fba0478bc1ef3bc4bea44f8e08582f5803.

Task-1H strong confirmation:
1b848079ae0d54dd9e7b01c8d004a93b16aeb62d.

QUESTION

Can the organism-wide V0.1 recruitment pool:

pc;
ps;

be replaced by two bounded-local recurrent signal channels

without losing the useful developmental / task behavior
that V0.1 already demonstrated?

WHY THIS EXPERIMENT IS REQUIRED

LU-0 established:

exact strict-local identifiability of V0.1 is FALSE.

LU-0B established:

LU0B_DIRECTIONAL_POOL_PREVALENT = TRUE;

LU0B_RATE_POOL_PREVALENT = TRUE;

LU0B_POOL_PRACTICALLY_NEGLIGIBLE = FALSE.

Therefore the missing nonlocal information
is not a rare edge case.

A strictly local learned updater
must not be trained yet
against a teacher whose U recruitment
routinely depends on hidden organism-wide state.

LU-1 tests a local replacement first.

DESIGN PRINCIPLE

The replacement is a deterministic,
mass-conserving local diffusion process.

Every cell carries two recurrent signal channels:

R_C(i);

R_S(i).

These channels are updated
using only the cell's existing
radius-12 V0.1 neighborhood.

No global broadcast is supplied.

No central aggregation is supplied.

No cell reads:

global C count;

global S count;

global queue length;

global task throughput;

pc;

ps;

or any full-organism summary.

FROZEN CONSTANTS

N = 64.

D = 2.

R_TASK = 2.

LOCAL_R = 12.

POOL_DIFFUSION_R = LOCAL_R = 12.

RECRUIT_R = 3.

ETA = 1/2.

POOL_NORM = 160.

POOL_MEMORY = 3/4.

W_POOL = 3/4.

W_LOCAL = 1/4.

K_SUPP = 1/2.

N_SUPP = 3.

G5_FULL = OFF.

No new radius is introduced.

No tunable diffusion coefficient is introduced.

No learned parameter is introduced.

LOCAL INJECTION

At epoch t,
use the exact inherited Task-1 demand adapter:

d_C(i,t);

d_S(i,t).

Define exact committed-side local feedback:

f_C(i,t)
=
1
iff
state_i = C
and
d_C(i,t) >= d_S(i,t);

otherwise 0.

f_S(i,t)
=
1
iff
state_i = S
and
d_S(i,t) >= d_C(i,t);

otherwise 0.

Define local injections:

x_C(i,t)
=
d_C(i,t)
+
f_C(i,t);

x_S(i,t)
=
d_S(i,t)
+
f_S(i,t).

These are exactly the per-cell terms
whose organism-wide sums
feed the inherited global pool.

RECURRENT LOCAL SIGNAL

Initialize:

R_C(i,0) = 0;

R_S(i,0) = 0;

for every cell.

For every epoch,
use a synchronous pre-transition snapshot.

First define provisional values:

Z_C(j,t)
=
POOL_MEMORY * R_C(j,t)
+
(N / POOL_NORM) * x_C(j,t).

Z_S(j,t)
=
POOL_MEMORY * R_S(j,t)
+
(N / POOL_NORM) * x_S(j,t).

Because:

N / POOL_NORM
=
64 / 160
=
0.4,

this scale is frozen.

Then for each cell i:

R_C(i,t+1)
=
mean
Z_C(j,t)

over all j
whose ring distance from i
is <= LOCAL_R.

Likewise:

R_S(i,t+1)
=
mean
Z_S(j,t)

over ring distance <= LOCAL_R.

The closed radius-12 neighborhood
contains exactly 25 cells.

No sequential in-place update.

All cells read the same pre-update snapshot.

LOCAL READOUT

For U recruitment at cell i:

pc_local(i,t)
=
min(
1,
max(
0,
R_C(i,t+1)
)
).

ps_local(i,t)
=
min(
1,
max(
0,
R_S(i,t+1)
)
).

These local values replace only:

pc;
ps;

inside the exact inherited U-cell
C/S recruitment equations.

They do NOT change:

LOCAL_HEDGE H formation;

LOCAL_HEDGE H release;

B update;

ECHO_PHASE;

support-margin fields;

cooperative fields;

refractory behavior;

task demand adapter;

request lifecycle;

task scheduler;

VERIFY / REPAIR;

or task randomness.

MASS-CONSERVATION INVARIANT

The 64-cell ring is regular.

The radius-12 mean operator
is doubly stochastic.

Therefore:

mean_i R_C(i,t+1)
=
POOL_MEMORY * mean_i R_C(i,t)
+
sum_i x_C(i,t) / POOL_NORM.

And identically for S.

Starting from zero,
the network mean of the uncapped recurrent channel
tracks the exact inherited global pool
divided by POOL_NORM.

Thus LU-1 does not discard
the organism-level demand mass.

It redistributes the computation
of that mass through local recurrent communication.

This invariant is mechanical
and must hold to <= 1e-12
before the primary may execute.

IMPORTANT SCALE BOUNDARY

LU-1 tests N = 64 only.

The factor:

N / POOL_NORM

is a frozen implementation constant,
not a runtime global observation.

No population-size generalization claim
is authorized by LU-1.

A later scale audit is required
before claiming size-independent local pooling.

LESION SEMANTICS

The Task-1 functional lesion
continues to disable task operations only.

V0.1 internal developmental state updates continue.

Therefore the local R_C / R_S signal update
also continues through lesioned cells.

This matches the inherited rule
that developmental state remains active
during the functional task lesion.

PRIMARY ARMS

Exactly three:

1.
GLOBAL_POOL.

Exact V0.1 parent.

Use the inherited scalar:

C_pool;
S_pool;
pc;
ps;

unchanged.

2.
LOCAL_DIFFUSIVE_POOL.

Exact V0.1
except U recruitment receives:

pc_local(i);
ps_local(i)

from the recurrent local channels above.

No global pool value
may enter treatment dynamics.

3.
NO_POOL.

Exact V0.1
except U recruitment receives:

pc = 0;
ps = 0.

No other behavior changes.

PURPOSE OF NO_POOL CONTROL

LU-0B proved
the global pool changes recruitment distributions.

That does not itself prove
the pool improves task function.

NO_POOL distinguishes:

useful local replacement

from

simply deleting a nonlocal term.

FRESH WORLDS

Freeze the implementation as:

LU1F1.

Only after LU1F1 exists,
derive exactly five fresh worlds.

For k = 1..5:

replicate key
=
SHA1(
"LU1-LOCAL-POOL|"
+
LU1F1
+
"|"
+
k
).

Task seed
=
first 32 hex chars of:

SHA256(
"LU1-PRIMARY-SEED|"
+
LU1F1
+
"|"
+
k
).

Use the exact inherited Task-1 generators for:

four balanced nonconstant nonaffine programs;

320 arrivals;

5% stateless corruption;

distributed eight-cell lesion;

initial anchors;

+16 Phase-4 anchor relocation.

Bind all five manifests
before any primary arm executes.

No world may equal a Task-1F,
Task-1H,
or LU-0B primary manifest.

No sixth world.

PRIMARY DYNAMICS

All three arms preserve:

64 cells;

160 epochs;

D2;

G5_FULL OFF;

LOCAL_HEDGE;

ECHO_PHASE;

request-bound handoff;

neutral sensing;

one-op-per-cell;

one-op-per-request;

R_TASK = 2;

six-edge task route;

five 32-epoch phases;

same task programs;

same arrivals;

same corruption;

same lesion;

same anchors;

same stateless task randomness.

SIGNAL TELEMETRY

For LOCAL_DIFFUSIVE_POOL report per epoch:

network mean R_C;

network mean R_S;

exact external reference
C_pool / POOL_NORM;

exact external reference
S_pool / POOL_NORM;

absolute mean-conservation error
before readout clipping;

mean / median / p90
absolute cell deviation from
the global reference;

spatial standard deviation
of R_C and R_S;

fraction of cells
whose local readout saturates at 1;

fraction of cells
with pc_local > ps_local;

fraction with ps_local > pc_local;

fraction tied.

The external global reference
is telemetry only.

It may never feed
LOCAL_DIFFUSIVE_POOL dynamics.

MECHANISM-ACTIVITY TEST

LOCAL_DIFFUSIVE_POOL is active iff
in every primary world:

1.
some epoch has
spatial std(R_C) > 1e-12
or
spatial std(R_S) > 1e-12;

2.
some U recruitment evaluation
uses a local pool value
different from the contemporaneous
global scalar by > 1e-12;

3.
the network mean-conservation invariant
still passes.

FUNCTIONAL METRICS

For every arm/world report:

arrivals;

correct DONE;

incorrect DONE;

expired;

unfinished final backlog;

completion fraction by phase;

correct completion by phase;

Phase-4 final-16
correct-completion rate;

final-16 backlog area;

operations per correct completion;

median latency;

p90 latency;

demand-reversal recovery latency;

lesion recovery latency;

lesion backlog area;

anchor-rotation recovery latency;

new Phase-4 C correct completions;

new Phase-4 S correct completions.

PARENT-PRESERVATION METRICS

For each world define:

phase4_gap_to_global
=
LOCAL_DIFFUSIVE_POOL Phase-4 final-16 completion
-
GLOBAL_POOL Phase-4 final-16 completion.

Define:

post_phase0_correct_ratio
=
LOCAL_DIFFUSIVE_POOL correct DONE
during phases 1..4
/
GLOBAL_POOL correct DONE
during phases 1..4,

when the parent denominator is positive.

NO-POOL CAUSAL METRICS

For each world define:

phase4_gain_over_no_pool
=
LOCAL_DIFFUSIVE_POOL Phase-4 final-16 completion
-
NO_POOL Phase-4 final-16 completion.

Define final-window backlog reduction:

(
NO_POOL final-16 backlog area
-
LOCAL_DIFFUSIVE_POOL final-16 backlog area
)
/
NO_POOL final-16 backlog area

when the denominator is positive.

Define:

post_phase0_correct_gain
=
LOCAL_DIFFUSIVE_POOL phases-1..4 correct DONE
-
NO_POOL phases-1..4 correct DONE.

LOCAL REPLACEMENT FUNCTIONALITY

LU1_LOCAL_POOL_FUNCTIONAL = TRUE iff all are true:

1.
mechanism active
in all five worlds;

2.
network mean-conservation error
<= 1e-12
for C and S
at every epoch
in every treatment world;

3.
all parent/runtime integrity probes pass;

4.
Phase-0 LOCAL_DIFFUSIVE_POOL completion
>= 95% of GLOBAL_POOL
in every world;

5.
LOCAL_DIFFUSIVE_POOL
Phase-4 final-16 completion
>= 85%
in at least 4 of 5 worlds;

6.
median LOCAL_DIFFUSIVE_POOL
Phase-4 final-16 completion
>= 85%;

7.
phase4_gap_to_global
>= -0.10
in at least 4 of 5 worlds;

8.
median phase4_gap_to_global
>= -0.05;

9.
post_phase0_correct_ratio
>= 0.90
in at least 4 of 5 worlds;

10.
anchor-rotation recovery
<= 8 epochs
in at least 4 of 5 worlds;

11.
demand-reversal recovery
<= 8 epochs
in all five worlds;

12.
the inherited lesion recovery criterion
passes in all five worlds;

13.
incorrect DONE = 0
in every treatment world;

14.
operations per correct completion
<= 125% of GLOBAL_POOL
in every world.

LOCAL REPLACEMENT CAUSAL VALUE

LU1_LOCAL_POOL_CAUSAL_VALUE = TRUE iff:

LU1_LOCAL_POOL_FUNCTIONAL = TRUE

and all are true:

1.
phase4_gain_over_no_pool > 0
in at least 4 of 5 worlds;

2.
median phase4_gain_over_no_pool
>= 0.10;

3.
LOCAL_DIFFUSIVE_POOL final-16 backlog area
is lower than NO_POOL
in at least 4 of 5 worlds;

4.
median final-window backlog reduction
relative to NO_POOL
>= 0.15;

5.
post_phase0_correct_gain > 0
in at least 4 of 5 worlds.

LU-1 QUALIFICATION

LU1_LOCAL_POOL_REPLACEMENT_QUALIFIED = TRUE iff:

LU1_LOCAL_POOL_FUNCTIONAL = TRUE

and

LU1_LOCAL_POOL_CAUSAL_VALUE = TRUE.

NO-POOL SUFFICIENCY DIAGNOSTIC

LU1_NO_POOL_FUNCTIONALLY_SUFFICIENT = TRUE iff all are true:

1.
NO_POOL Phase-0 completion
>= 95% of GLOBAL_POOL
in every world;

2.
NO_POOL Phase-4 final-16 completion
>= 85%
in at least 4 of 5 worlds;

3.
median NO_POOL Phase-4 final-16 completion
>= 85%;

4.
NO_POOL demand-reversal recovery
<= 8 epochs
in all five;

5.
NO_POOL lesion criterion
passes all five;

6.
NO_POOL anchor recovery
<= 8 epochs
in at least 4 of 5;

7.
incorrect DONE = 0
in every NO_POOL world;

8.
NO_POOL operation cost
<= 125% of GLOBAL_POOL
in every world.

This diagnostic does not authorize deletion by itself.

It identifies whether
a simpler pool-removal confirmation
would be justified.

MECHANICAL GATE

Before LU1F1 prove:

1.
exact GLOBAL_POOL parity
with frozen V0.1 / Task-1F LOCAL_HEDGE
on the mechanical world;

2.
LOCAL_DIFFUSIVE_POOL differs
only in the U-recruitment pool source
plus its two recurrent signal channels;

3.
NO_POOL differs
only by pc = ps = 0
inside U recruitment;

4.
LOCAL_DIFFUSIVE_POOL dynamics
never read the global reference pool;

5.
radius = 12 exactly;

6.
closed neighborhood count = 25;

7.
synchronous snapshot update;

8.
local injection equals
the exact decomposed parent
demand + committed feedback terms;

9.
mass-conservation invariant
<= 1e-12
through the mechanical trajectory;

10.
LOCAL_HEDGE exact;

11.
ECHO_PHASE exact;

12.
Task-1 mechanics exact;

13.
one-op invariants pass;

14.
incorrect DONE = 0;

15.
primary generator frozen
but no real LU1F1 manifest yet derived;

16.
two complete mechanical runs
byte-identical.

FREEZE DISCIPLINE

Freeze exact implementation as:

LU1F1.

Then:

derive five fresh manifests;

bind all five;

run two complete
three-arm five-world sweeps;

require byte identity;

open scientific outcomes only afterward.

NO POST-RESULT TUNING

Do not change after primary begins:

POOL_DIFFUSION_R;

POOL_MEMORY;

N / POOL_NORM scale;

neighborhood operator;

injection law;

clipping;

number of local channels;

five-world count;

world derivation;

Task-1 workload;

D family;

G5 status;

LOCAL_HEDGE;

ECHO_PHASE;

functional thresholds;

causal-value thresholds;

or interpretation rules.

FAILURE ATTRIBUTION

If mass conservation fails:

implementation defect.

Do not interpret scientifically.

If LOCAL_DIFFUSIVE_POOL is functionally weak
and local/global signal deviation is large:

bounded diffusion latency / spatial lag
is the supported diagnosis.

Do not tune radius or mixing strength inside LU-1.

If LOCAL_DIFFUSIVE_POOL is functional
but causal value versus NO_POOL fails:

the local replacement may be unnecessary
for Task-1 function.

A separately preregistered
NO_POOL simplification confirmation
is justified before any architecture change.

If NO_POOL is not sufficient
but LOCAL_DIFFUSIVE_POOL qualifies:

the global-pool function is useful
and can be supplied locally.

Require an independent confirmation
before promoting the replacement
into a new Developmental Substrate version.

If LOCAL_DIFFUSIVE_POOL qualifies:

do not begin learned-updater training
until that independent confirmation closes.

After confirmation,
the local recurrent channels
become candidate hidden-state inputs
for the learned shared per-cell updater.

If LOCAL_DIFFUSIVE_POOL fails:

do not expose pc/ps permanently
to the neural updater by default.

Diagnose the local communication failure first.

PLAIN-SPEAK QUESTION

The old organism asks a central question:

"How much C work and S work
exists across the whole body?"

Every cell gets that answer instantly.

That breaks the strict-local contract.

LU-1 replaces that broadcast
with two signals
that physically spread through neighboring cells.

Each cell adds
what it sees locally.

Then every epoch,
neighbors average their stored signal.

Because the averaging is balanced,
the organism as a whole
still preserves the same total demand mass.

But no individual cell
gets a magic global number.

We compare three organisms:

the old global broadcast;

the new locally spreading signal;

and no pool signal at all.

If the local signal keeps the organism useful
and clearly beats deleting the signal,
then we have a path
to a genuinely local neural cell brain.

If simply deleting the pool works just as well,
we test that simpler answer instead.

If local diffusion cannot keep up,
we learn that before training a neural network.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
