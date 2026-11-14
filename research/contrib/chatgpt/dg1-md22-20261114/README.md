# DG1-MD22 — charged locked-door interventions and bounded affordance memory

**ENGINEERING: original exact-SHA 9/9 prefirstuse and 54/54 inherited regression PASS on Ubuntu and Windows. SCIENCE: INVALID_TASK_COVERAGE / PRIMARY NO-GO. DEPLOYMENT: NONE.**

## Actual hypothesis and source boundary
The experiment asks whether physically learned **no-key locked-door toggle failure vs with-key unlock success** can make a simple topological navigator choose the key before a locked door when entering a new partially observable MiniGrid environment. This is deliberately a **rule-scaffolded** policy; only the conditional action-outcome relationship is learned. The code cannot support claims of general reasoning, end-to-end causal discovery, or AGI.

Preregistration-only `ada17791db5ba3892f2d8012e38dffd024b55dbb` preceded this experiment's source and first registered actions; predecessor MG21 #1007 was frozen at `8edf7b5563f5a37f3284a96354c9985266d58c18`. No original MG20/MG21 registered seed used and no native model changed. Registered MD22 worlds 930001..970012; exact original source+G29 candidate `4fb8bd4eb0edbeb37ca5e5812fbe7765221dae61`, tree `68d79b9133efca53beaa081cd5a0c7abad8ed291`.

Five models saw **identical, physically charged 48 training episodes** from a public-image-only teacher which intentionally probed a locked door without a key, acquired the key, and then unlocked the door. The candidate and sham shared the same rule-based pathfinder and the same learned counters but the sham did not use the learned causal condition in selecting a key-first subgoal. Also included a reactive navigator, fully trained tabular reward Q, and fully trained recurrent imitation. Heldouts: cold DoorKey6x6 before/after unrelated Empty interference, DoorKey8x8, and UnlockPickup. All actual agent actions were charged against the real third-party MiniGrid simulator.

## Frozen first-use result

| Held-out family, 12 seeds | Causal affordance (official goal / mean discounted reward) | Sham affordance |
| --- | ---: | ---: |
| Cold DoorKey6x6 after interference | 12/12, 0.86268893 | 12/12, 0.80248934 |
| New-size DoorKey8x8 | 12/12, 0.81997417 | 12/12, 0.76773046 |
| New-family UnlockPickup | **0/12, 0** | **0/12, 0** |

**48/48 shared physical training episodes reached their official goals.** There were **28 charged failed no-key locked-door interventions and 48 successful with-key unlocks**. Across the frozen 300 episodes, the five arms and shared teacher made **46,016 actual `env.step` calls**.

The causal-affordance policy appears more efficient than the matched sham on DoorKey8x8, but only by 0.05224 mean discounted official reward—**less than** the preregistered +0.08 margin. The same-scaffold sham also reached 12/12 goals. And **none of the five models earned any official goal reward in 12 unfamiliar UnlockPickup episodes**. The precommitted held-out family task coverage requirement was at least three goals collectively. This **invalidates cross-family scientific qualification**. The original class is `INVALID_TASK_COVERAGE`, primary false; no post-result tuning or reinterpretation as scientific success is permissible.

## Exact original provenance and reproducibility
- [Original physical first-use run 43577409758](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43577409758): **SUCCESS**, Ubuntu+Windows focused 9/9, full inherited 54/54 per OS, 46,016 paid steps, scientifically invalid coverage on BOTH. Independent exact action, reward, output, model checkpoint and non-timing JSON parity **PASS**.
- [Original independent G29 acceptance 43577409800](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43577409800): PASS Ubuntu+Windows.
- Full original action receipts and environment `pip freeze` remain in GitHub Actions only: artifact Ubuntu `14107410820`, ZIP SHA-256 `998a9d43e4e2bbd95edd70f32bb6dbf0150be5a3a3012612f8372ddc16689db4`; Windows `14107221144`, ZIP SHA-256 `4770c63f85bef82aaadcab0b95f1e405caa4cb8df4e3d6f695010fa81e8ce906`. Compact original gates and scores are in [result.json](result.json), exact original receipts in [provenance.json](provenance.json).

## Scientific next decision
Do not use any more MD22 registered actions or tune the MD22 source based on failed UnlockPickup scores. An independent prospective successor must first establish **positive unfamiliar-task reward coverage** and matched strong baselines, possibly by training on an additional distinct family with direct *box pickup after unlock* consequences. Re-run strict transfer/retention only on new held-out worlds under a new prereg, then compare to matched sham and successful fully trained conventional policies. Another invalid result is not a breakthrough.

No official acceptance, model integration, autonomous controller, merge, promotion, deployment, workstation action or ChatGPT Library file creation occurred.
