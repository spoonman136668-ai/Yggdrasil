# MG21 — independent reward-bearing control validation

**FROZEN SCIENCE: VALID MIXED_DEV, PRIMARY NO-GO.** Original engineering/reproducibility PASS on Linux/Windows. Native model untouched.

## Original question
Would a token-free episodic causal-map learner use actual partial-observation history to reach official MiniGrid goals more efficiently than strong conventional reward-trained controls, after all controls received **successful** physical demonstrations?

Unlike MG20's scientifically invalid 0/48 reward training, a new observation-only map navigator generated **48/48 actual successful training demonstrations** on independent MiniGrid Empty 5x5/6x6 worlds. Every arm saw identical charged behavior trajectories and reward histories. The Q-learning and recurrent imitation controls were genuinely trained on the positive-reward evidence. No hidden grid, global position, mission text or oracle actions were accessed.

Preregistration-only commit `36d6155a9b3c254f31c05bdb5f1e3469fcff616b` preceded new adapter source, observations or tests. Frozen MG20 algorithmic code was pinned at `9477ea4b366f2287eb316460514726cd6d2dfa7e`, reused without source modification. Fresh MG21 training/holdout seeds 830001..870012 are disjoint from MG20's registered cohort. Original source commit `3b3c7231199d810a5ddfbf7e77f8397fe8b3126e`.

## Frozen official outcome

| Measured official discounted reward, higher is better | Empty 8x8 transfer | Dynamic Obstacles 6x6 transfer |
| --- | ---: | ---: |
| Causal map (12/12 goal completions both) | 0.82293305 | 0.75964609 |
| Conventional recurrent imitation (12/12, 3/12) | **0.86940792** | -0.51013416 |
| Conventional trained Q-learning (12/12, 12/12) | 0.73138054 | **0.79922669** |
| Reactive nonlearning (12/12, 0/12) | 0.76698560 | 0.00000000 |
| Sham scrambled map (9/12, 0/12) | 0.35433558 | -0.93980221 |

**Candidate reached official goals 12/12 in both independent heldout families, but did not beat the strongest trained control by preregistered discounted official reward and per-seed criteria.** Recurrent was better in the larger Empty layout; Q-learning was better in the moving-obstacle environment. Cold-goal completion retained 12/12 before/after interference. Valid scientific classification `MIXED_DEV`, **primary NO-GO**. There is no proven generally superior intelligence, learning transfer, accepted Yggdrasil substrate integration, or AGI claim.

Physical custody: **11,823 actual `env.step` actions across 300 independent episodes**, from 48 positive-reward shared training, 12 shared interference and four independent 12×5 arm evaluation cohorts. All action/outcome, training and held-out evidence and fully trained control records captured in original GitHub Actions artifacts; see [result.json](result.json) and [provenance.json](provenance.json).

## Original exact-source qualification
[Original run 43549312541](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43549312541) SUCCESS Ubuntu+Windows, 9/9 toy-only prefirstuse, 54/54 full inherited regression each OS, independent exact original action/reward/checkpoint JSON parity PASS. [Independent G29 43549312583](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43549312583) success both OS. Full original GitHub-only artifacts: Ubuntu `14095144186` and Windows `14095795395` (archive hashes in provenance).

## First-use custody defect discovered and mitigated
Opening this stacked draft also triggered the inherited **MG20** workflow [run 43549312528](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43549312528), which replayed MG20 registered seeds. This is a **duplicate execution**, not independent scientific evidence, and must not be used to upgrade MG20. The source-branch gating bug was then fixed in MG20 and MG21 workflow definitions (see provenance commits) so first-use applies only to the named experiment's own PR-head branch and correct base. Original MG21 first-use itself was distinct; both original MG21 Ubuntu/Windows outcomes agree.

## Implication
The cause of the earlier MG20 invalidity was remedied in a separate prospective study, yielding a valid comparative NO-GO. Next research should focus on **active intervention and task-efficient causal policies** evaluated against trained reward-Q, trained recurrent, and well-engineered goal-aware controls on genuinely new tasks, not endless variations of previous synthetic gates. No tuning/replay of registered MG21 seeds, and no native integration without separate scientific qualification.
