TITLE: LU-1E — STATE-CONDITIONED EQUIVARIANT RELATIONAL UPDATER
DATE: 2026-09-23
STATUS: PREREGISTERED / NO TRAINING EXECUTION
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Test the next narrow learned-updater hypothesis:

the remaining committed-cell imitation error
comes from asking generic continuous layers
to rediscover exact categorical local relations
that are already explicitly present in OBS-V1.

LU-1E does not add information.

It changes only how the existing categorical state fields
condition learned transforms of the existing continuous local fields.

PARENTS

Developmental Substrate V0.2:

e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2.

LU-0E local-identifiability closure:

94eda73cf865a131365ac4cbe943dc558daaece1.

LU-1A closure:

5c81b6f38f9a0b4d05ccbcaad89ef7c2a9d7e745.

LU-1B closure:

0579573b3483c17a1932210eca245ec37c65b63e.

LU-1B residual audit:

b6957f04bbb9f3f047bbf6f0ff485fe2560c960d.

LU-1C closure:

044685fb09a04a46cb15bbab91b74418221ce3a0.

LU-1C residual audit:

1e00984d9e23ada0b94107d039d4c6b506691128.

LU-1D closure:

f9625901264f32ad774d69378001a2c3a8a3b2ef.

LU-1D reproduction-sensitivity diagnostic:

94ce811906de8df6445d81aafaa673cf2ac686d4.

SCIENTIFIC MOTIVATION

Across the learned-updater lineage:

LU-1A flat raw stay mean / p99:
0.0427632498 / 0.3573133560.

LU-1B focal-side canonical stay mean / p99:
0.0275619427 / 0.2435178667.

LU-1C shared-neighbor mean stay mean / p99:
0.0253735475 / 0.2891320121.

LU-1D gated pair-relational stay mean / p99:
0.0231283040 / 0.2005912924.

H release and U recruitment
already satisfy the frozen imitation bars.

The remaining failure is the C/S stay-defect law.

Authoritative LU-1B and LU-1C diagnostics
localized the residual to exact local conditional relations,
especially ECHO / challenge conditionality.

LU-1D gating supplied further information gain
but did not cross the unchanged bars.

A later reproduction-sensitivity diagnostic,
explicitly non-canonical,
reproduced the same broad ECHO-associated residual family
across three CPU numerical paths
whose aggregate LU-1D held-out metrics match the historical closure
at sub-micro scale.

The present experiment tests categorical relation routing,
not greater generic capacity.

INFORMATION BOUNDARY

Input information remains exactly OBS-V1:

seven radius-3 cell records,
each containing:

state one-hot over
C, S, U, H, FC, FS;

B_pre;

LC12;

LS12;

plus focal extras:

timer / D;

Q_prev;

Q_prev_side one-hot over
NONE, C, S;

LC3;

LS3.

Total semantic input width remains:

70.

No additional observation is authorized.

FOCAL-SIDE CANONICALIZATION

Retain exact LU-1B canonicalization.

For committed focal C:
identity.

For committed focal S:

C <-> S;
FC <-> FS;
B -> -B;
LC12 <-> LS12;
LC3 <-> LS3;
Q_prev_side C <-> S.

Q_prev unchanged.

For focal H or U:
identity.

Thus for the committed stay head:

canonical C = SELF;
canonical S = OPPONENT.

This transform remains deterministic,
information-preserving on the committed mirror family,
and target-independent.

SCIENTIFIC CHANGE

Replace LU-1D's generic focal-neighbor pair encoder
with an exact category-conditioned shared cell relation encoder.

For each of the seven cell slots:

categorical input:
the existing six-way state one-hot.

continuous input:
the existing three-vector

[B_pre, LC12, LS12].

The categorical state selects
one of six learned affine transforms:

3 -> 16.

The six transforms are shared by position.

That is:

one transform bank indexed only by existing state category;

not six position-specific encoders.

Apply SiLU.

Then one shared post transform:

16 -> 24;

SiLU.

Use the same relation bank
for focal and nonfocal cells.

NONFOCAL AGGREGATION

Encode each of the six nonfocal radius-3 cells
through the exact same relation bank.

Aggregate by arithmetic mean.

No ordering feature.

No slot embedding.

No position embedding.

No attention.

The nonfocal summary width is:

24.

FOCAL REPRESENTATION

Encode the focal cell
through the same state-conditioned relation bank.

Keep its representation separately.

Focal width:

24.

Q-SIDE RELATION ENCODER

Q_prev and Q_prev_side are already explicit OBS-V1 fields.

Use their categorical relation structurally.

Q_prev_side selects one of three learned affine transforms:

1 -> 8

for categories:

NONE;
canonical C;
canonical S.

