TITLE: TASK-1F T1FF1-R1 PRIMARY CLOSURE
DATE: 2026-09-22
STATUS: CLOSED / ROBUST LOCAL-H INFORMATION GAIN / FORMAL QUALIFICATION FAIL ON ONE REPAIR-LIFECYCLE CASE
TRACK: DG-1 / TASK-1F

T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063

R1 FIVE-MANIFEST BINDING:
49b12cbb00a75e4949b14866f81bc9e5a8002baa

R1 FROZEN SOURCE SHA256:
a3122a9f4f6da6c138cc12944528f5e2e3ef608e904067ef30da7feab7d640f4

DUPLICATE PRIMARY SWEEPS

runs:
2

replicates per sweep:
5

raw bytes per sweep:
177857

raw SHA256:
24bc9fd29ac7081109e35e8fe84650422dc3aa6edc3c1e2f87dfbc995c818885

byte identical:
true

external open output SHA256:
d3dc430e9e1c1cdb65084cdc9f11fc09391b4557052279b1c72ccb2e86e1bbdd

all integrity probes:
PASS

SCIENTIFIC STATUS

TASK1F_LOCAL_HEDGE_INFORMATION_GAIN:
TRUE

TASK1F_QUALIFIED:
FALSE

INFORMATION-GAIN CHECKS

mechanism active in all five:
PASS.

Phase-0 non-regression in all five:
PASS.

positive Phase-4 gain in at least 4/5:
PASS.
Observed:
5/5.

median Phase-4 gain >=10 percentage points:
PASS.

Median:
31.25 percentage points.

backlog lower in at least 4/5:
PASS.
Observed:
5/5.

median final-16 backlog reduction >=15%:
PASS.

Median:
18.87097%.

new Phase-4 S completion gain in at least 4/5:
PASS.
Observed:
5/5.

incorrect DONE zero and integrity all five:
PASS.

operation cost <=125% paired parent all five:
PASS.

REPLICATE EFFECTS

R1

GLOBAL_HEDGE frozen final-window completion-rate metric:
84.375%.

LOCAL_HEDGE:
125.0%.

Gain:
+40.625 percentage points.

Final-16 backlog reduction:
16.875%.

New Phase-4 S correct DONE:
7 -> 14.

R2

GLOBAL_HEDGE:
93.75%.

LOCAL_HEDGE:
125.0%.

Gain:
+31.25 points.

Backlog reduction:
18.87097%.

New S correct DONE:
1 -> 14.

R3

GLOBAL_HEDGE:
100.0%.

LOCAL_HEDGE:
115.625%.

Gain:
+15.625 points.

Backlog reduction:
11.51203%.

New S correct DONE:
5 -> 11.

R4

GLOBAL_HEDGE:
87.5%.

LOCAL_HEDGE:
128.125%.

Gain:
+40.625 points.

Backlog reduction:
22.96512%.

New S correct DONE:
4 -> 12.

R5

GLOBAL_HEDGE:
93.75%.

LOCAL_HEDGE:
121.875%.

Gain:
+28.125 points.

Backlog reduction:
20.68493%.

New S correct DONE:
0 -> 10.

NOTE ON COMPLETION-RATE METRIC

The frozen final-window metric counts correct completions
during the window relative to the nominal arrival rate.

It may exceed 100%
when the organism drains previously accumulated backlog.

No metric definition is changed after observing the result.

QUALIFICATION CHECKS

information gain:
PASS.

median LOCAL_HEDGE final-window completion >=85%:
PASS.

LOCAL_HEDGE final-window >=85% in at least 4/5:
PASS.
Observed:
5/5.

anchor-rotation recovery <=8 epochs in at least 4/5:
PASS.

demand-reversal recovery <=8 epochs in all five:
PASS.

lesion criterion in all five:
PASS.

repair detection >=95% in every applicable replicate:
PASS.

Phase-0 non-regression:
PASS.

repair success >=90% in every applicable replicate:
FAIL.

LOCAL_HEDGE REPAIR DETAIL

R1:
13 / 14 correctly completed after detected repair
= 92.857%.

R2:
8 / 9
= 88.889%.
FAIL.

R3:
16 / 16
= 100%.

R4:
11 / 11
= 100%.

R5:
12 / 12
= 100%.

Therefore the frozen universal repair-success condition fails
because exactly one replicate falls below 90%.

Do not average this into a pass.

Do not relax the threshold.

R2 FAILURE LOCALIZATION

The single missing R2 repair completion is request 219.

request:
219.

stream:
S.

created:
epoch 109.

corruption:
applied.

first corrupted egress:
epoch 138.

verification detection:
TRUE.

repair:
performed at epoch 140.

repaired output:
0.

expected truth-table output:
0.

Thus the repair itself is correct.

The request then expires:

epoch 141.

Post-repair verification:
not reached.

verified_after_repair:
FALSE.

Final stage:
EXPIRED.

Therefore the formal repair-success miss is caused by:

correct packet repair

followed by

insufficient remaining request lifetime
for mandatory re-verification.

It is not caused by:

incorrect recomputation;

missed corruption detection;

wrong-side task execution;

or a LOCAL_HEDGE correctness error.

CAUSAL INTERPRETATION

Task-1F strongly confirms the post-Task-1E diagnosis.

The H state was conflating:

global coexistence of C and S work

with

local ambiguity.

Using local C/S evidence only
for H formation and release
produces robust functional information gain
across five fresh manifests.

The effect is not one lucky anchor placement.

Every replicate:

improves the frozen Phase-4 completion metric;

reduces final-window backlog;

increases new relocated S completions;

preserves Phase-0 behavior;

preserves safety;

and stays inside the operation-cost bound.

Thus:

LOCAL AMBIGUITY
IS A BETTER H SEMANTIC
FOR SPATIAL TASK ORGANIZATION
THAN GLOBAL COEXISTENCE.

However Task-1F does not promote the mechanism into V0.

The preregistered qualification gate is FALSE.

The remaining failure is now a distinct task-lifecycle seam:
a detected-and-correctly-repaired request can run out of its
unchanged 32-epoch lifetime before mandatory re-verification.

NEXT JUSTIFIED STEP

Do not reroll Task-1F manifests.

Do not add extra confirmation replicates
to seek a passing repair statistic.

Do not promote LOCAL_HEDGE yet.

First close the repair-lifecycle seam
as a separate causal experiment.

The next experiment may compare
the frozen LOCAL_HEDGE substrate
under one preregistered local repair-service policy
that preserves:

32-epoch expiry;

mandatory post-repair verification;

verification correctness;

request-bound handoff;

task load;

topology;

and all LOCAL_HEDGE equations.

The treatment should target only
service ordering for already-detected repair work.

No expiry extension,
repair threshold tuning,
or result-dependent reroll is justified.

PLAIN-SPEAK INTERPRETATION

The uncertainty fix worked
in all five fresh worlds.

When cells asked:

"is MY neighborhood conflicted?"

instead of:

"is the whole organism doing both kinds of work?"

they reorganized much better.

The new S workplace finally got S-capable cells.

Backlogs fell.

Throughput rose.

And this happened in every fresh world we tested.

But one repaired job failed the final rule.

The repair calculation was right.

The job simply reached repair so late
that it expired before it could be checked one last time.

Our preregistered rule says
that still counts as a failure.

So we record the big positive result honestly,
keep qualification false,
and isolate the repair scheduling problem next.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
