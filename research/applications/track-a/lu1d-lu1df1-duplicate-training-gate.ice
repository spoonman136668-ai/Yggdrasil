TITLE: LU-1D LU1DF1 DUPLICATE TRAINING GATE
DATE: 2026-09-23
STATUS: PASS / HELD-OUT TEST OPEN AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1DF1:
1609425b3144e66ab373fb5ca7239888883ba351

SEED BINDING:
31c52075b50f3550c132c1019b1e9072447cadd0

PREREGISTRATION:
46dd05d8bfe108bf3925d09ba45622a4164601e6

TRAINING ENVIRONMENT

Isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

Python site initialization:
DISABLED.

TRAINING RUNS

complete runs:
2.

train examples per run:
40000.

validation examples per run:
8000.

epochs:
30.

batch:
512.

model:
shared focal-neighbor pair encoder 18 -> 32 -> 32;
six-pair mean;
focal encoder 9 -> 16;
extra encoder 7 -> 16;
value 64 -> 64;
gate 64 -> 64;
elementwise value*gate;
output 64 -> 32 -> 6.

trainable parameters:
12550.

optimizer / learning rate / weight decay:
AdamW / 0.001 / 0.00001.

CANONICAL WEIGHTS

bytes each:
50653.

SHA256 both:
2c8ee801e16dca803eb9a225dc7b711b168840ddb99cd7c93a058d4d4739a3eb.

byte identical:
TRUE.

TRAINING METRICS

SHA256 both:
7b451f086756f5c4be891ed9df576db5dadccbfb68c301989c3d23f2cb9506d7.

byte identical:
TRUE.

FINAL TRAIN MEAN-BATCH EQUAL-HEAD LOSS

1.246951245054414.

VALIDATION TOTAL EQUAL-HEAD LOSS

1.2202576398849487.

SEEDS

train data:
279019949553630300.

valid data:
4375678607704069369.

test data:
9539573411597111788.

train RNG:
2248740020908408423.

symmetry:
4603546316075662205.

quiescence:
12390433675675883523.

HELD-OUT TEST STATUS

LU-1D held-out test evaluations before this gate:
0.

Gate condition is satisfied.

The frozen fresh test set may now be opened once
against canonical weights SHA256:

2c8ee801e16dca803eb9a225dc7b711b168840ddb99cd7c93a058d4d4739a3eb.

No retraining or hyperparameter change is authorized.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
