TITLE: EXP-DG1B-HIST-001
EXPERIMENT: EXP-DG1B-HIST-001
HARNESS: yggdrasil-isolated
CURRICULUM: MNIST,CIFAR10,SVHN,FashionMNIST,EMNIST
GENOME_BUDGET_BYTES: 5000000
HIBERNATION_THRESHOLD_SEC: 30
MAX_ACTIVE_MODULES: 50
REGENERATION_LR: 0.001
REGENERATION_OPTIMIZER: adam
REGENERATION_STEPS: 5000
SEED: 42
SEEDS: 42,123,456,789,1024
COMPUTE_SECONDS: 1800

CONTROLS:
- DG-1B baseline without history retention (fresh genome per task)
- Hypernetwork baseline with equivalent parameter budget
- Fixed-architecture continual learning baseline (EWC)

METRICS:
- regeneration_cost_ratio < 0.5
- capability_recovery_ratio > 0.8
- retained_state_bytes_ratio < 0.15
- retained_capability_after_sequence > 0.7

STOP_CONDITIONS:
- regeneration_cost_ratio > 0.9 for any transition
- capability_recovery_ratio < 0.5 for any transition
- total_compute_seconds > 1800
- genome_budget_exceeded

POSITIVE_MEANING:
Regeneration cost ratio < 0.5 and capability recovery ratio > 0.8 for all 4 task transitions, with retained_capability_after_sequence > 0.7, confirming developmental history compresses future phenotype development.

NEGATIVE_MEANING:
Regeneration cost ratio >= 0.5 or capability recovery ratio <= 0.8 for >=3 of 4 transitions, or retained_capability_after_sequence <= 0.7, indicating developmental history does not compress future development trajectories.

MIXED_MEANING:
Regeneration cost reduces for some transitions but not others, or capability recovery varies significantly by task order, suggesting history compression is task-pair dependent rather than general.
