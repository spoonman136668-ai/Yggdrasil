# FKP-03: information-seeking actions for native causal-law discovery

Follow-on to [Issue #1088](https://github.com/spoonman136668-ai/Yggdrasil/issues/1088) and [FKP-02 DEV negative, PR #1091](https://github.com/spoonman136668-ai/Yggdrasil/pull/1091). This is **isolated research**, NOT Yggdrasil accepted model state, user workstation execution, protected scientific first-use, or a scheduled/controller job.

**Objective:** Test the actual weak seam from FKP-02. The previous method could generate compositional relationships but picked the wrong one; can experience-derived basic relations plus active information-seeking interventions produce useful 3-parent causal inference from an equal 16-action budget?

## Frozen custody

- Parent `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, tree `180008502f6bdfe5a06c3d0d6f47f941dd01f20b`.
- First/only preregistration commit `da035763b42834828d3ea185b1074463b3e38172` before source, policy, tests or outcomes.
- Original source specification SHA-256 `3ce2d43c77ec55523d6bbe6872b4dc6a9481db719124ccbfe02c40c6f6637246`, not source-code identity (the exact Git blob must also be verified).
- Fresh DEV worlds `400..415` are separate from FKP-01 and FKP-02. Primary `1400..1463` and negative `2400..2415` are **protected**. Their hidden source law cannot be instantiated without an external 32+-byte owner key. No protected key belongs in this repo, chat, CI job, or a learner.
- The source owner exposes **64 public candidate actions** per world, but a learning arm pays for **exactly 16 distinct action-consequence observations**, with adaptive selection allowed. All arms predict the same 128 held input states, disjoint from all 64 candidates.

## Frozen DEV implementation

The code in `source.py`, `model.py`, and `run_dev.py` is stdlib-only, deterministic and source-only. All model fitting and action choices read only the public action set and genuine consequences through `CausalWorld.observe()`; no target family, parent indices or original evaluator-private key enters fitting.

`model.py` first infers two-parent Boolean relation tables from the **16,384** historical source experiences over 256 source worlds, then builds a general 3-variable truth-table closure from whatever gates were actually acquired. The closure's 218 genuinely 3-input functions are available to a fixed posterior over 220 potential input parent triples, with no supplied rule identity. `Posterior.choose()` picks the next action by balancing posterior predictions. The experiment independently compares the same inference system with frozen random actions and geometric/coverage active actions.

A family-aware conventional exact symbolic active posterior is an explicit *stronger-source-prior* reference, **not a fair matched-information superiority comparator**. We also evaluate that strong posterior on the **exact transcript chosen by the candidate**, without extra queries. A preloaded exact grammar control receives the same hypothesis set but pays no historical-learning cost; equality there means foundational acquisition showed no advantage over a preprogrammed algebra. Fully trained conventional capacity/cost-matched learners and sequential cold-retention interference are **not yet independently qualified**, and are mandatory for any scientific acceptance.

A developer-only source owner evaluates held consequences **after all arm predictions have been sealed**. Protected-world evaluator never runs. The original source secrets remain beyond the eventual external owner-first-use boundary.

## Reproduction at exact candidate SHA (public DEV ONLY)

```console
python -B -m unittest discover -s research/contrib/chatgpt/FKP-03 -p test_fkp03.py -v
python -B research/contrib/chatgpt/FKP-03/source.py
python -B research/contrib/chatgpt/FKP-03/run_dev.py
python -B scripts/build_code_atlas.py --check-if-present
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

The preset positive **DEV policy** requirement is at least +5 percentage points accuracy over both random and geometric coverage, positive world-paired 95% CI against both controls, and no loss on either actual DEV source-family group. Otherwise close **DEV_NO_GO** without tuning/retrying an exposed DEV split. Even DEV-policy-signal does **NOT** establish native model superiority, continued retention, or SCIENTIFIC_PASS.

## Conditional main-model integration

A beneficial scientific result would have to be independently reproduced on new original causal sources with fully qualified strong conventional and Bayesian controls, source/first-use custody, evidence of native function improvement, cold retention and whole-process efficiency. Only then implement the smallest native Yggdrasil cell/memory/routing change and pass exact-source Windows/Linux full regression + G29 + separate owner acceptance. PR or G29 PASS alone never means the native model has been improved.
