TITLE: LU-1B PRE-LU1BF1 MECHANICAL GATE
DATE: 2026-09-23
STATUS: PASS / LU1BF1 FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
a5524c912c67c861be4590a28d0e9f43a5243773

PARENT LU1AF1:
d1c6de67fe33cd48d5163dd08dcdc3112c5b0013

PARENT LU-1A CLOSURE:
5c81b6f38f9a0b4d05ccbcaad89ef7c2a9d7e745

PARENT LU-1A DIAGNOSTIC:
0d499c003ee955e233e31f9d336a4eeba6993338

CANDIDATE SOURCE

bytes:
12351

SHA256:
ecc52037e85ac684722e2a0ed2e01641e45e3d239134a5b4b104dc8dbfdd883c

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
897.

serialized evidence SHA256:
7c9da78f2af535433c86efeeac4b1116cc2e49f6be4e0b0b6f7299d50afd298d.

byte identical:
TRUE.

PROBES

model dimensions exactly LU-1A 70 -> 128 -> 64 -> 6:
PASS.

trainable parameter count = 17734:
PASS.

no new input field:
PASS.

focal C transform = identity:
PASS.

focal S transform swaps exactly:
C/S;
FC/FS;
B sign;
LC12/LS12;
Q-side C/S;
LC3/LS3:
PASS.

focal H transform = identity:
PASS.

focal U transform = identity:
PASS.

raw committed C observation and exact C/S-swapped S counterpart
canonicalize to byte-identical model input:
PASS.

teacher stay probability of that swapped pair exactly equal:
PASS.

observed teacher pair absolute difference:
0.0.

canonicalization idempotent on canonical committed input:
PASS.

no mode / pressure / qraw / qeff / target added:
PASS.

data counts and training schedule exactly LU-1A:
PASS.

six post-freeze seed namespaces distinct:
PASS.

duplicate mechanical structure:
PASS.

STRUCTURE IDENTITY

bytes:
244.

SHA256:
5445659ad8b727cd6dc2e38ea8d80819160d1b2d591921d58d8f25cc4948b95a

SCIENTIFIC BLINDING

No LU1BF1 exists yet.

No LU-1B train/valid/test seed has been derived.

No LU-1B training has executed.

No LU-1B held-out test has been opened.

FREEZE AUTHORIZATION

Freeze this exact source identity as LU1BF1.

Only after LU1BF1 exists:

derive the six frozen LU-1B seeds;

bind them before training;

run complete training twice;

require canonical weight bytes and metrics byte-identical;

then open the fresh held-out test set.

No hyperparameter, architecture, loss, threshold,
dataset-size, or canonical-transform change is authorized
after training begins.

PLAIN-SPEAK INTERPRETATION

The repair is mechanically what we intended.

We did not make the neural cell larger.

We did not add information.

We only changed the viewpoint used by already-committed cells
so SELF always looks like C and OPPONENT always looks like S.

Mirrored C/S situations now become literally the same neural input.

The teacher agrees exactly that those mirrored situations
should have the same stay probability.

The experiment is therefore ready to freeze
before any learning result is visible.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
