TITLE: TASK-1F T1FF1 PRE-PRIMARY SERIALIZATION-VALIDATOR REPAIR
DATE: 2026-09-22
STATUS: PRE-PRIMARY DEFECT / ZERO SCIENTIFIC EXECUTION / R1 REFREEZE REQUIRED
TRACK: DG-1 / TASK-1F

T1FF1:
f21bdb00fbd585e36068940322f54f2e6a6af02e

FIVE-MANIFEST BINDING:
7476b025ae6d722316346ef0a7e713a8c5254fde

OBSERVED FAILURE

The first attempted five-replicate sweep
stopped during validate_manifest
on replicate 1

before run_replicate executed either arm.

No GLOBAL_HEDGE arm executed.

No LOCAL_HEDGE arm executed.

No scientific metric was produced or inspected.

CAUSE

The frozen manifest was serialized to JSON.

Request bit tuples produced in memory by:

make_arrivals(...)

therefore reloaded as JSON arrays / Python lists.

The Task-1F validator compared:

loaded arrivals

to

fresh in-memory arrivals

using raw Python object equality.

The values are identical,
but:

list != tuple

under Python object equality.

This is a serialization-representation defect,
not a manifest-content mismatch
and not a dynamics failure.

AUTHORIZED REPAIR

Change only the Task-1F exact-arrival validation
to compare canonical JSON representations.

Canonical JSON serializes both tuples and lists
as the same JSON array values.

No request value changes.

No ordering changes.

No seed changes.

No program changes.

No arrival changes.

No corruption changes.

No lesion changes.

No anchor changes.

No H semantics change.

No dynamics change.

No qualification change.

Add one mechanical acceptance probe:

a primary-format manifest
must survive JSON serialize -> parse -> validate
without changing its canonical content identity.

REFREEZE

Do not modify T1FF1 in place.

Freeze the repaired source as:

T1FF1-R1.

The existing five-manifest binding
is retired UNEXECUTED.

After T1FF1-R1 exists:

derive five fresh manifests
from T1FF1-R1;

bind all five before execution;

then attempt duplicate primary sweeps.

No result from the retired manifest set
may be interpreted scientifically.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
