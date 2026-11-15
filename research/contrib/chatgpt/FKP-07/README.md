# FKP-07 — bounded shared causal-weight repair

**Research-only stacked candidate**, based on FKP-06 [PR #1097](https://github.com/spoonman136668-ai/Yggdrasil/pull/1097) at exact source/G29 head `845cc614915fa26f3377136b4635bae2a16276f5`. See `prereg.json` committed independently **before** these sources and any original DEV outcomes. Current accepted Yggdrasil `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` remains unchanged.

This experiment reuses the *public four-parent XOR-of-two-AND hypothesis family*, but generates fresh disjoint DEV law worlds 800..823 and eight contradictory updates 840..847. It does **not** reuse consumed FKP-06 targets 700..723. Protected source cohorts are fenced and never instantiated in research. Historical law and revision values stay source-owner-private; inference gets genuine public action consequences only.

The actual numerical causal memory in `repair.py` holds **496 fixed shared pair-count weights** and **32 fixed context program slots**. When an existing context changes, it subtracts its two old pair contributions, adds the two newly learned pairs *in the same weight array*, and overwrites **the same** context slot. It does not append a posterior slot per revision. It explicitly forgets obsolete earlier versions of revised contexts; the retention requirement concerns 16 still-current, unaffected contexts. The local checksum-sealed checkpoint has an exactly fixed size and verifies the global aggregate against independently replayed context programs on restore.

`run_dev.py` tests real actions and posterior inference on fresh DEV worlds with **64 interventions/world and prefix scores at 4, 8, 12, 16, 32, 64**, measured against a fully informed *independent exact replay* of the same public causal histories and a destructive unscoped overwrite negative. It reports source access cost, prediction quality, immutable evidence, memory, wall/CPU and total end-to-end cost. It does **not** invent an outside-family causal operator, use a protected source, train the currently accepted native Yggdrasil weights, or claim superiority over Bayesian inference. Exact symbolic is expected to tie prediction accuracy; only independently replicated end-to-end benefit over matched optimized baselines could justify future acceptance.

## Reproduction (fresh DEV cohort only once; subsequent runs are reproducibility checks)

At exact source SHA, Python 3.12 standard library, from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s research/contrib/chatgpt/FKP-07 -p test_fkp07.py -v
PYTHONDONTWRITEBYTECODE=1 python -B research/contrib/chatgpt/FKP-07/source.py
PYTHONDONTWRITEBYTECODE=1 python -B research/contrib/chatgpt/FKP-07/run_dev.py
```

The first DEV action/held evaluation must only happen **after** the original source, test, code SHA, prereg, and exact isolated engineering qualification are established. Stage0 tests use *fixture* worlds 880/881, never DEV originals. The genuine DEV result must be classified and preserved even if negative; do not modify the protocol or implementation after seeing it. Do not merge native model or alter controllers, official loops, main, private owner evaluators, paid APIs or self-hosted runners.
