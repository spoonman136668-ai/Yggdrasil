TITLE: TASK-1G PRE-T1GF1 MECHANICAL GATE
DATE: 2026-09-23
STATUS: PASS / T1GF1 FREEZE AUTHORIZED
TRACK: DG-1 / TASK-1G

PREREGISTRATION:
2b1988f0d891d1e24de28ad32b8a32a3d6c0e29a

PARENT TASK-1F T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063

PARENT TASK-1F CLOSURE:
fda86a2fee99fb948524b53b0eb0652011d655f6

TESTED CANDIDATE SOURCE

bytes:
15987

SHA256:
dc46ac0cc462f5f3ff93c56c28db4ed7da92ce67654d1633b4d3014e9ae01197

MECHANICAL SEED

TASK1G-MECHANICAL-V1

DUPLICATE MECHANICAL SWEEPS

complete sweeps:
2

serialized gate result bytes:
36640

serialized gate result SHA256:
3976eb343565f1f4d8960c842483e00b3f5262338ca9ff6734c01d8999d3132f

byte identical:
true

MECHANICAL PROBES

duplicate_byte_identical:
PASS

parent_exact_parity:
PASS

noncritical_empty_fixture_exact:
PASS

expiry_age_32:
PASS

critical_definition_narrow:
PASS

repair_math_parent:
PASS

verify_math_parent:
PASS

mandatory_reverify_parent:
PASS

local_hedge_parent:
PASS

no_new_rng:
PASS

runtime_integrity:
PASS

primary_manifest_json_roundtrip:
PASS

MECHANISM BOUNDARY

The treatment changes only local request proposal ordering.

Repair-critical work is exactly:

REPAIR_PENDING;

or

AT_EGRESS with repaired = true
and mandatory post-repair verification still pending.

No RAW, SENSED, PROCESSED, ROUTING,
or ordinary unrepaired AT_EGRESS request
receives deadline priority.

Expiry remains exactly 32 epochs.

Repair computation is unchanged.

Verification computation is unchanged.

Repair alone cannot mark a request DONE.

No new randomness exists.

No global scheduler input exists.

FREEZE PUBLICATION

The exact tested source will be published
as deterministic gzip level 9, mtime 0,
then base64 split into four chunks.

source bytes:
15987

source SHA256:
dc46ac0cc462f5f3ff93c56c28db4ed7da92ce67654d1633b4d3014e9ae01197

gzip bytes:
5006

gzip SHA256:
8df6b8feb73862cf643bd820416d91a7120356c2b002d94074bc69fbeead051e

base64 chars:
6676

base64 SHA256:
fa7a7a56431ba98b38aca1369d152c65237be381bfdf1e4910c68a7a76442d8e

chunk count:
4

No Task-1G primary manifest
has been derived.

No Task-1G scientific arm
has executed.

The earlier repository file:

task1g_local_deadline_repair_v1.candidate.py

was a staging form used before local exact-parent recovery.
It is NOT the frozen source identity.

Only the tested source identity recorded above
may be frozen as T1GF1.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
