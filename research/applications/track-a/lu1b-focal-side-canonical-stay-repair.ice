TITLE: LU-1B — FOCAL-SIDE CANONICAL STAY-HEAD REPAIR
DATE: 2026-09-23
STATUS: PREREGISTERED / NO TRAINING EXECUTION
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Repair the single failed LU-1A approximation axis
without adding capacity,
new information,
or relaxed thresholds.

LU-1A learned:

H RELEASE:
inside frozen error bars.

U RECRUITMENT:
inside frozen error bars.

C/S STAY-DEFECT:
outside frozen error bars.

The post-closure diagnostic localized
the largest errors to:

CHALLENGE;

especially ECHO-dominant CHALLENGE;

and the stay-head C/S symmetry tail.

The present experiment tests
whether an exact focal-side coordinate transform
removes that unnecessary representational burden.

PARENTS

Developmental Substrate V0.2:

e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2.

LU-0E local-identifiability closure:

94eda73cf865a131365ac4cbe943dc558daaece1.

LU-1A closure:

5c81b6f38f9a0b4d05ccbcaad89ef7c2a9d7e745.

LU-1A diagnostic:

0d499c003ee955e233e31f9d336a4eeba6993338.

SCIENTIFIC CHANGE

Exactly one change is authorized:

for committed C/S focal examples,
represent OBS-V1 in a focal-side canonical frame
before the shared MLP sees it.

No model-size change.

No optimizer change.

No loss change.

No teacher change.

No added feature.

No removed feature.

No threshold change.

CANONICAL TRANSFORM

For focal C:

identity.

For focal S:

swap state labels:

C <-> S;

FC <-> FS;

U unchanged;

H unchanged.

For every radius-3 cell:

B_pre -> -B_pre;

LC12 <-> LS12.

Focal extras:

LC3 <-> LS3;

Q_prev unchanged;

Q_prev_side:

C <-> S;

NONE unchanged.

timer unchanged.

After this transform,
a committed focal cell is always represented
as canonical SELF = C.

Thus:

canonical C means SELF;

canonical S means OPPONENT

for the stay-defect head.

The transform is deterministic,
bijective on the committed C/S observation family,
and contains exactly the same information
as OBS-V1.

It does not calculate:

mode;

pressure;

qraw;

qecho;

qeff;

support margin;

teacher probability;

or any target-derived quantity.

It therefore does not hand
the teacher's answer to the student.

H / U INPUTS

For focal H or U:

OBS-V1 is unchanged.

This ensures the already-successful
H RELEASE and U RECRUITMENT questions
receive the same semantic input
as LU-1A.

MODEL

Exactly LU-1A:

input:
70.

hidden:
128.

SiLU.

hidden:
64.

SiLU.

outputs:
6.

Trainable parameter count:
17734.

Parameter ceiling:
18000.

No attention.

No recurrence.

No dropout.

No batch normalization.

No per-cell parameters.

No task embedding.

No position embedding.

No stage id.

Hard lifecycle still chooses
which output head is active.

TEACHER

Exact V0.2 probabilities:

H RELEASE;

C/S STAY;

U [C,S,H,U].

No sampled teacher labels.

DATA

Freeze implementation as:

LU1BF1.

Only after LU1BF1 exists
derive fresh seeds.

TRAIN:
40000.

VALID:
8000.

TEST:
12000.

Balanced exactly as LU-1A:

H/C/S/U equally represented.

Dataset generation remains
the exact LU-1A valid local snapshot generator.

Only the model-facing
committed C/S coordinate frame changes.

SEED NAMESPACES

After LU1BF1:

LU1B-TRAIN-DATA;

LU1B-VALID-DATA;

LU1B-TEST-DATA;

LU1B-TRAIN-RNG;

LU1B-SYMMETRY;

LU1B-QUIESCENCE.

Use first unsigned big-endian 64 bits
of SHA256(label + "|" + LU1BF1).

All six seeds must be distinct.

TRAINING

Exactly LU-1A:

PyTorch CPU.

deterministic algorithms ON.

