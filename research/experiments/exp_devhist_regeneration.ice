TITLE: EXP-DG1B-DEVHIST-001
SCHEMA: yggdrasil.research-experiment.v1
EXPERIMENT: EXP-DG1B-DEVHIST-001
BRANCH: research/yggdrasil-exp-dg1b-devhist-001-r1
BASELINE_SHA: 1c03ddc0a587a97611f54e75d198d113fcf03778
HARNESS: yggdrasil-isolated

QUESTION
Does persistent developmental history reduce regeneration cost and enable cross-task motif reuse beyond minimal retained state?

HYPOTHESIS
Developmental history encoding enables regeneration at lower cost than minimal retained state by preserving causal developmental trajectories and reusable motifs.

FIXED_PARAMETERS
development_steps_per_task: 2000
history_encoding: full_lineage
memory_budget_mb: 512
num_tasks: 5
population_budget: 1000
regeneration_protocol: genome_plus_history
retained_state_fraction: 0.05

CONTROLS
- minimal-state regeneration baseline (EXP-DG1B-MINSTATE-001 protocol)
- continuous active learning baseline
- fixed hypernetwork baseline
- fixed adapter baseline

METRICS
- regeneration_cost_ratio < 0.45
- capability_recovery_ratio >= 0.9
- regeneration_steps_ratio < 0.5
- cross_task_motif_transfer > 0.15

SEEDS
42, 123, 456, 789, 101112, 131415, 161718, 192021

STOP_CONDITIONS
- regeneration_cost_ratio > 0.6 for 3 consecutive seeds
- capability_recovery_ratio < 0.8 for any seed
- compute_seconds > 1800
- population_budget exceeded
- memory_budget exceeded

POSITIVE_MEANING
Regeneration cost ratio < 0.45 (improvement over 0.495 baseline), capability recovery >= 0.9, and cross-task motif transfer > 0.15. Developmental history provides measurable benefit for regeneration and reuse.

NEGATIVE_MEANING
Developmental history does not reduce regeneration cost below minimal-state baseline (regeneration_cost_ratio >= 0.495) or capability recovery drops below 0.9. History encoding adds persistent storage without proportional benefit.

MIXED_MEANING
Regeneration cost improves but capability recovery drops, or vice versa; cross-task transfer is marginal. Requires mechanism dissection.
