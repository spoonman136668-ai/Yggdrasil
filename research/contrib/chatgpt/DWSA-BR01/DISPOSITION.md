# DWSA-BR01 disposition — same-law correction signal, no competitive gain

**2026-11-21. STATUS: DEV SCREEN PASS; SCIENTIFIC NO-GO / NOT VERIFIED; DEPLOYMENT NONE.**

## Original immutable evidence
- Preregistered commit before scoring: `510f06ede757e33900fadc63735842c2e75fd87b`.
- Implementation commit: `53e1791c0a67bc28b7bacd8c95dd5ced0a0fa164`; evaluated result commit: `a5b06d014be492b9d394c95a399e4c6f3421fdce`.
- Readback confirmed exact branch head `a5b06d014be492b9d394c95a399e4c6f3421fdce` and three changed files against accepted main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Pinned source Git blobs match `16ea8cf939bfa0f5f21e227d159b11d4ff578eca` (stored donor weights) and `6f95eea88422ceb01b3118e65cd45b9a4c065bd9` (same-family generator). No source model forward, original environment stepping, or donor runtime.
- Score was computed once inside an isolated V8 development evaluator using original weight and generator text returned by the source connector; code and result were then committed. The committed `run.mjs` CLI has **not** been independently executed from a local checkout on pinned donor bytes. Linux/Windows exact-head full regression and G29 atlas are UNVERIFIED.

## Frozen numeric outcome

| Arm | 7% flips, 2,000 | 12% flips, 2,000 |
| --- | ---: | ---: |
| DWA original | 1,603 / 80.15% | 1,424 / 71.20% |
| DWA + 11 accepted bounded edits | 1,860 / 93.00% | 1,666 / 83.30% |
| Fully fitted same-capacity, same-200-label control | 1,978 / 98.90% | 1,931 / 96.55% |
| Zero-initialized + identical bounded procedure | 664 / 33.20% | 582 / 29.10% |

200 class-balanced calibration labels; 74 proposed donor-bit changes; 11 accepted; 63 rejected. In-family improvement **+12.85 pp**; shifted corruption **+12.10 pp**, so frozen narrow development screening PASS. However, the conventional matched fitted control is still ahead by **5.90 pp** and **13.25 pp**, respectively.

**Checkpoint-test qualification correction:** Result field `restores=3` records three deterministic packed-bit serialization/deserialization roundtrips **within the same V8 process**, plus one malformed-padding rejection. It is NOT a fresh-process cold restart, cryptographically authenticated checkpoint, original native-model restore, cross-platform regression, or proof of lifelong retention. The stronger original retention gate has not been exercised.

## Prior stronger evidence and stop rule
Existing, independent, original-data **DWSA-64** already tested authentic pretrained LunarLander feature transplantation plus bounded residual correction under frozen seed-disjoint source splits. [Protocol](https://github.com/spoonman136668-ai/Yggdrasil/pull/1347#issuecomment-7068997228), [result](https://github.com/spoonman136668-ai/Yggdrasil/pull/1347#issuecomment-7069020649). Donor B-held Brier improved 0.020432 -> 0.013293, but raw-input frozen/control Brier ~0.005585 beat it. That preregistered experiment closed DEV_NO_GO. Neither this synthetic digit screen nor DWSA-64 demonstrates true native Yggdrasil cumulative retention or causal transfer.

**Disposition:** preserve this branch and negative/positive evidence; DO NOT merge or move accepted state, retrain same template cohort, dispatch CI/runner, or revive donor-derived feature transplant on this evidence alone. Next meaningful untested mechanism would retain native raw identity features alongside donor-derived features with bounded correction *only after a disjoint original-world source/fresh-cohort protocol, owner-authorized first use, and full fitted/matched baseline are available.* No protected first use is authorized here.
