# DG1-MD24 — unknown-blocker prospective transfer (toy prefirstuse NO-GO)

The frozen protocol (`prereg.json` at commit `81e167c174097df83e50e57e0ae6494231cbd032`) remains unmodified and precedes source. Parent is sealed MD23 source/atlas commit `9b0557f2cfe829d7991fd41c9f131c41a141626f`, PR #1013. This is an isolated follow-up, not part of main or the native Yggdrasil substrate.

## Question

Does a learner that extracts portable pickup/drop effects from *real charged actions* transfer to previously unseen MiniGrid-BlockedUnlockPickup better than a matched blind generic obstacle handler and the strongest available trained controls? The first-use registered cohort is explicitly distinct from toy seeds; the unfamiliar family is absent from training.

## Observation from original bounded development-only toy experiment

Before first use, on seeds 11,17,19,23,29,31 (a disjoint diagnostic cohort), the shared public-view teacher completed 6/6 DoorKey and 6/6 UnlockPickup episodes, producing 18 observed pickup-clear effects and six drop-place effects. The generic handler's novel-family toy rollout confirmed real removal of one obstruction in **all six toy episodes** for each of the learned and blind arms, but **none of the six controllers completed a novel-family episode** within the 256 charged-action cap (0/36 total successes). After activating the effect gate with six genuinely distinct toy drop observations, learned and blind agents still made the **same physical action choices**; comparison of all six complete action/reward trace hashes is the negative control.

This is **INVALID_TASK_COVERAGE_TOY / NO-GO BEFORE PRIMARY FIRST USE**, not a scientific negative on the registered cohort. It exposes both an unsolved post-obstruction planning failure and a non-identifiable learned-effect contribution relative to the equally capable blind generic procedure. The latter cannot support a claim of learning-specific improvement even if both eventually succeed.

## Custody and disposition

- Freeze, seed ranges and original hypothesis remain in prereg without postresult threshold changes. This test was entirely public MiniGrid 3.2.0 / Gymnasium 1.4.0 / NumPy 2.3.4 CPU simulation with charged `env.step` actions; no hidden env, mission, global grid, oracle or task-specific ball rule in the policy.
- **No registered train, interference, cold or blocked-family first-use seeds were executed.** The study intentionally has no registered first-use workflow or primary runner. No automatic original replay is permitted.
- The toy science outcome is preserved as a reproducible explicit result; technical qualification checks may pass even when toy task coverage is invalid. Both platform CI and the source-bound G29 inherited regression must still independently qualify the final code.
- No native Yggdrasil integration, accepted reference, merge or deployment. Prior MD23 result and other research branches remain untouched.

## Next falsifiable mechanism

To establish causal-learning value, the next *separately frozen* study must make learned action-consequence predictions change paid intervention selection or placement, versus a strong identical-information generic probe controller, **before** testing any novel-family registered seeds. Solving the scripted navigation problem alone would not demonstrate a new learning mechanism.
