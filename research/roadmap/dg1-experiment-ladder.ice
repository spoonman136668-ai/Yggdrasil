TITLE: YG-R4 — DG-1 Developmental Intelligence Experiment Ladder
DATE: 2026-09-17
STATUS: ACTIVE ROADMAP
TRACK: DG-1
CONFIDENCE: SUPPORTED AS RESEARCH PLAN

QUESTION
What sequence of experiments maximizes information gained per unit compute while preventing later complexity from masking foundational failures?

ROADMAP RULE
Scale only after the smaller experiment has answered its question. A later stage may begin early only when it does not obscure the acceptance criteria of the current stage.

GLOBAL MEASUREMENT FAMILIES
FUNCTION:
- primary task metric
- generalization metric
- recovery metric after damage
RETENTION:
- prior-task performance after each new task
- forgetting / backward transfer
DEVELOPMENT:
- steps to functional threshold
- new cells / edges / parameters created
- reuse fraction
RESOURCE:
- active cells / parameters
- persistent parameters
- resident and peak bytes
- communication
- latency
SPECIALIZATION:
- task affinity
- intervention-specific functional loss
- cluster/role reuse

DG-1A — FOUNDATIONAL REPRODUCTION
Question: can the implementation reproduce known local growth, persistence, and regeneration behavior?
Prototype:
- canonical 2D NCA growth from seed
- fixed local neighborhood
- shared residual update rule
- stochastic/asynchronous updates if reproduction requires
Baselines:
- published/canonical behavior ranges where reproducible
Success:
- target growth is stable across randomized update horizons;
- damage-trained model recovers morphology materially better than non-regenerating control;
- telemetry and seeds are reproducible.
Failure:
- unstable growth, exploding state, or inability to reproduce known behavior after implementation validation.
Gate to DG-1B:
- cell/update abstraction is stable enough to reuse;
- deterministic experiment configuration and metrics exist.

DG-1B — FUNCTIONAL CELLULAR COMPUTATION
Question: can shared local rules produce task function rather than only morphology?
Tasks in increasing difficulty:
- distributed Boolean/consensus tasks
- synthetic shape classification
- self-classifying MNIST-style task
- small symbolic/grid transformations
Baselines:
- fixed MLP/CNN with matched active parameter budget where meaningful
- recurrent convolution/message-passing model without developmental damage training
Success:
- task function above declared baseline threshold;
- no hidden global controller;
- task remains interpretable under cell-state telemetry.
Gate:
- at least one functional task supports controlled damage experiments.

DG-1C — EMERGENT SPECIALIZATION
Question: do useful roles differentiate under multi-task demand?
Protocol:
- multiple task families in one environment
- role/state probes
- targeted ablations
Success:
- stable function-linked specialization by intervention criteria, not representational difference alone;
- reuse of at least some structure across task families.
Failure mode to distinguish:
- homogeneous cells can still solve tasks; this does not disprove development, but does fail the specialization mechanism.

DG-1D — FUNCTIONAL REGENERATION
Question: can developed computation recover from structural damage?
Damage sets:
- random cells
- high-utility cells
- specialist clusters
- communication edges
- volatile state
Metrics:
- immediate capability loss
- recovered capability
- steps to recovery
- new structure
- resource cost
Success:
- functional recovery exceeds no-repair control under at least two damage regimes;
- recovery does not depend on restoring a saved full phenotype.

DG-1E — CONTINUAL DEVELOPMENT
Question: can sequential tasks accumulate without near-linear active-phenotype growth or catastrophic forgetting?
Protocol:
A -> B -> C -> D with repeated probes of all prior tasks.
Baselines:
- ordinary sequential fine-tuning
- replay or regularization baseline
- task-specific expansion baseline
- PackNet-like structural allocation where applicable
Success:
- useful retention and acquisition;
- measurable reuse;
- active phenotype grows more slowly than naive per-task duplication in the tested sequence.

DG-1F — DEVELOPMENTAL NEURAL MODULES
Question: what cell granularity supports useful scalable neural function?
Candidates:
- tiny MLP
- low-rank adapter
- recurrent memory module
- micro-expert
Baselines:
- same modules statically allocated
- fixed router
Selection criteria:
- training stability
- specialization
- recovery
- byte/compute cost
- hardware realization
Gate:
- select at most one or two module types for DG-1G/H; do not carry every candidate forward.

DG-1G — FROZEN INTELLIGENT SEED
Question: can development add capability around an existing model without destabilizing the core?
Protocol:
- small pretrained core frozen
- developmental modules attached at bounded insertion points
- core-only baseline
Success:
- task improvement over frozen seed;
- bounded added active parameters;
- previous seed behavior remains within declared tolerance.

DG-1H — DEVELOPMENTAL ADAPTER POPULATION
Question: does developmental structure add value beyond adapter routing?
Required baselines:
- fixed LoRA
- multiple fixed LoRAs
- learned adapter router
- developmental adapter population
Metrics:
- performance
- adaptation speed
- retention
- total and active parameters
- regeneration
- reuse
Success:
- developmental system demonstrates at least one material advantage specific to the thesis, such as functional regeneration, lower persistent storage for multiple phenotypes, improved reuse, or better continual adaptation at matched active cost.

DG-1I — ANCESTOR INHERITANCE
Question: can ancestor capability become regenerable developmental information?
Initial protocol:
- common frozen seed
- 3-5 ancestor specialist adapters
- train descendant genome to regenerate/assemble capability
- remove donor weights at evaluation
Success:
- multiple capabilities recovered;
- donor checkpoints not required at evaluation;
- compactness and/or regeneration/composition advantage over static routing and hypernetwork baseline.

DG-1J — RESOURCE-CONSTRAINED ORGANISM
Question: does explicit scarcity produce useful compact developmental organization on consumer hardware?
Budgets:
- max active cells
- max RAM/VRAM
- max communication
- max latency
- max development steps
Protocol:
- staged penalties, one resource axis at a time before combined budgets
Success:
- graceful capability/resource frontier;
- phenotype scales with task demand;
- no hidden dense controller;
- measured hardware savings, not only theoretical sparsity.

CROSS-STAGE STOP RULES
STOP AND REPAIR if:
- metric cannot distinguish developmental behavior from baseline;
- resource accounting omits a dominant storage/compute term;
- global information leakage makes local-development claim invalid;
- repeated runs are too unstable for inference;
- a simpler baseline has not been implemented.

DO NOT STOP THE PROGRAM solely because:
- one cell representation fails;
- one penalty causes collapse;
- specialization does not emerge in the first environment;
- a grid topology underperforms a graph;
- one module granularity is poor.
These are mechanism results, not automatically evidence against the developmental thesis.

HARD THESIS CHECKPOINTS
Checkpoint 1 after DG-1D:
Can local development support functional computation and functional regeneration?

Checkpoint 2 after DG-1H:
Does developmental modularity offer anything beyond strong static/routed adapter baselines?

Checkpoint 3 after DG-1J:
Under measured consumer-hardware constraints, can accumulated capability increase faster than active phenotype/resource demand over a meaningful task sequence?

DECISION
Begin with DG-1A reproduction followed immediately by a DG-1B/D bridge experiment for functional regeneration. Do not start pretrained-seed or ancestor work until the measurement and resource ledger is trusted.

NEXT EXPERIMENT
DG-1A-P0 canonical NCA reproduction, followed by DG-1B/D-P1 distributed functional regeneration.
