TITLE: EXP-REGEN-COST-001
SCHEMA: ckb-plane.research-experiment-preregistration.v1
EXPERIMENT: EXP-REGEN-COST-001
CANDIDATE: CAND-REGEN-COST-001
HARNESS: yggdrasil-isolated

QUESTION
Does regeneration from persistent developmental information achieve substantially lower cost than cold retraining while preserving function?

HYPOTHESIS
Regeneration from compact developmental state achieves regeneration_cost_ratio < 0.5 and regeneration_accuracy > 0.90 compared to cold retraining baseline.

CONTROLS
- Cold retraining from identical random initialization
- Fixed task complexity and data distribution
- Identical compute budget for regeneration and retraining
- Same random seeds for both conditions

FIXED PARAMETERS
- genome_size: 1024
- memory_budget_mb: 512
- phenotype_size: 4096
- population_budget: 32
- task_complexity: medium
- wake_state_budget: 256

METRICS
- regeneration_cost_ratio < 0.5
- regeneration_accuracy > 0.9
- wake_latency_ratio < 2

SEEDS
42, 123, 456, 789, 1024, 2048, 4096, 8192

COMPUTE_SECONDS: 1800

STOP CONDITIONS
- Regeneration completes or exceeds 2x cold retraining time
- Accuracy converges or plateaus for 100 steps
- Memory budget exceeded
- Population budget exceeded

POSITIVE_MEANING
Regeneration cost ratio < 0.5 AND regeneration accuracy > 0.90 across >= 6 of 8 seeds, confirming regeneration advantage.

NEGATIVE_MEANING
Regeneration cost ratio >= 0.95 OR regeneration accuracy < 0.85 across all seeds, falsifying the regeneration advantage claim.

MIXED_MEANING
Regeneration cost ratio < 0.5 but accuracy < 0.9, or cost ratio >= 0.5 but accuracy > 0.95, indicating tradeoffs requiring architectural revision.

BASELINE_SHA: b431d79e431c86c57395f382444494f0ca0d7738
PROPOSAL_SHA256: afe7b7b4c2fba5e039a08e176e1d6be64ea92aaa74fdf831abea8a6bc5b83ac1
DRAFT_SHA256: 0fd03d087ffd68952ec94dfe3b7777c25e4a136d915ec08116dcbf449354f2af
