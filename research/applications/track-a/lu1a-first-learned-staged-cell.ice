TITLE: LU-1A — FIRST LEARNED SHARED STAGED PER-CELL UPDATER
DATE: 2026-09-23
STATUS: PREREGISTERED / NO TRAINING EXECUTION
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

NAMING NOTE

A prior LU-1 preregistration was retired unexecuted
during the LU-0C lineage cleanup.

LU-1A is a new experiment
and does not revive or inherit
the retired LU-1 mechanism.

PURPOSE

Train the first learned Yggdrasil cell rule
against the exact stochastic decision heads
of Developmental Substrate V0.2.

This experiment tests:

teacher-probability imitation only.

It does not authorize:

closed-loop replacement;

substrate promotion;

deployment;

structural growth;

dynamic topology;

or functional-regeneration claims.

PARENT

Developmental Substrate V0.2:

e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2.

LU-0E closure:

94eda73cf865a131365ac4cbe943dc558daaece1.

LU-0E established:

LU0E_V02_STAGED_LOCAL_IDENTIFIABLE = TRUE;

LU0E_MINIMALITY_CONTROLS_PASS = TRUE;

LU0E_STAGING_REQUIRED = TRUE.

STUDENT QUESTION

Can one small shared feed-forward function
recover the exact V0.2 local stochastic decision law
from OBS-V1
without global context,
task identity,
future information,
or per-cell learned parameters?

OBSERVATION V1

Use exactly the LU-0E accepted information boundary.

For offsets d = -3..+3,
seven cells total:

state_(i+d);

B_pre_(i+d);

LC12_(i+d);

LS12_(i+d).

State encoding:

one-hot over:

C;
S;
U;
H;
FC;
FS.

Per radius-3 cell feature width:

6 state channels
+
1 B channel
+
1 LC12 channel
+
1 LS12 channel

=
9.

Radius-3 block:

7 x 9
=
63 features.

Focal extras:

timer_i / D;
Q_prev_i;
Q_prev_side_i one-hot over NONE/C/S;
LC3_i;
LS3_i.

Focal extras:
7.

TOTAL INPUT WIDTH

70.

No global feature.

No phase id.

No task id.

No request id.

No cell id.

No absolute position.

No future field.

No global score.

No global count.

No global pool.

MODEL

One shared MLP
used for every cell.

Input:
70.

Hidden layer 1:
128.

Activation:
SiLU.

Hidden layer 2:
64.

Activation:
SiLU.

Outputs:
6 logits.

Output interpretation:

logit 0:
H RELEASE Bernoulli logit.

logit 1:
C/S STAY Bernoulli logit.

logits 2..5:
U recruitment categorical logits
for:

C;
S;
H;
U.

No dropout.

No batch normalization.

No recurrence inside the learned model.

No attention.

No per-cell embeddings.

No task embeddings.

No position embeddings.

The hard lifecycle engine selects
which output head is relevant
from the focal cell's current lifecycle state.

The model itself receives no explicit stage id.

PARAMETER CEILING

Canonical trainable parameter count
must be <= 18000.

If implementation exceeds 18000:

mechanical gate fails.

TEACHER

Use exact Developmental Substrate V0.2
stochastic decision equations:

H RELEASE;

C/S STAY-DEFECT;

U C/S/H recruitment.

Teacher sampling is not used for labels.

Targets are exact teacher probabilities.

Thus training learns the distribution,
not one Bernoulli/categorical draw.

HARD / LEARNED BOUNDARY

Remain hard/fixed in LU-1A:

bounded local perception operators;

B recurrence;

refractory timer lifecycle;

Q/ECHO trace bookkeeping;

released-this-epoch exclusion;

valid state transitions;

hard resource/safety guards;

stateless sampling.

Learn only:

H RELEASE probability;

C/S STAY probability;

U [C,S,H,U] transition distribution.

DATA GENERATOR

Freeze implementation as:

LU1AF1.

Only after LU1AF1 exists,
derive all dataset seeds
from LU1AF1.

TRAIN SET

examples:
40000.

Exactly balanced focal lifecycle classes:

H:
10000.

