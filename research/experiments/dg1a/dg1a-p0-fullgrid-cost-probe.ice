TITLE: DG-1A-P0 Full-Grid CPU Cost Probe
DATE: 2026-09-17
STATUS: EXPLORATORY FEASIBILITY MEASUREMENT
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR THIS SANDBOX MEASUREMENT ONLY

QUESTION
Is the repository's 40 x 40, 16-state-channel, hidden-width-128 P0 base envelope computationally feasible enough in a CPU environment to justify bounded full-grid exploratory training rather than immediately requiring a GPU?

EVIDENCE CLASS
MEASURED SANDBOX PERFORMANCE RESULT.

MACHINE-READABLE EVIDENCE
evidence/dg1a/p0_fullgrid_cost_probe.json

CONFIGURATION
Grid: 40 x 40
Batch size: 8
State channels: 16
Hidden channels: 128
Precision: float32
Update-rule parameters: 8,320
Device: CPU

PROCEDURE
Execute one forward developmental rollout followed by morphology-loss backward propagation at two development horizons matching the lower and upper P0 base training range.

No optimizer step, state-pool update, checkpoint write, or multi-iteration training throughput is included.

MEASURED RESULT — 64 STEPS
Forward: 0.47894 s
Backward: 0.48329 s
Combined: 0.96223 s
Observed process max RSS: approximately 1,012,420 KB
State remained finite: YES

MEASURED RESULT — 96 STEPS
Forward: 0.75071 s
Backward: 0.64573 s
Combined: 1.39644 s
Observed process max RSS: approximately 1,400,808 KB
State remained finite: YES

ANALYSIS
The full-grid P0 model is small in persistent parameter count; compute and autograd-state residency dominate the cost.

The measured 96-step batch fits inside approximately 1.4 GB process RSS in this environment. This supports CPU feasibility for bounded exploratory work and is comfortably below the project's home-hardware RAM/VRAM tiers when interpreted only as an early implementation measurement.

The measurement does not establish end-to-end training duration, peak memory under every optimizer/state-pool configuration, or equivalent performance on the user's Windows machine.

DECISION
Full-grid P0 exploratory work is computationally justified.

Do not scale model width or grid size further until the 40 x 40 P0 question is answered.

Do not interpret parameter count alone as hardware feasibility; continue reporting measured memory and wall-clock behavior.

NEXT ACTION
Run a bounded full-grid seed-0 growth/regeneration bring-up through an execution path capable of preserving a continuous training state for the complete configured run. Maintain the calibrated 0.60 evaluation lesion for the matched recovery gate.
