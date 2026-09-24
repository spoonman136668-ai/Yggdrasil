TITLE: LU-2N LU2NF1 PRIMARY CLOSURE
DATE: 2026-09-24
STATUS: CLOSED / CONTIGUOUS-LESION ROBUSTNESS FALSE / EXACT-PARENT COVERAGE INSUFFICIENT
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
f35e9330ba703fecdcdcfc6b9134b89e07df0dc3

MECHANICAL GATE:
09de01078b6c1ba20de753805fbd969f37ba6232

LU2NF1:
a4657c94a654d2b4f83b6af0c7844b65e6999593

TEN-MANIFEST BINDING:
81c00fc0af062876ffbfaf811369da1be4e2d92c

BOUND PRIMARY RUN:
36056265256

BOUND PRIMARY HEAD:
928e8b772b14784387f19ca13fa2ac6667b23e92

BOUND PRIMARY ARTIFACT:
10832413015

DUPLICATE PRIMARY SWEEPS

bytes each:
216141

SHA256 both:
a742491a9282e346d848850000c0f24a3f6ea7fdf4b8c62eefa35e7f31432d77

byte-identical:
TRUE

EXACT-ARTIFACT QUALIFICATION

run:
36056481917

head:
cc8861b801f46a6110e178538c6eb2d2cc762d17

qualification artifact:
10832956192

SCIENTIFIC STATUS

LU2N_CONTIGUOUS_LESION_ROBUSTNESS:
FALSE

baseline-feasible U_A0 worlds:
7 / 10

required:
>= 8 / 10

evidence coverage:
FAIL

causal learned-U participation across baseline-feasible worlds:
TRUE

H teacher preserved:
TRUE

median paired completion-area ratio across baseline-feasible worlds:
1.0

CAUSAL TOTALS ACROSS BASELINE-FEASIBLE WORLDS

U evaluations:
8526

U evaluations with nonzero teacher-vs-A25 TV:
8526

realized learned-U transition differences:
47

H learned probability differences:
0

H realized learned-controlled differences:
0

BASELINE-INFEASIBLE EXACT-PARENT WORLDS

replicates:
5, 8, 10

All three fail the baseline contract only because repair integrity is incomplete.

replicate 5:
corruptions reaching egress = 10
verification detected = 10
repaired = 9
correct DONE after repair = 9
expired = 0
incorrect DONE = 0

replicate 8:
corruptions reaching egress = 11
verification detected = 11
repaired = 10
correct DONE after repair = 10
expired = 0
incorrect DONE = 0

replicate 10:
corruptions reaching egress = 10
verification detected = 10
repaired = 9
correct DONE after repair = 9
expired = 0
incorrect DONE = 0

In all three:

every phase produced correct DONE;
both C and S streams remained active;
operations per correct completion stayed finite;
matching duplicate-cell and duplicate-request integrity passed;
zero incorrect DONE occurred;
zero request expiry occurred.

Therefore the exact-parent coverage failure is specifically an incomplete
detect -> repair -> reverify service sequence within the fixed 160-epoch
observation horizon, not general task collapse.

PAIRWISE DESCRIPTIVE SIGNAL

Among the seven baseline-feasible pairs, six passed every pairwise gate.

replicate 1 had:

U_A0 anchor-recovery latency = 2
U_A25 anchor-recovery latency = null

while completion area, backlog, demand recovery, lesion recovery, correctness,
repair, and matching remained preserved.

Because the preregistered exact-parent coverage gate already failed, this
secondary learned-arm signal is descriptive only and is not interpreted as
the cause of the LU-2N FALSE result.

DESCRIPTIVE TOTALS ACROSS ALL TEN WORLDS

U_A0 correct DONE:
1459

U_A25 correct DONE:
1460

U_A0 incorrect DONE:
0

U_A25 incorrect DONE:
0

U_A0 expired:
0

U_A25 expired:
0

state-divergence epochs:
967

first divergence epochs:
3, 2, 20, 21, 1, 7, 17, 2, 5, 11

INTERPRETATION

Changing only lesion geometry from distributed 16-cell damage to one
contiguous 16-cell neighborhood crossed a capacity boundary for the exact
hand-written parent under the current 160-epoch Task-2 evaluation contract.

The experiment therefore cannot support a learned-U robustness conclusion.

It also does not support a learned-U regression conclusion.

The exact parent itself misses the preregistered 8/10 baseline coverage bar.

The failure is narrow: work continues in every phase and stream, no wrong
answers occur, no jobs expire, and every corruption reaching egress is
detected in the three failed exact-parent worlds. One detected repair sequence
per failed world simply does not complete within the recorded horizon.

NEXT SCIENTIFIC QUESTION

Before changing the environment or authority, determine whether the three
exact-parent failures are finite-horizon truncation or a deeper contiguous-
damage repair-capacity defect.

Run an instrumentation-only replay of the exact accepted LU-2N U_A0 worlds
that records per-corruption service timestamps while requiring the original
160-epoch aggregate outputs to match accepted evidence exactly.

No new world.
No replacement.
No threshold change.
No learner change.

PLAIN-SPEAK INTERPRETATION

Concentrating the same sixteen-cell injury into one neighborhood finally
found a boundary.

But it did not make the organism collapse.

The hand-written parent still handled the task, kept both directions alive,
never produced a wrong answer, and never expired a job.

In three worlds it detected every bad result that reached verification, but
one repair in each world was still unfinished when the 160-epoch test ended.

So the next question is very specific:

did the clock simply stop while a valid repair was in progress, or did
contiguous damage create a real repair-capacity failure?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
