TITLE: LU-2L — FRESH L1 TASK-2 LEARNED-U TRANSFER
DATE: 2026-09-24
STATUS: PREREGISTERED / NO LU-2L WORLD DERIVED OR EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT LU-2K CLOSURE:
c6333ccf2fa9e3244feee66bf021cdc17924d145

PARENT LU2KF1:
441d90e9c39e0ed9444953937d90d585084b4c7b

PARENT LU-2G CLOSURE:
1fcfef885ca9bd8c3219333965d90cc9cc4a60e9

PARENT LU2GF1:
e9a01aa97587fc97dde073cb2a6a35ad141006cd

CANONICAL LU-1E WEIGHTS:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

PURPOSE

Answer the original LU-2G transfer question in the now-validated L1 Task-2 service environment.

SCIENTIFIC QUESTION

On ten fresh paired one-request-per-epoch Task-2 worlds, does the accepted
25-percent learned U-recruitment blend causally alter developmental
recruitment while preserving the validated exact-parent functional envelope?

ARMS

Exactly two arms:

U_A0:
exact V0.2 U recruitment.

U_A25:
P(U) = 0.75 * P_teacher(U) + 0.25 * P_learned(U).

H release remains exact teacher.
C/S stay-defect remains exact teacher.
FC/FS hard lifecycle remains exact teacher.

No retraining.
No optimizer.
No online adaptation.
No weight mutation.
No learned C/S authority.

TASK-2 ENVIRONMENT

Use the LU-2K validated L1 environment:

one request per epoch;
160 epochs;
five 32-epoch phases;
64-cell ring;
D2;
LOCAL_HEDGE;
ECHO_PHASE;
NO_POOL;
G5_FULL OFF;
request-bound handoff;
neutral sensing;
distributed lesion;
anchor relocation;
32-epoch inherited expiry.

Task computation remains exact LU-2G/LU-2K Task-2:

RAW -> SENSED -> PROCESSED_A -> PROCESSED_B -> ROUTING -> AT_EGRESS
-> VERIFIED -> DONE.

Verification failure enters REPAIR_PENDING, recomputes both stages from
immutable provenance, and requires independent re-verification.

OBSERVATION BOUNDARY

Learned U receives exactly OBS-V1.

No task program.
No stage id.
No request id.
No phase id.
No absolute position.
No global queue.
No evaluator correctness.
No future information.

COMMON RANDOMNESS

Within each paired world:

same manifest;
same programs;
same arrivals;
same corruption schedule;
same lesion;
same anchors;
same initial state;
same transition variates.

No learned-model RNG.

IMPLEMENTATION FREEZE

Create LU2LF1 before deriving any primary world.

No primary manifest may exist before LU2LF1.

FRESH WORLDS

Exactly 10 fresh paired worlds.

Namespace:

LU2L-TASK2-L1-LEARNED-U|LU2LF1|replicate

replicate 1..10.

Do not reuse LU-2G, LU-2I, or LU-2K worlds.

Bind all ten complete manifests before execution.
No world replacement.
No rejection sampling.
No result-dependent selection.

BASELINE FEASIBILITY

For each pair, U_A0 is baseline-feasible iff:

1. at least one correct DONE in every phase;
2. zero incorrect DONE;
3. both C and S produce correct DONE;
4. repair integrity passes;
5. finite operations per correct completion;
6. matching duplicate-cell and duplicate-request integrity pass.

At least 8 / 10 worlds must be baseline-feasible.

If fewer than 8 / 10 are feasible:

LU2L_L1_LEARNED_U_TRANSFER = FALSE

and interpret as failure of the fresh L1 baseline evidence coverage, not as
learned-U regression.

PAIRWISE PRESERVATION GATES

For every baseline-feasible pair require:

1. correct-completion area phases 0-4:
U_A25 >= 0.90 * U_A0;

2. median paired completion-area ratio:
>= 0.95;

3. final-16 backlog area:
U_A25 <= 1.25 * U_A0;

4. final backlog:
U_A25 <= 1.25 * U_A0;

5. operations per correct completion:
U_A25 <= 1.25 * U_A0;

6. stream noncollapse:
for each measured phase/stream where U_A0 has >=4 correct DONE,
U_A25 retains >=75 percent;

7. anchor-rotation recovery:
U_A25 no more than 8 epochs later than paired U_A0;

8. demand-reversal recovery:
U_A25 no more than 8 epochs later than paired U_A0;

9. lesion inherited criterion:
U_A25 lesion recovery <=8 epochs OR lesion backlog area <= paired U_A0;

10. incorrect DONE:
0;

11. repair integrity:
PASS;

12. matching integrity:
PASS.

CAUSALITY GATE

Across baseline-feasible worlds require:

U evaluations > 0;
teacher-vs-A25 U TV > 0;
at least one realized U transition differs under the shared variate.

H learned-vs-teacher delta must remain zero.

OVERALL SIGNAL

LU2L_L1_LEARNED_U_TRANSFER = TRUE iff:

- duplicate complete paired sweeps are byte-identical;
- at least 8 / 10 U_A0 worlds are baseline-feasible;
- causal learned-U participation is TRUE;
- every baseline-feasible pair passes every preservation gate;
- median paired completion-area ratio >= 0.95;
- no incorrect DONE occurs.

MECHANICAL GATE BEFORE LU2LF1

Prove:

1. exact LU-2K validated L1 environment semantics;
2. exact canonical LU-1E weight SHA;
3. U_A0 exact teacher one-step parity;
4. U_A25 exact 0.25 convex U blend;
5. H teacher exact;
6. C/S/FC/FS teacher exact;
7. OBS-V1 unchanged;
8. one request per epoch exact;
9. Task-2 stage order exact;
10. corruption / repair / reverify exact;
11. 32-epoch expiry exact;
12. common transition variates exact;
13. learned calls restricted to H/U;
14. no model RNG;
15. duplicate mechanical evidence byte-identical.

NO POST-RESULT TUNING

After LU2LF1 do not change:

alpha;
weights;
OBS-V1;
load;
expiry;
Task-2 computation;
corruption;
repair;
verification;
phase structure;
manifest count;
qualification bars;
world namespace;
or common-random policy.

NEXT STEP RULE

If TRUE:
run one fresh independent confirmation before considering any increase in
learned authority or task distance.

If FALSE with baseline coverage:
diagnose the narrowest pairwise failure without tuning the frozen experiment.

If FALSE for baseline coverage:
diagnose the exact-parent L1 failure before any learned-U conclusion.

PLAIN-SPEAK QUESTION

We finally have a fair two-step-task environment.

The hand-written parent passed ten of ten fresh L1 worlds.

Now we put the same 25-percent neural recruitment authority back in, but we
change nothing else.

If the neural recruiter actually makes different recruitment decisions and
the organism keeps the same throughput, backlog, repair, recovery, stream,
cost, and correctness envelope, then learned local developmental control has
generalized beyond Task-1 into a genuinely different compositional task.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
