# CVH-03 — exact original causal MDP source factory, zero physical actions

**Engineering status: source-free tests PASS and genuine upstream constructor-only integration PASS on Windows and Ubuntu. Full exact-final repository regression and G29 are separate gates. SCIENTIFIC: UNVERIFIED. DEPLOYMENT: NONE.**

## What changed that was missing before

An existing separately qualified third-party source path is already in the repository, and it must not be rebuilt from scratch:

- [FKP-24 #1120](https://github.com/spoonman136668-ai/Yggdrasil/pull/1120) pins the unchanged original Apache-2.0 CausalAILab/Causal-Gymnasium repository at `c94e9a4cd3641588b6b8507e71ccee5c27032bdf` and its original 16 original core/MDP source blobs through FKP-25. Its `public_mechanical_episode(source_factory,policy,seed,...)` is strictly **action before observed public reward** and deliberately never sends private `info`, the source object, unobserved labels, or counterfactuals to the learner.
- [FKP-25 #1122](https://github.com/spoonman136668-ai/Yggdrasil/pull/1122) qualifies constructing the actual **unchanged upstream MDPPCH**, but through targeted in-memory namespace containers replacing only eager unrelated top-level package imports. It is not a verified whole upstream package installation or an actual source `reset/do` experiment.
- [CVH-02 #1130](https://github.com/spoonman136668-ai/Yggdrasil/pull/1130) already has a tokenless/public `choose/observe` learned-return policy and exact inherited FKP24 adapter **mock-only** integration, qualified with full Python/G29 on Windows+Ubuntu in [run #43860636081](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43860636081): 54/54 root, 11/11 CVH01, 13/13 CVH02, 240 completed mock episodes per policy and 7,440 fabricated public callbacks total.

**The actual missing engineering seam:** allow a *trusted source-side adapter* to acquire a fresh unchanged original MDPPCH object via the FKP-25 targeted verified source import, without invoking the unqualified upstream package's eager broad imports, and shut down the factory safely when the pinned import scope ends. This project adds that **factory provider**, not yet an action executor or new causal learning algorithm.

`source_binding.py` returns a context-scoped callable `verified_original_factory(clean_pinned_checkout)`. It first checks the exact original Git commit/16 original blobs and package-version pins, imports only original core/MDP classes while bypassing two unrelated package initializers with temporary namespace modules, and yields a callable which creates a **new original MDPPCH(max_step=30,Task(LearningRegime.do))** each time. The factory refuses future use after its context closes and removes the temporary original module namespace on exit, including failure. No original source code or learner, SCM, PCH, task type, `do`, `reset`, or reward implementation is copied, monkeypatched or silently mocked. **This is not a secure process boundary**; independent scientific source isolation must use an authorized source service with appropriate permissions.

`probe_constructor.py` deliberately constructs two original MDP objects, proves both are fresh class-identical source objects and constructor effect counters are zero, then closes the factory and proves stale use is rejected. Its `--source-action` flag **always rejects before loading any source**. No actual original source worlds or target/evaluation seeds are consumed.

## Frozen source and qualification results

Preregistration-only **FIRST commit `956f017a73b9d55d595535c390db791db4d18456`** preceded implementation and tests. All new code and 16 source-free tests committed before first test/constructor at **`e0b1ffb7b50f5bda7fba437a522b6077e6fee8d5`**, based on exact CVH-02 qualified SHA `ae61ecdf535e5c4de35ea48f1223a7afe871a09b`.

The original source-binding module Git blob is `7d38d861044d844f4bd8f59c1e234c4d7f01ee76`, **unchanged after all results**. The first read-only [source-free CI #43929834593](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43929834593) passed **16/16 Ubuntu** and **15/16 Windows**: Windows checkout was converting `LF` to `CRLF`, correctly failing the exact inherited FKP25 blob check. A **CI-only** `git config --global core.autocrlf false` before checkout fixed that infrastructure setting; [final source-free run #43930029985](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43930029985) **PASS 16/16 both OS**.

The first genuine original constructor [CI #43930336729](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43930336729) fetched the exact original clean Git SHA and exact pins, then constructed two real unchanged objects. The subsequent diagnostic attempted to access private `obj.__class__`, which the original upstream PCH **correctly denies**. It is a **test-harness interface error, not a source-world/model failure**. The only harness correction at commit `97833d7624cb905da99afe8dda58f5e292075e48` replaced that diagnostic with the builtin `type(obj)`. The actual factory source, upstream source, prereg, public policy, allowed seeds, outcome budgets and scientific thresholds remain unchanged. The failed run used **zero** original `reset` or `do` actions.

The corrected [original-constructor-only CI **#43930592515**](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43930592515) **COMPLETED SUCCESS** on both Windows 2022 and Ubuntu 24.04, Python 3.12, pinned exact original 16 Git blobs, and direct dependencies:

| Qualification | Windows | Ubuntu |
|---|---|---|
| Exact original upstream SHA and clean Git tree | PASS | PASS |
| Exact source 16 Git blobs and direct pinned packages | PASS | PASS |
| Two separate original MDPPCH constructors | PASS | PASS |
| Post-context original factory reuse refused | PASS | PASS |
| Original `reset` calls | **0** | **0** |
| Original `do` interventions | **0** | **0** |
| Protected 996100/996500/996600 source seed first use | **0** | **0** |

Cross-platform identical canonical receipt SHA256: `b7ba99d127f57339f549cdb413111e7b01dc9426c5d1864670e7e7d2c5969214`.

### Reproduce *without* accessing external source

```sh
python -B -m unittest discover -s research/contrib/chatgpt/CVH-03 -p 'test_*.py' -v
python -B research/contrib/chatgpt/CVH-03/probe_constructor.py --checkout /missing --out /tmp/never.json --source-action  # MUST refuse
```

The actual original-constructor one-shot workflow (external original source clone with original read-only SHA and standard-library-only test driver) is preserved as CI evidence, not integrated into the accepted runtime. The full root regression and source-derived G29 must qualify the **final** CVH-03 research SHA on both Windows/Linux separately.

## Authority and research decision

**ENGINEERING:** Original unchanged causal MDP can be delivered as a bounded, previously source-qualified factory to the source-facing trusted adapter shape, instead of requiring whole-eager upstream optional environment imports. Every construct is still pre-action, not a source trial or training event.

**SCIENTIFIC:** **UNVERIFIED.** No original CausalGym public `reset/do` happened, no earned rewards were learned, no full source-blind interface action isolation was established, and the existing CVH01 independently implemented conventional return estimator still ties on mocked public records. This does not demonstrate autonomous causal discovery, unfamiliar transfer, actual trained conventional superiority or native cognition integration.

**DEPLOYMENT:** **NONE.** Isolated research draft remains unmerged; accepted Yggdrasil main, owner-controlled native runtime, Forge/Wingless/Hybrid, full historical fact image, controllers, runners and scheduled tasks unchanged.

**Next independently authorized first-use:** original external source mechanical TRAIN seeds `996100..996103`, at most 32 actual binary `do` interventions each, with FKP24's only-public consequence adapter, original unchanged CausalGym code, CVH02 existing policy, and strongest separately pretrained/fully trained conventional controls at matched action/compute budgets. This step must be admitted by the **project-scoped source owner** with complete non-replay first-use custody and source-private process boundary. Protected DEV `996500..996531` and TRANSFER `996600..996663` remain closed. Neither ChatGPT next-gate shorthand nor GitHub CI by itself grants that authority.
