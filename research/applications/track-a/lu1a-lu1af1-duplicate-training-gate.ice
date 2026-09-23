TITLE: LU-1A LU1AF1 DUPLICATE TRAINING GATE
DATE: 2026-09-23
STATUS: PASS / HELD-OUT TEST OPENING AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
01c5f6b7072b712ac287cc8757e08fb5e96ca6aa

MECHANICAL GATE:
1a89a39c57a36e672cee363a554c0f8a1cf3e7e7

LU1AF1:
d1c6de67fe33cd48d5163dd08dcdc3112c5b0013

SEED BINDING:
67faea47c66c655e3002f782a86baaa7501a33b0

PARENT V0.2:
e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2

LU-0E CLOSURE:
94eda73cf865a131365ac4cbe943dc558daaece1

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

PyTorch:
2.10.0+cpu.

NumPy:
2.3.5.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

COMPLETE TRAINING RUNS

runs:
2.

Each run independently:

derived the frozen 40000-example train set;

derived the frozen 8000-example validation set;

initialized from the frozen LU1A-TRAIN-RNG seed;

executed exactly 30 epochs;

used AdamW lr 0.001;

weight decay 0.00001;

batch size 512;

used the final epoch only;

and serialized canonical weights.

RUN 1

canonical weight bytes:
71105.

canonical weight SHA256:
2969022d99944928a12df9d91a96114da877354d433582e20e06d63c3325c12f.

training metrics JSON bytes:
739.

training metrics JSON SHA256:
3ed77ad57456ace477cdec30a35f91db60e3b51069706439011ebe00ddd3d69b.

RUN 2

canonical weight bytes:
71105.

canonical weight SHA256:
2969022d99944928a12df9d91a96114da877354d433582e20e06d63c3325c12f.

training metrics JSON bytes:
739.

training metrics JSON SHA256:
3ed77ad57456ace477cdec30a35f91db60e3b51069706439011ebe00ddd3d69b.

DETERMINISM GATE

canonical weight byte identity:
PASS.

training metrics JSON byte identity:
PASS.

TRAINING METRICS

train examples:
40000.

validation examples:
8000.

parameter count:
17734.

final train mean batch equal-head loss:
1.2602440043340755.

validation total equal-head loss:
1.2953544855117798.

Validation remained report-only.

No early stopping.

No checkpoint selection.

TEST BLINDING

The held-out LU1A-TEST-DATA set
has not been generated or evaluated
before this duplicate-training gate.

The symmetry audit set
has not been evaluated.

The quiescence audit set
has not been evaluated.

No LU1A imitation qualification
has been calculated.

AUTHORIZATION

The preregistered determinism condition is satisfied.

The canonical model for held-out testing is:

weight SHA256:
2969022d99944928a12df9d91a96114da877354d433582e20e06d63c3325c12f.

The frozen held-out test,
symmetry,
and quiescence audits
may now be executed.

No training,
model,
feature,
optimizer,
or qualification threshold
may change before test interpretation.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