C:
10000.

S:
10000.

U:
10000.

VALIDATION SET

examples:
8000.

Exactly balanced:

2000 each
for H/C/S/U.

Validation is report-only.

No early stopping.

No checkpoint selection from validation.

TEST SET

examples:
12000.

Exactly balanced:

3000 each
for H/C/S/U.

The test set remains unopened
until training is complete.

SEED DERIVATION

train data seed:

first 64 bits of
SHA256(
"LU1A-TRAIN-DATA|"
+
LU1AF1
).

validation data seed:

first 64 bits of
SHA256(
"LU1A-VALID-DATA|"
+
LU1AF1
).

test data seed:

first 64 bits of
SHA256(
"LU1A-TEST-DATA|"
+
LU1AF1
).

model initialization / training-order seed:

first 64 bits of
SHA256(
"LU1A-TRAIN-RNG|"
+
LU1AF1
).

The three dataset seeds
must be distinct.

SYNTHETIC LOCAL SNAPSHOT GENERATOR

Each example is a valid
staged local teacher snapshot.

Neighbor lifecycle states
are sampled from:

C/S/U/H/FC/FS.

Focal class is fixed
by the balanced class schedule.

B values are sampled
within the exact reachable bounded domain:

[-1,1].

Q_prev:

[0,1].

Q_prev_side:

NONE/C/S.

Timer is zero
for H/C/S/U focal examples.

Task demand is generated
from deterministic synthetic local request occupancy
on the 64-cell ring.

Generate C and S request occupancy
independently
using a deterministic mixture of occupancy densities
that includes:

0;
sparse;
moderate;
dense.

LC12 / LS12 / LC3 / LS3
must be produced
by the exact inherited Task-1 demand adapter.

Do not synthesize those four values independently.

This preserves valid fixed-perception geometry.

Distant request occupancy
may vary freely;
V0.2 teacher labels must remain local.

C/S symmetry must be present
in the generator.

TRAINING

Framework:
PyTorch CPU.

Deterministic algorithms:
ON.

Torch threads:
1.

Optimizer:
AdamW.

Learning rate:
0.001.

Weight decay:
0.00001.

Batch size:
512.

Epochs:
30.

Learning-rate schedule:
NONE.

Gradient clipping:
NONE.

Checkpoint selection:
FINAL EPOCH ONLY.

No hyperparameter search.

No post-result retraining.

LOSS

Use soft teacher probability targets.

H examples:

binary cross entropy with logits
against exact H-release probability.

C/S examples:

binary cross entropy with logits
against exact stay probability.

U examples:

cross entropy against
the full exact teacher distribution:

[C,S,H,U].

For every training batch:

compute the mean H loss
over H examples present;

mean STAY loss
over C/S examples present;

mean U loss
over U examples present.

Total batch loss:

L =
L_H
+
L_STAY
+
L_U.

If a batch happens to omit a head class,
that head contributes zero for that batch.

No auxiliary loss.

No task-performance reward.

No global regularizer.

DETERMINISM GATE

Run the complete training procedure twice
from the same frozen source,
LU1AF1,
dataset derivations,
and seed.

Canonicalize trained parameters
as:

parameter name
+
dtype
+
shape
+
raw contiguous tensor bytes

in sorted parameter-name order.

Required:

canonical weight SHA256
identical between training run 1 and run 2.

Final training metrics JSON
must also be byte-identical.

If training is not deterministic:

do not interpret test performance.

TEST METRICS

H RELEASE

mean absolute probability error.

95th percentile absolute error.

99th percentile absolute error.

maximum absolute error.

C/S STAY

same four metrics.

U RECRUITMENT

total-variation distance
between student and teacher
[C,S,H,U].

Report:

mean TV;

95th percentile TV;

99th percentile TV;

maximum TV.

Also report teacher target ranges
for each head
to demonstrate non-degenerate coverage.

SYMMETRY AUDIT

Construct 2000 held-out
C/S-swapped OBS-V1 pairs
from the frozen test generator.

Swap:

C <-> S state labels;

B sign;

LC12 <-> LS12;

LC3 <-> LS3;

