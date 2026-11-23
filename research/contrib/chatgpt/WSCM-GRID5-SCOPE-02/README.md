# WSCM-GRID5-SCOPE-02 — cross-episode hidden law contamination negative + safety patch

**Actual result:** ENGINEERING source-free original evidence class 24/24 focused PASS under Linux CPython 3.13.5 normal and `-O`, with negative A→B cold-restart case. Native 3-layer integration suite and full final platform regression **NOT RUN**. SCIENTIFIC gain **NOT VERIFIED**; original-world first-use #426 **HOLD**; DEPLOYMENT NONE.

## Why this patch is necessary

The previous detached candidate `448d5d49df68ecc56dc3040c8c42b0633016fda2` used a **global cross-episode** readout in `NativeGrid5Evidence.public_forecast`. The author-native DarkroomPermuted benchmark can assign different physical roles to the same public action ID on different permutations. Using source-free fixture A (action 0 from [0,0] → [0,1] for 50-step episode) followed by fresh fixture B (action 1 from [0,0] → [0,0], **no B witness of action 0**), the old concrete original component **incorrectly predicted [0,1] for B's action 0** and its coverage `public_plan` counted A's historical actions. This is an observed engineering **FAIL**, not a theoretical risk or a new original-world experiment.

## Minimal existing-architecture change

- The updated original `NativeGrid5Evidence.public_forecast(state, action, *, episode_id)` and `public_plan(state, *, episode_id)` require an exact 64-lowercase-hex **public episode ID** and filter witnessed outcomes / counts to the requested episode. Missing or malformed IDs fail closed. Fresh episode B produces **None (abstain)** for unwitnessed action 0; after a B witness (action 0 at [0,0] → [1,0]), B forecasts [1,0] while A's old [0,1] remains independently accessible; exact cold byte restore preserves both records.
- The existing `NativeEpisodeExperience`, `NativeCumulativeLearner`, and `NativeCausalAmalgam` optional fixture-only APIs now pass the explicit episode context. Original `NativeCausalAmalgam.plan(view)` and binary counters are unchanged. No invented structural identity, hidden permutation map, source actor, control plane or new learner.
- Nine existing native integration tests were authored previously and remain unexecuted. A **new tenth** native integration negative asserts A→B failure-closed/restore/relearning per episode, but is also **NOT EXECUTED**.
- Source-only isolated evidence class old 18 tests were updated for explicit episode IDs, and six *new* negative/positive tests added. Exact Git blobs match the locally tested code.

## Test and custody report

- Before: original evidence class blob `8734509b24dac0d3a13d5795f198082bda37f939`, 18/18 baseline tests PASS but missed this defect. The independent explicit A→B counterexample showed the faulty non-abstaining result. Evidence from the base source is original intact Git content, not edited benchmark code.
- After: evidence class blob `198056465930d1c2c5f47d6dc8f70fb43754aa0c` (local SHA256 `5829ff7309fbffc8e09fd4d08b502ba07723e4937c39f738c485badba0ca659e`); updated old test blob `351c0c1167d44f0b0db07e7a1fffac79f9fc2d8f` (SHA256 `a0c821a5bb22e30c24c360be073ec09817461ddfd365c3fd57a7bbed1f71b642`); new independent test blob `7085619c0386b06faa122d04a0a30ac41501e1b6` (SHA256 `aad24540ba0c87b78da5f5a91d2790117b731a633c9f47db75939aefec158ac2`). Both local commands `python -B -m unittest -v test_grid5_native_evidence test_grid5_episode_scope` and optimized `python -O -B -m unittest -v test_grid5_native_evidence test_grid5_episode_scope` => **24/24 PASS**, no skips; `python -m py_compile` PASS.
- The first local patched test command failed with a temporary **SyntaxError** from a test-rewrite quoting typo, repaired *before the final test runs and Git blob pin*; no source logic or scientific score was tuned in response. Preserve this as a dev tooling issue, not scientific false gain.
- Exact upstream source is `jaehyeon-son/dicp@e36b3f713fdca775728525dc621820a1989691f8` `gridworld/env/darkroom.py` blob `54f12df08dbe9215d0b7be91a94f0b059f2787ab`. No original world construct/reset/step or unconsumed cohort, no paid API, no runner and no known upstream license authorization.

## Gaps/decision

This corrected source has NOT been run against the real full native episode/cumulative/Amalgam class graph (the local path contains only exact Grid5 evidence/ingress modules). Do NOT count 24/24 as native integration qualification or source-world science. The current implicit DICP task family has *potentially shared* action mapping across successive resets, but that shared identity is **not authenticated** in WSCM, so conservative per-episode abstention is necessary. Provenance-qualified cross-episode reuse is a separate experiment subject to owner custody and strongest matched controls.

Until mandatory exact-commit cross-platform Linux+Windows full regression, interface negatives, source atlas and owner separately signed first-use, keep this detached candidate **DEVELOPMENT ONLY / NO PROMOTION**.
