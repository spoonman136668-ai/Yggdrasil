TITLE: LU-1E LU1EF1 DUPLICATE TRAINING GATE
DATE: 2026-09-23
STATUS: PASS / HELD-OUT TEST OPEN AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1EF1:
f459273c897a7bd889b6de2ec2d9720374215327

SEED BINDING:
cdad7f1577313160a419fcec07b27c222ebd6879

PREREGISTRATION:
1adbbfc33514fc3143f98a5d85ffb4d5b99ae3eb

TRAINING ENVIRONMENT

Isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

TRAINING RUNS

complete runs:
2

train examples per run:
40000

validation examples per run:
8000

epochs:
30

batch:
512

architecture:
shared six-category state-conditioned 3 -> 16 relation bank;
shared 16 -> 24 post transform;
same bank for all seven cell slots;
six nonfocal cell mean;
focal representation 24;
three-category Q-side 1 -> 8 relation bank;
Q-side 8 -> 16 post transform;
timer/LC3/LS3 3 -> 16;
context 80;
value 80 -> 64;
gate 80 -> 64;
elementwise value*gate;
output 64 -> 32 -> 6.

trainable parameters:
13694

optimizer / learning rate / weight decay:
AdamW / 0.001 / 0.00001

CANONICAL WEIGHTS

bytes each:
55917

SHA256 both:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

byte identical:
TRUE

TRAINING METRICS

bytes each:
928

SHA256 both:
e5a54d75e37b475653a3bb3384fa27c791f928c0d50953a105a80144dd3d0c8e

byte identical:
TRUE

FINAL TRAIN MEAN-BATCH EQUAL-HEAD LOSS

1.2409695477425298

VALIDATION TOTAL EQUAL-HEAD LOSS

1.2430675029754639

BOUND SEEDS

train data:
17513806788112854841

valid data:
3383256385979393164

test data:
6527350706768495827

train RNG:
15950533691745232350

symmetry:
1680958176011558531

quiescence:
680341377581921091

HELD-OUT TEST STATUS

LU-1E held-out test evaluations before this gate:
0

Gate condition is satisfied.

The frozen fresh held-out test set
may now be opened once
against canonical weights SHA256:

b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

No retraining or hyperparameter change is authorized.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
