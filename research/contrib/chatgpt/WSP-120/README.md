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

## WSP-120 conventional comparator qualification (source-safe only)

The predeclared 64-hidden-state GRU is implemented in `trained_gru.py` using
CPU PyTorch 2.10.0, fixed optimization seeds 120901/120902/120903, Adam
at learning rate 0.01, at most 2000 epochs per seed and a training-only
cross-entropy ceiling of 0.01 with 100% training accuracy. The training
inputs comprise only the visible graph (UNKNOWN edges explicit) and
the learner's already verified responses; held-out endpoints and source
laws are never inputs or selectors. All three seeds run and the best
converged checkpoint is selected by **training loss only**. Nonconvergence
means an invalid conventional comparison, not numerical superiority.

The additional `test_trained_gru.py` uses only disjoint world 120900;
the public 120000..120023 and reserved 120800..120863 worlds remain
unopened. This is **not** a scored scientific result. The GRU's model
parameters, inference time and full training time must be counted against
numeric and symbolic whole-process resource budgets. There is no
permission here for original first-use, native integration, or merge.

## WSP-120 guarded fixture-only evaluation plumbing

The isolated `fixture_evaluation.py` module and `test_fixture_evaluation.py`
now exercise **only** the independent engineering world 120900. The API takes
no external world/seed argument and rejects any non-fixture world, so it
cannot itself open the unconsumed 24-world scientific cohort. It evaluates
five independently instantiated arms (numeric active, numeric passive,
numeric fixed3, independent symbolic active and no-update), enforces equal
verified source-call budgets, preserves source-label receipts, checks cold
snapshot/restore for every numeric arm, and reports held predictions with
abstentions and wrong-confident predictions separated. Deterministic
receipt hashes exclude nondeterministic timing. Wall-clock time is recorded
diagnostically but does not yet constitute whole-process matched cost.

The conventional GRU can only be invoked through this harness with 32
observations and gets exactly the numeric passive arm's verified evidence.
Failure to converge is explicitly an invalid comparison, not a numerical
win. This source-safe engineering fixture does **not** constitute
independently qualified scientific first-use, cross-world retention,
energy measurement, native admission, or evidence of invented operators.
The preregistered scientific first-use authorization flag remains false.

## Maximum-budget fixture and batched GRU scoring — source-safe engineering

At the exact pre-archive candidate `2a660159ce9bc211834a2a52a9106ab6693a236f`,
[existing dual-OS run #43782619052](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43782619052)
completed successfully. It exercised the full `run_fixture(exposure=32, tier=384,
family=0, include_gru=True)` path on **only** engineering world `120900`,
checking all five evidence arms and the fully trained three-seed conventional
GRU. The comparator converged on the fixture and emitted 24 held predictions.
The scorer now calls the GRU in batched mode and rejects mismatched prediction
counts; source-safe regression tests cover abstentions, wrong-confident answers
and batched shape failures. Scalar scoring was a real preflight defect corrected
before any original scientific first-use.

These are engineering fixture checks, **not** original 24-world scientific
scores, matched scientific cost, multiworld independent reproduction, invention
of unfamiliar primitives, accepted native model benefit or promotion. Original
worlds `120000..120023` and reserved `120800..120863` remain unopened.
The separately controlled `scientific_first_use=false` boundary is unchanged.

## Engineering commands

```console
python -B -m unittest discover -s research/contrib/chatgpt/WSP-120 -p 'test_wsp120.py' -v
python -B -m unittest discover -s tests -p 'test_*.py' -v
python -B scripts/build_code_atlas.py --check-if-present
```

Unit tests use only the isolated engineering source `120900`, not the unconsumed original public cohort. A successful unit test is not a primary science result or final source-archive acceptance. No new controller, scheduler, paid service, research runner, merge, accepted-ref update or automatic native integration is authorized by this contribution.

Source-safe development qualification (before G29 archive): [run 43777178612](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43777178612) passed the six WSP120 engineering fixtures on each of Ubuntu and Windows. Full inherited regression remains required **at the exact post-G29 archive SHA**; do not infer science or admission from this checkpoint.
