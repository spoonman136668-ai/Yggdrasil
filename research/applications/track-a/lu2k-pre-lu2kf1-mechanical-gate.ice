TITLE: LU-2K PRE-LU2KF1 MECHANICAL GATE
DATE: 2026-09-24
STATUS: PASS / LU2KF1 FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
8f9d87545c2cd0e2ec33b59fd6cba9c0120c6bf0

CANDIDATE:
f5be2edb5c840f23f85baf5a2bcf572b9852e84e

CANDIDATE FILE:
research/applications/track-a/lu2k_fresh_l1_exact_parent_validation_v1.candidate.py

CANDIDATE SOURCE SHA256:
96c95b3e0730c5a29ec878d28d9e4e4e27ef601e931af800e7a9ba603c0d6bc8

MECHANICAL RUN:
36051498479

EXECUTION HEAD:
13f7b1a7806d063bf6f73be0d86a1b1380004b7f

DUPLICATE EVIDENCE

bytes each:
540

SHA256 both:
282619a29ac968f0672ec4995c96dcde7f9d93dd6390ede3ed6b27c9030f036f

byte-identical:
TRUE

all_pass:
TRUE

PROBES

exact LU2IF1 parent bound:
PASS

exact parent execution path available:
PASS

load-one schedule exact:
PASS

phase 0 C/S:
16 / 16

phase 1 C/S:
24 / 8

phase 2 C/S:
8 / 24

phase 3 C/S:
16 / 16

phase 4 C/S:
16 / 16

Task-2 two PROCESS stages:
PASS

Task-2 repair / mandatory reverify:
PASS

immutable repair provenance:
PASS

inherited expiry 32:
PASS

horizon 160:
PASS

D2:
PASS

G5_FULL OFF:
PASS

fresh namespace requires LU2KF1:
PASS

no learned arm defined:
PASS

no manifest derived during mechanical gate:
PASS

DECISION

Freeze the exact candidate source as LU2KF1.

Only after LU2KF1 exists may the ten fresh LU-2K manifests be derived.

No scientific world has been derived or executed by this gate.

PLAIN-SPEAK INTERPRETATION

The one-job Task-2 validation harness is wired correctly.

It keeps the exact hand-written parent, the same two-stage task, the same
repair path, the same 32-epoch lifetime, and the same five-phase schedule.

The mechanical test did not secretly create any of the ten validation worlds.

We can now freeze the implementation and only then create those worlds.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
