TITLE: LU-2Q — THREE-STAGE TASK-3 EXACT-PARENT FEASIBILITY
DATE: 2026-09-24
STATUS: PREREGISTERED / NO LU-2Q PRIMARY WORLD DERIVED OR EXECUTED
TRACK: DG-1 / TASK-DISTANCE EXPANSION

PARENT LU-2P CLOSURE:
207c4afc422cc59ef9c0576130eaa7713f5c9d1d

PARENT LU2PF1:
6cf5ac96c4357fa3d065f2076ee64fe401e542e9

PARENT DEVELOPMENTAL SUBSTRATE V0.2:
e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2

PURPOSE

Increase task distance after qualified Task-2 transfer and perturbation
robustness without increasing learned authority.

First establish that the exact hand-written parent can support a deeper
three-stage compositional task fairly.

No learned-U scientific conclusion is permitted in LU-2Q.

SCIENTIFIC QUESTION

Can exact V0.2 developmental control sustain a fresh three-stage
compositional transform service at one request per epoch while preserving
correctness, repair integrity, directional service, and recovery under the
validated inherited perturbation regime?

ARM

Exactly one scientific arm:

U_A0:
exact V0.2 U recruitment.

H release:
exact teacher.

C/S stay-defect:
exact teacher.

FC/FS lifecycle:
exact teacher.

No learned inference is required for the scientific arm.
No retraining.
No optimizer.
No online adaptation.
No authority expansion.

TASK-3 COMPUTATION

Each request carries immutable:

4-bit input x0;
stage-A truth-table program PA;
stage-B truth-table program PB;
stage-C truth-table program PC;
stream;
creation epoch;
deterministic request id.

Interpreter remains the exact 4-bit truth-table interpreter:

index = a | (b<<1) | (c<<2) | (d<<3)
output = (program >> index) & 1

Stage A:

yA = PA(x0)

x1 is x0 with bit 0 replaced by yA.

Stage B:

yB = PB(x1)

x2 is x1 with bit 1 replaced by yB.

Stage C:

yC = PC(x2)

Verified answer:
yC.

Every request therefore requires three causally ordered PROCESS operations.

LIFECYCLE

RAW
-> SENSED
-> PROCESSED_A
-> PROCESSED_B
-> PROCESSED_C
-> ROUTING
-> AT_EGRESS
-> VERIFIED
-> DONE.

No stage may be skipped.

Verification recomputes A, B, and C from immutable provenance.

Verification failure enters REPAIR_PENDING.

REPAIR recomputes all three stages from immutable x0 / PA / PB / PC.

Independent re-verification remains mandatory before DONE.

ENVIRONMENT

Retain the validated L1 external regime:

64-cell ring;
160 epochs;
one request per epoch;
five 32-epoch phases;
D2;
LOCAL_HEDGE;
ECHO_PHASE;
NO_POOL;
G5_FULL OFF;
request-bound handoff;
neutral sensing;
32-epoch expiry;
same C/S directional schedule;
same anchor relocation semantics.

Return perturbation to the inherited baseline:

8-cell distributed lesion;
epoch 96 inclusive through 108 exclusive.

Do not retain the LU-2P 16-cell contiguous lesion.

This isolates task-distance change from perturbation severity.

PROGRAM DERIVATION

Only after LU2QF1 exists derive six distinct programs per world:

C-A
C-B
C-C
S-A
S-B
S-C

Namespace:

LU2Q-TASK3-L1|LU2QF1|replicate|stream|stage|counter

Programs must be:

16-bit truth tables;
nonconstant;
nonaffine;
distinct within a replicate.

No difficulty filtering.
No result-dependent replacement.

LOAD

Exactly one request per epoch.

Do not load-normalize downward.

The added third PROCESS operation is part of the intended increase in task
distance.

If the exact parent cannot support this service demand, that is a valid
capacity result and will be diagnosed before any learned-U test.

REPAIR MATURITY CONTRACT

