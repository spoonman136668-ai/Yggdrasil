TITLE: TASK-1B MECHANICAL EVIDENCE CORRECTION — MODULE NAMESPACE
DATE: 2026-09-22
STATUS: CORRECTED / T1BF1 SOURCE REMAINS MECHANICALLY QUALIFIED
TRACK: DG-1 / TASK-1B

PURPOSE

Correct the pre-T1BF1 mechanical evidence identity after discovering
a sandbox-only module-emulation defect.

WHAT HAPPENED

The first local Task-1B mechanical execution created a ModuleType
and copied already-defined parent functions into it.

Those function objects retained their original Python __globals__ mapping.

Task-1B correctly monkeypatched attributes on the synthetic module object,
but the copied parent run_arm function still resolved cell eligibility
through the old globals dictionary.

Therefore the first local mechanical output identity did not faithfully
exercise the in-repository import/monkeypatch semantics.

This was a local harness-emulation defect.

It was not a Task-1B source defect.

No Task-1B scientific result is accepted from that emulation.

CORRECTION

The exact frozen T1F1 parent source was re-executed directly inside
a real ModuleType namespace.

The exact mechanically tested Task-1B source was then imported against
that real module namespace.

Under this faithful module binding, the full mechanical gate was rerun.

SOURCE IDENTITY

Task-1B source bytes:
12748

Task-1B source SHA256:
e8d409c5eb8e750123aae4979fd1091611a915c22f7cf977e420345186aef6b9

This is unchanged from T1BF1.

FAITHFUL MECHANICAL GATE

duplicate_byte_identical:
PASS

matched_parent_parity:
PASS

fixed_parent_parity:
PASS

neutral_opposite_stream_sense_fixture:
PASS

downstream_still_stream_matched_fixture:
PASS

noncommitted_cannot_sense_fixture:
PASS

all_runtime_integrity:
PASS

Correct compact mechanical output bytes:
36818

Correct compact mechanical output SHA256:
bc1ea1e149638ee2a046eb57bbec28bda6b192073cb29d48bee4e167936aac21

Two faithful mechanical sweeps:
byte-identical.

T1BF1 STATUS

T1BF1 remains valid.

The source itself passes every preregistered mechanical gate
under the faithful module semantics.

The correction changes only the recorded local mechanical output identity.

PRIMARY MANIFEST STATUS

The already-bound T1BF1 primary manifest re-derives exactly under
the faithful module namespace.

Manifest SHA256 remains:

0a88b7f42c283c09c74925744157e9cd5279afd4a6c02e1b9a866da5016b9d71

No manifest field changes.

INVALID LOCAL PRIMARY NOTE

Any Task-1B primary output produced through the defective copied-function
module emulation is non-authoritative and must not be interpreted.

The authoritative primary must be rerun using faithful module semantics
and must satisfy the duplicate-byte gate before opening.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
