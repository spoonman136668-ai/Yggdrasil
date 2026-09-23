TITLE: LU-1B LU1BF1 DUPLICATE TRAINING GATE
DATE: 2026-09-23
STATUS: PASS / HELD-OUT TEST OPEN AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1BF1:
bdda0fab372187f71b889065698a7b0bf953f95a

SEED BINDING:
3ba742168d1724336ecc9269a73485ee56f0d79e

PREREGISTRATION:
a5524c912c67c861be4590a28d0e9f43a5243773

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
70 -> 128 -> 64 -> 6.

trainable parameters:
17734.

optimizer / learning rate / weight decay:
AdamW / 0.001 / 0.00001.

CANONICAL WEIGHTS

bytes each:
71105.

SHA256 both:
387a6348704e381046e4d0cd05f6a32b2e5da00864e9a9c718f61e2190cd4387.

byte identical:
TRUE.

TRAINING METRICS

SHA256 both:
27a99e55fc893ef66f7665f7ab08412484f462fd951cd18d7e6355920be50772.

byte identical:
TRUE.

FINAL TRAIN MEAN-BATCH EQUAL-HEAD LOSS

1.2492861974088452.

VALIDATION TOTAL EQUAL-HEAD LOSS

1.2344777584075928.

SEED IDENTITY

train data:
502655983500444875.

valid data:
9694845022939735731.

test data:
14608912084358458571.

train RNG:
16518927410859238074.

symmetry:
11636929758771673607.

quiescence:
6885936144843713252.

HELD-OUT TEST STATUS

LU-1B held-out test evaluations before this gate:
0.

Gate condition is satisfied.

The frozen fresh test set may now be opened once
against canonical weights SHA256:

387a6348704e381046e4d0cd05f6a32b2e5da00864e9a9c718f61e2190cd4387.

No retraining or hyperparameter change is authorized.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
