TITLE: EXP-TIMING-WINDOW-001
SCHEMA: ckb-plane.research-experiment-record.v1
EXPERIMENT_ID: EXP-TIMING-WINDOW-001
CANDIDATE_ID: CAND-TIMING-WINDOW-001
HARNESS: yggdrasil-isolated
BASELINE_SHA: 5e32c327a94f9d41960105ace748c5eeeb10aa77

QUESTION
What is the maximum allowable delay between phenotype discard and successful regeneration, and how does retained state size affect this timing window?

HYPOTHESIS
Regeneration success decays exponentially with discard-to-regeneration delay, but a minimal developmental seed state extends the viable window by at least 10x compared to zero retained state.

FIXED_PARAMETERS
delays=[0,1,5,10,25,50,100]
developmental_step_budget=500
distractor_task_count=3
genome_size=1024
max_active_modules=64
random_seed_base=42
retained_state_sizes=[0,32,128,512,2048]
task_family=parametric_maze_navigation
seeds=[42,123,456,789,1024,2048,4096,8192]
compute_seconds=1200

METRICS
regeneration_cost_ratio < 1
capability_recovery_ratio >= 0.7
regeneration_cost_ratio_at_max_delay_with_seed < 0.8
timing_window_extension_factor > 5

CONTROLS
Cold retraining from scratch on Task A (baseline regeneration_cost_ratio = 1.0)
Regeneration with zero delay and full retained state (upper bound)
Regeneration with zero retained state at each delay (lower bound)
Distractor task interference control (same delay, no regeneration attempt)

STOP_CONDITIONS
All delay × retained_state_size conditions completed
Compute budget (1200s) exhausted
Regeneration cost ratio > 2.0 for any condition (catastrophic failure)
Harness error or resource limit reached

POSITIVE_MEANING
Regeneration cost ratio < 1.0 and capability recovery ratio >= 0.7 for delays up to >=10 steps with minimal retained state <=128 bytes, and timing window extension factor >=5x.

NEGATIVE_MEANING
Regeneration cost ratio >=1.0 for all delays >0, or capability recovery ratio <0.7 even at minimal delay with maximal retained state.

MIXED_MEANING
Regeneration viable at short delays but not extended by retained state; suggests timing window exists but developmental seed mechanism insufficient.
