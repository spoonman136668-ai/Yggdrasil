# Y-SYN01 — synthetic-only retained-majority falsification

**Not Y095 external science, not external validation, not READY_RESEARCH, no primary result yet.**

Mechanism foundation: Yggdrasil PR #17 at exact head `f0bd57e7ae5f592b2e387a9d3fc1dcba828fb0c7`.
Preregistration frozen alone in commit `3ca661a94b6226e24cf3b36e77e9c4f1104266dc`, **before implementation and outcomes**.
Implementation commit `ac34200a4707b7c4caf89872f6fc6786fbf197c7`; mechanical-only test `922b44f775928a4b86ee721a701b7236d2bf7dcc`.

## Scientific question
Can a fixed strict-majority/coherence retained-memory gate fail on internally consistent but false memories? The frozen synthetic regimes deliberately contrast reliable coherent retained state, coherent high-confidence wrong retained state, and incoherent retained state. Compare A0/A1/A2, preserve negative or mixed outcomes, and report synthetic-only scope.

The design freezes four seeds, 256 cases/seed/regime, 3 regimes, zero learner parameters/model calls and exact 16 total / 7 active / 9 retained capacity. No external cohort is consumed or reclassified.

## Execution separation
Mechanical qualification **without primary evaluation**:

`python -m unittest discover -s research/contrib/ckb-synthetic/y-syn01 -p test_synthetic_pilot.py -v`

Primary execution is guarded behind `CKB_SYN_Y01_QUALIFIED_RUN=yes`. This environment marker is **not** proof of authority. Existing CKB scientific authority must independently pin the frozen preregistration, exact source/harness identity, approve the separately synthetic-only protocol, issue an authorized run receipt, and invoke the primary with isolated research compute. Do not turn on the guard in normal PR CI or via a repo-local scheduler. The output retains `official_ckb_acceptance=false` until independent classification.

Y094 negative and Y095 origin/source disjointness requirements remain untouched. Synthetic cohorts must never be treated as external Y095 proof. No KTRADE, accepted-ref mutation, live broker, production, runner, queue, or autonomous controller changes.
