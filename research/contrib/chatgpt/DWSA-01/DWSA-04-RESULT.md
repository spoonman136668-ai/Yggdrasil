# DWSA-04 — frozen nonlinear-structure assimilation: DEV NO-GO

**Decision:** DWSA04_DEV_NO_GO (0/4 preregistered tasks meet threshold).
**ENGINEERING:** Local Linux Python 3.13.5 focused source/codec checks: 8/8 PASS using compatibility shims for DWSA-02/03; full exact-repository dependencies, Python 3.12, Windows and G29 source-anchored regression **UNVERIFIED**. Historical G29 atlas failure remains unresolved here.
**SCIENCE:** UNVERIFIED; retrospective already-trained-on engineering fixture. No independent held-out, transfer, causal-effect learning, retention or gains over fully trained conventional controls.
**DEPLOYMENT:** NONE. No accepted-main, checkpoint, model owner, training lineage, controller, scheduler, source first-use or integration edits.

## Frozen source and protocol
- Parent negative: DWSA-03 (do not erase or reclassify).
- Preregistration: research/contrib/chatgpt/DWSA-01/DWSA-04-PROTOCOL.md at commit c4d1fa2fad30a80cfae6bbafc6de60a2741146f6, before first DWSA-04 scoring.
- Accepted Yggdrasil main at start: 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9.
- Archived Amalgam original training fixture: run 44499793023, artifact 14517860401.
- Original ZIP SHA-256: b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d (verified).
- amalgam-joint-state.json SHA-256: 576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8 (verified).
- Source: engineering_fixture_only, 1,025 *already-consumed* historical records, conventional fit prefix 820, late-training rechecks 205. These are **not** unseen for the trained donor.
- No donor forward inference, no source actor replay, no private owner invocation, no protected first use and no teacher output labels.
- Fixed 320-byte checksum-protected recipient; 32 tanh units across four heads; no fitted recipient updates on the 205 scored rechecks.

## Result: Brier score, lower is better

| Task | Nonlinear 320B | Affine 320B | Fitted logistic 320B | Untrained 320B |
|---|---:|---:|---:|---:|
| Action transition | 0.372424 | 0.482272 | 0.241075 | 0.248340 |
| Action reward | 0.448125 | 0.538623 | 0.220541 | 0.248947 |
| Temporal transition | 0.373977 | 0.409609 | 0.242331 | 0.250150 |
| Temporal reward | 0.412677 | 0.470858 | 0.220153 | 0.249239 |
| **Macro mean** | **0.401801** | **0.475341** | **0.231025** | **0.249169** |

Additional controls: half-constant Brier 0.250000; prefix-Laplace prevalence mean Brier 0.247530.

Preregistered success required the nonlinear 320B model to beat BOTH the affine and directly fitted logistic controls by at least 0.0100 absolute on **every** task. **0/4 passed**. The nonlinear candidate improves the earlier collapsed affine model on all four tasks, but loses badly to all relevant simple predictive controls. No threshold adjustment, new data or post-result tuning.

## Local receipt
- Original source and test code committed to this same contributor branch under DWSA-01/dwsa04.py and test_dwsa04.py.
- dwsa04.py Git blob SHA: 661ae3f1e409d91975deab42bd224e1eb02e26e3 (matches local exact bytes); file SHA-256 3474831f0e2d89f01e935021812771205aeedabd53bf2569ef7affcb20eeeac2.
- test_dwsa04.py Git blob SHA: 326b772064bf77a0022b2dab3ac4d97a3b150909 (matches local exact bytes); file SHA-256 94a892cb4d858a9783b7ed53c502be9129917aa55c25b3e9ab726c2bc6de36ae.
- Evaluated 320B checkpoint SHA-256 ba28b61b08026fc14bf41dff288f0a7a0e50c31be24b9c9f9585db0607a29430.
- Local full-precision result JSON SHA-256 0706c274481ed9076583f62d18b5bd86bb7787532cdcac4b5a48f7ac33b409a4 (not independently CI reproduced). Local scoring wall time 1.662 s; not a qualified whole-process performance claim.
- **8/8** local focused tests PASS with local helper *compatibility shims*, not independently downloaded exact upstream dwsa02.py and dwsa03.py. Their frozen baseline macro values reproduce DWSA-03's archived report; full exact-dependency repeat and G29 remain necessary.
- 3/3 cold restores, deterministic duplicate, 12 valid signed/permutation-gauge cases (maximum recipient probability difference zero on test features), checksum failure rejection and unsupported 4-bit P-code rejection PASS.

## Mechanistic conclusion / continuation
The DWSA-03 failure was partly due to losing tanh nonlinearity, but restoring a 320B quantized tanh recipient remains noncompetitive even on familiar source-training episodes. **Do not promote.** For this archived trained head, terminate additional tuning of the same 320B fixed-footprint recipe. Any successor must introduce a genuinely distinct, preregistered mechanism and independently licensed, source-grounded novel tasks with fully trained, same-budget and symbolic controls before any intelligence/transfer claim.

For exact repository qualification, run source/test at the unchanged new PR HEAD on original Linux/Windows and resolve atlas fail-closed with an authorized regenerating owner; the stalled old G29 gate must not be presented as a scientific negative. Original-model integration stays exclusively with the Unified Causal Intelligence Amalgam Work coordinator.
