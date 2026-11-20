# DWSA-03 — sealed retrospective training-fixture result

**Outcome:** RETROSPECTIVE_SIGNAL_NO_GO (failed 4 of 4 pre-set criteria).
**Scientific:** UNVERIFIED / NOT SCIENTIFIC_PASS.
**Deployment:** NONE. No accepted checkpoint, owner, training continuation,
runner, scheduler, source actor, or main ref changed.

## Provenance

- Preregistered BEFORE scoring at commit 037557374badeefa76bb122ceaae1f369f2e095c.
- Donor: archived experimental Amalgam run 44499793023,
  artifact 14517860401, ZIP SHA-256
  b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d,
  state SHA-256 576370a1963158f7dc43099360f491eb6a1e49355448922943b6dbe374d484c8.
- Source mode: engineering_fixture_only; **1025 already-consumed episodes**,
  820 used for independent conventional-control fitting, final 205 are
  retrospective *late-training rechecks* (NOT unseen heldout for donor).
- Donor model forward calls: **0**. Protected original world actions: **0**.
  Existing native learner replay/restoration/training: **0**.
- Local environment: Linux Python 3.13.5, stdlib only; measured evaluator
  wall time 2.1235711519998404 seconds; peak RSS 111992 KiB.
  These timings are local diagnostics, not qualified end-to-end budgets.
- dwsa03.py Git blob SHA (matches tested bytes):
  919a44ce846214418048675f979102d9814b0f90.
- test_dwsa03.py Git blob SHA (matches tested bytes):
  3a703bc91f33255c76d54edda483f293f5bc3dde.
- Original full-precision local result JSON SHA-256:
  d57a02a585cad0530fd09f91049f0701e9f69de638bfec6c308915188df13964.
  This summary reports rounded results; the raw 2,921,047-byte checkpoint
  and private witnessed episodes were not committed.
- Local **7/7** tests PASS. Python 3.12 and Windows qualification remain
  UNVERIFIED. G29 dual-OS CI currently FAIL before source tests.

## Brier scores, late episodes already seen by source training (lower better)

| Task | Compiled DWSA 320B | 0.5 baseline | Laplace constant | Untrained init | 320B direct-fit logistic |
| --- | ---: | ---: | ---: | ---: | ---: |
| Action transition | 0.482272 | 0.250000 | 0.249767 | 0.248340 | **0.241075** |
| Action reward | 0.538623 | 0.250000 | 0.245293 | 0.248947 | **0.220541** |
| Temporal transition | 0.409609 | 0.250000 | 0.249767 | 0.250150 | **0.242331** |
| Temporal reward | 0.470858 | 0.250000 | 0.245293 | 0.249239 | **0.220153** |
| **Mean** | **0.475341** | **0.250000** | **0.247530** | **0.249169** | **0.231025** |

Exact unquantized weight-algebra version: macro Brier **0.475328**.
Readout-shuffled sham: macro Brier **0.366532**.
Near-equal performance of exact vs quantized projection shows ordinary int8
rounding is NOT the main bottleneck. The trained affine projection was
worse than the untrained structural initializer on all four tasks.

The frozen criterion required DWSA to beat both 0.5 and prior-prevalence
by 0.0100 absolute on ALL FOUR heads; **0/4 passed**.
No post-result threshold changes, extra data, or model retuning occurred.

## Interpretation and future research

This rejects collapsing nonlinear trained heads into affine weight products
as a useful archived-fixture outcome predictor. It does NOT reject all
weight-only assimilation, or prove the original nonlinear donor performs
badly: donor inference was never executed.

Do not propose this candidate for native Amalgam integration. A future
independent preregistration may test *nonlinearity-preserving structure*
under a fixed footprint (piecewise tanh motifs / threshold motifs), with
a fair matched capacity and pre-specified controls. The present retrospective
data do not authorize native promotion, original-world first-use, or science
acceptance. The sole Amalgam coordinator retains all learner authority.
