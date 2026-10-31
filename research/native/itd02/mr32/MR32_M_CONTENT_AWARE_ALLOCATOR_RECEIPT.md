# MR32-M — content-conditioned learned memory allocator receipt

Date: 2026-10-31
PR #716: OPEN / DRAFT / UNMERGED.
Exact source/test head: `045f58cb5cdea0d49cadaf9d65bccf6697d8138e`.
Dedicated Actions run: `41227351075`.
- Windows job `124614166517`: PASS, 54 tests, syntax, resource inventory, clean checkout.
- Ubuntu job `124614166680`: PASS, 54 tests, syntax, resource inventory, clean checkout.

## Candidate

`content_aware_memory_allocator.py` is a separate version of the learned fixed-budget allocator. It uses the existing five metadata features plus all 16 stored representation values (22 utility inputs including bias). It retains exactly 16 slots, seven active and nine retained, updates utility weights only after selected-use feedback, rejects checkpointing while feedback is pending, and restores an integrity-checked state.

The metadata-only candidate MR32-H is unchanged.

## Synthetic content discrimination

FIT: eight new memory keys with the same metadata, four with representation coordinate 0 set to +1 and four set to -1. Each is explicitly marked used and trained for 40 rounds; usefulness feedback is positive for +1 and zero for -1.

TRANSFER: a fresh store receives only learned scorer weights and 16 disjoint-key memories, eight of each representation sign, with metadata held identical. No transfer feedback is given. Keys are arranged so the metadata-only zero-weight tie-break selects negative records first.

Results on both Windows and Ubuntu:
- Content-aware scorer active set: **7/7 useful**.
- Metadata-only scorer active set: **0/7 useful**.
- Content-aware transfer feedback events: **0**.

This isolates a case where metadata-only cannot distinguish the candidates but learned representation weights can. It is a simple linear separability fixture, not general content understanding or authentic task utility.

## Resource inventory

Same deterministic 256-step descriptive inventory:
- Content-aware native serialized state: 4,555 bytes.
- Common checkpoint envelope: 4,663 bytes.
- Deep Python object estimate: 7,664 bytes.
- Tracemalloc peak: not copied into this receipt; hosted-runner Python allocation metric is not OS RSS.
- Wall time: 0.1605 s Windows / 0.1597 s Ubuntu.

For reference, the metadata-only allocator reported 4,313 native bytes, 4,416 common-envelope bytes, 7,121 estimated object bytes, and 0.1357/0.1374 seconds. These are single-run hosted-runner diagnostics, not calibrated benchmarks or equality of total resource use. Content awareness adds state and compute overhead.

## Limitations

- Representation inputs are fixed-dimensional, caller-supplied 16-value vectors; their formation is not learned.
- Utility model is a hand-designed linear function class; only its weights are learned.
- FIT and TRANSFER use the same synthetic sign rule; only memory IDs are disjoint.
- The task does not model future queries, delayed retrieval, causal world state or authentic reward.
- No unfamiliar task-family transfer, restart-under-interference benefit, or independent scientific replication.
- Resource accounting is descriptive, not exact total-resource parity.

## Disposition

`CONTENT_CONDITIONED_WINDOWS_LINUX_CI=PASS`
`SYNTHETIC_HELDOUT_CONTENT_SELECTION=7_OF_7`
`METADATA_ONLY_CONTROL=0_OF_7`
`TRANSFER_FEEDBACK_EVENTS=0`
`LEARNED_REPRESENTATION_FORMATION=NOT_IMPLEMENTED`
`AUTHENTIC_TASK_EFFICACY=NOT_TESTED`
`UNFAMILIAR_WORLD_TRANSFER=NOT_TESTED`
`G29_ATLAS=SEPARATE_STALE_INDEX_BLOCKER`
`FSA04_ORIGINAL_FIRST_USE=BLOCKED`

No original environment, protected cohort, accepted source, R7 integration, production model, merge or promotion was touched.
