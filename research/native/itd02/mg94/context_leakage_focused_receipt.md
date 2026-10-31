# MG94-AI focused regression correction and reproduction

**Source commit:** `1618907a36a99b90a8b76ebbf835fd808ab7aff9`
**Corrected test blob:** `bac15efb61d9a40049a5087f67613758eed3303a`
**Classification:** SYNTHETIC ENGINEERING DEVELOPMENT ONLY.

Confirmed source defect: TRAIN context prefixes are `(0,1)` and `(0,0)`; HELDOUT prefixes are `(1,0)` and `(1,1)`. Intersection is empty. The preceding source asserted nonempty intersection and was incorrect.

Corrected test: assert disjoint prefixes, but do not infer independent transfer from synthetic disjointness. The contextual control defaults to routing disabled in all evaluation contexts.

**Focused result:** 6/6 PASS in an isolated Linux Python reproduction of the relevant source logic/tests. This was a source-derived standalone reproduction, **not exact-blob source execution** or official GitHub Actions. Unrelated full regression NOT EXECUTED. Original-world scientific experiment NOT EXECUTED. Native benefit NOT DEMONSTRATED. No acceptance or promotion.
