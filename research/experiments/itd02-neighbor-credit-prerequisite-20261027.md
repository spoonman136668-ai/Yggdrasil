# ITD-02 local conditional credit — bounded prerequisite gate, 2026-10-27

Original Yggdrasil #582 SHA a39171a76d0d7817e3563682bb139a9d7ecf37c4 and parent #574 stay unchanged, draft. Source-free research only.

Research prerequisite: v7 15-entry observation-action reward table improves synthetic tasks only slightly but is a **global public lookup**, not a neighbor-local cellular learning mechanism. Prove what each original reward-output cell at site 0/2/5 can observe locally in the two-phase public input, compare how many contexts are indistinguishable under single-phase or unordered phase-averaged features, and ensure none of the three heads can represent the 15 context-action pairs with a single local binary snapshot.

Run byte-frozen read-only diagnostic against v7 `3a32bd54f270058462d662302eb5732878d2edee` on both Ubuntu and Windows. For each reward cell, calculate phase0/phase1 ordered neighbor-bit words from the same original source and assert all 15 are distinguishable in ordered form, but only 9 with unordered phases and at most 4 in one phase. Compare different histories' per-cell neighbor trace; demonstrate the mere existence of traces cannot establish local *learned* conditional credit. No new model, no actual-world training, no FSA, no G29 claim.

Decision: If these limits hold, the next controlled implementation must use an explicitly cell-owned, checkpointed, **phase-sensitive context-action credit** (rather than a global reward table), train only from chosen public consequence, and prove its credit affects action ranks before expensive acting heldouts. Never assume this source-free representation capacity proves transfer or retail performance.
