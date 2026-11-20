# Gate 18 — Strictly withheld intervention-combination generalization

**Contributor science: bounded finite-domain unseen-action generalization signal, NOT structural self-assembly superiority or native Yggdrasil acceptance.** This is not a merge/first-use request.

## Evidence and custody

- [Frozen preregistered experiment](./prereg.json), source-before-outcome commit `666a5ef577186e2ca94998f523c6b07de9c053cc` (blob `bb31fad85f74d4760cb1ef1c7e5aa9a59bed2d88`).
- [Executable frozen source](./run.cjs) committed `e7ed73a4056cf27fcb283bf1b7f06f5c4052856b` (blob `c89e088a07f618837e798c28d1555b906c38d10c`) before any Gate18 scoring.
- [Sealed primary result](./result.json), exact deterministic re-evaluation before commit `3cbb1d107aca514e9f1dedff8d617315a98e4117` (blob `7b040d256d5048c97de0ac8073029a1ef35db6c5`).
- [Independent mathematical audit](./audit.cjs) checks exact source record sizes/thresholds, pair statistics and an analytical *nonidentifiability* counterexample; it does **not** reimplement the full learner independently.
- [Provenance](./provenance.json) separates development source, engineering CI, scientific limits and authority.

Reproduce using Node.js only:

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate18/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate18/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate18/audit.cjs
```

## Frozen protocol and strict split

Gate17 trained on all 32 possible intervention vectors, so it could not demonstrate action-vector holdout transfer. Gate18 uses the *same exact Bayesian and compact generic learner families* but randomly splits the 32 possible five-bit intervention action IDs into **24 training-only and 8 strictly held** per seed/context. The action shuffle is independent of true source mask/table and noise. Four independently shuffled 24-action training rounds make exactly **96 action/label observations per world**; the held eight actions were not used during *any* fitting or training-only validation. Held outcomes use a separate noise domain. Each policy receives the same training data and 388-byte saved-evidence budget.

Fresh cohort seeds: majority `71000..71047`, MUX `72000..72047`, random essential 3-input Boolean `73000..73047`, 3-parent XOR parity `74000..74047`, pair `75000..75047`, unary `76000..76047` and independent fair `77000..77047`. Total **336 seeds / 672 source worlds / 64,512 training outcomes / 5,376 held action outcomes**.

Baselines: fixed full 1/2/3-parent subset classifier of equal persisted size, truncated one/two-parent classifier, parity-only model, Laplace 32-action table (each held action unseen, so p=0.5), exact Beta-binomial Bayesian subset mixture with extra computational scratch but equal persisted raw records, and p=0.5 null. Three-parent functions are newly sampled each trial; no hidden source labels, operator identifiers or true parents are provided to learners.

## Held-out Brier on NEVER-SEEN full intervention actions (lower is better)

| Source family | Compact adaptive | Fixed full same-state | Truncated 1/2 order | Direct action table | Bayesian subset averaging |
|---|---:|---:|---:|---:|---:|
| Majority of 3 | **0.0696577840** | 0.0696577840 | 0.2058736084 | 0.2500000000 | **0.0694289608** |
| MUX 3 | **0.0632830046** | 0.0632830046 | 0.2209261136 | 0.2500000000 | **0.0593835801** |
| Random essential 3-input function | **0.0768013733** | 0.0768013733 | 0.1717683844 | 0.2500000000 | **0.0635137351** |
| 3-input XOR | **0.0591904939** | 0.0591904939 | 0.2660387816 | 0.2500000000 | 0.0591904939 |
| Pair XOR | 0.0498818445 | 0.0498818445 | 0.0498818445 | 0.2500000000 | 0.0501252120 |
| Unary | 0.0578581154 | 0.0578581154 | 0.0578581154 | 0.2500000000 | 0.0584828660 |
| Independent fair noise | 0.2542462776 | 0.2542462776 | 0.2542462776 | 0.2500000000 | 0.2570588786 |

**Positive:** The generic causal-subset learner predicts 8 unobserved five-bit actions per world substantially better than direct five-bit action memorization. Paired improvement vs flat: majority **+0.1803422160** (95% normal CI **[0.1676832543,0.1930011776]**); MUX **+0.1867169954** ([0.1714829454,0.2019510455]); random essential **+0.1731986267** ([0.1583620555,0.1880351979]); parity **+0.1908095061** ([0.1812977498,0.2003212624]). All frozen action-generalization thresholds pass. Exact source parents recovered 94/96 majority, 95/96 MUX, 76/96 random essential and 96/96 XOR.

**Critical matched-control FAIL:** The equally compact fixed full causal-subset model makes exactly identical predictions across all seven held-out families and **every one of 336 seeds**. Dynamic model's paired Brier gain vs fixed is **zero, CI [0,0]**, failing both structural-superiority gates. It is not qualified self-assembly. Bayes does better on random essential functions by **0.0132876382 Brier** (paired 95% CI of adaptive minus Bayes [0.0068650128,0.0197102635]); it passes the frozen 0.02 deficit ceiling but is still a stronger control. The fixed nonlinear representation's advantage over flat memorization is **not unique** to adaptive construction.

**Identifiability limit:** Training omits eight entire 5-bit action vectors but often covers every *three-parent input pattern* through other action vectors that share the relevant three input bits. In **8 held observations** across all seven cohorts, the true-parent pattern itself was absent from training—4 random essential and 4 parity held outcomes. In each such case adaptive, flat and Bayes Brier was **0.25**, chance-level. The [independent audit](./audit.cjs) also exhibits two *essential-three-parent* Boolean truth tables producing indistinguishable labels on all training interventions when one parent input bin is excluded, yet opposite outcomes for that bin. Thus prediction on unseen full action vectors is **not** discovery of unobserved truth-table bits. This explicitly limits the science claim.

All 336 seed trials passed strict train/held action-set disjointness, deterministic exact result replay and 388-byte compact prediction restoration. Persistence across process termination, new input dimensions, native checkpoint continuation, causal intervention planning, interference resistance and long-term accumulation **remain untested**. Timed primary local V8 source replay was 10.039s, not a platform-controlled efficiency benchmark; feature-fit comparison counts exclude all prediction overhead and physical memory.

## Disposition

**ENGINEERING:** Frozen protocol → source → primary result → sealed receipt; independent audit and existing full repository Linux/Windows CI required to close engineering.

**SCIENTIFIC:** **Bounded unseen-full-action development signal.** Structural superiority definitively fails equal-size fixed control; Bayesian advantage persists on random nonlinear rules. New-parent-pattern inference is not proven and in several cases unidentifiable. Native Yggdrasil intelligence/transfer claims are NOT verified.

**DEPLOYMENT:** No accepted model, central Amalgam learner or native checkpoint modification, merge, scheduler or first-use. PR #1340 stays DRAFT. Next candidate must show cumulative retained causal knowledge under controlled **environment shift** and avoid trivial reuse of training parent-bin coverage, comparing fully trained controls and cross-process state restoration.
