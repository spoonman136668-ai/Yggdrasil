TITLE: LU-1D LU1DF1 IMITATION CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / IMITATION NOT QUALIFIED / GATING HELPS BUT STAY REMAINS OUTSIDE BARS
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
46dd05d8bfe108bf3925d09ba45622a4164601e6

MECHANICAL GATE:
b379c77797b5ecb054a0153c3e45878329de9ff9

LU1DF1:
1609425b3144e66ab373fb5ca7239888883ba351

SEED BINDING:
31c52075b50f3550c132c1019b1e9072447cadd0

DUPLICATE TRAINING GATE:
c34ef36b4a9adf2b6e3003fd432a6353e2a7baf1

FROZEN SOURCE SHA256:
8d74638a49c3206f5fa7461967de1d2151be7ef87980a2de86f5d83076934b1f

CANONICAL WEIGHT SHA256:
2c8ee801e16dca803eb9a225dc7b711b168840ddb99cd7c93a058d4d4739a3eb

HELD-OUT TEST ARTIFACT

bytes:
1588.

SHA256:
b096114e910cd8226f2b7b7176157b7a0aee2a46cd6d10080b95f7c9255bfe3a.

SCIENTIFIC STATUS

LU1D_IMITATION_QUALIFIED:
FALSE.

H RELEASE

mean absolute error:
0.0097855350.

p99:
0.0423786691.

PASS.

U RECRUITMENT

mean TV:
0.0243193758.

p95:
0.0513469027.

p99:
0.0664115611.

PASS.

C/S STAY-DEFECT

mean absolute error:
0.0231283040.

required:
<=0.02.

FAIL.

p95:
0.1051339701.

p99:
0.2005912924.

required:
<=0.08.

FAIL.

maximum:
0.6327946782.

SYMMETRY

corrected committed canonical identity:
1000 / 1000.

identity rate:
1.0.

student symmetry mean:
0.0045624735.

p99:
0.0309165112.

PASS.

QUIESCENCE

mean U:
0.9963319302.

p01 U:
0.9955227971.

PASS.

PERMUTATION

maximum logit difference:
3.814697265625e-06.

frozen tolerance:
1e-05.

PASS.

OUTPUT SAFETY

finite:
PASS.

bounded / normalized:
PASS.

parameter ceiling:
PASS.

no global/task/future/position feature:
PASS.

COMPARATIVE STAY ERROR

LU-1A flat raw:
mean 0.0427632498;
p99 0.3573133560.

LU-1B focal-side canonical flat:
mean 0.0275619427;
p99 0.2435178667.

LU-1C shared-neighbor mean:
mean 0.0253735475;
p99 0.2891320121.

LU-1D gated pair relational:
mean 0.0231283040;
p99 0.2005912924.

Relative LU-1B -> LU-1D improvement:

mean error reduction:
16.09%.

p99 reduction:
17.62%.

Relative LU-1A -> LU-1D improvement:

mean error reduction:
45.92%.

p99 reduction:
43.87%.

Thus explicit gating supplies real information gain
without adding information or exceeding the original parameter ceiling.

However it does not cross
the unchanged imitation bars.

CAUSAL INTERPRETATION

The learned-updater sequence now shows a consistent pattern.

Focal-side canonicalization:
large improvement.

Generic neighbor sharing:
small / mixed improvement.

Explicit multiplicative gating:
additional improvement.

This supports the diagnosis
that the committed-cell law is difficult
because it is built from exact conditional local relations.

But a generic learned sigmoid gate
still has to discover
the discrete state-conditioned algebra
from continuous approximation alone.

Do not promote LU-1D.

Do not run it closed-loop.

Do not relax the bars.

Do not merely widen the gate.

NEXT AUTHORIZED STEP

Run an observation-only LU-1D residual audit
against the already-open test set.

If the same ECHO / mode conditionality remains,
preregister one state-conditioned equivariant experiment
that exposes only exact categorical relation structure already present
in OBS-V1,
without exposing derived teacher quantities.

Candidate direction:

use focal-side canonicalization;

split categorical state relations
from continuous local values;

apply shared relation-specific learned transforms
to neighbor B / LC12 / LS12 channels;

retain learned multiplicative gating;

do not precompute mode, pressure, qraw, qecho, qeff,
support margin, teacher probability, or target.

PLAIN-SPEAK INTERPRETATION

The learned gate helped.

It moved us closer again.

But it still does not understand
the commitment rule precisely enough.

We are now at roughly half
the original average error,
yet the worst one percent
is still much too large.

That says the direction is useful,
but the model still spends learning capacity
rediscovering exact categorical relationships
that the hand-designed cell already treats structurally.

The next diagnostic will tell us
whether that is still the same ECHO-under-challenge problem.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
