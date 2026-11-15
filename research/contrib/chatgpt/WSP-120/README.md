# WSP-120 — Grow relation structures from verified contradictions

**Isolated research contribution, NOT accepted Yggdrasil model code.** The accepted `main` is `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Parent: frozen WSP-119 PR #1112 at `618e005cce477eaa01fc4191cea997e44f669825`; its scientific NO-GO remains intact.

## Frozen source and status

- Initial preregistration commit: `afbec2ce5e25cac09001d00ff1bb777838b7a937`.
- **Before implementation or source use**, corrected the full-background edge count from 256 to 384 and set nested tiers 192/288/384: `65393f50007de24cc8611eeda27d2e725d3633bc`. No observed outcomes motivated this correction.
- Primary public synthetic cohort: 24 worlds `120000..120023`, with three relation families per world: a four-hop chain, a five-hop chain, and a parity-conditional choice between two distinct two-hop paths.
- Primary/source outcome first-use **NOT RUN**. Reserved seeds `120800..120863`, protected science, Wikidata and official datasets never accessed. Engineering fixture seed `120900` is disjoint from the primary and reserved cohorts.
- This stage implements the guarded generator, numerical structural expansion, independently coded exact symbolic grammar control, cold-integrity tests and source-safety checks. **Trained GRU comparison, full primary scoring, interference/retention study, cost normalization and scientific acceptance remain NOT RUN**.

## Why this test differs from WSP-119

In WSP-119 all 216 three-hop programs were supplied as candidates from the start. In WSP-120 the numeric learner initially knows only those 216 candidate forms. Contradictions from actual requested source consequences may eliminate them all, at which point it allocates new numerical candidates representing length-four/five compositions and a conditional branch, then **replays only already verified observations** into the new counters. This is bounded, no-gradient, content-addressed evidence-based *structural growth*, and it can be persisted/restored. A fixed-grammar numeric ablation cannot expand.

The equal-information symbolic control independently searches the full same grammar from the start. If this symbolic method matches or beats the numeric learner, **do not claim a uniquely numerical or emergent scientific advantage**. The primitive relations, composition operator, parity condition and branch construction are all provided in code. No arbitrary new primitive was invented. No actual source answer is available to an active query selector until after it chooses that source.

## Frozen budget and success boundary

64 entities; six primitive relation permutations; at most 32 legal verified source queries per world/family/coverage/arm from a pool of 40; 24 held subjects unavailable to querying. Graph visibility: 192, 288, 384 of 384 primitive edges. Score 0/4/8/16/32 observations. Full grammar has **10,548** candidate structures, capped at 16,384, with at most 131,072 bytes of learned signed-int32 support/contradiction weights.

Predeclared public diagnostic requires at 384 known primitive edges, 16 source observations, numerical active >=60% held endpoint accuracy and >=15 percentage points above fixed-three-hop, paired lower confidence bound >0, zero confident errors, intact cold state. This can establish only bounded known-grammar extension. Strong scientific acceptance additionally requires independently qualified unseen-law families, strongest exact symbolic and fully converged GRU controls, cold/interference tests, complete whole-process costs and independently witnessed first-use, all under preset thresholds. Do not reclassify an untrained control as a victory.

## Engineering commands

```console
python -B -m unittest discover -s research/contrib/chatgpt/WSP-120 -p 'test_wsp120.py' -v
python -B -m unittest discover -s tests -p 'test_*.py' -v
python -B scripts/build_code_atlas.py --check-if-present
```

Unit tests use only the isolated engineering source `120900`, not the unconsumed original public cohort. A successful unit test is not a primary science result or final source-archive acceptance. No new controller, scheduler, paid service, research runner, merge, accepted-ref update or automatic native integration is authorized by this contribution.
