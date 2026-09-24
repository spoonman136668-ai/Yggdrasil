TITLE: LU-2I — TASK-2 EXACT-PARENT PAIRED LOAD-RESPONSE CALIBRATION
DATE: 2026-09-24
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT LU-2H CLOSURE:
dba00160c1e783af47c6d43b8d695b608c171736

PARENT LU-2G CLOSURE:
1fcfef885ca9bd8c3219333965d90cc9cc4a60e9

FROZEN TASK-2 IMPLEMENTATION:
e9a01aa97587fc97dde073cb2a6a35ad141006cd

QUESTION

Is the exact-parent Task-2 baseline infeasibility caused primarily by
ordinary offered-load overload at three requests per epoch?

Specifically:

does reducing physical arrivals from 3 to 2 or 1 request per epoch
monotonically reduce pre-SENSE congestion and restore the exact parent's
service / repair feasibility without changing the organism?

WHY THIS QUESTION NOW

LU-2H localized the dominant delay to PRE-SENSE:

mean:
21.1452812645 epochs

median:
26

p90:
30

while post-admission extra waits were near zero.

The inherited request lifetime is 32 epochs.

Therefore the smallest remaining causal test is to change only
offered request arrivals.

ARMS

Exact parent U_A0 only.

Three offered-load arms:

L1:
1 request per epoch

L2:
2 requests per epoch

L3:
3 requests per epoch

No learned-U arm.

No alpha comparison.

No model retraining.

No learned-model query is required.

PAIRED REQUEST DESIGN

Each calibration replicate first defines the exact fresh L3 request stream.

L3 uses the exact LU-2G temporal stream schedule:

balanced phases:
even epoch C,C,S
odd epoch C,S,S

C-heavy phase:
epochs 0,1,2 modulo four C,C,S
epoch 3 modulo four C,C,C

S-heavy phase:
mirror:
epochs 0,1,2 modulo four C,S,S
epoch 3 modulo four S,S,S

Request identity is fixed as:

rid = epoch * 3 + slot

for slots 0,1,2.

L2 and L1 are deterministic subsets of the L3 request identities.

BALANCED PHASE SUBSETS

even epoch:

L3 slots:
0,1,2 = C,C,S

L2:
slots 0,2 = C,S

L1:
slot 0 = C

odd epoch:

L3 slots:
0,1,2 = C,S,S

L2:
slots 0,1 = C,S

L1:
slot 1 = S

Thus L1 is balanced over two epochs,
L2 is balanced every epoch,
and both are strict subsets of L3.

C-HEAVY PHASE SUBSETS

For modulo-four epochs 0,1:

L2 selects C,S.
For epochs 2,3:
L2 selects C,C.

Across four epochs:
6 C : 2 S = 3:1.

L1 selects:

epoch 0:
S

epochs 1,2,3:
C

Across four epochs:
3 C : 1 S.

All selected request identities are subsets of paired L3.

S-HEAVY PHASE SUBSETS

Mirror exactly:

For modulo-four epochs 0,1:
L2 selects C,S.

For epochs 2,3:
L2 selects S,S.

Across four epochs:
2 C : 6 S = 1:3.

L1 selects:

epoch 0:
C

epochs 1,2,3:
S

Across four epochs:
1 C : 3 S.

COMMON WORLD MATERIAL

Within each replicate all three loads share exactly:

Task-2 programs;
request bits for any shared request identity;
corruption decision for any shared request identity;
lesion;
initial anchors;
rotated anchors;
developmental seed;
all substrate dynamics.

Thus lower-load arms remove requests from the paired L3 world;
they do not replace surviving work.

FRESH CALIBRATION WORLDS

After LU2IF1 exists,
derive exactly ten fresh calibration replicates from:

LU2I-TASK2-LOAD-CALIBRATION | LU2IF1 | replicate

replicate 1..10.

These worlds must not reuse LU-2G primary seeds.

All 30 load-arm manifests must be bound before execution.

No calibration world may later be used as a learned-U transfer primary.

FROZEN ORGANISM / TASK SEMANTICS

Preserve exactly:

