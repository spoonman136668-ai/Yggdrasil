TITLE: YGG-C2 Independent World Parallel Throughput Closure
DATE: 2026-09-25
STATUS: CLOSED / VALID ENGINEERING POSITIVE
LANE: YGG-C
PREREGISTRATION: 44a6f5ff63c6ef93eef53f6193d51adbb03432ed
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc
LU2VF1: e832853554e813db2e185d6b607543541f32d887
EXECUTION_HEAD: 321d28ac6eb63ea3135704ceda092d5fb3cf441d
WORKFLOW_RUN_ID: 36107163141
ARTIFACT_ID: 10851154599
ARTIFACT_ZIP_SHA256: 563f5890e4363a1c44235ce0a5800c2ff310b62cc66b50afad85ddc4efa1c85b

VALIDITY
all_evidence_identical=true
all_integrity_pass=true
valid=true
worker_counts=1,2,4,8
torch_num_threads_per_worker=1
ordered_scientific_evidence_sha256=a0b3d090f05491dbb6894c01705180053703cf0abe880abfe78b0f16e76767f9
reference_one_worker_seconds=25.782054249953944

MEASURED PASSES
workers 1:
- 28.00488659995608 s, 0.3570805389376468 worlds/s, speedup 0.9206269826493201
- 23.559221899951808 s, 0.4244622357421938 worlds/s, speedup 1.0943508388961982

workers 2:
- 13.4289592000423 s, 0.7446593478345293 worlds/s, speedup 1.9198847703605155
- 13.395926700090058 s, 0.746495574653508 worlds/s, speedup 1.9246189403067289

workers 4:
- 8.114333500037901 s, 1.232387108559599 worlds/s, speedup 3.1773471289827464
- 8.073746900074184 s, 1.2385822993668674 worlds/s, speedup 3.1933196035309273

workers 8:
- 5.652884699986316 s, 1.7690083082756325 worlds/s, speedup 4.560866817258161
- 5.838352399994619 s, 1.712811991275007 worlds/s, speedup 4.4159811679023875

INTERPRETATION
C2 is a valid execution-efficiency result under the frozen preregistration.
Scientific evidence identity is unchanged across all eight scored passes.
On this Windows consumer host, process-level parallelism scales useful LU-2V throughput through eight workers, reaching about 4.4x to 4.6x the one-worker reference at eight workers.

MECHANICAL REPAIR NOTE
The first C2 attempt failed before producing a valid scored result because concurrent workers collided on a shared source-adjacent temporary canonical-weight path.
The repaired harness gives each spawned worker a byte-identical private Track-A tree for materialization while retaining the frozen LU-2V source, ten primary manifests, worker counts, one-thread discipline, unscored mechanical warmup, scored passes, evidence ordering, and integrity criteria.
No accepted LU-2V scientific code or task semantics were changed.

BOUNDARY
This is an engineering throughput result, not a new scientific mechanism.
No shared-baseline promotion.
No GPU claim.
No accepted LU-2V mutation.
No CKB/KTRADE/Wingless/CKB-plane runtime modification.
