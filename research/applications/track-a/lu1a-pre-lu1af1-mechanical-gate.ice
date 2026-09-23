TITLE: LU-1A PRE-LU1AF1 MECHANICAL GATE
DATE: 2026-09-23
STATUS: PASS / LU1AF1 FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
01c5f6b7072b712ac287cc8757e08fb5e96ca6aa

PARENT V0.2:
e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2

LU-0E CLOSURE:
94eda73cf865a131365ac4cbe943dc558daaece1

CANDIDATE SOURCE

bytes:
17518

SHA256:
c493e9353b98563139fafb8c5dd5a46b8152b780f6148b248c7e17f57f304700

DETERMINISTIC PUBLICATION

gzip level:
9

gzip mtime:
0

gzip bytes:
6130

gzip SHA256:
4c22c2aea31961330d7324bde7209e01bda909fb640170c1c670337e75460649

base64 characters:
8176

base64 SHA256:
dbd3a1f9b8ca99a91276e3d9ed4bd66cb9f3b7a9185272b14648052836ec7767

source chunks:
4

chunk sizes:
2048;
2048;
2048;
2032

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

Python:
system Python with site packages enabled.

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

MECHANICAL DUPLICATE GATE

complete invocations:
2

serialized evidence bytes:
885 each

serialized evidence SHA256:
437f4618da34b5a317a774b4948b7a5d7dfc2adcc68b2a218d7818fd94d05309

byte identical:
TRUE

MODEL

input:
70.

hidden:
128;
64.

output:
6.

trainable parameters:
17734.

parameter ceiling:
18000.

PASS.

TEACHER PARITY

Exact analytic local teacher
versus frozen LU-0E teacher
on all 16 LU-0E local templates:

maximum discrepancy:
0.0.

PASS.

PROBES

input width 70:
PASS.

hidden widths 128 / 64:
PASS.

outputs 6:
PASS.

parameter count <=18000:
PASS.

only OBS-V1 features:
PASS.

no stage/task/phase/position/global/future input:
PASS.

teacher parent V0.2:
PASS.

dataset sizes 40000 / 8000 / 12000:
PASS.

balanced focal classes:
PASS.

seed namespaces distinct:
PASS.

fixed 30 epochs:
PASS.

final-epoch-only checkpoint:
PASS.

deterministic Torch configuration implemented:
PASS.

canonical weight hashing implemented:
PASS.

test set not evaluated:
PASS.

duplicate mechanical structure:
PASS.

SCIENTIFIC BLINDING

No LU1AF1 exists yet.

No train dataset has been generated.

No validation dataset has been generated.

No test dataset has been generated.

No optimizer step has executed.

No learned weight exists.

No imitation metric has been inspected.

FREEZE AUTHORIZATION

Freeze this exact source
as LU1AF1.

After LU1AF1 exists:

derive and bind exact seed identities;

run the complete fixed training twice;

require canonical weight identity
and byte-identical training metrics;

only then open the held-out test set.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
