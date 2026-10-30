# MG81 — Prospective original MiniGrid local-cell reward guard DEV, source-pinned

**Registered before the MG81 executable.** Engineering acceptance MG80: Yggdrasil exact commit `aa05346f5844c68c700280b5af63b022a58c3bc4`; G29 run 41025177388 and MG51 run 41025177301 both Linux/Windows PASS. This is a new, *advisory* DEV protocol, not accepted learning science or FORGE execution authority.

## Immutable source and roles
- Original Farama MiniGrid: `7f5853792ea7f04f75614661006d87fcf949f26d` (unchanged original, check `minigrid/envs/doorkey.py` Git blob `df5b29ef063be34e6d83b8b478e092c6e3e01512`).
- Native source exact files: `research/native/itd02/mg37/{source_bridge.py,progress_cells.py}` and `research/native/itd02/mg28/selected_change_cells.py` at frozen MG80 source tree, unchanged from their qualified blobs `ed9184349dc74b43d8a28e18ac1d558512b7948c`, `175c4a7e2ed83a37c2f103339aefc9a4e95eca86`, `2c30ca4da6f6603ecc5ec36b1f460a246b120d89`.
- Role A: unmodified `SelectedProgressCells` (MG37 context-reward guard over MG28).
- Role B: unmodified `SelectedChangeCells` (MG28 parent), same original public observations, time/steps, seeds, selected feedback. No prewritten action choices, hidden world state, next-state oracle, memory cloning between roles, cross-role replay, or live trades.
- Three source-original families: `MiniGrid-KeyCorridorS3R2-v0`, `MiniGrid-KeyCorridorS4R3-v0`, `MiniGrid-ObstructedMaze-1Dl-v0`, with registry identities `minigrid.envs:KeyCorridorEnv`, `minigrid.envs:KeyCorridorEnv`, `minigrid.envs:ObstructedMaze_1Dlhb` from frozen original source.
- Prospective non-MG56 development seeds per family: (2111101,2111103), (2111201,2111203), (2111301,2111303), then *held-out* evaluation seeds (3111107),(3111207),(3111307). Exact seeds are hypotheses, not selected by measured score.
- Maximum 96 selected actions per episode; per-family learner persistent only between two DEVELOPMENT episodes; separate OS process checkpoint restore before held-out episode for both roles. No family-to-family memory sharing. Stop on original termination/truncation. Fixed cap, no retries to cherry-pick winners.

## Required measures and decision
- Genuine source-public action/feedback custody counts and SHA-256 ledger digest, per family/role/seed public mission, positive terminal rewards, return, terminal/truncated status, selected original actions and public-observation changes.
- MG37 actual **reward-conditioned override count**, exact parent actions for candidate on-policy before overrides, counts of source-context positive prior evidence; separately count first positive terminal reward and pre-first-success override attempts.
- Held-out pairwise MG37-vs-MG28 terminal success, return, source-action counts, original-world reward, and cold-process restored checkpoint integrity; identical seeds and equal world step limits.
- Engineering FAIL on source pin/hash drift, privileged observations, missing matched episodes, altered native implementation, inconsistent selected-action ledger, checkpoint mismatch, non-finite reward, changed tracked source, or no genuine original-world steps.
- A **DEV result** is descriptive, not independent scientific validation; with one held-out seed per family no statistical superiority can be claimed, and a zero-override result cannot be promoted as learning.
- Resource accounting: per-role/family elapsed wall seconds, process max RSS where available, source step counts and JSON report checksum. Preserve raw reports and failures as Actions artifacts for independent review. Native model+runner is **not** upgraded or merged from this gate.

## Safety
Runner stays on existing isolated draft PR and GitHub-hosted Ubuntu with read-only contents. The Farama clone is pinned original source; no downloads of alternative environment implementations; no env internals (position, grid, carry or goals) passed to learners. Source must first pass re-generated G29 atlas+MG51. Stop at any incompatible native API or original source identity. Keep FORGE autonomy and Wingless branch untouched.
