# FKP-18 — tokenless temporal eligibility traces (independent successor)

**Status: ENGINEERING PROTOTYPE — scientific first-use NOT RUN, native Yggdrasil main NOT CHANGED.**

## Why this exists

FKP-17 draft PR #1109, exact qualified candidate `272423baac407d97791409247df05e4e98fcb7da`, preserved a meaningful 64-world known-family result (STRUCTURED +0.7246 over its strongest equally informed control) but also reproduced a decisive representational limitation on both Ubuntu and Windows: its action×register×delta memory collapses causal histories with different starting-state conditions or event order. Additional training of that same unconditioned representation cannot eliminate the alias. Its original unfamiliar DEV/TRANSFER worlds are untouched. **FKP-17 remains frozen, unmerged, and NOT a scientific pass.**

WSP-120 (draft PR #1113) already independently explores growing finite causal graph programs after contradictions. **FKP-18 does not copy, merge into, or modify that track.** Here the distinct question is what a small tokenless event-memory *must be able to express* before making delayed or history-dependent intervention claims.

## Preregistration and scope

The **first and only change in the first FKP-18 commit** `1a53f16231871d2ac6db0b25e0e9a8ab61b03b60` was this track's `prereg.json`, on baseline accepted Yggdrasil `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. The four source-safe synthetic two-step witnesses were mathematically specified before code: A (+1 then −1 for action3), B (−1 then +1), AB (action2 then5), BA (action5 then2), with physically consistent public registers and earned reward. No protected world seed or private generator is used, and the input-binary hashes are **not** qualified scientific-source identities.

This is an **engineering representational capacity gate**, not an unseen-world learning score. Any later scientific hypothesis requires its own source-owner freeze, identifiability/headroom, frozen matched strong controls including fully trained recurrent models, retention/interference/transfer and separately authorized first use.

## Implementation

`temporal_trace.py`: a bounded explicit non-gradient, non-token, non-transformer memory. Given a genuine public action consequence, it initially stores action×target×signed-delta counts. When a new **observed** result conflicts with the earlier action-only effect, it allocates a sparse current-state-value context fork, backfilling only the verified first witness. It also tracks actually observed predecessor-action→current-action adjacencies; **these are event-order records, not automatically true causal credit or evidence of an inferred hidden operator**. No source-private labels, future returns or alternative outcomes are available. Each action record requires a monotonic event index and consistent physically observed history; rejected events do not mutate learned evidence.

The architecture is deliberately bounded to **512 sparse relation slots**, **65,536 logical learned bytes** and 256 public events per local episode. Logical byte accounting describes its compact conceptual parameter ledger, **not Python object heap/RSS**. Pure JSON+SHA snapshot/restore is bounded and never executes pickle or source code.

`source_safe_witness.py` constructs exactly four frozen two-action public transcripts, with physical state continuity, signed earned rewards and verified preceding history. `test_temporal_trace.py` proves the expected state/temporal distinction, tests independent **exact conditional retrieval** (which can also solve the toy conditional case), tests no-context/no-order ablations, checks content-addressed cold restore, rejected private/future records, duplicates, nonphysical histories, capacity and atomic rejection. `test_prereg.py` preserves the experiment scope and frozen first commit.

`run_source_safe_capacity.py` prints a machine-readable source-SHA-pinned engineering receipt. It must report **conditional A +1, B −1**, distinct candidate semantic receipts, the expected ablation aliases, two observed physical actions per case, and cold state replay. No training data beyond those four previously specified toy witnesses is exposed.

## Acceptance and scientific limits

- **ENGINEERING PASS** only after the exact source SHA is pinned and source-safe tests, generated G29 atlas and mandatory full inherited regression pass on both Ubuntu and Windows. The independent proof must agree across OS. The preregistration and baseline source must not change afterward.
- **MIXED/NEGATIVE** if either the conditional or temporal distinction aliases, or if the stronger exact retrieval baseline shows the same capacity (which it does for state-conditioned effects). Never inflate this into unique native superiority.
- **SCIENCE NOT RUN:** FKP-18 currently proves an expressive distinction only. It does **not** demonstrate unanticipated operator invention, independent causal agency, actual delayed effect attribution, unfamiliar-law transfer, autonomous self-improvement, latency gain, accepted model integration or general intelligence.
- **DEPLOYMENT NONE:** no accepted `main`, controller, scheduled task, unrelated WSP/Wingless/Hybrid project, private owner, source protection or paid API was modified.

The next substantive science question is whether **true delayed causal credit** can be inferred from controlled action consequences at matched information and computation, rather than merely remembering ordered actions. That needs a separately frozen, independently owned evaluator and new first-use authority—not another retuning of this capacity toy.
