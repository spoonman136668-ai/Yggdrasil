TITLE: DG-1 Measurement Framework
DATE: 2026-09-17
STATUS: ADOPTED FOR EARLY EXPERIMENT DESIGN
TRACK: DG-1
CONFIDENCE: SUPPORTED

QUESTION
What must Yggdrasil measure so claims about development, specialization, regeneration, reuse, inheritance, and resource efficiency remain falsifiable?

MEASUREMENT PRINCIPLE
A developmental system can appear successful for the wrong reason. Every claim must therefore separate function, structure, persistent information, active resource use, developmental cost, and control performance.

EVIDENCE CLASSES
MEASURED RESULT
Directly produced by a Yggdrasil run under recorded configuration.

SIMULATED RESULT
Produced in a simulator/model whose assumptions are recorded.

ESTIMATED RESULT
Computed from a declared proxy or model rather than direct measurement.

HYPOTHESIS
Unverified expectation or proposed mechanism.

These labels must not be collapsed.

CORE IDENTIFIERS PER RUN
- experiment ID;
- code/commit identity;
- config identity/hash;
- random seed;
- device;
- precision;
- dataset/task version;
- cell/module representation;
- topology representation;
- genome/update-rule parameter count;
- maximum and realized development horizon;
- damage/resource-pressure configuration;
- baseline/control identity.

FUNCTION METRICS
Every experiment defines one or more primary task metrics before the run.
Examples:
- accuracy;
- reward;
- exact-match or edit metric;
- Boolean truth-table correctness;
- routing success;
- sequence loss;
- graph objective.

No morphology metric may substitute for a functional metric after DG-1A unless morphology itself is the declared task.

DEVELOPMENT METRICS
- steps to first viable function;
- steps to stable function;
- performance-versus-development-step curve;
- variance across randomized update horizons;
- cell/module state-change magnitude over time;
- birth/death/connect/disconnect/hibernate/wake counts where enabled;
- developmental churn;
- failed or reverted structural operations.

CAPACITY ACCOUNTING
Report four distinct quantities whenever applicable.

G — GENOME
Persistent shared developmental information.
Metrics:
- parameter count;
- serialized bytes;
- auxiliary persistent metadata bytes.

R — RESIDENT PHENOTYPE
Instantiated phenotype retained in current memory/storage whether active or not.
Metrics:
- resident parameter count;
- resident state bytes;
- topology/metadata bytes.

A — ACTIVE PHENOTYPE
Structure participating in the current computation window.
Metrics:
- active parameters/modules/cells;
- active state bytes;
- measured or estimated active FLOPs/operations;
- active communication.

D — DEVELOPMENT / REGENERATION COST
Cost required to create or restore phenotype.
Metrics:
- development steps;
- wall-clock time;
- peak memory;
- communication operations;
- estimated FLOPs where feasible;
- energy proxy only when measurement method is declared.

PRIMARY NORTH-STAR RATIOS
These are research metrics, not assumed truths.

CapabilityDensity = declared_capability_score / active_phenotype_cost.
Use only within a fixed benchmark family where capability score is comparable.

ResidentCapabilityDensity = declared_capability_score / resident_phenotype_cost.

DevelopmentEfficiency = gained_function / development_cost.

RegenerationEfficiency = recovered_function / repair_cost.

ReuseFraction = functionally reused active structure / active structure for new task.
Requires a declared causal or routing-based definition.

ACTIVE-PHENOTYPE GROWTH TEST
For sequential tasks 1..N, record accumulated capability C_N and active phenotype A_N under a fixed evaluation protocol.

The north-star hypothesis is that A_N grows materially slower than C_N.
Do not call this sublinear unless a declared scaling fit across sufficient N supports that description.
Small-N visual trends are insufficient.

Suggested reporting:
- C_N curve;
- A_N curve;
- R_N curve;
- G_N curve;
- performance retained on all prior tasks;
- fit families with uncertainty only when sample count supports them.

SPECIALIZATION METRICS
DESCRIPTIVE — NOT SUFFICIENT ALONE
- latent-state clustering;
- parameter divergence;
- activation clustering;
- spatial/graph communities.

FUNCTIONAL
- task-affinity difference;
- task-conditioned routing frequency;
- per-task mutual contribution proxy;
- output-gradient influence where scientifically appropriate.

CAUSAL — PREFERRED
- task-specific ablation delta;
- targeted damage/recovery delta;
- replacement/interchange test;
- communication-edge intervention;
- contribution to transfer/reuse.

SPECIALIZATION CLAIM RULE
A cluster/cell type/module is called functionally specialized only when a functional or causal metric links it preferentially to a task/function and the pattern replicates across multiple seeds.