Developmental Substrate V0.2;
D2;
LOCAL_HEDGE;
ECHO_PHASE;
NO_POOL;
G5_FULL OFF;
H teacher behavior;
U exact teacher behavior;
C/S stay-defect teacher;
FC/FS lifecycle teacher;
64-cell ring;
Task-2 two-stage program semantics;
PROCESS_A;
PROCESS_B;
six route hops;
verification computation;
corruption computation;
repair recomputes both stages from immutable provenance;
mandatory post-repair verification;
32-epoch expiry;
160-epoch horizon;
distributed lesion;
anchor rotation;
request-bound handoff;
neutral sensing;
one-operation-per-cell-per-epoch;
one-operation-per-request-per-epoch.

Only offered arrival count changes.

NO RECOVERY-TARGET TUNING

Continue to report the frozen LU-2G recovery target descriptively.

Do not require that target for LU-2I's load-response conclusion.

LU-2H established that exact L3 U_A0 reaches it in 0/30 event windows.

LU-2I may measure whether lower load makes it reachable,
but may not redefine it.

PRIMARY MEASUREMENTS PER LOAD

For each load report across ten fresh exact-parent worlds:

strict LU-2G baseline-feasible worlds;

correct DONE;

incorrect DONE;

expired;

unfinished backlog;

repair integrity;

operations per correct completion;

pre-SENSE wait:
mean, median, p90, max;

phase completion;

stream completion;

frozen event recovery target reachability;

functional cell-state organization:
mean and phase-specific counts of
C, S, U, H, FC, FS.

MECHANICAL GATE BEFORE LU2IF1

Prove:

1. L3 arrival schedule equals LU-2G stream schedule exactly.
2. L2 arrivals are strict deterministic subsets of paired L3.
3. L1 arrivals are strict deterministic subsets of paired L2 / L3.
4. Balanced phases remain exactly balanced over their frozen period.
5. C-heavy remains exactly 3:1 at every load over four epochs.
6. S-heavy remains exactly 1:3 at every load over four epochs.
7. shared request rid has identical bits and corruption decision across loads.
8. programs / lesion / anchors are identical across paired loads.
9. U_A0 calls exact V0.2 teacher path only.
10. expiry remains 32.
11. Task-2 stage / repair / verify semantics unchanged.
12. no new stochastic scheduling or model RNG.
13. two complete mechanical evidence runs are byte-identical.

LOAD-RESPONSE DECISION

Define strict baseline feasibility exactly as LU-2G:

at least one correct DONE in every phase;
zero incorrect DONE;
both streams produce correct DONE;
repair integrity pass;
finite operations per correct completion;
matching integrity pass.

For each load L:

baseline_coverage(L)
=
number of strict baseline-feasible exact-parent worlds / 10.

LU2I_ORDINARY_OVERLOAD_SUPPORTED = TRUE iff:

1. baseline_coverage(L2) > baseline_coverage(L3);
2. baseline_coverage(L1) >= baseline_coverage(L2);
3. median pre-SENSE wait strictly decreases L3 -> L2;
4. median pre-SENSE wait does not increase L2 -> L1;
5. no lower-load arm produces incorrect DONE;
6. the reduction is not explained by a loss of both functional stream populations.

If these conditions do not hold:

ordinary offered-load overload alone is not sufficient.

Then the next experiment should test developmental-demand under-signaling /
nonmonotonic workforce organization rather than lowering load again.

CALIBRATION SUCCESS FOR A FUTURE ENVIRONMENT

This experiment does NOT authorize a learned-U transfer comparison.

A load is only a candidate for a future Task-2 environment if:

baseline_coverage(L) >= 8 / 10

and

both streams remain functionally active.

Any candidate load must then undergo
a fresh exact-parent validation on a new ten-world set
before a learned-U comparison is preregistered.

No calibration-world reuse.

NO POST-RESULT TUNING

Do not change:

load set 1,2,3;
subset schedule;
world count;
program rules;
expiry;
horizon;
corruption rate;
lesion;
anchor rotation;
developmental dynamics;
baseline definition;
or decision criteria after results.

PLAIN-SPEAK QUESTION

Task-2 jobs are spending almost their whole 32-epoch lifetime
waiting to get sensed.

The simplest explanation is that three jobs per epoch is still too much.

We will test that directly.

The exact same organism gets fresh paired worlds with:

three jobs per epoch;
two of those same jobs;
or one of those same jobs.

Nothing else changes.

If the admission queue gets steadily healthier as jobs are removed,
ordinary overload is the problem.

If it does not,
then the problem is more interesting:
changing request pressure may also be changing how the organism organizes
its workforce.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
