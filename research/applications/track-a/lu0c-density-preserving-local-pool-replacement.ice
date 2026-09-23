TITLE: LU-0C — Density-Preserving Local Recruitment-Pool Replacement
DATE: 2026-09-23
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT

Developmental Substrate V0.1:
4d3887fba0478bc1ef3bc4bea44f8e08582f5803.

LU-0 closure:
074513c64a64318053fcbfcabdc9207202849063.

LU-0B closure:
c974b4def2973e72feec8b6be078c9255a0070d0.

Task-1H strong confirmation:
1b848079ae0d54dd9e7b01c8d004a93b16aeb62d.

QUESTION

Can the organism-wide C/S recruitment pools:

pc;
ps;

be replaced by a strictly local,
density-preserving recurrent signal

without materially losing
the useful V0.1 task behavior
that LOCAL_HEDGE established?

SCIENTIFIC MOTIVATION

LU-0 proved
exact strict-local identifiability is false
for the current V0.1 teacher.

LU-0B then proved
the nonlocal dependency is prevalent
during natural V0.1 trajectories:

median-world fraction
TV_side >= 0.05:
approximately 94.83%;

median-world fraction
R_rate >= 0.10:
approximately 98.93%;

C/S side flips:
all five worlds;

pooled side-flip fraction:
approximately 7.72%.

Therefore strict-local neural-updater training
must not begin against the unchanged
global-pool teacher.

LU-0C tests whether
the global recruitment-pool function itself
can be localized first.

NO LEARNED MODEL YET

LU-0C trains no neural network.

It changes only
the source of the C/S recruitment-pool term.

All other V0.1 and Task-1 mechanics
remain frozen.

PRIMARY ARMS

Exactly three:

GLOBAL_POOL_PARENT;

LOCAL_POOL_R12;

NO_POOL.

All three use:

V0.1 LOCAL_HEDGE;

A45 ECHO_PHASE;

D2;

G5_FULL OFF;

the same 64-cell ring;

the same requests;

the same stateless random namespaces;

the same lesions;

the same anchors;

the same request-bound handoff;

the same neutral sensing;

the same scheduler;

the same VERIFY / REPAIR lifecycle.

GLOBAL_POOL_PARENT

Exact frozen V0.1 / Task-1F R1 LOCAL_HEDGE behavior.

The inherited global pool is:

C_pool'
=
0.75 * C_pool
+
sum_j d_C(j)
+
fb_C;

S_pool'
=
0.75 * S_pool
+
sum_j d_S(j)
+
fb_S;

