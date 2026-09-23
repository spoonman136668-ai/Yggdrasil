TITLE: LU-1C LU1CF1 TRAINING / DATA SEED BINDING
DATE: 2026-09-23
STATUS: BOUND AFTER LU1CF1 / BEFORE TRAINING
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1CF1:
10f4a6d4cd012dd200d6df8e0e1e56f38e2606ec

FROZEN SOURCE:
bytes = 13204
sha256 = e4abb65ac7abf2909cb8df5ceb7f3bfd8bcf142bf5a7c6453e90fbd4e828f7c1

PREREGISTRATION:
c77e622a08d6bd15c74c75ff61ddc5aefb9ade2d

MECHANICAL GATE:
c7909617581b676d0e244ce2a1af86222c2867e6

PARENT LU1BF1:
bdda0fab372187f71b889065698a7b0bf953f95a

PARENT LU-1B CLOSURE:
0579573b3483c17a1932210eca245ec37c65b63e

PARENT LU-1B RESIDUAL DIAGNOSTIC:
b6957f04bbb9f3f047bbf6f0ff485fe2560c960d

DERIVATION

Each seed is the first unsigned big-endian 64 bits of:

SHA256(label + "|" + LU1CF1)

TRAIN DATA
label:
LU1C-TRAIN-DATA
seed:
16552792480449611933

VALID DATA
label:
LU1C-VALID-DATA
seed:
131082024586281972

TEST DATA
label:
LU1C-TEST-DATA
seed:
15086128415640175680

TRAIN RNG
label:
LU1C-TRAIN-RNG
seed:
10727793279095647554

SYMMETRY
label:
LU1C-SYMMETRY
seed:
13293065989730539888

QUIESCENCE
label:
LU1C-QUIESCENCE
seed:
17798153824267588879

DISTINCTNESS

all six seeds distinct:
TRUE.

BINDING RULE

No seed may change.

No dataset count may change.

No training hyperparameter may change.

No model geometry may change.

No aggregation rule may change.

No canonical-transform rule may change.

No qualification threshold may change.

Duplicate complete training must finish
before the fresh held-out test set is opened.

TRAINING STATUS AT BINDING

training runs executed:
0.

held-out LU-1C tests opened:
0.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
