TITLE: YGG-C1 R3 Host-Memory Instrumentation Diagnosis
DATE: 2026-09-24
STATUS: INSTRUMENTATION DEFECT
LANE: YGG-C
PREREGISTRATION: fa1b88d0e6e4b9605d113a719742f75b01f2ceb1
RUN: 36073389399
HEAD: eae3e0edbd7e03fbb38c92b43595ec2c1452b9dd
ARTIFACT_ID: 10839008389
ARTIFACT_SHA256: 87e2999d2242961f7d8f73349d86982413d4d03f9101a826df5e1900214ee106

VALID EVIDENCE
Two scored timing passes completed at 1,2,4,8,10 worlds.
Evidence hashes matched across both passes for every scale.
Runner GPU inventory: NVIDIA GeForce RTX 5070 Ti Laptop GPU, 12227 MiB, driver 596.13.
Benchmark runtime: Python 3.12.10, torch 2.10.0+cpu.
CUDA execution unavailable in this frozen runtime, therefore accelerator allocation/reservation is legitimately unavailable.

DEFECT
peak_rss_bytes is null for every scored row even though Windows working-set information is observable on this host.

ROOT CAUSE
The ctypes Windows memory probe did not declare the native GetCurrentProcess/GetProcessMemoryInfo signatures. The call returned false and the script silently converted that to null.

AUTHORIZED REPAIR
Declare the native function argtypes/restype and retain the same PROCESS_MEMORY_COUNTERS structure and PeakWorkingSetSize measurement.
Rerun the identical preregistered warm-up and two scored 1,2,4,8,10-world passes.

FORBIDDEN
No change to LU-2V semantics, manifests, seeds, task, authority, alpha, qualification, scale points, warm-up count, or scored-pass count.

CLASSIFICATION
R3 provides valid timing evidence but is incomplete as the full C1 cost audit until host-memory observation is repaired.
