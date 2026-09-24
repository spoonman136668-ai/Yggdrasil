TITLE: LU-2R — FRESH TASK-3 LEARNED-U TRANSFER
DATE: 2026-09-24
STATUS: PREREGISTERED / NO LU-2R PRIMARY WORLD DERIVED OR EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT LU-2Q CLOSURE:
b53159cbf2a87f1a8e7afaeb7232b2f63e41bc1d

PARENT LU2QF1:
c2907a97aeff03f6fb7bebacf448fc9027859e19

PARENT LU-2P CLOSURE:
207c4afc422cc59ef9c0576130eaa7713f5c9d1d

PARENT LU-2L CLOSURE:
ed618450559eb8275557108f758c61949e030653

CANONICAL LU-1E WEIGHTS:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

PURPOSE

Test whether the accepted bounded learned U-recruitment behavior transfers
from the qualified two-stage task into the independently validated deeper
three-stage Task-3 environment.

SCIENTIFIC QUESTION

On ten fresh paired Task-3 worlds, does the accepted 25-percent learned U
blend causally change developmental recruitment while preserving the
validated exact-parent functional envelope?

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

TASK-3 ENVIRONMENT

Use exact LU-2Q Task-3 semantics:

one request per epoch;
160 epochs;
64-cell ring;
D2;
LOCAL_HEDGE;
ECHO_PHASE;
NO_POOL;
G5_FULL OFF;
request-bound handoff;
neutral sensing;
32-epoch expiry;
same five-phase C/S schedule;
same anchor relocation;
same inherited distributed 8-cell lesion over [96,108).

Each request performs three causally ordered transforms:

A -> B -> C

with immutable x0 / PA / PB / PC provenance.

Lifecycle:

RAW
-> SENSED
-> PROCESSED_A
-> PROCESSED_B
-> PROCESSED_C
-> ROUTING
-> AT_EGRESS
-> VERIFIED
-> DONE.

Repair recomputes all three stages from immutable provenance and independent
re-verification remains mandatory.

REPAIR MATURITY CONTRACT

Retain exact LU-2Q / LU-2P maturity semantics.

Mature detection:
first detection <=156.

All mature detections must repair, reverify, and reach correct DONE by 159.

Terminal in-flight detections:

157:
repair by 158, reverify by 159, VERIFIED terminal permitted;

158:
repair by 159, AT_EGRESS terminal permitted;

159:
REPAIR_PENDING terminal permitted.

Detection remains mandatory for every corruption that reaches egress.

Incorrect DONE is always forbidden.

No drain epochs.

OBSERVATION BOUNDARY

Learned U receives exactly OBS-V1.

No task identity.
No program identity.
No stage identity.
No phase id.
No absolute position.
No global queue.
No evaluator correctness.
No lesion flag.
No future information.

COMMON RANDOMNESS

Within each pair:

same manifest;
same programs;
same arrivals;
same corruption;
same lesion;
same anchors;
same initial developmental state;
same transition variates.

No learned-model RNG.

IMPLEMENTATION FREEZE

Create LU2RF1 before deriving any LU-2R primary world.

No primary manifest may exist before LU2RF1.

FRESH WORLDS

Exactly 10 fresh paired worlds.

Namespace:

LU2R-TASK3-L1-A25|LU2RF1|replicate

replicate 1..10.

Do not reuse LU-2Q or any earlier world.

Bind all ten manifests before any primary arm executes.

No replacement.
No rejection sampling.
No result-dependent selection.

BASELINE FEASIBILITY

U_A0 is baseline-feasible iff:

1. at least one correct DONE in every phase;
2. zero incorrect DONE;
3. both C and S produce correct DONE;
4. maturity-conditioned repair integrity passes;
5. operations per correct completion is finite;
6. matching duplicate-cell and duplicate-request integrity pass;
7. demand-reversal recovery is finite and <=8 epochs;
8. anchor-relocation recovery is finite and <=8 epochs;
9. inherited-lesion recovery is finite and <=8 epochs OR the preregistered
   inherited-parent lesion backlog criterion passes.

