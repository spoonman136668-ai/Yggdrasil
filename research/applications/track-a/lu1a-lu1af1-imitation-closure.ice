TITLE: LU-1A LU1AF1 IMITATION CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / IMITATION NOT QUALIFIED / STAY-DEFECT HEAD FAILURE
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
01c5f6b7072b712ac287cc8757e08fb5e96ca6aa

MECHANICAL GATE:
1a89a39c57a36e672cee363a554c0f8a1cf3e7e7

LU1AF1:
d1c6de67fe33cd48d5163dd08dcdc3112c5b0013

SEED BINDING:
67faea47c66c655e3002f782a86baaa7501a33b0

DUPLICATE TRAINING GATE:
3655f3d2911e4edcbed67e77af5deb9299f68340

PARENT V0.2:
e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2

LU-0E CLOSURE:
94eda73cf865a131365ac4cbe943dc558daaece1

FROZEN SOURCE

bytes:
17518

SHA256:
c493e9353b98563139fafb8c5dd5a46b8152b780f6148b248c7e17f57f304700

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

PyTorch:
2.10.0+cpu.

NumPy:
2.3.5.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

DUPLICATE TRAINING

complete runs:
2.

canonical weight bytes:
71105 each.

canonical weight SHA256:
2969022d99944928a12df9d91a96114da877354d433582e20e06d63c3325c12f.

byte identical:
TRUE.

training metrics JSON bytes:
739 each.

training metrics SHA256:
3ed77ad57456ace477cdec30a35f91db60e3b51069706439011ebe00ddd3d69b.

byte identical:
TRUE.

HELD-OUT TEST DUPLICATION

test runs:
2.

test JSON bytes:
1460 each.

test JSON SHA256:
4e7dca93269bf13241633bfcfee4309058870e14787b001a8a31df1ee94076e6.

byte identical:
TRUE.

test examples:
12000.

SCIENTIFIC STATUS

LU1A_IMITATION_QUALIFIED:
FALSE.

The duplicate-training conditions pass.

The held-out imitation metric gate fails.

PASSING HEAD — H RELEASE

mean absolute probability error:
0.0136262647.

required:
<=0.02.

PASS.

95th percentile:
0.0372435510.

99th percentile:
0.0589982109.

required p99:
<=0.08.

PASS.

maximum:
0.1141503155.

Teacher target range:
0.0 to 0.3485609293.

PASSING HEAD — U RECRUITMENT

mean total-variation distance:
0.0195418293.

required:
<=0.03.

PASS.

95th percentile TV:
0.0500642838.

required:
<=0.08.

PASS.

99th percentile TV:
0.0722490808.

required:
<=0.12.

PASS.

maximum TV:
0.1159709245.

Teacher component range:
0.0 to 1.0.

FAILED HEAD — C/S STAY-DEFECT

mean absolute probability error:
0.0427632498.

required:
<=0.02.

FAIL.

95th percentile:
0.1962773263.

99th percentile:
0.3573133707.

required p99:
<=0.08.

FAIL.

maximum:
0.7476477623.

Teacher target range:
0.1111111119 to 1.0.

Thus the first shared MLP
does not approximate the stay-defect law
with sufficient fidelity.

SYMMETRY

mean student C/S symmetry error:
0.0174534330.

required:
<=0.02.

PASS.

99th percentile symmetry error:
0.1334269953.

required:
<=0.08.

FAIL.

Teacher symmetry:
exact.

The symmetry failure is therefore
a student approximation-tail defect,
not a teacher asymmetry.

DEGENERATE QUIESCENCE

mean predicted U probability:
0.9991815090.

required:
>=0.98.

PASS.

1st percentile predicted U probability:
0.9983112216.

required:
>=0.90.

PASS.

minimum:
0.9977979660.

SAFETY / NUMERICS

parameter count:
17734 <=18000.

PASS.

no global/task/future/position feature:
PASS.

all outputs finite:
PASS.

probabilities bounded and normalized:
PASS.

QUALIFICATION CHECKS

PASS:
parameter ceiling.

PASS:
duplicate training canonical weights.

PASS:
duplicate training metrics.

PASS:
local-only feature boundary.

PASS:
H mean error.

PASS:
H p99 error.

FAIL:
STAY mean error.

FAIL:
STAY p99 error.

PASS:
U mean TV.

PASS:
U p95 TV.

PASS:
U p99 TV.

PASS:
symmetry mean.

FAIL:
symmetry p99.

PASS:
quiescence mean U.

PASS:
quiescence p01 U.

PASS:
finite outputs.

PASS:
normalized outputs.

INTERPRETATION

The first learned cell is not a general failure.

Two of the three stochastic V0.2 decision families
are already learned inside the frozen error bars:

H release;

U recruitment.

The remaining failure is concentrated
in the committed C/S stay-defect law.

This is scientifically useful localization.

Do not:

place LU-1A into closed-loop Task-1 dynamics;

promote it into the substrate;

increase model size after seeing this result;

change the learning rate;

change the loss;

change OBS-V1;

change the error thresholds;

or retrain the same frozen experiment.

NEXT AUTHORIZED STEP

Run an observation-only diagnostic
on the already-open held-out test set
and canonical LU-1A weights.

The diagnostic may stratify
the failed stay-defect errors by:

C versus S;

support versus challenge versus neutral regime;

ECHO/Q activity;

B magnitude / sign;

local support-margin terms;

teacher probability range;

and distance to any sharp teacher-law boundary.

It may not retrain,
change weights,
or test alternate hyperparameters.

Use that diagnosis
to preregister one narrow LU-1B repair experiment.

PLAIN-SPEAK INTERPRETATION

The first neural cell learned two jobs well.

It learned:

when uncertainty should release;

and what an uncommitted cell should become.

It did not learn the third job well enough:

when an already committed cell
should hold its ground
or defect.

The average miss there
was about 4.3 percentage points,
and the hard tail was much worse.

That also explains
why a small number of C/S-swapped examples
broke the symmetry limit.

So we do not put this neural cell
inside the organism yet.

We also do not start turning knobs.

The next step is to examine
exactly which stay/defect situations
the network misunderstood.

That will tell us whether the problem is:

a sharp rule boundary;

the echo-memory interaction;

the representation;

or insufficient function shape
for this particular head.

LU-1A is a negative qualification result,
but it is a useful one:
the learned-updater problem
has narrowed from three behaviors
to one.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
