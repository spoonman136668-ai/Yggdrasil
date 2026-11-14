# WSP-103 — historical TRAIN-only structural headroom audit

**Stage:** DEV source task audit only; not a learned weight mechanism, not evaluated scientific performance.

**Parent qualified WSP-102:** `b31875fa8306eb13a742d103cfb08f6273916e1e`, tree `9796106766b0a6ed844f90e254829f8988ca840e`.

**Frozen-before-code prereg:** `e9c7e396d8229a3d8296b072e3474bcdc9543498`. It fixes the 1/32 full subject–predicate group holdout and the lowest-priority 4,096 query groups, across all **21,343,681** rows in the independently sealed historical mirror's `train.txt`. This is **not** the canonical Wikidata5M heldout benchmark.

The auditor makes three read-only passes over the **training member only**: verify original source count/bytes/SHA; enumerate complete target multisets for preselected groups; then measure retained-side subject/object incidence while excluding every heldout group. It reports only aggregate counts, timing, and a SHA of query-plus-answer identities. It does **not** train models, evaluate predictive accuracy, read official validation/test facts, or modify Yggdrasil's accepted weights.

A source-query that has both endpoints represented in the retained graph is **not proven identifiable**. The future independent conventional and exact-symbolic controls must establish substantive learnable headroom before any direct-weight method can claim a benefit; keep all negative results. Preserve the WSP-101 H03 ceiling finding unchanged.

Provenance: source mirror compressed SHA `ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878`; training SHA `2ef1a279f6393a8edfbb2b44114a2c97944272e5fe2a1bd2a7cbe48f94742f1a`.

**Isolation:** This stacked draft branch leaves WSP-102, WSP-101, Yggdrasil main/model, FORGE and CKB controller, protected first-use cohorts, private runners, paid APIs, schedule, accepted refs and deployment unchanged.
