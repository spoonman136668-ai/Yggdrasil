# CKAD42-EXACT — Lossless native causal-weight checkpoint determinism

This is an **engineering-only successor revision on the existing draft PR #1296**, not a second PR, accepted Yggdrasil trainer, scientific promotion, or a re-run of original CKAD42's consumed experiment.

**Frozen exact protocol commit:** `091e366fe804a2c71944df87f7e1ecebe64a023b`. This predates source edits and all exact-mode fixture executions. The earlier experimental 12-digit lossy codec is preserved with original SHA, scores and report in `CKAD-42-ENG/fixture_report.json`, but is **superseded**, not adopted, by the lossless alternative.

## Source-level repair

The exact alternative restores original full-precision `LearnedCausalBasis.checkpoint()` and full-precision `NativeInterventionRelations.checkpoint()`. Original CKAD42's seven unit fixtures and their **strict `==` forecast equality after cold restore** have been reinstated without relaxation.

The original learned weights' likelihood increments were `math.log(.85/.15/.9/.1)`, and softmax plus prequential Hedge used `math.exp`. Python's platform `libm` may change final IEEE-754 bits. The exact engineering fork pins likelihood increments using predeclared binary64 `float.fromhex` constants and computes exponentials using `decimal.Context.exp` with 42 precision and round-to-nearest, then converts once to binary64. It does not quantize, truncate or reinterpret stored weights.

## First-divergence diagnosis and bounded fix

The initial lossless candidate [Actions run #44492264866](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44492264866) passed original **7** and additional **7** unit tests per OS, and restored all nine fixture checkpoints *exactly*. However, Linux/Windows snapshot hashes matched for only **6/9** checkpoints. Of the six learned components, **only the Hedge mixture-weight field** diverged in the `action_interactions` fixture; all native causal basis weights and source receipts matched.

A disjoint fixture-only two-platform trace [run #44492689617](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44492689617) located the **first** difference at the **75th authentic engineering fixture event** (zero-index `t=74`). Its full/discounted forecast probabilities and prior Hedge state were exactly identical between OS. The **prequential discounted Brier squared residual** computed with Python `**2` differed by **one ULP** between OS, which changed the next Hedge factor and all subsequent stored Hedge bytes.

The source now replaces only the Hedge update's `(p - outcome)**2` operations with ordered binary64 multiplications `error*error` and `*0.5`, avoiding platform `pow`. The standalone trace itself uses the same strict path. This is a bounded deterministic arithmetic repair—not a retune of scientific seeds, choice of a new causal representation, or a change to validation thresholds.

## Frozen exact engineering controls

The original development scientific seed calls **do not run**. Exact fixture-only work includes `cycle`, `rule_shift`, and `action_interactions` (each 480 disjoint synthetic source episodes) with checkpoints at 160, 320 and 480. `fixtures.py` requires **zero** forecast change before/after cold restore. After the last source change the exact CI workflow must show **9/9** cross-platform full checkpoint SHA equality, **54/54** component SHA equality, **14** unit tests per OS, and original full-weight snapshot byte identity without any lossy codec.

*The old fixture report remains a historical checkpoint of the previous, superseded 12-digit candidate.* Exact-mode qualification evidence and original test logs must be added as a new separate `CKAD-42-EXACT/fixture_report.json` on the same branch after matching both OS logs.

## Boundary

This research branch is not authorized to rewrite accepted `main`, alter the official native Yggdrasil owner/runtime, issue a scheduled task, consume reserved `42211/42212/42311/42312/42313` seeds, repeat original `42111/42112` as fresh science, merge or deploy. Success on reused synthetic **engineering fixtures** supports code determinism only—not scientific improvement, independent unfamiliar-world learning, scientific first-use, matched compute efficiency, or acceptance regression qualification.

A production adoption would still need interface review (including performance), full final regression on exact candidate SHA and separately authorized science comparison on genuinely disjoint tasks. The previously reported CKAD42 scientific `DEV_NO_GO` remains unchanged.
