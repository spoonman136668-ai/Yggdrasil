# AAI-07P — external memory/action-consequence environment preflight

After AAI-06's preregistered negative scientific outcome, the next useful step is to stop inventing another binary-rule benchmark. This gate inspects a **real, independently maintained, unmodified** reinforcement-learning environment, Farama Foundation's MiniGrid Memory suite.

The official `MiniGrid-MemoryS11-v0` and `MiniGrid-MemoryS13Random-v0` environments require seeing a clue, navigating away from it and choosing its matching object later. Native observations are partial grid integer arrays and an orientation, not language tokens.

**External custody:** exact upstream Git SHA `64e1eaec904bc35e7de041167274e2c0dfe541d2` and `minigrid/envs/memory.py` Git blob `660b0a1b769948034c87bb421759c2b9a4f24548`. External source is retrieved from the official repository and run unchanged under separately pinned dependencies. No upstream code is copied here. The repository LICENSE and pyproject license metadata differ; this research merely fetches and executes the official source, and carries no redistribution of it.

**Scope of this gate:** mechanical only. Exactly eight reserved seeds per environment verify repeatable reset and step behavior, pixel-only observation access, valid actions, source identity and no simulator-private answer leakage. Neither algorithm performance nor scientific held-out seeds are touched. These smoke-trace fingerprints are *not* scientific results.

The next scientific study must be separately preregistered **before any outcome is inspected**, with train/DEV/TRANSFER seeds, an explicit learner and strong fully trained conventional controls, matched action/data/compute budgets, no privileged navigation, genuine online learning, cold retention and interference. It must use the actual `step` reward and termination signals and preserve null outcomes.

This is an external contribution and cannot change Yggdrasil's native non-token architecture, official loop, controller, accepted research state, model weights or deployment.
