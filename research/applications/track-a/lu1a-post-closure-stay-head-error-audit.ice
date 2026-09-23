TITLE: LU-1A POST-CLOSURE STAY-HEAD ERROR AUDIT
DATE: 2026-09-23
STATUS: OBSERVATION-ONLY DIAGNOSTIC / NO RETRAINING
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1AF1:
d1c6de67fe33cd48d5163dd08dcdc3112c5b0013

LU-1A CLOSURE:
5c81b6f38f9a0b4d05ccbcaad89ef7c2a9d7e745

CANONICAL WEIGHT SHA256:
2969022d99944928a12df9d91a96114da877354d433582e20e06d63c3325c12f

PURPOSE

Localize the already-observed
C/S stay-defect imitation failure.

This audit is observation-only.

It does not:

retrain;

change weights;

change OBS-V1;

change thresholds;

evaluate alternate model sizes;

or select a new hyperparameter.

SOURCE EVIDENCE

Frozen held-out LU-1A test set.

Stay examples:
6000.

C:
3000.

S:
3000.

DIAGNOSTIC ARTIFACT

bytes:
12572.

SHA256:
a7638fc440886f2c5940c529533d8c64268d8f011decba57949bee024675f769.

OVERALL STAY ERROR

mean absolute error:
0.0427632498.

p95:
0.1962773263.

p99:
0.3573133560.

maximum:
0.7476477921.

C VS S

C mean:
0.0443489533.

S mean:
0.0411775463.

C p99:
0.3626913494.

S p99:
0.3570871468.

Therefore the failure is not
a one-sided C-only or S-only defect.

LOCAL MODE STRATIFICATION

SUPPORT

n:
2682.

mean absolute error:
0.0204284249.

p99:
0.1927426121.

NEUTRAL

n:
788.

mean absolute error:
0.0167185452.

p99:
0.2662934597.

CHALLENGE

n:
2530.

mean absolute error:
0.0745518773.

p99:
0.4542420521.

Thus CHALLENGE examples
are the dominant failure regime.

ECHO STRATIFICATION INSIDE CHALLENGE

CHALLENGE with ECHO/Q dominating current qraw:

n:
799.

mean absolute error:
0.1172127777.

p95:
0.3950773090.

p99:
0.5756875360.

maximum:
0.7476477921.

mean signed bias:
-0.0632193466.

The student systematically underestimates stay probability
in this regime.

CHALLENGE without ECHO dominance:

n:
1731.

mean absolute error:
0.0548603352.

p99:
0.2614373773.

Thus ECHO dominance is the strongest concentration,
but CHALLENGE remains harder
even when current qraw dominates.

NON-CHALLENGE

n:
3470.

mean absolute error:
0.0195859508.

This is approximately at
the frozen LU-1A mean-error bar.

PRESSURE / TEACHER SHAPE

The exact teacher law is:

pressure
=
max(
0,
opposition
-
own_aligned_B
-
Q_eff
)

only in CHALLENGE,
with Q_eff = max(qraw,qecho).

Then:

p_stay = 1
for pressure <= 0,

otherwise:

1 / [1 + (pressure / 0.5)^3].

The largest errors occur
when ECHO almost cancels opposition,
leaving a small positive pressure
and therefore a teacher stay probability
very near 1.

Representative worst case:

state:
C.

mode:
CHALLENGE.

opposition:
0.920000017.

own aligned evidence:
0.

qraw:
0.

qecho:
0.876724303.

pressure:
0.043275714.

teacher stay:
0.999352038.

student stay:
0.251704246.

absolute error:
0.747647792.

This is not missing information.

OBS-V1 contains all required values.

It is a learned relational/gating failure.

CORRELATION WITH ABSOLUTE ERROR

opposition:
+0.461778.

pressure:
+0.322720.

qeff:
+0.238720.

qecho:
+0.233370.

own aligned evidence:
-0.257505.

qraw:
+0.036450.

The low qraw correlation
combined with strong ECHO-dominant failure
is consistent with difficulty learning
the conditional relation:

qecho applies only
when qside matches focal committed side,

and only affects pressure
under CHALLENGE.

SYMMETRY BY HEAD

A separate observation-only
2000-example symmetry audit
was stratified by output head.

H RELEASE:

n:
500.

mean symmetry error:
0.0099682167.

p99:
0.0331669316.

fraction >0.08:
0.

PASS-like behavior.

U RECRUITMENT:

n:
500.

mean symmetry TV:
0.0105393842.

p99:
0.0403790659.

fraction >0.08:
0.

PASS-like behavior.

C/S STAY:

n:
1000.

mean symmetry error:
0.0246530656.

p99:
0.1589896721.

fraction >0.08:
8%.

Thus the LU-1A aggregate symmetry-tail failure
is localized to the same stay head.

DIAGNOSIS

The evidence does not justify
a generic increase in capacity.

The failure is concentrated in
a relational symmetry problem:

for a committed C cell,
C is SELF and S is OPPONENT;

for a committed S cell,
S is SELF and C is OPPONENT.

Likewise:

B sign;

LC/LS;

Q_prev_side;

same-side neighbor identity

must all be interpreted
relative to the focal committed side.

LU-1A asked a generic MLP
to discover this coordinate transformation
from data
while simultaneously learning
the max/gating/Hill stay law.

The H and U heads do not show
the same failure.

NEXT JUSTIFIED EXPERIMENT

Use a deterministic,
information-preserving
focal-side canonical transform
for C/S stay examples only.

For focal C:
identity.

For focal S:

C <-> S state labels;

FC <-> FS labels;

B -> -B;

LC12 <-> LS12;

LC3 <-> LS3;

Q_prev_side C <-> S.

After canonicalization,
the focal committed state is always C/SELF
for the stay head.

Do not add:

pressure;

qraw;

qeff;

challenge flag;

teacher probability;

or any new derived teacher answer.

This transform adds no information.

It only expresses the same OBS-V1
in a focal-relative coordinate frame.

Retain:

the same MLP size;

same optimizer;

same loss;

same data counts;

same epoch count;

same qualification thresholds.

This is the narrowest repair
supported by the observed failure.

PLAIN-SPEAK INTERPRETATION

The neural cell did not fail
because it was too small everywhere.

It failed on one kind of reasoning:

when a committed cell is under attack,
especially when its one-epoch memory
nearly cancels the attack.

The raw input also makes the network
learn the same rule twice:

once from C's point of view
and again mirrored from S's point of view.

The teacher does not really have two rules.

It has one rule:

ME versus THE OTHER SIDE.

So the next experiment should not
make the neural network bigger.

It should present the same local information
in the same point of view
for every committed cell.

A C cell stays C.

For an S cell,
we flip the local coordinate system
so S becomes SELF
and C becomes OPPONENT.

Nothing new is revealed.

Nothing global is added.

The model simply no longer has to
rediscover a symmetry
we already know is exact.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
