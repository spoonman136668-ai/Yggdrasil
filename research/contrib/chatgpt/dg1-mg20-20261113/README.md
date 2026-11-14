# DG1-MG20 — real rewarded MiniGrid action choice, incomplete control qualification

**ENGINEERING: original exact-source PASS on Ubuntu and Windows. SCIENCE: INVALID_TASK_COVERAGE; NOT a scientific PASS. DEPLOYMENT: NONE.**

## Why this experiment was pursued
Earlier MG19 found that episodic observation forecasts retained across interference, but failed to beat persistence in both unseen MiniGrid families. This new independent preregistered experiment made *official goal completion from actual chosen simulator actions* its primary metric, rather than forecast MSE.

The baseline architecture is an online token-free topological map, built only from official 7×7×3 partial image frames, publicly returned direction, action and consequence; no global agent position, hidden full grid, mission text or expert oracle is read. Compared to same-capacity spatially scrambled memory, reactive explorer, fully trainable reward Q and conventional recurrent imitation under shared training information and equal source budget.

Preregistration frozen at `029bd7e8da15e0512c2a11bba90a9fb322bb751f` before implementation and first use. Training seeds 730001..730024 in Empty 5x5/6x6; held-out size and obstacle-family seeds are distinct.

## Original true goal-success results

| Environment, 12 registered seeds | causal map | sham map | reactive | tabular reward-Q | trained recurrent imitation |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cold Empty 6x6 before interference | 12 | 11 | 0 | 0 | 0 |
| Cold Empty 6x6 after interference | 12 | 11 | 0 | 0 | 0 |
| Unseen Empty 8x8 | 12 | 6 | 12 | 12 | 0 |
| Unseen Dynamic-Obstacles 6x6 | 12 | 0 | 0 | 0 | 0 |

Original physical actions: **25,981 `env.step` calls** across 300 actual episodes; success represents actual official reward>0, not an invented score.

**Critical defect: zero of the 48 shared behavior-training episodes earned any official goal reward**. The tabular Q learner thus did not see positive goal returns; the recurrent imitation control had no successful demonstrations. The preregistered training-coverage requirement was at least eight rewarded episodes. Its failure makes this experiment **INVALID_TASK_COVERAGE** and blocks scientific acceptance, even though the candidate achieved visible held-out goal-completion results. No strong-conventional-control superiority, AGI, or native-model improvement can be claimed. See [result.json](result.json) for preregistered pass/fail booleans.

## Custody and reproducibility
- Original prereg-only commit `029bd7e8da15e0512c2a11bba90a9fb322bb751f`.
- Original source, code-atlas and first-use candidate `dcb5549c872d4a6243ec36ce86529f021c26dfc6`, tree `2292d08061b67b59283200c99ec5b3761bbb4acc`.
- [First-use 43548323255](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43548323255): Linux/Windows SUCCESS on focused 9/9 and full 54/54 inherited regression, original physical action/outcome receipts; independent cross-OS exact action/goal/checkpoint parity SUCCESS.
- [Independent G29 43548323237](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43548323237): Linux + Windows SUCCESS.
- Original full per-episode and package receipts GitHub Actions only: `14095515815` Ubuntu, `14095600731` Windows, with archive SHA-256 in [provenance.json](provenance.json).

**Next independent falsification:** Do NOT tune the observed MG20 original result. Preregister a disjoint set of seeds and an observation-only training policy that actually produces enough official goal rewards; fully retrain the tabular and recurrent comparators on that same successful training trace, then retest independent goal performance. Preserve true negative/invalid original outcomes.

No accepted reference, native Yggdrasil architecture, official research loop or workstation changed.