At least 8 / 10 U_A0 worlds must be baseline-feasible.

If fewer than 8 / 10 are feasible:

LU2R_TASK3_LEARNED_U_TRANSFER = FALSE

and interpret as insufficient fresh Task-3 exact-parent coverage, not as
learned-U regression.

PAIRWISE PRESERVATION GATES

For every baseline-feasible pair require:

1. correct-completion area:
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

7. anchor recovery:
finite and <= paired U_A0 + 8 epochs;

8. demand recovery:
finite and <= paired U_A0 + 8 epochs;

9. inherited-lesion recovery:
finite and <= paired U_A0 + 8 epochs OR
U_A25 lesion backlog area <= U_A0;

10. incorrect DONE:
0;

11. maturity-conditioned repair integrity:
PASS;

12. matching integrity:
PASS.

CAUSALITY

Across baseline-feasible worlds require:

U evaluations > 0;
teacher-vs-A25 U TV > 0;
at least one realized U transition differs under the shared variate.

H learned probability delta:
0.

H realized learned-controlled differences:
0.

OVERALL SIGNAL

LU2R_TASK3_LEARNED_U_TRANSFER = TRUE iff:

- duplicate complete paired sweeps are byte-identical;
- at least 8 / 10 U_A0 worlds are baseline-feasible;
- learned-U causality is TRUE;
- H remains exact teacher;
- every baseline-feasible pair passes every preservation gate;
- median completion-area ratio >=0.95;
- zero incorrect DONE occurs.

MECHANICAL GATE BEFORE LU2RF1

Prove:

1. exact LU-2Q Task-3 semantics;
2. exact canonical learned-weight SHA;
3. exact alpha=.25 U blend;
4. U_A0 exact teacher one-step parity;
5. H/C/S/FC/FS exact teacher;
6. OBS-V1 unchanged;
7. one request per epoch exact;
8. exactly three ordered PROCESS stages;
9. Stage B consumes Stage-A-derived x1;
10. Stage C consumes Stage-B-derived x2;
11. verification recomputes all three stages;
12. repair recomputes all three stages;
13. independent re-verification required;
14. inherited distributed 8-cell lesion unchanged;
15. lesion window [96,108);
16. anchor relocation unchanged;
17. expiry remains 32;
18. LU-2Q maturity contract unchanged;
19. paired transition variates common;
20. no model RNG;
21. learned calls restricted to H/U;
22. no primary manifest during gate;
23. duplicate mechanical evidence byte-identical.

NO POST-RESULT TUNING

After LU2RF1 do not change:

alpha;
weights;
OBS-V1;
Task-3 stage semantics;
program derivation;
load;
expiry;
lesion;
phase schedule;
repair;
verification;
maturity contract;
manifest count;
qualification bars;
world namespace;
common-random policy.

NEXT STEP RULE

If TRUE:

the same bounded learned recruitment behavior has transferred from Task-1
through two-stage Task-2 and into deeper three-stage Task-3 without
retraining.

Run one fresh independent Task-3 confirmation before increasing task distance
again.

Do not increase learned authority automatically.

If FALSE with baseline coverage:

diagnose the narrowest learned-vs-parent failure without tuning the frozen
experiment.

If FALSE from baseline coverage:

diagnose the exact-parent Task-3 fresh-world failure before any learned-U
conclusion.

PLAIN-SPEAK QUESTION

The hand-written organism can handle the deeper three-step job.

Now we put the same neural recruiter back in with exactly the same limited
25-percent say over U recruitment.

It still gets no clue what task, stage, program, phase, lesion, or global
queue it is dealing with.

If it makes real developmental decisions and the organism still keeps pace
with the hand-written parent, then the learned local behavior has transferred
another step farther from the task where it was learned.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
