EXPERIMENT_ID: EXP-TIMING-WINDOW-REGEN-001
CANDIDATE_ID: CAND-TIMING-WINDOW-001
HARNESS_ID: yggdrasil-isolated

CONTROLS:
- Cold-retraining from scratch on same task (baseline regeneration cost)
- Continuous active training without hibernation (upper bound on capability)
- Random initialization with same developmental budget (lower bound)
- Fixed dormancy period of 0 steps (immediate regeneration control)

FIXED_PARAMETERS:
- development_step_budget: 10000
- dormancy_steps: [0, 100, 500, 1000, 5000, 10000]
- genome_size: 1000000
- hibernation_retention_ratio: 0.1
- num_dormancy_levels: 6
- regeneration_step_budget: 5000
- task_complexity: medium

METRICS:
- regeneration_cost_ratio < 1
- capability_recovery_ratio > 0.8
- max_viable_dormancy_steps < 5000

SEEDS: [42, 123, 456, 789, 1024, 2048, 4096, 8192]
COMPUTE_SECONDS: 1200

STOP_CONDITIONS:
- All dormancy levels tested across all seeds
- Compute budget exhausted (1200 seconds)
- Regeneration cost ratio exceeds 2.0 for 3 consecutive dormancy levels
- Capability recovery ratio drops below 0.3 for any dormancy level

POSITIVE_MEANING:
Regeneration cost ratio < 1.0 and capability recovery ratio > 0.8 for dormancy periods up to at least 5000 steps, confirming a substantial timing window where regeneration is both cheaper and effective.

NEGATIVE_MEANING:
Regeneration cost ratio >= 1.0 for all dormancy periods > 0, or capability recovery ratio < 0.5, indicating no meaningful timing window exists; regeneration is never cheaper than cold retraining.

MIXED_MEANING:
Regeneration cost ratio < 1.0 for some but not all dormancy periods, or capability recovery between 0.5-0.8, indicating a limited or conditional timing window that depends on task/genome specifics.
