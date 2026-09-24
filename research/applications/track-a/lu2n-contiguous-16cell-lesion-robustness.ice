TITLE: LU-2N — CONTIGUOUS 16-CELL LESION ROBUSTNESS
DATE: 2026-09-24
STATUS: PREREGISTERED / NO LU-2N PRIMARY WORLD DERIVED OR EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT LU-2M CLOSURE:
240e4cd49056a9ec2f80fe66e6e5decca1799be2

PARENT LU2MF1:
e05168e6452f81cad45474ed0984fe4970762456

PARENT LU-2L CLOSURE:
ed618450559eb8275557108f758c61949e030653

CANONICAL LU-1E WEIGHTS:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

PURPOSE

Change perturbation structure after qualified doubled distributed-lesion
robustness while holding perturbation size, duration, Task-2 load, and
learned authority fixed.

SCIENTIFIC QUESTION

Does the accepted 25-percent learned U-recruitment authority remain causally
active and functionally contained when the same 16-cell, 12-epoch lesion is
concentrated into one contiguous region instead of distributed around the
64-cell ring?

ARMS

U_A0:
exact V0.2 U recruitment.

U_A25:
0.75 * exact teacher U + 0.25 * frozen learned U.

H release:
exact teacher.

C/S stay-defect:
exact teacher.

FC/FS lifecycle:
exact teacher.

No retraining.
No optimizer.
No online adaptation.
No weight mutation.
No authority increase.

TASK ENVIRONMENT

Retain exact LU-2M / LU-2L L1 Task-2 semantics:

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
anchor relocation;
32-epoch expiry;
two-stage Task-2 computation;
same corruption, repair, verification and mandatory re-verification.

PERTURBATION CHANGE — STRUCTURE ONLY

Lesion onset:
epoch 96 inclusive.

Lesion end:
epoch 108 exclusive.

Duration:
12 epochs.

Lesion cardinality:
16 cells.

Let:

k = h64("TASK1-LESION-OFFSET", seed) mod 8.

LU-2N contiguous lesion:

{ (k + j) mod 64 : j = 0..15 }.

Required properties:

exactly 16 distinct cells;
one contiguous ring interval of length 16;
same seed-derived base offset family as inherited lesion;
same 12-epoch lesion duration;
same 25-percent ring footprint as LU-2M;
not the LU-2M interleaved distributed 16-cell pattern;
no load change;
no expiry change;
no corruption change;
no task-program change.

OBSERVATION BOUNDARY

Learned U receives exactly OBS-V1.

No lesion flag.
No lesion size.
No lesion geometry.
No task program.
No stage id.
No phase id.
No absolute position.
No global queue.
No evaluator correctness.
No future information.

COMMON RANDOMNESS

Within each paired world:

same manifest;
same contiguous lesion;
same programs;
same arrivals;
same corruption;
same anchors;
same initial developmental state;
same transition variates.

No learned-model RNG.

IMPLEMENTATION FREEZE

Create LU2NF1 before deriving any LU-2N primary world.

No primary manifest may exist before LU2NF1.

FRESH PRIMARY WORLDS

Exactly 10 fresh paired worlds.

Namespace:

LU2N-TASK2-L1-CONTIG16|LU2NF1|replicate

replicate 1..10.

Do not reuse any LU-2G/LU-2I/LU-2K/LU-2L/LU-2M world.

Bind all ten complete manifests before any primary arm executes.

No replacement.
No rejection sampling.
No result-dependent selection.

BASELINE FEASIBILITY

U_A0 is baseline-feasible iff:

1. at least one correct DONE in every phase;
2. zero incorrect DONE;
3. both C and S produce correct DONE;
4. repair integrity passes;
5. finite operations per correct completion;
6. matching duplicate-cell and duplicate-request integrity pass.

At least 8 / 10 exact-parent worlds must be baseline-feasible.

If fewer than 8 / 10 are feasible:

LU2N_CONTIGUOUS_LESION_ROBUSTNESS = FALSE

and interpret as insufficient exact-parent capacity under contiguous damage,
not as learned-U regression.

PAIRWISE PRESERVATION GATES

For every baseline-feasible pair require:

1. completion-area ratio:
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
where U_A0 phase/stream correct DONE >=4,
U_A25 retains >=75 percent;

7. anchor-relocation recovery:
U_A25 finite and <= U_A0 + 8 epochs;

8. demand-reversal recovery:
U_A25 finite and <= U_A0 + 8 epochs;

9. contiguous-lesion recovery:
either U_A25 lesion recovery is finite and <= U_A0 + 8 epochs,
or U_A25 lesion backlog area <= U_A0;

10. incorrect DONE:
0;

11. repair integrity:
PASS;

12. matching integrity:
PASS.

CAUSALITY

Across baseline-feasible worlds require:

U evaluations > 0;
teacher-vs-A25 U TV > 0;
at least one realized U transition difference.

H learned delta:
0.

H realized learned-controlled differences:
0.

OVERALL SIGNAL

LU2N_CONTIGUOUS_LESION_ROBUSTNESS = TRUE iff:

- duplicate paired primary sweeps are byte-identical;
- at least 8 / 10 U_A0 worlds are baseline-feasible;
- learned-U causality is TRUE;
- H remains teacher;
- every baseline-feasible pair passes every preservation gate;
- median completion-area ratio >=0.95;
- zero incorrect DONE occurs.

MECHANICAL GATE BEFORE LU2NF1

Prove:

1. exact LU-2M/LU-2L learned-U semantics;
2. exact canonical learned-weight SHA;
3. exact alpha=.25;
4. U_A0 exact teacher parity;
5. H/C/S/FC/FS remain teacher;
6. OBS-V1 unchanged;
7. one request per epoch unchanged;
8. Task-2 stage/repair/reverify semantics unchanged;
9. expiry remains 32;
10. lesion has exactly 16 cells;
11. lesion cells form one contiguous ring interval;
12. lesion duration remains 12 epochs;
13. footprint equals 25 percent of ring;
14. geometry differs from LU-2M distributed 16-cell lesion;
15. no lesion feature enters learned inference;
16. paired transition variates are common;
17. no model RNG;
18. no primary manifest during mechanical gate;
19. duplicate mechanical evidence byte-identical.

NO POST-RESULT TUNING

After LU2NF1 do not change:

lesion geometry;
lesion size;
lesion duration;
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
common-random policy.

NEXT STEP RULE

If TRUE:
the learned recruitment transfer has survived both distributed and
spatially concentrated 25-percent damage. Increase task distance next,
not authority.

If FALSE with baseline coverage:
diagnose the narrowest learned-vs-parent failure caused by spatial
concentration.

If FALSE from baseline coverage:
diagnose exact-parent contiguous-lesion capacity first.

PLAIN-SPEAK QUESTION

The last test knocked out sixteen cells spread around the ring and the
learned recruiter held up.

This time we knock out the same sixteen cells' worth of capacity, for the
same amount of time, but all in one neighborhood.

That is harder in a different way: one local region loses all nearby service
coverage at once.

If the neural recruiter still changes real developmental decisions while the
organism preserves the hand-written parent's envelope, the robustness is not
just an artifact of evenly distributed damage.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