Apply SiLU.

Then shared post transform:

8 -> 16;

SiLU.

This is not qecho.

It does not compare Q_prev to a teacher-computed mode.

It does not decide whether memory should be active.

It only presents the already-observed
Q_prev value in a representation conditioned
on its already-observed side category.

OTHER FOCAL EXTRAS

Encode the existing continuous extras:

timer / D;
LC3;
LS3

through:

3 -> 16;

SiLU.

CONTEXT

Concatenate:

nonfocal mean:
24;

focal relation representation:
24;

Q-side representation:
16;

other focal extras:
16.

Context width:

80.

MULTIPLICATIVE GATE

Retain LU-1D's learned conditional-interaction geometry.

VALUE:

80 -> 64;
SiLU.

GATE:

80 -> 64;
sigmoid.

Interaction:

VALUE * GATE

elementwise.

OUTPUT

64 -> 32;
SiLU;

32 -> 6 logits.

The hard lifecycle remains external
and chooses the active output family:

H release;

C/S stay-defect;

U recruitment.

PARAMETER COUNT

Expected trainable parameter count:

13694.

Derivation:

shared six-state 3->16 affine bank:
384;

shared 16->24 post transform:
408;

three-category Q-side 1->8 affine bank:
48;

Q-side 8->16 post transform:
144;

other-extra 3->16:
64;

value 80->64:
5184;

gate 80->64:
5184;

output 64->32:
2080;

output 32->6:
198.

Total:

13694.

Frozen parameter ceiling remains:

18000.

No parameter increase above LU-1A / LU-1B
is permitted.

TEACHER

Exact Developmental Substrate V0.2 probabilities.

No sampled teacher labels.

H release:
unchanged.

C/S stay-defect:
unchanged.

U recruitment:
unchanged.

FORBIDDEN DERIVED INPUTS

LU-1E may not precompute or expose:

mode;

challenge flag;

support flag;

pressure;

opposition;

own aligned B;

qraw;

qecho;

qeff;

support margin;

teacher probability;

teacher class;

target;

task id;

request id;

phase id;

global workload;

global C/S count;

future request;

future lesion;

future anchor;

position embedding.

The relation bank may use only
categorical state bits already present in OBS-V1
to select learned transforms.

The Q-side bank may use only
Q_prev_side already present in OBS-V1
to select a learned transform of Q_prev.

DATA

Freeze implementation as:

LU1EF1.

Only after LU1EF1 exists
derive fresh deterministic seeds.

TRAIN:
40000.

VALID:
8000.

TEST:
12000.

Class balance:
exact LU-1A/LU-1B/LU-1C/LU-1D balance.

Dataset generator:
exact inherited LU-1D generator.

Only model geometry changes.

SEED NAMESPACES

After LU1EF1:

LU1E-TRAIN-DATA;
LU1E-VALID-DATA;
LU1E-TEST-DATA;
LU1E-TRAIN-RNG;
LU1E-SYMMETRY;
LU1E-QUIESCENCE.

For each label:

first unsigned big-endian 64 bits of

SHA256(label + "|" + LU1EF1).

All six seeds must be distinct.

TRAINING

Exactly inherited:

PyTorch CPU;

deterministic algorithms ON;

threads:
1;

AdamW;

learning rate:
0.001;

weight decay:
0.00001;

batch:
512;

epochs:
30;

scheduler:
NONE;

gradient clipping:
NONE;

checkpoint:
FINAL EPOCH ONLY;

no early stopping;

no hyperparameter search.

LOSS

Exact inherited equal-head soft-target loss:

L =
L_H
+
L_STAY
+
L_U.

No symmetry penalty.

No auxiliary loss.

No relation-label supervision.

No teacher-derived intermediate loss.

MECHANICAL GATE BEFORE LU1EF1

Prove all of the following before freeze:

1.
semantic input information is exactly OBS-V1 / width 70;

2.
LU-1B focal-side canonicalization is exact;

3.
a raw committed C observation
and its exact full C/S mirror
canonicalize to byte-identical model-facing semantic input;

4.
teacher stay probabilities
for that exact mirror are identical;

5.
focal H and U canonicalization is identity;

6.
one six-category relation bank exists;

7.
the same relation-bank parameters
are used for all seven cell slots;

8.
the relation bank reads only:
state one-hot,
B_pre,
LC12,
LS12;

9.
nonfocal aggregation uses exactly
the six nonfocal radius-3 cells;

10.
nonfocal aggregation is arithmetic mean;

11.
no neighbor slot / absolute position parameter exists;

12.
Q-side relation bank has exactly three categories:
NONE, canonical C, canonical S;

13.
Q-side relation bank reads only:
Q_prev,
Q_prev_side;

