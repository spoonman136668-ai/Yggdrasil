# Native readout locality — developer diagnostic, not a repair

**Repository:** `spoonman136668-ai/Yggdrasil`. **Original coordinator:** [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), frozen head `86264b41a08d49f558418c0fba367f3a2636befa`. **Stacked retention PR:** [#1329](https://github.com/spoonman136668-ai/Yggdrasil/pull/1329), head `bbcca1d06d394a7bcfdc514f4e04bb269cb023cb`. Both carry the same native episode source blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`. Accepted `main` remains separate.

## Verified implementation fact

`NativeEpisodeExperience._context_weights_for(view, first, next_state)` returns `self._context_weights` unchanged when `next_state is None`. `context_forecast` uses this same vector for the first action for *every* requested public view; its component experts *do* receive the view. The separate terminal-stage path conditions weights on an already observed transition, but cannot provide first-stage view-specific routing. `_update_context` replaces the global posterior using all observed events; refresh optionally mixes it toward a global prior, not a bank indexed by the requested public view.

This is a **source-level capability boundary**, not evidence that every historical regression came from routing or that no other bank/adapter can work.

## Deterministic API counterexample

`tests/test_native_episode_context_recall_locality.py` uses the real `NativeEpisodeExperience.context_forecast` API with *two deliberately fake, fixed* experts: expert 0 gives 0.9 for public view (0,0) and 0.1 for (1,1), while expert 1 does the reverse. Both models are fully retained and queryable. If the global posterior is (0.99, 0.01), the native readout returns 0.892 for view (0,0), but only **0.108** for view (1,1), despite the retained expert for (1,1) giving **0.9**. For a **hypothetical** binary target 1 at view (1,1), squared errors would be **0.795664** for the mixture and **0.01** for that expert.

This constructs a counterexample to *context-specific retrieval guaranteed merely by saving old experts*. The fake specialists, hand-set prior and hypothetical label are **not** source evidence, a genuine trained model, a prospective benchmark, or measured native intelligence gain. No new world input is sampled.

## Execution, qualification, next experiment

- Source-blob equality across PR #1278 and #1329: **verified**.
- Diagnostic module syntax `python -m py_compile`: **PASS** in isolated Linux environment.
- Focused native unit test execution: **UNVERIFIED** (this container has no exact Yggdrasil PR checkout; it cannot reach GitHub to clone). Do not claim PASS from source inspection or `py_compile`.
- Exact candidate Linux/Windows complete regression, G29, native checkpoint custody and source-owner acceptance: **UNVERIFIED**.
- Changed native model code/weights, accepted main, PR heads, checkpoints, controller, original-world actions: **NONE**.

Run the diagnostic on the exact PR #1278 checkout: `python -m unittest discover -s tests -p 'test_native_episode_context_recall_locality.py' -v`. This is a **current-behavior** test documenting a retrieval limitation, not a test that a solution works.

**Next valid research question:** On a separately owner-qualified, already-consumed native checkpoint and fixed old-world witness windows, does at least one retained individual expert still predict old contexts accurately when the globally mixed first-stage readout fails? Report per-expert Brier, mixture Brier, source witnesses and cold-readout parity. Oracle-after-label best expert is only diagnostic, not a deployable router. If expert quality survives, trial an explicitly pre-action, context-conditioned read-only selector on newly qualified held data against the fully trained matching controls. If *all* retained experts have failed, investigate memory write/consolidation instead. Preserve existing source first-use NO-GO [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426). No training or unapproved dispatch.
