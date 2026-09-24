TITLE: LU-2P — FRESH CONTIGUOUS-LESION ROBUSTNESS WITH MATURE REPAIR CONTRACT
DATE: 2026-09-24
STATUS: PREREGISTERED / NO LU-2P PRIMARY WORLD DERIVED OR EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT LU-2O CLOSURE:
1d5deaa6231b854a00fb50e76b685e437b29e700

PARENT LU-2N CLOSURE:
096c8dee7ae368f69e322be8e1b8a5ca20feff08

PARENT LU2NF1:
a4657c94a654d2b4f83b6af0c7844b65e6999593

CANONICAL LU-1E WEIGHTS:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

PURPOSE

Retest contiguous 16-cell lesion robustness on fresh worlds after LU-2O
proved that LU-2N exact-parent baseline failures were final-epoch repair
truncation rather than a repair-capacity defect.

SCIENTIFIC QUESTION

With organism dynamics unchanged, does the accepted 25-percent learned U
recruitment remain causally active and functionally contained under a
16-cell contiguous lesion when repair integrity is evaluated only over
requests that had enough physical service epochs to mature?

ARMS

U_A0:
exact V0.2 U recruitment.

U_A25:
0.75 * exact teacher U + 0.25 * frozen learned U.

H, C/S, FC/FS:
exact teacher.

No retraining.
No optimizer.
No online adaptation.
No authority increase.

ENVIRONMENT

Exactly the LU-2N environment:

one request per epoch;
160 epochs, indexed 0..159;
five 32-epoch phases;
64-cell ring;
D2;
LOCAL_HEDGE;
ECHO_PHASE;
NO_POOL;
G5_FULL OFF;
request-bound handoff;
neutral sensing;
32-epoch expiry;
same two-stage Task-2 computation;
same corruption semantics;
same anchor relocation;
same 16-cell contiguous lesion;
same lesion window [96,108).

No drain epochs.

No extra service ticks.

No change to organism dynamics.

REPAIR MATURITY CONTRACT

Task-2 repair requires distinct service operations:

detection at epoch t;
repair no earlier than t+1;
successful re-verification no earlier than t+2;
DONE finalization no earlier than t+3.

Therefore:

MATURE DETECTION:
first verification detection epoch <= 156.

Every mature detected corruption must:

- be repaired;
- be successfully re-verified;
- reach correct DONE by epoch 159;
- never expire;
- never produce incorrect DONE.

TERMINAL IN-FLIGHT DETECTION:
first verification detection epoch in {157,158,159}.

These are not counted as completed-repair failures solely because the
160-epoch horizon ends first.

They must still satisfy mechanically reachable progress:

detected at 157:
repair by 158;
successful reverify by 159;
terminal state VERIFIED at epoch 160 is permitted because DONE finalization
would first be possible at epoch 160.

detected at 158:
repair by 159;
terminal state AT_EGRESS at epoch 160 is permitted because reverify would
first be possible at epoch 160.

detected at 159:
terminal state REPAIR_PENDING at epoch 160 is permitted because repair would
first be possible at epoch 160.

For every corruption reaching egress:

detection is still mandatory.

Incorrect DONE remains forbidden.

Expiry remains forbidden for a valid terminal in-flight repair.

This contract is fixed before LU2PF1 and is derived from the one-operation-
per-request-per-epoch lifecycle, not from LU-2P outcomes.

OBSERVATION BOUNDARY

Learned U receives exactly OBS-V1.

No lesion flag.
No lesion geometry.
No repair-maturity flag.
No task/program/stage/phase id.
No absolute position.
No global queue.
No evaluator correctness.
No future information.

COMMON RANDOMNESS

Within every pair:

same manifest;
same contiguous lesion;
same programs;
same arrivals;
same corruption;
same anchors;
same initial state;
same transition variates.

No learned-model RNG.

IMPLEMENTATION FREEZE

Create LU2PF1 before deriving any LU-2P primary world.

No primary namespace or manifest may exist before LU2PF1.

