# MG84 — Original-world public goal-event diagnostic (prospective, observation only)

This preregistration is frozen before the MG84 executable and before MG84 original-world first use. The previous original-world [MG83 run #41030036761](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/41030036761) successfully executed 27 episodes / 5,184 actions but obtained **zero** genuine positive terminal rewards for MG83, MG82 effect, and MG82 count-only. Revisit reduction was inferior to count-only exploration; public SHA changes were not task success. **Do not propose a fourth rewardless exploration policy before identifying the missing real-world task-progress signal.**

## Exact custody and scope

- Parent Yggdrasil MG83 draft commit `e29e461db26f78abc5c42081b0999947f2d7f601`; unchanged native Yggdrasil `research/native/itd02/mg83/revisit_cells.py` blob `f45ff00875256502011c39e5a5b0ea40300286ab`, MG82 `research/native/itd02/mg82/effect_cells.py` blob `7e45d03a83f6e17c36337acf7d2ec9d8e703a056`, MG28 `research/native/itd02/mg28/selected_change_cells.py` blob `2c30ca4da6f6603ecc5ec36b1f460a246b120d89`. Unmodified MG83 learner, MG82 effect, MG82 count-only comparators; **no training algorithm modification**, no promotion.
- Original Farama MiniGrid commit `7f5853792ea7f04f75614661006d87fcf949f26d`, original `minigrid/envs/doorkey.py` blob `df5b29ef063be34e6d83b8b478e092c6e3e01512`; 7 original actions; ONLY public `image, direction, mission`, own action, returned reward and terminal/truncated. No env.grid, agent_pos, carrying, task oracle, hidden map, reward injection, altered source.
- Same 3 original family registrations: KeyCorridorS3R2, KeyCorridorS4R3, ObstructedMaze-1Dl. Fixed 2 development seeds per family: (8111101,8111103), (8111201,8111203), (8111301,8111303). Fixed cold-process heldout seeds: (9111107,9111207,9111307). 27 predeclared original-world episodes, 192 original actions cap each, no seed/threshold tuning.
- Each role/family DEV checkpoint independently constructed; same role checkpoint cold-restored in separate Python OS process before heldout. No family sharing, no cross-role shared policy memory.

## Predeclared outcomes

Primary outcomes: original `env.step()` reward, positive terminal success/return and true termination/truncation. Task-event diagnostics are *observation only*:
1. Public mission text exact equality throughout episode.
2. Visible key/door/goal encounters from original image object channels (`key=5`, `door=4`, `goal=8` as defined by original upstream public encoding), noting first index and count; no priviledged state inference.
3. Possible publicly observed **selected pickup**: action 3 and front pixel before object-key, front pixel after no longer same key, no heading change. Classify only as possible public pickup; no true carried-state claim.
4. Public **selected door-state change**: action 5, front door color maintained and door state changed from non-open (1/2) to public open (0) without heading change. This is directly observed, not environment internal access.
5. Distinct public successor SHA count, repeated selected (before SHA, action, after SHA), selected action histogram; changes remain SECONDARY, not scores to optimize.
6. Original-world source SHA selected ledger, per-episode elapsed time, process max RSS, cold checkpoint identity, exact source and prereg commit identities.

Engineering fail closed on source drift, unexpected observation field, invalid shapes/types, action/custody mismatch, invalid feedback, missing seeds, untrusted hidden access, evidence output mismatch, dirty worktree. Preserve raw evidence in GitHub Actions artifacts; no external service, no broker.

## Decision rule and limits

- No MG84 learner introduced. The only gate under test is whether original-world **task-relevant public evidence** is obtained at all by existing independent native candidates and controls. If none, next improvement must be source-public task-grounded inference/active exploration plus equal-information trained model-based/Bayesian comparator, **not** another raw-view-change maximizer.
- One heldout seed/family, small DEV; intermediate event detection does not establish learned causal structure, native reasoning, transfer, or statistically significant improvement. Must not treat any public key/door/goal visibility as solved task unless original positive terminal reward occurs.
- All original negative results retained. Draft PR only, not merged. No protected ref or FORGE autonomy/controller/queue/scheduler change; distinct Wingless lineage issue remains separate.
