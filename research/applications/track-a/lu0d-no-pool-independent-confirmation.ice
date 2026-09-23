TITLE: LU-0D — INDEPENDENT NO_POOL CONFIRMATION
DATE: 2026-09-23
STATUS: PREREGISTERED / NO PRIMARY EXECUTION
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Independently test whether the LU-0C NO_POOL result
replicates on five newly derived Task-1 worlds.

LU-0C established:

LU0C_NO_POOL_SIMPLIFICATION_VIABLE = TRUE;

LU0C_LOCAL_POOL_PRESERVES_V01 = FALSE;

LU0C_LOCAL_POOL_ADDS_VALUE_OVER_NO_POOL = FALSE.

The present experiment does not search for a better local pool.

It asks only:

can the global recruitment-pool contribution
be removed again
without materially degrading
the already-validated V0.1 functional envelope?

PARENT ARCHITECTURE

Developmental Substrate V0.1:

4d3887fba0478bc1ef3bc4bea44f8e08582f5803.

Task-1H confirmation closure:

1b848079ae0d54dd9e7b01c8d004a93b16aeb62d.

LU-0C closure:

2356cdb49171a1144c3f56a28ba9d29a47f42796.

PARENT IMPLEMENTATION

Use the exact frozen LU0CF1 implementation:

872509a6da0935e791f458eca42d0d8741c9e200.

The LU-0D implementation may wrap LU0CF1
but may not reimplement or modify
the developmental dynamics.

ARMS

Exactly two:

GLOBAL_POOL_PARENT;

NO_POOL.

GLOBAL_POOL_PARENT

Exact LU0CF1 GLOBAL_POOL_PARENT behavior.

This is the frozen Developmental Substrate V0.1
recruitment-pool behavior used in LU-0C.

NO_POOL

Exact LU0CF1 NO_POOL behavior.

Delete only the C/S recruitment-pool contribution:

pc_i = 0;

ps_i = 0.

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

lambda_S;

LOCAL_HEDGE;

ECHO_PHASE;

all task mechanics;

and all safety/integrity semantics.

NO_POOL does not create
a replacement local recurrent state.

STRICT BOUNDARY

No change to:

C/S/U/H/FC/FS state semantics;

LOCAL_HEDGE equations;

ECHO_PHASE;

B accumulation;

evidence radius;

recruitment radius;

D2;

G5_FULL OFF;

N = 64;

R_TASK = 2;

request-bound handoff;

neutral sensing;

scheduler;

expiry;

five-phase schedule;

anchor relocation;

lesion;

truth-table programs;

corruption semantics;

repair;

verification;

or operation accounting.

No new global read.

No new local state.

No new RNG namespace for treatment dynamics.

COMMON RANDOMNESS

Within each paired world use identical:

programs;

arrivals;

corruption schedule;

lesion;

anchors;

seed;

epoch;

cell;

request randomness;

state-transition salt;

and task randomness.

Only the recruitment-pool contribution differs.

FRESH-WORLD DERIVATION

Freeze implementation as:

LU0DF1.

Only after LU0DF1 exists
derive exactly five fresh primary worlds.

For k = 1..5:

replicate_key =
SHA1(
"LU0D-NO-POOL-CONFIRM|"
+
LU0DF1
+
"|"
+
k
).

task seed =
first 32 hex characters of:

SHA256(
"LU0D-PRIMARY-SEED|"
+
LU0DF1
+
"|"
+
k
).

Use the exact inherited Task-1 generators.

Bind all five manifests
before any primary arm executes.

The five LU-0D manifest identities
must be distinct from all bound manifests from:

Task-1F R1;

Task-1H;

LU-0B;

LU-0C.

PRIMARY METRICS

For every arm/world report at minimum:

Phase-0 completion;

Phase-4 final-window completion;

correct-completion area Phases 1-4;

final-16 total backlog area;

anchor-rotation recovery latency;

demand-reversal recovery latency;

lesion recovery / lesion backlog criterion;

incorrect DONE;

operations per correct completion;

final backlog if exposed by the frozen parent;

new Phase-4 S correct completions;

and all inherited integrity probes.

CONFIRMATION GATE

LU0D_NO_POOL_CONFIRMED = TRUE iff all are true:

1. parent GLOBAL_POOL_PARENT exact LU0CF1 parity;

