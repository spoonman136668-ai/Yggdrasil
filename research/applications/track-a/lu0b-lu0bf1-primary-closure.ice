TITLE: LU-0B LU0BF1 PRIMARY CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / GLOBAL POOL PREVALENT IN NATURAL V0.1 TRAJECTORIES
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
fc0332e5ab625e5aa05b931dbf47a43034760dfd

MECHANICAL GATE:
82b8fec283abcb0bf3e037d7227abe02b8deed18

LU0BF1:
3cbcb11042a177e76db8877a6e5d826aaa7aa9c7

FIVE-MANIFEST BINDING:
5babec4928b4d8794d9273e927da9def13293bea

FROZEN SOURCE SHA256:
b2ef10e618871a081871d8858b3fcd153228cb831a643dc068bd3b30d9f6358f

PARENT V0.1:
4d3887fba0478bc1ef3bc4bea44f8e08582f5803

LU-0 CLOSURE:
074513c64a64318053fcbfcabdc9207202849063

DUPLICATE PRIMARY SWEEPS

runs:
2

worlds per sweep:
5

raw bytes per sweep:
166514

raw SHA256:
e9c43f019f1b46f976e7b7e941d3026a87530414a0fb34e8b600db332388d861

byte identical:
true

external open bytes:
170612

external open SHA256:
bf26d5cb47bf03863e57b782ec58da3eaaf2ebc0d03f6585b31b1741547e486b

all integrity probes:
PASS

SCIENTIFIC STATUS

LU0B_DIRECTIONAL_POOL_PREVALENT:
TRUE

LU0B_RATE_POOL_PREVALENT:
TRUE

LU0B_POOL_PRACTICALLY_NEGLIGIBLE:
FALSE

DIRECTIONAL PREVALENCE

Frozen threshold:

median across worlds
fraction(TV_side >= 0.05)
>= 0.10.

Observed median:
0.9483146067.

Equivalent:
94.8315% of directional U-recruitment evaluations
in the median world
shifted by at least five percentage points
when pc/ps were removed from the shadow calculation.

Frozen side-flip requirements:

at least 4/5 worlds
contain at least one C/S side flip;

pooled side-flip fraction >= 0.02.

Observed:

worlds with side flip:
5 / 5.

Pooled side-flip fraction:
0.07720588235.

Equivalent:
7.7206%.

Therefore the directional prevalence gate
passes decisively.

RATE PREVALENCE

Frozen threshold:

median across worlds
fraction(R_rate >= 0.10)
>= 0.25.

Observed median:
0.9893162393.

Equivalent:
98.9316% of U-recruitment evaluations
in the median world
change C/S recruitment rate
by at least 10%
under the no-pool shadow.

Worlds with nonzero
R_rate >= 0.10 prevalence:
5 / 5.

Therefore the rate prevalence gate
passes decisively.

WORLD SUMMARIES

R1

U evaluations:
451.

Directional evaluations:
425.

mean TV_side:
0.2768964881.

median TV_side:
0.2647364024.

p90 TV_side:
0.4847328946.

fraction TV_side >= 0.05:
0.9317647059.

side flips:
30.

side-flip fraction:
0.07058823529.

mean R_rate:
0.6519505779.

median R_rate:
0.7096695051.

fraction R_rate >= 0.10:
0.9955654102.

fraction R_rate >= 0.50:
0.7450110865.

R2

U evaluations:
432.

Directional evaluations:
400.

mean TV_side:
0.2800157783.

median TV_side:
0.2770879408.

p90 TV_side:
0.4730292342.

fraction TV_side >= 0.05:
0.94.

side flips:
29.

side-flip fraction:
0.0725.

mean R_rate:
0.6216937694.

median R_rate:
0.6696441633.

fraction R_rate >= 0.10:
0.9606481481.

fraction R_rate >= 0.50:
0.7013888889.

R3

U evaluations:
468.

Directional evaluations:
431.

mean TV_side:
0.3076707987.

median TV_side:
0.3060884973.

p90 TV_side:
0.4797108231.

fraction TV_side >= 0.05:
0.9814385151.

side flips:
45.

