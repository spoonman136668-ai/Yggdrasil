# CVH-04 — Real original CausalGym public rewards, retrospective tokenless memory

**Research-only and retrospective. No additional source actions, original first-use, owner activation, model promotion, merge or deployment.**

## What actually changed from CVH-03

FKP26 [draft #1158](https://github.com/spoonman136668-ai/Yggdrasil/pull/1158) executed a single authorized mechanical original-source Causal-Gymnasium run of 124 native `MDPPCH.do` interventions (four 31-step episodes, seeds 996100–996103), recording **66 actual public binary rewards**. It was not learning; it used an untrained fixed deterministic action policy. CVH01's independent `EarnedReturnMemory` was previously tested on made-up source-shaped records, and CVH02/CVH03 tested policy interface and original constructor but not CVH01's learning on these actual source consequences.

CVH04 **reuses CVH01 without code or parameter edits**, and **reuses CVH01's independently implemented exact conventional batch estimator**, for a strict frozen retrospective prediction and cold-retention test on those already-consumed public actions. The already-consumed FKP26 traces are part of a public repository, not a claim of blind prospective evaluation. No original third-party environment is imported, constructed, reset, stepped, or re-invoked.

### Original source and immutability

- CVH03 qualified parent draft [#1160](https://github.com/spoonman136668-ai/Yggdrasil/pull/1160), exact source SHA `0975c5d83aa9b0357735139cae3457338ec67027`, tree `d71539fff8867231753901d5275dd57edadc2ab0`.
- **Preregistration FIRST `d35ff1eb7afca66b586352eab988fcdbbd657569`**, before creating the new CVH04 learner evaluation or inspecting full held scores.
- Original source independently authored `CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf` (Apache-2.0), actual FKP26 GitHub Actions [#43930489602](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43930489602), candidate `f99552f29947767eb8764c68ba72518327c3d25c`.
- Original FKP26 ZIP [artifact #14257634107](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43930489602/artifacts/14257634107) digest `4c877a6df5685516cc7ba445b2b90c90afb3674537ab741fb67adb5453e5c9ef`. FKP26 full summary SHA256 `bdad1c832fd008746d7eb9ae2bc248e30ffa4be4a3e667209c6bfc33a0a93c22`.
- `consumed_public_fixture.json` is a compact, reversible **six-bit-per-observation representation of all 124 actual public rows**. Each decoded 31-row episode must rehash to the original source `public_transitions_sha256` **and** the independently frozen FKP26 public receipt SHA256. Every row retains exact state/action/reward/next-state/terminal/truncation bits. This preserves the small original non-private public source dataset durably in the repo after Actions artifact expiry, without calling the source again. It is not a substitute for public original source provenance.
- **KNOWN NON-BLIND LIMIT:** During FKP26 verification, all four episode reward totals and the first two source rows of each episode were viewed before this preregistration. The held episodes are **historical consumed data**, NOT virgin independently sealed science. No value can be called `SCIENTIFIC_PASS` from this evaluation.

### Frozen evaluation

- Train the unchanged CVH01 `EarnedReturnMemory` only on original public episodes **996100 and 996101**, 62 transition events. No DEV/TRANSFER source opens, and no new actions. Freeze the learned 36-slot numerical state and exact SHA256 cold restore.
- Held retrospective data: **996102 and 996103**, 62 already observed actions. For each row, determine only its observed public `(previous action,previous reward,current before,current action)` address; freeze candidate and conventional predictions for the entire episode before reading actual next-four-observed-reward targets. Do not fit from either held episode before its predictions.
- Each target = earned actual next **up to four** public rewards `r0 + r1/2 + r2/4 + r3/8`, respecting source truncation and no episode-boundary leak. This measures **prediction of returns under the fixed behavior policy**, NOT action selection, counterfactuals or causal effect of action.
- Fitted source-matched independent **strong conventional exact batch** `batch_public_returns` MUST tie native CVH01 at every supported prediction. Other controls: train-only global-return prior, exact per-address posterior shrinkage with frozen two pseudo-observations to the global mean, independent immediate-only ablation, and reward-rotated train-only invalid causal-sequence negative. Conditional and unconditional MSEs reported with separate denominators.
- The candidate **abstains** unless its address has at least two fully observed training returns. Report how many of the 62 held rows are supported. On unsupported rows, a separately labelled global-prior fallback is permitted strictly for the all-row utility diagnostic, never misreported as learned native knowledge.
- Post-evaluation separately continue the original snapshot with the **same already-consumed held observations**; require each original learned slot count/sum to be preserved, independent conventional 124-row parity and byte-identical restore. This is cumulative numeric retention, **not demonstrated durable generalized knowledge**.
- Frozen *weak development only* signal threshold: >=16 supported/62, candidate supported MSE lower than same-row TRAIN global prior by at least 0.01, cold source/strong exact control checks PASS. If not, preserve NO-GO. An equal fitted exact-control model means **zero** demonstrated scientific superiority regardless of internal learning result.

### Engineering qualification

Ubuntu24.04 and Windows2022 source-free same-model reproduction, negative tamper tests on the original public FKP26 hashes, CVH01–04 focused, the complete existing root suite, generated-only G29 source index and independent G29 verification on the identical final source SHA/tree. Stable metrics and source SHA must match both operating systems. Never claim source data use automatically authorizes a protected scientific first-use or a new model acceptance step.

**No tokens-as-cognitive-foundation, no copied donor architecture, no paid API, no new controller, no scheduler, no private source info or new runner, no merge/owner-admitted `main` changes.** Underlying native architectures and all sibling research drafts remain isolated. The next genuine new science requires a separately authorized, disjoint, prospectively held external source cohort and fully trained conventional and symbolic controls under matched actions, information and compute.
