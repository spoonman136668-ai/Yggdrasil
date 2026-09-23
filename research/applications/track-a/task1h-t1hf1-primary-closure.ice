TITLE: TASK-1H T1HF1 PRIMARY CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / STRONG INDEPENDENT LOCAL_HEDGE CONFIRMATION
TRACK: DG-1 / TASK-1H

PREREGISTRATION:
1e284a15d0e176cbee09c57a1e219ba6927f05b0

T1HF1:
2b57ce116fa9a92a5da55399fbdea3737f9aafe8

MECHANICAL GATE:
251f7a789b7a12b40d8dda3fa882f217ec268c2e

FIVE-MANIFEST BINDING:
1d88458c4997a3d57c9439f37f3abb9afde6a751

FROZEN SOURCE SHA256:
076e67aef313943fdcd5545ed8c888b6630431638bd158be4e705d81ebebe445

PARENT TASK-1F T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063

PARENT TASK-1F CLOSURE:
fda86a2fee99fb948524b53b0eb0652011d655f6

SERVICE-ENVELOPE AUDIT:
e6ea693894ab12a6d542d50e297e97abf801124c

DUPLICATE PRIMARY SWEEPS

runs:
2

replicates per sweep:
5

raw bytes per sweep:
183595

raw SHA256:
6357294bb99cdbd252606daa767a4da10ad017f70323afe56b845867173be186

byte identical:
true

external open output bytes:
187672

external open output SHA256:
d1f0a34d64018c507bd10e9af0964fb88b2046f2afaceabecc0c25e778db80c5

all integrity probes:
PASS

SCIENTIFIC STATUS

TASK1H_LOCAL_HEDGE_CONFIRMED:
TRUE

TASK1H_LOCAL_HEDGE_STRONG_CONFIRMATION:
TRUE

CONFIRMATION CHECKS

LOCAL_HEDGE mechanism active in all five:
PASS.

Phase-0 LOCAL_HEDGE >=95% of GLOBAL_HEDGE in all five:
PASS.

Observed Phase-0 completion:
100% / 100%
in every paired replicate.

Positive Phase-4 gain in at least 4/5:
PASS.

Observed:
5/5.

Median Phase-4 gain >=10 percentage points:
PASS.

Observed median:
+21.875 percentage points.

Final-16 backlog lower in at least 4/5:
PASS.

Observed:
5/5.

Median backlog reduction >=15%:
PASS.

Observed median:
18.307692%.

New relocated S completion gain in at least 4/5:
PASS.

Observed:
4/5.

Incorrect DONE = 0 in every LOCAL_HEDGE replicate:
PASS.

LOCAL_HEDGE operations per correct completion
<=125% of GLOBAL_HEDGE in every replicate:
PASS.

Observed ratios:
R1 98.039%;
R2 91.477%;
R3 94.726%;
R4 93.848%;
R5 96.539%.

All integrity probes:
PASS.

STRONG CONFIRMATION CHECKS

Median LOCAL_HEDGE Phase-4 final-window completion >=85%:
PASS.

Observed median:
125.0%.

The frozen metric may exceed 100%
when the final window drains backlog
created before that window.
The metric definition is unchanged.

At least 4/5 LOCAL_HEDGE replicates
Phase-4 final-window completion >=85%:
PASS.

Observed:
5/5.

Anchor-rotation recovery <=8 epochs
in at least 4/5:
PASS.

Observed LOCAL_HEDGE recovery latencies:
R1 0;
R2 0;
R3 1;
R4 0;
R5 0.

Demand-reversal recovery <=8 epochs in all five:
PASS.

Observed:
R1 0;
R2 1;
R3 2;
R4 1;
R5 0.

Lesion recovery criterion in all five:
PASS.

LOCAL_HEDGE lesion recovery latencies:
R1 0;
R2 2;
R3 0;
R4 0;
R5 0.

PAIRED PHASE-4 EFFECTS

R1

GLOBAL_HEDGE:
103.125%.

LOCAL_HEDGE:
125.0%.

gain:
+21.875 points.

final-16 backlog:
596 -> 512.

backlog reduction:
14.094%.

new relocated S correct completions:
6 -> 12.

R2

GLOBAL_HEDGE:
62.5%.

LOCAL_HEDGE:
131.25%.

gain:
+68.75 points.

final-16 backlog:
817 -> 525.

