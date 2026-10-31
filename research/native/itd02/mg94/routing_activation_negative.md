# MG94-V — routing activation negative

Development-only local reproduction of source: `research/native/itd02/mg94/surprise_routing_ablation.py`, Git blob `5e33e1c21d4b8dc5e05ac871f5dca55824dc3af2` at Yggdrasil commit `46ba06f949159069fd4fc61acd3b8cc2dd48ae7b`.

Using the four hard-coded, 24-event source streams and both route-enabled and route-disabled controls, an isolated local Python reproduction produced:

| Stream | Correct | Routed messages | Predictions identical |
| --- | ---: | ---: | --- |
| stable | 23/24 | 0 | yes |
| reversal | 21/24 | 0 | yes |
| recurrence | 20/24 | 0 | yes |
| alternating | 22/24 | 0 | yes |

**Negative finding:** No message is emitted on these streams. Therefore the current ablation cannot test the causal effect of communication. A future test must first verify nonzero delivery, then compare matched controls with and without consequential intercellular updates; preserve source-public observation and same information budgets.

Classification: source-free synthetic engineering evidence. Execution was local reproduction, NOT official exact-head CI. Full regression UNVERIFIED. Original-world test NOT EXECUTED. Scientific gain NOT DEMONSTRATED. No acceptance or promotion.
