TITLE: Regeneration Cost Ratio Experiment
EXPERIMENT: EXP-REGEN-COST-RATIO-001
HARNESS: yggdrasil-isolated

QUESTION
Is functional regeneration from developmental checkpoints cheaper than cold retraining, and does the cost ratio improve with accumulated developmental history?

FIXED PARAMETERS
architecture: yggdrasil-dg1b
batch_size: 128
checkpoint_intervals: 100,500,1000,2000 steps
max_dev_steps_per_task: 5000
memory_budget_mb: 512
optimizer: adam,lr=1e-3
population_budget: 1000 cells
seed_task: mnist-classification
transfer_tasks: fashion-mnist,kmnist,emnist-letters

METRICS
regeneration_cost_ratio < 1
regeneration_cost_ratio_transfer < 1
capability_recovery_fraction > 0.95
wake_latency_ratio < 2

SEEDS
42,123,456,789,101112

CONTROLS
Cold retraining from random initialization with identical architecture and optimizer
Fixed-architecture continual learning baseline (EWC, replay, adapters)
Regeneration from checkpoints at different developmental stages
Transfer tasks of varying similarity to seed task
