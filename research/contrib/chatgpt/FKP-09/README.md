# FKP-09 — Actual shared-core causal weight repair under incompatible contexts

**Independent Yggdrasil contributor research, never a native acceptance or production change.**

This is a distinct follow-up to [FKP-08 #1099](https://github.com/spoonman136668-ai/Yggdrasil/pull/1099) and the already-qualified [ST9 #1087](https://github.com/spoonman136668-ai/Yggdrasil/pull/1087). FKP-08 learned append-only revision patches without ever changing the shared causal base. ST9 repaired an 8-feature **single within-family** causal law, with independent active conventional GF2 controls matching it. Neither established a compact repair mechanism that **actually changes shared synapses** yet preserves previously learned *mutually conflicting* contextual laws.

## Frozen source and original test

Protocol was committed **alone before implementation and original DEV outcome** as `research/contrib/chatgpt/FKP-09/prereg.json`, first SHA `63fac40726d6ec2fe49fc5f78aebf6d2d97260bf`. Source protocol SHA-256 `f5e32854fb5d179b33f06c51250c6d15b9db0b84e3e2679955f2d8848a9077c8`. Accepted Yggdrasil main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` is the unchanged research parent.

A world consists of **128 binary causal factors** and a hidden 128-bit shared causal coefficient vector, learned from exactly **128 genuine one-factor source interventions**. Sixteen new contexts have **different fixed 2-coefficient causal edits**. Each context yields 128 public candidate 128-bit intervention masks and 128 genuinely disjoint held masks. The learning methods observe only **32 true public action–consequence pairs** per context and must predict held consequences. The source privately knows actual edits; model APIs never receive them.

After learning the 16 context-specific laws, the source's shared 128-bit core changes three times. Each change flips two unknown causal factors and is learned by **128 new independently paid one-factor observations**. The model updates the **same shared core weights**, then adjusts existing sparse context adapters by XOR compensation. If an update would require more than eight adapter coefficient indices for any context, it must abort atomically rather than silently overwrite past knowledge. Fixture-only stage 4 introduces a much larger 16-flip shift and must reject the update.

All prior context predictions are sealed **before** any shared-core update, and checked again after every update and after a cold SHA-256 integrity-restored checkpoint. The candidate cannot store full 128-bit laws separately for every context. Fixed raw learned state is **16 bytes shared core + 16 contexts × 8 byte-sized sparse adapter slots = 144 bytes** (plus checkpoint header and digest, all reported). A full conventional exact per-context coefficient cache needs **256 raw bytes**; an equal-information conventional sparse-delta algorithm can use the same 144 bytes, and must be given full credit for a tie.

The strong Bayesian control independently enumerates **C(128,2)=8,128 causal edit hypotheses** on exactly the same action observations. Original source identifiability compares this strong reference after 12 vs 32 of the *same* genuinely observed 32 consequences (no extra paid queries). Frozen DEV source condition: 32-action accuracy ≥0.98 and improvement ≥0.05 versus the 12-action strong reference. All model predictions are built **before** the DEV-only held evaluator reveals true hidden consequences.

Public DEV contexts `900..915` are original first-use only. Pre-DEV tests instantiate only **fixture** contexts `850..853` and synthetic independently authored vectors; they do not open DEV held labels. Owner-private protected primary `1900..1963` and protected negative `2900..2915` remain unopened; their external private source key is never committed to repo or passed to models. Original synthetic DEV source and learner are in the same Python process, **not** an independent cryptographically blinded scientific evaluator.

## Reproduction at source SHA

```console
python -B -m unittest discover -s research/contrib/chatgpt/FKP-09 -p test_fkp09.py -v
python -B research/contrib/chatgpt/FKP-09/run_dev.py
python -B scripts/build_code_atlas.py --check-if-present
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

A later run of the 16 once-consumed original DEV contexts is **engineering replay**, not independent science. Full exact-source and atlas G29, original DEV statistics, 5 fixture-only focused tests and final inherited regression must qualify on both Ubuntu and Windows, source blobs/tree pinned. Missing qualification is UNVERIFIED, never implicitly a PASS.

## Decision rule

The defined **DEV mechanism gate** requires correct actual shared-weight rebase, 16/16 previously learned contexts preserved bit-for-bit after each of 3 rebase stages, a correctly fixed **144-byte** raw capacity, exact cold restore, and atomic rejection of the stage-4 overcapacity shock. DEV source headroom is independently checked. These are engineering/source feasibility results only.

An actual novel **scientific superiority** signal requires ≥5 absolute points held improvement over strongest same-information Bayesian/conventional references with a positive context-paired 95% bootstrap lower bound, or equal accuracy within 0.5 points and ≥2× **whole-process** CPU/wall+memory cost benefit. Tying an equally informed **sparse-delta conventional** model, even at 144 bytes, is **NO-GO** for unique native learning advantage. Do not tune this source after revealing its DEV results or call synthetic deterministic law fitting AGI, autonomous law invention, or out-of-family general intelligence.

Neither main nor the production research loop, sibling models, CKB-plane, protected evaluator, paid APIs, schedulers, accepted native weights or accepted refs are changed.

## Frozen original public DEV result (2026-11-15)

The separate source-only experiment has now completed at **original SOURCE SHA `8d7284b740910db7a4d90318ce40f09aa70ef229`** (Git tree `307162ffdf233ea584ff2226d3d6ebc61be3bb60`) and its strictly generated-only G29 child `c05318d7f4144e58952f3444e8876f78e9426e4f`. The original one-shot [CI run #43725770531](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43725770531) passed on Ubuntu and Windows. It required source-custody, G29, fixture-only FKP09 and full inherited regression to succeed on **both** platforms **before** the first original DEV evaluator ran on Linux; Windows then replayed consumed public DEV deterministically. Both OS: G29 focused **4/4**, source fixture **5/5**, inherited root regression **54/54** PASS, and clean worktrees.

One earlier pre-DEV [run #43725656904](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43725656904) correctly stopped at a *fixture test expectation* (source raised unauthorized-stage `PermissionError` instead of the test's `ValueError`). The **test only** was corrected before original held outcomes, with unchanged source/model/run logic/prereg and fresh full exact-source qualification on both OS. This infrastructure repair is not an additional scientific attempt.

**Original 16 DEV contexts 900..915, each receiving 32 genuine context intervention outcomes plus four global stages of 128 genuinely observed base-bit outcomes = 1,024 total source observations.** Held evaluation scores 16×128=2,048 disjoint binary outcomes/arm; after each of three genuine shared-core changes all original context predictions were audited again. Original score:

| Learner | Held exact accuracy |
|---|---:|
| **Fixed-capacity 144-byte shared-core and real numerical weight rebase (candidate), 32 actions** | **100.0000%** |
| Independently refit exact Bayesian posterior, same 32 actions | **100.0000%** |
| Conventional full 128-bit context-law reference, same observations | **100.0000%** |
| **Conventional equal-information exact sparse delta, 144 bytes** | **100.0000%** |
| Exact Bayesian posterior after only first 12 of same actions | 73.1445% |
| Shared-core only, without context learning | 50.5859% |

The source-identifiability preflight PASSES: strong 32-action held reference 1.0 minus strong 12-action held reference 0.7314453125 is **+0.2685546875**, well above the frozen minimum +0.05. No extra source feedback is used to calculate the 12-action reference. The candidate outperforms the 12-action reference by the same 26.86pp (paired-context bootstrap CI95 `[0.22314453125,0.3037109375]`), and the no-context control by 49.41pp (`[0.46923828125,0.51611328125]`). However, **all three matched strong conventional controls tie the candidate exactly** with zero accuracy delta and zero CI range. Engineering PASS and authentic source headroom do **not** imply unique scientific superiority.

**Real shared-weight repair**: exactly two shared causal synapses changed at each of three independently paid global updates; the model directly mutated its learned 128-bit core and rewrote only bounded compensating *indices* in all 16 context adapters. Every previously learned context remained bit-identical after all three updates: **16/16, 16/16, 16/16**. Raw memory **144 bytes**; validated SHA-256-cold checkpoint **180 bytes**; both cold re-prediction and tamper rejection PASS. A fixture-only catastrophic 16-bit global shock exceeded eight adapter positions and was rejected **atomically without changing the existing checkpoint**. This demonstrates **bounded simultaneous contextual retention under actual shared weight changes**, but only within the known 2-bit-edit family, and does not establish out-of-family reasoning or native Yggdrasil plasticity.

**Scientific outcome**: `DEV_NO_GO_EQUAL_INFORMATION_CONVENTIONAL_TIE` / `SCIENTIFIC_PASS=false` / `NATIVE_INTEGRATION=NONE`. A conventional sparse-delta representation requires the **same 144 raw bytes** and provides the same predictions and rebase behavior; matched whole-process comparator cost is UNVERIFIED, so **no 2× efficiency claim**. Original DEV is now consumed and must not be retuned. Read `result.json` and `provenance.json` for source SHA, original-run receipts, negative controls and scope. Further qualification runs only reproduce this already-consumed public DEV. Protected owner-primary and owner-negative cohorts remain unopened.
