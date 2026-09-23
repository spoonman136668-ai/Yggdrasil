TITLE: LU-1D — GATED FOCAL-NEIGHBOR RELATIONAL UPDATER
DATE: 2026-09-23
STATUS: PREREGISTERED / NO TRAINING EXECUTION
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Test the specific residual hypothesis
supported independently by LU-1B and LU-1C diagnostics:

the remaining committed-cell imitation error
is a conditional local relational-interaction problem,
especially the rule that ECHO protection
must modulate stay behavior only in the appropriate local context.

LU-1D changes only network geometry.

No information is added.

No teacher-derived feature is added.

No parameter ceiling is increased.

No training rule or qualification bar is relaxed.

PARENTS

Developmental Substrate V0.2:
e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2

LU-0E staged-local identifiability closure:
94eda73cf865a131365ac4cbe943dc558daaece1

LU-1B closure:
0579573b3483c17a1932210eca245ec37c65b63e

LU-1B residual diagnostic:
b6957f04bbb9f3f047bbf6f0ff485fe2560c960d

LU-1C closure:
044685fb09a04a46cb15bbab91b74418221ce3a0

LU-1C residual diagnostic:
1e00984d9e23ada0b94107d039d4c6b506691128

SCIENTIFIC QUESTION

Can a small shared focal-neighbor relational encoder
plus a learned multiplicative gate
recover the exact V0.2 stochastic decision law
inside the unchanged imitation error bars?

OBSERVATION

Exactly the accepted OBS-V1 information.

Model-facing semantic width remains 70:

seven cell slots x nine values = 63;

plus seven focal extras = 7.

Per cell slot:

state one-hot:
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

Q_prev_side one-hot:
NONE;
C;
S;

LC3;

LS3.

No input channel is added or removed.

FOCAL-SIDE CANONICALIZATION

Exactly LU-1B and LU-1C.

Committed focal C:
identity.

Committed focal S:
C <-> S;
FC <-> FS;
B -> -B;
LC12 <-> LS12;
LC3 <-> LS3;
Q_prev_side C <-> S.

Q_prev and timer unchanged.

Focal H/U:
identity.

Correct full C/S mirror pairs
must canonicalize to byte-identical model-facing observations.

MODEL

PAIR ENCODER

For each of the six nonfocal neighbors,
concatenate:

focal cell slot:
9 values;

neighbor cell slot:
9 values.

Pair width:
18.

Apply one shared pair encoder instance:

18 -> 32 -> 32

with SiLU after each linear layer.

The same pair encoder weights
are used for all six focal-neighbor pairs.

No neighbor-specific weights.

No slot embedding.

No position embedding.

No attention.

No recurrence.

PAIR AGGREGATION

Take the arithmetic mean
of the six 32-value pair encodings.

Result:
32 values.

This aggregate is permutation-invariant
over the six nonfocal neighbors
up to floating-point reduction tolerance.

FOCAL ENCODER

Encode the focal 9-value cell slot separately:

9 -> 16

with SiLU.

Result:
16 values.

FOCAL-EXTRA ENCODER

Encode the seven focal extras:

7 -> 16

with SiLU.

Result:
16 values.

CONTEXT

Concatenate:

pair mean:
32;

focal encoding:
16;

focal-extra encoding:
16.

Total:
64 values.

MULTIPLICATIVE GATE

From the same 64-value context compute:

VALUE:
64 -> 64
followed by SiLU.

GATE:
64 -> 64
followed by sigmoid.

Interaction representation:

Z =
SiLU(VALUE(context))
*
sigmoid(GATE(context)).

This multiplication is the only newly authorized
explicit multiplicative interaction.

It is learned.

It is not a hand-coded challenge flag.

It is not supplied a teacher answer.

OUTPUT TRUNK

Z:

64 -> 32 -> 6

with SiLU after the 32-value hidden layer.

The six outputs keep
the exact LU-1A/LU-1B/LU-1C meanings.

Hard lifecycle still chooses
which stochastic decision head is active.

PARAMETER COUNT

PAIR ENCODER:

18*32 + 32
+
32*32 + 32
=
1664.

FOCAL ENCODER:

9*16 + 16
=
160.

FOCAL-EXTRA ENCODER:

7*16 + 16
=
128.

VALUE:

64*64 + 64
=
4160.

GATE:

64*64 + 64
=
4160.

OUTPUT:

64*32 + 32
+
32*6 + 6
=
2278.

TOTAL:

12550.

Mechanical gate must verify exactly:

12550 trainable parameters.

Parameter ceiling remains:

<=18000.

WHY THIS CHANGE IS JUSTIFIED

LU-1B focal-side canonicalization
removed about one third of the original stay error.

LU-1C shared-neighbor mean aggregation
provided only a small further mean improvement
and worsened the tail.

The LU-1C residual audit reproduced
the same conditional-ECHO signature:

ECHO-dominant CHALLENGE:
high error with negative stay bias;

ECHO-dominant SUPPORT / NEUTRAL:
high error with positive stay bias;

no-ECHO SUPPORT / NEUTRAL:
much smaller error.

Therefore the remaining problem is not:

global information;

focal C/S symmetry;

neighbor list ordering;

or raw parameter count.

The evidence supports testing
a learned conditional multiplicative interaction
between local relational context and decision features.

FORBIDDEN DERIVED FEATURES

LU-1D may not precompute or supply:

SUPPORT / CHALLENGE / NEUTRAL mode;

pressure;

opposition;

own aligned B;

qraw;

qecho;

qeff;

support margin;

same-side count;

teacher probability;

target label;

global state;

