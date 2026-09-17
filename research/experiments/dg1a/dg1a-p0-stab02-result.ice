TITLE: DG-1A-P0-STAB-02 Result — Development-Horizon Stabilization
DATE: 2026-09-17
STATUS: EXPLORATORY NEGATIVE RESULT
TRACK: DG-1A
CONFIDENCE: SUPPORTED FOR THIS SINGLE-SEED ABLATION

QUESTION
Does extending regeneration-training trajectories from 64..96 to 64..128 steps reduce late post-repair relapse while preserving meaningful lesion sensitivity and a viable developed phenotype?

EVIDENCE CLASS
MEASURED SANDBOX RESULT.

PROVENANCE LIMIT
Execution occurred in an isolated reconstructed ChatGPT CPU workspace, not a commit-bound checkout. This result is mechanism-selection evidence only.

MACHINE-READABLE EVIDENCE
evidence/dg1a/p0_stab02_sandbox.json

PREREGISTERED CANDIDATE
H128
- seed: 0
- variant: regeneration
- grid: 40 x 40
- state channels: 16
- hidden channels: 128
- training iterations: 200
- training development steps: 64..128
- training lesion: center 0.50 x 0.50
- maturity threshold: 16 active cells
- evaluation growth horizon: 96
- recovery horizon: 96
- evaluation lesion: center 0.60 x 0.60

MEASURED TRAINING
Initial recorded loss: 0.0294179674
Minimum recorded loss: 0.0250349939
Final recorded loss: 0.0295742173
Accumulated training time: 194.7508211 seconds
Checkpoint bytes: 6,672,345

MEASURED EVALUATION
Pre-damage active cells: 0 / 1600
Post-damage active cells: 0 / 1600
Final active cells: 0 / 1600
Pre-lesion error: 0.0295742173
Post-lesion error: 0.0295742173
RelativeDamageEffect: 0.0
ActiveCellRemovalFraction: 0.0
Valid lesion: NO
Bounded RecoveryFraction: UNDEFINED
Stable T50: NOT ATTAINED
Stable T90: NOT ATTAINED

IMPROVEMENT RULE
H128 required all of:
1. valid lesion;
2. stable T50;
3. final RecoveryFraction > 0.423023;
4. pre-lesion error <= 0.0361635;
5. final active cells <= 800;
6. finite state.

RESULT
FAIL.
The candidate fails at the viability/lesion gate before recovery can be interpreted.

FAILURE MODE
ALL-DEAD PHENOTYPE.

The model converged to a phenotype with zero active cells by the 96-step evaluation horizon. The evaluation lesion therefore has no effect and regeneration is undefined.

IMPORTANT DIAGNOSTIC
The final loss exactly equals the all-dead phenotype's unweighted visible-channel morphology MSE for the current small disk target: approximately 0.0295742.

This exposes a training-objective degeneracy. On the 40 x 40 grid, most pixels are target background. An all-zero phenotype can therefore achieve a deceptively moderate global MSE while completely failing the developmental objective.

The longer-horizon curriculum did not merely fail to stabilize repair; it increased pressure toward the dead-state attractor.

NEGATIVE KNOWLEDGE RETAINED
1. Extending training horizon alone is not a repair-stabilization solution.
2. H128 must not be widened to more seeds inside STAB-02.
3. Global unweighted pixel MSE is insufficient as the sole training objective for sparse targets at this scale.
4. Evaluation MSE remains useful for continuity, but training must make target-foreground failure expensive enough that zero activity cannot masquerade as acceptable morphology.
5. This is an objective-design issue, not evidence against developmental intelligence.

DECISION
Close STAB-02 as a negative result.
Do not test H160/H192 or other longer horizons in this packet.
Return the development horizon to the H96 control for the next stabilization experiment.

NEXT MECHANISM
DG-1A-P0-STAB-03 — Foreground/Background-Balanced Morphology Training.

The next experiment should change only the training morphology objective while preserving the H96 developmental horizon, maturity threshold, lesions, target, grid, evaluation metric, and resource limits.

Candidate objective:
- compute foreground loss on pixels where target alpha is active;
- compute background loss on the complement;
- combine foreground and background terms with fixed equal contribution so target occupancy cannot make the dead phenotype competitive;
- continue reporting the original global morphology MSE for evaluation and cross-experiment comparability.

FIBONACCI RELATION
No Fibonacci mechanism is introduced in STAB-03. DG-1A-FIB1 remains downstream of a viable canonical P0 control.
