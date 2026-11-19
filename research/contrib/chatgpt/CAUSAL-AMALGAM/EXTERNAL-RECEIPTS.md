# Source-bound development receipts

The existing CKAD-20 admission and checkpoint bytes are preserved. A caller
authorized for a new development source can pass its frozen manifest SHA-256 as
`external_source_sha256`. It supplies this pin independently of the producer's
`source_sha256` claim. `experience_packet_sha256` binds the source, receipt ID,
paired views, and public row. The source pin identifies the producer contract.
The caller must still validate the frozen split and the actual revealed row
before admission.

The first valid external receipt appends to the existing native prefix and
starts one contiguous source suffix. The native checkpoint records the boundary,
source pin, and ordered packet digests. The joint checkpoint replays each entry
with its original source identity through the same native and four-specialist
transaction. Restoration requires the independently pinned checkpoint hash and
source manifest hash. A different source, a reused ID from the legacy prefix,
or a conflicting duplicate is rejected. An identical suffix retry is idempotent.
This version deliberately supports a single external source suffix. It has no
source actor, source-owner lease, scheduler, or held-data admission route.

## Qualification

Use the two pinned donor blobs and reconstruct the legacy anchor with
`joint_update_preflight.py --checkpoint-out`. Place the native donor,
specialist donor, and anchor under their names in `selection_protocol_dev.json`.
From the repository root run:

```sh
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python -B research/contrib/chatgpt/CAUSAL-AMALGAM/external_receipt_preflight.py INPUTS
```

The fixture uses a declared engineering row, independently restores the
disposable descendant in a fresh process, and checks wrong/missing pins,
legacy-source packets, legacy-ID reuse, conflicting replay, a forged head and
altered checkpoint provenance. It acquires no new source actions. The historical
curriculum and its source hashes stay sealed at their original commits.

## Continuation

Before producing the circuit intake, implement the source adapter and a
cell-local public-evidence readout. Freeze the allowed FIT receipt inputs,
disjoint probe/scored rosters, source pin and exact parent in Git. Verify that
unknown, scored and out-of-roster packets fail closed at that adapter. Preserve
the original CKAD-20 replay and the existing native action policy.
