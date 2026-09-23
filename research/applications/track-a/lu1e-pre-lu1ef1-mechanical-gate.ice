TITLE: LU-1E PRE-LU1EF1 MECHANICAL GATE
DATE: 2026-09-23
STATUS: PASS / LU1EF1 FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
1adbbfc33514fc3143f98a5d85ffb4d5b99ae3eb

CANDIDATE COMMIT:
9653afcb2e7d77c6fb30f9a286b6591939fdf46f

PARENT V0.2:
e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2

PARENT LU1DF1:
1609425b3144e66ab373fb5ca7239888883ba351

PARENT LU-1D CLOSURE:
f9625901264f32ad774d69378001a2c3a8a3b2ef

PARENT LU-1D DIAGNOSTIC:
94ce811906de8df6445d81aafaa673cf2ac686d4

CANDIDATE SOURCE

bytes:
13963

SHA256:
38c3d42786426d4ace4a779b69d49509d65a7eb31f9bfa3c4209e603879d0b2a

DETERMINISTIC PUBLICATION

gzip level:
9

gzip mtime:
0

gzip bytes:
4951

gzip SHA256:
a2455d35710e540d5da7f83a7c4df6710d4af850a1a17a2e7403a9e7e6597134

base64 characters:
6604

base64 SHA256:
ca05287ca5318011868482baf009c29ce6b1014f786e82d77098521e45c426b6

source chunks:
4

chunk sizes:
2048;
2048;
2048;
460.

MECHANICAL DUPLICATE GATE

complete mechanical invocations:
2

byte identical:
TRUE

mechanical evidence SHA256:
98e3d7fa62940279dd05e1f7391cc8529df22e944f947c22ae0262bd0f023817

PROBES

semantic input exactly OBS-V1 width 70:
PASS.

exact LU-1B focal-side canonicalization:
PASS.

full committed C/S mirror canonicalizes byte-identically:
PASS.

mirrored teacher stay probabilities identical:
PASS.

H canonicalization identity:
PASS.

U canonicalization identity:
PASS.

one six-category state relation bank:
PASS.

same relation-bank parameters shared across all seven cell slots:
PASS.

relation bank reads only state category plus B/LC12/LS12:
PASS.

exactly six nonfocal slots:
PASS.

nonfocal aggregation arithmetic mean:
PASS.

no neighbor-slot or position parameters:
PASS.

Q-side relation bank has exactly three categories:
PASS.

Q-side relation bank reads only Q_prev and Q_prev_side:
PASS.

other-extra encoder reads only timer/D, LC3, LS3:
PASS.

context width = 80:
PASS.

value stream = 80 -> 64 / SiLU:
PASS.

gate stream = 80 -> 64 / sigmoid:
PASS.

single elementwise value*gate interaction:
PASS.

output = 64 -> 32 -> 6:
PASS.

trainable parameter count = 13694:
PASS.

parameter ceiling <=18000:
PASS.

no attention / recurrence / dropout / batchnorm / position embedding:
PASS.

no forbidden teacher-derived feature:
PASS.

neighbor permutation maximum logit difference:
1.4901161193847656e-08

required:
<=1e-05

PASS.

teacher exact inherited V0.2:
PASS.

data / optimizer / schedule / loss inherited:
PASS.

six post-freeze seed namespaces structurally distinct:
PASS.

duplicate mechanical structure:
PASS.

TRAINING STATUS

LU1EF1 does not yet exist.

No LU-1E training seed has been derived.

No LU-1E train, validation, or held-out test dataset has executed.

No LU-1E model has trained.

No held-out LU-1E result has been opened.

FREEZE AUTHORIZATION

Freeze exactly source SHA256:

38c3d42786426d4ace4a779b69d49509d65a7eb31f9bfa3c4209e603879d0b2a

as LU1EF1.

Only after LU1EF1 exists:

derive and bind the six fresh seeds;

run complete training twice;

require canonical weight-byte identity
and training-metrics byte identity;

then and only then
open the fresh held-out test set once.

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
