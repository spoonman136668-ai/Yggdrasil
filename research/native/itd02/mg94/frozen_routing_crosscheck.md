# MG94-AD frozen routing-selection cross-check

Classification: SOURCE-FREE SYNTHETIC DEVELOPMENT / NEGATIVE NATIVE CLAIM.

Source commit: `9d087ee9c937e358cf1aae0a93ef9d8c18aceeff`.
Source blob: `bc589c3b66e8837c9578d7d3d8b2121622e251ff`.

Frozen training data (two disjoint named streams) yielded:
- train_irregular: off 17, on 14 net
- train_blocks: off 7, on -4 net
- combined train: off 24, on 10
- selection rule: route only if train net exceeds disabled net, so **frozen route = false**.

Independent JavaScript implementation of the exact transition equations yielded held-out scores:
- irregular-shift: frozen/off 13, always-on 9
- blocks-shift: frozen/off 6, always-on -4
- alternating: frozen/off/on 22
- stable-one: frozen/off/on 22

Message cost is 1; on/off initial state equal. Train/evaluation streams are distinct named synthetic sequences, but shared generation patterns; this is **not independent original-world transfer**. Exact committed Python execution UNVERIFIED. No learned local causal message-value mechanism; this is conventional *global* routing-mode selection. Independent source comparison complete at the formula level; origin-owner CI and final full regression UNVERIFIED. No promotion or native scientific gain.
