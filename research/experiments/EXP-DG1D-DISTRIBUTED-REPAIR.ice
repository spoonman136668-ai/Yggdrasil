TITLE: EXP-DG1D-DISTRIBUTED-REPAIR
EXPERIMENT_ID: EXP-DG1D-DISTRIBUTED-REPAIR-001
CANDIDATE_ID: CAND-DISTRIBUTED-REPAIR-001
HARNESS_ID: yggdrasil-isolated
STATUS: PREREGISTERED

QUESTION
Can distributed local repair restore specialized function after targeted damage without global coordination?

HYPOTHESIS
Local developmental operations (REPAIR, REGENERATE) can restore task-relevant function after targeted ablation using only surviving structure and bounded neighborhood dynamics, with repair cost < 0.5x cold retraining and functional recovery > 0.85.

FALSIFIER
Repair cost exceeds 0.8x cold retraining cost OR functional recovery ratio < 0.7 OR repair requires > 5% of cells to receive global signals.

MECHANISM
Train a multi-task phenotype, then ablate 30% of cells in a task-specialized region. Trigger local REPAIR operations using only surviving neighbor state and developmental rules. Measure repair steps, active parameter change, and functional recovery on held-out tasks.

FIXED_PARAMETERS
ablation_fraction: 0.3
development_steps_per_task: 2000
max_repair_steps: 500
memory_budget_mb: 512
neighborhood_radius: 2
population_budget: 10000
task_count: 3

CONTROLS
- Cold retraining from scratch on same task after ablation
- Global fine-tuning with full gradient access
- No-repair baseline (ablation only)
- Sham repair (random parameter noise instead of developmental rules)

METRICS
- repair_cost_ratio_vs_retrain (< 0.5)
- functional_recovery_ratio (> 0.85)
- global_signal_fraction (< 0.05)
- active_parameter_growth_ratio (< 0.3)
- resident_byte_growth_ratio (< 0.2)

SEEDS
42, 123, 456, 789, 101112

COMPUTE_SECONDS: 1200
STOP_CONDITIONS
- repair_steps > 500
- functional_recovery > 0.95
- active_parameter_growth > 0.5 * original_parameters
- global_signal_fraction > 0.1
- wall_time_seconds > 1200

POSITIVE_MEANING
Local repair achieves recovery > 0.85 at cost < 0.5x retraining with < 5% global signals. Supports developmental thesis: distributed repair is viable, capability grows faster than active structure.

NEGATIVE_MEANING
Repair cost >= 0.5x retraining OR recovery < 0.85 OR global signals > 5%. Local repair insufficient; thesis weakened per falsifiable failure mode 'useful specialization requires effectively global centralized control'.

MIXED_MEANING
Partial repair succeeds (recovery 0.7-0.85) but requires non-local signals or excessive parameter growth. Indicates repair mechanism needs refinement but developmental thesis not falsified.
