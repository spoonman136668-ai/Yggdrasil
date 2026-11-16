# SFI-04 — information needed for new causal relationships

**Decision: STRUCTURE-FREE NO-FREE-LUNCH CONTROL CONFIRMED; unique native method superiority NO-GO.**

The original public experiment is recorded in `result.json`; exact Git blob, source and replay receipts are in `provenance.json`. Preregistered **first** at commit `0afc389fb461ce3f7381dafd6e3d64ebba6a38d1`. Python code and test files were authored locally prior to observing the first result and archived byte-identically at Git commit `fc0df31583c1d386a8b855e1d9508ab05230ca52`. The initial test run was locally executed, not repository-wide CI.

## Controlled falsification

32 new **public synthetic** worlds `880400..880431` each contain an independently drawn arbitrary map from 128 intervention contexts to one of eight rewarding actions. There is deliberately **no transferable relationship between different contexts**. Each world repeats a common source-defined 128-context public action tape, exploring 24, 128, 512, 1,024 and 2,048 actual actions. Reward for an action arrives **two steps later**, with source-private correct labels never passed to the learner. At each checkpoint, the frozen learner proposes one action in each of 128 contexts; a **read-only evaluator** scores actual source consequences without feeding test outcomes back.

Direct local weight programming stores 128 action-exclusion masks, one byte per context. A separately implemented conventional exact categorical Bayesian learner sees **the same public feedback and action sequence**. Shuffled-credit and no-update controls expose information leakage or memorization. This is an off-policy common-source diagnostic, **not a real agent autonomously selecting its training interventions**.

| Common public actions/world | Direct-weight accuracy | Exact Bayesian accuracy | No-update |
| ---: | ---: | ---: | ---: |
| 24 | 14.2822% | 14.2822% | 12.1582% |
| 128 | 24.6094% | 24.6094% | 12.1582% |
| 512 | 62.2070% | 62.2070% | 12.1582% |
| 1024 | 100.0000% | 100.0000% | 12.1582% |
| 2048 | 100.0000% | 100.0000% | 12.1582% |

After **24** actions only 22 delayed consequence labels have actually arrived. At least **106 of 128 contexts remain unseen**, and direct-weight accuracy on those unseen contexts is just **407/3,392 = 11.9988%** versus chance **12.5%**. Even *granting perfect identification on all 22 seen contexts*, the **expected** whole-context accuracy ceiling under independent uniformly random remaining labels is `(22 + 106/8) / 128 = 27.5391%`; actual binary evidence is weaker still.

The direct learner ultimately memorizes every context's correct action after exhaustive evidence; so does the conventional Bayesian learner. The fully matched result is **0.0 accuracy advantage** on all worlds/checkpoints, paired 1,000-resample 95% interval **[0,0]**. The preregistered superiority predicates fail.

**Interpretation:** A model cannot invent reliable action–consequence relationships among unrelated inputs without data or additional useful structure. Increasing programmed memory can accurately retain evidence but cannot substitute for causal generalization. This is a property of this controlled i.i.d. source distribution; it does not prove a universal limit on AI creativity or native Yggdrasil.

## Engineering and authority

- **7/7 focused source, receipt, delayed-outcome, budget, strong comparator and cold *prediction* restore tests PASS** on exact Git blob contents (Python 3.13.5 Linux), compilation PASS and complete non-timing deterministic replay PASS.
- 32 worlds × 2048 public actions = **65,536 training source actions**; 32 worlds × 5 checkpoints × 4 learner arms × 128 scored contexts = **81,920 read-only earned action evaluations**. Complete reproducible per-world correctness matrices and SHA-256 of full scored world records are retained in `result.json`.
- **Full final exact-source Linux/Windows regression/G29 and native acceptance remain UNVERIFIED.** Research-only branch, no new workflow definition or controller, no owner-private first-use, no paid API, no merge/native integration.
- No FKP-17 original held DEV `978500..978531` or TRANSFER `978600..978663` was opened; accepted main is unchanged.
- Raw direct mask 128 bytes is a logical state size, **not measured total process RAM/cost**. The local cold test restores prediction masks only, not the full custody checkpoint.

**Next useful research direction:** Test *structured* unfamiliar-world causal law induction where a model first learns primitive relationships from real consequences and then composes them into held-out combinations. Compare equally informed conventional models and fully trained recurrent controls, with genuinely disjoint law construction, real goals and prospectively frozen independent science. Repeating arbitrary lookup-table memorization is not a learning-mechanism discovery.
