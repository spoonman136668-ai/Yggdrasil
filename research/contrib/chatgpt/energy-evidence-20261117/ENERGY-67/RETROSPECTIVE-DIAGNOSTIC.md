# ENERGY-67 — retrospective failure localization (nonconfirmatory)

**Date:** 2026-11-19. **Classification:** retrospective development diagnostic; **no new scientific result**, no source rerun, no native Yggdrasil training or qualification.

## Exact custody boundary
- Source archive PR: [#1210](https://github.com/spoonman136668-ai/Yggdrasil/pull/1210); parent reviewed commit: `777050cb8f61679413d3e1463301a073c4347cbc`.
- Original prospectively frozen scorer commit: `eb3d2a33783bbe4af0fc7c2e841d902488c7ccaf`; original preregistration commit: `afa1b94d039619fd8ef60de9a7c037846c47e0b4`.
- Inputs: original `ENERGY-67/case_receipts.csv`, Git blob `0d13d46be4fe38523758238f58e82703c08e7735`, SHA-256 `ecc9a482dabfbd365c12776099093318b1a2f70ba98f7563bde74616c4e2f024`; and original `result.json`. **Inputs were not modified.**
- Method: read-only 24-row CSV aggregation, comparing `adaptive_cold_mse - cv_cold_mse` with absolute floating-point tie tolerance `1e-9`. This recomputes a descriptive difference from preserved case-level scores; it does **not** independently reconstruct fitted predictions, replace the preserved independent 101,547-check audit, or consume any new seeds.

## Derived case-level pattern
| COLD held comparison to same-path CV selection | Cases |
|---|---:|
| Adaptive worse (difference >1e-9) | 7 |
| Adaptive better (difference <-1e-9) | 2 |
| Exactly tied within 1e-9 | 15 |
| Total | 24 |

| Mechanism family | Worse | Better | Tied | Mean adaptive-minus-CV cold MSE |
|---|---:|---:|---:|---:|
| `two_quad` | 0 | 0 | 8 | 0.000000 |
| `four_quad` | 3 | 0 | 5 | 1.497775 |
| `four_quad_plus_fifth` | 4 | 2 | 2 | 1.514229 |

The seven worst positive deltas (all >3.2 MSE) occur at:
- seed `109711`, family `four_quad_plus_fifth`, world `1`: candidate 0 added vs CV 4; cold MSE +4.993000.
- seed `109727`, family `four_quad`, world `3`: candidate 0 added vs CV 5; cold MSE +4.722166.
- seed `109711`, family `four_quad_plus_fifth`, world `2`: candidate 1 added vs CV 4; cold MSE +4.076533.
- seed `109711`, family `four_quad`, world `2`: candidate 1 added vs CV 4; cold MSE +3.651004.
- seed `109711`, family `four_quad`, world `3`: candidate 0 added vs CV 4; cold MSE +3.609032.
- seed `109711`, family `four_quad_plus_fifth`, world `3`: candidate 0 added vs CV 4; cold MSE +3.539605.
- seed `109727`, family `four_quad_plus_fifth`, world `1`: candidate 1 added vs CV 5; cold MSE +3.209899.

Pooled retrospective difference: **+1.004002 MSE** for adaptive (1.9894968833) versus CV (0.9854952709). On all eight `two_quad` worlds their predictions/scores tie. The discontinuous early-stop rule causes especially severe losses when the true family has four candidate terms; the two losses in the opposite direction on unrepresentable-fifth contexts do not compensate. This is a descriptive *failure localization*, not a causal ablation proving which implementation step is solely responsible.

## Scientific decision and scope
- Preserve the frozen `SCREEN_NO_GO` of ENERGY-67 (**3/9 gates**, four critical failures); do **not** relabel or tune any tested seeds. The reserved primary seeds `109801, 109819, 109837` remain **unconsumed**.
- A retuned 3% cutoff or stopping after the earliest unfavorable factor would be outcome-directed and cannot count as confirmatory evidence on these cases.
- A defensible *new* successor must first state a **different structural hypothesis**, disjoint seeds/worlds, no hidden access to planted supports, complete held-set custody, and its own prior-to-scoring frozen protocol. Match full-path conventional capacity selection, fully trained conventional baselines, exact/symbolic controls, data/actions and measured whole-process compute. Require seedwise and familywise non-degradation, equal-or-better accuracy, and a separately specified end-to-end advantage; include a no-mechanism negative.
- **No new experiment was dispatched by this retrospective.** No source code, trained checkpoint, accepted ref, controller, external first-use, merger or deployment is changed. Original G29 atlas Linux/Windows failure remains an independent engineering issue.

**Disposition:** retain as an archival, nonpromotable diagnostic alongside the original negative evidence.