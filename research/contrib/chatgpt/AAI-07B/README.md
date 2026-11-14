# AAI-07B — real trial-and-error cue-to-action learning, not hard-coded matching

This contributor study uses the independent upstream MiniGrid Memory environment (exact source `64e1eaec904bc35e7de041167274e2c0dfe541d2`) after AAI-07A established that a single retained cue materially affects terminal reward. **This study removes the hand-coded matching decision** but retains a fixed observation-only navigation route. A learner must discover which binary terminal action succeeds from the official environment's actual outcome, not from an oracle, grid, success position, or key-equality lookup.

**Frozen before scientific first-use:** `10e0ad453454a0f85eafbda1c8618657979810bd`. Precisely 48 training episodes gathered by one deterministic common exploration policy on S11; reward-conditioned per-context direct association, fully trained 2000-step categorical logistic, conventional Laplace/Beta contextual table, and memoryless reactive control receive the same admissible learning information. DEV 64 S11 episodes, TRANSFER 64 disjoint variable-length S13 episodes, NEGATIVE 64 S13 episodes with permuted reward labels. 16 new disjoint S13 episodes update the same persistent model after its checkpoint; cold restore and before/after policy consistency are measured.

**Important interpretation:** This is a very small predefined categorical reward-association task. The direct additive table is equivalent in decision boundaries to a conventional Beta-count estimator with symmetric prior. Winning against weaker baselines could show ordinary within-task learning but **cannot constitute new learning algorithm superiority**. No new causal physics, visual feature learning, autonomous route learning, or conflicting-task interference is tested. The environment provides a learned-memory falsification baseline, not proof of AGI or Yggdrasil advancement.

Mechanical tests inspect only program invariants and synthetic dummy rows. All real first-use train/evaluation seeds remain unseen until a separate exact-source one-shot workflow. No native Yggdrasil, Wingless, Hybrid, FORGE controller or accepted ref changes.

## Qualification

The exact-source one-shot experiment archives original full per-seed data to a repository CI artifact and compact scientific evidence in the PR. Source/index full cross-platform engineering regression is separate. Keep the PR DRAFT and unmerged unless separately approved by native owners.