Q_prev_side C <-> S.

Teacher outputs must swap exactly.

Student outputs are compared
after applying the same output swap.

Report mean and 99th percentile
student symmetry TV/error.

DEGENERATE-QUIESCENCE AUDIT

Construct 1000 held-out U examples
with:

no local C demand;

no local S demand;

no local support-margin source;

no H recruitment drive.

Teacher target is:

U = 1.

Report student predicted U probability.

QUALIFICATION

LU1A_IMITATION_QUALIFIED = TRUE iff all are true:

1. parameter count <=18000;

2. duplicate training canonical weight SHA256 identical;

3. duplicate final training metrics JSON byte-identical;

4. no global/task/future/position feature enters the model;

5. H RELEASE mean absolute error <=0.02;

6. H RELEASE 99th percentile absolute error <=0.08;

7. C/S STAY mean absolute error <=0.02;

8. C/S STAY 99th percentile absolute error <=0.08;

9. U recruitment mean TV <=0.03;

10. U recruitment 95th percentile TV <=0.08;

11. U recruitment 99th percentile TV <=0.12;

12. student C/S symmetry mean error/TV <=0.02;

13. student C/S symmetry 99th percentile error/TV <=0.08;

14. mean predicted U probability
    on degenerate-quiescence audit >=0.98;

15. 1st percentile predicted U probability
    on degenerate-quiescence audit >=0.90;

16. all outputs finite;

17. all probability outputs normalized / bounded.

These thresholds are frozen before training.

No threshold may be changed afterward.

INTERPRETATION RULE

If LU1A_IMITATION_QUALIFIED = FALSE:

do not place the learned updater
into closed-loop Task-1 dynamics.

Diagnose the failed approximation axis.

Do not automatically enlarge the model.

Any model-size,
feature,
loss,
or optimizer change
requires a new preregistered experiment.

If LU1A_IMITATION_QUALIFIED = TRUE:

the student has earned
only an imitation qualification.

Next:

preregister a closed-loop
teacher-versus-student Task-1 experiment
on fresh worlds.

That experiment must test:

full functional envelope;

anchor relocation;

demand reversal;

lesion response;

incorrect DONE;

operation cost;

role/reorganization telemetry;

and divergence from teacher trajectories.

Do not promote the learned updater
to the substrate
from LU-1A alone.

PERSISTENT INFORMATION LEDGER

Report:

trainable parameter count;

parameter bytes;

model file/canonical weight bytes;

training examples generated;

no retained training examples required at inference;

optimizer state not required at inference.

The student must not rely
on stored phenotype examples
or hidden task-specific tables.

MECHANICAL GATE

Before LU1AF1 prove:

1. input width = 70;

2. hidden widths = 128,64;

3. outputs = 6;

4. parameter count <=18000;

5. only OBS-V1 fields enter encoder;

6. no stage/task/phase/position/global/future channel;

7. teacher parent = V0.2;

8. dataset cardinalities exact;

9. class balancing exact;

10. train/validation/test seed namespaces distinct;

11. fixed 30-epoch schedule;

12. final-epoch-only checkpoint rule;

13. deterministic torch settings;

14. canonical weight hashing implemented;

15. test set not evaluated by mechanical gate;

16. duplicate mechanical structure byte-identical.

PLAIN-SPEAK QUESTION

This is the first time
we actually teach a cell.

We are not asking it
to run the whole organism yet.

We give one small shared neural network
the exact local information
that LU-0E proved is sufficient.

Then we show it
the probabilities produced
by the hand-designed V0.2 cell rule.

It must learn three things:

when an uncertain cell should release;

when a committed cell should stay;

and what a recruitable cell should become.

The same neural network
serves every cell.

It gets no map position,
no task name,
no global state,
and no future information.

We train it twice from the same frozen setup.

If the two trainings are not exactly reproducible,
we stop.

If they are reproducible,
we open a completely separate test set
and ask how closely the learned probabilities
match the hand-designed teacher.

Even if it passes,
we still do not replace the real organism.

Passing LU-1A only earns the right
to test the learned cell
inside the full living software system
on fresh worlds.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
