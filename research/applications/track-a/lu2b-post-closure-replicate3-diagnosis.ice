TITLE: LU-2B POST-CLOSURE REPLICATE-3 DIVERGENCE DIAGNOSIS
DATE: 2026-09-23
STATUS: OBSERVATION-ONLY / NO RETRAINING / NO THRESHOLD CHANGE
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU-2B CLOSURE:
b2382bf65dbd239b1b53721f63c01d8c01dca9b6

CONFIRMATION HARNESS:
ce52acc9826eb9c385a022dba9abdcbe19797472

PARENT LU2AF1-R1:
ba771ec410b5a35498e0b146e71781ac4df4285c

PURPOSE

Diagnose the single failed LU-2B preservation bar
without tuning on the failed world.

FAILED WORLD

replicate:
3

only failed bar:

Phase-4 paired final-window completion gap.

teacher:
1.25

hybrid:
1.09375

paired difference:
-0.15625

allowed:
>= -0.10

absolute hybrid Phase-4 bar:
>=0.85

observed:
1.09375

PASS.

ANCHOR RELOCATION

teacher recovery latency:
1 epoch

hybrid recovery latency:
0 epochs

Therefore the miss is not
failure to recover from anchor relocation.

INGRESS

teacher final-16 raw ingress backlog area:
147

hybrid:
109

Hybrid is lower.

teacher zero-eligible-ingress epochs:
0

hybrid:
0

Therefore the miss is not
gross ingress starvation.

STREAM SPLIT — NEW PHASE-4 REQUESTS

C arrivals:
32 / 32

teacher C correct DONE:
22

hybrid C correct DONE:
20

difference:
-2

S arrivals:
32 / 32

teacher S correct DONE:
8

hybrid S correct DONE:
6

difference:
-2

Therefore the miss is not
a single-stream collapse.

PHASE-4 TOTAL

teacher correct DONE:
30 / 64

hybrid:
26 / 64

teacher median latency:
10

hybrid:
11.5

teacher p90 latency:
24

hybrid:
26

teacher mean epoch backlog:
40.6875

hybrid:
41.15625

teacher Phase-4 operations per correct completion:
13.2333333333

hybrid:
14.4230769231

The hybrid therefore has
a modest downstream service-efficiency deficit
during the relocation phase.

FINAL-WINDOW ORGANIZATION

teacher active cells:
43

hybrid:
42

teacher active PROCESS cells:
17

hybrid:
16

teacher active ROUTE cells:
39

hybrid:
38

teacher active VERIFY cells:
17

hybrid:
15

teacher active SENSE cells:
8

hybrid:
9

The hybrid retains strong organization
but allocates slightly less downstream
PROCESS / ROUTE / VERIFY service capacity.

PHASE-4 MATCHES

teacher NEW4 PROCESS:
47

hybrid:
44

teacher NEW4 ROUTE:
269

hybrid:
251

teacher NEW4 VERIFY:
31

hybrid:
27

teacher LEGACY ROUTE:
260

hybrid:
254

These deficits are consistent with
slower backlog drain after relocation.

LEGACY HANDOFF

teacher legacy unfinished at epoch 128:
46

hybrid:
47

teacher legacy completion after relocation:
46 / 46

hybrid:
47 / 47

Both:
100 percent.

Therefore the hybrid does not strand legacy work.

It completes all inherited work,
but the altered allocation trajectory
reduces new Phase-4 service throughput.

CAUSAL CONTROL

replicate-3 H evaluations:
4

realized H transition differences:
0

replicate-3 U evaluations:
1262

realized U transition differences:
33

first causal divergence epoch:
5

epochs with different state vector:
155

later trajectory reconvergence:
FALSE

Therefore the failed-world divergence
is attributable to learned U recruitment,
not a realized learned H-release decision.

DIAGNOSIS

The LU-2B miss is not:

anchor-recovery failure;

ingress starvation;

single-stream collapse;

legacy-work loss;

safety failure;

or learned H-release failure.

The evidence is most consistent with:

small learned U recruitment deviations
changing the persistent spatial/state allocation trajectory;

that trajectory carrying slightly less
PROCESS / ROUTE / VERIFY capacity
into the final relocation window;

and therefore clearing backlog more slowly
than the paired teacher in one world.

This is a closed-loop distribution/allocation sensitivity problem.

It is not evidence that the organism collapses under learned control.

It is sufficient evidence
that universal promotion is not yet justified.

NEXT SCIENTIFIC QUESTION

Before any retraining,
test whether the LU-1E U head's approximation error
changes systematically between:

teacher-generated closed-loop U observations;

and hybrid-generated closed-loop U observations,

especially after demand reversal,
lesion,
and anchor relocation.

Use fresh diagnostic worlds.

Do not reuse LU-2B replicate 3 for training.

Do not alter weights.

Do not change H authority.

Do not change C/S authority.

Do not relax qualification bars.

If hybrid-generated U states show
materially higher teacher-vs-learned TV
than teacher-generated U states,
then distribution shift is supported.

If U TV remains comparable
but functional divergence persists,
then even small unbiased U approximation errors
may be amplified by developmental path dependence,
and the next authority boundary should become narrower
rather than simply retraining the same head.

PLAIN-SPEAK INTERPRETATION

The neural organism did not fail to move.

It moved faster than the hand-written one.

It did not run out of sensing capacity either.

The difference was subtler.

Early neural recruitment choices
put the cells onto a slightly different developmental path.

That path persisted.

By the final relocation phase,
the neural organism had about the same overall workforce,
but a little less of it was doing
processing,
routing,
and verification.

That was enough to finish four fewer new jobs
during the phase
and clear old backlog more slowly.

So the next question is not
"make the neural network bigger."

It is:

does the neural recruitment head become less accurate
on the kinds of cell states
its own decisions create in closed loop?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
