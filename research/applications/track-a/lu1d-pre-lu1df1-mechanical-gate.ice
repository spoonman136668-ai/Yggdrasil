TITLE: LU-1D PRE-LU1DF1 MECHANICAL GATE
DATE: 2026-09-23
STATUS: PASS / LU1DF1 FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
46dd05d8bfe108bf3925d09ba45622a4164601e6

PARENT LU1CF1:
10f4a6d4cd012dd200d6df8e0e1e56f38e2606ec

PARENT LU-1C CLOSURE:
044685fb09a04a46cb15bbab91b74418221ce3a0

PARENT LU-1C RESIDUAL DIAGNOSTIC:
1e00984d9e23ada0b94107d039d4c6b506691128

CANDIDATE SOURCE

bytes:
13562

SHA256:
8d74638a49c3206f5fa7461967de1d2151be7ef87980a2de86f5d83076934b1f

DETERMINISTIC PUBLICATION

gzip level:
9

gzip mtime:
0

gzip bytes:
4776

gzip SHA256:
54de5eba252b9058f5335e2ddce5428bffb091ba25ab5cdcd91d8cad129c7f64

base64 characters:
6368

base64 SHA256:
f32581967886939bcefc4d07bf77819ac210249f96d97a1e482d3f2e00d36964

source chunks:
4

chunk sizes:
2048;
2048;
2048;
224.

MECHANICAL DUPLICATE GATE

runs:
2.

serialized evidence bytes:
1306.

serialized evidence SHA256:
d6f9ff3accf7f7e0f5d82e881ac5e6e6be225bd799b03ab014365f99881f3ea0.

byte identical:
TRUE.

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

PROBES

semantic input exactly OBS-V1:
PASS.

LU-1B focal-side canonicalization exact:
PASS.

full committed C/S mirror canonical identity:
PASS.

pair width = 18:
PASS.

one shared pair encoder 18 -> 32 -> 32:
PASS.

pair encoder used only for six nonfocal neighbors:
PASS.

no neighbor-specific parameters:
PASS.

pair aggregation = mean:
PASS.

focal encoder = 9 -> 16:
PASS.

focal-extra encoder = 7 -> 16:
PASS.

context width = 64:
PASS.

value = 64 -> 64 + SiLU:
PASS.

gate = 64 -> 64 + sigmoid:
PASS.

single elementwise value*gate interaction:
PASS.

output = 64 -> 32 -> 6:
PASS.

trainable parameter count = 12550:
PASS.

parameter count <=18000:
PASS.

no attention / recurrence / position embedding:
PASS.

neighbor permutation numerical probe <=1e-5:
PASS.

observed maximum logit difference:
1.4901161193847656e-08.

no forbidden derived feature:
PASS.

H semantics unchanged:
PASS.

U semantics unchanged:
PASS.

teacher exact V0.2:
PASS.

data/training exact inherited contract:
PASS.

six future seed namespaces distinct:
PASS.

duplicate mechanical structure:
PASS.

STRUCTURE IDENTITY

bytes:
381.

SHA256:
ae2c0f6971112316b64a577d11db12603f6a36972c589aeeb673a8dc87b4baa1.

SCIENTIFIC BLINDING

No LU1DF1 exists yet.

No LU-1D train/valid/test seed has been derived.

No LU-1D training has executed.

No LU-1D held-out test has been opened.

FREEZE AUTHORIZATION

Freeze this exact source identity as LU1DF1.

Only after LU1DF1 exists:

derive six fresh seeds;

bind before training;

run complete training twice;

require byte-identical canonical weights and metrics;

then open the fresh held-out test.

No post-result change is authorized.

PLAIN-SPEAK INTERPRETATION

The gated model is mechanically clean.

Every neighbor is compared with the focal cell
through the same learned pair rule.

Those six pair summaries are combined symmetrically.

Then one learned path produces a value
and another produces a gate.

The two are multiplied.

That gives the model a direct way
to learn when one local signal should matter
without telling it the challenge rule.

It still sees only OBS-V1.

It is still below the original parameter ceiling.

No training result has been seen yet.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
