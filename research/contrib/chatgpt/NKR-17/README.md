# NKR-17 — Audit every random intervention schedule, not one lucky seed

## Why

NKR-16 [draft PR #1153](https://github.com/spoonman136668-ai/Yggdrasil/pull/1153) proved that, on 12 deterministic already-studied positive-conjunction action worlds, selecting interventions by known-family information gain identifies **56/72** previously unprobed action-effect consequences versus **38/72** from one precommitted SHA-seeded random-action policy, at the same two additional public-action outcomes/world; no incorrect confident predictions and **384/384** old retention. An independently fitted exact symbolic information-gain controller **tied** the native planner completely. There is no established scientific superiority.

The next falsifiable objection is *random seed robustness*: a comparison to a single random control can overstate intervention value if the random controller happened to choose poor contexts. Instead of introducing yet more synthetic worlds and claiming novelty, NKR-17 computes the **complete finite random-choice reference distribution** over the original fixed cohort, then locates native active's 56/72 against that distribution.

This also separates scientific claims: another Yggdrasil [external MiniGrid experiment #1004](https://github.com/spoonman136668-ai/Yggdrasil/pull/1004) previously ran **8,016 genuine `env.step` actions** and had a negative primary result because **persistence outperformed the candidate** on both transfer families. That result is preserved, not rerun or silently substituted by NKR-16's synthetic success. NKR-17 is **retrospective source-safe development** on ALREADY consumed synthetic data; there is **no new independent scientific first-use**.

## Frozen FIRST prereg and exact parent

- Frozen **prereg FIRST commit `cb195797e737cba02e45038cddc27dd7bb9719b8`**, committed before writing the exhaustive analyzer, tests or inspecting resulting robustness statistics.
- Exact NKR-16 parent `4562b8b47a2309bec496cd3ad6420d9a0a349e6d`, tree `122ac8a789c3fb64e4f8517fd7bbaf30916ad83a`; NKR-16 [final CI #43918065047](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43918065047) passed **151/151** full root regression on Ubuntu/Windows and independent G29 on both.
- Accepted main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` unchanged. Original historical 21.3M image is not reread, no external authentic causal source, additional owner runner, schedule, paid model, controller or model activation.

## The entire finite control population

The original 12 source worlds are immutable; each has 8 withheld cold contexts `[6,7,9,11,12,13,14,15]`. The action chooser can select two **distinct** contexts with action=1 after the initial 16 action observations. A uniform without-replacement random policy has **8 × 7 = 56 equally likely ordered two-action sequences** per world. The 28 unordered pairs appear twice; order is kept because the original random policy is sequential.

`research/contrib/chatgpt/NKR-17/experiment.py` evaluates **ALL 56** ordered policies in **ALL 12** frozen worlds, 672 total policies and exactly **1,344** additional selected public action observations across those independent retrospective audits. For each policy, it:
1. Fits the same source-visible initial eight pairs, independently derives the parity action-zero baseline, and enumerates all **15** positive conjunctions from the published context bits. This independent implementation does not call the NKR-16 native policy or the NKR-12 symbolic fitter.
2. **Selects** each public intervention before invoking the fixed computational source environment; observes only the two actually selected action outcomes, filters candidate masks and records canonical source SHA-256 receipts.
3. Scores **only the six remaining unprobed action-1 outcomes**, never credits the selected public outcomes as a novel cold prediction and abstains when the surviving masks disagree.
4. Independently re-derives the greedy highest-entropy context choice after the first observed effect and verifies it matches the unmodified actual NKR-16 native action choices and final cold score, on each of the 12 worlds.
5. Separately executes the **unchanged original SHA-seeded random policy** at NKR-16 and verifies the exact earlier 56 and 38 headline correct scores. Preserves every original warm learned mechanism at **384/384**.
6. Combines 12 exact per-world 56-choice score histograms by **integer polynomial convolution**. There are `56^12` equally likely assignments of independent uniform random two-action policies across 12 frozen worlds. Report exact expected total, variance, quantiles, and **one-sided descriptive tail fraction** `P(random >= native 56)`. Also report the offline best among 56 pairs as an **oracle upper bound**, NOT a fair online comparator.

No Monte Carlo and no search for a friendlier random seed; the source and hypotheses remain exactly those already used in NKR-16.

## Preset decision and interpretation

**Retrospective DEV_ROBUST** only if native 56/72 exceeds the exhaustive random expected correct total by **at least 4** and the exact random-assignment fraction attaining native's score is **at most 5%**, with no confidently wrong predictions and original source/retention control passing. Otherwise **ROBUSTNESS_NOT_ESTABLISHED**; the original 56/72 and 38/72 still occurred, but they should not be claimed as robust. This criterion was fixed before reading NKR-17's actual answer.

All 56 schedules per world must yield equal 2-action cost, six unprobed tests, no false confidence under the known-conjunction family and reproducible exact original source receipts. The 56-schedule table is *retrospective exhaustive source querying*, not 672 autonomous real-world rollouts, independent trials of an open environment, or evidence of transfer.

**A very low tail fraction is not a real-world statistical p-value or scientific admission**: it describes only the combinatorics of 12 already-known synthetic worlds and a preprogrammed conjunction prior. The strongest independent fully fitted symbolic information-gain controller makes the same choices as native, so there remains **zero architecture-specific scientific superiority**. No new-world operator creation, user-owned model integration, first-use, deployment or 21M historical image installation.

## Qualification

GitHub-hosted Ubuntu and Windows source-safe focused 7-test suite plus NKR-16 inherited tests, then one source-pinned, generated-only G29 `.ice/code-atlas.{html,ice,json}` update and mandatory entire inherited root regression plus NKR05 six tests **on both OS at the exact final SHA/tree**. Do not rerun any earlier NKR-16 qualification or original MiniGrid first-use; reuse original hashes and current source. Preserve real engineering setup/test times.

**Next real scientific milestone (separate authority):** Independent source-authentic action–consequence exploration on previously unseen external task families, fully trained conventional controls, a realistic whole-process action/compute budget and genuine cold retention, with first-use and source ownership approved independently. This audit is about controlling an overclaim in the current synthetic result—not substituting for that milestone.
