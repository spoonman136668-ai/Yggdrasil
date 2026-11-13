# DG1-SL01 — Wake–sleep causal-memory experiment (local development)

Preregistered before implementation at commit `1714e2b8d46f8a34391e16f61ad3d7430817075b`. Research remains isolated from main, the native Yggdrasil substrate, the owner/autonomous loop, and the parallel weight-editing line.

## First synthetic development result

Eight worlds, 32 physical observations each (16 in A, 16 in B). Audit of A over 512 state/action queries:

| Arm | Correct | Confidently wrong | Correct on unseen |
|---|---:|---:|---:|
| Episodic recall | 128 | 0 | 0 |
| Online causal-rule inference | 207 | 0 | 79 |
| Offline sleep compression | 207 | 0 | 79 |
| Conventional batch inference | 207 | 0 | 79 |
| Dream ablation | 207 | 0 | 79 |

Four focused local unit tests passed. The preregistered advantage over episodic recall passed, **but the sleep-specific mechanism is negative**: online and conventional models tie exactly. Dreaming provided no gain. The benchmark provides a stored-A audit, not label-blind context retrieval. This is **NOT** general intelligence evidence, not a scientific pass, and not dual-OS qualification.

Executable implementation, tests, preregistration and full per-world output were supplied as `Yggdrasil-DG1-SL01-wake-sleep-dev.zip` in the originating conversation; they have **not** been pushed as source to this branch. No CI or native integration is claimed.

## Subsequent experiment

SL02 must establish an actual offline-only mechanism with precommitted label-blind A→B→A retrieval, matched memory and conventional controls. The next scientific question is whether sleep gives a measured gain over **online learning**, not merely over raw episodic lookup.
