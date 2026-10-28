# ITD-02 V31K — inherited regression-contract and source-index qualification-only repair

**Frozen parent:** V31J draft PR #633 exact `00f9b3c67459516eb5f362a6113ae219b6e9fd8d`. This document is created as the first V31K commit, before changing inherited tests or derived index. No science preregistration is replaced or new held-out family admitted.

## Failure custody (from original 138-test full Ubuntu regression)

- `test_code_atlas.G29.test_source_and_pinned_artifact`: stale committed G29 source index (indexed file set changed).
- Five old `source_only.v8` assertions in `test_itd02_cell_temporal_register_dev.py`, `test_itd02_context_credit_v7_dev.py`, `test_itd02_local_credit_v6_dev.py`, `test_itd02_neighbor_trace_dev.py`, and `test_itd02_two_phase_public_native_dev.py`. The exact unmodified original bridge source has schema `source_only.v12`.
- One old frozen neighbor-trace assertion in `test_itd02_neighbor_trace_dev.py` contradicted V12's explicit **inference trace updates during `learning=False`**, while model weights and learned action-credit must remain frozen. Preserve the failed-learning rollback veto, assert the exact current trace update formula, parameter identities unchanged, and checkpoint roundtrip; do not relax actual frozen-parameter verification.

## Bounded changes

Only those five inherited test files, this note, and a one-shot isolated source-index rebuild workflow may be authored before derived artifact production. No changes to the native bridge, V22 or V31I/J learners, source/reward worlds, holdout, criterion, resource receipt, FORGE, CKB-plane, original runtime, or model checkpoint. G29 reanchor workflow may generate **only** `.ice/code-atlas.json`, `.ice/code-atlas.html`, and `.ice/code-atlas.ice` on this isolated qualification branch, after verifying exact source SHA and changed paths. Preserve the original V31J measurement as independent evidence.

## Qualification

- Verify exactly one frozen V31J parent and prereg-first commit, unchanged original native bridge/V17/V22 and original V31J audit blobs, bounded test-only delta.
- Focused tests for five corrected contracts and V31I/V31J, followed by deterministic G29 regeneration on exact new source commit and independent source-index validation.
- Run **one complete inherited Python regression** with all tests (including G29) on both Windows and Ubuntu after G29 is committed. Zero skipped tests except platform-inapplicable tests explicitly disclosed; full regression must not exclude known failures. Read-only generated Atlas validation on both hosts. Fail closed if bot push unavailable or any test still fails.
- G29 generator and original SCIENCE NO-GO/heldout boundaries unchanged. Qualifying frozen inference traces is NOT permission to mutate frozen learned parameters. Distinguish infrastructure repair from scientific evidence. Keep both source and derived qualification draft/unmerged; no accepted-ref or protected-main changes.

**Reused immutable foundation:** 00f9b3c67459516eb5f362a6113ae219b6e9fd8d. One final integration/full regression is mandatory despite focused-test reuse. Qualification is not promotion.
