TITLE: YGG-C2 Independent World Parallel Throughput Preregistration
DATE: 2026-09-24
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: 85a4e7fd05bbf363079af1dec860ed1c65868416
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Can independent accepted LU-2V worlds obtain useful process-level throughput scaling on the dedicated consumer Windows host without changing scientific evidence?

SCIENTIFIC STATE
No scientific mechanism changes.
This is an execution-efficiency experiment only.

FROZEN WORKLOAD
Use the same accepted LU-2V source and the same ten deterministic primary manifests used by YGG-C1.
Each world is executed independently with lu2v.run_pair.
Result order is restored to manifest order before evidence hashing.

PROCESS COUNTS
1,2,4,8 worker processes.

THREAD DISCIPLINE
Inside each worker set torch_num_threads=1 to avoid nested CPU oversubscription.
Do not change LU-2V task semantics, manifests, seeds, authority, alpha, or qualification logic.

WARMUP
For each process count:
- create the process pool;
- execute one unscored mechanical-world job per worker;
- keep the warmed pool alive for scored passes.

SCORED PASSES
Two scored passes per process count.
Each scored pass executes all ten primary worlds.
Measure:
- wall seconds
- worlds per second
- ordered scientific evidence SHA256

INTEGRITY
All eight scored evidence SHA256 values must be identical.
Each returned world must retain zero matching-duplicate violations and preserve its deterministic result identity.

INTERPRETATION
Report measured speedup relative to the C2 one-worker scored median.
Do not require a minimum speedup for scientific PASS; poor or negative scaling is a valid engineering result.
A run is invalid only if evidence identity changes, a worker fails, or the frozen workload is not completed.

BOUNDARY
No shared-baseline promotion.
No GPU port in C2.
No change to accepted LU-2V code.
No modification of CKB, KTRADE, Wingless, or CKB-plane runtime.