threads:
1.

AdamW.

learning rate:
0.001.

weight decay:
0.00001.

batch:
512.

epochs:
30.

scheduler:
NONE.

gradient clipping:
NONE.

checkpoint:
FINAL EPOCH ONLY.

No early stopping.

No hyperparameter search.

LOSS

Exactly LU-1A:

soft teacher targets.

L =
L_H
+
L_STAY
+
L_U.

No symmetry penalty.

No auxiliary loss.

The experiment tests
whether representation alone
is sufficient.

MECHANICAL CANONICALIZATION PROBES

Before LU1BF1 prove:

1. model dimensions exactly LU-1A;

2. trainable parameters =17734;

3. no new input field exists;

4. focal C transform is identity;

5. focal S transform swaps exactly:
   C/S,
   FC/FS,
   B sign,
   LC/LS,
   Q-side C/S;

6. focal H/U transform is identity;

7. a raw committed C observation
   and its exact C/S-swapped S counterpart
   canonicalize to byte-identical
   model input;

8. teacher stay probabilities
   of that C/S-swapped pair
   are exactly equal;

9. canonicalization is idempotent
   on already-canonical committed inputs;

10. no mode/pressure/qraw/qeff
    or target value is added;

11. data counts and training schedule
    exactly match LU-1A;

12. duplicate mechanical evidence
    byte-identical.

DUPLICATE TRAINING GATE

Run complete training twice.

Require:

canonical weight bytes identical;

weight SHA256 identical;

training metrics JSON byte-identical.

Only then open the fresh held-out test set.

TEST METRICS

Use exactly the LU-1A metrics.

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

mean/p95/p99/max TV.

Symmetry:

2000 fresh held-out swap pairs.

For committed C/S rows,
the canonical transform should map
a correct C/S swap
to the same model-facing input.

Report exact committed-pair
canonical input identity rate
in addition to student symmetry error.

Quiescence:

1000 U examples.

QUALIFICATION

LU1B_IMITATION_QUALIFIED = TRUE iff
the exact LU-1A qualification bars all pass:

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

17. normalized/bounded outputs.

No bar is relaxed from LU-1A.

ADDITIONAL REPRESENTATION CHECK

For all held-out committed C/S symmetry pairs:

canonicalized model-facing inputs
must be byte-identical.

If not:

LU1B representation implementation fails,
regardless of imitation metrics.

INTERPRETATION

If LU1B qualifies:

the LU-1A failure was substantially
a coordinate/relational representation problem,
not evidence that the local law requires
more capacity or nonlocal information.

Next:

preregister fresh-world closed-loop
teacher-vs-student Task-1 execution.

Do not promote from imitation alone.

If LU1B still fails stay approximation:

do not increase capacity automatically.

Use the remaining error structure
to test one narrow next hypothesis,
such as whether exact local relational aggregation
needs a structured permutation/equivariant operator
rather than a flat MLP.

NO POST-RESULT TUNING

Do not change:

70-dimensional information content;

128/64 hidden widths;

17734 parameter architecture;

optimizer;

learning rate;

weight decay;

batch;

epochs;

loss;

dataset counts;

teacher;

qualification bars;

or canonical transform

after training begins.

PLAIN-SPEAK QUESTION

The first neural cell was being asked
to learn the same commitment rule twice.

For C:

C meant ME.

For S:

S meant ME.

The network had to discover
that those are mirror images,
while also learning
how attack,
local evidence,
and echo memory interact.

LU-1B removes only that bookkeeping problem.

When a committed cell is S,
we flip the local coordinate system
before the neural network sees it.

Now the committed cell always sees:

ME as C;

THE OTHER SIDE as S.

We also flip the evidence sign
and swap the matching local-demand channels.

No information is added.

No answer is calculated for it.

The neural network is the same size.

Training is the same.

The pass bars are the same.

If this works,
we will have learned something important:

the first failure was not
that the neural cell lacked intelligence or capacity.

It was that we represented
an exact biological symmetry
in an unnecessarily difficult coordinate system.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
