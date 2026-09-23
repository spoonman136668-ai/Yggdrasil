TITLE: LU-1C PRE-LU1CF1 MECHANICAL GATE
DATE: 2026-09-23
STATUS: PASS / LU1CF1 FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
c77e622a08d6bd15c74c75ff61ddc5aefb9ade2d

PARENT LU1BF1:
bdda0fab372187f71b889065698a7b0bf953f95a

PARENT LU-1B CLOSURE:
0579573b3483c17a1932210eca245ec37c65b63e

PARENT LU-1B RESIDUAL DIAGNOSTIC:
b6957f04bbb9f3f047bbf6f0ff485fe2560c960d

CANDIDATE SOURCE

bytes:
13204

SHA256:
e4abb65ac7abf2909cb8df5ceb7f3bfd8bcf142bf5a7c6453e90fbd4e828f7c1

DETERMINISTIC PUBLICATION

gzip level:
9

gzip mtime:
0

gzip bytes:
4705

gzip SHA256:
2f4bf869396d2fd48b80248418d3ce544862e314d77a34b747c25aa02e4b1156

base64 characters:
6276

base64 SHA256:
cb871c72c783e2e00404a35210c977063cd150a635651bdbb210a931f4a5a56e

source chunks:
4

chunk sizes:
2048;
2048;
2048;
132.

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

Python site initialization:
DISABLED.

MECHANICAL DUPLICATE GATE

runs:
2.

serialized evidence bytes:
1183.

serialized evidence SHA256:
f22a00a015d9642b2fee282230f934c56851d2c60c2a758bed6e49a600ccddf7.

byte identical:
TRUE.

MODEL STRUCTURE

OBS-V1 information width:
70.

cell slot width:
9.

shared cell encoder:
9 -> 32 -> 32.

nonfocal aggregation:
arithmetic mean of six encoded neighbors.

focal-extra encoder:
7 -> 16.

combined trunk input:
80.

output trunk:
80 -> 64 -> 32 -> 6.

trainable parameter count:
8966.

parameter ceiling:
18000.

PROBES

input information exactly OBS-V1:
PASS.

LU-1B focal-side canonicalization exact:
PASS.

full committed C/S mirror canonical input identity:
PASS.

teacher stay symmetry on exact mirror:
PASS.

cell-slot width = 9:
PASS.

exactly one shared cell encoder:
PASS.

no separate neighbor encoders:
PASS.

no slot-specific or position parameters:
PASS.

six nonfocal encodings combined by mean:
PASS.

focal extras exactly seven:
PASS.

extra encoder = 7 -> 16:
PASS.

trunk = 80 -> 64 -> 32 -> 6:
PASS.

parameter count = 8966:
PASS.

parameter count <=18000:
PASS.

neighbor permutation invariance:
PASS.

maximum observed logit difference under nonfocal permutation:
1.4901161193847656e-08.

focal slot excluded from neighbor mean:
PASS.

no forbidden mode / pressure / qraw / qecho / qeff / target feature:
PASS.

H input semantics unchanged:
PASS.

U input semantics unchanged:
PASS.

teacher exact LU-1A / LU-1B / V0.2:
PASS.

data counts and training schedule exact LU-1A / LU-1B:
PASS.

six future seed namespaces distinct:
PASS.

duplicate mechanical structure:
PASS.

STRUCTURE IDENTITY

bytes:
332.

SHA256:
3b1333434c170e3a4dd942918946da396ffac802c9767aaf91c5a4a854884882.

SCIENTIFIC BLINDING

No LU1CF1 exists yet.

No LU-1C training/data seed has been derived.

No LU-1C training has executed.

No LU-1C held-out test has been opened.

FREEZE AUTHORIZATION

Freeze this exact source identity as LU1CF1.

Only after LU1CF1 exists:

derive the six frozen LU-1C seeds;

bind them before training;

run complete training twice;

require canonical weight bytes and metrics byte-identical;

then open the fresh held-out test set.

No model geometry, optimizer, loss, data count,
canonicalization, qualification threshold,
or interpretation rule may change after training begins.

PLAIN-SPEAK INTERPRETATION

The new neural cell is mechanically what we intended.

It receives exactly the same local information as before.

But instead of treating six neighbors
as unrelated positions in one long vector,
it examines every neighbor with the same small neural rule
and combines them symmetrically.

The focal cell stays separate.

Its short-term local memory stays separate.

The model is not larger.

It has only 8,966 trainable parameters,
about half the previous flat network.

Changing neighbor list order does not change its answer.

So the next result will test network structure,
not extra information or brute-force capacity.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
