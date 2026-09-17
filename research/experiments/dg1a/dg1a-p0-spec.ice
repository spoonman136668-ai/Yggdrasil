TITLE: DG-1A-P0 Experiment Specification
DATE: 2026-09-17
STATUS: PREREGISTERED / IMPLEMENTATION OPEN
TRACK: DG-1A
CONFIDENCE: SUPPORTED AS CONTROL EXPERIMENT

EXPERIMENT ID
DG1A-P0

PURPOSE
Reproduce a bounded canonical Growing-NCA-style developmental substrate before testing functional intelligence. P0 validates shared local updates, persistence, damage injection, deterministic evidence capture, and recovery instrumentation.

SCIENTIFIC CLAIM ALLOWED IF SUCCESSFUL
Yggdrasil can reproduce a known class of local shared-rule developmental growth/regeneration dynamics with trustworthy instrumentation.

CLAIMS NOT ALLOWED
P0 does not establish cognition, functional specialization, continual learning, ancestor inheritance, compact capability scaling, or general intelligence.

PRIMARY HYPOTHESES
H-P0-1
A shared residual local update rule can grow a stable target morphology from a single seed under randomized development horizons.
CONFIDENCE BEFORE RUN: SUPPORTED BY PRIOR LITERATURE.

H-P0-2
Persistence training improves long-horizon stability relative to growth-only training.
CONFIDENCE BEFORE RUN: SUPPORTED BY PRIOR LITERATURE.

H-P0-3
Damage/regeneration training improves post-lesion recovery relative to the growth-only control under identical lesions.
CONFIDENCE BEFORE RUN: SUPPORTED BY PRIOR LITERATURE.

CELL REPRESENTATION
Default starting width: 16 channels.
Required visible channels: RGBA-compatible first 4 channels for canonical morphology target.
Remaining channels: hidden mutable state.
Alive mask: derived from alpha/liveness neighborhood threshold in canonical-style implementation.

DEVELOPMENTAL RULE
Per step:
1. compute local perception from fixed convolution kernels;
2. apply one shared neural update network independently at every cell;
3. optionally apply stochastic firing mask;
4. add residual state delta;
5. apply pre/post alive masking;
6. enforce fixed grid bounds.

DEFAULT PERCEPTION
Identity + Sobel-X + Sobel-Y over every channel.
No learned global attention.
No global phenotype state at execution.

DEFAULT UPDATE NETWORK
1x1 convolution / per-cell MLP equivalent:
perception_width -> hidden_width -> state_width.
Final projection initialized to zero so the initial rule is near identity.

INITIAL CONFIGURATION FAMILY
state_channels: 16
hidden_channels: 128
grid_size: 40 x 40
fire_rate: 0.5
train_steps_min: 64
train_steps_max: 96
seed location: center
alive_threshold: 0.1
batch_size: implementation/configurable
precision: float32 baseline

These are starting values, not confirmed optimum values.

TARGET
Use a small deterministic RGBA target generated from repository-native data or a compact checked-in asset. Avoid remote runtime dependencies.

TRAINING VARIANTS
V0 — GROWTH ONLY
Train from seed states only.

V1 — PERSISTENCE
Maintain a state pool and include mature states advanced beyond ordinary growth horizon.

V2 — REGENERATION
Maintain a state pool and apply controlled lesions to mature states during training.

DAMAGE PROTOCOLS FOR EVALUATION
D0-RECT
Erase a deterministic rectangular region selected by seed/config.

D0-DROPOUT
Erase a configured fraction of live cells using seeded random selection.

D0-CENTER
Erase a fixed central region sized as a fraction of active bounding box.

Immutable target is never used to restore damaged state.

PRIMARY METRIC
Morphology error on visible RGBA channels versus target over the declared crop/grid.
Exact loss formulation must be logged in config/evidence.

RECOVERY METRICS
- error before lesion;
- error immediately after lesion;
- error after each recovery step/window;
- normalized RecoveryFraction using improvement toward pre-lesion error;
- T50/T90 where attainable;
- area under normalized recovery curve;
- active cell count;
- mean update magnitude;
- repair wall-clock when executed;
- state bytes and update-rule parameter count.

PERSISTENCE METRICS
- target error from ordinary training horizon through extended horizon;
- active cell-count drift;
- visible-state drift;
- numerical instability/non-finite count.

RESOURCE METRICS
- genome/update-rule parameter count;
- serialized model bytes when checkpointed;
- state tensor bytes;
- active cells;
- development steps;
- approximate perception/update operations proxy;
- wall-clock per developmental step;
- peak RAM and VRAM where measurable.

HARD LIMITS
- fixed configured grid dimensions;
- fixed configured state width;
- fixed configured update-network width;
- maximum development steps per train/eval call;
- no dynamic tensor growth;
- no cell replication outside existing grid slots;
- no external state reload during repair.

PREREGISTERED SUCCESS CONDITIONS
S1 — GROWTH
At least one declared target/config family reaches a stable, visually and numerically meaningful low-error morphology from the seed across multiple independent training seeds.
The exact numeric error threshold must be frozen in config before confirmatory runs after exploratory implementation validation.

S2 — PERSISTENCE
V1 shows materially lower long-horizon degradation than V0 under the same evaluation horizon and seed family.

S3 — REGENERATION
V2 suffers a meaningful immediate lesion error increase and subsequently recovers materially more lost morphology quality than V0 under the same lesion family.

S4 — REPRODUCIBILITY
Every evidence record identifies code revision, config, RNG seed, device, precision, and target identity.

S5 — INSTRUMENTATION
Metrics distinguish pre-damage state, damage effect, repair trajectory, active cells, state bytes, and model parameter count.

FAILURE CONDITIONS
F1
Implementation cannot reproduce basic canonical behavior after unit correctness is established and a bounded exploratory sweep is exhausted.

F2
Training diverges or produces non-finite state under all bounded validated configurations.

F3
Lesions produce negligible error increase, invalidating regeneration measurement.

F4
Apparent repair depends on copying saved undamaged state.

F5
Recovery telemetry is insufficient to distinguish passive robustness from post-lesion developmental change.

EXPLORATORY VS CONFIRMATORY
Implementation bring-up and bounded hyperparameter search are EXPLORATORY.
After a stable configuration family is identified, freeze thresholds/config ranges in a follow-up .ice amendment before reporting confirmatory support.

MANDATORY TESTS BEFORE TRAINING CLAIMS
- perception shape and dtype preservation;
- shared update output shape;
- deterministic seeded firing masks when generator supplied;
- alive mask behavior;
- fixed-grid hard limits;
- rectangular/center/dropout damage correctness;
- damage never mutates immutable target data;
- metric calculations on known synthetic tensors;
- recovery metric edge cases;
- non-finite-state detection.

EVIDENCE OUTPUT
Machine-readable run evidence may be JSON/JSONL/CSV under evidence/ or a configured external run directory.
Narrative interpretation, decisions, failures, and conclusions remain .ice.

IMPLEMENTATION BOUNDARY
This packet may create only the P0 substrate and infrastructure needed for this specification.
Do not add graph growth, functional P1 tasks, adapters, pretrained seeds, ancestor models, or structural replication.

NEXT ACTION
Implement deterministic NCA core, damage operators, metrics/resources helpers, and unit tests before implementing the full training loop.