REGENERATION METRICS
Use the Functional Regeneration Protocol.
Required:
- pre-damage performance;
- immediate post-damage performance;
- recovery trajectory;
- RecoveryFraction;
- T50/T90 where attainable;
- normalized area under recovery curve;
- damage severity;
- retained bytes;
- repair cost;
- control recovery.

ROBUSTNESS VS REGENERATION
Robustness = function survives damage.
Regeneration = lost function returns through developmental dynamics.
A model that suffers no meaningful functional loss demonstrates robustness but does not by that fact demonstrate regeneration.

CONTINUAL LEARNING METRICS
For sequential tasks:
- acquisition performance;
- retained performance after each later task;
- forgetting per prior task;
- forward transfer;
- backward transfer where meaningful;
- new resident capacity;
- new active capacity;
- reused capacity;
- development cost per task;
- number of new modules/cells/edges;
- number hibernated/pruned/merged.

BASELINE-NORMALIZED REPORTING
Where possible report both absolute metrics and deltas versus matched controls.
Examples:
DeltaRecovery = developmental_recovery - control_recovery.
DeltaActiveCost = developmental_active_cost - baseline_active_cost.
DeltaRetention = developmental_retention - baseline_retention.

ANCESTOR INHERITANCE METRICS — LATER STAGE
- donor capability before extraction;
- descendant capability after donor removal;
- genome/persistent information added;
- phenotype development cost;
- functional similarity to donor;
- cross-capability interference;
- regeneration after phenotype deletion;
- performance on unseen combinations of inherited capabilities.

INHERITANCE CLAIM RULE
Do not claim inherited capability if the donor checkpoint or full donor-derived phenotype remains required at inference/development time.
The donor may be used during training/extraction, but the evaluation must state exactly what donor-derived information remains persistent.

RESOURCE METRICS
Required early:
- wall-clock time;
- peak RAM;
- peak VRAM when GPU used;
- serialized genome bytes;
- resident phenotype bytes;
- active cells/modules;
- active parameter estimate;
- communication/update operations proxy.

Required when structure becomes sparse/modular:
- realized kernel/operation density;
- measured latency;
- measured memory, not only theoretical sparsity;
- batching overhead;
- routing overhead;
- hibernation/wake latency;
- serialization/deserialization cost where relevant.

HOME-HARDWARE REPORTING TIERS
CPU ONLY
Report wall-clock, RAM, threads where relevant.

8/12/16/24 GB VRAM
Report GPU model, peak VRAM, wall-clock, batch size, precision, and whether experiment fits without offload.

Do not infer hardware feasibility from parameter count alone.

STATISTICAL DISCIPLINE
- use multiple random seeds for claims about learned dynamics;
- preregister primary metric and threshold in the experiment record before result interpretation;
- report mean/median and dispersion appropriate to sample count;
- retain per-seed results;
- do not hide unstable seeds;
- distinguish exploratory sweeps from confirmatory runs;
- do not tune success thresholds after inspecting outcomes.

FAILURE RECORDING
Record negative outcomes in .ice with:
- failed hypothesis;
- exact configuration family;
- observed failure mode;
- evidence location;
- whether implementation defect was ruled out;
- what remains unknown;
- next bounded discriminating experiment.

MANDATORY BASELINE CLASSES BY STAGE
DG-1A:
- canonical growth-only NCA;
- persistence/regeneration training controls.

DG-1B/D:
- matched no-damage-training developmental model;
- frozen-dynamics robustness control;
- fixed/recurrent/message-passing baseline where meaningful.

DG-1C/E:
- fixed-capacity model;
- dynamic modular/growth baseline;
- continual-learning baseline.

DG-1F/H:
- fixed LoRA;
- multiple fixed LoRAs;
- adapter router;
- developmental adapter population.

DG-1I:
- donor retained;
- independent adapters/experts;
- hypernetwork generation;
- developmental inheritance candidate.

SUCCESS LANGUAGE
Use precise levels:
REPRODUCED — established reference behavior independently reproduced.
OBSERVED — measured phenomenon without sufficient replication/causal evidence.
SUPPORTED — replicated evidence favors hypothesis over declared controls.
DISPROVEN — declared hypothesis fails its preregistered test under validated implementation.
UNKNOWN — evidence insufficient.

Do not promote a mechanism from OBSERVED to SUPPORTED merely because visualization is compelling.

DECISION
This framework is the default measurement contract for DG-1. Individual experiments may add metrics but may not silently omit core categories needed to support their claims.

OPEN QUESTIONS
- What single capability accumulator is valid across heterogeneous task families? Likely none; benchmark-family-specific reporting may be required.
- Which information-flow metric is cheap enough for routine NCA diagnostics?
- How should active module use be attributed when modules contribute partially or recurrently?
- What development-cost normalization best compares CPU and GPU runs?

NEXT EXPERIMENT
Encode the minimum P0 subset into the DG-1A experiment specification after R8 closeout, then use the full regeneration subset for P1.