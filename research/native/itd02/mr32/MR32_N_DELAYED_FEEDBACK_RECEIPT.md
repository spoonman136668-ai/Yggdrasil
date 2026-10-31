# MR32-N — delayed-feedback feature receipt qualification

Date: 2026-10-31
PR #716: OPEN / DRAFT / UNMERGED.
Exact tested head: `be38b05fa71d5c8c5447c224babc4d67b33411b0`.
Dedicated source-only Actions run: `41227842101`.
- Windows job `124615779471`: PASS, 56 tests, compilation, resource inventory, clean checkout.
- Ubuntu job `124615779280`: PASS, 56 tests, compilation, resource inventory, clean checkout.

## Defect found

Both learned memory allocator variants previously recomputed utility features when the usefulness outcome arrived. If feedback was delayed by intervening events, the scorer therefore updated using later recency/use metadata rather than the metadata that was present when the memory was retrieved and used.

## Correction

Both the metadata-only and content-aware allocators now:
- capture the exact utility-feature vector at `mark_use`;
- retain that immutable per-memory feature receipt while feedback is pending;
- compute the pre-feedback utility prediction and gradient from that receipt when the selected-use outcome arrives;
- clear the receipt after successful feedback;
- reject checkpointing while the receipt remains pending;
- validate that `pending_use` and `pending_features` are consistent;
- reject old schema versions after bumping metadata-only to `v3` and content-aware to `v2`.

The content-aware checkpoint restore return annotation was also corrected at this exact tested head.

## Regression evidence

New delayed-feedback tests insert five distractor memories between use and outcome feedback. They preserve the feature vector captured at use time, verify it differs from the later-arrival feature vector, compute the expected linear update from the frozen receipt, and compare each resulting coefficient to that expected value. Both allocator variants pass.

Run `41227842101`:
- Windows: 56/56 tests PASS.
- Ubuntu: 56/56 tests PASS.

The tests establish delayed-credit implementation correctness for this bounded scorer. They do not demonstrate delayed causal credit for real-world task effects, because outcomes are synthetic test values and the metadata/representation basis remains hand-designed.

## Disposition

`USE_TIME_FEATURE_RECEIPT=IMPLEMENTED`
`DELAYED_FEEDBACK_REGRESSION_WINDOWS_LINUX=PASS`
`PENDING_RECEIPT_CHECKPOINT_GUARD=PASS`
`AUTHENTIC_TASK_CAUSAL_CREDIT=NOT_TESTED`
`UNFAMILIAR_WORLD_TRANSFER=NOT_TESTED`
`G29_ATLAS=SEPARATE_STALE_INDEX_BLOCKER`
`FSA04_ORIGINAL_FIRST_USE=BLOCKED`

All evidence is stored in the Yggdrasil repository. No original-world environment, protected cohort, accepted R7 source, merge, production integration or promotion was used.
