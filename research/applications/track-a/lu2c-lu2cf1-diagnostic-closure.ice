TITLE: LU-2C LU2CF1 DIAGNOSTIC CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / PATH DEPENDENCE WITHOUT U-TV SHIFT SUPPORTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
44b2cf29148f3d2f3ef19815ef23d8c1ed61bb34

LU2CF1:
3bb2eaf473212b13a2703dda048cf98341bfbb5f

MECHANICAL GATE:
c54b8431fa0922ee58381869c3188f77a05f166d

TEN-MANIFEST BINDING:
4f5ad14fcddeaad7be5684d5ced8c68c2acf99b7

PARENT LU2AF1-R1:
ba771ec410b5a35498e0b146e71781ac4df4285c

LU-2B DIAGNOSIS:
c6cee6c747e17e3a45a906ed76d767afe3ec1074

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

BOUND-WORLD INTEGRITY

All ten regenerated diagnostic manifest SHA256 values
matched the committed LU-2C binding exactly.

Canonical ten-manifest bundle:

bytes:
223628

SHA256:
a1e07e11fcaf558dd0964928c4635d0c1ef486d94a4cd9c637782ca3e3f5e641

No world replacement.

No rejection sampling.

No result-dependent selection.

DIAGNOSTIC ARTIFACT

canonical JSON bytes:
248093

SHA256:
763c25040669ad97a37395883f10a0efcdb568eb9069464ad95fe7169bde6d3e

SCIENTIFIC STATUS

LU2C_U_CLOSED_LOOP_SHIFT_SUPPORTED:
FALSE

LU2C_PATH_DEPENDENCE_WITHOUT_TV_SHIFT_SUPPORTED:
TRUE

OVERALL WORLDWISE U-TV RATIOS

Defined:
10 / 10

Worlds with HYBRID mean U TV > TEACHER:
0 / 10

Median HYBRID / TEACHER overall mean-TV ratio:
0.6022310114

Required for overall shift support:
>=1.10
with HYBRID > TEACHER in at least 7 / 10 worlds.

FAILS SHIFT CRITERION decisively.

PHASE-4 WORLDWISE U-TV RATIOS

Defined:
10 / 10

Worlds with HYBRID phase-4 mean U TV > TEACHER:
0 / 10

Median HYBRID / TEACHER phase-4 mean-TV ratio:
0.2618754687

Required for phase-4 shift support:
>=1.15
with HYBRID > TEACHER in at least 7 / 10 worlds.

FAILS SHIFT CRITERION decisively.

POOLED U-TV

TEACHER_TRAJECTORY_U evaluations:
9879

Pooled mean U TV:
0.0409178774

HYBRID_TRAJECTORY_U evaluations:
15428

Pooled mean U TV:
0.0244155358

Thus hybrid-generated U observations
are not harder for the frozen LU-1E U head by TV error.

They are easier on average.

POOLED PHASE-4 U-TV

TEACHER phase-4 evaluations:
1779

Pooled mean U TV:
0.0646333224

HYBRID phase-4 evaluations:
1981

Pooled mean U TV:
0.0180833881

The strongest separation occurs in the opposite direction
from the distribution-shift hypothesis.

PATH DEPENDENCE

State trajectories differ:
10 / 10 worlds.

Worlds with at least one realized learned-controlled H/U difference:
10 / 10.

Total realized learned-controlled H/U transition differences:
384.

Therefore:

small learned-vs-teacher probability differences
produce persistent trajectory divergence
despite no increase in U approximation error
on hybrid-generated closed-loop observations.

WORLDWISE OVERALL MEAN-TV RATIOS

1:
0.5647244703

2:
0.6698428104

3:
0.6220755802

4:
0.6014596773

5:
0.5765758063

6:
0.6030023456

7:
0.5831806175

8:
0.6519882330

9:
0.5006440569

10:
0.6208884634

WORLDWISE PHASE-4 MEAN-TV RATIOS

1:
0.2176551867

2:
0.3343695057

3:
0.3488429526

4:
0.3345254214

5:
0.2538785883

6:
0.2496092246

7:
0.2067942403

8:
0.4435158280

9:
0.2635552810

10:
0.2601956565

CAUSAL INTERPRETATION

The LU-2B confirmation miss
is not explained by the U head becoming less accurate
on states created by its own closed-loop decisions.

The evidence points instead to developmental amplification:

a small local U probability change
changes one or more recruitment outcomes;

those outcomes change the cell-state allocation;

the changed allocation changes later local observations and service capacity;

and the trajectory does not necessarily reconverge.

This explains how a learned U head
can remain locally close to the teacher
while still producing a materially different organism-level trajectory.

The developmental substrate is path-sensitive.

That property is scientifically useful,
but it makes learned authority boundaries important.

DECISION

Do not retrain the same U head
on the assumption that ordinary closed-loop distribution shift
caused the LU-2B miss.

Do not promote full learned U authority.

Do not widen learned authority.

Do not relax the LU-2B functional bars.

The next justified experiment
should test whether limiting the magnitude
of learned U intervention
reduces trajectory amplification.

A diagnostic authority-dose experiment
is preferred before inventing a confidence gate.

Reason:

a dose-response can determine whether
organism-level divergence scales with
the amount of learned probability substitution.

This is a cleaner causal test
than immediately introducing a new gating heuristic.

PLAIN-SPEAK INTERPRETATION

The neural recruiter is not getting worse
because it creates strange new situations.

The opposite happened.

On the neural organism's own trajectory,
its recruitment predictions were actually closer
to the hand-written rule.

But tiny recruitment differences still changed real cell decisions.

Those changed cells then changed
what happened later.

That effect compounded.

So the issue is not mainly
"the neural model sees unfamiliar states."

It is:

"this developmental system remembers small early differences
because those differences alter what the organism becomes."

That means the next question should be
how much learned authority the system can tolerate
before those small differences amplify too far.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