task id;

phase id;

position id;

future information.

The gate must infer useful conditional structure
from OBS-V1 only.

TEACHER

Exactly Developmental Substrate V0.2:

H RELEASE;

C/S STAY-DEFECT;

U [C,S,H,U].

Soft exact teacher probabilities.

No sampled teacher labels.

DATA

Freeze implementation as:

LU1DF1.

Only after LU1DF1 exists
derive fresh seeds.

TRAIN:
40000.

VALID:
8000.

TEST:
12000.

Exact LU-1A/LU-1B/LU-1C class balance
and valid local snapshot generator.

SEED NAMESPACES

After LU1DF1:

LU1D-TRAIN-DATA;
LU1D-VALID-DATA;
LU1D-TEST-DATA;
LU1D-TRAIN-RNG;
LU1D-SYMMETRY;
LU1D-QUIESCENCE.

Each is first unsigned big-endian 64 bits of:

SHA256(label + "|" + LU1DF1).

All six must be distinct.

TRAINING

Exactly inherited:

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

Exactly inherited:

L =
L_H
+
L_STAY
+
L_U.

Soft targets.

No auxiliary gate loss.

No symmetry loss.

No pressure loss.

No teacher-derived intermediate target.

MECHANICAL GATE

Before LU1DF1 prove:

1. semantic input exactly OBS-V1;

2. exact LU-1B focal-side canonicalization;

3. corrected full committed C/S mirror canonical identity = 100%;

4. pair width = 18;

5. exactly one shared 18->32->32 pair encoder;

6. pair encoder applied exactly six times,
   once per nonfocal neighbor;

7. no neighbor-specific learned parameters;

8. pair aggregation = arithmetic mean;

9. focal encoder = 9->16;

10. focal-extra encoder = 7->16;

11. context width = 64;

12. value path = 64->64 + SiLU;

13. gate path = 64->64 + sigmoid;

14. elementwise value*gate multiplication exists exactly once
    as the authorized learned interaction;

15. output path = 64->32->6;

16. trainable parameter count = 12550;

17. parameter count <=18000;

18. no attention / recurrence / position embedding;

19. permuting six nonfocal neighbors changes logits
    by no more than 1e-5 in the numerical probe;

20. no forbidden derived feature;

21. H/U model-facing semantics unchanged;

22. teacher exact V0.2;

23. data counts and training schedule exactly inherited;

24. six future seed namespaces distinct;

25. duplicate mechanical evidence byte-identical.

The 1e-5 permutation tolerance is fixed before training.
It covers ordinary floating-point reduction-order noise
without authorizing semantic position dependence.

DUPLICATE TRAINING GATE

Run complete training twice.

Require:

canonical weight bytes identical;

weight SHA256 identical;

training metrics JSON byte-identical.

Only after that gate is committed
may the fresh held-out LU-1D test be opened.

TEST METRICS

Exactly inherited.

H RELEASE:
mean/p95/p99/max absolute error.

C/S STAY:
mean/p95/p99/max absolute error.

U:
mean/p95/p99/max total-variation distance.

SYMMETRY:
2000 exact corrected C/S mirror pairs;
canonical identity rate;
mean/p95/p99/max student symmetry error.

QUIESCENCE:
1000 U examples;
mean/p01/minimum U probability.

QUALIFICATION

LU1D_IMITATION_QUALIFIED = TRUE iff all are true:

parameter count <=18000;

duplicate weights;

duplicate metrics;

no global/task/future/position feature;

H mean <=0.02;

H p99 <=0.08;

STAY mean <=0.02;

STAY p99 <=0.08;

U mean TV <=0.03;

U p95 TV <=0.08;

U p99 TV <=0.12;

symmetry mean <=0.02;

symmetry p99 <=0.08;

quiescence mean U >=0.98;

quiescence p01 U >=0.90;

finite outputs;

bounded/normalized probabilities;

committed canonical identity rate = 1.0;

neighbor permutation max-logit difference <=1e-5.

No approximation bar is relaxed.

INTERPRETATION

IF LU1D QUALIFIES

The evidence will support
that a small learned gated relational operator
can imitate the V0.2 staged local stochastic law
inside the frozen envelope.

Next:

preregister fresh-world closed-loop
V0.2 teacher versus LU-1D student Task-1 execution.

Do not promote from imitation alone.

IF STAY STILL FAILS

Do not increase capacity automatically.

Use an observation-only residual audit.

If the same ECHO conditionality remains,
the next hypothesis must be qualitatively different,
for example a more explicit equivariant
state-conditioned interaction primitive.

IF H/U REGRESS

Do not relax their bars.

Treat it as evidence
that the gated representation harms
already-learned decision families.

NO POST-RESULT TUNING

After training begins do not change:

pair encoder;

aggregation;

focal encoder;

extra encoder;

gate/value dimensions;

multiplication;

output trunk;

parameter ceiling;

optimizer;

learning rate;

weight decay;

batch;

epochs;

loss;

data counts;

teacher;

canonicalization;

seed namespaces;

qualification bars;

permutation tolerance;

or interpretation rules.

PLAIN-SPEAK QUESTION

The cell still makes one repeating mistake.

It sees local memory
but does not reliably learn
WHEN that memory should matter.

So this experiment gives the neural cell
one new kind of computation:

a learned gate.

The gate can learn:

"under this local situation,
let this signal through."

or:

"under this other situation,
suppress it."

We are not telling it
what challenge means.

We are not calculating pressure for it.

We are not adding global information.

It still has to discover the rule.

But the network now has
the right kind of mathematical operation
to represent conditional modulation directly.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
