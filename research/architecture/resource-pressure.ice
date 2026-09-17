TITLE: YG-R3 — Resource-Constrained Development Model
DATE: 2026-09-17
STATUS: RECOMMENDED EXPERIMENTAL MODEL
TRACK: DG-1 / DG-1J
CONFIDENCE: PLAUSIBLE

QUESTION
How should resource scarcity influence development without turning the experiment into arbitrary regularization or allowing the learned system to violate hardware limits?

PRINCIPLE
Resource pressure is part of the environment, but safety/resource ceilings are not negotiable rewards. Use a two-layer model:

HARD CONSTRAINT LAYER
The runtime enforces absolute limits that learned policy cannot override.

SOFT ECONOMIC LAYER
Within those limits, the objective prices resource use so the organism can learn tradeoffs.

HARD CONSTRAINTS
Every structural experiment must specify:
- maximum active cells
- maximum total cells retained
- maximum active payload parameters
- maximum resident RAM/VRAM
- maximum edges / communication fanout
- maximum developmental steps per episode
- maximum structural actions per step
- optional latency deadline

A growth request that exceeds a hard limit fails deterministically and emits telemetry. The learned controller does not receive authority to raise the limit.

COST VECTOR
Report resource use as a vector before collapsing it into one scalar:
C = {
  active_parameters,
  persistent_parameters,
  resident_bytes,
  peak_bytes,
  communication_bytes_or_messages,
  active_edges,
  development_steps,
  task_steps,
  measured_latency,
  structural_actions,
  wake_or_regeneration_bytes
}

SCALAR OBJECTIVE — CANDIDATE
L_total = L_task
        + lambda_active * norm(active_parameters)
        + lambda_resident * norm(resident_bytes)
        + lambda_comm * norm(communication_cost)
        + lambda_dev * norm(development_steps)
        + lambda_latency * norm(latency)
        + lambda_growth * norm(new_persistent_structure)

For continual experiments add:
        + lambda_forget * L_retention
        + lambda_rebuild * norm(regeneration_cost)

NORMALIZATION
Costs must be normalized against a declared reference budget or baseline. Raw units with unrelated scale should not be summed directly.

RECOMMENDED TRAINING REGIMES

R0 — NO RESOURCE PENALTY
Purpose: establish achievable task behavior and avoid confusing optimization failure with resource effects.

R1 — ACTIVITY PRESSURE
Penalize active cells / active parameters only.
Question: can the organism solve the task with sparse activation?

R2 — COMMUNICATION PRESSURE
Add message/edge cost.
Question: does local organization become more efficient, or does performance collapse?

R3 — RESIDENCY PRESSURE
Price persistent and resident bytes separately from active compute.
Question: does hibernation or compact persistent state become useful?

R4 — DEVELOPMENT TIME PRESSURE
Price developmental steps and wake latency.
Question: does repeated experience create faster developmental trajectories?

Do not activate all penalties in the first experiment. Add one axis at a time so causal interpretation remains possible.

BUDGET RANDOMIZATION
Later experiments should sample resource envelopes during training rather than train under one fixed ceiling. Example:
- high-budget episodes reward peak task performance;
- constrained episodes force reuse/hibernation;
- low-communication episodes test local modularity.

Hypothesis: variable budgets may favor developmental policies that can scale phenotype size to task demand instead of specializing to a single fixed budget.
Confidence: SPECULATIVE.

RESOURCE-AWARE LIFECYCLE
ACTIVE:
- pays active compute + resident cost.
HIBERNATING:
- pays retained-state cost, near-zero payload compute.
ARCHIVED:
- pays storage and load cost, not active memory.
REGENERABLE:
- pays genome/context storage plus future development cost.
PRUNED:
- pays no ongoing cost but loses recovery guarantee.

REGENERATION ECONOMICS
A regenerable phenotype is useful only when some operating regime satisfies a tradeoff such as:
retained_regeneration_state_bytes << stored_full_phenotype_bytes
AND
regeneration_latency <= acceptable_cold_start_budget
AND
regenerated_function >= declared recovery threshold

No single ratio is universally sufficient; report the entire tradeoff curve.

HARDWARE REALISM
Logical sparsity is not equivalent to physical savings. Unstructured sparse tensors may reduce parameter count without reducing wall-clock cost on consumer GPUs. Prefer measurements of actual peak memory and latency, and test structured sparsity / module-level sparsity when hardware savings matter.

RESOURCE PRESSURE FAILURE MODES
- organism learns to suppress activity while preserving a hidden dense controller;
- penalty scaling overwhelms task loss and produces dead cells;
- development becomes extremely slow to minimize resident structure;
- communication is encoded indirectly in large local state;
- frequent hibernate/wake thrashing increases total cost;
- logical sparsity has no realized hardware benefit;
- population fragments into many tiny modules with routing overhead greater than saved compute.

MEASUREMENT SCHEMA
Every run should emit at minimum:
- task metric
- active cell count: mean / p95 / max
- total cell count
- active and persistent parameter counts
- peak RAM / VRAM when available
- development steps
- messages or edge traversals
- structural action counts by type
- wall-clock development and task latency
- retained bytes required for wake/regeneration
- recovery metric after damage when applicable

DECISION
Use hard budgets plus staged soft penalties. Begin DG-1A/B with telemetry only or light activity pressure; do not let resource optimization obscure whether functional development works at all.

OPEN QUESTIONS
- Should the cost function use fixed lambdas or constrained optimization / Lagrange multipliers?
- Is communication count or transferred-byte count the better early proxy?
- When does recomputation become cheaper than residency on actual home hardware?
- Can budget randomization induce graceful phenotype scaling?

NEXT EXPERIMENT
Add activity-cost telemetry to DG-1B functional regeneration without training pressure. After a stable baseline exists, sweep one activity penalty across at least five values and plot task performance versus active-cell cost.
