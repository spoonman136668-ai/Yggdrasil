TITLE: LU-0B PRE-LU0BF1 MECHANICAL GATE
DATE: 2026-09-23
STATUS: PASS / LU0BF1 FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
fc0332e5ab625e5aa05b931dbf47a43034760dfd

PARENT V0.1:
4d3887fba0478bc1ef3bc4bea44f8e08582f5803

LU-0 CLOSURE:
074513c64a64318053fcbfcabdc9207202849063

LU0F1:
67b4c725193c6af707f5d3937d6854006704bfaa

TASK-1H CLOSURE:
1b848079ae0d54dd9e7b01c8d004a93b16aeb62d

PARENT TASK-1F T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063

CANDIDATE SOURCE

bytes:
13906

SHA256:
b2ef10e618871a081871d8858b3fcd153228cb831a643dc068bd3b30d9f6358f

DETERMINISTIC PUBLICATION

gzip level:
9

gzip mtime:
0

gzip bytes:
4381

gzip SHA256:
ec64b6300c6452e6890ffb01384df8b4dcdc7281c89c3dda1b3c383dcae5e7ed

base64 characters:
5844

base64 SHA256:
cfab9d8e472030e98e7624a3d3f88f711436f434db9cb8791241bf7f6c3f20ed

source chunks:
3

chunk sizes:
2048;
2048;
1748.

MECHANICAL DUPLICATE GATE

full mechanical runs:
2

bytes each:
440

SHA256:
aed88078fbf0b8edf2ba51c197942fc2198c8cb5c1d8b9cb82a8ef73f2d2e893

byte identical:
true

observed parent payload bytes:
33427

observed parent payload SHA256:
533ae706e92a6327a59be1d3a1dc8c6e6ee72567dd79294449cca654382b2e28

PROBES

Exact parent LOCAL_HEDGE behavioral parity:
PASS.

Observer returns parent behavior unchanged:
PASS.

Observer active:
PASS.

Observer sees only U-cell recruitment support calls:
PASS.

No-pool counterfactual is shadow-only:
PASS.

Phase labels diagnostic only:
PASS.

Five-manifest generator frozen:
PASS.

Runtime integrity:
PASS.

Duplicate mechanical byte identity:
PASS.

OBSERVATION BOUNDARY

The observer computes the exact inherited updated pc/ps
from the same pre-step state and demand fields.

It intercepts the exact inherited support-margin calls
used by U recruitment and returns their original values unchanged.

The no-pool calculation sets pc = ps = 0
only inside a diagnostic shadow calculation.

The shadow result is never supplied to:

cell state;
B;
timers;
Q;
global pools;
request state;
operation matching;
randomness;
or any parent transition.

SCIENTIFIC BLINDING

The mechanical gate does not report:

fresh-world TV_side distributions;

fresh-world R_rate distributions;

side-flip prevalence;

LU0B_DIRECTIONAL_POOL_PREVALENT;

LU0B_RATE_POOL_PREVALENT;

or

LU0B_POOL_PRACTICALLY_NEGLIGIBLE.

No LU-0B primary manifest has been derived.

No LU-0B primary trajectory has executed.

FREEZE AUTHORIZATION

Freeze this exact candidate as LU0BF1.

Only after LU0BF1 exists may exactly five fresh manifests
be derived from the preregistered LU-0B namespaces
and bound before any primary trajectory.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