Retain the mechanics-derived LU-2P horizon contract because the post-detection
repair sequence is unchanged:

mature detection:
first detection <=156.

Mature detections must repair, reverify, and reach correct DONE by 159.

For terminal in-flight detections:

157:
repair by 158, reverify by 159, VERIFIED terminal permitted;

158:
repair by 159, AT_EGRESS terminal permitted;

159:
REPAIR_PENDING terminal permitted.

Detection remains mandatory for every corruption that reaches egress.

Incorrect DONE is always forbidden.

No drain epochs.

No extra service time.

FRESH PRIMARY WORLDS

Exactly 10 fresh exact-parent worlds.

Namespace:

LU2Q-TASK3-L1|LU2QF1|replicate

replicate 1..10.

Do not reuse LU-2K/L/LU-2M/LU-2N/LU-2P worlds.

Bind all ten manifests before execution.

No replacement.
No rejection sampling.
No result-dependent selection.

BASELINE FEASIBILITY PER WORLD

A world is feasible iff:

1. at least one correct DONE in every phase;
2. zero incorrect DONE;
3. both C and S produce correct DONE;
4. maturity-conditioned repair integrity passes;
5. operations per correct completion is finite;
6. matching duplicate-cell and duplicate-request integrity pass;
7. demand-reversal recovery is finite and <=8 epochs;
8. anchor-relocation recovery is finite and <=8 epochs;
9. inherited lesion recovery is finite and <=8 epochs OR lesion backlog area
   does not exceed the preregistered inherited-parent criterion implemented
   before freeze.

EVIDENCE COVERAGE

At least 8 / 10 worlds must be baseline-feasible.

LU2Q_TASK3_EXACT_PARENT_FEASIBLE = TRUE iff:

- duplicate complete sweeps are byte-identical;
- at least 8 / 10 worlds are baseline-feasible;
- all worlds have zero incorrect DONE;
- no scheduler/matching integrity failure occurs.

If fewer than 8 / 10 are feasible:

LU2Q_TASK3_EXACT_PARENT_FEASIBLE = FALSE.

Interpret as Task-3 capacity/environment evidence.

Do not infer anything about learned U.

MECHANICAL GATE BEFORE LU2QF1

Prove:

1. exact V0.2 developmental parent;
2. U exact teacher;
3. H/C/S/FC/FS exact teacher;
4. D2 / LOCAL_HEDGE / ECHO_PHASE / NO_POOL / G5_FULL OFF preserved;
5. one request per epoch exact;
6. exactly three ordered PROCESS stages;
7. Stage B depends on Stage A through x1;
8. Stage C depends on Stage B through x2;
9. no PROCESS stage can be skipped;
10. verification recomputes all three stages from immutable provenance;
11. repair recomputes all three stages;
12. independent reverify required;
13. inherited distributed 8-cell lesion restored;
14. lesion window [96,108);
15. anchor relocation unchanged;
16. expiry remains 32;
17. maturity boundary/rules unchanged from LU-2P;
18. no model RNG;
19. no primary manifest during gate;
20. duplicate mechanical evidence byte-identical.

NO POST-RESULT TUNING

After LU2QF1 do not change:

Task-3 stage semantics;
program derivation;
load;
expiry;
lesion;
phase schedule;
repair;
verification;
maturity boundary;
manifest count;
baseline bars;
world namespace.

NEXT STEP RULE

If TRUE:

preregister a fresh paired Task-3 learned-U transfer experiment using the
same 25-percent U_A25 authority and no other authority increase.

If FALSE:

diagnose whether the exact-parent failure is service-capacity, repair,
recovery, or another Task-3-specific mechanism before changing load or
architecture.

PLAIN-SPEAK QUESTION

We already know the neural recruiter can transfer to a two-step job and can
survive severe damage.

Now we make the job itself deeper.

Each request has to complete three dependent transforms instead of two.

We first ask only whether the hand-written organism can handle that job
fairly at the same external arrival rate.

If it can, then we can make a clean learned-vs-hand-written Task-3 test next.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
