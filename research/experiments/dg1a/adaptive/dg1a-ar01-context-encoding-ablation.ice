TITLE: DG-1A-AR-01 — Seasonal Context Encoding Ablation
DATE: 2026-09-18
STATUS: SYNTHETIC ARCHITECTURE-SELECTION AUDIT — NOT A YGGDRASIL RESULT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar

PURPOSE
Choose the smallest explicit environmental context representation that preserves the strong AR-01 conditional-rule effect before any Yggdrasil implementation is modified.

BOUNDARY
This audit:
- is synthetic;
- does not modify or execute STAB-18-R1;
- does not modify Yggdrasil;
- does not spend the canonical R1 scientific run;
- compares context encodings only inside the synthetic local-policy surrogate.

COMMON SYNTHETIC TASK
Local state:
8 scalar local-state features.

Modes:
EXPANSION
CONSOLIDATION
MAINTENANCE
REPAIR
DORMANCY
REACTIVATION

Outputs:
growth
retention
repair
activity

Network:
input -> 32 -> 32 -> 4
tanh hidden activations

Training:
- 12,000 states per seed
- 5,000 held-out states per seed
- Adam
- learning rate 0.003
- 220 full-batch epochs

For every encoding, its fixed-rule control had:
- the identical input width;
- identical trainable parameter count;
- identical initialization seed;
- identical training schedule;
- context channels clamped to zero.

ENCODINGS

SCALAR-1
One centered scalar:
(mode_index - 2.5) / 2.5

CIRCLE-2
Two scalars:
cos(2*pi*mode_index/6)
sin(2*pi*mode_index/6)

BINARY-3
Three binary mode bits.

ONEHOT-6
Six-way one-hot context.

FIRST-PASS RESULTS — 8 MATCHED SEEDS

Encoding   Params   Context MSE mean   Context MSE sd   Fixed MSE mean   Fixed/Context
SCALAR-1   1508     0.031792           0.001516         0.045869         1.446x
CIRCLE-2   1540     0.003619           0.000463         0.045871        12.878x
BINARY-3   1572     0.007358           0.004687         0.045850         7.796x
ONEHOT-6   1668     0.004217           0.000231         0.045841        10.894x

INTERPRETATION
A single scalar compresses the six regimes too aggressively for this small network and synthetic target family.

Three binary bits work, but seed-to-seed variance is materially higher.

Six-way one-hot is strong and stable, but it uses the widest condition interface.

The two-dimensional circular code is the smallest tested encoding that retains strong regime separation and low held-out error.

CIRCLE-2 CONFIRMATION — 12 MATCHED SEEDS

Trainable parameters per candidate/control:
1540

Held-out action MSE:
context:
mean 0.003971
sd   0.000973

fixed-rule control:
mean 0.045980
sd   0.000582

Unseen same-state mode-switch diagnostic:
context switch-delta R2-like mean:
0.919166
sd 0.020005

fixed-rule switch-delta:
0.000000

Context normalized switch-delta RMSE:
mean 0.282659
sd   0.031984

Held-out DORMANCY activity/update drive:
context:
mean 0.050519
sd   0.025818

fixed-rule:
mean 0.547406
sd   0.003368

DECISION
Use CIRCLE-2 as the initial AR-01 explicit seasonal context representation.

Frozen conceptual encoding:
SeasonPhase = phi_m

Context[0] = cos(phi_m)
Context[1] = sin(phi_m)

with six preregistered discrete phase points separated by 60 degrees.

RATIONALE
- only two exogenous scalars;
- no separate neural network;
- no per-cell genome;
- exact parameter-count matching remains trivial;
- naturally represents a seasonal cycle;
- leaves later AR work free to replace explicit phase with endogenous mode inference.

IMPORTANT LIMITATION
The six phase points are discrete in AR-01.

Do not claim interpolation to unseen intermediate phases unless separately tested.

Do not claim that circular ordering is biologically privileged.

This is an economical control representation selected by a synthetic ablation.

NEXT
Preregister AR-01 with CIRCLE-2 as the explicit context signal and an exact dummy-context fixed-rule control.

PROVENANCE
evidence_class = SYNTHETIC
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
context_encodings_tested = 4
selected_context_encoding = CIRCLE_2
selected_context_dimensions = 2