FRESH PRIMARY WORLDS

Exactly 10 fresh paired worlds.

Namespace:

LU2P-TASK2-L1-CONTIG16-MATURE|LU2PF1|replicate

replicate 1..10.

Do not reuse LU-2N worlds.

Bind all ten manifests before execution.

No replacement.
No rejection sampling.
No result-dependent selection.

BASELINE FEASIBILITY

U_A0 baseline-feasible iff:

1. at least one correct DONE in every phase;
2. zero incorrect DONE;
3. both streams produce correct DONE;
4. maturity-conditioned repair integrity passes;
5. finite operations per correct completion;
6. matching integrity passes.

At least 8 / 10 U_A0 worlds must be baseline-feasible.

PAIRWISE PRESERVATION

Use the LU-2N pairwise gates unchanged except replace strict all-detections
repair integrity with the maturity-conditioned repair contract above.

Require for every baseline-feasible pair:

completion area >= 90 percent of U_A0;
median completion-area ratio >= 0.95;
final-16 backlog area <= 125 percent U_A0;
final backlog <= 125 percent U_A0;
operations per correct completion <= 125 percent U_A0;
stream noncollapse;
anchor recovery finite and <= U_A0 + 8;
demand recovery finite and <= U_A0 + 8;
contiguous-lesion recovery paired criterion;
incorrect DONE = 0;
maturity-conditioned repair integrity PASS;
matching integrity PASS.

CAUSALITY

Across baseline-feasible worlds require:

U evaluations > 0;
teacher-vs-A25 U TV > 0;
at least one realized U transition difference.

H learned delta = 0.
H realized learned-controlled differences = 0.

OVERALL SIGNAL

LU2P_CONTIGUOUS_LESION_ROBUSTNESS = TRUE iff:

- duplicate complete paired sweeps are byte-identical;
- at least 8 / 10 exact-parent worlds are baseline-feasible;
- learned-U causality is TRUE;
- H remains teacher;
- every baseline-feasible pair passes every preservation gate;
- median completion-area ratio >= 0.95;
- zero incorrect DONE occurs.

MECHANICAL GATE BEFORE LU2PF1

Prove:

1. exact LU-2N dynamics unchanged;
2. exact canonical weight SHA;
3. alpha exactly 0.25;
4. U_A0 exact teacher parity;
5. H/C/S/FC/FS teacher exact;
6. OBS-V1 unchanged;
7. load one request per epoch;
8. contiguous lesion exactly 16 cells;
9. lesion window [96,108);
10. expiry remains 32;
11. Task-2 stage semantics unchanged;
12. maturity boundary exactly detection <=156;
13. terminal progress rules for detection 157/158/159 exactly as preregistered;
14. no drain epochs;
15. common paired transition variates;
16. no model RNG;
17. no primary manifest during gate;
18. duplicate mechanical evidence byte-identical.

NO POST-RESULT TUNING

After LU2PF1 do not change:

maturity boundary;
terminal in-flight stage rules;
lesion geometry;
lesion size;
lesion duration;
load;
expiry;
alpha;
weights;
OBS-V1;
Task-2 dynamics;
corruption;
repair;
verification;
phase structure;
manifest count;
qualification bars;
common-random policy.

NEXT STEP RULE

If TRUE:
contiguous 25-percent damage robustness is qualified under a physically
feasible repair evaluation contract. Increase task distance next, not
learned authority.

If FALSE with exact-parent coverage:
diagnose the narrowest learned-vs-parent preservation failure.

If FALSE from exact-parent coverage:
diagnose remaining exact-parent capacity failure before any learned-U
conclusion.

PLAIN-SPEAK QUESTION

We are not giving the organism extra time or making repair easier.

We are only stopping the scorecard from calling a repair broken when the bad
request was first detected on a tick where the remaining required repair
steps could not physically fit before the experiment ended.

Fresh worlds decide whether the neural recruiter still holds up under the
same concentrated sixteen-cell injury once that impossible scoring case is
removed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
