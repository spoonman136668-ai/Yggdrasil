TITLE: LU-1C — STRUCTURED PERMUTATION-INVARIANT LOCAL RELATIONAL UPDATER
DATE: 2026-09-23
STATUS: PREREGISTERED / NO TRAINING EXECUTION
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Test the narrow hypothesis supported by the LU-1B residual audit:

the remaining C/S stay-defect error is caused primarily
by asking a flat MLP to discover repeated local relational structure
and conditional ECHO gating from a 70-value flat vector.

LU-1C changes network geometry only.

It does not add information.

It does not add capacity.

It does not change the teacher.

It does not change training.

It does not relax any qualification bar.

PARENTS

Developmental Substrate V0.2:
e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2

LU-0E staged-local identifiability closure:
94eda73cf865a131365ac4cbe943dc558daaece1

LU-1A closure:
5c81b6f38f9a0b4d05ccbcaad89ef7c2a9d7e745

LU-1B closure:
0579573b3483c17a1932210eca245ec37c65b63e

LU-1B residual diagnostic:
b6957f04bbb9f3f047bbf6f0ff485fe2560c960d

SCIENTIFIC QUESTION

Can a small shared local relational architecture,
using exactly the already-accepted OBS-V1 information,
learn the V0.2 stochastic decision law
inside the unchanged LU-1A/LU-1B error bars?

OBSERVATION

Exactly OBS-V1.

Model-facing information remains 70 scalar values:

seven radius-3 cell slots x nine values each = 63;

plus seven focal extras = 7.

Per cell slot:

six-way state one-hot:
C;
S;
U;
H;
FC;
FS;

B_pre;

LC12;

LS12.

Focal extras:

timer / TIMER_NORM;

Q_prev;

three-way Q_prev_side one-hot:
NONE;
C;
S;

LC3;

LS3.

No feature is added.

No feature is removed.

FOCAL-SIDE CANONICALIZATION

Exactly LU-1B.

For committed focal C:
identity.

For committed focal S:
C <-> S;
FC <-> FS;
B -> -B;
LC12 <-> LS12;
LC3 <-> LS3;
Q_prev_side C <-> S.

Q_prev and timer unchanged.

For focal H/U:
identity.

The exact full C/S mirror of committed observations
must canonicalize to byte-identical model-facing observations.

STRUCTURED MODEL

Replace only the flat LU-1A/LU-1B MLP
with the following shared relational architecture.

CELL ENCODER

One shared encoder instance
is applied independently to every one of the seven cell slots:

9 -> 32 -> 32

with SiLU after each linear layer.

The same weights are used
for focal and nonfocal cell slots.

No slot-specific weights.

No position embedding.

No neighbor index embedding.

No attention.

No recurrence.

CENTER REPRESENTATION

Use the encoded focal slot directly:

32 values.

NEIGHBOR REPRESENTATION

Encode each of the six nonfocal radius-3 neighbors
with the same CELL ENCODER.

Aggregate their six 32-value encodings
with an arithmetic mean.

Result:

32 values.

The aggregate is permutation-invariant
over the six nonfocal neighbor slots.

Because the neighborhood cardinality is fixed at six,
mean versus sum differs only by a fixed factor.

FOCAL-EXTRA ENCODER

Encode the seven focal extras through:

7 -> 16

with SiLU.

Result:

16 values.

TRUNK

Concatenate:

center encoding:
32;

neighbor mean encoding:
32;

focal-extra encoding:
16.

Total:
80.

Shared output trunk:

80 -> 64 -> 32 -> 6

with SiLU after the 64 and 32 hidden layers.

The six outputs have exactly the LU-1A/LU-1B meanings.

Hard lifecycle still chooses
which stochastic decision head is active.

PARAMETER COUNT

Expected trainable parameter count:

CELL ENCODER:
9*32 + 32
+
32*32 + 32
=
1376.

