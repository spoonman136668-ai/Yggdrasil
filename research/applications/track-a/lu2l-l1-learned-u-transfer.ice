TITLE: LU-2L — LEARNED-U TRANSFER ON VALIDATED L1 TASK-2
DATE: 2026-09-24
STATUS: PREREGISTERED / NO LU-2L WORLD DERIVED OR EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT LU-2K CLOSURE:
c6333ccf2fa9e3244feee66bf021cdc17924d145

PARENT LU2KF1:
441d90e9c39e0ed9444953937d90d585084b4c7b

PARENT LU-2G IMPLEMENTATION:
e9a01aa97587fc97dde073cb2a6a35ad141006cd

PARENT LU-2E A25 LINEAGE:
377fdc6e3b65fe843f77296cf1bbdc82736813a1

CANONICAL LU-1E WEIGHT SHA256:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

PURPOSE

Return to the original second-task transfer question only after LU-2K
independently established a baseline-feasible Task-2 environment.

SCIENTIFIC QUESTION

On fresh paired one-request-per-epoch compositional Task-2 worlds, does the
accepted 25-percent learned U-recruitment authority causally change
developmental decisions while preserving the validated exact-parent
functional envelope?

ARMS

Exactly two arms:

U_A0:
exact V0.2 U recruitment.

U_A25:
P(U) = 0.75 * P_teacher + 0.25 * P_learned.

All other developmental transitions remain exact teacher:

H release:
teacher.

C/S stay-defect:
teacher.

FC/FS lifecycle:
teacher.

No retraining.
No optimizer.
No online adaptation.
No weight mutation.
No authority increase.

TASK-2 ENVIRONMENT

Use exactly the validated L1 Task-2 service regime:

one request per epoch;
64-cell ring;
160 epochs;
five 32-epoch phases;
D2;
LOCAL_HEDGE;
ECHO_PHASE;
NO_POOL;
G5_FULL OFF;
request-bound handoff;
neutral sensing;
distributed lesion;
anchor relocation;
inherited 32-epoch expiry.

Task computation remains:

RAW
-> SENSED
-> PROCESSED_A
-> PROCESSED_B
-> ROUTING
-> AT_EGRESS
-> VERIFIED
-> DONE.

A failed verification enters REPAIR_PENDING,
recomputes both stages from immutable provenance,
and requires independent re-verification.

OBSERVATION BOUNDARY

Learned U receives exactly OBS-V1.

No task program.
No program id.
No stage id.
No request id.
No phase id.
No absolute position.
No global queue length.
No evaluator correctness.
No future information.
No teacher-derived feature is supplied to the learned model.

The exact teacher U distribution may be used only outside the learned model
to form the frozen alpha=.25 blend.

COMMON RANDOMNESS

Within every paired world:

same manifest;
same programs;
same arrivals;
same corruption schedule;
same lesion;
same anchors;
same initial developmental state;
same transition random variates.

No learned-model RNG.

IMPLEMENTATION FREEZE

Create LU2LF1 before any LU-2L primary manifest exists.

The implementation must reuse the accepted LU-2G paired Task-2 machinery and
the accepted 25-percent U blend semantics.

Do not derive a primary namespace during the mechanical gate.

FRESH PRIMARY WORLDS

Exactly 10 fresh paired worlds.

Namespace:

LU2L-TASK2-L1-A25-TRANSFER|LU2LF1|replicate

replicate 1..10.

Do not reuse LU-2G, LU-2I, or LU-2K worlds.

Bind all ten complete manifests before any primary arm executes.

No replacement.
No rejection sampling.
No result-dependent selection.

BASELINE-FEASIBILITY CONTRACT

Before interpreting U_A25, paired U_A0 must satisfy:

1. at least one correct DONE request in every phase;
2. zero incorrect DONE;
3. both C and S streams produce correct DONE;
4. verification / repair integrity pass;
5. finite operations per correct completion;
6. matching / scheduler integrity pass.

At least 8 / 10 U_A0 worlds must be baseline-feasible.

If fewer than 8 / 10 are feasible:

LU2L_L1_LEARNED_U_TRANSFER = FALSE

and interpret the failure as lack of fresh-environment replication rather
than evidence against learned U.

