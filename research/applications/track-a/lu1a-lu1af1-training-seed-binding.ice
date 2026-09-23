TITLE: LU-1A LU1AF1 TRAINING / DATA SEED BINDING
DATE: 2026-09-23
STATUS: BOUND AFTER LU1AF1 / BEFORE DATASET GENERATION OR OPTIMIZER EXECUTION
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
01c5f6b7072b712ac287cc8757e08fb5e96ca6aa

MECHANICAL GATE:
1a89a39c57a36e672cee363a554c0f8a1cf3e7e7

LU1AF1:
d1c6de67fe33cd48d5163dd08dcdc3112c5b0013

PARENT V0.2:
e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2

LU-0E CLOSURE:
94eda73cf865a131365ac4cbe943dc558daaece1

FROZEN SOURCE:
bytes = 17518
sha256 = c493e9353b98563139fafb8c5dd5a46b8152b780f6148b248c7e17f57f304700

SEED DERIVATION

seed64(label) =
unsigned big-endian integer
from the first 8 bytes of:

SHA256(label + "|" + LU1AF1)

TRAIN DATA

label:
LU1A-TRAIN-DATA

seed64:
8347224665891909091

examples:
40000

balanced:
H 10000
C 10000
S 10000
U 10000

VALIDATION DATA

label:
LU1A-VALID-DATA

seed64:
6449823474641458300

examples:
8000

balanced:
H 2000
C 2000
S 2000
U 2000

Validation is report-only.

No early stopping.

No checkpoint selection.

TEST DATA

label:
LU1A-TEST-DATA

seed64:
3844385596907545809

examples:
12000

balanced:
H 3000
C 3000
S 3000
U 3000

The test set is not to be generated/evaluated
until duplicate complete training passes.

TRAINING RNG

label:
LU1A-TRAIN-RNG

seed64:
1736448498807086032

SYMMETRY AUDIT

label:
LU1A-SYMMETRY

seed64:
17590282262860288454

QUIESCENCE AUDIT

label:
LU1A-QUIESCENCE

seed64:
6852673584180758321

DISTINCTNESS

All six seeds:
distinct.

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

Python:
system Python with site packages enabled.

PyTorch:
2.10.0+cpu.

NumPy:
2.3.5.

Torch deterministic algorithms:
ON.

Torch intra-op threads:
1.

Torch inter-op threads:
1.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

TRAINING CONTRACT

model:
70 -> 128 -> 64 -> 6 shared MLP.

trainable parameters:
17734.

optimizer:
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

checkpoint selection:
FINAL EPOCH ONLY.

Two complete training runs
must independently derive the same data
from this binding
and finish with:

identical canonical weight bytes / SHA256;

and

byte-identical final training metrics JSON.

Only then may the held-out test set be opened.

BINDING RULE

Do not replace any seed.

Do not add a training replicate
to select a favorable outcome.

Do not inspect test metrics
before duplicate training identity passes.

Do not change model,
optimizer,
dataset size,
batch size,
epoch count,
loss,
or qualification thresholds
after this binding.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
