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
