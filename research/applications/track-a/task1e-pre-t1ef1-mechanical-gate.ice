TITLE: TASK-1E PRE-T1EF1 MECHANICAL GATE
DATE: 2026-09-22
STATUS: PASS / T1EF1 FREEZE AUTHORIZED
TRACK: DG-1 / TASK-1E

PREREGISTRATION:
5b77a388267479f7bdb2bb005df1ea7c245b436e

PARENT T1BF1:
83af31c2a95adeba47700f7c34d159d7739549c9

FLOW-HANDOFF DIAGNOSIS:
d3c42b834e684a7716c3c87f4c9b36d02c9c82c6

FINAL CANDIDATE SOURCE

bytes:
15476

SHA256:
c1578a0d21d1125a26d81664adc0c3a78a3a23e9a4a2a4865d526e41af7d2207

DETERMINISTIC PUBLICATION

gzip level:
9

gzip mtime:
0

gzip bytes:
4427

gzip SHA256:
21c1a751c98a7586ead0224ee7af11ee85265ec513fd1f90f631c6558f8f39f3

concatenated base64 characters:
5904

base64 SHA256:
b141106f4c74c8b61d935de3dfff42f6d86ba9bbb6f16ce7fc64ae0ae193de31

source chunks:
3

chunk sizes:
2048;
2048;
1808.

MECHANICAL SEED

TASK1E-MECHANICAL-V1

COMPLETE MECHANICAL SWEEPS

2.

canonical output bytes per sweep:
40124.

canonical output SHA256:
d666ee4537b086d7fc7f7160b901feed6aedcf83c1a608b65be9ff070811ccda.

BYTE IDENTICAL:
true.

MECHANICAL PROBES

duplicate_byte_identical:
PASS.

dynamic_parent_parity:
PASS.

pre128_trace_parity:
PASS.

pre128_operation_parity:
PASS.

legacy_bound_old_anchor:
PASS.

phase4_bound_new_anchor:
PASS.

anchor_generations_differ:
PASS.

runtime_integrity:
PASS.

INTERPRETATION

The new treatment changes only request anchor-generation semantics.

The inherited DYNAMIC_REBIND arm is behaviorally identical
to frozen T1BF1 NEUTRAL_SENSE.

REQUEST_BOUND and DYNAMIC_REBIND are exactly identical
through epoch 127.

No pre-rotation divergence exists.

Requests created before the anchor shift
remain bound to the old anchor generation.

Requests created at or after epoch 128
use the new anchor generation.

No request teleportation is introduced.

No route direction changes.

No V0 dynamics change.

No scheduler change.

No G5 activation.

No post-result parameter exists.

MECHANICAL OUTCOME BOUNDARY

Mechanical-world completion or relocation magnitudes
are not scientific evidence.

They may not be used to retune:

handoff semantics;

phase length;

expiry;

anchor displacement;

scheduler;

V0;

or Task-1E thresholds.

FREEZE AUTHORIZATION

T1EF1 may freeze
the exact candidate source identity above.

No Task-1E primary seed,
program set,
arrival schedule,
corruption schedule,
lesion offset,
anchor geometry,
or scientific result
has yet been derived or observed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
