TITLE: LU-1B LU1BF1 TRAINING / DATA SEED BINDING
DATE: 2026-09-23
STATUS: BOUND AFTER LU1BF1 / BEFORE TRAINING
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1BF1:
bdda0fab372187f71b889065698a7b0bf953f95a

FROZEN SOURCE:
bytes = 12351
sha256 = ecc52037e85ac684722e2a0ed2e01641e45e3d239134a5b4b104dc8dbfdd883c

PREREGISTRATION:
a5524c912c67c861be4590a28d0e9f43a5243773

MECHANICAL GATE:
7f3ec3df2fe24fd75be359efd7738f0681e12347

PARENT LU1AF1:
d1c6de67fe33cd48d5163dd08dcdc3112c5b0013

PARENT LU-1A CLOSURE:
5c81b6f38f9a0b4d05ccbcaad89ef7c2a9d7e745

PARENT LU-1A DIAGNOSTIC:
0d499c003ee955e233e31f9d336a4eeba6993338

DERIVATION

Each seed is the first unsigned big-endian 64 bits of:

SHA256(label + "|" + LU1BF1)

TRAIN DATA
label:
LU1B-TRAIN-DATA
seed:
502655983500444875

VALID DATA
label:
LU1B-VALID-DATA
seed:
9694845022939735731

TEST DATA
label:
LU1B-TEST-DATA
seed:
14608912084358458571

TRAIN RNG
label:
LU1B-TRAIN-RNG
seed:
16518927410859238074

SYMMETRY
label:
LU1B-SYMMETRY
seed:
11636929758771673607

QUIESCENCE
label:
LU1B-QUIESCENCE
seed:
6885936144843713252

DISTINCTNESS

all six seeds distinct:
TRUE.

BINDING RULE

No seed may change.

No dataset count may change.

No training hyperparameter may change.

No model dimension may change.

No canonical-transform rule may change.

No qualification threshold may change.

Duplicate complete training must finish
before the fresh held-out test set is opened.

TRAINING STATUS AT BINDING

training runs executed:
0.

held-out LU-1B tests opened:
0.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
