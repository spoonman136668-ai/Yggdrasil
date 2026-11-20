# YGG-JEPA2-05 historical native forgetting across five old windows

**Independent contributor research only.** This work is `UNPREREGISTERED_POSTHOC`. Both native models, their old Brier failures and original continuation events were already consumed. The first commit on this isolated branch freezes the five disjoint window positions, original source/checkpoint custody, tolerance and two-seed outcome labels *before the code was added*. This is not prospective scientific source or heldout generalization: every 32-episode historical window consists of previously learned training events.

This experiment addresses a distinct uncertainty in JEPA2-05: do old-episode predictions deteriorate broadly across **old chronology**, or chiefly the original published **last-32** old-probe set? Source-exact snapshots of the original and continued trained native models score identical 32-witness blocks at starts `floor(k * (n-32) / 4)` for `k = 0..4`; the last block reproduces the published original retention metric. During exact 16-observation continuation, the code also measures every selected window directly before its single documented reset, with the same event learned on a disposable clone **without only the context repartition**, and after the true reset.

Every replay event is one of the original sixteen previously witnessed episode tuples from immutable archived checkpoints; 0 new source actions or generator calls. The test asserts authentic original/final native cold hashes, exact witness prefix, reset ordinal, published initial/final last32 Brier score, disjoint windows, cross-OS score parity, and no model promotion. The inherited repository regression and G29 source-index seal remain mandatory.

**Integration rights:** Only Unified Causal Intelligence Amalgam Work chat coordinates the accepted learner and checkpoint lineage. This research result provides no permission to import JEPA2's synthetic episode source into the different official Amalgam source contract, promote learned states or start another owner.

Run Python 3.12 on exact checked-out candidate, with original pinned dependencies:

```bash
python -B research/contrib/chatgpt/YGG-JEPA2-05-OLD-WINDOW-RETENTION-POSTHOC/window_map.py --platform linux --output window-map.json
```
