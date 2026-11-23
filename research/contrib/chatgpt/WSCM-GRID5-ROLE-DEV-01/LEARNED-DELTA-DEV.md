# Source-free learned displacement in the original native Grid5 memory

This development-only, opt-in readout learns a **tentative translation vector** from public same-episode action consequences whose successors lie strictly within the grid. It contains no preloaded 5-action displacement table and does not receive the evaluator's hidden action-role permutation.

* A conflict between strictly interior effects returns `CONTRADICTION`; absent or clipped evidence returns `ABSTAIN`.
* A supported query at a non-boundary state and with a non-boundary forecast returns `HYPOTHESIS`, **not** `ENTAILED`.
* Observed evidence remains in the unchanged original `NativeGrid5Evidence` ledger; persistence, source mode, default planning and checkpoint formats are unchanged. The three native layers only forward this optional readout.
* This mechanism still assumes that a public action can behave like a constant translation on the tested interior domain. It does not learn arbitrary causal laws or boundary physics and cannot establish unfamiliar-family transfer.
* Frozen source-free prereg: `operator-delta-prereg.json` at parent commit `31abe0b3`. Dedicated negative tests and the disclosed 120-map screen are engineering checks, **not a fresh scientific evaluation**.
* The historical, already-consumed controls report standalone fitted-delta coverage 62.6667% and known-physics symbolic coverage 75.6% on 48,000 novel-state/action development queries. The new native readout's coverage is logged separately and must not be advertised as independent scientific gain.
* No original-world steps, paid API, Genome mutation, controller, new checkpoint schema, protected merge or autonomous promotion.