14.
other-extra encoder reads exactly:
timer/D,
LC3,
LS3;

15.
context width = 80;

16.
value stream = 80 -> 64 with SiLU;

17.
gate stream = 80 -> 64 with sigmoid;

18.
one elementwise VALUE * GATE interaction;

19.
output = 64 -> 32 -> 6;

20.
trainable parameter count = 13694 exactly;

21.
trainable parameter count <=18000;

22.
no attention;

23.
no recurrence;

24.
no dropout;

25.
no batch normalization;

26.
no position embedding;

27.
no forbidden derived feature;

28.
neighbor permutation probe
maximum trained-independent logit difference <=1e-5;

29.
teacher function is exact inherited V0.2 teacher;

30.
data counts / optimizer / schedule / loss
are exact inherited values;

31.
six seed namespaces are distinct;

32.
duplicate mechanical evidence byte-identical.

DUPLICATE TRAINING GATE

After LU1EF1 and seed binding:

run complete training twice.

Require:

canonical weight bytes identical;

weight SHA256 identical;

training metrics JSON byte-identical.

Only after that gate passes
may the fresh LU-1E held-out TEST set be opened.

HELD-OUT TEST METRICS

Use exactly the historical LU-1 qualification metrics.

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

U RECRUITMENT:

mean TV;
p95 TV;
p99 TV;
max TV.

SYMMETRY:

2000 fresh held-out exact full C/S mirror pairs.

Report:

canonical committed input identity rate;

student symmetry mean;

student symmetry p99.

QUIESCENCE:

1000 U examples.

Report:

mean U probability;

p01 U probability.

PERMUTATION:

report maximum output-logit difference
under a permutation of the six nonfocal neighbors.

QUALIFICATION

LU1E_IMITATION_QUALIFIED = TRUE iff
all inherited qualification bars pass:

1.
parameter count <=18000;

2.
duplicate training weight identity;

3.
duplicate training metrics identity;

4.
no global/task/future/position feature;

5.
H mean <=0.02;

6.
H p99 <=0.08;

7.
STAY mean <=0.02;

8.
STAY p99 <=0.08;

9.
U mean TV <=0.03;

10.
U p95 TV <=0.08;

11.
U p99 TV <=0.12;

12.
symmetry mean <=0.02;

13.
symmetry p99 <=0.08;

14.
quiescence mean U >=0.98;

15.
quiescence p01 U >=0.90;

16.
all outputs finite;

17.
probabilities bounded / normalized;

plus representation integrity:

18.
committed canonical mirror identity = 1.0;

19.
neighbor permutation max logit difference <=1e-5.

No historical bar is relaxed.

INTERPRETATION

IF LU1E QUALIFIES

Then:

the residual learned-updater failure
was substantially a categorical relational representation problem.

Next:

preregister fresh-world
closed-loop teacher-versus-student Task-1 execution.

Do not promote LU-1E from imitation alone.

Do not replace V0.2 teacher dynamics
until closed-loop functional evidence passes.

IF LU1E DOES NOT QUALIFY

Do not widen automatically.

Do not add global context.

Do not expose teacher-derived algebra.

Run one observation-only residual audit.

If the stay tail remains concentrated
around conditional ECHO/mode interactions,
the next question must test
a still more explicit equivariant/local operator
or reconsider whether pure approximation of the hand law
is the right learning target.

NO POST-RESULT TUNING

After training begins do not change:

OBS-V1;

canonicalization;

categorical routing;

relation-bank widths;

Q-side routing;

context width;

gate/value widths;

parameter ceiling;

optimizer;

learning rate;

weight decay;

batch;

epochs;

loss;

dataset counts;

seed namespaces;

teacher;

qualification bars;

permutation tolerance;

or interpretation rules.

PLAIN-SPEAK QUESTION

The neural cell already sees
which state every neighbor is in.

But previous networks treated that fact
mostly like just another number
that had to be mixed with everything else.

LU-1E asks a narrower question:

what if the cell is allowed to use
the neighbor's existing state label
to choose HOW to interpret
that neighbor's local numbers?

A SELF neighbor,
an OPPONENT neighbor,
an uncertain neighbor,
and a refractory neighbor
can use different learned transforms.

Those transforms are shared everywhere.

There is still no position map.

There is still no global signal.

There is still no teacher answer.

The same idea is applied to
the already-existing Q_prev_side label:

the network may represent memory differently
depending on which side that memory belongs to,
but it still has to learn
whether the current situation should use that memory.

The network remains smaller
than the original LU-1A/LU-1B model.

If this crosses the same frozen bars,
we will have evidence that
the hard part was not more capacity.

It was respecting exact local categorical relationships
in the architecture.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
