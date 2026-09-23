TITLE: LU-0 LU0F1 PRIMARY CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / STRICT-LOCAL IDENTIFIABILITY FALSE / MATERIALITY GATE INCOMPLETE
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
d560e9ae69b4aee92882b7d535e729605beb037b

MECHANICAL GATE:
248bb45d46b61d466d46910cbd06f7b5a81495fe

LU0F1:
67b4c725193c6af707f5d3937d6854006704bfaa

PARENT V0.1:
4d3887fba0478bc1ef3bc4bea44f8e08582f5803

FROZEN SOURCE SHA256:
c77dd0cb2e7c919f2ec7fafc12aa0eae5509c36d82c468a41ad68a70e4401dcd

DUPLICATE PRIMARY

runs:
2

bytes each:
6509

SHA256:
29f918bf4742bb1fd77e1d0f9dd7ee115820a422293e75c39622b85fdc501f78

byte identical:
true

external open bytes:
6644

external open SHA256:
30e31c0e3f57214b5bedb03108f24fefbcca96260b9f3cd0a31853a0672029e1

PRIMARY STATUS

LU0_STRICT_LOCAL_IDENTIFIABLE:
FALSE

LU0_MATERIAL_POOL_DEPENDENCE:
FALSE

PAIR COUNT:
12

All pair local signatures byte-identical:
PASS.

SCIENTIFIC RESULT

Median total-variation distance:
0.0728829581.

Equivalent probability-mass shift:
7.2883 percentage points.

Maximum total-variation distance:
0.1013271514.

Equivalent maximum probability-mass shift:
10.1327 percentage points.

Thus the two preregistered magnitude bars:

median TV >= 0.05;

max TV >= 0.10;

both pass.

However the third materiality bar required:

all four DC-versus-DS local templates
to flip the higher-probability C/S recruitment side.

Observed:
2 / 4.

Therefore:

LU0_MATERIAL_POOL_DEPENDENCE = FALSE.

Do not weaken the 4/4 criterion.

CONSTRUCTIVE NONIDENTIFIABILITY

The following fact is established directly:

two V0.1 probe cells
can have byte-identical complete radius-12 local signatures

while

the exact V0.1 U-cell transition distributions differ.

Therefore a strictly radius-12 local student,
given only the audited local signature,
cannot reproduce the exact V0.1 U-recruitment distribution
for every valid state.

This is an information limitation,
not a neural-network capacity result.

PAIR RESULTS

L0 / DC vs DS:
TV 0.0979817159.
C -> S side flip.

L0 / DC vs D0:
TV 0.0758101773.

L0 / DS vs D0:
TV 0.0758101773.

L1 / DC vs DS:
TV 0.1011958934.
C remains preferred.

L1 / DC vs D0:
TV 0.0699557390.

L1 / DS vs D0:
TV 0.0680013844.

L2 / DC vs DS:
TV 0.1011958934.
S remains preferred.

L2 / DC vs D0:
TV 0.0680013844.

L2 / DS vs D0:
TV 0.0699557390.

L3 / DC vs DS:
TV 0.1013271514.
C -> S side flip.

L3 / DC vs D0:
TV 0.0619985734.

L3 / DS vs D0:
TV 0.0619985734.

POOL RANGE OBSERVED IN CONSTRUCTED PAIRS

Representative DC / DS pool values reached:

pc approximately 0.319 to 0.350
against
ps approximately 0.038 to 0.075,

with the directional mirror
under DS.

Local signatures remained identical.

INTERPRETATION

LU-0 closes one question:

EXACT STRICT-LOCAL DISTILLATION
OF THE CURRENT V0.1 TEACHER
IS NOT GENERALLY IDENTIFIABLE.

The remaining question is prevalence.

The constructed counterfactuals show
probability effects large enough
to pass both magnitude thresholds,

but not broad enough across local templates
to satisfy the preregistered
4/4 directional-flip criterion.

Therefore LU-0 does NOT yet authorize:

removing pc/ps;

replacing the global pool;

or permanently exposing pc/ps
to a learned updater.

NEXT REQUIRED STEP

Per the preregistered interpretation rule:

run a fresh-trajectory prevalence audit.

The next experiment must use
fresh V0.1 task trajectories
not used by Task-1F or Task-1H
and measure how often the organism-wide pool
materially changes U recruitment distributions
under naturally reached states.

No neural network is required yet.

No architecture change is authorized yet.

PLAIN-SPEAK INTERPRETATION

We proved that a local neural cell
sometimes would not have enough information
to copy V0.1 exactly.

Two cells can see
the exact same neighborhood

and still receive different instructions
from the hand-written organism

because of activity far away.

The difference was not microscopic:
the typical constructed shift
moved about seven percent
of the transition probability,
and the largest moved about ten percent.

But our stricter rule also asked
whether distant demand
would reverse the preferred C/S direction
in every local situation we tested.

It only did that in two of four.

So we do not redesign the organism yet.

Now we ask the more important practical question:

HOW OFTEN DOES THIS NONLOCAL DEPENDENCY
ACTUALLY MATTER
IN REAL V0.1 TRAJECTORIES?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
