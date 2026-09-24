TITLE: YGG-C — Efficiency and Scaling
DATE: 2026-09-24
STATUS: ACTIVE LANE / BOOTSTRAP ONLY / NO LANE SCIENCE CONSUMED

SHARED ACCEPTED BASELINE:
878464cf84833d06a1ac7e45988bfb79608547dc

SHARED BASELINE RESULT:
LU-2V independently confirmed frozen 25-percent learned U-recruitment transfer on four-stage Task-4.

PURPOSE

Measure whether the developmental architecture can remain practical on consumer hardware: active-cell sparsity, state dimension, memory retention cost, long-context scaling, CPU/GPU behavior, and readout cost.

IMMEDIATE FRONTIER

First scientific frontier after bootstrap: observation-only profiling of accepted frozen workloads and hardware capability; no scientific dynamics change until a scaling bottleneck is demonstrated.

GOVERNANCE

- This branch is isolated from the other Yggdrasil research lanes.
- Do not mutate another lane branch.
- Do not merge scientific changes into dg1a-ar automatically.
- Cross-lane promotion requires an explicit evidence review and a new shared-baseline decision.
- Preregister before primary science.
- Freeze implementation before deriving primary worlds.
- Bind primary manifests before execution.
- Duplicate deterministic evidence before interpretation.
- Negative results are valid scientific closures.
- Do not tune frozen thresholds or parameters after observing primary results.
- No result-dependent world replacement or rejection sampling.
- Infrastructure defects are not scientific results.

AUTHORITY BOUNDARY

- alpha remains 0.25 unless a future explicit governance decision changes it;
- H/C/S/FC/FS remain protected as in the accepted baseline;
- no learned C/S authority;
- no online adaptation;
- no recursive self-modification;
- no deployment or production authority;
- no broker or credential access;
- no KTRADE;
- no CKB or ckb-plane;
- no Wingless integration;
- no Windows production-runner reuse.

RUNNER ROUTING

required labels:
self-hosted
Windows
X64
yggdrasil
ygg-c
research-only

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
