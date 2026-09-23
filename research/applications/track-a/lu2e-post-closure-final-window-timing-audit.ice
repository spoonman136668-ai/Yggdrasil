TITLE: LU-2E POST-CLOSURE REPLICATE-3 FINAL-WINDOW TIMING AUDIT
DATE: 2026-09-23
STATUS: OBSERVATION-ONLY / CONFIRMATION RESULT UNCHANGED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU-2E CLOSURE:
64835405e06039396e4b73cc2dbf5e54dab09961

LU2EF1:
377fdc6e3b65fe843f77296cf1bbdc82736813a1

FAILED WORLD:
replicate 3

PURPOSE

Determine whether the LU-2E replicate-3
paired Phase-4 final-window miss
reflects sustained service-capacity loss
or temporal/backlog-history alignment.

No retraining.

No alpha change.

No model change.

No bar change.

No reinterpretation of LU-2E qualification.

FAILED FROZEN METRIC

U_A0 final-16 correct completions:
42

U_A25:
38

Nominal 16-epoch arrival denominator:
32

Rates:

U_A0:
1.3125

U_A25:
1.1875

paired gap:
-0.125

required:
>= -0.10

LU-2E remains FAILED.

PHASE-4 NEW-WORK COMPLETION

New Phase-4 requests correct DONE:

U_A0:
36 / 64

U_A25:
36 / 64

IDENTICAL.

C stream:

21 vs 21.

S stream:

15 vs 15.

Thus the failed raw final-window rate
does not reflect fewer new Phase-4 requests completed overall.

CARRY-IN STATE AT RELOCATION

Backlog at epoch 127:

U_A0:
45

U_A25:
42

Backlog at epoch 128:

U_A0:
46

U_A25:
42

The low-dose arm enters relocation
with less inherited unfinished work.

PRE-PHASE-4 COMPLETIONS

Cumulative completions before epoch 128:

U_A0:
209

U_A25:
214

U_A25 has already completed 5 more requests
before the relocation phase.

PHASE-4 ALL COMPLETIONS

Epoch 128 through 159:

U_A0:
81

U_A25:
78

difference:
-3

This difference is consistent in scale
with the lower carry-in backlog.

FINAL STATE

Final backlog:

U_A0:
28

U_A25:
28

IDENTICAL.

Final-16 backlog area:

U_A0:
490

U_A25:
478

U_A25 is LOWER.

TOTAL RUN COMPLETIONS

U_A0:
290

U_A25:
292

U_A25 is HIGHER by 2.

FINAL-16 COMPLETION SEQUENCES

U_A0:
[5,3,0,4,0,5,3,2,7,2,3,1,0,5,0,2]

U_A25:
[2,1,2,4,2,4,3,1,8,1,1,2,1,3,1,2]

The completion timing differs substantially
despite equal Phase-4 new-request completion totals.

INTERPRETATION

The frozen Phase-4 final-window metric
counts all completions in the window,
including old backlog drained from earlier phases.

Because completion rate is normalized
to nominal new arrivals rather than
available carry-in plus new work,
the metric can exceed 100 percent.

That property was already known.

In LU-2E replicate 3,
the teacher enters Phase 4
with more inherited backlog
and therefore has more old work available to drain
inside the final window.

The low-dose arm enters Phase 4
after having already completed more work.

It completes the same number
of new Phase-4 requests,
ends at the same final backlog,
and has a lower final-window backlog area.

Therefore the observed 12.5-point final-window gap
is not evidence of a sustained deficit
in new Phase-4 functional capacity.

It is substantially influenced by
carry-in backlog history and completion timing.

BOUNDARY

This finding does NOT make LU-2E pass.

The bar was frozen.

LU2E_A25_INDEPENDENT_CONFIRMATION remains FALSE.

Do not alter that record.

MEASUREMENT-DESIGN LESSON

Future preregistered closed-loop evaluations
should separate at least two quantities:

1.
NEW-PHASE SERVICE

completion of requests created
after the relocation boundary;

2.
LEGACY CLEARANCE

fraction / timing of unfinished work
carried into the relocation boundary.

A raw final-window completion count
normalized only by nominal new arrivals
conflates these two quantities
and can reward an arm
for having more backlog available to drain.

Any future metric revision
must be prospective,
preregistered before fresh worlds,
and must not retroactively re-score LU-2E.

NEXT JUSTIFIED QUESTION

Use fresh worlds to test
bounded U_A25 under a decomposed relocation-capacity contract:

new Phase-4 completion;

legacy carry-in clearance fraction;

final backlog;

backlog area;

and inherited safety/cost/recovery measures.

Retain the old raw final-window metric
as descriptive telemetry,
not silently erase it.

Do not use LU-2E replicate 3
as a pass under the new contract.

PLAIN-SPEAK INTERPRETATION

The failed score was real,
but it was measuring two things at once.

The hand-written organism entered the last phase
with more old work still waiting.

That gave it more backlog to finish
during the final 16 epochs,
which pushed its throughput number higher.

The 25-percent neural organism
had already finished more work earlier.

It completed exactly as many new jobs
during the final phase,
ended with the same backlog,
and carried less backlog through the final window.

So the neural version was not simply slower.

The old metric was partly rewarding
the other version for arriving later
with more unfinished work.

We keep LU-2E marked failed.

But future tests should measure
new work and old backlog separately
so this timing effect cannot masquerade
as a capacity failure.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
