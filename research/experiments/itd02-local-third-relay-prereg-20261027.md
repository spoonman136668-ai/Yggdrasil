# ITD-02 additional local readout relay, locked engineering hypothesis — 2026-10-27

**Authority: development-only, not FSA scientific first-use.** Frozen unchanged PR #582 source `a39171a76d0d7817e3563682bb139a9d7ecf37c4`, original legacy G29 remains not qualified for PR #582. This experimental branch must not merge into any accepted source or dispatch an original-world task.

## Falsifiable source-grounded mechanism

The original 8-cell Yggdrasil memory head exchanges public observation features through exactly two sequential neighbor-hops. Exact-source evidence [run 40575348091](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/40575348091) establishes that TurnAround maps both MRV and docked_MRV to identical zero inputs, while GoForward maps Nothing and docked_LRV to identical zero inputs, even after real native learning. The original native predictor can distinguish those observations, but the fused policy did not in the forced-action contrast.

Change **only** `NativeRingMemoryDev._signals()`: after the original two-hop neighbor scalar exchange, perform **one additional strictly neighbor-only exchange** for both public pulse and retained-memory signals. Preserve `ROUNDS=2` as the per-call bound and preserve `_local_credit(..., ROUNDS=2)` with no longer-distance reward-credit leak. Account for exactly 3 physical message hops rather than 2 in `messages`. Keep original ring topology, public source contract, 8 gates + 9 action-head coefficients, checkpoint schema, fixed readout site mapping and original native weights. No global central broadcast, teacher or token architecture.

**Necessary checks:** both original zero-zero alias pairs become separable to their selected action heads at zero history; no fabricated reward labels or hidden source state; original local credit remains zero beyond two hops; 17 learnable scalars only; full original non-G29 Linux and Windows-portable test suites plus snapshot/cold-restore; exact source-byte identity. Increasing neighbor message count is a real **+50% readout-message cost** at fixed number of `_signals()` calls, not resource-free. Record measured CPU/RSS and checkpoint storage.

## Prospective independent holdout

Do not reuse previous fitting or diagnostic seeds. The only chosen comparison is **family IDs 14..21, seeds 12..19**, using the existing frozen-source unfamiliar-family source-free public-interface harness with deterministic hash-designed reward rules, 90 initial + 90 unfamiliar/change public steps, 4 independently acting actor types (native plus full-history count, recent EMA(0.5), last-six count). Every actor receives same information budgets and identical source-blind rotating exploration. Two source revisions (frozen #582 and candidate), Windows 2022 + Linux 24.04; **64 independent family/seed pairs × 180 steps × 4 actors = 46,080 events per implementation per OS**. Mandatory fresh Python process at phase checkpoint for native state.

**Precommitted verdict:** reject candidate if it fails its original native tests, loses mean initial or mean unfamiliar reward relative to frozen #582, or has no improvement on target action-alias reward contrasts. Even an engineering positive cannot justify promotion against independent conventional controls without further heldout trials, real source, full G29 regeneration, crash-reconciled durable custody, retail hardware and independent science validation.

No post-hoc coefficient tuning based on these holdout results is authorized within this experiment. Preserve all negatives and raw trial records.
