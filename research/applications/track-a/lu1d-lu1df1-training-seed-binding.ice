TITLE: LU-1D LU1DF1 TRAINING / DATA SEED BINDING
DATE: 2026-09-23
STATUS: BOUND AFTER LU1DF1 / BEFORE TRAINING
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1DF1:
1609425b3144e66ab373fb5ca7239888883ba351

FROZEN SOURCE:
bytes = 13562
sha256 = 8d74638a49c3206f5fa7461967de1d2151be7ef87980a2de86f5d83076934b1f

PREREGISTRATION:
46dd05d8bfe108bf3925d09ba45622a4164601e6

MECHANICAL GATE:
b379c77797b5ecb054a0153c3e45878329de9ff9

PARENT LU1CF1:
10f4a6d4cd012dd200d6df8e0e1e56f38e2606ec

PARENT LU-1C CLOSURE:
044685fb09a04a46cb15bbab91b74418221ce3a0

PARENT LU-1C RESIDUAL DIAGNOSTIC:
1e00984d9e23ada0b94107d039d4c6b506691128

DERIVATION

Each seed is the first unsigned big-endian 64 bits of:

SHA256(label + "|" + LU1DF1)

TRAIN DATA
label:
LU1D-TRAIN-DATA
seed:
279019949553630300

VALID DATA
label:
LU1D-VALID-DATA
seed:
4375678607704069369

TEST DATA
label:
LU1D-TEST-DATA
seed:
9539573411597111788

TRAIN RNG
label:
LU1D-TRAIN-RNG
seed:
2248740020908408423

SYMMETRY
label:
LU1D-SYMMETRY
seed:
4603546316075662205

QUIESCENCE
label:
LU1D-QUIESCENCE
seed:
12390433675675883523

DISTINCTNESS

all six seeds distinct:
TRUE.

BINDING RULE

No seed may change.

No dataset count may change.

No training hyperparameter may change.

No pair encoder, aggregation, gate, value path,
or output geometry may change.

No canonical-transform rule may change.

No qualification threshold or permutation tolerance may change.

Duplicate complete training must finish
before the fresh held-out LU-1D test is opened.

TRAINING STATUS AT BINDING

training runs executed:
0.

held-out LU-1D tests opened:
0.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
