# MR32-A qualification receipt — source-only prototype

Date: 2026-10-31
PR: [#716](https://github.com/spoonman136668-ai/Yggdrasil/pull/716)
Branch: `research/mr32-residual-belief-dev-20261031`
Parent: MR31 head `0503b25fe74dca30035a65c1d81edabddd31926e`
Current PR head at receipt creation: `e7559fbbd72acf6aa0aa295e167c122ca6f1580c`

## Delivered source

- `research/native/itd02/mr32/residual_belief.py`
- `research/native/itd02/mr32/test_residual_belief.py`
- `research/native/itd02/mr32/MR32_A_SOURCE_ONLY_PROTOCOL.md`
- `.github/workflows/mr32-residual-belief-source-only.yml`

The candidate is isolated from accepted R7 PR #501 and implements a fixed 16-slot representation (7 active, 9 retained), selected-outcome-only correction, bounded eviction/promotion and SHA-256-checked checkpoint restore.

## Focused local engineering evidence

Local isolated Python execution:
- `python -m unittest -v`: **9/9 PASS**.
- `python -m py_compile residual_belief.py test_residual_belief.py`: **PASS**.

The retained-state promotion test initially exposed a cardinality bug: promotion emptied a retained slot rather than swapping the promoted belief with a demoted active belief. The implementation now performs a swap and the test confirms exactly 7 active and 9 retained valid slots after promotion.

The cold-restart test was also hardened: it now snapshots only at a valid post-feedback boundary and compares two independently restored instances. It does not manipulate the implementation's pending-feedback internals.

These results are local source-working-copy tests. **Exact committed Git-blob execution by CI is UNVERIFIED.**

## GitHub readback and CI

All four added artifacts were read back from GitHub. Draft PR #716 remains OPEN/DRAFT/UNMERGED.

On prior PR head `8731e563cb1fce21efc3895cf3a1138e50fb94b5`, generic checks reported:
- NCI-04G5 focused native observation: PASS.
- NCI-04G6 focused native learning/source controls: PASS.
- NCI-04G7 source-bound producer: PASS.
- G29 atlas acceptance: FAIL-CLOSED on both Windows and Linux because the indexed source file set changed.

The G29 result is an atlas freshness/integration failure; it is not a reported MR32 unit-test failure. The four new MR32 source files have not yet been added to the advisory atlas. The dedicated `mr32-residual-belief-source-only` workflow was committed, but no run for that workflow was observable through the connected Actions endpoints at the time of this receipt. Do not report cross-platform MR32 CI as PASS.

The last committed test source was read back successfully. No Windows or Linux exact-source execution of the MR32-specific test file is claimed.

## Scientific interpretation

This is a mechanism prototype, not a scientific result. Nearest-prototype residual memory may be no better than conventional prototype, recurrent or Bayesian memory. There is no trained-control comparison, no prospective held-out source family, no reward/decision outcome, no causal intervention study, and no total-resource parity result.

The 16-slot count is only a structural bound. Full checkpoint bytes, Python object overhead, feature transport, inference CPU, wall time and peak RSS must be measured and matched against the baselines before any scientific acceptance.

## Governance and next gate

- FSA-04 issue #83 remains OPEN; independent first-use authority remains unavailable.
- No original environment reset/step, source family intake, protected cohort, accepted ref, controller, queue, model integration, merge or promotion occurred.
- MR31 remains an acquisition-only development result.
- Wingless remains independent; no code or state was copied into Wingless.
- Next safe engineering gate: exact MR32 source CI on Windows/Linux, G29 advisory atlas refresh and full regression; then add equal-byte memoryless/recurrent/Bayesian controls and pre-freeze a strictly separate development protocol. Original-world evaluation still requires independently qualified FSA admission.

Disposition:
`MR32_SOURCE_ONLY_IMPLEMENTATION=COMMITTED`
`LOCAL_FOCUSED_TESTS=9/9_PASS`
`EXACT_COMMIT_CI=UNVERIFIED`
`G29_ATLAS=FAIL_CLOSED_PENDING_REINDEX`
`SCIENTIFIC_GAIN=NOT_TESTED`
`ORIGINAL_WORLD_FIRST_USE=BLOCKED`
`ACCEPTANCE_OR_PROMOTION=NOT_GRANTED`

## Post-receipt CI finding and repair

The first exact-head MR32-specific workflow run, `41209034566`, completed with **Windows FAIL and Linux FAIL** in the test-invocation step. Both failures were the same harness defect: the test runner was invoked from repository root while the test module imports its sibling as `residual_belief`, producing `ModuleNotFoundError`. This was a test-discovery/infrastructure failure, not a model or scientific result.

Corrective workflow commit: `78e66a443bb6bd5d214ed2c0c6d98e29fcbb892a`. The workflow now changes into `research/native/itd02/mr32` before byte-compilation and unittest discovery. The correction was read back from GitHub. A new exact-head dual-platform run was not observable after this update through the connected Actions endpoints; therefore the fix is committed but **Windows/Linux requalification remains PENDING/UNVERIFIED**. Do not cite run `41209034566` as PASS.

The local 9/9 result remains source-working-copy evidence. Scientific gain remains NOT TESTED.

## Final MR32-specific exact-head qualification update

After correcting the test working directory, the exact-head dedicated workflow run `41209106407` completed **SUCCESS** on both `ubuntu-latest` and `windows-latest`. Both jobs completed source checkout, Python setup, syntax compilation, the nine focused unit tests and clean-checkout verification. This qualifies the committed MR32 candidate files on both operating systems for these focused source-only contracts.

The previous run `41209034566` remains recorded as a failed test-discovery attempt; it is superseded by the passing corrected run, not erased.

At the time of this update, separate G29 atlas workflow `41209106414` remained in progress on Linux while the Windows job failed closed at `scripts/build_code_atlas.py --check-if-present` because the MR32 paths changed the indexed file set. The MR32-specific source-only PASS does NOT imply G29 atlas acceptance or full integration regression PASS.

## MR32-B — conventional controls and exact-head qualification

Current PR #716 head: `c753e5044ecb6570915405978f8c79d01e42662d`.

Added:
- `mr32_controls.py`: a memoryless global-mean control and a conventional nearest-prototype/online-EMA control.
- `test_mr32_controls.py`: four interface/partition/state-serialization tests.
- Updated protocol and dedicated workflow to include both control tests on Linux and Windows.

Exact-head dedicated source-only Actions run `41214448272` completed:
- Ubuntu: **PASS**.
- Windows: **PASS**.
- Syntax compile, residual-belief tests, control tests and clean-checkout checks all completed successfully.

The tests establish interface and bounded-slot software properties only. The conventional prototype shares a 16-slot, 7/9 partition, but exact byte/resource parity is NOT established. These controls are not yet a capable trained recurrent/state-space or Bayesian/model-based comparison; no efficacy result is claimed.

The separate G29 atlas workflow `41214448271` remains an integration blocker:
- Windows failed at `scripts/build_code_atlas.py --check-if-present` because the new MR32 paths are not indexed.
- Linux was still in progress at this receipt update, with the same freshness check already failed and regeneration/clean-check steps pending.
- Do not mark G29/full integration PASS. The exact MR32-specific Linux/Windows workflow remains green independently.

Next safe gate: resolve generated atlas artifacts using the repository generator against the exact PR head, then complete G29 and required full regression. Following integration, add full recurrent/Bayesian controls and total-byte/process-resource accounting in a frozen source-only development protocol. No original-world admission or scientific cohort use is authorized.

Disposition:
`MR32_SOURCE_ONLY_CI_LINUX=PASS`
`MR32_SOURCE_ONLY_CI_WINDOWS=PASS`
`MR32_CONVENTIONAL_CONTROLS=IMPLEMENTED_INTERFACE_ONLY`
`TOTAL_RESOURCE_PARITY=UNVERIFIED`
`G29_ATLAS=BLOCKED_STALE_INDEX`
`NATIVE_SCIENTIFIC_GAIN=NOT_TESTED`
`ORIGINAL_WORLD_FIRST_USE=BLOCKED`


## MR32-C — selected-action conditioning correction

Source review identified a critical omission in MR32-A/B: the predictive belief key was public features only, not (public features, selected action). This could conflate consequences of distinct actions and did not meet the ITD-02 action→consequence requirement.

Corrected source now:
- requires selected action explicitly on prediction;
- conditions belief lookup and update on that action;
- persists the action key in each occupied slot;
- binds action to the pending one-shot feedback receipt;
- bumps checkpoint schema to `yggdrasil.mr32.residual-belief.action-conditioned.v2`;
- updates both conventional controls to the same call contract;
- adds tests for action separation and an action-insensitive memoryless control.

These are source changes only. They supersede earlier local test counts and require a fresh exact-head Windows/Linux run. No passing CI is claimed for MR32-C until that run terminates successfully. The action index 0..2 is a development assumption; source-owner mapping and original-world permission remain absent. The candidate has not been scientifically evaluated.


## MR32-C follow-up comparator repair

The action-conditioned conventional prototype control initially wrote every unseen action-context prototype into active slot zero, accidentally overwriting other action keys. Corrected it to use an empty active slot first and only replace an existing active prototype when all active slots are occupied. This is a comparator engineering repair. The exact-head dual-platform workflow must cover it before the control is considered qualified. No scientific comparison result is claimed.

## MR32-C first exact-head attempt and harness repair

The first action-conditioned CI run associated with head `5cbc17f44ece54d9d427dcfa27d2e28049e93b29` was run `41216007649`. Linux and Windows both failed in the focused unit-test step. Linux logs isolated one stale test call: the invalid-feature-dimension test called `predict(features)` without the now-required selected-action argument, so Python raised a missing-argument `TypeError` before checking the dimension. This was a test-harness/interface migration defect, not a learner result.

Corrected the test to call `predict((0.0,), 0)` and committed it at `122de0a152b41e3d4eb7203f7914850764bfee7a`. The corrected file was read back. A fresh exact-head MR32 Windows/Linux CI result for `122de0a...` was not observable through the connected workflow-run listing at the time of this receipt; therefore current action-conditioned code is **NOT YET QUALIFIED**. Prior MR32 pass `41214448272` predates action conditioning and does not qualify this code.

The G29 atlas workflow remains fail-closed on the new file set. No acceptance or promotion is requested.

## MR32-C corrected exact-head CI closure

After fixing the final stale test call to supply selected action `0`, exact-head dedicated Actions run `41216087359` completed SUCCESS on both Windows and Ubuntu.

Both jobs completed:
- Python syntax compilation for residual candidate, both conventional controls and both test files.
- Full focused unittest invocation for `test_residual_belief` and `test_mr32_controls`.
- Clean-checkout verification.

This is the corrected action-conditioned source and test set. The earlier run `41216007649` failed on the missing selected-action argument; it is retained as a harness failure and is not counted as passing qualification.

At the same PR head, the separate G29 workflow run `41216087470` did not pass: Windows failed at atlas file-set freshness (`YGG_ATLAS_FAIL_CLOSED: indexed file set changed`); Linux had reached the same failing freshness check and remained in atlas regeneration at last observation. G29 and full integration qualification remain blocked until the canonical generated atlas artifacts are refreshed and both platforms complete their checks.

MR32 focused CI PASS is only source/software-contract qualification. It does not demonstrate efficacy, causal learning advantage, equal total-resource performance, or unfamiliar-world transfer. FSA-04 remains OPEN and original-world first-use remains blocked.

## MR32-D — cross-platform source-only resource inventory

The updated exact-head Actions run `41217380126` passed on Ubuntu and Windows. It compiled all four candidate/control/test modules, ran both focused suites, ran `resource_inventory.py --steps 256`, and passed clean-checkout verification.

Measured results on the same deterministic 256-step synthetic stream:

| Metric | MR32 residual belief | Conventional prototype | Memoryless mean |
|---|---:|---:|---:|
| Serialized state bytes | 3,853 | 3,483 | 63 |
| Deep Python object bytes | 7,335 | 4,419 | 852 |
| Windows tracemalloc peak | 178,456 | 134,736 | 166,320 |
| Windows wall seconds | 0.04369 | 0.01073 | 0.00437 |
| Linux tracemalloc peak | 178,352 | 134,728 | 166,312 |
| Linux wall seconds | 0.09642 | 0.02100 | 0.00898 |

These are descriptive host measurements, not fair resource parity: checkpoint formats differ, Python deep-size/tracemalloc are not OS process RSS, and wall-time measurements on hosted runners are noisy. Still, the initial signal is unfavorable: MR32 uses more stored state and substantially more runtime than the conventional prototype on this stream. Its compactness/resource advantage is **not demonstrated**.

Machine-readable result: `research/native/itd02/mr32/resource_inventory_receipt.json`, commit `0a6946f60993a6c236f932fb233b51bbe1052a30`.

## Latest separate G29 state

At exact code head `14f653d7b3d4d7fe68ca83f5cd65e8d4eaa3e5e2`, G29 run `41217380160` remained in progress on Linux and failed on Windows at the same fail-closed indexed-file-set check. It is not a MR32 source test failure; the generated advisory atlas artifacts have not been refreshed for the new files. Atlas and full integration acceptance remain blocked.

Disposition:
`MR32_ACTION_CONDITIONED_FOCUSED_CI_WINDOWS=PASS`
`MR32_ACTION_CONDITIONED_FOCUSED_CI_LINUX=PASS`
`MR32_256_STEP_RESOURCE_INVENTORY=PASS_EXECUTION`
`MR32_RESOURCE_ADVANTAGE=NOT_DEMONSTRATED`
`G29_ATLAS=BLOCKED_STALE_INDEX`
`SCIENTIFIC_EFFICACY=NOT_TESTED`
`ORIGINAL_WORLD_FIRST_USE=BLOCKED_FSA04`


## MR32-G interaction Bayesian baseline

Added `interaction_bayes_control.py`, which extends the Bayesian linear feature map with all feature×selected-action terms (68 coefficients per output), plus `test_interaction_bayes_control.py`. The test includes a balanced, held-out sign-reversal synthetic relation to verify that the interaction basis can represent action-conditioned feature effects that the additive model cannot.

The dedicated workflow already compiles and runs this test module and includes the model in the resource inventory. New commit requires exact-head Windows/Linux qualification. This control is still a diagonal-covariance Bayesian linear predictor over a fixed interaction basis, not a full Bayesian causal learner. No native-learning result or original-world cohort is claimed.


## MR32-H learned allocator exact-partition correction

The initial allocator draft capped memory count at 16 but represented partially filled stores with fewer than 16 positions. This did not meet the repository's exact fixed-state contract. The implementation was revised to use 16 explicit positions from initialization, with exactly 7 active and 9 retained slots at all times; unoccupied positions are explicit placeholders. A dedicated test now asserts the partition before any memory is inserted. Rebalancing fills the top seven predicted-utility entries into active slots and the next nine into retained slots; when full, the lowest-utility retained item is evicted. Pending-use items cannot be evicted.

This is a correctness fix to the source-only learned allocator. It requires fresh exact-head Linux/Windows qualification; no earlier CI result covers this revision.
