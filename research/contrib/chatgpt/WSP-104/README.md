# WSP-104 — full historical TRAIN-only frequency-control admission (DEV)

**Research classification:** no protected first use, no trained conventional KG neural model, no direct-weight-learning result, no official evaluation labels, no scientific superiority, no deployment.

This track does not replace WSP-103 or alter the accepted Yggdrasil architecture. The starting source is [WSP-103 PR #1051](https://github.com/spoonman136668-ai/Yggdrasil/pull/1051) at `b004935f24670b49f8b418964d6f325a9bc4c366`, with passing Ubuntu/Windows exact-tree regression and G29.

The immutable design `prereg.json` was committed **before** any control code at `84773389ce77107004a2bd93c2a01b147d0937b1`. It freezes WSP-103's heldout 1/32 entire-subject–predicate query groups, the lowest 4,096 stable digest priorities, and the preexisting source-and-answer witness `008249f2c9731a426645c584e887bb056662c96f8c2385ba946b98ca3d9f49dc`. The known historical mirror has 21,343,681 training triples / 828 relations; it is **not canonical Wikidata5M**. No official validation/test files may be opened.

First baseline pilot: stream ALL the retained training triples through a 64-counter per-relation deterministic Misra–Gries candidate learner, then recount those candidates exactly using retained records. Compare descending frequency ranking with reversed-frequency order and the guaranteed zero-coverage exact retained lookup. Measure macro any-answer Hits@1/10 and first-correct reciprocal rank. Masked answers are never training features; model snapshots and per-query outputs are never saved or uploaded. Real data is ephemeral and source digest verified.

This is only an inexpensive learned non-neural heuristic; **it is not the strongest conventional control** and cannot establish true answer identifiability or scientific headroom. Future serious claims require separate preregistered fully trained KG embeddings / symbolic path controls, matched action and whole-process budgets, cold restoration, novel weight updates and disjoint first-use evaluation.

Implementation and negative tests are isolated to WSP-104, G29 generated files, and its own workflow. Preserve the earlier first failed DEV test receipt (test-harness duplicate keyword only). No controller, queue, scheduler, private runner, paid API, main, accepted model, merging or deployment.
