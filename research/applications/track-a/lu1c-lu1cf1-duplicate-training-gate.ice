TITLE: LU-1C LU1CF1 DUPLICATE TRAINING GATE
DATE: 2026-09-23
STATUS: PASS / HELD-OUT TEST OPEN AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1CF1:
10f4a6d4cd012dd200d6df8e0e1e56f38e2606ec

SEED BINDING:
bb3ff579a66004334f969e5a337d69ed3e5cfc58

PREREGISTRATION:
c77e622a08d6bd15c74c75ff61ddc5aefb9ade2d

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
shared cell encoder 9 -> 32 -> 32;
six-neighbor mean;
focal extras 7 -> 16;
trunk 80 -> 64 -> 32 -> 6.

trainable parameters:
8966.

optimizer / learning rate / weight decay:
AdamW / 0.001 / 0.00001.

CANONICAL WEIGHTS

bytes each:
36213.

SHA256 both:
c3cb57e6ac6da729a045bc4866c5020b404f3713c9bd03fced60e64757e7112b.

byte identical:
TRUE.

TRAINING METRICS

SHA256 both:
25360386ffd78c924ea3b7ebda87b1398ff4f0768ca69226463e968bcaecf50a.

byte identical:
TRUE.

FINAL TRAIN MEAN-BATCH EQUAL-HEAD LOSS

1.242305056958259.

VALIDATION TOTAL EQUAL-HEAD LOSS

1.2286604642868042.

SEED IDENTITY

train data:
16552792480449611933.

valid data:
131082024586281972.

test data:
15086128415640175680.

train RNG:
10727793279095647554.

symmetry:
13293065989730539888.

quiescence:
17798153824267588879.

EXECUTION NOTE

The first combined shell command attempted both complete training runs
inside one sandbox invocation and reached the sandbox wall-clock limit
after the first training artifact had completed.

That timeout is not a scientific or training failure.

The second frozen training run was then executed separately
with identical source, seed, data, and parameters.

The two completed outputs match byte-for-byte.

No partial artifact entered the duplicate gate.

HELD-OUT TEST STATUS

LU-1C held-out test evaluations before this gate:
0.

Gate condition is satisfied.

The frozen fresh test set may now be opened once
against canonical weights SHA256:

c3cb57e6ac6da729a045bc4866c5020b404f3713c9bd03fced60e64757e7112b.

No retraining or hyperparameter change is authorized.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