backlog reduction:
35.741%.

new relocated S correct completions:
4 -> 13.

R3

GLOBAL_HEDGE:
121.875%.

LOCAL_HEDGE:
125.0%.

gain:
+3.125 points.

final-16 backlog:
650 -> 531.

backlog reduction:
18.308%.

new relocated S correct completions:
9 -> 15.

R4

GLOBAL_HEDGE:
90.625%.

LOCAL_HEDGE:
112.5%.

gain:
+21.875 points.

final-16 backlog:
778 -> 599.

backlog reduction:
23.008%.

new relocated S correct completions:
8 -> 6.

R5

GLOBAL_HEDGE:
115.625%.

LOCAL_HEDGE:
134.375%.

gain:
+18.75 points.

final-16 backlog:
666 -> 560.

backlog reduction:
15.916%.

new relocated S correct completions:
8 -> 16.

MECHANISM ACTIVITY

The local ambiguity mechanism was active in every replicate.

Observed H-semantic change-event counts:
R1 453;
R2 623;
R3 541;
R4 499;
R5 466.

Thus the confirmation is not produced
by an inert treatment label.

REPAIR / SERVICE-ENVELOPE REPORTING

These metrics are descriptive only
under the frozen Task-1H preregistration.

R1:
repair detection 100%;
repair success 100%;
deadline-impossible detections 0.

R2:
repair detection 100%;
repair success 93.75%;
deadline-impossible detections 1:
request 126.

R3:
repair detection 100%;
repair success 100%;
deadline-impossible detections 0.

R4:
repair detection 100%;
repair success 94.444%;
deadline-impossible detections 1:
request 237.

R5:
repair detection 93.75%;
repair success 93.333%;
deadline-impossible detections 1:
request 130.

Horizon-censored correctly repaired requests:
0 across all five LOCAL_HEDGE replicates.

The repair observations are consistent
with the already-frozen Task-1 service-envelope diagnosis.

They do not enter Task-1H confirmation
and do not retroactively alter
Task-1F or Task-1G qualification.

CAUSAL INTERPRETATION

Task-1F found robust causal information gain
from changing H from global coexistence semantics
to local ambiguity semantics.

Task-1H independently repeats that result
on five new worlds derived only after T1HF1 froze.

Across the confirmation set:

Phase-4 completion improves in 5/5;

final-window backlog falls in 5/5;

new relocated S completion improves in 4/5;

Phase-0 remains exactly preserved;

demand reversal remains fast;

lesion recovery remains fast;

anchor relocation recovers within one epoch in every replicate;

incorrect DONE remains zero;

and operation cost does not increase.

Therefore the evidence now supports:

LOCAL AMBIGUITY
IS A REPLICATED BETTER H SEMANTIC
FOR THIS FROZEN DEVELOPMENTAL SUBSTRATE
UNDER SPATIAL TASK REORGANIZATION.

HISTORICAL BOUNDARY

Do not rewrite prior outcomes.

Task-1F remained formally unqualified
because of its frozen universal repair-success condition.

Task-1G remained negative
for repair-critical EDF.

The service-envelope audit showed
those repair misses can arise from
deadline impossibility / finite benchmark lifetime,
not LOCAL_HEDGE failure.

Task-1H does not edit those thresholds.

Its strong confirmation is an independent
mechanism-replication result.

NEXT AUTHORIZED STEP

The preregistered V0.1 decision rule is satisfied.

A separate architecture decision may now promote:

LOCAL_HEDGE

from experimental candidate

to:

Developmental Substrate V0.1
default H formation / release semantics.

That architecture decision must preserve
all other V0 mechanisms and boundaries
unless separately supported by evidence.

PLAIN-SPEAK INTERPRETATION

We gave the uncertainty rule
five completely new worlds
and asked it to prove itself again.

It did.

In every world,
using local uncertainty
helped the organism move work
after the workplace moved.

The backlog also fell
in every world.

The system did not pay for that
by getting worse before the move,
making incorrect answers,
or using more work per successful job.

One world did not improve
the specific count of new S jobs,
but the preregistered rule required four of five
and that passed exactly.

The important result is now replicated:

a cell should ask

"IS MY NEIGHBORHOOD AMBIGUOUS?"

not

"IS THE WHOLE ORGANISM DOING BOTH KINDS OF WORK?"

That distinction is strong enough
to justify freezing it
into the next substrate version.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