FOCAL-EXTRA ENCODER:
7*16 + 16
=
128.

TRUNK:
80*64 + 64
+
64*32 + 32
+
32*6 + 6
=
7462.

TOTAL:
8966.

Mechanical gate must verify this exact count.

Parameter ceiling remains:
<=18000.

Thus LU-1C has approximately half
the trainable parameters of LU-1A/LU-1B.

WHY THIS CHANGE IS JUSTIFIED

LU-1B removed the focal C/S coordinate burden
and reduced stay-head error materially,
but did not qualify.

The residual audit showed:

pressure = 0 cases are learned very well;

remaining error is concentrated
where the network must construct
the correct relational pressure from local inputs;

ECHO-associated errors remain large
outside CHALLENGE,
even though the teacher ignores ECHO there.

All required information is local
and already present in OBS-V1.

Therefore this experiment tests
a representation of repeated local relations,
not additional information
and not brute-force parameter growth.

TEACHER

Exactly Developmental Substrate V0.2 teacher probabilities:

H RELEASE;

C/S STAY-DEFECT;

U [C,S,H,U].

No sampled teacher labels.

No teacher-derived feature.

DATA

Freeze implementation as:

LU1CF1.

Only after LU1CF1 exists
derive fresh seeds.

TRAIN:
40000.

VALID:
8000.

TEST:
12000.

Exactly balanced as LU-1A/LU-1B:

H/C/S/U equally represented.

Use the exact LU-1A valid local snapshot generator.

Use exact LU-1B focal-side canonicalization
for model-facing committed C/S inputs.

SEED NAMESPACES

After LU1CF1:

LU1C-TRAIN-DATA;
LU1C-VALID-DATA;
LU1C-TEST-DATA;
LU1C-TRAIN-RNG;
LU1C-SYMMETRY;
LU1C-QUIESCENCE.

Each seed is the first unsigned big-endian 64 bits of:

SHA256(label + "|" + LU1CF1).

All six seeds must be distinct.

TRAINING

Exactly LU-1A/LU-1B:

PyTorch CPU;

deterministic algorithms ON;

threads = 1;

AdamW;

learning rate = 0.001;

weight decay = 0.00001;

batch = 512;

epochs = 30;

scheduler = NONE;

gradient clipping = NONE;

checkpoint = FINAL EPOCH ONLY;

no early stopping;

no hyperparameter search.

LOSS

Exactly LU-1A/LU-1B:

soft teacher targets.

L =
L_H
+
L_STAY
+
L_U.

No symmetry penalty.

No auxiliary loss.

No architecture-specific regularizer.

FORBIDDEN DERIVED FEATURES

LU-1C may not precompute or supply:

SUPPORT / CHALLENGE / NEUTRAL mode;

pressure;

opposition;

own aligned B;

qraw;

qecho;

qeff;

support margin;

same-side counts;

teacher probability;

target label;

global state;

task id;

phase id;

position id;

future information.

The shared encoder must infer useful local relations
from the accepted OBS-V1 channels.

MECHANICAL GATE

Before LU1CF1 prove:

1. input information exactly OBS-V1;

2. LU-1B canonicalization exact;

3. full committed C/S mirror canonical input identity = 100%;

4. model cell-slot width = 9;

5. exactly one shared 9->32->32 cell encoder;

6. no separate neighbor encoders;

7. no slot-specific or position parameters;

8. six nonfocal encodings combined only by arithmetic mean;

9. focal extras exactly seven values;

10. focal-extra encoder = 7->16;

11. trunk = 80->64->32->6;

12. trainable parameter count = 8966;

13. parameter count <=18000;

14. permuting the six nonfocal neighbor slots leaves model output
    identical to numerical tolerance;

15. focal slot is not included in the neighbor mean;

16. no forbidden derived feature exists;

17. H/U inputs retain their original semantics;

18. teacher probabilities exactly LU-1A/LU-1B/V0.2;