2. NO_POOL exact LU0CF1 NO_POOL parity;

3. all common-randomness, locality, and runtime integrity probes pass
   in all five worlds;

4. Phase-0 NO_POOL completion
   is at least 95% of paired GLOBAL_POOL_PARENT
   in every world;

5. NO_POOL Phase-4 final-window completion
   is at least 85%
   in at least 4 of 5 worlds;

6. median NO_POOL Phase-4 final-window completion
   is at least 85%;

7. NO_POOL Phase-4 final-window completion
   is no more than 10 percentage points
   below paired GLOBAL_POOL_PARENT
   in at least 4 of 5 worlds;

8. median paired Phase-4 delta
   NO_POOL minus GLOBAL_POOL_PARENT
   is at least -5 percentage points;

9. correct-completion area across Phases 1-4
   is at least 90% of paired GLOBAL_POOL_PARENT
   in at least 4 of 5 worlds;

10. median paired Phases-1-4
    correct-completion-area ratio
    is at least 95%;

11. final-16 total backlog area
    is no more than 125%
    of paired GLOBAL_POOL_PARENT
    in at least 4 of 5 worlds;

12. anchor-rotation recovery <=8 epochs
    in at least 4 of 5 worlds;

13. demand-reversal recovery <=8 epochs
    in all five worlds;

14. lesion criterion passes
    in all five worlds;

15. incorrect DONE = 0
    in all five worlds;

16. operations per correct completion
    <=125% of paired GLOBAL_POOL_PARENT
    in all five worlds.

The confirmation gate intentionally repeats
the LU-0C NO_POOL preservation envelope.

Do not weaken it
because LU-0C already passed.

ARCHITECTURE DECISION RULE

If:

LU0D_NO_POOL_CONFIRMED = TRUE

then:

the NO_POOL simplification has passed
two independent five-world sets.

A separate architecture record may then propose:

Developmental Substrate V0.2

with the global C/S recruitment-pool contribution removed.

That architecture decision must not silently alter
any other V0.1 mechanism.

If:

LU0D_NO_POOL_CONFIRMED = FALSE

then:

do not remove the global pool from V0.1.

Use the observed failure axis
to determine whether:

the LU-0C result was world-sensitive;

a bounded local communication mechanism
is needed;

or the first learned updater must retain
a separately supplied global-pool channel.

No post-result threshold tuning.

MECHANICAL GATE

Before LU0DF1 prove:

1. GLOBAL_POOL_PARENT exact LU0CF1 parity;

2. NO_POOL exact LU0CF1 parity;

3. no developmental dynamics reimplemented;

4. only the two preregistered arms exist;

5. D2;

6. G5_FULL OFF;

7. N64;

8. R_TASK2;

9. LOCAL_HEDGE exact V0.1 semantics;

10. ECHO_PHASE exact V0.1 semantics;

11. request-bound handoff preserved;

12. one operation per cell;

13. one operation per request;

14. incorrect DONE = 0;

15. common-random-number contract;

16. five-manifest generator JSON roundtrip;

17. two complete mechanical invocations byte-identically.

PRIMARY DISCIPLINE

After LU0DF1:

derive exactly five fresh manifests;

bind all five before execution;

run two complete
five-world x two-arm sweeps;

require byte identity;

then open the result.

NO POST-RESULT TUNING

Do not change:

the NO_POOL equation;

W_POOL;

W_LOCAL;

support-margin semantics;

LOCAL_HEDGE;

ECHO_PHASE;

D family;

G5 status;

task load;

manifest count;

seed namespace;

phase duration;

anchor rotation;

lesion;

expiry;

scheduler;

success thresholds;

or interpretation rules
after primary execution begins.

PLAIN-SPEAK QUESTION

The last experiment gave us a surprising answer:

the organism may not need
its global recruitment signal at all.

That is important enough
that we should not trust one set of worlds.

So this experiment does nothing clever.

We take the current organism.

We make one copy
with the old global recruitment signal.

We make one copy
with that signal removed.

Then we give both copies
five completely new worlds.

If the simpler organism
again keeps up with the old one,
survives the move,
survives demand reversal,
survives damage,
stays correct,
and does not spend extra work,
then deletion has earned a second independent pass.

Only then should we change the substrate.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
