TITLE: LU-2M — DOUBLED DISTRIBUTED LESION ROBUSTNESS
DATE: 2026-09-24
STATUS: PREREGISTERED / NO LU-2M PRIMARY WORLD DERIVED OR EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT LU-2L CLOSURE:
ed618450559eb8275557108f758c61949e030653

PARENT LU2LF1:
799058733a864c1d8437569cf4e8cdc6502fa6c3

PARENT LU-2K CLOSURE:
c6333ccf2fa9e3244feee66bf021cdc17924d145

CANONICAL LU-1E WEIGHTS:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

PURPOSE

Increase perturbation difficulty after successful Task-2 learned-U transfer
without increasing learned authority or changing Task-2 service load.

SCIENTIFIC QUESTION

Does the accepted 25-percent learned U-recruitment authority remain causally
active and functionally contained when the distributed lesion footprint is
doubled while every other Task-2 condition remains fixed?

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
No learned-authority increase.

TASK ENVIRONMENT

Retain the validated LU-2K / qualified LU-2L L1 Task-2 environment exactly:

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
two-stage compositional Task-2 computation;
same corruption, repair, verification and re-verification semantics.

PERTURBATION CHANGE — ONE AXIS ONLY

Inherited lesion window remains exactly:

epoch 96 inclusive
through epoch 108 exclusive

duration:
12 epochs.

Inherited lesion set has eight distributed cells:

base(seed) = p.lesion_set(seed)

with positions spaced every eight cells.

LU-2M doubles only the footprint by adding the interleaved offset-4 partner
of every inherited lesion cell:

strong_lesion(seed) =
base(seed) UNION { (i + 4) mod 64 : i in base(seed) }

Required properties:

base lesion is an exact subset of strong lesion;
strong lesion has exactly 16 distinct cells;
same seed controls the base lesion offset;
same lesion onset and end epochs;
no lesion-duration change;
no task-load change;
no corruption change;
no expiry change.

Thus LU-2M increases unavailable-cell footprint from:

8 / 64 = 12.5 percent

to:

16 / 64 = 25 percent

for the same 12-epoch window.

OBSERVATION BOUNDARY

Learned U receives exactly OBS-V1.

No lesion flag.
No lesion size.
No task program.
No program id.
No stage id.
No request id.
No phase id.
No absolute position.
No global queue length.
No evaluator correctness.
No future information.

COMMON RANDOMNESS

Within each paired world:

same manifest;
same strong lesion;
same programs;
same arrivals;
same corruption;
same anchors;
same initial developmental state;
same transition random variates.

No learned-model RNG.

IMPLEMENTATION FREEZE

Create LU2MF1 before deriving any LU-2M primary world.

No primary manifest may exist before LU2MF1.

FRESH PRIMARY WORLDS

Exactly 10 fresh paired worlds.

Namespace:

LU2M-TASK2-L1-DOUBLE-LESION|LU2MF1|replicate

replicate 1..10.

Do not reuse LU-2G, LU-2I, LU-2K, or LU-2L worlds.

Bind all ten complete manifests before any primary arm executes.

No replacement.
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

LU2M_DOUBLE_LESION_ROBUSTNESS = FALSE

and interpret as insufficient exact-parent evidence under the stronger lesion,
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
for each phase/stream where U_A0 has >=4 correct DONE,
U_A25 retains >=75 percent;

7. anchor-relocation recovery:
U_A25 finite and no more than 8 epochs later than paired U_A0;

8. demand-reversal recovery:
U_A25 finite and no more than 8 epochs later than paired U_A0;

9. stronger-lesion recovery:
either U_A25 lesion recovery latency is finite and <= paired U_A0 + 8 epochs,
or U_A25 lesion backlog area <= paired U_A0;

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

LU2M_DOUBLE_LESION_ROBUSTNESS = TRUE iff:

- duplicate paired primary sweeps are byte-identical;
- at least 8 / 10 U_A0 worlds are baseline-feasible;
- learned-U causality is TRUE;
- H remains teacher;
- every baseline-feasible pair passes every preservation gate;
- median completion-area ratio >=0.95;
- zero incorrect DONE occurs.

MECHANICAL GATE BEFORE LU2MF1

Prove:

1. exact LU-2L learned-U semantics;
2. exact canonical learned weight SHA;
3. exact alpha=.25;
4. U_A0 teacher parity;
5. H/C/S/FC/FS remain teacher;
6. OBS-V1 unchanged;
7. L1 one-request-per-epoch load unchanged;
8. Task-2 stage/repair/reverify semantics unchanged;
9. expiry remains 32;
10. inherited lesion has 8 cells;
11. strong lesion has exactly 16 cells;
12. inherited lesion is exact subset of strong lesion;
13. lesion duration remains 12 epochs;
14. no lesion feature enters learned inference;
15. paired transition variates are common;
16. no model RNG;
17. no primary manifest is derived during mechanical gate;
18. duplicate mechanical evidence is byte-identical.

NO POST-RESULT TUNING

After LU2MF1 do not change:

lesion footprint;
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

learned recruitment has now transferred to Task-2 and survived a stronger
distributed perturbation without authority expansion.

The next experiment should increase task distance or perturbation structure,
not alpha.

If FALSE with baseline coverage:

diagnose the narrowest learned-U versus exact-parent divergence mechanism.

If FALSE from baseline coverage:

diagnose exact-parent stronger-lesion capacity before drawing any learned-U
conclusion.

PLAIN-SPEAK QUESTION

The neural recruiter already survived a different two-step task.

Now we damage twice as many distributed service cells for the same amount of
time.

We do not make the job harder in any other way and we do not give the neural
controller more power.

If the 25-percent learned recruiter still changes real developmental
decisions while the organism keeps pace with the hand-written parent, that
is evidence the transferred behavior is not fragile to a substantially
larger local disruption.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
