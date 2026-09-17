TITLE: DG-1 Initial Architecture Decision
DATE: 2026-09-17
STATUS: ACCEPTED FOR FIRST PROTOTYPE
TRACK: DG-1
CONFIDENCE: PLAUSIBLE

DECISION PURPOSE
Resolve the first implementation gate sufficiently to permit bounded toy reproduction and the first functional prototype. This decision does not lock later DG-1F+ architecture.

1. CELL REPRESENTATION
ACCEPTED FOR DG-1A/B:
A dense latent-state cell vector, initially 16-32 float channels, with explicit activity/alive state, task-visible or immutable channels where required, communication channels, and private/internal channels.

Cells do not initially contain independent neural modules. All cells share the developmental update parameters.

2. DEVELOPMENTAL UPDATE MECHANISM
ACCEPTED:
Shared residual neural cellular automaton rule:
local perception -> shared small neural update -> residual cell-state delta.
Support randomized update horizon and optionally stochastic/asynchronous firing.

3. COMMUNICATION TOPOLOGY
ACCEPTED FOR DG-1A/B:
Fixed 2D Moore neighborhood / 3x3 local perception.

RATIONALE:
This is reproducible, computationally cheap, and aligned with established NCA work. Learned sparse graphs remain planned for later functional-module stages.

4. TRAINING OBJECTIVE
ACCEPTED INITIAL FORM:
L = L_task + lambda_stability * L_stability.

For explicit regeneration training, expose damaged states in the training distribution.

Resource terms are initially measured without pressure, then introduced one axis at a time after stable task learning.

5. RESOURCE OBJECTIVE
ACCEPTED INITIAL FORM:
Hard limits always enforced.
Early telemetry:
- active cells
- resident bytes
- active parameters
- development steps
- communication count
- wall-clock / peak memory

First soft pressure after stable baseline:
+ lambda_activity * normalized_active_cell_or_parameter_cost.

6. FIRST BASELINES
DG-1A:
- canonical growth-only NCA
- persistence-trained NCA
- damage/regeneration-trained NCA

DG-1B/D functional regeneration:
- same architecture trained without damage exposure
- same architecture with damage exposure
- fixed or recurrent non-developmental model with comparable active parameter budget where task semantics permit

Later required baselines:
- hypernetwork generator
- fixed LoRA
- multiple LoRAs + router
- sparse/fixed expert routing

7. FIRST EXPERIMENT
DG-1A-P0 — canonical NCA reproduction.
Immediately followed by DG-1B/D-P1 — distributed functional regeneration using the same cell abstraction.

8. MEASUREMENT SCHEMA
Required per run:
CONFIGURATION
- seed
- device
- precision
- grid size
- state width
- update-rule parameter count
- update horizon
- firing probability if used
- damage protocol

FUNCTION
- task metric before damage
- immediate post-damage metric
- recovered metric
- recovery steps to threshold

STRUCTURE
- active cells over time
- damaged cells/edges
- newly active cells where applicable

RESOURCE
- active parameters
- resident parameters
- peak RAM/VRAM when measurable
- update count
- message/neighborhood operations proxy
- wall-clock training and evaluation latency

REPRODUCIBILITY
- multiple random seeds
- stored machine-readable metrics
- configuration hash or equivalent deterministic identity

9. SUCCESS CONDITION
DG-1A-P0 succeeds when:
- growth/persistence behavior is reproducible across multiple seeds/configurations;
- damage-trained system demonstrates measurable recovery after controlled damage;
- instrumentation is trustworthy enough to support functional experiments.

DG-1B/D-P1 succeeds when:
- shared local dynamics solve the declared functional task above its pre-registered threshold;
- controlled damage causes measurable function loss;
- the trained developmental dynamics recover a meaningful fraction of that lost function beyond a no-repair/no-damage-training control;
- recovery does not load a saved full phenotype;
- resource and recovery metrics are recorded.

10. FAILURE CONDITION
DG-1A-P0 fails if known basic behavior cannot be reproduced after implementation/debug validation, or state dynamics are irreducibly unstable under the declared configuration.

DG-1B/D-P1 fails if:
- task function never reaches the predeclared threshold;
- apparent recovery is explained by damage having negligible functional effect;
- recovery requires global/full-state restoration;
- results are too unstable across seeds to distinguish from control;
- resource accounting is insufficient to determine what was retained or recomputed.

IMPLEMENTATION BOUNDARY
AUTHORIZED BY THIS RESEARCH DECISION:
- toy/canonical DG-1A reproduction
- bounded DG-1B/D prototype
- measurement and test infrastructure required for those experiments

NOT YET JUSTIFIED:
- large pretrained seed integration
- open-ended cell replication
- large-scale ancestor ingestion
- autonomous structural growth without hard population limits
- claims of general intelligence or sublinear capability scaling

DECISION
The first implementation gate is satisfied for bounded DG-1A and DG-1B/D work. Later stages must pass their own gates before scaling.

NEXT EXPERIMENT
Execute DG-1A-P0 as specified in the prototype recommendation.