pc
=
min(1, C_pool' / 160);

ps
=
min(1, S_pool' / 160).

This is the paired parent baseline.

LOCAL_POOL_R12

Replace only
the organism-wide recruitment pool
with one local recurrent C/S pool pair
per cell position.

The local-pool radius is exactly:

R_LOCAL_POOL = 12.

This is not a new tuned radius.

It is the already-frozen V0/V0.1
local evidence radius.

For each cell i,
define the existing radius-12 ring window:

W_i
=
{j : ring_distance(i,j) <= 12}.

Window size:

|W_i| = 25.

LOCAL COMMITTED FEEDBACK

For each cell i:

fb_C_i
=
count of j in W_i
such that:

state_j = C

and

d_C(j) >= d_S(j).

Similarly:

fb_S_i
=
count of j in W_i
such that:

state_j = S

and

d_S(j) >= d_C(j).

LOCAL RAW INPUT

raw_C_i
=
sum over j in W_i d_C(j)
+
fb_C_i.

raw_S_i
=
sum over j in W_i d_S(j)
+
fb_S_i.

LOCAL RECURRENT POOLS

Each cell position carries:

C_pool_i;
S_pool_i.

Initial values:

0;
0.

Update every epoch:

C_pool_i'
=
0.75 * C_pool_i
+
raw_C_i;

S_pool_i'
=
0.75 * S_pool_i
+
raw_S_i.

No diffusion.

No global averaging.

No neighbor-pool read.

Only the cell's prior local-pool state
and its current radius-12 local window
enter the recurrence.

DENSITY-PRESERVING NORMALIZATION

Do not introduce a fitted normalization.

Scale the inherited global denominator
by the fraction of the organism
visible in the local window:

LOCAL_POOL_NORM
=
POOL_NORM
*
|W_i| / N.

With frozen values:

160 * 25 / 64
=
62.5.

Then:

pc_i
=
min(1, C_pool_i' / 62.5);

ps_i
=
min(1, S_pool_i' / 62.5).

This is the only normalization.

No coefficient sweep is authorized.

LOCAL C/S RECRUITMENT

For U cell i,
replace parent scalar pc/ps only here:

sup_C_i
=
W_POOL * pc_i
+
W_LOCAL * L_C3(i);

sup_S_i
=
W_POOL * ps_i
+
W_LOCAL * L_S3(i);

opp_C_i
=
W_POOL * ps_i
+
W_LOCAL * L_S3(i);

opp_S_i
=
W_POOL * pc_i
+
W_LOCAL * L_C3(i).

Preserve exactly:

W_POOL = 3/4;

W_LOCAL = 1/4;

K_SUPP = 1/2;

N_SUPP = 3;

ETA = 1/2;

support_margin_field;

g_C;

g_S;

lambda_C;

lambda_S.

LOCAL_HEDGE H formation and release
remain exactly V0.1.

ECHO_PHASE remains exactly V0.1.

NO_POOL

Delete only the recruitment-pool contribution.

For U C/S recruitment:

pc_i = 0;

ps_i = 0.

Therefore:

sup_C
=
W_LOCAL * L_C3;

sup_S
=
W_LOCAL * L_S3;

opp_C
=
W_LOCAL * L_S3;

opp_S
=
W_LOCAL * L_C3.

Preserve all remaining equations exactly.

NO_POOL exists to answer:

is a local pool actually useful,

or can the global pool
simply be removed?

STRICT LOCALITY CONTRACT

LOCAL_POOL_R12 may read only:

the cell's prior local C/S pool state;

current cell states
within ring radius 12;

current d_C/d_S
within ring radius 12;

the already-frozen local evidence fields;

and the same local state
used by V0.1.

It may not read:

global C/S counts;

sum over all d_C/d_S;

global queue length;

global task throughput;

global majority;

phase identity;

future requests;

future lesion;

future anchor positions;

or GLOBAL_POOL_PARENT pc/ps.

NO_POOL may read no global recruitment-pool signal.

COMMON RANDOMNESS

Use identical:

seed;

epoch;

cell position;

state transition salt;

request randomness;

corruption schedule;

and task randomness

for all three paired arms.

No treatment-specific random namespace.

LOCAL POOL STATE STATUS

C_pool_i / S_pool_i are
developmental recurrent state,
not task-state shortcuts.

They are tied to cell positions
and updated every epoch.

They contain no:

task id;

request id;

phase id;

future information;

global score;

or target label.

They are candidate future
per-cell neural-state channels.

FRESH PRIMARY WORLDS

Freeze implementation as LU0CF1.

Only after LU0CF1 exists,
derive exactly five fresh worlds.

For k = 1..5:

replicate key =
SHA1(
"LU0C-LOCAL-POOL|"
+
LU0CF1
+
"|"
+
k
).

task seed =
first 32 hex chars of:

SHA256(
"LU0C-PRIMARY-SEED|"
+
LU0CF1
+
"|"
+
k
).

Use the exact inherited Task-1 generators.

Bind all five manifests
before any primary arm executes.

PRIMARY METRICS

For every arm/world report
the existing Task-1 metrics,
including:

Phase-0 completion;

Phase-4 final-window completion;

correct-completion area Phases 1-4;

final-16 total backlog area;

anchor-rotation recovery;

demand-reversal recovery;

lesion recovery;

incorrect DONE;

operations per correct completion;

final backlog;

new Phase-4 S correct completions.

LOCAL_POOL_R12 TELEMETRY

Report:

mean pc_i;

mean ps_i;

median pc_i;

median ps_i;

mean spatial standard deviation pc_i;

mean spatial standard deviation ps_i;

fraction pc_i saturated at 1;

fraction ps_i saturated at 1;

number of epochs with nonzero
spatial variance in either pool;

number of U recruitment evaluations
using LOCAL_POOL_R12.

This telemetry may not alter dynamics.

LOCAL-POOL PRESERVATION GATE

LU0C_LOCAL_POOL_PRESERVES_V01 = TRUE iff all are true:

1. LOCAL_POOL_R12 mechanism active
   in all five worlds;

2. all locality and runtime integrity probes pass;

3. Phase-0 completion
   is at least 95% of GLOBAL_POOL_PARENT
   in every world;

4. Phase-4 final-window completion
   is at least 85%
   in at least 4 of 5 worlds;

5. median LOCAL_POOL_R12
   Phase-4 final-window completion
   is at least 85%;

6. LOCAL_POOL_R12 Phase-4 final-window completion
   is no more than 10 percentage points
   below paired GLOBAL_POOL_PARENT
   in at least 4 of 5 worlds;

7. median paired Phase-4 delta
   LOCAL minus GLOBAL
   is at least -5 percentage points;

8. correct-completion area across Phases 1-4
   is at least 90% of paired GLOBAL_POOL_PARENT
   in at least 4 of 5 worlds;

9. median paired Phases-1-4
   correct-completion-area ratio
   is at least 95%;

10. final-16 total backlog area
    is no more than 125%
    of paired GLOBAL_POOL_PARENT
    in at least 4 of 5 worlds;

11. anchor-rotation recovery <=8 epochs
    in at least 4 of 5 worlds;

12. demand-reversal recovery <=8 epochs
    in all five worlds;

13. lesion criterion passes
    in all five worlds;

14. incorrect DONE = 0
    in all five worlds;

15. operations per correct completion
    <=125% of paired GLOBAL_POOL_PARENT
    in all five worlds.

NO-POOL SIMPLIFICATION GATE

LU0C_NO_POOL_SIMPLIFICATION_VIABLE = TRUE iff
NO_POOL independently satisfies
the same preservation conditions 3 through 15
against GLOBAL_POOL_PARENT.

This is intentionally stringent.

If simply deleting the global pool
preserves the behavior,
do not retain a more complex local mechanism
without evidence.

LOCAL POOL VALUE OVER NO POOL

LU0C_LOCAL_POOL_ADDS_VALUE_OVER_NO_POOL = TRUE iff all are true:

1. LOCAL_POOL_R12 Phase-4 final-window completion
   is at least NO_POOL
   in at least 4 of 5 worlds;

2. median paired
   LOCAL_POOL_R12 minus NO_POOL
   Phase-4 gain
   is at least +5 percentage points;

3. LOCAL_POOL_R12 final-16 backlog area
   is lower than NO_POOL
   in at least 4 of 5 worlds;

4. median paired backlog reduction
   versus NO_POOL
   is at least 10%.

INTERPRETATION

CASE A

If:

LOCAL_POOL_PRESERVES_V01 = TRUE

and:

LOCAL_POOL_ADDS_VALUE_OVER_NO_POOL = TRUE

and:

NO_POOL_SIMPLIFICATION_VIABLE = FALSE

then:

the density-preserving local recurrent pool
is a viable replacement candidate.

Do not promote immediately.

Run one independent five-world confirmation
before V0.2.

CASE B

If:

NO_POOL_SIMPLIFICATION_VIABLE = TRUE

then:

the simpler removal of pc/ps
is a viable candidate.

Do not prefer LOCAL_POOL_R12
merely because it is biologically attractive.

Run a fresh confirmation
of NO_POOL before V0.2.

CASE C

If:

LOCAL_POOL_PRESERVES_V01 = FALSE

and:

NO_POOL_SIMPLIFICATION_VIABLE = FALSE

then:

neither this first local recurrence
nor deletion preserves V0.1 sufficiently.

Do not tune the 62.5 normalization
inside LU-0C.

The next experiment must test
a qualitatively different local communication mechanism,
such as bounded neighbor propagation,
or explicitly compare
STRICT_LOCAL versus LOCAL_PLUS_GLOBAL_POOL
at the learned-student stage.

CASE D

Any other combination:

INTERMEDIATE.

Do not promote.

Use the observed failure axis
to preregister the next narrow experiment.

MECHANICAL GATE

Before LU0CF1 prove:

1. GLOBAL_POOL_PARENT
   exact Task-1F R1 LOCAL_HEDGE parity;

2. LOCAL_POOL_R12 differs only
   in the recruitment-pool source/state;

3. NO_POOL differs only
   by deleting the recruitment-pool contribution;

4. LOCAL_POOL_NORM = 62.5 exactly;

5. local window size = 25 exactly;

6. local pool initial state = 0;

7. local pool recurrence rho = 0.75 exactly;

8. no global demand/count read
   enters LOCAL_POOL_R12 dynamics;

9. no global demand/count read
   enters NO_POOL dynamics;

10. LOCAL_HEDGE exact V0.1 semantics;

11. ECHO_PHASE exact V0.1 semantics;

12. D2 / G5 OFF / N64 / R_TASK2;

13. one-operation cell/request invariants;

14. common random-number contract;

15. two complete mechanical sweeps
    byte-identically.

PRIMARY DISCIPLINE

After LU0CF1:

derive all five manifests;

bind them before execution;

run two complete
five-world x three-arm sweeps;

require byte identity;

then open results.

NO POST-RESULT TUNING

Do not change:

R_LOCAL_POOL;

62.5 normalization;

pool rho;

W_POOL;

W_LOCAL;

support-margin semantics;

LOCAL_HEDGE;

ECHO_PHASE;

manifest count;

fresh-world namespaces;

Task-1 load;

phase lengths;

anchor rotation;

lesion;

expiry;

scheduler;

success thresholds;

or interpretation rules

after execution.

PLAIN-SPEAK QUESTION

We now know
the organism's global recruitment signal
matters all the time.

So we are replacing it
with the most literal local version possible.

Each cell gets two tiny memories:

"how much C-type pressure
has MY neighborhood recently had?"

and

"how much S-type pressure
has MY neighborhood recently had?"

They use the same decay rule
as the old organism-wide pool.

The normalization is scaled
only by how much of the ring
the cell can actually see.

We compare that against:

the original global signal;

and simply deleting the signal.

If the local memory preserves behavior
and deletion does not,
we have removed a real nonlocal dependency
without sacrificing the organism.

That would clear the information boundary
for the first genuinely local learned cell updater.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
