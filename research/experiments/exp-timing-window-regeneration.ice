TITLE: Timing Window Regeneration
EXPERIMENT_ID: EXP-TIMING-WINDOW-REGENERATION-001
CANDIDATE_ID: CAND-TIMING-WINDOW-REGENERATION
HARNESS: yggdrasil-isolated

QUESTION
Can phenotype activation become demand-driven without catastrophic cold-start latency?

HYPOTHESIS
Phenotype activation can become demand-driven with regeneration latency < 20% of cold retraining latency while retaining < 10% of full phenotype bytes as wake information.

CONTROLS
- Cold retraining from random initialization (same architecture, same compute budget)
- Full phenotype retention (no hibernation, immediate availability)
- Random wake information baseline (retained state replaced with noise)

FIXED_PARAMETERS
damage_fraction=0.0
development_step_budget=10000
hibernation_criterion=task_mastery_accuracy_95
memory_budget_mb=512
model_architecture=developmental_mlp_4layer_256
population_budget=128_modules
task_sequence=permuted_mnist_5_tasks
wake_information_budget_bytes=10240

METRICS
regeneration_latency_ratio < 0.2
retained_state_bytes_ratio < 0.1
function_recovery_accuracy >= 0.9
regeneration_development_steps_ratio < 0.3

SEEDS
42,123,456,789,1024,2048,4096,8192

COMPUTE_SECONDS
1200

STOP_CONDITIONS
- All seeds completed
- Wall time exceeds compute_seconds
- Any seed shows regeneration_latency_ratio > 0.5 (early futility)

POSITIVE_MEANING
Regeneration latency < 20% of cold retraining AND retained state < 10% of phenotype AND function recovery >= 90%; demand-driven phenotype activation is viable.

NEGATIVE_MEANING
Regeneration latency >= 20% of cold retraining, OR retained state >= 10% of phenotype, OR function recovery < 90%; demand-driven activation not viable with current mechanism.

MIXED_MEANING
Regeneration is faster than retraining but requires excessive retained state, or retains minimal state but fails to recover function accurately; indicates trade-off not yet resolved.