19. data counts and training schedule exactly LU-1A/LU-1B;

20. duplicate mechanical evidence byte-identical.

DUPLICATE TRAINING GATE

Run complete training twice.

Require:

canonical weight bytes identical;

weight SHA256 identical;

training metrics JSON byte-identical.

Only after that gate is committed
may the fresh held-out LU-1C test set be opened.

HELD-OUT TEST METRICS

Exactly LU-1A/LU-1B:

H RELEASE:
mean absolute error;
p95;
p99;
max.

C/S STAY:
mean absolute error;
p95;
p99;
max.

U:
mean;
p95;
p99;
max total-variation distance.

SYMMETRY

2000 fresh held-out exact C/S mirror pairs.

Use the corrected full mirror:

C <-> S;
FC <-> FS;
B sign;
LC12 <-> LS12;
Q-side C <-> S;
LC3 <-> LS3.

Report:

committed-pair canonical input identity rate;

student symmetry mean;

student symmetry p95;

student symmetry p99;

max.

QUIESCENCE

1000 U examples.

Report U probability:

mean;

p01;

minimum.

QUALIFICATION

LU1C_IMITATION_QUALIFIED = TRUE iff all are true:

1. parameter count <=18000;

2. duplicate training weight identity;

3. duplicate training metrics identity;

4. no global/task/future/position feature;

5. H mean <=0.02;

6. H p99 <=0.08;

7. STAY mean <=0.02;

8. STAY p99 <=0.08;

9. U mean TV <=0.03;

10. U p95 TV <=0.08;

11. U p99 TV <=0.12;

12. symmetry mean <=0.02;

13. symmetry p99 <=0.08;

14. quiescence mean U >=0.98;

15. quiescence p01 U >=0.90;

16. finite outputs;

17. normalized / bounded outputs;

18. corrected committed C/S canonical input identity rate = 1.0;

19. neighbor-permutation invariance probe passes.

No LU-1A/LU-1B approximation bar is relaxed.

INTERPRETATION

IF LU1C QUALIFIES

Then a smaller structured local relational network
is sufficient to imitate
the V0.2 staged stochastic decision heads
inside the frozen error envelope.

Next authorized experiment:

fresh-world closed-loop
V0.2 TEACHER
versus
LU-1C STUDENT
Task-1 execution.

Do not promote LU-1C into the substrate
from imitation alone.

Closed-loop perturbation,
damage,
and functional-regeneration evidence
remain required.

IF STAY STILL FAILS

Do not increase hidden width automatically.

The next narrow hypothesis should test
an explicit local multiplicative/gated/equivariant operator
for conditional relational interaction,
while preserving the same information boundary.

IF H OR U REGRESS

Treat that as evidence
that the structured aggregation lost useful expressivity
for those heads.

Do not relax their bars.

NO POST-RESULT TUNING

After training begins,
do not change:

canonical transform;

cell encoder dimensions;

aggregation operator;

extra encoder dimensions;

trunk dimensions;

parameter ceiling;

optimizer;

learning rate;

weight decay;

batch;

epochs;

loss;

dataset counts;

teacher;

seed namespaces;

qualification bars;

or interpretation rules.

PLAIN-SPEAK QUESTION

The neural cell has all the information it needs.

The remaining problem appears to be
how we ask it to organize that information.

The old network saw seventy numbers in one long row.

It had to discover for itself
that six neighboring cells
should all be examined by the same rule.

LU-1C builds that symmetry into the network shape.

Every nearby cell goes through
the same tiny encoder.

The six neighbors are then combined
without caring which list position they occupied.

The focal cell is kept separate.

The focal memory values are kept separate.

No answer is handed to the model.

No global information is added.

The network is actually much smaller
than the one that just failed.

If it succeeds,
we will have evidence that the problem
was not lack of neural capacity.

It was choosing a network shape
that matches the local developmental law.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
