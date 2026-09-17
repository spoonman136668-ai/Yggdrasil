TITLE: YG-R2A — Cell Model Architecture Study
DATE: 2026-09-17
STATUS: RECOMMENDED INITIAL DESIGN
TRACK: DG-1 / DG-1A through DG-1F
CONFIDENCE: PLAUSIBLE

QUESTION
What should a Yggdrasil cell be so that it can begin as a tractable NCA unit and later become useful neural computational structure without hiding the whole system inside each cell?

DESIGN PRINCIPLE
A cell is a bounded computational module with local state, bounded communication, an update rule shared or partially shared with peers, explicit resource cost, and a lifecycle state. Cell identity must be smaller than the global task solution.

STAGED REPRESENTATION

STAGE 0 — LATENT NCA CELL
Purpose: reproduce known growth, persistence, and damage recovery dynamics.
State:
- visible/task channels
- hidden communication channels
- alive/activity scalar
- immutable input channels when required by the task
Update:
- local 3x3 perception or bounded graph neighborhood
- shared small MLP/convolutional rule
- residual state update
- optional stochastic/asynchronous firing
Structural growth:
- implicit via alive mask only

STAGE 1 — FUNCTIONAL CELL
Purpose: DG-1B functional computation and regeneration.
Adds:
- task-state channels
- utility telemetry
- local confidence/error proxy
- activity gate
Readout:
- distributed consensus, pooled readout, or task-specific endpoint chosen before training
Constraint:
- no learnable per-cell parameter block yet; useful computation must primarily emerge from shared update dynamics plus state.

STAGE 2 — DIFFERENTIATING CELL
Purpose: DG-1C specialization.
Adds bounded role state:
- role logits or discrete role token
- role-conditioned micro-parameters generated from genome
- communication-channel mask
- lineage/age metadata for telemetry only unless explicitly exposed
Candidate roles:
COMPUTE
MEMORY
ROUTING
VERIFY
COMMUNICATION
Specialization is accepted only if intervention shows functional dependence on the role.

STAGE 3 — NEURAL MODULE CELL
Purpose: DG-1F onward.
Candidate payloads:
- tiny MLP
- low-rank adapter / LoRA block
- micro-expert
- recurrent memory module
- verification head
A cell then contains:
CONTROL STATE — compact developmental state
PAYLOAD — bounded neural parameters or generated parameterization
PORTS — typed sparse communication interfaces
LIFECYCLE — ACTIVE / HIBERNATING / ARCHIVED / REGENERABLE / PRUNED
RESOURCE LEDGER — resident bytes, active parameters, estimated FLOPs, communication bytes

RECOMMENDED INITIAL CELL VECTOR
For DG-1A/B, use a 16- to 32-channel float state as a sweep parameter, not a fixed doctrine. Suggested partition for a 24-channel prototype:
- 1 alive/activity
- 4 immutable/task-visible channels where needed
- 8 communication channels
- 8 private/internal channels
- 3 readout/control channels
Exact widths remain experimental.

LOCAL UPDATE
For a cell i at developmental step t:
perception_i = P({state_j : j in neighborhood(i)})
message_i = aggregate(perception_i)
delta_i = U_genome(state_i, message_i, task_context_local)
state_i(t+1) = state_i(t) + gate_i * delta_i

For early work, U_genome should be small and shared across all cells. Later work may condition U on role embeddings or generate bounded payload parameters.

COMMUNICATION TOPOLOGY
DG-1A: fixed 2D Moore neighborhood for reproducibility.
DG-1B: same topology unless the task itself requires a graph.
DG-1C/D: compare grid to bounded-degree graph while holding parameter budget constant.
DG-1F+: sparse typed graph is preferred for neural modules because cognitive modules need not occupy Euclidean positions.

Do not introduce globally dense attention as the default developmental communication mechanism. If attention is tested, bound its neighborhood or account explicitly for its global communication cost.

LIFECYCLE OPERATIONS
Each structural operation eventually requires:
- trigger
- permitted local observations
- global hard budget enforcement external to the learned preference
- resource cost
- telemetry
- deterministic failure behavior when budget is exhausted

HARD LIMITS
The learned rule may request growth. It must never control the hard population ceiling itself.
Required runtime guards for structural experiments:
- max cells
- max edges per cell
- max total edges
- max active parameters
- max resident bytes
- max developmental steps
- max spawn operations per step

SPECIALIZATION TEST
A cell/cluster is a useful specialist only if all three are observed:
1. statistically non-random task or function affinity;
2. perturbing/removing it selectively harms the associated function more than unrelated functions;
3. another cell/cluster can replace or regenerate that function under the tested repair regime, if regeneration is claimed.

ANTI-CHEATING TESTS
- Shuffle cell positions while preserving states where topology permits.
- Freeze developmental rule and permute role labels.
- Ablate private channels.
- Replace local messages with delayed/noisy messages.
- Compare against a centralized controller with matched parameters.
- Measure whether one cell or one global channel carries nearly all task information.

DECISION
Use latent-state shared-rule cells first. Do not start DG-1 with LoRA cells or micro-experts. Graduate to module cells only after local functional computation and functional regeneration are measured cleanly.

OPEN QUESTIONS
- Is private cell memory necessary for stable role identity?
- Does asynchronous firing improve robustness or merely regularize training?
- At what point does a graph topology outperform a grid enough to justify additional complexity?
- Can payload weights be generated on wake rather than stored during hibernation?

NEXT EXPERIMENT
Implement/reproduce a canonical NCA cell and instrument per-cell state, activity, neighborhood messages, and damage response. Then reuse the same cell abstraction for a functional consensus/classification task.