side-flip fraction:
0.1044083527.

mean R_rate:
0.6634970354.

median R_rate:
0.7036612130.

fraction R_rate >= 0.10:
0.9893162393.

fraction R_rate >= 0.50:
0.7542735043.

R4

U evaluations:
472.

Directional evaluations:
445.

mean TV_side:
0.2786216784.

median TV_side:
0.2782819423.

p90 TV_side:
0.4564316143.

fraction TV_side >= 0.05:
0.9483146067.

side flips:
34.

side-flip fraction:
0.07640449438.

mean R_rate:
0.6147925143.

median R_rate:
0.6670653638.

fraction R_rate >= 0.10:
0.9682203390.

fraction R_rate >= 0.50:
0.6631355932.

R5

U evaluations:
504.

Directional evaluations:
475.

mean TV_side:
0.3071439684.

median TV_side:
0.3051644929.

p90 TV_side:
0.4738152841.

fraction TV_side >= 0.05:
0.9894736842.

side flips:
30.

side-flip fraction:
0.06315789474.

mean R_rate:
0.6411732890.

median R_rate:
0.6856881306.

fraction R_rate >= 0.10:
0.9980158730.

fraction R_rate >= 0.50:
0.7420634921.

POOL OBSERVATION

Mean pc/ps are large in all five natural worlds:

R1:
pc 0.7574;
ps 0.7178.

R2:
pc 0.7444;
ps 0.7954.

R3:
pc 0.7107;
ps 0.7648.

R4:
pc 0.7663;
ps 0.7360.

R5:
pc 0.7637;
ps 0.7365.

Mean absolute pc/ps asymmetry is much smaller:

approximately 0.038 to 0.059.

Therefore the global pool affects U recruitment
not only through directional imbalance.

Its large common-mode magnitude
also changes the inherited nonlinear
support/opposition gates
and total recruitment hazard.

PHASE STRUCTURE

The dependency is not confined
to one perturbation phase.

Large TV_side and R_rate effects
appear during ordinary Phase 0
and again after Phase-4 anchor relocation.

Some low-U-evaluation middle phases
show fewer directional side flips,
but the rate effect remains broadly active.

This confirms that the pool is part of
routine developmental recruitment dynamics,
not merely a rare transition artifact.

CAUSAL INTERPRETATION

LU-0 established:

exact strict-local identifiability is false.

LU-0B now establishes:

the nonlocal pc/ps dependency
is materially prevalent
in naturally reached V0.1 states.

Therefore the learned-updater input problem
cannot be dismissed as
an out-of-distribution corner case.

A strictly local student
that does not receive an equivalent signal
would be asked to approximate
a teacher whose behavior routinely depends
on information outside the student's observation boundary.

That would confound
information sufficiency
with model capacity.

NEXT AUTHORIZED STEP

Per the frozen LU-0B interpretation rule:

preregister a LOCAL POOL REPLACEMENT experiment.

Do not begin strict-local neural-updater training yet.

Do not simply expose pc/ps
as permanent organism-wide broadcast inputs.

First test whether the existing global recruitment-pool function
can be replaced by a bounded local recurrent signal
while preserving useful V0.1 task behavior.

The replacement experiment must:

change only the recruitment-pool source;

preserve LOCAL_HEDGE;

preserve ECHO_PHASE;

preserve Task-1 mechanics;

remain fully local;

use fresh manifests;

include exact GLOBAL_POOL parent;

and include a NO_POOL causal control
so replacement value is distinguishable
from merely deleting the pool.

PLAIN-SPEAK INTERPRETATION

The distant signal matters a lot.

This was not a laboratory edge case.

While V0.1 was doing normal work,
removing the two global pool numbers
changed almost every uncommitted cell's
recruitment strength substantially.

It also changed which side
the cell preferred
about eight percent of the time.

So a tiny local neural cell
would routinely be missing information
if we trained it against V0.1 exactly as it exists today.

Making the neural network bigger
would not fix that.

The next job is to replace
the organism-wide recruitment signal
with something cells can build locally.

If that works,
then the learned cell brain
can stay genuinely local.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
