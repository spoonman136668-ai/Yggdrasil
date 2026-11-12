# WSP52 engineering boundary and negative controls

Parent: WSP47 at 9e6374119602ea57e479a1b36a35a5c0e932b4e1.
Original preregistration: 8cea083b5c230663b9a9dccfc8089a77f1c4c729, unchanged.
Draft research PR: #943. This is not an owner-admitted experiment.

## Implemented

- source.py: source-only deterministic 15-word prefix-free, undelimited acoustic evidence; 36 training experiences in A, 6 in B, 60/90 heldout per phase. Charged actions and source digests.
- controls.py: exact (before, entire bit-stream) evidence-table control; explicit contradiction => abstention, cold snapshot validation and tamper rejection. Erased control returns unknown.
- fixture_harness.py: passes only a learner-facing Observation to observe(), and only (before, raw acoustic bits) to predict(). Heldout targets stay with the evaluator. SELFTEST-only guard rejects registered cohorts.
- test_source.py and test_controls.py: fixture-only source/leakage, mutation, non-compositional and negative-control checks.
- Existing PR workflow runs the tests and full inherited WSP47 regression on both Linux/Windows. G29 atlas must match exact candidate SHA and pass both platforms.

## Important scientific limits

The supplied physical simulator computes new location as (destination+verb) mod 4; independent lexical identities of destination and verb are **not identifiable** from action consequences alone. A perfect predictor of those consequences does not prove the two concepts were separately learned. Pre-DEV protocol clarification or additional independently grounded evidence is needed before claiming those semantics.

The learner/evaluator seam is a data-interface discipline, **not a process or security isolation boundary**. Deliberately malicious in-process candidate code could read evaluator internals. Separate worker process isolation and capability-limited delivery are required before admitting an untrusted learner.

The exact-stream baseline is intentionally weak for unseen acoustic compositions. It is not a substitute for the independently trained neural and exhaustive symbolic comparators required by the preregistration. All primary metrics, whole-process timing/cost, and capacity matching remain **UNVERIFIED** until those arms exist.

No registered DEV or PRIMARY data has been sampled by these fixtures. There is no neural warmup, direct weight writer, trained baseline, scientific first-use, owner acceptance, or integration result from this gate.

## Commands

From WSP-52 directory (Python 3.12 or newer):
- python -m unittest -v test_source.py test_controls.py

## Status

Source and negative-control engineering implementation committed on isolated PR #943; exact-candidate final CI is required. No merge or accepted-ref mutation. Do not report SCIENTIFIC_PASS from fixture tests.