PAIRWISE PRESERVATION GATES

For every baseline-feasible paired world require:

1. total correct-completion area:
U_A25 >= 0.90 * U_A0;

2. median paired completion-area ratio across baseline-feasible worlds:
>= 0.95;

3. final-16 total backlog area:
U_A25 <= 1.25 * U_A0;

4. final backlog:
U_A25 <= 1.25 * U_A0;

5. operations per correct completion:
U_A25 <= 1.25 * U_A0;

6. stream noncollapse:
for each phase and stream, when U_A0 has at least four correct DONE,
U_A25 must retain at least 75 percent;

7. anchor-relocation recovery:
U_A25 recovery latency must be finite and no more than 8 epochs later
than paired U_A0;

8. demand-reversal recovery:
U_A25 recovery latency must be finite and no more than 8 epochs later
than paired U_A0;

9. inherited lesion criterion:
either U_A25 lesion recovery latency is finite and <= 8 epochs,
or U_A25 lesion backlog area <= paired U_A0;

10. incorrect DONE:
0;

11. corruption / repair integrity:
PASS;

12. matching integrity:
PASS.

CAUSALITY GATE

Across baseline-feasible worlds require:

U evaluations > 0;

teacher-vs-A25 U TV > 0;

at least one realized U transition differs under the shared transition
variate.

H nonzero probability delta:
0.

H realized learned-controlled differences:
0.

If no realized U transition differs, the experiment may not be called
positive.

OVERALL SIGNAL

LU2L_L1_LEARNED_U_TRANSFER = TRUE iff:

- duplicate complete paired sweeps are byte-identical;
- at least 8 / 10 U_A0 worlds are baseline-feasible;
- causal learned-U participation is TRUE;
- every baseline-feasible pair passes every pairwise preservation gate;
- median paired completion-area ratio >= 0.95;
- zero incorrect DONE occurs;
- all required integrity checks pass.

OBSERVATION-ONLY REPORTING

Also report:

repair opportunity counts for each arm;
expired count;
per-world recovery latencies;
state-divergence epochs;
first divergence epoch;
mean teacher-vs-learned U TV.

These are descriptive only and may not change gates after execution.

MECHANICAL GATE BEFORE LU2LF1

Prove before freeze:

1. exact V0.2 parent identity;
2. exact canonical LU-1E weight SHA;
3. exact accepted alpha=.25 U blend;
4. U_A0 exact teacher behavior;
5. H remains teacher;
6. C/S/FC/FS remain teacher;
7. learned calls restricted to H/U;
8. OBS-V1 unchanged;
9. Task-2 stage order and repair/reverify semantics exact;
10. load is exactly one request per epoch;
11. expiry remains 32;
12. no model RNG;
13. paired transition variates are common;
14. D2 / LOCAL_HEDGE / ECHO_PHASE / NO_POOL / G5_FULL OFF preserved;
15. fresh primary namespace depends on LU2LF1;
16. no primary manifest is derived in the mechanical gate;
17. duplicate mechanical evidence byte-identical.

NO POST-RESULT TUNING

After LU2LF1 do not change:

alpha;
weights;
OBS-V1;
load;
expiry;
Task-2 computation;
repair;
verification;
phase structure;
manifest count;
baseline-feasibility bars;
pairwise preservation bars;
causality definition;
recovery definitions;
common-random policy.

NEXT STEP RULE

If TRUE:

this is direct evidence that bounded learned recruitment generalizes from
Task-1 to a distinct compositional Task-2 environment under a
baseline-validated service regime.

The next experiment must increase task distance or perturbation difficulty
without automatically increasing learned authority.

If FALSE:

classify whether failure is baseline replication, learned-U path
amplification, repair/integrity interaction, recovery behavior, or another
specific mechanism before proposing any architecture change.

PLAIN-SPEAK QUESTION

We finally have a fair two-step task environment.

The hand-written parent passed ten out of ten fresh worlds at one job per
epoch.

Now we put the same 25-percent neural recruitment authority back in, but we
do not let it see the task, the programs, the stage, the phase, or global
state.

The only thing being tested is whether the learned local recruiter can
change real developmental decisions and still preserve what the organism
gets done on this different kind of job.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
