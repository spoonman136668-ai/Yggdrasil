# DG1-MD28 — shifting causal law with costly physical re-probes

This is isolated **external research**, not a native Yggdrasil model change. Frozen preregistration `3b89e764ee859cc17ebaeea7bef6403cb770e3ea` preceded code and results. Previous MD27 `9f9cc2e50837f60945694473f4ae51621a0b19e2` and all older research were untouched.

## Hypothesis and prospective controls

A new original standard-library **ShiftingRelay-v1** simulator allows a hidden polarity to change *inside an episode*. The agent sees only public context and target, not the latent polarity or flip event. A paid `pre_probe` (0.03) can reveal polarity before the physically paid `disturb` (0.04); disturbance flips the polarity with a public-hazard-dependent probability of 0.01 (low) or 0.5 (high). The agent may pay another `post_probe` (0.20) before irreversible `apply_A`/`apply_B` (0.03, +1 correct or -0.5 wrong).

The agent must decide whether post-disturbance uncertainty makes another physical probe worth its cost. A fixed teacher performed **240 complete physically charged 4-action episodes (960 actions)** evenly across three visible training wiring combinations, with 40 episodes per context and hazard; no training example had the new wiring combination `(0,1)`. The entire shared training dataset is used by all eight models, including conventional full-batch logistic and a fully trained factorized adaptive maximum-likelihood model. Preselected toy heldout seeds `181..228` are disjoint from training, cold replay `229..240`, and unused registered cohort `1050001..1050096`.

## Real action/consequence developmental observation

On 48 new heldout changing-regime episodes:

| Policy | Official goals | Mean net physical reward | Paid actions |
|---|---:|---:|---:|
| causal-adaptive learned counts + factor prior | **48/48** | **0.815** | 144 |
| fully trained conventional factorized adaptive MLE | **48/48** | **0.815** | 144 |
| scripted known-physics ceiling | **48/48** | **0.815** | 144 |
| always post-disturbance probe | 48/48 | 0.730 | 144 |
| never probe | 22/48 | 0.1175 | 96 |
| always pre-probe / skip post | 31/48 | 0.36875 | 144 |
| trained joint lookup | 0/48 | -0.685 | 144 |
| fully trained logistic without cross feature | 0/48 | -0.685 | 144 |

All **12/12 frozen toy gates PASS**. In low-hazard cases the candidate used a paid initial probe and skipped the redundant paid second probe; in high-hazard cases it deferred to a paid post-disturbance probe. It earned **+0.085** per episode over always probing after disturbance and **+0.6975** over never probing; 24 paired utility wins versus always post-probe. Cold restart yielded identical physical action/reward traces and frozen checkpoints.

**There is 0.0 gain over the strongest fully trained conventional factorized model or the scripted optimal-policy ceiling.** This validates an interpretable task and explicit factorization/value-of-information prior, not a novel AGI or superior learning substrate.

## Qualification and stop boundary

- The source-only dual-OS toy run [43589257261](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43589257261) passed six focused tests and strict entire non-timing physical observation/action/reward parity on both platforms. Full final inherited 54-test regression and G29 source atlas must still be tied to the final derived source commit.
- Scientific phase: **development toy PASS**, original registered cohort `1050001..1050096` **UNUSED**, independent scientific acceptance **UNVERIFIED**. Do not retune a frozen first use or claim native capability improvement.
- Deployment: **NONE**. Do not merge, change main or accepted refs, run owners/controllers, integrate into native weights, start scheduled tasks or disrupt Wingless/Hybrid/Forge.

The next research question must compare genuinely adaptive multi-step causal memory against the **strongest** learned model-based policy on a task with interference and repeated law changes; choosing a good cost threshold based on an explicit prior is insufficient evidence of novel intelligence.
