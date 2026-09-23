TITLE: TASK-1G T1GF1 PUBLICATION-FORM AMENDMENT
DATE: 2026-09-23
STATUS: BOUND BEFORE T1GF1 AND BEFORE ANY TASK-1G PRIMARY MANIFEST
TRACK: DG-1 / TASK-1G

MECHANICAL-GATE COMMIT:
6c98e16f72c695ef08668ad86cf56281e424fba1

TESTED SOURCE IDENTITY

bytes:
15987

SHA256:
dc46ac0cc462f5f3ff93c56c28db4ed7da92ce67654d1633b4d3014e9ae01197

AMENDMENT

The pre-T1GF1 mechanical-gate record proposed deterministic
gzip/base64 chunk publication.

Before T1GF1 and before any primary manifest is derived,
the publication container is changed to direct plaintext source
plus a fail-closed loader.

Reason:

the exact tested plaintext candidate already exists in the repository;

direct source publication removes unnecessary encoded-chunk transport
and avoids repeating prior source-part corruption risk.

This changes only publication transport.

It does not change:

source bytes;

source SHA256;

Task-1G scheduling;

LOCAL_HEDGE;

repair-critical definition;

expiry;

repair computation;

verification computation;

mandatory post-repair verification;

randomness;

manifest derivation;

qualification;

or any scientific threshold.

The final loader must verify:

source byte count = 15987;

source SHA256 =
dc46ac0cc462f5f3ff93c56c28db4ed7da92ce67654d1633b4d3014e9ae01197

before execution.

No Task-1G primary manifest has been derived.
No Task-1G scientific arm has executed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
